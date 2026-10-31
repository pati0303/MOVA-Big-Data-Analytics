"""AP 5.5: gespeichertes Modell, echte V2, keine Fit-Aufrufe."""
import json
import sys
import unittest
from pathlib import Path
from unittest.mock import patch
import numpy as np
import pandas as pd
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'src'))
import modeling_regression_evaluate as evaluation


class RegressionEvaluationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.table,cls.weeks,cls.result=evaluation.evaluate()
        cls.frame=pd.read_csv(evaluation.ROOT/evaluation.TEST)

    def test_full_evaluation_with_training_and_scaling_blocked(self):
        with patch('sklearn.linear_model.LinearRegression.fit',side_effect=AssertionError('Fit verboten')),\
             patch('sklearn.preprocessing.StandardScaler.fit_transform',side_effect=AssertionError('Fit verboten')),\
             patch('sklearn.preprocessing.StandardScaler.fit',side_effect=AssertionError('Fit verboten')):
            table,weeks,result=evaluation.evaluate()
        pd.testing.assert_frame_equal(table,self.table)
        self.assertEqual(result,self.result)
        self.assertEqual(len(table),400);self.assertEqual(table.user_id.nunique(),100)

    def test_target_or_metadata_in_features_rejected(self):
        for features in [evaluation.FEATURES+['activities_next_week'],['activities_current_week','activities_next_week'],
                         evaluation.FEATURES[::-1],evaluation.FEATURES+['user_id']]:
            with self.assertRaises(ValueError):evaluation.select_features(self.frame,features)

    def test_invalid_data_or_weeks_rejected(self):
        for field,value in [('activities_current_week',np.inf),('activities_next_week',np.nan),
                            ('activities_next_week',-1),('activities_next_week',1.5),('week_index',21)]:
            bad=self.frame.copy();bad[field]=bad[field].astype(float);bad.loc[0,field]=value
            with self.assertRaises(ValueError):evaluation.validate_test(bad)
        bad=self.frame.copy();bad.loc[0]=bad.loc[1]
        with self.assertRaises(ValueError):evaluation.validate_test(bad)

    def test_future_information_in_history_detected(self):
        weekly=pd.read_csv(evaluation.ROOT/'data/processed/user_weekly_activities.csv')
        bad=self.frame.copy();bad.loc[0,'avg_activities_last_4_weeks']+=.25
        with self.assertRaises(ValueError):evaluation.check_history(bad,weekly)

    def test_errors_and_metrics_independently_from_export(self):
        table=pd.read_csv(evaluation.ROOT/'outputs/tables/regression_test_predictions.csv',float_precision='round_trip')
        error=table.predicted_activities_next_week.to_numpy()-table.actual_activities_next_week.to_numpy()
        np.testing.assert_allclose(table.prediction_error,error,atol=1e-14,rtol=1e-14)
        np.testing.assert_array_equal(table.absolute_error,np.abs(table.prediction_error))
        self.assertAlmostEqual(sum(abs(error))/400,self.result['mae'])
        self.assertAlmostEqual(np.sqrt(sum(error**2)/400),self.result['rmse'])
        self.assertAlmostEqual(sum(error)/400,self.result['mean_signed_error'])
        self.assertEqual(table[['user_id','week_index']].values.tolist(),
                         table.sort_values(['user_id','week_index'])[['user_id','week_index']].values.tolist())

    def test_weekly_and_zero_group_aggregation(self):
        self.assertEqual(self.weeks.target_week.tolist(),[23,24,25,26])
        self.assertEqual(self.weeks.n_observations.tolist(),[100]*4)
        self.assertAlmostEqual(self.weeks.mae.mean(),self.result['mae'])
        self.assertAlmostEqual(np.sqrt((self.weeks.rmse**2).mean()),self.result['rmse'])
        groups=self.result['zero_week_groups']
        self.assertEqual(sum(g['n_observations'] for g in groups.values()),400)
        self.assertAlmostEqual(sum(g['n_observations']*g['mae'] for g in groups.values())/400,self.result['mae'])

    def test_predictions_are_unmodified_and_model_metadata_consistent(self):
        model,meta=evaluation.load_model()
        with evaluation.threadpool_limits(limits=1):
            direct=model.predict(self.table[evaluation.FEATURES])
        np.testing.assert_array_equal(direct,self.table.predicted_activities_next_week)
        np.testing.assert_array_equal(model.coef_,[meta['coefficients'][f] for f in evaluation.FEATURES])
        self.assertEqual(model.intercept_,meta['intercept'])
        self.assertEqual(int((direct<0).sum()),self.result['negative_predictions'])
        self.assertFalse(self.result['baseline_evaluated'])


if __name__=='__main__':unittest.main()
