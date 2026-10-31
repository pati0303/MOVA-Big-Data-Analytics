"""AP 5.4 nur Training: technische Prüfung, keine Testevaluation."""
import json
import sys
import unittest
from pathlib import Path
from unittest.mock import patch
import joblib
import numpy as np
import pandas as pd
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'src'))
import modeling_regression_train as regression


class RegressionTrainingTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.frame,cls.x,cls.y,_=regression.load_training()
        cls.model=joblib.load(regression.ROOT/regression.MODEL)
        cls.meta=json.loads((regression.ROOT/regression.METADATA).read_text())

    def test_training_roles_and_global_scope(self):
        self.assertEqual(self.x.shape,(1800,2))
        self.assertEqual(self.frame.user_id.nunique(),100)
        self.assertEqual(list(self.model.feature_names_in_),regression.FEATURES)
        self.assertEqual(self.model.get_params()['fit_intercept'],True)
        self.assertEqual(self.meta['n_training_rows'],1800)
        self.assertFalse(self.meta['test_evaluation_performed'])

    def test_coefficients_against_independent_ols(self):
        solution=np.linalg.lstsq(np.column_stack([np.ones(1800),self.x]),self.y,rcond=None)[0]
        np.testing.assert_allclose(np.r_[self.model.intercept_,self.model.coef_],solution,atol=1e-12,rtol=1e-12)
        self.assertEqual(self.meta['intercept'],self.model.intercept_)
        np.testing.assert_array_equal([self.meta['coefficients'][f] for f in regression.FEATURES],self.model.coef_)

    def test_missing_nonfinite_and_fractional_counts_rejected(self):
        for feature,value in [('activities_current_week',np.inf),('avg_activities_last_4_weeks',np.nan),
                              ('activities_next_week',-1),('activities_current_week',1.5),
                              ('activities_next_week',1.5),('activities_next_week',np.nan),('activities_next_week',np.inf)]:
            bad=self.frame.copy();bad[feature]=bad[feature].astype(float);bad.loc[0,feature]=value
            with self.assertRaises(ValueError):regression.validate_train(bad)

    def test_leakage_features_and_wrong_weeks_rejected(self):
        for feature in ['cluster_id','interest_sport','activities_previous_week']:
            with self.assertRaises(ValueError):regression.validate_train(self.frame.assign(**{feature:0}))
        bad=self.frame.copy();bad.loc[0,'week_index']=22
        with self.assertRaises(ValueError):regression.validate_train(bad)

    def test_duplicates_and_calendar_rejected(self):
        bad=self.frame.copy();bad.loc[0]=bad.loc[1]
        with self.assertRaises(ValueError):regression.validate_train(bad)
        bad=self.frame.copy();bad.loc[0,'week_end']='2026-02-02'
        with self.assertRaises(ValueError):regression.validate_train(bad)

    def test_training_without_test_access_scaling_or_scoring(self):
        original=pd.read_csv
        def restricted(path,*args,**kwargs):
            self.assertEqual(Path(path).name,'regression_train.csv')
            return original(path,*args,**kwargs)
        with patch.object(regression.pd,'read_csv',side_effect=restricted),\
             patch('sklearn.preprocessing.StandardScaler.fit',side_effect=AssertionError('Keine Skalierung')),\
             patch.object(regression.LinearRegression,'score',side_effect=AssertionError('Keine Evaluation')),\
             patch.object(regression.LinearRegression,'predict',side_effect=AssertionError('Keine Vorhersagen')):
            frame,x,y,_=regression.load_training()
            model=regression.train(x,y)
        np.testing.assert_array_equal(model.coef_,self.model.coef_)
        self.assertEqual(model.intercept_,self.model.intercept_)
        pd.testing.assert_frame_equal(frame,self.frame)
        np.testing.assert_array_equal(x.to_numpy(),self.frame[regression.FEATURES].to_numpy())
        self.assertEqual(regression.sha256(regression.ROOT/regression.MODEL),self.meta['model_sha256'])

    def test_loaded_training_predictions_equal_fresh_fit(self):
        fresh=regression.train(self.x,self.y)
        with regression.threadpool_limits(limits=1):
            expected=fresh.predict(self.x)
            actual=self.model.predict(self.x)
        np.testing.assert_array_equal(actual,expected)
        np.testing.assert_allclose(actual,self.model.intercept_+self.x.to_numpy()@self.model.coef_,
                                   atol=1e-12,rtol=1e-12)
        self.assertEqual(self.meta['parameters'],self.model.get_params())
        self.assertEqual(self.meta['feature_order'],list(self.model.feature_names_in_))
        self.assertEqual(self.meta['algorithm'],'sklearn.linear_model.LinearRegression')

    def test_coefficient_table_matches_model(self):
        table=pd.read_csv(regression.ROOT/regression.COEFFICIENTS,float_precision='round_trip')
        self.assertEqual(table.term.tolist(),['intercept']+regression.FEATURES)
        np.testing.assert_array_equal(table.coefficient,np.r_[self.model.intercept_,self.model.coef_])


if __name__=='__main__':unittest.main()
