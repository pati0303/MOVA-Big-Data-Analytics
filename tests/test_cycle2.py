"""Targeted cycle-2 tests; model fitting occurs only in explicit comparison tests."""
import builtins
import csv
import io
import json
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch
import numpy as np
import pandas as pd
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'src'))
import cycle2_compare as c


class Cycle2Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.frame = c.load()
        cls.train = cls.frame.drop(columns=c.EXTRA)
        cls.history = pd.read_csv(c.ROOT/'data/processed/user_weekly_activities.csv')
        cls.history = cls.history[cls.history.week_index <= 22].copy()

    def test_calendar_reference_and_zero_count(self):
        for r in self.frame.itertuples():
            begin = pd.Timestamp(r.week_start)
            h = self.history[(self.history.user_id == r.user_id) &
                             pd.to_datetime(self.history.week_start).between(begin-pd.Timedelta(days=21),begin)]
            self.assertEqual(len(h),4)
            self.assertEqual(getattr(r,c.EXTRA),int((h.activities_count == 0).sum()))
        self.assertEqual(int(self.frame.iloc[0][c.EXTRA]),3)
        pd.testing.assert_frame_equal(c.construct(self.train,self.history.iloc[::-1]),self.frame)

    def test_future_change_preserves_earlier_inputs(self):
        altered = self.history.copy()
        altered.loc[(altered.user_id=='U001') & (altered.week_index==12),'activities_count'] = 0
        train = self.train.copy()
        # Rebuild legacy X/y for this counterfactual; test only historical causality.
        lookup = altered.set_index(['user_id','week_index']).activities_count
        for idx,r in train.iterrows():
            window = [lookup.loc[(r.user_id,t)] for t in range(r.week_index-3,r.week_index+1)]
            train.loc[idx,c.BASE] = [window[-1],sum(window)/4]
            train.loc[idx,c.TARGET] = lookup.loc[(r.user_id,r.week_index+1)]
        result = c.construct(train,altered)
        mask = (self.frame.user_id!='U001') | (self.frame.week_index<12)
        pd.testing.assert_frame_equal(result.loc[mask,c.BASE+[c.EXTRA]],self.frame.loc[mask,c.BASE+[c.EXTRA]])

    def test_missing_duplicate_and_invalid_history_rejected(self):
        for bad in [self.history.iloc[1:],pd.concat([self.history,self.history.iloc[:1]])]:
            with self.assertRaises(ValueError): c.construct(self.train,bad)
        for value in [-1, .5, np.nan]:
            bad=self.history.copy(); bad['activities_count']=bad.activities_count.astype(float);bad.loc[0,'activities_count']=value
            with self.assertRaises(ValueError): c.construct(self.train,bad)

    def test_bad_calendar_and_legacy_values_rejected(self):
        bad=self.train.copy();bad.loc[0,'week_end']='2026-02-02'
        with self.assertRaises(ValueError): c.construct(bad,self.history)
        bad=self.train.copy();bad.loc[0,c.BASE[1]]+=1
        with self.assertRaises(ValueError): c.construct(bad,self.history)

    def test_folds_and_label_availability(self):
        keys=[]
        for spec in c.FOLDS:
            train,val=c.split(self.frame,spec)
            self.assertEqual(set(train.week_index),set(range(4,spec[1]+1)))
            self.assertEqual(set(val.week_index),set(range(spec[2],spec[3]+1)))
            self.assertLessEqual(train.week_index.max()+1,val.week_index.min())
            self.assertEqual(len(val),400)
            keys.extend(zip(val.user_id,val.week_index))
        self.assertEqual(len(keys),1200);self.assertEqual(len(set(keys)),1200)

    def test_input_boundary_rejects_test_access_and_discards_later_weeks(self):
        original=Path.open
        allowed={str(c.ROOT/p) for p in c.SOURCES}
        def guarded(path,*args,**kwargs):
            self.assertIn(str(path),allowed)
            return original(path,*args,**kwargs)
        original_construct=c.construct
        def bounded(train,history):
            self.assertEqual(history.week_index.max(),22)
            self.assertEqual(train.week_index.max(),21)
            return original_construct(train,history)
        with patch.object(Path,'open',guarded),patch.object(c,'construct',side_effect=bounded):
            c.load()

    def test_exact_six_fits_training_only_and_frozen_prediction(self):
        original_fit=c.LinearRegression.fit
        original_predict=c.LinearRegression.predict
        calls=[];predictions=[]
        def fit(model,x,y,*args,**kwargs):
            calls.append((len(x),list(x.columns)))
            self.assertIn(len(x),[600,1000,1400])
            pd.testing.assert_series_equal(y,self.frame.loc[x.index,c.TARGET].astype(float))
            return original_fit(model,x,y,*args,**kwargs)
        def predict(model,x):
            predictions.append(len(x));self.assertEqual(len(x),400)
            return original_predict(model,x)
        with patch.object(c.LinearRegression,'fit',fit),patch.object(c.LinearRegression,'predict',predict):
            result=c.evaluate(self.frame)
        self.assertEqual([n for n,_ in calls],[600,600,1000,1000,1400,1400])
        self.assertEqual(predictions,[400]*6)
        table,summary,folds,groups,paired,weekly,models,manifest,decision=result
        self.assertEqual(len(table),3600)
        for name,g in table.groupby('model'):
            self.assertEqual(len(g),1200)
            row=summary.set_index('model').loc[name]
            self.assertAlmostEqual(row.mae,abs(g.prediction-g.actual).mean())
            self.assertAlmostEqual(row.rmse,np.sqrt(((g.prediction-g.actual)**2).mean()))
        persist=table[table.model=='persistence']
        source=self.frame.set_index(['user_id','week_index'])
        for r in persist.itertuples():self.assertEqual(r.prediction,source.loc[(r.user_id,r.week_index),'activities_current_week'])
        mae=summary.set_index('model').mae
        fm=folds.pivot(index='fold',columns='model',values='mae')
        self.assertEqual(decision['adopt_extended'],bool(mae.linear_3<mae.linear_2 and (fm.linear_3<fm.linear_2).sum()>=2))
        self.assertAlmostEqual(paired.improvement_linear3_vs_linear2.mean(),mae.linear_2-mae.linear_3)

    def test_no_overwrite_and_output_boundary(self):
        with tempfile.TemporaryDirectory() as directory:
            root=Path(directory)
            c.persist(root,{'outputs/cycle2/test.json':b'one'})
            c.persist(root,{'outputs/cycle2/test.json':b'one'})
            with self.assertRaises(ValueError):c.persist(root,{'outputs/cycle2/test.json':b'two'})
            self.assertEqual((root/'outputs/cycle2/test.json').read_bytes(),b'one')
            with self.assertRaises(ValueError):c.persist(root,{'outputs/old.json':b'bad'})


if __name__=='__main__':unittest.main()
