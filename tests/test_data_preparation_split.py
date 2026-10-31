"""Chronologischer Split: echte V2-Referenz und isolierte technische Fehlerfälle."""
import copy
import random
import sys
import unittest
from collections import Counter
from datetime import date, timedelta
from pathlib import Path

sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'src'))
import data_preparation_split as split


class ChronologicalSplitTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.source = split.read_csv(split.ROOT/split.INPUT_PATH, split.OUTPUT_COLUMNS)
        cls.users = sorted({r['user_id'] for r in cls.source})
        cls.train,cls.test = split.split_rows(cls.source,cls.users)

    def test_complete_unchanged_partition(self):
        self.assertEqual((len(self.train),len(self.test)),(1800,400))
        self.assertEqual(Counter(r['user_id'] for r in self.train),Counter({u:18 for u in self.users}))
        self.assertEqual(Counter(r['user_id'] for r in self.test),Counter({u:4 for u in self.users}))
        self.assertEqual(sorted(self.train+self.test,key=split.key),sorted(self.source,key=split.key))
        self.assertFalse({split.key(r) for r in self.train}&{split.key(r) for r in self.test})

    def test_order_independence(self):
        shuffled=copy.deepcopy(self.source)
        random.Random(42).shuffle(shuffled)  # Nur Zeilenreihenfolge, keine Datengenerierung.
        self.assertEqual(split.split_rows(shuffled,self.users),(self.train,self.test))
        self.assertEqual(split.csv_payload(self.train),split.csv_payload(split.split_rows(shuffled,self.users)[0]))
        self.assertEqual(split.split_rows(list(reversed(self.source)),self.users),(self.train,self.test))

    def test_wrong_boundaries_overlap_and_gap_rejected(self):
        for train,test in [(range(4,23),range(23,26)),(range(4,23),range(22,26)),
                           (range(4,21),range(22,26))]:
            with self.assertRaises(split.QualityError):
                split.split_rows(self.source,self.users,train,test)

    def test_target_calendar_separation(self):
        train_end=max(date.fromisoformat(r['week_end'])+timedelta(days=7) for r in self.train)
        test_begin=min(date.fromisoformat(r['week_start'])+timedelta(days=7) for r in self.test)
        self.assertEqual(train_end,date(2026,6,7))
        self.assertEqual(test_begin,date(2026,6,8))
        self.assertLess(train_end,test_begin)
        for uid in self.users:
            self.assertEqual([int(r['week_index']) for r in self.train if r['user_id']==uid],list(range(4,22)))
            self.assertEqual([int(r['week_index']) for r in self.test if r['user_id']==uid],list(range(22,26)))

    def test_missing_duplicate_or_changed_rows_rejected(self):
        broken=copy.deepcopy(self.source);broken[0]=copy.deepcopy(broken[1])
        with self.assertRaises(split.QualityError):split.split_rows(broken,self.users)
        with self.assertRaises(split.QualityError):split.split_rows(self.source[1:],self.users)
        altered=copy.deepcopy(self.train);altered[0]['avg_activities_last_4_weeks']='0.75'
        with self.assertRaises(split.QualityError):
            split.validate_split(self.source,altered,self.test,self.users)

    def test_invalid_values_rejected(self):
        for field,value in [('activities_next_week','-1'),('activities_next_week','1.5'),
                             ('activities_next_week',''),('avg_activities_last_4_weeks','inf'),
                             ('avg_activities_last_4_weeks','NaN'),('week_start','2026-01-27')]:
            broken=copy.deepcopy(self.source);broken[0][field]=value
            with self.assertRaises(split.QualityError):split.split_rows(broken,self.users)

    def test_roles_and_rolling_history(self):
        self.assertEqual(split.MODEL_FEATURES,['activities_current_week','avg_activities_last_4_weeks'])
        self.assertNotIn(split.TARGET,split.MODEL_FEATURES)
        self.assertTrue(set(split.METADATA).isdisjoint(split.MODEL_FEATURES))
        weekly=split.read_csv(split.ROOT/'data/processed/user_weekly_activities.csv',split.WEEKLY_COLUMNS)
        source={(r['user_id'],int(r['week_index'])):int(r['activities_count']) for r in weekly}
        # Woche 23 ist erst Ziel der ersten und danach bekannter Eingang der zweiten Testzeile.
        first=next(r for r in self.test if r['user_id']=='U001' and r['week_index']=='22')
        later=next(r for r in self.test if r['user_id']=='U001' and r['week_index']=='23')
        self.assertEqual(later['activities_current_week'],first['activities_next_week'])
        self.assertEqual(float(later['avg_activities_last_4_weeks']),
                         sum(source['U001',week] for week in range(20,24))/4)


if __name__=='__main__':
    unittest.main()
