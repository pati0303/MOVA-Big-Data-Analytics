"""AP 6.3d: additive JSON interface acceptance for the existing V2 demonstrator."""
import copy
from datetime import date
import json
from pathlib import Path
import sys
import unittest

sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'src'))
import recommendation_engine as e


class DashboardContractTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.data=e.load_data(include_activity=True)

    def output(self,uid='U001',interests=True,garmin=True,data=None):
        return e.recommend_user(data or self.data,uid,interests_permission=interests,
                                garmin_permission=garmin,as_of=date(2026,7,5))

    def test_three_actual_scenarios_fields_and_json(self):
        expected={
            'U001': (['Freizeit','Outdoor','Sport'],0,'Geringere Trainingshäufigkeit',
                     ['O001','O006','O009','O010','O002'],['A','A','A','A','B']),
            'U002': (['Freizeit','Outdoor'],1,'Höhere Trainingshäufigkeit',
                     ['O009','O010','O011','O012','O013'],['A','A','B','B','B']),
            'U003': (['Wellness'],0,'Geringere Trainingshäufigkeit',
                     ['O017','O018','O019','O020','O021'],['B']*5)}
        catalog={r['offer_id']:r for r in self.data.offers}
        for uid,(cats,cid,label,ids,tiers) in expected.items():
            with self.subTest(uid=uid):
                out=self.output(uid);profile=out['profile']
                self.assertEqual(json.loads(json.dumps(out,allow_nan=False)),out)
                self.assertEqual(out['user_id'],uid)
                self.assertEqual(out['interest_categories'],cats)
                self.assertEqual(profile['cluster_id'],cid)
                self.assertEqual(profile['segment_label'],label)
                self.assertEqual(profile['segment_source'],'stored_user_clusters')
                self.assertEqual(profile['source'],'new_inference_saved_regression_model')
                self.assertEqual(profile['prediction_status'],'available')
                self.assertEqual(profile['target_week_start'],'2026-07-06')
                self.assertEqual(profile['target_week_end'],'2026-07-12')
                self.assertEqual(set(profile['sport_shares']),set(e.SPORTS))
                for sport,value in profile['sport_shares'].items():
                    self.assertEqual(value,float(self.data.profiles[uid]['share_'+sport.lower()]))
                self.assertEqual([r['offer_id'] for r in out['recommendations']],ids)
                self.assertEqual([r['ranking_tier'] for r in out['recommendations']],tiers)
                for r in out['recommendations']:
                    offer=catalog[r['offer_id']]
                    self.assertEqual(r['offer_title'],offer['title'])
                    self.assertEqual(r['category'],offer['category'])
                    self.assertEqual(r['price_eur'],float(offer['price_eur']))
                    self.assertEqual(r['discount_pct'],int(offer['discount_pct']))
                    self.assertTrue(r['match_reason'])

    def test_no_garmin_personal_activity_output(self):
        out=self.output(garmin=False);p=out['profile']
        self.assertEqual(p['sport_shares'],{})
        for key in ['segment_label','cluster_id','regression_prediction','input_features',
                    'input_week_end','target_week_start','target_week_end']:
            self.assertIsNone(p[key],key)
        self.assertNotIn('segment_period_end',p)
        for key in ['segment_status','sport_profile_status','prediction_status']:
            self.assertEqual(p[key],'permission_denied')
        self.assertTrue(out['interest_categories'])
        self.assertTrue(all(r['ranking_tier']=='B' for r in out['recommendations']))

    def test_interest_permission_is_independent(self):
        out=self.output(interests=False)
        self.assertEqual(out['interest_categories'],[])
        self.assertEqual(out['recommendations'],[])
        self.assertEqual(out['personalization_status'],'interests_permission_denied')
        self.assertEqual(out['profile']['prediction_status'],'available')
        self.assertTrue(out['profile']['sport_shares'])
        flags=out['permissions_simulated']
        self.assertIs(flags['simulated'],True)
        self.assertIs(flags['real_consent_record'],False)

    def test_unavailable_contexts_preserve_categories(self):
        data=copy.deepcopy(self.data);data.clusters={};data.weeks=[]
        out=self.output(data=data)
        self.assertIsNone(out['profile']['segment_label'])
        self.assertEqual(out['profile']['segment_status'],'missing_or_ineligible')
        self.assertIsNone(out['profile']['regression_prediction'])
        self.assertEqual(out['profile']['prediction_status'],'insufficient_history')
        self.assertTrue(out['interest_categories'])
        self.assertTrue(out['recommendations'])
        self.assertEqual(json.loads(json.dumps(out,allow_nan=False)),out)

    def test_invalid_sports_do_not_expose_raw_values(self):
        data=copy.deepcopy(self.data);data.profiles['U001']['share_running']='nan'
        out=self.output(data=data)
        self.assertEqual(out['profile']['sport_shares'],{})
        self.assertEqual(out['profile']['sport_profile_status'],'invalid_profile')
        json.dumps(out,allow_nan=False)

    def test_deterministic_for_all_permission_combinations(self):
        for ip in [False,True]:
            for gp in [False,True]:
                first=self.output(interests=ip,garmin=gp)
                second=self.output(interests=ip,garmin=gp)
                self.assertEqual(json.dumps(first,sort_keys=True,allow_nan=False),
                                 json.dumps(second,sort_keys=True,allow_nan=False))
                self.assertLessEqual(len(first['recommendations']),5)


if __name__=='__main__':unittest.main()
