"""Persistenzvergleich nur aus vorhandenen V2-Dateien, ohne Modellaufrufe."""
import sys
import unittest
from pathlib import Path
from unittest.mock import patch
import numpy as np
import pandas as pd
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'src'))
import modeling_regression_baseline as baseline


class BaselineTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.table,cls.metrics=baseline.compare()
        cls.test=pd.read_csv(baseline.ROOT/baseline.SOURCES[0],float_precision='round_trip')
        cls.predictions=pd.read_csv(baseline.ROOT/baseline.SOURCES[1],float_precision='round_trip')

    def test_comparison_without_model_training_or_prediction(self):
        with patch('sklearn.linear_model.LinearRegression.fit',side_effect=AssertionError('Training')),\
             patch('sklearn.linear_model.LinearRegression.predict',side_effect=AssertionError('Neue Prognose')),\
             patch('joblib.load',side_effect=AssertionError('Kein Modell nötig')):
            table,result=baseline.compare()
        pd.testing.assert_frame_equal(table,self.table)
        self.assertEqual(result,self.metrics)

    def test_join_is_by_keys_and_order_independent(self):
        actual=baseline.align(self.test.iloc[::-1],self.predictions.iloc[::-1])
        pd.testing.assert_frame_equal(actual,self.table)
        self.assertEqual(self.table.user_id.nunique(),100)
        self.assertEqual(self.table.groupby('user_id').size().unique().tolist(),[4])

    def test_duplicate_missing_or_changed_keys_rejected(self):
        for bad in [self.predictions.iloc[:-1],pd.concat([self.predictions.iloc[1:],self.predictions.iloc[[1]]])]:
            with self.assertRaises(ValueError):baseline.align(self.test,bad)
        bad=self.predictions.copy();bad.loc[0,'user_id']='UNKNOWN'
        with self.assertRaises(ValueError):baseline.align(self.test,bad)

    def test_changed_target_or_inputs_rejected(self):
        for col in ['actual_activities_next_week','activities_current_week','avg_activities_last_4_weeks']:
            bad=self.predictions.copy();bad.loc[0,col]+=1
            with self.assertRaises(ValueError):baseline.align(self.test,bad)

    def test_metrics_from_export_independently(self):
        t=pd.read_csv(baseline.ROOT/'outputs/tables/regression_baseline_comparison.csv',float_precision='round_trip')
        np.testing.assert_array_equal(t.baseline_prediction,t.activities_current_week)
        for method in ['regression','baseline']:
            error=t[method+'_prediction'].to_numpy()-t.actual_activities_next_week.to_numpy()
            self.assertAlmostEqual(sum(abs(error))/400,self.metrics[method]['mae'])
            self.assertAlmostEqual(np.sqrt(sum(error**2)/400),self.metrics[method]['rmse'])
            self.assertAlmostEqual(error.mean(),self.metrics[method]['mean_signed_error'])
        np.testing.assert_allclose(t.absolute_error_difference,t.baseline_absolute_error-t.regression_absolute_error,
                                   atol=1e-14,rtol=1e-14)
        self.assertAlmostEqual(t.absolute_error_difference.mean(),self.metrics['absolute_mae_improvement'])

    def test_improvement_sign_and_zero_denominator(self):
        self.assertEqual(baseline.improvement(2,1),dict(absolute_mae_improvement=1.,relative_mae_improvement_pct=50.))
        self.assertEqual(baseline.improvement(1,2)['relative_mae_improvement_pct'],-100.)
        self.assertIsNone(baseline.improvement(0,1)['relative_mae_improvement_pct'])
        self.assertEqual(baseline.improvement(0,1)['absolute_mae_improvement'],-1.)

    def test_group_counts_and_mae_consistency(self):
        outcomes=self.metrics['individual_outcomes']
        self.assertEqual(sum(g['count'] for g in outcomes.values()),400)
        self.assertAlmostEqual(sum(g['share'] for g in outcomes.values()),1)
        self.assertEqual(outcomes['regression_better']['count'],int((self.table.absolute_error_difference>0).sum()))
        for groups in [self.metrics['by_target_week'],list(self.metrics['by_actual_group'].values())]:
            self.assertEqual(sum(g['n_observations'] for g in groups),400)
            for method in ['regression','baseline']:
                self.assertAlmostEqual(sum(g[method]['mae']*g['n_observations'] for g in groups)/400,
                                       self.metrics[method]['mae'])
        self.assertEqual(self.metrics['by_actual_group']['actual_zero']['n_observations'],92)


if __name__=='__main__':unittest.main()
