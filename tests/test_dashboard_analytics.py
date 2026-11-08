"""AP 7.4: real saved results, analytic calculations, gates and Streamlit reruns."""
import ast
import csv
import json
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch
import numpy as np

ROOT=Path(__file__).resolve().parents[1]
sys.path[:0]=[str(ROOT),str(ROOT/'src')]
from dashboard.analytics_data import ResearchData,PermissionRequired,K_VALUES,RAW
from dashboard.data_access import DataAccessError
from streamlit.testing.v1 import AppTest


class ResearchTests(unittest.TestCase):
    def setUp(self):self.d=ResearchData()

    def test_understanding_actual_population_and_sport_filter(self):
        a=self.d.understanding();self.assertEqual((a['users'],a['weeks'],a['activities'],a['weekly_rows'],len(a['sports'])),(100,26,6465,2600,8))
        total=0
        for sport in a['sports']:
            b=self.d.understanding(sport);total+=b['selected_count']
            self.assertEqual(len(b['series']),26);self.assertEqual(b['series']['Aktivitäten'].sum(),b['selected_count'])
            self.assertAlmostEqual(b['share'],b['selected_count']/6465)
            self.assertNotIn('user_id',b['selected']);self.assertNotIn('activity_id',b['selected'])
        self.assertEqual(total,6465)

    def test_zero_denominators_mean_and_distribution(self):
        a=self.d.zero_weeks(True);b=self.d.zero_weeks(False)
        self.assertEqual((a['n'],a['zero_n'],b['n'],b['zero_n']),(2600,558,2042,0))
        self.assertAlmostEqual(a['mean'],6465/2600);self.assertAlmostEqual(b['mean'],6465/2042)
        self.assertAlmostEqual(a['relative_pct'],27.32615083251715)
        self.assertEqual(a['distribution'].Nutzerwochen.sum(),2600)
        self.assertFalse((b['distribution'].activities_count==0).any())

    def test_actual_pipeline_shapes_and_separate_inputs(self):
        expected={'Auswahl / Prüfung':((6465,6),(6465,5)),'Wochenaggregation':((6465,5),(2600,6)),
                  'K-Means-Features':((6465,5),(100,12)),'K-Means-Skalierung':((100,12),(100,10)),
                  'Regressionsfeatures':((2600,6),(2200,7)),'Modellinputs / Split':((2200,7),(1800,7))}
        for step,shapes in expected.items():
            r=self.d.pipeline(step);self.assertEqual((r['input_shape'],r['output_shape']),shapes)

    def test_scaling_matches_saved_values_without_fit(self):
        params=self.d.metadata('outputs/models/kmeans_scaling_params.json')
        with patch('sklearn.preprocessing.StandardScaler.fit',side_effect=AssertionError('fit')):
            for uid in ['U001','U002','U003']:
                for f in params['feature_order']:
                    r=self.d.scaling(uid,f,garmin_permission=True)
                    self.assertAlmostEqual(r['z'],(r['x']-r['mean'])/r['scale'])
                    self.assertAlmostEqual(r['weighted'],r['z']*r['weight'])
                    self.assertAlmostEqual(r['weight'],1 if f=='avg_activities_per_week' else 1/np.sqrt(8))

    def test_chronological_split_counts_and_target_boundaries(self):
        r=self.d.split();m=r['manifest']
        self.assertEqual((r['all_rows'],r['train_rows'],r['test_rows']),(2200,1800,400))
        self.assertEqual(m['test_target_weeks'],[23,24,25,26])
        self.assertLess(m['train_target_date_range'][1],m['test_target_date_range'][0])

    def test_k_choices_saved_scores_final_profiles_and_no_fit(self):
        with patch('sklearn.cluster.KMeans.fit',side_effect=AssertionError('fit')):
            for k,expected in zip(K_VALUES,[.30333715184382104,.18464238109971873,.19430902295353497,.20612962999737008]):
                r=self.d.kmeans(k)
                self.assertAlmostEqual(r['selected'].silhouette_score,expected)
                self.assertEqual(r['profiles'].n_users.tolist(),[57,43])
                self.assertEqual(r['metadata']['n_clusters'],2)
        with self.assertRaises(DataAccessError):self.d.kmeans(5)

    def test_regression_parameters_and_all_400_testcases(self):
        m=self.d.regression_metadata()
        self.assertEqual(m['feature_order'],['activities_current_week','avg_activities_last_4_weeks'])
        self.assertAlmostEqual(m['intercept'],.8397931020190079)
        self.assertAlmostEqual(m['coefficients']['activities_current_week'],.22819007785063997)
        # Fresh request per case is unnecessary: request-scoped verified bytes are reused only here.
        for i in range(1,101):
            for w in [22,23,24,25]:
                c=self.d.regression_case(f'U{i:03}',w,garmin_permission=True);p=c['prediction'];b=c['baseline']
                self.assertAlmostEqual(sum(c['contributions']),p['predicted_activities_next_week'],places=11)
                self.assertEqual(len(c['history']),4)
                self.assertTrue((c['history'].week_index<=w).all())
                self.assertEqual(b['baseline_prediction'],p['activities_current_week'])
                self.assertAlmostEqual(b['regression_absolute_error'],abs(b['regression_prediction']-b['actual_activities_next_week']))

    def test_evaluation_totals_rmse_and_zero_groups(self):
        all_=self.d.evaluation();zero=self.d.evaluation(group='Zielwoche = 0');positive=self.d.evaluation(group='Zielwoche > 0')
        self.assertEqual((all_['n'],zero['n'],positive['n']),(400,92,308))
        self.assertAlmostEqual(all_['regression_mae'],1.4898770575225395)
        self.assertAlmostEqual(all_['baseline_mae'],1.71)
        self.assertAlmostEqual(all_['improvement_pct'],12.872686694588332)
        self.assertAlmostEqual(all_['regression_rmse'],1.9085376545370092)
        self.assertAlmostEqual(zero['regression_mae'],1.8782923959526365)
        self.assertAlmostEqual(zero['baseline_mae'],1.3804347826086956)
        self.assertLess(zero['improvement_pct'],0)
        self.assertEqual(sum(self.d.evaluation(w)['n'] for w in range(23,27)),400)

    def test_recommendation_totals_have_no_individual_examples(self):
        r=self.d.recommendation_totals()
        self.assertEqual((r['users'],r['change_groups']['unchanged'],r['change_groups']['composition_changed']),(100,36,64))
        self.assertEqual((r['slots_before'],r['slots_after'],r['tier_a_after'],r['users_with_tier_a']),(475,475,344,81))
        self.assertAlmostEqual(r['tier_a_after_pct'],344/475*100)
        self.assertNotIn('examples',r)

    def test_recommendation_engine_replay_all_users_without_model_loading(self):
        with patch('joblib.load',side_effect=AssertionError('unneeded model inference')):
            for i in range(1,101):
                r=self.d.recommendation_case(f'U{i:03}',garmin_permission=True,interests_permission=True)
                self.assertTrue(all(o['ranking_tier']=='B' for o in r['before']))
                self.assertLessEqual(len(r['after']),5)
                self.assertEqual(len({o['offer_id'] for o in r['after']}),len(r['after']))

    def test_all_personal_gates_before_source_reads(self):
        with patch.object(self.d,'table',side_effect=AssertionError('read')):
            for fn in [lambda:self.d.scaling('U001','share_running',garmin_permission=False),
                       lambda:self.d.cluster_for_user('U001',garmin_permission=False),
                       lambda:self.d.regression_case('U001',22,garmin_permission=False),
                       lambda:self.d.recommendation_case('U001',garmin_permission=False,interests_permission=True),
                       lambda:self.d.recommendation_case('U001',garmin_permission=True,interests_permission=False)]:
                with self.assertRaises(PermissionRequired):fn()

    def test_missing_or_changed_source_no_fallback(self):
        with tempfile.TemporaryDirectory() as tmp:
            d=ResearchData(tmp)
            with self.assertRaises(DataAccessError):d.understanding()
        with patch.object(self.d.root.__class__,'read_bytes',return_value=b'altered'):
            with self.assertRaises(DataAccessError):self.d.understanding()

    def test_request_isolation(self):
        a=self.d.scaling('U001','share_running',garmin_permission=True)
        b=ResearchData().scaling('U002','share_running',garmin_permission=True)
        self.assertNotEqual(a['x'],b['x'])
        a['features'].iloc[0,0]=999
        fresh=self.d.scaling('U001','share_running',garmin_permission=True)
        self.assertNotEqual(fresh['features'].iloc[0,0],999)

    def test_iteration_uses_paired_control_not_historical_frequency_change(self):
        r=self.d.iteration('Top2_Mittel_%')
        self.assertAlmostEqual(r.Wert.iloc[2]-r.Wert.iloc[1],6.50673885865432)
        f=self.d.iteration('Aktivitaeten');self.assertEqual(f.Wert.tolist(),[6665,6465,6465])


class LabAppTests(unittest.TestCase):
    def app(self):
        a=AppTest.from_file(str(ROOT/'app.py'),default_timeout=20).run()
        a.segmented_control[0].set_value('ANALYTICS LAB').run()
        self.assertEqual(len(a.exception),0)
        return a

    def test_all_seven_sections_without_grants_and_no_individual_data(self):
        a=self.app()
        for section in ['Data Understanding','Data Preparation','K-Means','Regression','Evaluation','Empfehlungssystem','CRISP-DM']:
            a.sidebar.radio[0].set_value(section).run()
            self.assertEqual(len(a.exception),0,section);self.assertEqual(len(a.error),0,section)
            self.assertGreater(len(a.get('plotly_chart')),0,section)
            if section in ['K-Means','Regression','Empfehlungssystem']:
                self.assertTrue(any('gesperrt' in x.value for x in a.info))
        a.segmented_control[0].set_value('USER VIEW').run()
        self.assertEqual(a.selectbox[0].value,'U001')
        self.assertEqual([t.value for t in a.toggle],[False,False])

    def test_null_switch_scaling_and_k_variants(self):
        a=self.app();a.sidebar.radio[0].set_value('Data Preparation').run()
        next(w for w in a.radio if w.key=='zero_variant').set_value('Ohne Nullwochen').run()
        self.assertTrue(any(m.value=='2.042' for m in a.metric))
        next(w for w in a.segmented_control if w.key=='prep_experiment').set_value('Skalierung').run()
        self.assertTrue(any('gesperrt' in x.value for x in a.info))
        a.toggle[1].set_value(True).run()
        next(w for w in a.selectbox if w.key=='scale_feature').select('share_running').run()
        for step in [1,2,3,4]:
            next(w for w in a.slider if w.key=='scale_step').set_value(step).run()
            self.assertEqual(len(a.exception),0)
        a.sidebar.radio[0].set_value('K-Means').run()
        for k in [2,3,6,8]:
            next(w for w in a.selectbox if w.key=='cluster_k').select(k).run()
            self.assertEqual(len(a.exception),0)

    def test_regression_case_and_interest_gate_user_switch(self):
        a=self.app();a.sidebar.radio[0].set_value('Regression').run()
        a.toggle[1].set_value(True).run()
        for week in [23,24,25,26]:
            next(w for w in a.selectbox if w.key=='reg_week').select(week).run()
            self.assertEqual(len(a.exception),0)
        a.sidebar.radio[0].set_value('Empfehlungssystem').run()
        self.assertTrue(any('Interessenfreigabe' in x.value for x in a.info))
        a.toggle[0].set_value(True).run()
        self.assertEqual(len(a.exception),0);self.assertTrue(any('<div class="mova-compare-title">' in x.value for x in a.markdown))
        a.selectbox[0].select('U002').run()
        self.assertEqual([t.value for t in a.toggle],[False,False])
        # Public ML examples name shoes too; only personal comparison cards must disappear.
        self.assertFalse(any('<div class="mova-compare-title">' in x.value for x in a.markdown))

    def test_no_lab_training_calls(self):
        for file in ['analytics_data.py','analytics_view.py','ml_integration.py']:
            tree=ast.parse((ROOT/'dashboard'/file).read_text())
            for node in ast.walk(tree):
                if isinstance(node,ast.Call) and isinstance(node.func,ast.Attribute):
                    self.assertNotIn(node.func.attr,('fit','fit_predict','fit_transform','train','predict','rank_offers'))


if __name__=='__main__':unittest.main()
