# MOVA V3 – ML-Integration im Analytics Lab

## Bestand und Erweiterung

`dashboard/analytics_view.py` enthält die bestehende Navigation (`PAGES`) und
`recommendations()`. Der historische Vergleich verwendet
`ResearchData.recommendation_totals()` und `recommendation_case()` aus
`dashboard/analytics_data.py`: 30 Bestandsangebote, Interessenfilter versus
Sportartenpriorisierung, 64/100 veränderte Zusammensetzungen. Dieser Code und
seine Darstellung bleiben erhalten. Ein zusätzlicher Render-Aufruf folgt direkt
auf die bisherigen Quellen; es gibt keine weitere Kategorie oder Navigation.

`dashboard/ml_integration.py` ergänzt die nachgelagerte Iteration
Modeling → Evaluation → Deployment, zwei kompakte Regelerklärungen, einen
horizontalen Balkenvergleich mit direkten Wertbeschriftungen und einen
Erkenntniskasten. Farben und Diagrammlayout stammen aus dem bestehenden Design.

`load_ablation()` liest ausschließlich `outputs/ml_recommendations_v1/comparison.json`,
prüft dessen SHA-256 gegen das vorhandene `manifest.json` und zählt Unterschiede
aller geordneten Angebots-ID-Listen erneut im Speicher. Die Zusammenfassung muss
mit den gespeicherten Einzelfällen übereinstimmen. Es werden nur aggregierte
Zahlen an die Darstellung zurückgegeben; kein Engine-Aufruf, Training oder Export.
Ohne ML ist die Referenz mit identischem 38er-Katalog und gleicher Gruppierung.
Die gespeicherten Ergebnisse lauten 63/100, 9/100 und 63/100. Sie belegen Einfluss,
keine Verbesserung tatsächlicher Relevanz oder Qualität.

Fehlende Dateien, ungültiges JSON, Hashabweichungen oder widersprüchliche Werte
führen zu einem lokalen Warnhinweis ohne Ersatzwerte; der historische Vergleich
bleibt sichtbar. Tests stehen in `tests/test_dashboard_ml_integration.py`.

## Fachlicher Abgleich

Geprüft: `src/ml_recommendation_rules.py` (`select_variants`),
`src/recommendation_engine.py` (`rank_offers`, `recommendations`) und
`data/catalog/recommendation_metadata_v1.json`.

- Cluster 0: O031/O036 für gelegentliche Nutzung; Cluster 1: O032/O037 für häufige Nutzung.
- Regression <2: O033; >=3: O034 mit drei wöchentlichen Terminen.
- Präzisierung zur Aufgabenbeschreibung: Im Intervall [2,3) wird keine spezielle
  Regressionsvariante gewählt (`sessions=None`). Die Standardauswahl bleibt
  erhalten, im aktuellen Katalog O033. Es gibt keine separat erlernte Standardvariante.
- Nur gültige Modellinformationen, positive passende Sporthistorie und autorisierte
  Aktivitätsdaten erlauben ML-Einfluss. Interessen filtern weiterhin verbindlich.
- Die Regression prognostiziert Gesamtaktivitäten, keine Laufeinheiten oder Terminverfügbarkeit.
- Die Gruppenposition bleibt unverändert. Regeln und Schwellen sind Demoannahmen.

## Erneuter Launch über das bestehende Repository

Nach lokal erfolgreicher Prüfung Änderungen gezielt vormerken:

```bash
git add dashboard/analytics_view.py dashboard/ml_integration.py tests/test_dashboard_ml_integration.py tests/test_dashboard_analytics.py tests/test_mova_v3_reference.py documentation/analytics_ml_integration.md
git diff --cached --check
git diff --cached
git commit -m "Extend Analytics Lab with saved ML ablation"
```

Den Arbeitsbranch im bestehenden Repository `pati0303/MOVA-Big-Data-Analytics`
pushen und über einen Pull Request nach `main` übernehmen. Falls direkt auf
`main` gearbeitet wird, den geprüften Commit nach `origin main` pushen.
Die laufende App verwendet laut vorhandener Deploymentdokumentation `main` und
`app.py`; diese Zuordnung vor dem Launch im Verwaltungsportal bestätigen.

In Streamlit Community Cloud die bestehende App
https://mova-big-data-analytics.streamlit.app/ verwalten. Python 3.12 und den neuen
Commit prüfen, Build/Neustart und Logs kontrollieren; bei Bedarf „Reboot app“.
Keine Änderung der Deploymentkonfiguration ist Teil dieser Erweiterung.

Abnahme online: User View mit U070, danach beide simulierten Freigaben aktivieren;
Angebote und Modellbegründungen prüfen. Analytics Lab → Empfehlungssystem:
historischen Vergleich (64/100) und neuen ML-Abschnitt (63/9/63) prüfen, auch ohne
Freigaben. Übrige Analytics-Bereiche öffnen. Veröffentlichung und Bestätigung der
laufenden Cloudinstanz erfolgen durch die Betreiber, nicht durch diese Änderung.

## Technische Prüfung dieser Erweiterung

- Streamlit 1.66.1 startet lokal unter Python 3.12; Browsercheck mit Chromium bei
  1366 × 900: neuer Abschnitt und Balkenbeschriftungen sichtbar, keine JavaScriptfehler.
  Screenshots wurden lokal geprüft.
- Neue vier Tests prüfen 63/9/63 gegen die gespeicherten Listen, fehlende und
  beschädigte Quellen, widersprüchliche Zusammenfassungen sowie den Fortbestand
  des historischen Vergleichs bei fehlender ML-Auswertung.
- Bestehende Freigabeprüfung präzisiert: öffentliche Modellbeispiele dürfen
  „Laufschuhe“ nennen; individuelle Vergleichskarten verschwinden bei Nutzerwechsel.
  Die Dateigrenzprüfung erlaubt genau das neue Dashboardmodul; unveränderte
  Design-Dateien bleiben weiterhin hashgeprüft. Der Training-Call-Check erfasst
  auch das neue Modul.
- Erster Gesamtlauf vor der Replay-Testkorrektur: 230 Tests, davon 207 bestanden, 22 Trainingstests übersprungen,
  ein bestehender numerischer Replay-Test fehlgeschlagen (siehe unten). User View,
  alle bisherigen Analytics-Bereiche und historischer Vergleich bestehen die Tests.
  Aufruf: `python tests/run_without_training.py`; Training explizit
  blockiert; 22 Trainingstests werden bewusst übersprungen. Kein Modelltraining.
- Alle 155 bestehenden Dateien unter `data/`, `outputs/` und `src/` wurden
  nach den Prüfungen per SHA-256 als bytegleich bestätigt. Der historische
  `recommendations()`-Funktionskörper ist per AST bis auf den abschließenden
  Aufruf des neuen Renderers identisch zum ursprünglichen Stand.
- Ursprünglicher Bestandsbefund (durch die unten dokumentierte Assertion-Korrektur behoben): `test_evaluation_artifacts_and_actual_outputs` in
  `tests/test_ml_recommendations.py` vergleicht Prognoseprofile mit exakter
  Float-Gleichheit. In dieser Laufzeit weicht eine gespeicherte Prognose um etwa
  9 × 10⁻¹⁶ ab. Auch `OPENBLAS_NUM_THREADS=1` beseitigt die Abweichung nicht.
  Engine, Modelle und Ergebnisdateien wurden dafür nicht verändert. Die
  Ablationsanzeige verwendet ausschließlich die gespeicherten, verifizierten
  Listen und ist davon unabhängig. Die anschließende Untersuchung und gezielte Testkorrektur sind unten dokumentiert.
- Nicht durchgeführt: Veröffentlichung, Push/Merge, Prüfung der laufenden
  Streamlit-Cloudinstanz oder ihrer Buildlogs. Deploymentkonfiguration unverändert.

Die Dashboarderweiterung ist lokal funktionsfähig. Die Onlineabnahme der veröffentlichten Instanz bleibt beim Betreiber.


## Untersuchung und Korrektur des numerischen Replay-Tests

Betroffen: `MLRecommendationsTests.test_evaluation_artifacts_and_actual_outputs`
in `tests/test_ml_recommendations.py`. Ursprüngliche Assertion:
`self.assertEqual(row['profile'], self.actual[row['user_id']]['profile'])`.
Damit wurden auch neu berechnete Fließkommaprognosen bitgenau verglichen.

Die Untersuchung aller 100 Profile zeigt ausschließlich Abweichungen im Feld
`regression_prediction`: 13 Werte unterscheiden sich um ein bis zwei binary64-ULPs,
maximal 8.881784197001252e-16. Alle anderen Profilfelder sowie alle 400 vollständigen
Empfehlungslisten der vier Varianten sind exakt identisch.

Beispiel U002: gespeichert 3.6927952445497203, Replay 3.6927952445497194.
Mit 60-stelliger Decimal-Arithmetik auf den gespeicherten binary64-Koeffizienten
und identischen Eingängen ergibt sich
3.692795244549719857474201489822007715702056884765625.
Beide Werte liegen jeweils 4.440892098500626e-16 davon entfernt. Dies bestätigt
Rundung bei der Auswertung der linearen Formel; die genaue CPU-/BLAS-Operation,
die unterschiedlich gerundet hat, ist damit nicht isoliert. Kein Hinweis auf
abweichende Modelle oder Eingaben. Die nächste gespeicherte Prognose liegt
0.00568441842583578 von einer Entscheidungsschwelle (2 oder 3) entfernt;
die beobachteten Abweichungen ändern keine Entscheidung.

Geändert wurde ausschließlich der Profilvergleich dieser Testmethode:
Alle Felder außer `regression_prediction` bleiben exakt verglichen, nur diese
Prognose verwendet `assertAlmostEqual(..., delta=1e-15)`. Die absolute Toleranz
liegt knapp über dem beobachteten Maximum; es gibt keine zusätzliche relative
Toleranz. Vollständige Empfehlungslisten, Quell- und Artefaktprüfsummen bleiben
unverändert streng geprüft. Modelle, Daten, Regeln und Evaluationsergebnisse
wurden nicht verändert.

Der betroffene Einzeltest besteht (1 Test, OK).

Abschließender Gesamtlauf: `python tests/run_without_training.py` – 230 Tests,
208 bestanden, 22 Trainingstests bewusst übersprungen, keine Fehler
(`OK (skipped=22)`). Die Trainingsaufrufe werden vom Runner aktiv blockiert.
Zusätzlich `git diff --check` ohne Befund und alle 155 bestehenden Dateien
unter `data/`, `outputs/` und `src/` per SHA-256 weiterhin bytegleich.
