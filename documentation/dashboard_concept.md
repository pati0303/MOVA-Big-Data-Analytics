# MOVA – Move beyond: Dashboard-Konzept AP 7.1

Stand: 01.11.2026. Konzept und Bestandsprüfung, noch keine Webanwendung.

## 1. Zielsetzung und verifizierte Ausgangsbasis

Eine lokal ausführbare Webanwendung präsentiert die Geschäftsidee und die wissenschaftliche Arbeit aus AP 1–6. Zwei Ansichten teilen Daten, Modelle und Empfehlungsengine. Wissenschaftliche Schwerpunkte sind Datenverständnis, Aufbereitung, Feature Engineering, mathematische Modelllogik, Evaluation und die tatsächlich dokumentierte CRISP-DM-Iteration.

GitHub-Integration am 01.11.2026 geprüft:

- PR #6: geschlossen und `merged=true`, Merge am 31.10.2026 um 13:06:13 UTC (14:06:13 Uhr Europe/Berlin).
- Tatsächlicher Branchkopf `main`: `23ac008651de490d59e9ec5ceae590ba97daf0e5`, über GitHub-Branch-Endpunkt bestätigt.
- Git-Baum: `cd1b2099d36f3763cb99c8e91f72b8ab8eefd036`.
- AP-6-Feature-Commit `62ae54efb12e77109b73dd140ebe2ba06230cdae` ist zweiter Merge-Elterncommit. Sein Dateibaum und der Merge-Dateibaum sind identisch.
- Neuer Worktree `/workspace/MOVA-AP7`, neuer Branch `ap7-dashboard`, exakt vom bestätigten main-Commit erstellt. Vorheriger Worktree bleibt inhaltlich unverändert; nur die für einen Git-Worktree erforderlichen gemeinsamen Git-Metadaten wurden ergänzt.
- `git fsck --full` ohne Befund. Der rekursiv über die Integration gelesene GitHub-Baum ist vollständig (`truncated=false`). Alle 168 versionierten Dateien wurden anhand ihrer Git-Blobhashes mit den lokalen Bytes abgeglichen: 168 Übereinstimmungen, keine Abweichung. Die 15 AP-6-Dateien sind damit ebenfalls vollständig vorhanden. Aktive V2-Hashes und die geprüften Modell-/Quellhashes stimmen.

Der bekannte Git-Proxy wird nicht umgangen: Remote-Nachweis über die GitHub-Integration, Worktree aus bereits lokal vorhandenem, remote bestätigtem Commit. Ein direkter Fetch war dafür unnötig. Der derzeitige GitHub-Stand ist eine Prüfung zum genannten Datum, keine Garantie gegen spätere Remote-Änderungen.

Abgrenzung: keine Rohdaten-/Modelländerung, kein Training, keine neuen Angebote, keine Rankingänderung, kein Commit, kein PR. Alle folgenden App-Dateien und Interaktionen sind Planung für AP 7.2–7.5.

## 2. Zwei-Ansichten-Konzept

**MOVA USER VIEW:** Sport-/Lifestyle-Demo für simulierte Garmin-Nutzer. Persönliche Aktivitätsübersicht, gespeichertes Segment, unverbindliche Folgewochenschätzung und maximal fünf tatsächlich berechnete fiktive Angebote. Wenig Fachsprache, nachvollziehbare Begründungen.

**MOVA ANALYTICS LAB:** didaktische Untersuchung derselben synthetischen V2 und bestehenden Ergebnisse. Erklärt Datenpipeline, Merkmalsgewichtung, Clusterwahl, Regression, Baseline, Regelwirkung und Projektverlauf. Jede Hauptseite hat mindestens eine fachlich begründete Interaktion.

Ein sichtbarer Umschalter im Kopfbereich wechselt beide Ansichten innerhalb desselben Streamlit-Prozesses. Streamlit führt bei Interaktionen das Skript erneut aus; das ist kein Serverneustart. Die ausgewählte Nutzer-ID wird im gemeinsamen Session State erhalten. Die Ansichten erzeugen keine getrennten Modellinstanzen mit abweichender Fachlogik.

Das Lab ist ausdrücklich eine Untersuchung des synthetischen Hochschuldatensatzes. Globale Forschungsanalysen sind von den simulierten Freigaben der User View zu unterscheiden; ein Moduswechsel erteilt keine Freigabe. Persönliche Engine-Demonstrationen im Lab beachten dieselben Simulationsparameter. Der gespeicherte AP-6-Vergleich ist als historischer Versuch unter festen True/True-Bedingungen beschriftet, kein Ergebnis aktuell erteilter Freigaben.

## 3. Technologieentscheidung

**Entscheidung: Streamlit + Plotly + bestehende Python-Module, CSV/JSON/joblib, ein lokaler Prozess.**

| Ansatz | Eignung für den tatsächlichen Bestand | Aufwand und Entscheidung |
| --- | --- | --- |
| Streamlit + Plotly | Beide stehen bereits in `requirements.txt`; direkte Python-Imports, Session State, native Regler, Tabellen und interaktive Charts; keine API nötig | Gewählt. Geringster Integrationsaufwand, gute Präsentierbarkeit mit gezielter Gestaltung |
| Dash + Plotly | Python und detaillierte Callbacksteuerung geeignet; Dash ist keine vorhandene Abhängigkeit | Mehr Callback-/Layoutarbeit; hier kein ausreichender Zusatznutzen |
| NiceGUI | Python-basierte flexible Komponenten; ebenfalls nicht im Bestand | Zusätzlicher Frameworkwechsel und Lern-/Stabilisierungsaufwand |
| React/Vue + Python-API | Größte gestalterische Freiheit | Separate Frontend-Toolchain und API nötig; widerspricht Effizienz und schlanker Infrastruktur |
| Reine HTML/JS-App | Gut für statische Lehrbeispiele | Bestehende joblib-Modelle und Engine nicht direkt nutzbar; Risiko doppelter Logik |

Die Auswahl folgt den Projektkriterien, keinem durchgeführten UI-Benchmark. Streamlit hat Grenzen bei pixelgenauen Layouts und komplexen Animationen. Diese rechtfertigen für die geplanten Filter, Schritte und gespeicherten Fallvergleiche kein separates Backend.

Tatsächlich verfügbare Laufzeit: Python 3.12.14, NumPy 2.3.5, pandas 2.2.3, scikit-learn 1.8.0, joblib 1.5.3; passend zur dokumentierten Modellumgebung. Streamlit und Plotly sind hier noch nicht installiert. AP 7.2 installiert und fixiert kompatible UI-Versionen in einer isolierten Umgebung mit `requirements-modeling.txt` als Constraints. Nicht unkontrolliert die Modellbibliotheken aktualisieren. Die konkrete UI-Version und ein erfolgreicher App-Start sind noch nicht nachgewiesen.

Geplanter lokaler Start ab AP 7.2: vom Projektwurzelverzeichnis mit `PYTHONPATH=src streamlit run app.py`. Git-Historie und Basisobjekte müssen vorhanden bleiben. Keine Laufzeitabhängigkeit von GitHub, CDN-Schriften oder externen Bildern für die lokale Präsentation.

## 4. Technische Architektur

```text
app.py: Kopfbereich, Modus, globale Nutzer-ID, Session State
  ├─ dashboard/user_view.py
  └─ dashboard/analytics_lab.py (sieben fachliche Bereiche)
         ↓
  dashboard/services.py: gemeinsame Orchestrierung und Statusübersetzung
    ├─ recommendation_engine.run(..., root=PROJECT_ROOT)
    ├─ dashboard/data_access.py: geprüfte CSV-/JSON-Ansichten
    ├─ bestehende transform_saved-Funktion (nur Transformation)
    └─ recommendation_comparison.compare: optionaler erklärter Replay
         ↓
  unveränderte data/, outputs/, documentation/ und lokaler Git-Bestand
```

Geplante Module, keine in AP 7.1 angelegten App-Dateien. Service und Datenzugriff enthalten ausschließlich Integration, Tabellen-Joins, Präsentationsaggregate und Fehlerbehandlung. Kein K-Means-Fit, kein Scaler-Fit, keine zweite Regression, kein Nachbau von Angebotssortierung oder Matching.

User-View-Empfehlungen und Demo-Prognose kommen immer aus `recommendation_engine.run`. Diesen Einstieg zunächst bevorzugen: Er prüft die Freigaben und lädt Aktivitätsquellen nur bei Garmin-Freigabe. Ein unkontrolliert vorgeladenes `ProjectData` mit vollständiger Historie ist kein geeigneter Ersatz. Ein späterer optimierter Weg über `load_data`/`recommend_user` muss dieselbe Ladegrenze erhalten.

Für persönliche Wochencharts fehlen der Engine-Ausgabe einzelne Wochen und Minuten. Ein gemeinsamer Adapter liest die vorhandenen Wochen-/Aktivitätsdateien erst nach expliziter Garmin-Freigabe und positivem Verifikationsstatus; keine Änderung des Engine-Vertrags nötig. User View zeigt Interessen ausschließlich aus dem freigegebenen Engine-Ergebnis. Nutzerkennungen dürfen immer für die Auswahl geladen werden.

Lab-Analysen lesen vorhandene Forschungsartefakte. Gespeicherte Regressionstestergebnisse werden untersucht statt bei jedem Filter neu inferiert. Eine eingeblendete Gleichungszerlegung erklärt nur die gespeicherte Ausgabe; ihr Ergebnis ersetzt nie die Engine oder die gespeicherte Prognose.

Session State: `mode`, `selected_user_id`, `lab_section`, `lab_step`, `lab_filters`, `interests_permission`, `garmin_permission`. Nutzer-ID bleibt beim Moduswechsel erhalten. Nutzerwechsel setzt beide simulierten Freigaben auf False zurück und entfernt alte persönliche Resultate. Entzug einer Freigabe entfernt betroffene Ausgaben sofort vor der nächsten Darstellung. Nur sichtbaren Bereich rendern und berechnen.

Zunächst keine global gecachten persönlichen Engine-Antworten. Unpersönliche Forschungstabellen dürfen über `st.cache_data` mit Projektwurzel und Quellfingerprint geladen werden; Daten als Kopien behandeln. Ein späterer persönlicher Cache müsste mindestens Nutzer, beide Freigaben, Stichtag und Quellenstand im Schlüssel enthalten. Kein Caching darf Lade-/Freigabeprüfungen umgehen. Abgefangene Ausnahmen ergeben verständliche Statusfelder; keine alte Antwort eines anderen Nutzers stehen lassen.

## 5. Wiederverwendete Python-Module

| Bestehendes Modul | Verwendung und Grenze |
| --- | --- |
| `src/recommendation_engine.py` | `run`, `recommend_user`, geprüfte Kategorien/Sportanteile, gespeichertes Segment, Prognose und unveränderte Top-5; zentrale Fachschnittstelle |
| `src/recommendation_comparison.py` | `compare(data)` liefert Nutzer-/Angebotstabellen und Summary mit drei vollständigen Beispielen über dieselbe Engine; optionaler Replay im Speicher ohne `main`/Dateiexport und ohne Modellinferenz |
| `src/data_preparation_scaling.py` | `transform_saved(rows, params)` für tatsächliche gewichtete Werte ohne Fit; ungewichtetes z nur als erklärter Zwischenwert |
| `src/data_preparation_selection.py`, `*_weekly.py`, `*_kmeans.py`, `*_regression.py`, `*_split.py` | Quellen der vorhandenen Pipeline und ihrer Regeln; nur geeignete reine Hilfsfunktionen nach Prüfung, keine Export-`main`-Aufrufe durch UI |
| `src/data_preparation_audit.py` | Vorhandener Auditbericht und ggf. reine Kontrollen; keine erneuten Exporte beim Navigieren |
| `src/modeling_kmeans_inference.py` | Bestehender Transformations-/Inferenzvertrag als Referenz; für bekannte Nutzer reicht die gespeicherte Zuordnung, keine neue Clusterzuordnung nötig |
| `src/modeling_regression_evaluate.py`, `*_baseline.py`, `*_evaluation_summary.py` | Referenz der Fehler-/Baseline-Definitionen; gespeicherte Tabellen verwenden, keine Trainings- oder Exportprogramme aufrufen |

Trainingsmodule bleiben außerhalb der Laufzeitpfade. Die vorhandenen `main`-Funktionen können Dateien schreiben oder Modelle fitten und sind keine UI-Callbacks.

## 6. Verfügbare Datenquellen und gesicherte Ergebnisse

Alle Pfade relativ zur Projektwurzel; aktive Quelle V2 vom 05.01.–05.07.2026.

| Quelle | Tatsächlich verfügbar | Nutzbarkeit |
| --- | --- | --- |
| `data/raw/users_simulated.csv` | 100 IDs, vier Interessenbooleans | Auswahl und positive Kategorien; keine Namen, Alter, Geschlecht, Bilder oder Gesundheitsdaten |
| `data/raw/activities_simulated.csv` | 6.465 Zeilen, ID, Nutzer, Datum, Sport, Minuten, Distanz | Acht Sportarten, Verteilungen und gefilterte Zeitreihen; 1.698 strukturell nicht anwendbare Distanzen, keine Nullimputation |
| `data/raw/offers_simulated.csv` | 30 fiktive Angebote, Titel/Kategorie/Preis/Rabatt | Katalogdarstellung; keine Produktfotos, Buchungen oder Relevanzlabels |
| `data/processed/activities_selected.csv` | 6.465 Zeilen × 5 Spalten | Auswahl ohne Distanz; keine Aktivität entfernt oder erfunden |
| `data/processed/user_weekly_activities.csv` | 2.600 Zeilen × 6 Spalten, 100 × 26 | Counts, Minuten, 558 Nullwochen; relative Projektwoche, keine ISO-KW |
| `data/processed/kmeans_user_features.csv` | 100 × 12 Spalten einschließlich ID | Häufigkeit + acht Anteile als Modelleingänge; Minuten und Vielfalt nur Interpretation |
| `data/processed/kmeans_user_features_scaled.csv` | 100 × 10 einschließlich ID | Neun standardisierte/gewichtete Eingänge |
| `outputs/models/kmeans_scaling_params.json` | Reihenfolge, Mittelwerte, Populationsskalen, Gewichte | Transformation und Zwischenwerte ohne Refit |
| `data/processed/user_clusters.csv` | 100 gespeicherte Zuordnungen | Final k=2, 57/43 Nutzer; relative Trainingshäufigkeit |
| `outputs/models/kmeans_final.joblib`, `kmeans_final_metadata.json` | Finalmodell, Zentren, Parameter, Hashes | Tatsächlicher Modellkontext; keine Modelle für andere k gespeichert |
| `outputs/tables/kmeans_k_selection.csv` | k=1…8; Silhouette für k≥2, Inertia, Min-/Maxgröße | Auswahl k=2,3,6,8 mit gespeicherten Werten |
| `outputs/tables/kmeans_candidate_comparison.csv`, `kmeans_stability_results.csv` | Zusammenfassung und einzelne Stabilitätsläufe | 20 Seeds je Kandidat, ARI/Silhouette; keine Zuordnungsmatrizen daraus ableiten |
| `outputs/tables/kmeans_candidate_profiles.csv` | Nur fünf Profilzeilen: zwei für k=2, drei für k=3, Seed 42 | Profile k=2/3 verfügbar; k=6/8 ausdrücklich nicht verfügbar |
| `outputs/tables/kmeans_final_cluster_profiles.csv` | Zwei finale Profile | Häufigkeitsmittel 1,5351 und 3,7478; Sportmix und Interpretationsmerkmale |
| `data/processed/regression_weekly_features.csv` | 2.200 Zeilen × 7 Spalten | Eingabewochen 4…25 mit beobachteter Folgewoche |
| `data/processed/regression_train.csv`, `regression_test.csv` | 1.800 / 400 Zeilen | Chronologischer Split, 18 / 4 pro Nutzer |
| `documentation/regression_split_manifest.json` | Exakte Grenzen und Hashes | Eingabewochen Training 4…21, Test 22…25; Zielwochen 5…22 / 23…26 |
| `outputs/models/regression_linear.joblib`, `regression_linear_metadata.json` | Zwei Koeffizienten, Intercept, Feature-Reihenfolge, Modellhash | Unveränderte Einwocheninferenz ohne Skalierung |
| `outputs/tables/regression_test_predictions.csv` | 400 tatsächliche Testfälle mit X, Ist, Prognose, Fehler | Nutzer-/Wocheninspektor und Rechenweg |
| `outputs/tables/regression_baseline_comparison.csv` | 400 Fälle einschließlich Baseline und beider absoluter Fehler | Exakt verbundener Vergleich über Nutzer + Eingabewoche |
| `outputs/tables/regression_test_metrics.json`, `regression_test_metrics_by_week.csv`, `regression_baseline_metrics.json`, `modeling_evaluation_summary.json` | Gesamt-, Wochen- und Nullwochenmetriken | MAE Regression 1,489877; Baseline 1,71; relative Verbesserung 12,872687 % |
| `documentation/offer_sport_tags_approved.csv` | Acht bestätigte Zuordnungen | O001, O003–O007, O009/O010; 22 Angebote ohne Tag bleiben kategoriezulässig |
| `outputs/tables/recommendation_before_after_{users,offers}.csv`, `recommendation_before_after_summary.json` | 100 Nutzer-, 30 Angebotszeilen, Summary mit Quellhashes | 64 Zusammensetzungsänderungen, 36 unverändert, keine reine Umordnung; 475 Slots je Variante, A nachher 344 |
| `outputs/tables/data_preparation_audit_report.md`, `outputs/figures/` | Tatsächlicher Audit und AP-4-/AP-5-/AP-6-Diagramme | Nachweis/Reservefolie; interaktive Charts aus zugehörigen Daten neu rendern, keine Werte aus PNG schätzen |
| `outputs/simulation_comparison/` und `documentation/crisp_dm_log.md` | V1-Snapshot, Vergleichstabellen, gepaarte Nutzeränderungen, Iteration MOVA-ITER-001 | Belegter Versions-/Kontrollvergleich, ohne erneute Simulation |

## 7. Konkretes Navigationskonzept

Kopf: MOVA / Move beyond · `[USER VIEW | ANALYTICS LAB]` · `Synthetische V2-Demo` · Nutzerwahl U001…U100. User-View-Freigaben in einer klar beschrifteten Simulationsleiste; Demo-Stichtag 05.07.2026 dauerhaft sichtbar.

User View: eine übersichtliche Seite mit Aktivität → Segment/Prognose → Angebote; technische Details in ausklappbaren Quellenhinweisen.

Analytics Lab: linke Navigation mit B1 Daten, B2 Aufbereitung, B3 K-Means, B4 Regression, B5 Evaluation, B6 Empfehlungen, B7 CRISP-DM. Jede Seite: Leitfrage, zentrale Interaktion, Diagramm, Erklärung zur Auswahl und aufklappbarer Daten-/Berechnungsnachweis. Keine sieben gleichzeitig gerenderten schweren Tabs. B2 hat zusätzlich Zurück/Weiter und direkt anwählbare Verarbeitungsschritte. Filter gelten lokal, solange nicht explizit Nutzer-ID global ist.

Präsentationsroute: B1 Bestand → B2 Nullwochen/Skalierung/Split → B3 Modellwahl → B4 einzelner Rechenfall → B5 Grenzen → B6 Regelwirkung → User View. B7 verbindet fachliche Entscheidungen mit Nachweisen.

## 8. User-View-Funktionen

- Profil: „Simulierter Nutzer U001“, ausschließlich tatsächlich freigegebene positive Interessen. Initialen-/ID-Symbol statt erfundener Personendaten.
- KPI-Karten: Aktivitäten gesamt, Aktivitäten je Woche, Trainingsminuten und abgedeckter Zeitraum; alle aus demselben gefilterten vollständigen Wochenraster. Wochenbereich als vollständige Montag–Sonntag-Intervalle, damit Nenner eindeutig bleiben.
- Entwicklung: Wochenlinie oder Balken für Counts/Minuten; Umschaltung ändert Einheit und Achsenbeschriftung. Nullwochen sichtbar belassen.
- Sportmix: tatsächliche Counts/Anteile über alle 26 Wochen. Optionaler Wochenfilter deskriptiv aus Einzelaktivitäten; als ausgewählter Ausschnitt beschriften. Das feste Engine-Profil und Segment werden dabei nicht neu berechnet oder umgedeutet.
- Segment: gespeicherter Labeltext; „beschreibt deine relative Trainingshäufigkeit in dieser synthetischen Gruppe“. Keine Fitness-, Gesundheits- oder Erfahrungsbewertung.
- Prognose: „Geschätzte Aktivitäten 06.–12.07.2026“, Stichtag 05.07.2026, Eingabefenster und Unsicherheit. Anzeige beispielsweise auf zwei Dezimalstellen gerundet, ungerundeter Originalwert in Details; keine Kappung oder Ganzzahl-Rundung in der Berechnung. Kein Konfidenzband erfinden.
- Angebote: höchstens fünf Engine-Einträge in unveränderter Reihenfolge; fiktiver Titel, Kategorie, `price_eur`, `discount_pct`, Stufe A/B und `match_reason`. Preis und Rabatt getrennte Katalogangaben, kein behaupteter bereits rabattierter Endpreis. Keine zusätzliche Preis-/Rabatt-/Score-Sortierung, kein Kaufbutton mit echter Transaktion.
- Status statt Ersatzwerte: fehlende Prognose bleibt „nicht verfügbar“, nicht 0; leere Angebote erläutern ihren tatsächlichen Status. Bei fehlender Garmin-Freigabe erscheinen keine persönlichen Charts, Anteile, Cluster oder Prognosen.

## 9. Analytics-Lab-Funktionen

**B1 Data Understanding:** Datenumfang, Sport-/Dauerverteilungen, Verlauf und Feldlexikon. Sport-/Nutzer-/Zeitraumfilter zeigen reale Teilmengen und ihre Bezugsgrößen. Leere Filter sind zulässige Ergebnisse. Distanz bleibt sportabhängig; fehlende strukturelle Werte nicht als 0 km zählen.

**B2 Data Preparation:** Schrittweise Rohdaten → Prüfung/Auswahl → vollständiges Wochenraster → Nutzerfeatures → Skalierung; zweiter, expliziter Pfad Wochenraster → Regressionsfeatures → chronologischer Split. Skalierte K-Means-Daten sind keine Regressionsinputs. Bei jedem Schritt Eingabe, Verarbeitung, Ausgabe, Zeileneinheit, Schema und fachlicher Grund. Die „Bereinigung“ bestand hier aus Validierung und Feldauswahl: keine erfundenen entfernten Duplikate/Ausreißer. Distanz entfällt aus X, weil nicht benötigt und sportübergreifend begrenzt vergleichbar.

Nullwochen sind die wichtigste Interaktion: vollständiges Raster gegen bedingten Mittelwert aktiver Wochen mit expliziten Nennern. Danach Nutzer-/Featurewahl für tatsächliche Standardisierung und Gewichtung sowie Zeitfensterinspektor für vier vergangene Wochen und Zielwoche.

**B3 K-Means:** Auswahl k=2,3,6,8 lädt gespeicherte Kennzahlen; kein Fit beim Umschalten. Seed-42-Silhouetten 0,303337 / 0,184642 / 0,194309 / 0,206130. Getrennte Darstellung der 20-Seed-Mittelwerte 0,303337 / 0,180135 / 0,184549 / 0,199977. Keine Vermischung von Einzellauf und Seedmittel. Final k=2: Größen 57/43, echte Profile, Segmentcharakteristik und Gewichtungsannahme. Bei k=3 Kandidatenprofile explizit vorläufig. Bei k=6/8 nur vorhandene Evaluationswerte, keine erfundenen Profile, Clusterpunkte oder Nutzerlabels. k=1 hat keine Silhouette.

**B4 Regression:** gespeicherter Testfall wird per Nutzer und Zielwoche 23…26 gewählt. Eingabe-X, vier historische Counts, Modellbeiträge, gespeicherte Prognose, Ist, Baseline und Fehler erscheinen schrittweise. Interaktive Zeitachse trennt t−3…t von t+1. Die tatsächliche Gleichung lautet:

`ŷ(t+1) = 0.8397931020190079 + 0.22819007785063997 × activities_current_week + 0.42396047869339204 × avg_activities_last_4_weeks`.

Die aktuelle Woche ist im Vierwochenmittel enthalten. Baseline = aktuelle Wochenaktivitätszahl. Fehler = Prognose − Ist, absoluter Fehler = Betrag. Metadaten liefern die Konstanten; keine hartcodierte produktive Ersatzregression. Beispiel U001, Eingabewoche 22: X=(1; 2,25), gespeicherte Prognose 2,0218942569297802, Ist 2, Baseline 1. Join über Nutzer und Eingabewoche; Zielwoche = Eingabewoche + 1. Demo-Prognose Woche 27 strikt vom historischen Test unterscheiden; kein Istwert für 06.–12.07.2026 vorhanden.

**B5 Evaluation:** Gesamtübersicht und auswählbare Zielwochen bzw. Gruppen Ist=0/Ist>0. MAE = Mittel der absoluten Fehler, Verbesserung = `(MAE_Baseline − MAE_Regression) / MAE_Baseline × 100`. Bei Nenner 0 nicht definiert statt erfundener Prozentzahl. Gefilterte Werte sind neue deskriptive Ansichten derselben gespeicherten Testfälle und ersetzen nicht die Gesamtmetrik. N immer anzeigen. Von 400 Fällen sind 92 Nullzielwochen: dort Regression-MAE 1,878292, Baseline 1,380435, relative Veränderung −36,0653 %; bei 308 positiven Zielwochen Regression 1,373857 gegen Baseline 1,808442. So bleibt sichtbar, dass bessere Gesamt-MAE nicht jede Untergruppe oder jeden Nutzer betrifft. Keine neue Modellauswahl nach Testfiltern.

**B6 Empfehlungssystem:** gespeicherter kontrollierter Vergleich ohne/mit acht bestätigten Tags. Nebeneinander Top-5, Ein-/Austritte und Positionsänderungen; Fallauswahl U001, U002, U003 demonstriert verschiedene Ursachen. Die CSV enthält geordnete IDs, aber nicht jede vollständige Begründung/Stufe jeder Vorher-Liste. Primär gespeicherte IDs mit Katalogdaten verbinden; Vorher ist nach geprüftem Versuch vollständig B. `recommendation_comparison.compare(data)` liefert genau drei Rückgabewerte: Nutzerzeilen, Angebotszeilen, Summary. Die Summary enthält vollständige Vorher-/Nachher-Einträge für drei Beispiele, keine vollständigen Detailantworten für alle 100 Nutzer. Diese Beispiele können direkt verwendet werden. Für vollständige Details eines beliebigen ausgewählten Nutzers verwendet der gemeinsame Adapter denselben kontrollierten Ablauf wie `compare`: explizite True/True-Versuchsbedingungen, geprüfte Kategorien und Sportanteile, zwei Aufrufe der vorhandenen `engine.recommendations` mit identischen Eingaben und ausschließlich unterschiedlicher Tagmenge (leer/acht bestätigt). Keine neue Matchinglogik und keine ML-Inferenz. Den Replay mit gespeicherten IDs/Counts abgleichen und als Rekonstruktion kennzeichnen; keine Freigabedatei überschreiben. Dieser historische Versuchsweg ersetzt nicht den freigabeprüfenden `run`-Einstieg der persönlichen User View. Globale Bezugsgrößen: 64/100 veränderte Zusammensetzungen, 344/475 A-Slots nachher = 72,42 %, 81 Nutzer mit mindestens einem A-Angebot. Diese drei Größen nicht gleichsetzen. Keine beobachtete reine Umordnung vorhanden.

**B7 CRISP-DM:** sechs Phasen als klickbarer Verlauf mit vorhandenen Artefakten. Deployment bezeichnet hier geplante lokale Demonstration, kein bereits veröffentlichtes System. MOVA-ITER-001 zeigt die tatsächliche Rückkehr aus Data Understanding zur Konstruktion der Simulation: Auffälligkeit breiter Repertoires → Exponent 1,3 → erneute Qualitätsprüfung. V1, technische Kontrolle Exponent 1,0 mit getrennten Zufallsströmen und V2 sauber auseinanderhalten: 6.665 V1-Aktivitäten gegen 6.465 in Kontrolle/V2; die Countdifferenz ist kein nachgewiesener Exponenteneffekt. Gepaarter Kontrolle→V2-Vergleich zeigt Top-2-Anteil +6,507 Prozentpunkte und Nutzer mit acht Sportarten 58→40. Git-Proxy, technische Fehlerbehebung und reine Validierungswiederholungen sind keine fachlichen Iterationen.

## 10. Konkrete Interaktionen und Erkenntnisse

| Interaktion | Verwendete Daten | Tatsächliche Berechnung / Darstellung | Fachliche Erkenntnis |
| --- | --- | --- | --- |
| U: Nutzer + simulierte Freigaben | Nutzer-IDs, `run`-Antwort | Engine mit expliziten bools und festem Cutoff; Ausgaben nach Status | Interessen und Aktivitätskontext sind unabhängige Wege |
| U: vollständige Wochen auswählen, Count/Minuten wechseln | Wochenraster; freigegeben/verifiziert | Summe Counts/Minuten, Countsumme geteilt durch Zahl ausgewählter Wochen | Umfang und Häufigkeit sind verschiedene Größen; Pausen zählen mit |
| B1: Sport/Nutzer/Zeitraum filtern | Roh-/ausgewählte Aktivitäten, Feldlexikon | Filter, Count, Histogramm; Anteil mit ausgewiesenem Nenner | Population und Ausschnitt bestimmen die Aussage |
| B2: Pipeline-Schritt wählen | Vorhandene CSVs, Audit, Skriptregeln | Je Stufe echte Tabellenproben, Spalten und Zeilenzahlen | Feature Engineering verändert die Analyseeinheit |
| B2: mit/ohne Nullwochen, optional Nutzerwahl | Vollständige Nutzerwochen | Summe/n aller Wochen versus Summe/n positiver Wochen, relative Differenz | Weglassen verändert Nenner und Fragestellung |
| B2: Nutzer und Feature auswählen | Unskalierte/scalierte Features, Skalierungs-JSON | x, gespeichertes μ/σ/Gewicht, z=(x−μ)/σ, vorhandenes `transform_saved` | Standardisierung und Gewichtung sind unterschiedliche Schritte |
| B2: Eingabewoche anwählen | Wochenraster, Regressionsfeatures, Splitmanifest | t−3…t, Mittel, t+1 und Ausschluss früher/letzter Eingaben | Keine Zukunftsinformation in X; zeitlicher Split |
| B3: k auswählen | k-Auswahl/Stabilität/Kandidatenprofile | Vorhandene Silhouette/Inertia/ARI; Profile nur wo gespeichert | Höheres k ist nicht automatisch besser; Datenlücken sichtbar |
| B3: finales Cluster/Profilmerkmal wählen | Finale Profile, Zuordnungen | Gruppengröße und unskalierte Mittel, ggf. reale Featurepunkte aus Join | Segment beschreibt beobachtete Häufigkeit, keine Fitness |
| B4: Nutzer/Testzielwoche + Rechenschritt | Testprognosen, Baseline, Wochenquelle, Modellmetadaten | Historie → X → Beiträge → gespeicherte Prognose → Ist/Fehler | Globale Gleichung liefert individuelle, fehlerbehaftete Schätzungen |
| B5: Zielwoche und Nullzielgruppe wählen | 400 Baseline-Vergleichsfälle | MAE beider Methoden, N, relative Differenz | Gesamtvorteil kann sich für Nullwochen umkehren |
| B6: Nutzer/Beispiel auswählen | AP-6-CSVs/JSON, Katalog, optional `compare` | Identische IDs markieren, Eintritt/Austritt und Position vergleichen | Regelwirkung und Rangstufe sind kein Gütenachweis |
| B7: Phase/Variante/Nutzer auswählen | CRISP-Log, Vergleichs-/gepaarte Tabellen | Dokumentierte Metriken/Quellen einblenden, gepaarte Differenzen | Fachliche Hypothese braucht kontrollierten Vergleich |

## 11. Erforderliche Daten und Umsetzungsgrenzen je Interaktion

U- und B-Interaktionen aus Abschnitt 10 benötigen keine neuen Rohdaten. CSV-Listenfelder im AP-6-Vergleich müssen als JSON dekodiert werden, nicht mit Stringsplit an Kommas. Schlüssel und Beziehungen vor Joins auf Eindeutigkeit prüfen; keine stillen many-to-many-Vervielfachungen.

Für B2 müssen die historischen Ausgabestufen gelesen und erläutert werden. Eine tatsächlich gespeicherte „bereinigte Fehlerliste“ existiert nicht, weil keine Zeilen entfernt wurden; stattdessen geprüfte Regeln und unveränderte 6.465 Zeilen zeigen. Der direkte Nullwochenvergleich ist aus der Wochenquelle vollständig berechenbar. Nutzer ohne positive Wochen in einem Filter ergeben „nicht definiert“ für den bedingten Mittelwert.

Für B3 fehlen k=6/8-Profile, alternative gespeicherte Modelle und Nutzerzuordnungen. Das Konzept benötigt sie nicht: Auswahl bietet dort nur Kennzahlen und Stabilitätsnachweise. Für k=3 sind aggregierte Profile vorhanden, aber keine vollständige gespeicherte Nutzerlabeltabelle. Nutzerpunkte dürfen daher nur mit finalen k=2-Labels eingefärbt werden. Keine neue Anpassung zur Schließung dieser Lücken.

Für B4 fehlen beobachtete Zielwerte nach Woche 26 und gespeicherte individuelle Unsicherheitsintervalle. Es gibt keine prospektiv gemessene Güte der Woche-27-Demo. Die vorhandene Gesamt-MAE ist eine vergangene Testkennzahl, kein garantierter Fehlerbereich für die nächste Woche.

Für B6 fehlen Klicks, Käufe, Ratings und Kontrollgruppen realer Nutzer. Qualitäts-/Umsatzsteigerung ist nicht berechenbar. Vollständige Detailbegründungen sind über den bestehenden Vergleich im Speicher rekonstruierbar; die gespeicherten Vergleichs-CSVs werden dabei nicht ersetzt. Die drei gespeicherten Summary-Beispiele reichen für die unverzichtbare didaktische Detaildemonstration.

Für B7 vorhandene Vergleichstabellen und V1-Snapshot nutzen. Historische Verweise auf Kontroll-/V2-Unterordner bedeuten nicht, dass alle damaligen Zwischen-CSVs versioniert sind. Die benötigten aggregierten und gepaarten Vergleiche liegen vor; fehlende Kontroll-Rohdaten nicht neu erzeugen.

`E3_WebApp_Klassifikation.html` wurde unter `/workspace` gesucht und nicht gefunden; im versionierten Projektbaum ebenfalls nicht vorhanden. Sie wurde nicht gelesen. Übernommen werden ausschließlich die im Auftrag beschriebenen Interaktionsprinzipien: klare Regler, Beispiele, Schritte, Zwischenwerte und dynamische Diagramme.

## 12. Designsystem

Gemeinsame dunkle MOVA-Plattform mit ruhigem Grün statt vollflächiger Neonoptik. Vorgeschlagene Tokens: Hintergrund `#0B1110`, Oberfläche `#14201C`, angehobene Karten `#1A2B24`, primärer Text `#F2F7F4`, sekundär `#B4C6BC`, Akzent `#7DE2A6`, Rahmen `#30483B`. Akzent für Auswahl und Handlung; Vergleichsreihen zusätzlich Blau `#76B7E5` und Orange `#F1B675`. Exakte Kontraste in AP 7.5 prüfen.

Typografie: lokale Systemschrift, 16–18 px Fließtext, große KPI-Zahlen, klare Überschriften; auf Projektor mindestens gut lesbare Achsen und Tooltips. 8-px-Abstandsraster, 16–24 px Karteninnenabstand, dezente 12–16 px Rundung. Schrift-/Farb-/Abstandstokens zentral; zunächst native Komponenten und öffentliche Theme-/Layoutoptionen. Kein fragiles CSS über interne Streamlit-DOM-Klassen.

User View emotionaler durch großzügigen Einstieg, sportliche Symbole und Aktivitätskarten, horizontale Angebotskarten bzw. 2-Spalten-Raster. Keine erfundenen Produktbilder oder simulierten Fotos realer Personen nötig. Analytics Lab ruhiger mit klarer Leitfrage, höchstens einem dominanten Chart je Arbeitsfläche, Rechenwerten und verknüpfter Tabelle.

Desktop-Skizze:

```text
MOVA · Move beyond        USER VIEW | ANALYTICS LAB        Nutzer U001
SYNTHETISCHE DEMO · Daten bis 05.07.2026
User: [simulierte Garmin-Freigabe] [simulierte Interessenfreigabe]
[Aktivitäten] [Aktivitäten/Woche] [Trainingsminuten] [Zeitraum]
[       Aktivitätsentwicklung        ] [     Sportmix      ]
[Gespeichertes Segment] [Schätzung 06.–12.07.2026 + Hinweis]
[Angebot 1 · A · Preis/Rabatt · Begründung] [Angebot 2 ...]

Lab: [B1 … B7] | Leitfrage und Auswahl
               | [Interaktiver Chart] [Zwischenwerte / Erklärung]
               | [Daten / Berechnung / Quelle aufklappen]
```

Kleine Fenster stapeln Spalten; Modus und Nutzerwahl bleiben auffindbar. Farbe nie alleinige Information: A/B, Ein-/Austritt und Status erhalten Text/Symbole. Tastaturbedienbare native Widgets, verständliche Leer-/Fehlerzustände, sinnvolle Legenden und deutsche Zahlen-/Datumsformatierung. Grafiken erhalten explizite Einheiten, Beobachtungszeitraum und N. Animationen und große Hero-Bilder optional, nicht Voraussetzung der Demo.

## 13. Simulierte Freigaben

| Interessen | Garmin | Tatsächliches Engine-Verhalten und UI |
| --- | --- | --- |
| False | False | Keine Interessen-/Empfehlungs-/persönliche Aktivitätsausgabe |
| True | False | Positive Kategorien und Kategorieangebote, ausschließlich B; keine persönlichen Aktivitäten, Anteile, Cluster, Prognose |
| False | True | Unabhängiger verfügbarer Aktivitäts-/Modellkontext; keine Kategorien oder Empfehlungen |
| True | True | Kategorienangebote, optional A mit bestätigtem Tag und positivem Sportanteil; unabhängig verfügbarer Modellkontext |

Initial beide False. Nutzerwechsel setzt zurück; Moduswechsel behält Werte für denselben Nutzer, setzt sie aber niemals automatisch auf True. Schalter heißen ausdrücklich „Simulierte …-Freigabe“. Kein Garmin-OAuth, keine reale Einwilligung, keine echte Datenübertragung. `permissions_simulated`, `simulated=true`, `real_consent_record=false` bleiben die Referenz. Die Engine ist keine Benutzer-Authentifizierung; diese ist für die lokale synthetische Einzelplatzdemo nicht neu zu bauen.

## 14. Wissenschaftliche Transparenz

- Datenquelle und synthetischer Charakter auf beiden Ansichten sichtbar. Simulation ist keine empirische Garmin-Population.
- Gespeicherte Ergebnisse, aktuelle Engine-Inferenz und rein deskriptive Filteraggregate visuell benennen; keine scheinbare Echtzeitmodellierung.
- K-Means: neun Modellfeatures, acht Anteile nur sieben unabhängige Freiheitsgrade. Standardisierung mit Populationsvarianz ddof=0; Frequenzgewicht 1, Sportkoordinaten je 1/√8. So sind Varianzsummen der beiden Blöcke ungefähr gleich, nicht empirisch optimal. Minuten und Vielfalt sind Interpretationsmerkmale, keine X-Spalten.
- Keine Gewichtungsregler, die neue Cluster ohne Fit suggerieren. Zwischenwerte dürfen erklärt, finale Modell-/Rankingresultate nicht dadurch verändert werden.
- Regressionsmodell global über bekannte Nutzer; chronologischer Test ist kein Test an neuen Personen. Wiederholte Nutzer und überlappende Fenster begrenzen Unabhängigkeitsannahmen.
- Rollierende Einwochenprognosen: frühere Testbeobachtungen dürfen bei späteren Prognosen Historie sein, das Modell bleibt unverändert. Keine gleichzeitige Vierwochenprognose behaupten. Trainingsziele reichen bis 07.06.2026; die Engine sperrt frühere Modellverwendung.
- Regression-Metadaten enthalten historisch `test_evaluation_performed=false`; das ist der Trainingsstand. Die spätere tatsächliche Evaluation ist durch die separaten Testartefakte belegt. Historische „uncommitted“-Felder in AP-4-Metadaten sind ebenso keine aktuelle Git-Zustandsaussage.
- Rangstufen sind Regeln, keine Wahrscheinlichkeiten. Cluster und Regression beeinflussen das Ranking nicht. 64 % geänderte Listen messen Regelwirkung, keine belegte Verbesserung.
- CRISP-DM-Iteration nur mit Anlass, Änderung, erneuter Prüfung und Quellen. Geplantes Deployment nicht als abgeschlossen kennzeichnen.

## 15. Priorisierung

| Stufe | Umfang |
| --- | --- |
| Unverzichtbar | Gemeinsame Python-Logik, Moduswechsel/Nutzererhalt, korrektes Freigabeverhalten, echte User-View-KPIs/Segment/Prognose/Top-5; B1 Filter; B2 Pipeline, Nullwochen, Skalierung und Zeitfenster/Split; B3 gespeicherter k-Vergleich/finale Profile; B4 realer Testfall; B5 Baseline und Nullzielgruppen; B6 gespeicherter Vergleich; B7 belegte Iteration; Fehler-/Quellenhinweise |
| Sinnvolle Ergänzungen | Seed-/ARI-Detailvergleich, zweidimensionale finale Featurepunkte, zusätzliche Rohdatenverteilungen, individuelle Vorher-Nachher-Detailbegründungen per Engine-Replay, CSV-Download vorhandener gefilterter Tabellen |
| Optionale Designverbesserungen | Zusätzliche Illustrationen, sanfte Übergänge, feinere Karten-/Tooltipgestaltung, weitere responsive Optimierung nach Kernabnahme |

Zuerst wissenschaftliche Korrektheit und die belastbaren Interaktionen fertigstellen; gestalterische Zusätze dürfen den lokalen Demoablauf nicht destabilisieren.

## 16. Umsetzungsschritte und Abnahme

**AP 7.2 – gemeinsame Grundlage:** isolierte Umgebung und fixierte UI-Abhängigkeiten, App-Shell, dunkles Theme, globale Nutzerwahl, Moduswechsel/Session State, gemeinsamer Service/Datenzugriff und Fehleradapter. Read-only-Quellinventar und Startprüfung. Abnahme: lokaler Start, Nutzererhalt, False/False-Initialisierung, Reset bei Nutzerwechsel, keine alten Daten nach Fehler/Freigabeentzug; Modellbibliotheken unverändert. Noch keine Vollimplementierung aller Lab-Seiten erforderlich.

**AP 7.3 – vollständige User View:** vorhandene Engine direkt anschließen, gated Wochen-/Sportcharts ergänzen, gespeichertes Segment, Woche-27-Prognose, Karten mit echten Katalogwerten/Begründungen. Abnahme U001/U002/U003, alle vier Freigabekombinationen, Nutzer ohne positive Kategorien und fehlender Modellkontext. Empfehlungen müssen mit Engine-Ausgabe einschließlich Reihenfolge und Anzahl übereinstimmen.

**AP 7.4 – Analytics Lab:** zuerst B2 → B3 → B4 → B5; anschließend kompakte B1/B6/B7. Reine Datenfilter und vorhandene Ergebnistabellen nutzen, keine Trainingsskripte starten. Abnahme jeder Interaktion anhand der Zuordnung in Abschnitt 10, Referenzwerte für Nullwochen, k-Scores, globale/Teilgruppen-MAE und AP-6-Zahlen. Filter ändern niemals die gespeicherten Modelle oder Originalergebnisse.

**AP 7.5 – Gesamttests, Präsentation und Sicherung:** Integrationsprüfungen für Modus-/Nutzer-/Freigabewechsel, Status-/Fehlerfälle, Zeitraum-/Join-/Nennerkorrektheit und ausbleibendes Fit/Dateischreiben. Vorher-/Nachherhashes für Rohdaten, Modelle, Tags und Rankingmodule. Visuelle Prüfung in Desktop-/Projektorgröße und kleinem Fenster, Offline-Demodurchlauf, README mit reproduzierbarem Start. UI-Versionen und Einschränkungen dokumentieren. Erst in diesem separat beauftragten Schritt GitHub-Sicherung vorbereiten; AP 7.1 erstellt keinen Commit/PR.

Aufwandseinschätzung für ein kleines Hochschulprojekt: AP 7.2 etwa 0,5–1, AP 7.3 etwa 1–2, AP 7.4 etwa 2–3, AP 7.5 etwa 1 Arbeitstage; Planungswerte, keine gemessene Zusage. B2 und Sitzungs-/Freigabekorrektheit haben Vorrang vor optionaler Optik. Bestehende Tests gezielt übernehmen; komplette Modelltestläufe nur nach Prüfung, ob sie Fit auslösen.

## 17. Technische Risiken, offene Fragen und Startfähigkeit

| Befund | Konsequenz / geplante Behandlung |
| --- | --- |
| Loader prüft manche Aktivitätsquellen via `git show a8f97ad…:pfad`; Skalierungs-JSON bietet dafür nicht überall den erwarteten `source_sha256`-Schlüssel | Lokaler Worktree mit vollständigem Git-Bestand nötig. Nicht nur App-/CSV-Dateien kopieren; Packagingproblem bleibt bewusst offen |
| Git-Proxyproblem bekannt | Lokale Demo ohne Remote-Zugriff; spätere GitHub-Sicherung über Integration bei Bedarf. Keine unbestätigte Remote-Basis verwenden |
| Streamlit/Plotly noch nicht installiert und UI-Versionen unfixiert | AP 7.2 muss Installation, Versionsbindung, Start und Session-Verhalten belegen; heute keine getestete UI behaupten |
| Streamlit-Reruns und optionale Caches | Nur aktive Seite rendern, Session-State-Keys stabil halten, Freigaben nicht aus Datensätzen ableiten, Resultate nach Entzug löschen |
| Infrastrukturfehler nicht vollständig in Engine abgefangen | UI-Adapter fängt gezielt Daten-/Systemfehler ab und zeigt keinen alten Nutzerkontext |
| Kein generischer Export-/Deploymentvertrag | Projektwurzel explizit übergeben, Git-Objekte erhalten; keine Cloud-/Garmin-Infrastruktur für diese Phase |
| k=6/8 ohne Profile/Labels, k=3 ohne Nutzerlabels | Nur gespeicherte Kennzahlen/Kandidatenaggregate zeigen; kein Nachtraining und keine scheinbaren Punktzuordnungen |
| Kein Istwert der Demo-Zielwoche und keine individuellen Intervalle | Klare historische Datumsanzeige und Unsicherheit, keine Zukunftsevaluation |
| CSVs enthalten JSON-Listen und verschieden benannte Wochen-Counts | Strikt parsen, Schema/Join-Schlüssel prüfen: `activities_count` im Raster versus `activity_count` in Kontrolltabelle |
| Einige Berichte dokumentieren historische Zwischenstände | Aktuelle Artefakte und spätere Fortschreibungen haben Vorrang; keine historischen Flags als aktuellen Stand übernehmen |

AP-7.1-Prüfung: 42 vorhandene Empfehlungstests werden ohne Training ausgeführt. Beim ersten Lauf fehlte im frischen Worktree das ignorierte Verzeichnis `work/`; ein Test mit `TemporaryDirectory(dir=ROOT/'work')` konnte deshalb nicht starten. Das Verzeichnis wurde angelegt und der Lauf wiederholt; kein Testcode oder Fachcode geändert. Endgültiges Ergebnis: **42 Tests bestanden** (25 Engine-, 11 Vergleichs-, 6 Dashboard-Vertragstests), 0 Fehler. Die Tests prüfen unter anderem unveränderte Basisdateien, Freigabegrenzen, Modellkontext ohne Fit und gespeicherte Vergleichsergebnisse.

**AP 7.2 kann beginnen.** Keine fachliche Datenlücke blockiert den beschriebenen Kernumfang. Die offenen UI-Installations-/Startprüfungen sind konkrete Arbeitspakete von AP 7.2. AP 7.1 endet mit diesem Konzept; die Webanwendung ist noch nicht implementiert.
