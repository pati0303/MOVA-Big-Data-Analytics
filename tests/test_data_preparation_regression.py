"""AP-4.5-Tests mit echten V2-Daten und ausschließlich isolierten Speicherkopien.

Aufruf: python -m unittest discover -s tests -p 'test_data_preparation_regression.py' -v
"""
import copy
import sys
import unittest
from datetime import date, timedelta
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'src'))
import data_preparation_regression as preparation


class RegressionPreparationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        root = preparation.ROOT
        cls.weekly = preparation.read_csv(root/'data/processed/user_weekly_activities.csv',
                                          preparation.WEEKLY_COLUMNS)
        cls.users = sorted({r['user_id'] for r in cls.weekly})
        cls.rows = preparation.construct_features(cls.weekly, cls.users)

    def test_independent_calendar_reference_for_all_rows(self):
        # Datums-Join statt positionsbasierter Fensterkonstruktion: alle 2.200 Zeilen.
        source = {(r['user_id'], r['week_start']): int(r['activities_count']) for r in self.weekly}
        for row in self.rows:
            begin = date.fromisoformat(row['week_start'])
            values = [source[row['user_id'], (begin-timedelta(days=days)).isoformat()]
                      for days in (21,14,7,0)]
            self.assertEqual(row['avg_activities_last_4_weeks'], sum(values)/4)
            self.assertEqual(row['activities_current_week'], values[-1])
            self.assertEqual(row['activities_next_week'],
                             source[row['user_id'], (begin+timedelta(days=7)).isoformat()])
        preparation.validate(self.rows, self.weekly, self.users)

    def test_future_change_cannot_change_earlier_inputs(self):
        altered = copy.deepcopy(self.weekly)
        changed = next(r for r in altered if r['user_id']=='U001' and r['week_index']=='5')
        changed['activities_count'] = str(int(changed['activities_count'])+1)
        result = preparation.construct_features(altered, self.users)
        for before,after in zip(self.rows,result):
            if before['user_id']!='U001' or before['week_index']<5:
                for feature in preparation.MODEL_FEATURES:
                    self.assertEqual(before[feature],after[feature])
            if before['user_id']=='U001' and before['week_index']==4:
                self.assertEqual(after['activities_next_week'], before['activities_next_week']+1)
            else:
                self.assertEqual(before['activities_next_week'],after['activities_next_week'])

    def test_validator_detects_future_value_in_window(self):
        altered = copy.deepcopy(self.rows)
        row = altered[0]  # U001, Woche 4: wahre Historie [0,0,2,0], Folgewoche 1.
        self.assertEqual(row['avg_activities_last_4_weeks'], .5)
        row['avg_activities_last_4_weeks'] = (0+2+0+1)/4  # absichtlich t-2 bis t+1
        with self.assertRaises(preparation.QualityError):
            preparation.validate(altered, self.weekly, self.users)

    def test_missing_history_and_duplicate_week_stop(self):
        with self.assertRaises(preparation.QualityError):
            preparation.construct_features(self.weekly[1:], self.users)
        altered = copy.deepcopy(self.weekly)
        altered[0] = copy.deepcopy(altered[1])
        with self.assertRaises(preparation.QualityError):
            preparation.construct_features(altered, self.users)

    def test_real_zero_history_and_observation_edges(self):
        first = self.rows[0]
        self.assertEqual((first['user_id'],first['week_index']),('U001',4))
        self.assertEqual((first['activities_current_week'],first['avg_activities_last_4_weeks'],
                          first['activities_next_week']), (0,.5,1))
        for uid in self.users:
            rows = [r for r in self.rows if r['user_id']==uid]
            self.assertEqual([r['week_index'] for r in rows],list(range(4,26)))
            self.assertEqual(rows[-1]['week_start'],'2026-06-22')
            self.assertEqual(rows[-1]['week_end'],'2026-06-28')

    def test_month_boundaries_and_group_isolation(self):
        # Einschließlich Monatswechsel März/April und Mai/Juni sowie Beobachtungsrand.
        for uid in ['U001','U045','U100']:
            for index in [4,13,21,25]:
                row = next(r for r in self.rows if r['user_id']==uid and r['week_index']==index)
                history = [r for r in self.weekly if r['user_id']==uid and
                           index-3<=int(r['week_index'])<=index]
                target = next(r for r in self.weekly if r['user_id']==uid and int(r['week_index'])==index+1)
                self.assertEqual(len(history),4)
                self.assertEqual(row['avg_activities_last_4_weeks'],sum(int(r['activities_count']) for r in history)/4)
                self.assertEqual(row['activities_next_week'],int(target['activities_count']))
        shuffled = list(reversed(copy.deepcopy(self.weekly)))
        self.assertEqual(preparation.construct_features(shuffled,self.users),self.rows)

    def test_wrong_target_and_invalid_counts_rejected(self):
        rows = copy.deepcopy(self.rows);rows[0]['activities_next_week']+=1
        with self.assertRaises(preparation.QualityError):
            preparation.validate(rows,self.weekly,self.users)
        for invalid in ['','-1','NaN','1.5']:
            weekly=copy.deepcopy(self.weekly);weekly[0]['activities_count']=invalid
            with self.assertRaises(preparation.QualityError):
                preparation.construct_features(weekly,self.users)


if __name__ == '__main__':
    unittest.main()
