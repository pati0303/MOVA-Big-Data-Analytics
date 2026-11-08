"""Saved-ablation rendering and fail-closed input handling, without training."""
import hashlib
import json
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT), str(ROOT / 'src')]
from dashboard.data_access import DataAccessError
from dashboard.ml_integration import load_ablation
from streamlit.testing.v1 import AppTest


class MLIntegrationTests(unittest.TestCase):
    def test_saved_counts(self):
        self.assertEqual(load_ablation(), (100, dict(no_ml=0, kmeans_only=63, regression_only=9, both=63)))

    def test_missing_corrupt_and_inconsistent_results(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            with self.assertRaises(DataAccessError):
                load_ablation(root)
            directory = root / 'outputs/ml_recommendations_v1'
            directory.mkdir(parents=True)
            manifest = json.loads((ROOT / 'outputs/ml_recommendations_v1/manifest.json').read_bytes())
            (directory / 'manifest.json').write_text(json.dumps(manifest))
            (directory / 'comparison.json').write_text('{}')
            with self.assertRaises(DataAccessError):
                load_ablation(root)
            data = json.loads((ROOT / 'outputs/ml_recommendations_v1/comparison.json').read_bytes())
            data['summary']['changed_top5_vs_no_ml']['both'] = 62
            raw = json.dumps(data).encode()
            (directory / 'comparison.json').write_bytes(raw)
            manifest['artifact_sha256']['comparison.json'] = hashlib.sha256(raw).hexdigest()
            (directory / 'manifest.json').write_text(json.dumps(manifest))
            with self.assertRaises(DataAccessError):
                load_ablation(root)

    def app(self):
        app = AppTest.from_file(str(ROOT / 'app.py'), default_timeout=30).run()
        app.segmented_control[0].set_value('ANALYTICS LAB').run()
        app.sidebar.radio[0].set_value('Empfehlungssystem').run()
        return app

    def test_chart_and_separation(self):
        app = self.app()
        self.assertEqual(len(app.exception), 0)
        self.assertEqual(len(app.error), 0)
        figures = [json.loads(c.proto.spec) for c in app.get('plotly_chart')]
        bars = figures[-1]['data'][0]
        self.assertEqual(bars['text'], ['63 von 100', '9 von 100', '63 von 100'])
        self.assertTrue(any('64 veränderte' in s.value for s in app.success))
        self.assertTrue(any('Qualität' in s.value and '63 von 100' in s.value for s in app.success))

    def test_missing_ml_keeps_historical_comparison(self):
        with patch('dashboard.ml_integration.load_ablation', side_effect=DataAccessError('ML-Ablation nicht verfügbar')):
            app = self.app()
        self.assertEqual(len(app.exception), 0)
        self.assertTrue(any('ML-Ablation nicht verfügbar' in w.value for w in app.warning))
        self.assertTrue(any('64 veränderte' in s.value for s in app.success))
        self.assertEqual(len(app.get('plotly_chart')), 1)


if __name__ == '__main__':
    unittest.main()
