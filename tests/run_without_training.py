"""Discover the complete test suite, explicitly skip legacy training checks.

Run from repository root: .venv/bin/python tests/run_without_training.py
Existing test files and training implementations remain unchanged.
"""
from pathlib import Path
import sys
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT), str(ROOT / 'src')]


def main():
    suite = unittest.defaultTestLoader.discover(str(ROOT / 'tests'))
    # These classes fit models in setUpClass, even for their validation methods.
    for module_name in ('test_modeling_kmeans_k_selection', 'test_modeling_kmeans_stability'):
        module = sys.modules[module_name]
        for value in vars(module).values():
            if isinstance(value, type) and issubclass(value, unittest.TestCase):
                unittest.skip('AP 7.3: Klassen-Setup trainiert K-Means; Training ausdrücklich untersagt.')(value)
    methods = {
        'test_cycle2': ['test_exact_six_fits_training_only_and_frozen_prediction'],
        'test_modeling_kmeans_final': ['test_no_scaling_and_exact_input_reproduction'],
        'test_modeling_regression_train': ['test_training_without_test_access_scaling_or_scoring',
                                         'test_loaded_training_predictions_equal_fresh_fit']}
    # Resolve the actual class name from the loaded module, fail if the method disappeared.
    for module_name, names in methods.items():
        module = sys.modules[module_name]
        for method in names:
            found=False
            for value in list(vars(module).values()):
                if isinstance(value,type) and issubclass(value,unittest.TestCase) and hasattr(value,method):
                    setattr(value,method,unittest.skip('AP 7.3: Dieser Test trainiert ein neues Modell.')(getattr(value,method)))
                    found=True
            if not found:raise RuntimeError(f'Unbekannter Trainingstest: {module_name}.{method}')
    # Any overlooked training path must fail rather than silently fit.
    with patch('sklearn.cluster.KMeans.fit', side_effect=AssertionError('Training in AP 7.3 verboten')), \
         patch('sklearn.linear_model.LinearRegression.fit', side_effect=AssertionError('Training in AP 7.3 verboten')), \
         patch('sklearn.preprocessing.StandardScaler.fit', side_effect=AssertionError('Scaler-Fit in AP 7.3 verboten')):
        result=unittest.TextTestRunner(verbosity=2).run(suite)
    return 0 if result.wasSuccessful() else 1


if __name__=='__main__':
    raise SystemExit(main())
