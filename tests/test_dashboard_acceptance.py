"""AP 7.5a: regression checks for byte portability and compact result-first views."""
from pathlib import Path
import subprocess
import sys
import unittest

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from streamlit.testing.v1 import AppTest


class AcceptanceTests(unittest.TestCase):
    def test_windows_checkout_filters_preserve_verified_source_bytes(self):
        # Real Git working-tree filtering with Windows-style user settings; no writes.
        for path in ['data/raw/activities_simulated.csv','data/processed/user_weekly_activities.csv',
                     'outputs/models/regression_linear_metadata.json','outputs/models/regression_linear.joblib']:
            spec=f'23ac008651de490d59e9ec5ceae590ba97daf0e5:{path}'
            expected=subprocess.check_output(['git','-C',str(ROOT),'show',spec])
            filtered=subprocess.check_output(['git','-C',str(ROOT),'-c','core.autocrlf=true',
                                              'cat-file','--filters',f'--path={path}',spec])
            self.assertEqual(filtered,expected,path)

    def test_compact_comparison_keeps_original_order_and_grant_reset(self):
        a=AppTest.from_file(str(ROOT/'app.py'),default_timeout=20).run()
        a.toggle[0].set_value(True).run();a.toggle[1].set_value(True).run()
        a.segmented_control[0].set_value('ANALYTICS LAB').run()
        a.sidebar.radio[0].set_value('Empfehlungssystem').run()
        self.assertEqual(len(a.exception),0)
        lists=[m.value for m in a.markdown if 'class="mova-compare-list"' in m.value]
        self.assertEqual(len(lists),2)
        for text,ids in zip(lists,[['O001','O002','O003','O004','O005'],['O001','O006','O009','O010','O002']]):
            offsets=[text.index(oid) for oid in ids]
            self.assertEqual(offsets,sorted(offsets))
            self.assertEqual(text.count('class="mova-compare-row"'),5)
        a.selectbox[0].select('U002').run()
        self.assertFalse(any('class="mova-compare-list"' in m.value for m in a.markdown))
        self.assertEqual([t.value for t in a.toggle],[False,False])
