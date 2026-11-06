"""Runtime must work from source archives/shallow clones, without historical Git objects."""
import os
from pathlib import Path
import shutil
import sys
import tempfile
import unittest
from unittest.mock import patch

ROOT=Path(__file__).resolve().parents[1]
sys.path[:0]=[str(ROOT),str(ROOT/'src')]
import recommendation_engine as e
from dashboard.data_access import check_engine_basis, DataAccessError
from dashboard.analytics_data import ResearchData


class DeploymentPortabilityTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.temp=tempfile.TemporaryDirectory()
        cls.addClassCleanup(cls.temp.cleanup)
        cls.root=Path(cls.temp.name)/'source'
        shutil.copytree(ROOT,cls.root,ignore=shutil.ignore_patterns('.git','work','.venv','__pycache__'))

    def test_u070_from_source_archive_and_other_working_directory(self):
        old=os.getcwd()
        try:
            os.chdir(self.temp.name)
            with patch('subprocess.check_output',side_effect=AssertionError('No runtime Git')):
                result=e.run('U070',interests_permission=True,garmin_permission=True,root=self.root)
                self.assertTrue(check_engine_basis(self.root))
        finally:
            os.chdir(old)
        self.assertEqual([o['offer_id'] for o in result['recommendations']],['O032','O034','O035','O006','O004'])
        self.assertTrue(result['recommendations'][0]['kmeans_influence'])
        self.assertTrue(result['recommendations'][1]['regression_influence'])
        self.assertIn('langfristiges Aktivitätssegment',result['recommendations'][0]['match_reason'])
        self.assertIn('keine Teilnahmevoraussetzung',result['recommendations'][1]['match_reason'])
        self.assertEqual(result['profile']['target_week_start'],'2026-07-06')

    def test_lab_verification_without_git_and_tampering_rejected(self):
        with patch('subprocess.check_output',side_effect=AssertionError('No runtime Git')):
            lab=ResearchData(self.root)
            self.assertEqual(lab.understanding()['users'],100)
            self.assertEqual(lab.cluster_for_user('U070',garmin_permission=True)['cluster_id'],1)
        # Modify only a temporary copy, never the original files.
        path=self.root/'data/processed/user_clusters.csv'; original=path.read_bytes()
        try:
            path.write_bytes(original.replace(b'U070,1,',b'U070,0,'))
            self.assertFalse(check_engine_basis(self.root))
            with self.assertRaises(ValueError):e.verify_tracked_bytes(self.root,'data/processed/user_clusters.csv')
            with self.assertRaises(DataAccessError):ResearchData(self.root).table('data/processed/user_clusters.csv')
        finally:
            path.write_bytes(original)

    def test_user_view_with_no_historical_git_access(self):
        from streamlit.testing.v1 import AppTest
        app=AppTest.from_file(str(ROOT/'app.py'),default_timeout=30).run()
        app.selectbox[0].select('U070').run()
        for toggle in app.toggle:toggle.set_value(True)
        with patch('subprocess.check_output',side_effect=AssertionError('No runtime Git')):
            app.run()
        self.assertFalse(app.exception);self.assertFalse(app.error)
        cards=[x.value for x in app.markdown if 'class="mova-offer"' in x.value]
        self.assertEqual(len(cards),5)
        self.assertTrue(all(oid in card for oid,card in zip(['O032','O034','O035','O006','O004'],cards)))
        self.assertIn('langfristiges Aktivitätssegment',cards[0])
        self.assertIn('keine Teilnahmevoraussetzung',cards[1])


if __name__=='__main__':unittest.main()
