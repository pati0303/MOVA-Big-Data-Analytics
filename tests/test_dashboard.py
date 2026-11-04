"""AP 7.2: meaningful state transitions, source failures and real Streamlit reruns."""
import ast
import hashlib
import json
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch, Mock

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from dashboard.data_access import load_user_ids, check_engine_basis, DataAccessError
from dashboard.state import initialize, user_changed, permissions_changed, capabilities, MODES, SECTIONS
from dashboard.services import recommendation_context, DEMO_DATE


class SourceTests(unittest.TestCase):
    def test_actual_users_and_independent_working_directory(self):
        ids = load_user_ids()
        self.assertEqual(ids, [f'U{i:03}' for i in range(1, 101)])
        self.assertTrue(check_engine_basis())

    def test_missing_sources(self):
        with tempfile.TemporaryDirectory() as tmp:
            with self.assertRaises(DataAccessError):
                load_user_ids(tmp)
            self.assertFalse(check_engine_basis(tmp))

    def test_tampered_source_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / 'data/raw').mkdir(parents=True)
            (root / 'documentation').mkdir()
            content = (ROOT / 'data/raw/users_simulated.csv').read_bytes()
            (root / 'data/raw/users_simulated.csv').write_bytes(content.replace(b'U001', b'U999'))
            (root / 'documentation/active_data_version.json').write_bytes(
                (ROOT / 'documentation/active_data_version.json').read_bytes())
            with self.assertRaisesRegex(DataAccessError, 'Prüfsumme'):
                load_user_ids(root)

    def test_invalid_schema_even_with_matching_hash(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / 'data/raw').mkdir(parents=True)
            (root / 'documentation').mkdir()
            payload = b'user_id\nU001\n'
            (root / 'data/raw/users_simulated.csv').write_bytes(payload)
            (root / 'documentation/active_data_version.json').write_text(json.dumps({
                'active_version': 'V2', 'sha256': {'data/raw/users_simulated.csv': hashlib.sha256(payload).hexdigest()}}))
            with self.assertRaisesRegex(DataAccessError, 'Spalten'):
                load_user_ids(root)


class StateTests(unittest.TestCase):
    def setUp(self):
        self.ids = load_user_ids()
        self.state = {}
        initialize(self.state, self.ids)

    def test_initial_state(self):
        self.assertEqual(self.state['selected_user_id'], 'U001')
        self.assertEqual(self.state['mode'], MODES[0])
        self.assertEqual(capabilities(self.state), {'activity': False, 'offers': False})

    def test_grants_independent(self):
        self.state['interests_permission'] = True
        self.assertEqual(capabilities(self.state), {'activity': False, 'offers': True})
        self.state.update(interests_permission=False, garmin_permission=True)
        self.assertEqual(capabilities(self.state), {'activity': True, 'offers': False})

    def test_user_change_clears_previous_payload_and_grants(self):
        self.state.update(selected_user_id='U002', interests_permission=True,
                          garmin_permission=True, personal_result={'user_id': 'U001'},
                          personal_activity=[1], personal_error='old')
        user_changed(self.state)
        initialize(self.state, self.ids)
        self.assertEqual(self.state['selected_user_id'], 'U002')
        self.assertFalse(any(capabilities(self.state).values()))
        self.assertFalse(any(k.startswith('personal_') for k in self.state))

    def test_revocation_clears_previous_payload(self):
        self.state.update(personal_result={'private': True}, personal_activity=[1], garmin_permission=False)
        permissions_changed(self.state)
        self.assertNotIn('personal_result', self.state)
        self.assertNotIn('personal_activity', self.state)

    def test_mode_keeps_user_and_permissions(self):
        self.state.update(selected_user_id='U042', interests_permission=True, mode=MODES[1])
        initialize(self.state, self.ids)
        self.assertEqual(self.state['selected_user_id'], 'U042')
        self.assertTrue(self.state['interests_permission'])

    def test_invalid_navigation_recovers(self):
        self.state.update(mode='bad', lab_section='bad')
        initialize(self.state, self.ids)
        self.assertEqual(self.state['mode'], MODES[0])
        self.assertEqual(self.state['lab_section'], SECTIONS[0])


class AdapterTests(unittest.TestCase):
    def test_exact_delegation_no_matching_implementation(self):
        engine = Mock()
        engine.run.return_value = {'user_id': 'U002', 'recommendations': []}
        with patch('dashboard.services.importlib.import_module', return_value=engine):
            result = recommendation_context('U002', interests_permission=True, garmin_permission=False)
        engine.run.assert_called_once_with('U002', interests_permission=True,
                                          garmin_permission=False, as_of=DEMO_DATE, root=ROOT)
        self.assertIs(result, engine.run.return_value)

    def test_failure_never_returns_previous_result(self):
        with patch('dashboard.services.importlib.import_module', side_effect=ImportError('missing')):
            with self.assertRaises(DataAccessError):
                recommendation_context('U001', interests_permission=False, garmin_permission=False)

    def test_permissions_must_be_explicit_bool(self):
        with self.assertRaises(ValueError):
            recommendation_context('U001', interests_permission=1, garmin_permission=False)

    def test_no_training_or_model_loading_in_dashboard(self):
        for file in [ROOT/'app.py', *(ROOT/'dashboard').glob('*.py')]:
            tree = ast.parse(file.read_text())
            for node in ast.walk(tree):
                if isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute):
                    self.assertNotIn(node.func.attr, ('fit', 'fit_predict', 'fit_transform', 'predict', 'rank_offers'))
        # Delegation test above checks the observable contract, not only a source scan.


try:
    from streamlit.testing.v1 import AppTest
except ImportError:
    AppTest = None


@unittest.skipIf(AppTest is None, 'Streamlit not installed')
class StreamlitTests(unittest.TestCase):
    def app(self):
        app = AppTest.from_file(str(ROOT / 'app.py'), default_timeout=15).run()
        self.assertEqual(len(app.exception), 0)
        return app

    def test_user_view_starts_without_engine_or_activity_access(self):
        with patch('dashboard.services.recommendation_context', side_effect=AssertionError('implicit inference')):
            app = self.app()
        self.assertEqual(len(app.selectbox[0].options), 100)
        self.assertEqual(app.selectbox[0].value, 'U001')
        self.assertEqual([t.value for t in app.toggle], [False, False])
        self.assertTrue(any('Aktivitätsbereiche gesperrt' in item.value for item in app.info))
        self.assertEqual(len(app.metric), 0)

    def test_mode_switch_and_all_lab_pages(self):
        app = self.app()
        app.selectbox[0].select('U042').run()
        app.segmented_control[0].set_value('ANALYTICS LAB').run()
        self.assertEqual(len(app.exception), 0)
        self.assertEqual(app.selectbox[0].value, 'U042')
        for section in SECTIONS:
            app.sidebar.radio[0].set_value(section).run()
            self.assertEqual(len(app.exception), 0, section)
            self.assertEqual(app.session_state['lab_section'], section)
        app.segmented_control[0].set_value('USER VIEW').run()
        self.assertEqual(app.selectbox[0].value, 'U042')
        app.segmented_control[0].set_value('ANALYTICS LAB').run()
        self.assertEqual(app.sidebar.radio[0].value, SECTIONS[-1])

    def test_grants_mode_change_user_change_and_revocation(self):
        app = self.app()
        app.toggle[0].set_value(True).run()
        self.assertFalse(app.toggle[1].value)
        app.toggle[1].set_value(True).run()
        app.session_state['personal_result'] = {'user_id': 'U001'}
        app.toggle[1].set_value(False).run()
        self.assertNotIn('personal_result', app.session_state)
        self.assertTrue(app.toggle[0].value)
        app.segmented_control[0].set_value('ANALYTICS LAB').run()
        self.assertTrue(app.toggle[0].value)
        self.assertFalse(app.toggle[1].value)
        app.toggle[1].set_value(True).run()
        app.session_state['personal_result'] = {'user_id': 'U001'}
        app.selectbox[0].select('U002').run()
        self.assertEqual([t.value for t in app.toggle], [False, False])
        self.assertNotIn('personal_result', app.session_state)
        app.segmented_control[0].set_value('USER VIEW').run()
        self.assertEqual(app.selectbox[0].value, 'U002')
        self.assertEqual(len(app.exception), 0)

    def test_source_failure_has_no_fallback(self):
        with patch('dashboard.data_access.load_user_ids', side_effect=DataAccessError('Nutzerquelle fehlt')):
            app = AppTest.from_file(str(ROOT/'app.py')).run()
        self.assertEqual(len(app.exception), 0)
        self.assertTrue(any('Nutzerquelle fehlt' in e.value for e in app.error))
        self.assertEqual(len(app.selectbox), 0)
        self.assertEqual(len(app.toggle), 0)


if __name__ == '__main__':
    unittest.main()
