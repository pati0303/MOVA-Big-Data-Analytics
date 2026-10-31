"""AP 5.3a ohne jeglichen Fit; Sonderfälle auf Kopien echter V2-Profile."""
import sys
import unittest
from pathlib import Path
from unittest.mock import patch
import numpy as np
import pandas as pd
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'src'))
import modeling_kmeans_inference as inference


class InferenceContractTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.artifacts=inference.load_artifacts()
        cls.raw=pd.read_csv(inference.ROOT/'data/processed/kmeans_user_features.csv')
        cls.features=cls.raw[inference.FEATURES].iloc[0].to_dict()

    def assign(self,features=None,**overrides):
        kwargs=dict(complete_weeks=26,records_complete=True,records_reliable=True,known_sports=True,
                    artifacts=self.artifacts)
        kwargs.update(overrides)
        return inference.assign_profile(self.features if features is None else features,**kwargs)

    def test_full_reproduction_without_fit(self):
        with patch('sklearn.cluster.KMeans.fit',side_effect=AssertionError('Training verboten')),\
             patch('sklearn.preprocessing.StandardScaler.fit',side_effect=AssertionError('Refit verboten')):
            result=inference.audit_existing()
            self.assertEqual(result['users'],100)
            self.assertTrue(result['assignments_match'])
            saved=pd.read_csv(inference.ROOT/'data/processed/user_clusters.csv').set_index('user_id')
            for _,row in self.raw.iterrows():
                out=self.assign(row[inference.FEATURES].to_dict())
                self.assertEqual(out['cluster_id'],saved.loc[row.user_id,'cluster_id'])
                self.assertEqual(out['segment_label'],saved.loc[row.user_id,'segment_label'])

    def test_transform_matches_prepared_csv(self):
        actual=inference.transform_saved(self.raw[inference.FEATURES],self.artifacts[1])
        expected=pd.read_csv(inference.ROOT/'data/processed/kmeans_user_features_scaled.csv')
        np.testing.assert_allclose(actual,expected[inference.FEATURES],atol=1e-10,rtol=1e-10)

    def test_wrong_order_missing_extra_features(self):
        for frame in [self.raw[inference.FEATURES[::-1]],self.raw[inference.FEATURES[:-1]],
                      self.raw[inference.FEATURES].assign(sport_diversity=1)]:
            with self.assertRaises(ValueError):inference.transform_saved(frame,self.artifacts[1])

    def test_invalid_numbers_and_shares(self):
        for key,value in [('avg_activities_per_week',np.nan),('avg_activities_per_week',np.inf),
                          ('avg_activities_per_week',-1),('avg_activities_per_week',True),
                          ('share_running',np.inf),('share_running',-0.1),('share_running',2),
                          ('share_running','0.5')]:
            values=dict(self.features);values[key]=value
            out=self.assign(values)
            self.assertEqual(out['status'],'invalid_features')
            self.assertIsNone(out['cluster_id'])

    def test_inactive_has_no_preferences_or_cluster(self):
        values={f:np.nan for f in inference.FEATURES};values[inference.FEATURES[0]]=0
        with patch.object(self.artifacts[0],'predict',side_effect=AssertionError('Keine Zuordnung')):
            out=self.assign(values)
        self.assertEqual(out['status'],'inactive');self.assertIsNone(out['cluster_id'])
        self.assertTrue(all(np.isnan(values[f]) for f in inference.FEATURES[1:]))
        for f in inference.FEATURES[1:]:values[f]=0
        self.assertEqual(self.assign(values)['status'],'invalid_features')

    def test_history_gate_and_unknown_sports(self):
        for options in [dict(complete_weeks=25),dict(complete_weeks=None),dict(records_complete=False),
                        dict(records_complete=None),dict(records_reliable=False),dict(known_sports=False)]:
            with patch.object(self.artifacts[0],'predict',side_effect=AssertionError('Keine Zuordnung')):
                out=self.assign(**options)
            self.assertNotEqual(out['status'],'assigned');self.assertIsNone(out['cluster_id'])


if __name__=='__main__':unittest.main()
