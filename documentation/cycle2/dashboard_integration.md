# Analytics Lab – zweiter Modellierungszyklus

Stand: 04.11.2026. Branch: `feature/crispdm-cycle-2`.

## Zugriff und Darstellung

ANALYTICS LAB → Forschungsbereich → **CRISP-DM – Zweiter Modellierungszyklus**.
Alle sieben bisherigen Bereiche bleiben erreichbar. Die User View wurde nicht verändert.

Der neue Bereich verwendet vorhandene MOVA-Designfarben und Plotly-Layouts:
dunkle Flächen, Mintgrün für die bisherige Regression, Blau für die Erweiterung,
Orange für Persistenz. Große Kennzahlen und drei Diagramme zeigen Gesamtvergleich,
chronologische Foldintervalle und Fold-MAE. Ein ausdrücklich als Rechenbeispiel
gekennzeichnetes Fensterpaar erläutert die zusätzliche Information der Nullzählung.
Sechs Phasenkarten und eine Pfeilkette verbinden beide CRISP-DM-Zyklen.

## Quellen und Sicherheit

`dashboard/cycle2.py` liest ausschließlich gespeicherte aggregierte Artefakte aus
`outputs/cycle2/`: comparison.csv, metrics_by_fold.csv, zero_week_analysis.csv,
decision.json und validation_manifest.json. Die Hashes werden gegen run_manifest.json
geprüft; Umfang, Foldzeiten, Verfahren, MAE-/RMSE-Aggregation, Gruppen und die
Modellentscheidung werden auf Konsistenz geprüft. Keine Ersatzwerte bei Fehlern.
Das lokale Manifest ist ein Konsistenznachweis, keine unabhängige digitale Signatur.

Keine Trainingsmodule importiert, keine Modellartefakte geladen oder geschrieben.
Die bisherigen 400 Testfälle werden vom neuen Loader nicht geöffnet. Vorhandene
Dashboardtests prüfen weiterhin die unveränderten alten Ansichten einschließlich
ihrer historischen Ergebnisse; das ist keine neue Modellauswahl oder Modellierung.

Angezeigter gepoolter MAE: Persistenz 1,729167; zwei Merkmale 1,522613;
drei Merkmale 1,523105. Bei 259 zukünftigen Nullzielen: Regressions-MAE 1,708690
gegenüber 1,713798. Entscheidung: zusätzliches Merkmal verworfen, bisheriges
Modell bleibt bestehen. Sämtliche Werte stammen aus den gespeicherten Tabellen.

## Änderungen

Geändert: app.py (Navigationszähler), dashboard/state.py (zusätzlicher Bereich),
dashboard/analytics_view.py (Registrierung), tests/test_dashboard.py (letzte
registrierte Seite statt fest kodierter bisheriger letzter Seite).
Neu: dashboard/cycle2.py, tests/test_dashboard_cycle2.py und dieser Bericht.

## Tatsächliche Prüfungen

- 5 neue Tests: gespeicherte Kennzahlen/Entscheidung, eng begrenzte Dateizugriffe,
  fehlende/manipulierte Dateien, widersprüchliche Entscheidung und Streamlit-AppTest
  für Start, drei Diagramme, Entscheidungstext und Rückkehr zur User View.
- Insgesamt 58 Dashboardtests (`test_dashboard*.py`) bestanden, einschließlich
  der fünf neuen Tests; während des Laufs waren LinearRegression.fit, KMeans.fit
  und StandardScaler.fit durch Fehler auslösende Sperren ersetzt.
- Echten Streamlit-Server gestartet: HTTP-Health-Endpunkt antwortete 200 `ok`.
  Testserver anschließend beendet.
- `git diff --check` ohne Befund.
- Hashprüfung: unveränderte bestehende Daten, Modelle und Ergebnisartefakte;
  sämtliche im Zyklus-2-Laufmanifest verzeichneten Artefakte weiterhin identisch.

Reproduktion der UI-Tests in einer Umgebung mit requirements-dashboard.txt:

```bash
python -m unittest discover -s tests -p 'test_dashboard*.py' -v
streamlit run app.py
```

Die Testumgebung liegt lokal isoliert unter work/dashboard-venv; Streamlit 1.66.1
und Plotly 6.4.0 entsprechen den vorhandenen Projektvorgaben. Keine Änderung an
Abhängigkeitsdateien. Keine neuen Modellfits und keine neuen wissenschaftlichen
Experimente. Kein PR erstellt oder gemergt.

Ein manueller visueller Abnahmelauf im tatsächlichen Aufnahmebrowser wurde nicht
vorgenommen. Für die Videoaufnahme empfiehlt sich eine kurze Prüfung von Zoom und
Fenstergröße; die Seite ist vertikal in Abschnitte gegliedert.
