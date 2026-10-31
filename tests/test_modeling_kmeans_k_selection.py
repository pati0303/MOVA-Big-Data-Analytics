"""Echte V2 als Referenz; Fehlerfälle ausschließlich in Speicherkopien."""
import sys
import unittest
from pathlib import Path
from unittest.mock import patch
import numpy as np
import pandas as pd
from sklearn.metrics import silhouette_score
sys.path.insert(0, str(Path(__file__).resolve().parents[1]/'src'))
import modeling_kmeans_k_selection as selection


class KSelectionTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.frame = pd.read_csv(selection.ROOT/'data/processed/kmeans_user_features_scaled.csv')
        cls.x = selection.load_input()
        cls.rows, cls.details = selection.evaluate(cls.x)

    def test_input_matches_prepared_values_without_refit(self):
        with patch('sklearn.preprocessing.StandardScaler.fit', side_effect=AssertionError('Refit')):
            x = selection.load_input()
            selection.evaluate(x, [2])
        np.testing.assert_array_equal(x, self.frame[selection.FEATURES].to_numpy())

    def test_forbidden_or_missing_features_rejected(self):
        for col in ['avg_duration_per_week','sport_diversity','interest_sport','internal_profile']:
            with self.assertRaises(ValueError):
                selection.validate_frame(self.frame.assign(**{col:0}))
        with self.assertRaises(ValueError):
            selection.validate_frame(self.frame.drop(columns=['share_running']))

    def test_invalid_users_rejected(self):
        for value in [None,'','  ',self.frame.loc[1,'user_id']]:
            altered = self.frame.copy(); altered.loc[0,'user_id'] = value
            with self.assertRaises(ValueError): selection.validate_frame(altered)
        with self.assertRaises(ValueError): selection.validate_frame(self.frame.iloc[:-1])

    def test_nonfinite_values_rejected(self):
        for value in [np.nan,np.inf,-np.inf]:
            altered = self.frame.copy(); altered.loc[0,selection.FEATURES[0]] = value
            with self.assertRaises(ValueError): selection.validate_frame(altered)

    def test_invalid_k_rejected(self):
        for ks in [[],[0],[9],[2,2],[3,2],[2.0],[True]]:
            with self.assertRaises(ValueError): selection.evaluate(self.x,ks)

    def test_results_and_inertia_reference(self):
        self.assertEqual([r['k'] for r in self.rows],list(range(1,9)))
        one = ((self.x-self.x.mean(axis=0))**2).sum()
        self.assertAlmostEqual(self.rows[0]['inertia'],one)
        for row,detail in zip(self.rows,self.details):
            self.assertEqual(detail['n_clusters'],row['k'])
            self.assertEqual(sum(detail['sizes'].values()),100)
            self.assertTrue(1 <= row['n_iterations'] <= 300)
            self.assertGreaterEqual(row['inertia'],0)
            if row['k'] > 1:
                self.assertTrue(-1 <= row['silhouette_score'] <= 1)
                self.assertEqual(row['min_cluster_size'],min(detail['sizes'].values()))
                self.assertEqual(row['max_cluster_size'],max(detail['sizes'].values()))
        self.assertTrue(all(b['inertia'] <= a['inertia']+selection.TOLERANCE
                            for a,b in zip(self.rows,self.rows[1:])))
        self.assertIsNone(self.rows[0]['silhouette_score'])
        self.assertIsNone(self.rows[0]['min_cluster_size'])

    def test_silhouette_and_inertia_independently_from_fit(self):
        from threadpoolctl import threadpool_limits
        with threadpool_limits(limits=1):
            model=selection.KMeans(n_clusters=2,**selection.PARAMETERS).fit(self.x)
            distances=((self.x-model.cluster_centers_[model.labels_])**2).sum()
            self.assertAlmostEqual(distances,self.rows[1]['inertia'])
            self.assertAlmostEqual(silhouette_score(self.x,model.labels_,metric='euclidean'),
                                   self.rows[1]['silhouette_score'])

    def test_repeat_reproducible_and_input_unchanged(self):
        before=self.x.copy()
        rows,details=selection.evaluate(self.x)
        self.assertEqual(selection.csv_bytes(rows),selection.csv_bytes(self.rows))
        self.assertEqual(details,self.details)
        np.testing.assert_array_equal(before,self.x)
        self.assertEqual((selection.ROOT/'outputs/tables/kmeans_k_selection.csv').read_bytes(),
                         selection.csv_bytes(rows))


if __name__ == '__main__':
    unittest.main()
