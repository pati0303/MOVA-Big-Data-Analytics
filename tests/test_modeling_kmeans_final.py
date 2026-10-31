"""Finales V2-Modell: Persistenz, fachliche Benennung und unabhängige Kontrollen."""
import hashlib
import json
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch
import joblib
import numpy as np
import pandas as pd
from sklearn.metrics import silhouette_score
from threadpoolctl import threadpool_limits
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'src'))
import modeling_kmeans_final as final


class FinalKMeansTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.scaled=pd.read_csv(final.ROOT/'data/processed/kmeans_user_features_scaled.csv')
        cls.raw=pd.read_csv(final.ROOT/'data/processed/kmeans_user_features.csv')
        cls.assignments=pd.read_csv(final.ROOT/'data/processed/user_clusters.csv')
        cls.profiles=pd.read_csv(final.ROOT/'outputs/tables/kmeans_final_cluster_profiles.csv')
        cls.meta=json.loads((final.ROOT/final.METADATA_PATH).read_text())
        # Ausschließlich das hier erzeugte vertrauenswürdige Projektartefakt.
        cls.model=joblib.load(final.ROOT/final.MODEL_PATH)

    def test_parameters_independent_from_binary(self):
        expected={'n_clusters':2,'init':'k-means++','random_state':42,'n_init':20,
                  'max_iter':300,'algorithm':'lloyd','tol':1e-4}
        for key,value in expected.items():
            self.assertEqual(self.meta['parameters'][key],value)
            self.assertEqual(self.model.get_params()[key],value)
        self.assertEqual(self.model.n_features_in_,9)
        self.assertEqual(list(self.model.feature_names_in_),final.FEATURES)
        self.assertEqual(self.meta['feature_order'],final.FEATURES)

    def test_reload_reproduces_all_assignments(self):
        final.verify_saved(final.ROOT,self.scaled,self.assignments)
        self.assertEqual(list(self.assignments.columns),['user_id','cluster_id','segment_label'])
        self.assertEqual(len(self.assignments),100)
        self.assertEqual(self.assignments.user_id.nunique(),100)
        self.assertFalse(self.assignments.isna().any().any())
        self.assertEqual(sorted(self.assignments.cluster_id.value_counts()),[43,57])

    def test_centers_and_metrics_independently_from_data(self):
        x=self.scaled[final.FEATURES].to_numpy()
        labels=self.assignments.cluster_id.to_numpy()
        centers=np.vstack([x[labels==c].mean(axis=0) for c in range(2)])
        np.testing.assert_allclose(centers,self.meta['cluster_centers'],atol=1e-12,rtol=1e-12)
        inertia=((x-centers[labels])**2).sum()
        self.assertAlmostEqual(inertia,self.meta['inertia'])
        with threadpool_limits(limits=1):
            self.assertAlmostEqual(silhouette_score(x,labels,metric='euclidean'),self.meta['silhouette_score'])
        previous=pd.read_csv(final.ROOT/'outputs/tables/kmeans_k_selection.csv').set_index('k').loc[2]
        self.assertAlmostEqual(inertia,previous.inertia)
        self.assertAlmostEqual(self.meta['silhouette_score'],previous.silhouette_score)

    def test_profiles_independent_user_id_join(self):
        joined=self.assignments.merge(self.raw,on='user_id',validate='one_to_one')
        for row in self.profiles.itertuples():
            group=joined[joined.cluster_id==row.cluster_id]
            self.assertEqual(len(group),row.n_users)
            for feature in final.PROFILE_FEATURES:
                self.assertAlmostEqual(sum(group[feature])/len(group),getattr(row,feature))
            top=sorted(final.FEATURES[1:],key=lambda s:(-group[s].mean(),s))[:3]
            self.assertEqual(' / '.join(s.removeprefix('share_') for s in top),row.top_3_sports)

    def test_names_follow_frequency_after_label_permutation(self):
        labels=self.assignments.cluster_id.to_numpy()
        permuted=1-labels
        assignment,profiles,mapping=final.describe_clusters(self.scaled,self.raw.iloc[::-1],permuted)
        self.assertEqual(assignment.segment_label.tolist(),self.assignments.segment_label.tolist())
        ordered=profiles.sort_values('avg_activities_per_week')
        self.assertEqual(ordered.segment_label.tolist(),[final.LOWER,final.HIGHER])
        self.assertEqual(mapping[1],self.meta['cluster_id_to_segment']['0'])

    def test_tied_frequency_or_invalid_join_stops(self):
        tied=self.raw.copy();tied['avg_activities_per_week']=1.0
        with self.assertRaises(ValueError):
            final.describe_clusters(self.scaled,tied,self.assignments.cluster_id.to_numpy())
        bad=self.raw.copy();bad.loc[0,'user_id']='UNKNOWN'
        with self.assertRaises(ValueError):
            final.describe_clusters(self.scaled,bad,self.assignments.cluster_id.to_numpy())

    def test_no_scaling_and_exact_input_reproduction(self):
        before=self.scaled.copy(deep=True)
        with patch('sklearn.preprocessing.StandardScaler.fit',side_effect=AssertionError('Refit')):
            model,score,assignments,profiles,mapping=final.train(self.scaled,self.raw,final.base.load_input())
        pd.testing.assert_frame_equal(self.scaled,before)
        self.assertEqual(final.csv_bytes(assignments),(final.ROOT/'data/processed/user_clusters.csv').read_bytes())
        self.assertEqual(final.csv_bytes(profiles),(final.ROOT/'outputs/tables/kmeans_final_cluster_profiles.csv').read_bytes())
        self.assertAlmostEqual(score,self.meta['silhouette_score'])
        with self.assertRaises(ValueError):
            final.base.validate_frame(self.scaled.assign(avg_duration_per_week=10))

    def test_input_and_model_hashes(self):
        for path,expected in {**self.meta['source_sha256'],**self.meta['selection_evidence_sha256']}.items():
            self.assertEqual(hashlib.sha256((final.ROOT/path).read_bytes()).hexdigest(),expected)
        self.assertEqual(final.base.digest(final.ROOT/final.MODEL_PATH),self.meta['model_sha256'])

    def test_tampered_artifact_rejected_before_loading(self):
        with tempfile.TemporaryDirectory(dir=final.ROOT/'work') as folder:
            root=Path(folder);(root/'outputs/models').mkdir(parents=True)
            (root/final.METADATA_PATH).write_text(json.dumps(self.meta))
            (root/final.MODEL_PATH).write_bytes((final.ROOT/final.MODEL_PATH).read_bytes()+b'changed')
            with patch.object(final.joblib,'load',side_effect=AssertionError('Darf nicht geladen werden')):
                with self.assertRaisesRegex(ValueError,'Modellhash'):
                    final.verify_saved(root,self.scaled,self.assignments)

    def test_metadata_segment_mapping_matches_actual_profiles(self):
        for row in self.profiles.itertuples():
            self.assertEqual(self.meta['cluster_id_to_segment'][str(row.cluster_id)],row.segment_label)
            self.assertAlmostEqual(self.meta['labeling_basis'][str(row.cluster_id)],row.avg_activities_per_week)
            self.assertEqual(self.meta['cluster_sizes'][str(row.cluster_id)],row.n_users)


if __name__=='__main__':unittest.main()
