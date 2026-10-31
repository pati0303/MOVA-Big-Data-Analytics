"""AP 5.2: echte V2, kontrollierte Fehler nur an Speicherkopien."""
import json
import sys
import unittest
from itertools import combinations
from pathlib import Path
from unittest.mock import patch
import numpy as np
import pandas as pd
from sklearn.metrics import adjusted_rand_score
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'src'))
import modeling_kmeans_stability as stability


class StabilityTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.x=stability.base.load_input()
        cls.scaled=pd.read_csv(stability.ROOT/'data/processed/kmeans_user_features_scaled.csv')
        cls.raw=pd.read_csv(stability.ROOT/'data/processed/kmeans_user_features.csv')
        cls.runs,cls.summary,cls.refs,cls.pairs=stability.evaluate(cls.x)
        cls.profiles=stability.candidate_profiles(cls.scaled,cls.raw,cls.refs)

    def test_full_design_and_valid_metrics(self):
        self.assertEqual(len(self.runs),80)
        for k,group in self.runs.groupby('k'):
            self.assertEqual(set(group.seed),set(stability.SEEDS))
            self.assertEqual(len(group),20)
            self.assertTrue((group.n_clusters==k).all())
            self.assertTrue((group.inertia>=0).all())
            self.assertTrue(group.silhouette_score.between(-1,1).all())
            self.assertTrue(group.ari_vs_seed_42.between(-1,1).all())
            for _,row in group.iterrows():
                counts=json.loads(row.cluster_sizes)
                self.assertEqual(len(counts),k)
                self.assertEqual(sum(counts.values()),100)
                self.assertEqual(min(counts.values()),row.min_cluster_size)

    def test_ari_is_label_permutation_invariant(self):
        labels=self.refs[3]
        renamed=np.array([17,4,99])[labels]
        self.assertEqual(adjusted_rand_score(labels,renamed),1)
        mappings={seed:(labels if seed%2 else renamed) for seed in stability.SEEDS}
        summary,pairs=stability.ari_summary(mappings)
        self.assertEqual(summary['n_pairs'],190)
        self.assertEqual(summary['n_unique_partitions'],1)
        np.testing.assert_array_equal(pairs,np.ones(190))

    def test_ari_pairs_independent_enumeration(self):
        # Reale Partitionen verschiedener k als technische ARI-Referenzen.
        labels={s:self.refs[(2,3,6,8)[i%4]] for i,s in enumerate(stability.SEEDS)}
        summary,pairs=stability.ari_summary(labels)
        expected=[adjusted_rand_score(labels[a],labels[b]) for a,b in combinations(stability.SEEDS,2)]
        self.assertAlmostEqual(summary['ari_pairwise_mean'],np.mean(expected))
        self.assertEqual(summary['ari_pairwise_min'],min(expected))
        self.assertEqual(summary['ari_pairwise_max'],max(expected))
        refs=[adjusted_rand_score(labels[42],labels[s]) for s in stability.SEEDS if s!=42]
        self.assertAlmostEqual(summary['ari_vs_42_mean'],np.mean(refs))

    def test_summary_matches_runs(self):
        for _,row in self.summary.iterrows():
            group=self.runs[self.runs.k==row.k]
            self.assertAlmostEqual(row.silhouette_mean,group.silhouette_score.mean())
            self.assertAlmostEqual(row.silhouette_std,group.silhouette_score.std(ddof=0))
            self.assertEqual(row.min_observed_cluster_size,group.min_cluster_size.min())
            self.assertAlmostEqual(row.inertia_mean,group.inertia.mean())

    def test_seed42_reproduces_ap51(self):
        previous=pd.read_csv(stability.ROOT/'outputs/tables/kmeans_k_selection.csv').set_index('k')
        for _,row in self.runs[self.runs.seed==42].iterrows():
            self.assertAlmostEqual(row.inertia,previous.loc[row.k,'inertia'])
            self.assertAlmostEqual(row.silhouette_score,previous.loc[row.k,'silhouette_score'])

    def test_profiles_join_by_id_and_match_independent_means(self):
        shuffled=self.raw.iloc[::-1].copy()
        pd.testing.assert_frame_equal(self.profiles,stability.candidate_profiles(self.scaled,shuffled,self.refs))
        for _,row in self.profiles.iterrows():
            ids=set(self.scaled.loc[self.refs[row.k]==row.candidate_cluster,'user_id'])
            group=self.raw[self.raw.user_id.isin(ids)]
            self.assertEqual(len(group),row.n_users)
            for feature in stability.PROFILE_FEATURES:
                self.assertAlmostEqual(sum(group[feature])/len(group),row[feature])
            self.assertAlmostEqual(sum(row[s] for s in stability.SPORTS),1)

    def test_bad_joins_rejected(self):
        for field,value in [('user_id','UNKNOWN'),('user_id',None),('user_id',self.raw.loc[1,'user_id'])]:
            bad=self.raw.copy();bad.loc[0,field]=value
            with self.assertRaises(ValueError):stability.candidate_profiles(self.scaled,bad,self.refs)

    def test_invalid_seeds_and_inputs_rejected(self):
        for seeds in [tuple(range(20)),(42,)*20,stability.SEEDS[:-1]]:
            with self.assertRaises(ValueError):stability.evaluate(self.x,seeds)
        with self.assertRaises(ValueError):stability.evaluate(self.x[:99])

    def test_no_refit_or_input_changes_and_reproducible(self):
        before=self.x.copy()
        with patch('sklearn.preprocessing.StandardScaler.fit',side_effect=AssertionError('Refit')):
            runs,summary,refs,pairs=stability.evaluate(stability.base.load_input())
        pd.testing.assert_frame_equal(runs,self.runs)
        pd.testing.assert_frame_equal(summary,self.summary)
        np.testing.assert_array_equal(self.x,before)
        for name,frame in [('kmeans_stability_results.csv',runs),('kmeans_candidate_comparison.csv',summary),
                           ('kmeans_candidate_profiles.csv',self.profiles)]:
            self.assertEqual((stability.ROOT/'outputs/tables'/name).read_bytes(),stability.frame_bytes(frame))

    def test_interpretation_features_do_not_affect_clustering(self):
        # Eingangsprüfung verbietet Interpretationsspalten; Profile verwenden sie nur nachträglich.
        with self.assertRaises(ValueError):stability.base.validate_frame(self.scaled.assign(sport_diversity=1))
        bad=self.raw.copy();bad['avg_duration_per_week']+=10
        profiles=stability.candidate_profiles(self.scaled,bad,self.refs)
        np.testing.assert_array_equal(profiles.n_users,self.profiles.n_users)
        np.testing.assert_allclose(profiles.avg_duration_per_week,self.profiles.avg_duration_per_week+10)


if __name__=='__main__':unittest.main()
