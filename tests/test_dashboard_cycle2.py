"""Saved-result and Streamlit checks; all fitting is prohibited."""
import hashlib
import json
from pathlib import Path
import shutil
import sys
import tempfile
import unittest
from unittest.mock import patch
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from dashboard.cycle2 import load_cycle2,TITLE
from dashboard.data_access import DataAccessError
from streamlit.testing.v1 import AppTest


class Cycle2DashboardTests(unittest.TestCase):
    def test_saved_results_and_decision_without_training(self):
        with patch('sklearn.linear_model.LinearRegression.fit',side_effect=AssertionError('No training')):
            r=load_cycle2()
        s=r['summary'].set_index('model')
        self.assertAlmostEqual(s.loc['persistence','mae'],1.7291666666666667)
        self.assertAlmostEqual(s.loc['linear_2','mae'],1.5226126103252913,places=6)
        self.assertAlmostEqual(s.loc['linear_3','mae'],1.5231053061786839,places=6)
        self.assertFalse(r['decision']['adopt_extended'])
        self.assertEqual(r['decision']['winning_folds'],2)
        self.assertEqual(len(r['fold_metrics']),9)
        self.assertEqual(r['validation']['folds'][2]['validation_target_weeks'],[19,22])

    def test_loader_reads_only_saved_cycle2_aggregates(self):
        original=Path.open
        allowed={'run_manifest.json','comparison.csv','metrics_by_fold.csv','zero_week_analysis.csv','decision.json','validation_manifest.json'}
        def guarded(path,*args,**kwargs):
            self.assertEqual(path.parent,ROOT/'outputs/cycle2')
            self.assertIn(path.name,allowed)
            return original(path,*args,**kwargs)
        with patch.object(Path,'open',guarded):load_cycle2()

    def test_missing_and_tampered_artifacts_fail_closed(self):
        with tempfile.TemporaryDirectory() as directory:
            root=Path(directory)
            with self.assertRaises(DataAccessError):load_cycle2(root)
            shutil.copytree(ROOT/'outputs/cycle2',root/'outputs/cycle2')
            p=root/'outputs/cycle2/comparison.csv';p.write_bytes(p.read_bytes()+b'\n')
            with self.assertRaises(DataAccessError):load_cycle2(root)

    def test_inconsistent_decision_even_with_updated_hash_rejected(self):
        with tempfile.TemporaryDirectory() as directory:
            root=Path(directory);shutil.copytree(ROOT/'outputs/cycle2',root/'outputs/cycle2')
            p=root/'outputs/cycle2/decision.json';d=json.loads(p.read_text());d['adopt_extended']=True;p.write_text(json.dumps(d))
            m=root/'outputs/cycle2/run_manifest.json';manifest=json.loads(m.read_text());manifest['artifact_sha256']['outputs/cycle2/decision.json']=hashlib.sha256(p.read_bytes()).hexdigest();m.write_text(json.dumps(manifest))
            with self.assertRaises(DataAccessError):load_cycle2(root)

    def test_app_start_new_page_and_return_to_user_view(self):
        with patch('sklearn.linear_model.LinearRegression.fit',side_effect=AssertionError('No training')),patch('sklearn.cluster.KMeans.fit',side_effect=AssertionError('No training')):
            app=AppTest.from_file(str(ROOT/'app.py'),default_timeout=30).run()
            self.assertFalse(app.exception)
            app.session_state['mode']='ANALYTICS LAB';app.session_state['lab_section']=TITLE;app.run()
            self.assertFalse(app.exception)
            self.assertFalse(app.error)
            self.assertEqual(len(app.get('plotly_chart')),3)
            self.assertTrue(any('Zusätzliches Merkmal verworfen.' in item.value for item in app.markdown))
            self.assertTrue(any('1,522613'==item.value for item in app.metric))
            app.session_state['mode']='USER VIEW';app.run();self.assertFalse(app.exception)


if __name__=='__main__':unittest.main()
