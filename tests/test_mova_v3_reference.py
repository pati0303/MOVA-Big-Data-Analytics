"""Preserve the user-approved V2 design and all imported lab artifacts byte for byte."""
import hashlib
import json
from pathlib import Path
import unittest

ROOT=Path(__file__).resolve().parents[1]


class MOVAV3ReferenceTests(unittest.TestCase):
    def test_v2_design_and_explicit_extension_boundary(self):
        reference=json.loads((ROOT/'documentation/mova_v3_reference.json').read_text())
        extended={'app.py','dashboard/analytics_data.py','dashboard/data_access.py',
                  'dashboard/analytics_view.py','dashboard/user_view.py'}
        actual={p for p,record in reference['ui'].items()
                if hashlib.sha256((ROOT/p).read_bytes()).hexdigest()!=record['sha256']}
        self.assertEqual(actual,extended)
        for p,record in reference['ui'].items():
            if p not in extended:
                self.assertEqual(hashlib.sha256((ROOT/p).read_bytes()).hexdigest(),record['sha256'],p)
        self.assertEqual({p.relative_to(ROOT).as_posix() for p in (ROOT/'dashboard').glob('*') if p.is_file()},
                         {p for p in reference['ui'] if p.startswith('dashboard/')} | {'dashboard/ml_integration.py'})

    def test_all_v2_lab_documents_figures_and_retrospective_preserved(self):
        reference=json.loads((ROOT/'documentation/mova_v3_reference.json').read_text())
        self.assertEqual(len(reference['lab_artifacts']),22)
        for p,expected in reference['lab_artifacts'].items():
            self.assertEqual(hashlib.sha256((ROOT/p).read_bytes()).hexdigest(),expected,p)


if __name__=='__main__':unittest.main()
