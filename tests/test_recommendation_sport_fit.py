"""Training-free standard-library tests for retrospective saved-list evaluation."""
import copy
import csv
import json
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch

sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'src'))
import recommendation_sport_fit as fit


class SportFitTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):cls.tables=fit.load()

    def test_known_totals_percentages_and_empty_users(self):
        r=fit.calculate(*self.tables)
        for name,matches in [('before',251),('after',344)]:
            v=r['variants'][name]
            self.assertEqual((v['users'],v['slots'],v['matching_slots']), (100,475,matches))
            self.assertEqual((v['users_with_match'],v['users_without_recommendations'],v['category_violations']),(81,5,0))
            self.assertAlmostEqual(v['matching_slot_pct'],matches/475*100)
        self.assertEqual(r['delta_matching_slots'],93)
        self.assertAlmostEqual(r['delta_percentage_points'],93/475*100)
        self.assertTrue(r['criterion']['formulated_post_hoc']);self.assertTrue(r['criterion']['met'])
        self.assertIsNone(r['criterion']['prospective_success_threshold'])
        self.assertEqual(fit.percentage(0,0),None)

    def test_u001_and_formal_tier_are_different_measures(self):
        r=fit.calculate(*self.tables)
        u=next(x for x in r['paired_user_matches'] if x['user_id']=='U001')
        self.assertEqual((u['before_matching_slots'],u['after_matching_slots']),(1,4))
        self.assertEqual(self.tables[0][0]['tier_a_before'],'0')
        self.assertEqual(sum(x['delta_matching_slots'] for x in r['paired_user_matches']),93)

    def test_consistency_with_stored_original_summary(self):
        original=json.loads((fit.ROOT/'outputs/tables/recommendation_before_after_summary.json').read_text())
        r=fit.calculate(*self.tables)
        self.assertEqual(r['variants']['after']['matching_slots'],original['tier_a_after'])
        self.assertEqual(r['variants']['before']['slots'],original['slots_before'])
        self.assertEqual(r['variants']['after']['users_with_match'],original['users_with_tier_a'])
        self.assertEqual(r['variants']['after']['users_without_recommendations'],original['users_no_positive_interests'])
        t=copy.deepcopy(self.tables)
        ids=json.loads(t[0][0]['top5_after']);ids[0]='O017';t[0][0]['top5_after']=json.dumps(ids)
        with self.assertRaisesRegex(ValueError,'category violation'):fit.calculate(*t)

    def test_duplicate_or_missing_users_rejected(self):
        for index in [0,1]:
            t=copy.deepcopy(self.tables);t[index].append(copy.deepcopy(t[index][0]))
            with self.assertRaises(ValueError):fit.calculate(*t)
            t=copy.deepcopy(self.tables);t[index].pop()
            with self.assertRaises(ValueError):fit.calculate(*t)

    def test_invalid_profiles_rejected(self):
        for value in ['NaN','-0.1','1.1','0.9']:
            t=copy.deepcopy(self.tables);t[1][0]['share_running']=value
            with self.assertRaises(ValueError):fit.calculate(*t)

    def test_unknown_duplicate_or_modified_list_rejected(self):
        for ids in [['O999'],['O001','O001'],['O002','O001','O003','O004','O005']]:
            t=copy.deepcopy(self.tables);t[0][0]['top5_before']=json.dumps(ids)
            with self.assertRaises(ValueError):fit.calculate(*t)

    def test_category_boundary_and_non_string_json_rejected(self):
        t=copy.deepcopy(self.tables);t[0][0]['categories']='["Wellness"]'
        with self.assertRaises(ValueError):fit.calculate(*t)
        for value in ['{}','[1]','["Sport","Sport"]']:
            with self.assertRaises(ValueError):fit.array(value)

    def test_invalid_unapproved_or_mismatched_tags_rejected(self):
        for field,value in [('review_status','pending_review'),('title','wrong'),('sport_tags','Unknown'),('reviewed_by','')]:
            t=copy.deepcopy(self.tables);t[3][0][field]=value
            with self.assertRaises(ValueError):fit.calculate(*t)

    def test_multiple_matching_tags_count_slot_once(self):
        from decimal import Decimal
        shares={'Running':Decimal('0.6'),'Walking':Decimal('0.4'),'Cycling':Decimal(0)}
        slots=[['Running','Walking'],['Cycling'],[]]
        self.assertEqual(fit.match_score(slots[0],shares),Decimal('0.6'))
        self.assertEqual(sum(fit.match_score(tags,shares)>0 for tags in slots),1)
        self.assertEqual(fit.match_score([],shares),0)
        self.assertEqual(fit.match_score(['Cycling'],shares),0)

    def test_only_four_files_read_and_sources_unchanged(self):
        before={p:fit.digest(fit.ROOT/p) for p in fit.SOURCES}
        original=Path.open
        def guarded(path,*args,**kwargs):
            self.assertIn(str(path),{str(fit.ROOT/p) for p in fit.SOURCES})
            return original(path,*args,**kwargs)
        with patch.object(Path,'open',guarded):fit.load()
        self.assertEqual(before,{p:fit.digest(fit.ROOT/p) for p in fit.SOURCES})

    def test_hash_mismatch_and_schema_rejected(self):
        with tempfile.TemporaryDirectory() as directory:
            root=Path(directory)
            for name in fit.SOURCES:
                p=root/name;p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes((fit.ROOT/name).read_bytes())
            p=root/fit.SOURCES[0];p.write_bytes(p.read_bytes()+b'\n')
            with self.assertRaises(ValueError):fit.load(root)
            p.write_text('wrong_header\nwrong\n')
            with patch.object(fit,'HASHES',(fit.digest(p),)+fit.HASHES[1:]):
                with self.assertRaises(ValueError):fit.load(root)

    def test_repeat_bytes_and_refuse_overwrite(self):
        a=fit.payload(fit.evaluate());b=fit.payload(fit.evaluate());self.assertEqual(a,b)
        with tempfile.TemporaryDirectory() as directory:
            p=Path(directory)/'result.json'
            fit.write_result(p,a);fit.write_result(p,b)
            with self.assertRaises(ValueError):fit.write_result(p,b'wrong')
            self.assertEqual(p.read_bytes(),a)


if __name__=='__main__':unittest.main()
