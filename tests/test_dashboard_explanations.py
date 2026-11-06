"""Public Streamlit API checks for explanatory UI; never fit a model."""
from pathlib import Path
import sys
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from streamlit.testing.v1 import AppTest
from dashboard.cycle2 import TITLE


class ExplanationTests(unittest.TestCase):
    def setUp(self):
        for target in ('sklearn.linear_model.LinearRegression.fit', 'sklearn.cluster.KMeans.fit'):
            guard = patch(target, side_effect=AssertionError('No training in UI'))
            guard.start()
            self.addCleanup(guard.stop)
        self.app = AppTest.from_file(str(ROOT / 'app.py'), default_timeout=30).run()
        self.app.segmented_control[0].set_value('ANALYTICS LAB').run()

    def section(self, name):
        self.app.sidebar.radio[0].set_value(name).run()
        self.assertFalse(self.app.exception)
        self.assertFalse(self.app.error)

    def text(self):
        return '\n'.join(x.value for kind in ('markdown', 'caption', 'info', 'warning', 'success')
                         for x in getattr(self.app, kind))

    def test_recommendation_definitions_and_saved_variant_identity(self):
        self.section('Empfehlungssystem')
        text = self.text()
        for phrase in ('Stufe A – Sportbezogen', 'Stufe B – Interessenbasiert',
                       'Kaufwahrscheinlichkeit', 'ohne bestätigte Tags',
                       'mit acht bestätigten Tags', 'dieselben Freigaben und Interessen'):
            self.assertIn(phrase, text)
        for toggle in self.app.toggle:
            toggle.set_value(True)
        self.app.run()
        self.assertFalse(self.app.exception)
        self.assertIn('#### Nur Interessen berücksichtigt', self.text())
        self.assertIn('#### Interessen und Sportarten berücksichtigt', self.text())

    def test_iteration_dynamic_definitions_and_all_six_phases(self):
        self.section('CRISP-DM')
        self.assertIn('K-Means und Regression zusätzlich dokumentierte Angebotsvarianten', self.text())
        select = next(w for w in self.app.selectbox if w.key == 'iteration_metric')
        for value, phrase in [('Top2_Mittel_%', 'beiden häufigsten Sportarten'),
                              ('Mittlere_Sportartenanzahl', 'Durchschnittliche Anzahl unterschiedlicher Sportarten'),
                              ('Nutzer_8_Sportarten', 'alle acht Sportarten'),
                              ('Aktivitaeten', 'Gesamtzahl der Aktivitäten'),
                              ('Nullwochen', 'genau null Aktivitäten')]:
            select.set_value(value).run()
            self.assertIn(phrase, '\n'.join(x.value for x in self.app.caption))
            self.assertFalse(self.app.exception)
        self.assertNotIn('Technische Git-Probleme', self.text())
        phase = next(w for w in self.app.selectbox if w.key == 'crisp_phase')
        for value in phase.options:
            phase.set_value(value).run()
            self.assertFalse(self.app.exception)
        self.assertIn('Interaktive Einblicke in unsere Daten', self.text())

    def test_validation_window_explanations_and_negative_decision(self):
        self.section(TITLE)
        text = self.text()
        for phrase in ('t−3 bis t', 't+1', '4–9', '10–13', '4–13', '14–17',
                       '4–17', '18–21', '400 Validierungsfälle', '1.200',
                       'kein unabhängiger Bestätigungstest', 'nachträglichen Fehleranalyse',
                       '0,000493', '2 von 3 Folds', 'UND-Regel'):
            self.assertIn(phrase, text)
        self.assertEqual(len(self.app.get('plotly_chart')), 3)
        self.assertIn('1,522613', [x.value for x in self.app.metric])
        self.assertIn('1,523105', [x.value for x in self.app.metric])


if __name__ == '__main__':
    unittest.main()
