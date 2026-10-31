"""AP 5.7: Nachweis unveränderter Ergebnisse und Diagnose ohne Modellaufrufe."""
import copy
import json
import sys
import unittest
from pathlib import Path
from unittest.mock import patch
import numpy as np
import pandas as pd
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'src'))
import modeling_evaluation_summary as summary


class EvaluationSummaryTests(unittest.TestCase):
    def test_no_training_model_loading_or_prediction(self):
        with patch('joblib.load',side_effect=AssertionError('Kein Modell laden')),\
             patch('sklearn.cluster.KMeans.fit',side_effect=AssertionError('Fit verboten')),\
             patch('sklearn.linear_model.LinearRegression.fit',side_effect=AssertionError('Fit verboten')),\
             patch('sklearn.linear_model.LinearRegression.predict',side_effect=AssertionError('Predict verboten')):
            actual=summary.summarize()
        saved=json.loads((summary.ROOT/'outputs/tables/modeling_evaluation_summary.json').read_text())
        self.assertEqual(actual,saved)

    def test_metrics_match_original_files(self):
        actual=summary.summarize()
        read=lambda f:json.loads((summary.ROOT/'outputs/tables'/f).read_text())
        self.assertEqual(actual['baseline_comparison'],read('regression_baseline_metrics.json'))
        original=read('regression_test_metrics.json')
        for key,value in original.items():self.assertEqual(actual['regression'][key],value)
        self.assertFalse(actual['real_user_production_validated'])

    def test_current_week_diagnosis_independent(self):
        actual=summary.summarize()
        table=pd.read_csv(summary.ROOT/'outputs/tables/regression_baseline_comparison.csv',float_precision='round_trip')
        for name,mask in [('current_week_zero',table.activities_current_week==0),
                          ('current_week_positive',table.activities_current_week>0)]:
            group=table[mask];saved=actual['current_week_diagnostics'][name]
            self.assertEqual(len(group),saved['n_observations'])
            for method in ['regression','baseline']:
                error=group[method+'_prediction']-group.actual_activities_next_week
                self.assertAlmostEqual(abs(error).mean(),saved[method]['mae'])
        self.assertEqual(sum(g['n_observations'] for g in actual['current_week_diagnostics'].values()),400)

    def test_changed_kmeans_statistic_rejected(self):
        root=summary.ROOT
        read=lambda path:json.loads((root/path).read_text())
        k=read('outputs/models/kmeans_final_metadata.json');k['silhouette_score']+=.1
        with self.assertRaises(ValueError):
            summary.validate_sources(k,
                pd.read_csv(root/'outputs/tables/kmeans_k_selection.csv'),
                pd.read_csv(root/'outputs/tables/kmeans_candidate_comparison.csv'),
                pd.read_csv(root/'outputs/tables/kmeans_final_cluster_profiles.csv'),
                read('outputs/tables/regression_test_metrics.json'),read('outputs/tables/regression_baseline_metrics.json'),
                pd.read_csv(root/'outputs/tables/regression_baseline_comparison.csv'))

    def test_changed_regression_metric_rejected(self):
        with patch.object(summary,'close',wraps=summary.close):
            original=summary.baseline.summarize
            def changed(table):
                result=original(table);result['regression']['mae']+=.1
                return result
            with patch.object(summary.baseline,'summarize',side_effect=changed):
                with self.assertRaises(ValueError):summary.summarize()


if __name__=='__main__':unittest.main()
