"""AP 7.3: independent observed-data checks and permission-bound real UI integration."""
import copy
import csv
from datetime import date
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT), str(ROOT / 'src')]
import recommendation_engine as engine
from dashboard.data_access import load_activity_summary, DataAccessError
from dashboard.services import user_context
from dashboard.charts import weekly_chart, sports_chart
from streamlit.testing.v1 import AppTest

EXPECTED = {
 'U001': (34,16,10,2086.0,'Running',2.6902546519777557, [('O001','A'),('O006','A'),('O009','A'),('O010','A'),('O002','B')]),
 'U002': (88,24,2,5227.7,'Walking',3.6927952445497203, [('O009','A'),('O010','A'),('O011','B'),('O012','B'),('O013','B')]),
 'U003': (54,19,7,2901.9,'Walking',2.005684418425836, [('O017','B'),('O018','B'),('O019','B'),('O020','B'),('O021','B')])}


def activity(uid='U001'):
    return load_activity_summary(uid, garmin_permission=True, verify_source=engine.verify_tracked_bytes)


class PersonalDataTests(unittest.TestCase):
    def test_examples_counts_means_and_pauses(self):
        for uid, (total,active,zero,minutes,top,*_) in EXPECTED.items():
            with self.subTest(uid=uid):
                a=activity(uid)
                self.assertEqual((a['total_activities'],a['active_weeks'],a['zero_weeks']), (total,active,zero))
                self.assertEqual(a['total_minutes'],minutes)
                self.assertAlmostEqual(a['avg_activities_per_week'],total/26)
                self.assertAlmostEqual(a['avg_minutes_per_week'],minutes/26)
                self.assertEqual(a['top_sports'],[top])
                self.assertGreater(total/active,a['avg_activities_per_week'])

    def test_full_26_weeks_and_sports_match_independent_raw_reference(self):
        with (ROOT/'data/raw/activities_simulated.csv').open() as f:
            rows=list(csv.DictReader(f))
        for uid in EXPECTED:
            a=activity(uid)
            self.assertEqual(len(a['weeks']),26)
            self.assertEqual([w['week_index'] for w in a['weeks']],list(range(1,27)))
            raw=[r for r in rows if r['user_id']==uid]
            from collections import Counter
            self.assertEqual(a['sport_counts'],dict(Counter(r['sport_type'] for r in raw)))
            for w in a['weeks']:
                subset=[r for r in raw if w['week_start']<=r['date']<=w['week_end']]
                self.assertEqual(w['activities_count'],len(subset))
                self.assertAlmostEqual(w['total_duration_min'],sum(float(r['duration_min']) for r in subset))

    def test_denied_means_no_reads_or_verification(self):
        with patch.object(Path,'open',side_effect=AssertionError('personal read')), \
             patch.object(engine,'verify_tracked_bytes',side_effect=AssertionError('verification reads')):
            self.assertIsNone(load_activity_summary('U001',garmin_permission=False,verify_source=engine.verify_tracked_bytes))

    def test_missing_source_fails_without_fabricated_weeks(self):
        with tempfile.TemporaryDirectory() as tmp:
            with self.assertRaises(DataAccessError):
                load_activity_summary('U001',garmin_permission=True,verify_source=engine.verify_tracked_bytes,root=tmp)

    def test_missing_week_not_zero_imputed(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp)
            (root/'data/processed').mkdir(parents=True)
            (root/'data/raw').mkdir(parents=True)
            (root/'data/raw/activities_simulated.csv').write_bytes((ROOT/'data/raw/activities_simulated.csv').read_bytes())
            with (ROOT/'data/processed/user_weekly_activities.csv').open() as f:
                rows=list(csv.DictReader(f))
            rows=[r for r in rows if not(r['user_id']=='U001' and r['week_index']=='1')]
            with (root/'data/processed/user_weekly_activities.csv').open('w') as f:
                writer=csv.DictWriter(f,fieldnames=list(rows[0]));writer.writeheader();writer.writerows(rows)
            # Isolate structural check; production always verifies the actual source hash.
            with self.assertRaises(DataAccessError):
                load_activity_summary('U001',garmin_permission=True,verify_source=lambda *_:None,root=root)

    def test_unknown_user_not_zero_activity_profile(self):
        with self.assertRaises(DataAccessError):activity('UNKNOWN')

    def test_chart_zero_markers_and_units(self):
        a=activity()
        counts=weekly_chart(a,'Aktivitäten');minutes=weekly_chart(a,'Trainingsminuten')
        self.assertEqual(len(counts.data[0].x),26)
        self.assertEqual(list(counts.data[0].y),[w['activities_count'] for w in a['weeks']])
        self.assertEqual(len(counts.data[1].x),10)
        self.assertTrue(all(y==0 for y in counts.data[1].y))
        self.assertEqual(list(minutes.data[0].y),[w['total_duration_min'] for w in a['weeks']])
        sport=sports_chart(a)
        self.assertEqual(sum(sport.data[0].x),34)
        self.assertAlmostEqual(sum(r[0] for r in sport.data[0].customdata),100)


class UserIntegrationTests(unittest.TestCase):
    def test_examples_saved_labels_predictions_and_rankings_without_fit(self):
        with patch('sklearn.cluster.KMeans.fit',side_effect=AssertionError('fit')), \
             patch('sklearn.linear_model.LinearRegression.fit',side_effect=AssertionError('fit')), \
             patch('sklearn.preprocessing.StandardScaler.fit',side_effect=AssertionError('fit')):
            with (ROOT/'data/processed/user_clusters.csv').open() as f:labels={r['user_id']:r for r in csv.DictReader(f)}
            for uid,e in EXPECTED.items():
                c=user_context(uid,interests_permission=True,garmin_permission=True)
                p=c['engine']['profile'];offers=c['engine']['recommendations']
                self.assertEqual(p['segment_label'],labels[uid]['segment_label'])
                self.assertEqual(p['cluster_id'],int(labels[uid]['cluster_id']))
                self.assertAlmostEqual(p['regression_prediction'],e[5],places=12)
                self.assertEqual((p['target_week_start'],p['target_week_end']),('2026-07-06','2026-07-12'))
                self.assertEqual([(o['offer_id'],o['ranking_tier']) for o in offers],e[6])
                self.assertLessEqual(len(offers),5)
                self.assertEqual(len({o['offer_id'] for o in offers}),len(offers))

    def test_all_four_permissions_and_zero_personal_activity_load_when_denied(self):
        for interests in (False,True):
            for garmin in (False,True):
                c=user_context('U001',interests_permission=interests,garmin_permission=garmin)
                r=c['engine'];p=r['profile']
                if not interests:self.assertEqual(r['recommendations'],[])
                if not garmin:
                    self.assertIsNone(c['activity'])
                    self.assertEqual(p['sport_shares'],{})
                    self.assertIsNone(p['cluster_id']);self.assertIsNone(p['regression_prediction'])
                    self.assertTrue(all(o['ranking_tier']=='B' for o in r['recommendations']))
        with patch('dashboard.data_access.load_activity_summary',side_effect=AssertionError('read')):
            c=user_context('U001',interests_permission=True,garmin_permission=False)
            self.assertEqual([o['offer_id'] for o in c['engine']['recommendations']],['O001','O002','O003','O004','O005'])

    def test_request_isolation_and_no_personal_cache(self):
        first=user_context('U001',interests_permission=True,garmin_permission=True)
        first['activity']['weeks'][0]['activities_count']=999
        second=user_context('U002',interests_permission=True,garmin_permission=False)
        self.assertEqual(second['engine']['user_id'],'U002');self.assertIsNone(second['activity'])
        again=user_context('U001',interests_permission=True,garmin_permission=True)
        self.assertEqual(again['activity']['weeks'][0]['activities_count'],0)

    def test_activity_failure_does_not_hide_eligible_offers(self):
        with patch('dashboard.data_access.load_activity_summary',side_effect=DataAccessError('Daten fehlen')):
            c=user_context('U001',interests_permission=True,garmin_permission=True)
        self.assertIsNone(c['activity']);self.assertEqual(c['activity_error'],'Daten fehlen')
        self.assertEqual(len(c['engine']['recommendations']),5)

    def test_missing_cluster_and_model_have_status_without_fake_values(self):
        real=user_context('U001',interests_permission=True,garmin_permission=True)
        data=engine.load_data(include_activity=True);data.clusters={}
        with patch.object(engine,'load_data',return_value=data):
            c=user_context('U001',interests_permission=True,garmin_permission=True)
        self.assertIsNone(c['engine']['profile']['cluster_id'])
        self.assertEqual(c['engine']['profile']['segment_status'],'missing_or_ineligible')
        with patch.object(engine,'predict_activity',return_value={**real['engine']['profile'],
                         'regression_prediction':None,'prediction_status':'model_unavailable_or_invalid'}):
            c=user_context('U001',interests_permission=True,garmin_permission=True)
        self.assertIsNone(c['engine']['profile']['regression_prediction'])
        self.assertEqual(c['engine']['profile']['prediction_status'],'model_unavailable_or_invalid')


class PersonalAppTests(unittest.TestCase):
    def app(self):
        app=AppTest.from_file(str(ROOT/'app.py'),default_timeout=20).run()
        self.assertEqual(len(app.exception),0)
        return app

    def test_complete_user_switch_units_and_revocation(self):
        app=self.app();self.assertEqual(len(app.get('plotly_chart')),0)
        app.toggle[0].set_value(True).run()
        self.assertEqual(len(app.get('plotly_chart')),0)
        self.assertTrue(any('O001' in m.value for m in app.markdown))
        app.toggle[1].set_value(True).run()
        self.assertEqual(len(app.exception),0)
        self.assertEqual(len(app.get('plotly_chart')),2)
        self.assertTrue(any('34' in m.value and 'mova-stat' in m.value for m in app.markdown))
        app.segmented_control[1].set_value('Trainingsminuten').run()
        self.assertEqual(len(app.exception),0)
        app.selectbox[0].select('U002').run()
        self.assertEqual([t.value for t in app.toggle],[False,False])
        self.assertEqual(len(app.get('plotly_chart')),0)
        self.assertFalse(any('mova-stat-value' in m.value and '<article' in m.value for m in app.markdown))
        app.toggle[1].set_value(True).run()
        self.assertTrue(any('88' in m.value and 'mova-stat' in m.value for m in app.markdown))
        app.toggle[1].set_value(False).run()
        self.assertEqual(len(app.get('plotly_chart')),0)
        self.assertFalse(any('geschätzte Aktivitäten' in m.value for m in app.markdown))

    def test_unavailable_contexts_render_without_previous_values(self):
        app=self.app()
        with patch('dashboard.user_view.user_context',side_effect=DataAccessError('Quelle fehlt')):
            app.toggle[1].set_value(True).run()
        self.assertEqual(len(app.exception),0)
        self.assertEqual(len(app.get('plotly_chart')),0)
        self.assertTrue(any('Quelle fehlt' in e.value for e in app.error))

    def test_lab_does_not_load_personal_context(self):
        app=self.app()
        app.segmented_control[0].set_value('ANALYTICS LAB').run()
        with patch('dashboard.user_view.user_context',side_effect=AssertionError('Lab leak')):
            app.toggle[1].set_value(True).run()
        self.assertEqual(len(app.exception),0)
        # AP 7.4 shows aggregate research charts, without a personal engine context.
        self.assertGreater(len(app.get('plotly_chart')),0)


if __name__=='__main__':unittest.main()
