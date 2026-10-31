"""Controlled comparison tests; all V2 calls reuse the existing engine."""
import copy
import csv
import hashlib
import json
from pathlib import Path
import sys
import unittest
from unittest.mock import patch

sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'src'))
import recommendation_comparison as c
import recommendation_engine as e


class ComparisonTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.data=e.load_data(include_activity=True)
        cls.users,cls.offers,cls.summary=c.compare(cls.data)

    def test_population_and_top_five(self):
        self.assertEqual(len(self.users),100)
        self.assertEqual(len({r['user_id'] for r in self.users}),100)
        for row in self.users:
            for key in ['top5_before','top5_after']:
                self.assertLessEqual(len(row[key]),5)
                self.assertEqual(len(row[key]),len(set(row[key])))

    def test_controlled_engine_arguments(self):
        snapshot=copy.deepcopy(self.data)
        approval=c.digest(e.ROOT/'documentation/offer_sport_tags_approved.csv')
        with patch.object(e,'recommendations',wraps=e.recommendations) as calls, \
             patch.object(e,'permission_flags',wraps=e.permission_flags) as permissions:
            c.compare(self.data)
        self.assertEqual(calls.call_count,200)
        permissions.assert_called_once_with(True,True)
        for i in range(0,200,2):
            before,after=calls.call_args_list[i:i+2]
            self.assertEqual(before.args[0],after.args[0])
            for pos in [1,2,4]:self.assertIs(before.args[pos],after.args[pos])
            self.assertEqual(before.args[3],{})
            self.assertEqual(after.args[3],c.EXPECTED_TAGS)
        self.assertEqual(snapshot,self.data)
        self.assertEqual(approval,c.digest(e.ROOT/'documentation/offer_sport_tags_approved.csv'))

    def test_classification_exclusive(self):
        self.assertEqual(c.classify([],[]),'unchanged')
        self.assertEqual(c.classify(['a','b'],['a','b']),'unchanged')
        self.assertEqual(c.classify(['a','b'],['b','a']),'reordered_only')
        self.assertEqual(c.classify(['a','b'],['a','c']),'composition_changed')
        self.assertEqual(sum(self.summary['change_groups'].values()),100)
        for row in self.users:
            self.assertEqual(row['change_group'],c.classify(row['top5_before'],row['top5_after']))

    def test_user_totals_independently(self):
        rows=self.users;s=self.summary
        self.assertEqual(s['users_changed'],sum(r['top5_before']!=r['top5_after'] for r in rows))
        self.assertEqual(s['slots_before'],sum(len(r['top5_before']) for r in rows))
        self.assertEqual(s['slots_after'],sum(len(r['top5_after']) for r in rows))
        self.assertEqual(s['mean_common_offers'],sum(len(set(r['top5_before'])&set(r['top5_after'])) for r in rows)/100)
        self.assertEqual(s['users_no_positive_interests'],sum(not e.interest_categories(u) for u in self.data.users.values()))
        self.assertEqual(s['users_fewer_than_five_eligible'],sum(r['eligible_offers']<5 for r in rows))
        self.assertEqual(s['users_with_tier_a'],sum(r['tier_a_after']>0 for r in rows))

    def test_offer_frequencies_and_transitions(self):
        for offer in self.offers:
            oid=offer['offer_id']
            self.assertEqual(offer['slots_before'],sum(oid in r['top5_before'] for r in self.users))
            self.assertEqual(offer['slots_after'],sum(oid in r['top5_after'] for r in self.users))
            self.assertEqual(offer['slot_delta'],offer['entered']-offer['exited'])
            retained=offer['retained_same_position']+offer['retained_changed_position']
            self.assertEqual(offer['slots_after'],offer['entered']+retained)
            self.assertEqual(offer['slots_before'],offer['exited']+retained)
            expected=sum(oid in r['top5_before'] and oid in r['top5_after'] and
                         r['top5_before'].index(oid)!=r['top5_after'].index(oid) for r in self.users)
            self.assertEqual(offer['retained_changed_position'],expected)

    def test_tier_totals_and_percent_denominators(self):
        s=self.summary
        self.assertEqual(s['tier_a_before'],0)
        self.assertEqual(s['tier_a_after'],sum(r['tier_a_after'] for r in self.users))
        self.assertEqual(s['tier_a_after'],sum(r['tier_a_after'] for r in self.offers))
        self.assertEqual(s['tier_a_after'],sum(s['tier_a_slots_by_sport'].values()))
        self.assertEqual(s['tier_a_after']+s['tier_b_after'],s['slots_after'])
        self.assertAlmostEqual(s['users_changed_pct'],100*s['users_changed']/100)
        self.assertAlmostEqual(s['tier_a_after_pct'],100*s['tier_a_after']/s['slots_after'])

    def test_category_counts_no_double_count(self):
        catalog={o['offer_id']:o['category'] for o in self.data.offers}
        for cat,stats in self.summary['category_analysis'].items():
            changed=set()
            for row in self.users:
                a={oid:i for i,oid in enumerate(row['top5_before'])}
                b={oid:i for i,oid in enumerate(row['top5_after'])}
                if any(catalog[oid]==cat and a.get(oid)!=b.get(oid) for oid in a.keys()|b.keys()):
                    changed.add(row['user_id'])
            self.assertEqual(stats['users_with_entry_exit_or_position_change'],len(changed))
            self.assertEqual(stats['slots_after'],sum(o['slots_after'] for o in self.offers if o['category']==cat))

    def test_exact_approvals_required(self):
        for bad in [{},dict(list(c.EXPECTED_TAGS.items())[:-1])]:
            data=copy.deepcopy(self.data);data.approved_tags=bad
            with self.assertRaises(ValueError):c.compare(data)

    def test_no_model_loading_training_or_inference(self):
        from sklearn.cluster import KMeans
        from sklearn.linear_model import LinearRegression
        paths=[e.ROOT/'outputs/models'/n for n in ['kmeans_final.joblib','regression_linear.joblib']]
        hashes=[c.digest(p) for p in paths]
        with patch('joblib.load',side_effect=AssertionError('no model load')), \
             patch.object(KMeans,'fit',side_effect=AssertionError('no fit')), \
             patch.object(LinearRegression,'fit',side_effect=AssertionError('no fit')), \
             patch.object(e,'predict_activity',side_effect=AssertionError('no prediction')):
            c.compare(self.data)
        self.assertEqual(hashes,[c.digest(p) for p in paths])

    def test_repeat_and_input_order(self):
        self.assertEqual((self.users,self.offers,self.summary),c.compare(self.data))
        data=copy.deepcopy(self.data)
        data.offers.reverse();data.users=dict(reversed(list(data.users.items())))
        self.assertEqual((self.users,self.offers,self.summary),c.compare(data))

    def test_persisted_results_and_hashes(self):
        saved=json.loads((e.ROOT/'outputs/tables/recommendation_before_after_summary.json').read_text())
        for k,v in self.summary.items():
            # JSON turns tag tuples into lists.
            self.assertEqual(json.loads(json.dumps(v)),saved[k])
        for p,h in saved['input_sha256'].items():self.assertEqual(c.digest(e.ROOT/p),h)
        for name,expected in [('users',100),('offers',30)]:
            rows=e.read_csv(e.ROOT/f'outputs/tables/recommendation_before_after_{name}.csv')
            self.assertEqual(len(rows),expected)


if __name__=='__main__':unittest.main()
