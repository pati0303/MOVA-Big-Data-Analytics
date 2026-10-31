"""AP 6.2 tests. F-prefixed offers and modified in-memory records are fixtures,
not V2 catalog facts. No model is trained or source CSV changed.
"""
import copy
import csv
from datetime import date
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'src'))
import recommendation_engine as e


class RecommendationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.data = e.load_data(include_activity=True)

    def call(self, data=None, uid='U001', interests=True, garmin=True, as_of=e.PROFILE_END):
        return e.recommend_user(data or self.data, uid, interests_permission=interests,
                                garmin_permission=garmin, as_of=as_of)

    def test_categories_strict_boolean(self):
        user = dict.fromkeys(e.INTERESTS, 'False'); user['interest_outdoor'] = 'True'
        self.assertEqual(e.interest_categories(user), {'Outdoor'})
        user['interest_sport'] = 'false'
        with self.assertRaises(ValueError): e.interest_categories(user)

    def test_multiple_interests_filter(self):
        result = self.call(garmin=False)
        cats = e.interest_categories(self.data.users['U001'])
        self.assertGreater(len(cats), 1)
        self.assertTrue(all(r['category'] in cats for r in result['recommendations']))
        self.assertEqual(len({r['offer_id'] for r in result['recommendations']}), 5)

    def test_no_positive_interests(self):
        self.assertEqual(self.call(uid='U023')['recommendations'], [])
        self.assertEqual(self.call(uid='U023')['personalization_status'], 'no_positive_interests')

    def test_no_interest_permission(self):
        self.assertEqual(self.call(interests=False)['recommendations'], [])

    def test_no_garmin_access_or_leak(self):
        with patch.object(e, 'sport_profile', side_effect=AssertionError('activity access')), \
             patch('joblib.load', side_effect=AssertionError('model access')):
            out = self.call(garmin=False)
        self.assertIsNone(out['profile']['segment_label'])
        self.assertIsNone(out['profile']['regression_prediction'])
        self.assertTrue(all(x['ranking_tier'] == 'B' for x in out['recommendations']))
        with patch.object(e, 'verify_tracked_bytes', side_effect=AssertionError('activity read')):
            e.run('U001', interests_permission=True, garmin_permission=False)

    def test_explicit_permissions(self):
        with self.assertRaises(TypeError): e.run('U001')
        for bad in [None, 'True', 1]:
            with self.assertRaises(ValueError): self.call(garmin=bad)

    def fixtures(self):
        offers = [dict(offer_id=oid, title='TEST FIXTURE', category='Sport', price_eur='10', discount_pct='0')
                  for oid in ['F003', 'F002', 'F001', 'F004']]
        return offers, {'F001': ('Running',), 'F002': ('Cycling',), 'F003': ('Running', 'Cycling')}

    def test_confirmed_sports_order_maximum_and_tie(self):
        offers, tags = self.fixtures()
        out = e.recommendations('TEST', offers, {'Sport'}, tags, {'Running': .2, 'Cycling': .6})
        self.assertEqual([x['offer_id'] for x in out], ['F002', 'F003', 'F001', 'F004'])
        self.assertEqual([x['ranking_tier'] for x in out], ['A', 'A', 'A', 'B'])
        self.assertIn('Cycling', out[0]['match_reason'])
        self.assertEqual(out, e.recommendations('TEST', offers[::-1], {'Sport'}, tags, {'Running': .2, 'Cycling': .6}))

    def test_zero_share_and_untagged_remain_eligible(self):
        offers, tags = self.fixtures()
        out = e.recommendations('TEST', offers, {'Sport'}, tags, {'Running': 0, 'Cycling': 0})
        self.assertEqual([x['offer_id'] for x in out], ['F001', 'F002', 'F003', 'F004'])
        self.assertTrue(all(x['ranking_tier'] == 'B' for x in out))

    def test_approval_boundary(self):
        offers, _ = self.fixtures()
        with tempfile.TemporaryDirectory(dir=e.ROOT / 'work') as td:
            p = Path(td) / 'approval.csv'
            fields = ['offer_id','title','sport_tags','review_status','reviewed_by','reviewed_at']
            def write(status):
                with p.open('w', newline='') as f:
                    w=csv.DictWriter(f, fieldnames=fields);w.writeheader()
                    w.writerow(dict(offer_id='F001',title='TEST FIXTURE',sport_tags='Running',review_status=status,
                                    reviewed_by='TEST reviewer',reviewed_at='2026-10-31'))
            write('proposed_unambiguous_pending_review')
            self.assertEqual(e.load_confirmed_tags(p, offers), {})
            write('manually_confirmed')
            self.assertEqual(e.load_confirmed_tags(p, offers), {'F001': ('Running',)})
            offers[2]['title']='CHANGED TITLE'
            with self.assertRaises(ValueError):e.load_confirmed_tags(p, offers)

    def test_actual_manual_approvals_and_pending_proposals(self):
        expected = {'O001': ('Running',), 'O003': ('Swimming',), 'O004': ('Tennis',),
                    'O005': ('Padel',), 'O006': ('Cycling',), 'O007': ('Strength',),
                    'O009': ('Hiking',), 'O010': ('Hiking',)}
        self.assertEqual(self.data.approved_tags, expected)
        approved = e.read_csv(e.ROOT/'documentation/offer_sport_tags_approved.csv')
        self.assertEqual(len(approved), 8)
        self.assertEqual(len({r['offer_id'] for r in approved}), 8)
        catalog = {r['offer_id']: r for r in self.data.offers}
        for row in approved:
            self.assertEqual(row['review_status'], 'manually_confirmed')
            self.assertEqual(row['title'], catalog[row['offer_id']]['title'])
            self.assertIn(row['sport_tags'], e.SPORTS)
        rows = e.read_csv(e.ROOT/'documentation/offer_sport_mapping_review.csv')
        self.assertEqual(len(rows), 30)
        self.assertTrue(all(x['review_status'].endswith('pending_review') for x in rows))
        # Review proposals alone never count as confirmations, even now.
        self.assertEqual(e.load_confirmed_tags(
            e.ROOT/'documentation/offer_sport_mapping_review.csv', self.data.offers), {})
        self.assertNotIn('O002', self.data.approved_tags)
        self.assertNotIn('O011', self.data.approved_tags)

    def test_actual_approved_tiers_and_sort_order(self):
        shares, status = e.sport_profile(self.data, 'U001', e.PROFILE_END)
        self.assertEqual(status, 'available')
        categories = e.interest_categories(self.data.users['U001'])
        ranked = e.rank_offers(e.filter_offers(self.data.offers, categories),
                               self.data.approved_tags, shares)
        keys = []
        for tier, _, oid, offer, matching in ranked:
            observed = [shares[s] for s in self.data.approved_tags.get(oid, ()) if shares[s] > 0]
            self.assertEqual(tier, 0 if observed else 1)
            keys.append((tier, -max(observed, default=0), oid))
            self.assertIn(offer['category'], categories)
            if oid in ('O002', 'O011'):
                self.assertEqual(tier, 1)
                self.assertEqual(matching, [])
        self.assertTrue(any(key[0] == 0 for key in keys))
        self.assertTrue(any(key[0] == 1 for key in keys))
        self.assertEqual(keys, sorted(keys))
        actual = self.call()['recommendations']
        self.assertEqual([r['offer_id'] for r in actual], [r[2] for r in ranked[:5]])

    def test_top_five_and_positions(self):
        out=self.call()['recommendations']
        self.assertLessEqual(len(out),5)
        self.assertEqual([x['ranking_position'] for x in out], list(range(1,len(out)+1)))
        for row in out:self.assertTrue(row['match_reason'])

    def test_missing_cluster_independent(self):
        data=copy.deepcopy(self.data);data.clusters={}
        out=self.call(data)
        self.assertIsNone(out['profile']['segment_label'])
        self.assertEqual(out['profile']['prediction_status'],'available')
        self.assertTrue(out['recommendations'])

    def test_model_context_does_not_rank(self):
        baseline = self.call()['recommendations']
        data = copy.deepcopy(self.data)
        data.clusters['U001'] = dict(user_id='U001', cluster_id='1',
                                    segment_label='Höhere Trainingshäufigkeit')
        # In-memory context fixtures only; same authorised sport profile.
        with patch.object(e, 'predict_activity', return_value=dict(
                regression_prediction=999.0, prediction_status='TEST_CONTEXT')):
            changed = self.call(data)
        self.assertEqual(changed['profile']['segment_label'], 'Höhere Trainingshäufigkeit')
        self.assertEqual(changed['profile']['regression_prediction'], 999.0)
        self.assertEqual(baseline, changed['recommendations'])

    def test_four_weeks_current_included_and_model_math(self):
        out=self.call()['profile']
        rows=sorted([r for r in self.data.weeks if r['user_id']=='U001'],key=lambda r:r['week_end'])[-4:]
        counts=[int(r['activities_count']) for r in rows]
        self.assertEqual(out['input_features'],dict(zip(e.FEATURES,[counts[-1],sum(counts)/4])))
        meta=json.loads((e.ROOT/'outputs/models/regression_linear_metadata.json').read_text())
        expected=meta['intercept']+sum(meta['coefficients'][k]*out['input_features'][k] for k in e.FEATURES)
        self.assertAlmostEqual(out['regression_prediction'],expected,places=13)
        self.assertEqual(out['target_week_start'],'2026-07-06')
        self.assertEqual(out['target_week_end'],'2026-07-12')

    def test_invalid_or_insufficient_weeks(self):
        for kind in ['short','gap','nan','negative','duplicate','calendar']:
            data=copy.deepcopy(self.data)
            data.weeks=sorted([r for r in data.weeks if r['user_id']=='U001'],key=lambda r:r['week_end'])[-4:]
            if kind=='short':data.weeks=data.weeks[:3]
            if kind=='gap':data.weeks[1]['week_end']='2026-06-07'
            if kind=='nan':data.weeks[-1]['activities_count']='nan'
            if kind=='negative':data.weeks[-1]['activities_count']='-1'
            if kind=='duplicate':data.weeks[-1]=data.weeks[-2].copy()
            if kind=='calendar':data.weeks[-1]['week_start']='2026-06-29'
            # Actual last start is June 29; deliberately use Tuesday instead.
            if kind=='calendar':data.weeks[-1]['week_start']='2026-06-30'
            with self.subTest(kind=kind):
                self.assertIsNone(self.call(data)['profile']['regression_prediction'])

    def test_no_future_observations_or_segment(self):
        cutoff=date(2026,6,14)
        first=self.call(as_of=cutoff)
        data=copy.deepcopy(self.data)
        for row in data.weeks:
            if row['week_end']>'2026-06-14':row['activities_count']='999999'
        self.assertEqual(first,self.call(data,as_of=cutoff))
        self.assertIsNone(first['profile']['segment_label'])
        self.assertEqual(first['profile']['input_week_end'],'2026-06-14')

    def test_no_future_training_information(self):
        out=self.call(as_of=date(2026,5,31))['profile']
        self.assertIsNone(out['regression_prediction'])
        self.assertEqual(out['prediction_status'],'model_training_after_cutoff')

    def test_inactive_profile_no_fabrication(self):
        data=copy.deepcopy(self.data);data.profiles['U001']['avg_activities_per_week']='0'
        out=self.call(data)
        self.assertEqual(out['profile']['sport_profile_status'],'inactive')
        self.assertIsNone(out['profile']['segment_label'])
        self.assertTrue(all(x['ranking_tier']=='B' for x in out['recommendations']))

    def test_unverified_and_unknown_sports(self):
        for attribute in ['records_verified','known_sports']:
            data=copy.deepcopy(self.data);setattr(data,attribute,False)
            out=self.call(data)
            self.assertIsNone(out['profile']['regression_prediction'])
            self.assertIsNone(out['profile']['segment_label'])
            self.assertTrue(out['recommendations'])

    def test_invalid_profile(self):
        data=copy.deepcopy(self.data);data.profiles['U001']['share_running']='nan'
        self.assertEqual(self.call(data)['profile']['sport_profile_status'],'invalid_profile')

    def test_missing_interests_and_unknown_user(self):
        data=copy.deepcopy(self.data);del data.users['U001']['interest_sport']
        self.assertEqual(self.call(data)['personalization_status'],'invalid_or_missing_interests')
        with self.assertRaises(ValueError):self.call(uid='NOT_A_USER')

    def test_no_training_and_no_target_file_access(self):
        from sklearn.cluster import KMeans
        from sklearn.linear_model import LinearRegression
        with patch.object(KMeans,'fit',side_effect=AssertionError('NO FIT')), \
             patch.object(LinearRegression,'fit',side_effect=AssertionError('NO FIT')), \
             patch.object(LinearRegression,'fit_predict',create=True,side_effect=AssertionError('NO FIT')):
            out=self.call()
        self.assertEqual(out['profile']['prediction_status'],'available')
        # Implementation never reads regression train/test/target feature tables.
        source=(e.ROOT/'src/recommendation_engine.py').read_text()
        self.assertNotIn('regression_train.csv',source)
        self.assertNotIn('regression_test.csv',source)
        self.assertNotIn('activities_next_week',source)

    def test_original_tracked_files_unchanged(self):
        tracked=subprocess.check_output(['git','-C',str(e.ROOT),'ls-tree','-r','HEAD'],text=True)
        for line in tracked.splitlines():
            metadata,path=line.split('\t'); mode,typ,sha=metadata.split()
            if typ=='blob':
                content=(e.ROOT/path).read_bytes()
                actual=hashlib.sha1(b'blob '+str(len(content)).encode()+b'\0'+content).hexdigest()
                self.assertEqual(actual,sha,path)

    def test_repeated_real_users_json_identical(self):
        for uid in ['U001','U002','U003']:
            first=json.dumps(self.call(uid=uid),sort_keys=True,allow_nan=False)
            second=json.dumps(self.call(uid=uid),sort_keys=True,allow_nan=False)
            self.assertEqual(first,second)


if __name__=='__main__':unittest.main()
