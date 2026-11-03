# MOVA – AP 8.1: Technische Ergebnisinventur und Abschlussprüfung

Prüfdatum: 03.11.2026 (Europe/Berlin). Gegenstand: unveränderte aktive synthetische V2 und gespeicherte Ergebnisse aus AP 1–7. Dieses Dokument liefert die Beleggrundlage für AP 8.2, noch keine wirtschaftliche Gesamtevaluation.

**Belegarten:** **Messung** bezeichnet aus vorhandenen Daten/Artefakten überprüfte Zahlen; **Implementierung** nachweisbares Programmverhalten; **Entscheidung** eine dokumentierte methodische Festlegung; **Grenze** eine Einschränkung; **offen** eine bislang nicht untersuchte Frage. Gemessene synthetische Ergebnisse sind keine Beobachtungen realer Nutzer.

## 1. Projektziele und erreichte Ergebnisse

### Git-Basis und Arbeitsbereich

Die GitHub-Integration bestätigte am Prüfdatum über den Branch-Endpunkt `repos/pati0303/MOVA-Big-Data-Analytics/branches/main` den tatsächlichen main-Commit **`4e5a538bde31b47a03eeb012745885e52b2cf97d`** (Tree `f8d583123785884a2bf680ede560f4f7fcdb6750`). [PR #7](https://github.com/pati0303/MOVA-Big-Data-Analytics/pull/7) ist geschlossen und `merged=true`, zusammengeführt am 01.11.2026 um 12:04:36 MEZ. Sein Merge-Commit entspricht diesem main. Eltern: `23ac008651de490d59e9ec5ceae590ba97daf0e5` und AP-7-Head `b0d9bcde9b57b891413b4fa5ac91e8527f6d1d87`. Der Feature-Commit ist somit nicht selbst der aktuelle main.

Lokal vorhandene vollständige Git-Historie verwendet; kein Git-Netzwerkabruf nötig. `git fsck --full` ohne Befund; AP-7-Head als Vorfahr der bestätigten Basis geprüft. Separater Worktree `/workspace/MOVA-AP8`, neuer lokaler Branch `ap8-evaluation`, HEAD auf bestätigtem main. Alle **200 bisherigen versionierten Dateien** vor dem Audit bytegenau mit HEAD verglichen. Kein Commit, Push oder PR für AP 8 erstellt.

### Business Understanding

**Ziel/Entscheidung:** MOVA („Move beyond“) ist eine geplante Personal-Advisor-Plattform, die Aktivitätsmuster verständlich macht und Angebote aus Sport, Outdoor, Wellness und Freizeit anhand freiwilliger Interessen und Sporthistorie auswählt. Problemannahme: Aus Aktivitätsdaten sollen verständliche Orientierung und passendere Angebotsvorauswahl entstehen. Zielgruppe laut `crisp_dm_log.md`: aktive Smartwatch-Nutzer mit unterschiedlichen Schwerpunkten. Die Geschäftsvision steht im `README.md`, die konkrete Demonstratorarchitektur in `dashboard_concept.md` und `recommendation_concept.md`.

**Hypothetischer Nutzen:** Nutzer könnten Angebote leichter finden und ihre Aktivität besser verstehen; eine gezieltere Vermittlung könnte für Angebotsanbieter wirtschaftlich relevant sein. Diese Wirkungskette ist eine Hypothese. Eine belastbar spezifizierte zusätzliche zahlende Kundenzielgruppe, ein validiertes Provisionsmodell oder ein Umsatznachweis ist in den geprüften Dokumenten nicht belegt. Keine Bewertung wirtschaftlichen Erfolgs.

**Implementiert und technisch überprüft:** synthetische Datenbasis, nachvollziehbare Aufbereitung, deskriptives K-Means, globale Einwochenregression, deterministische Empfehlungsengine und lokales interaktives Dashboard. **Gemessen:** Datenqualität/Konsistenz, interne Clusterkennzahlen, Fehler auf chronologischem synthetischem Testbestand und Veränderungen der Angebotslisten. **Nicht überprüft:** reale Akzeptanz, Relevanzurteile, Klicks, Buchungen, Provisionen, Umsatz oder kausaler Kundennutzen.

## 2. Datenbasis

**Messung:** 100 synthetische Nutzer, 26 vollständige Montag–Sonntag-Wochen vom 05.01. bis 05.07.2026, 6.465 Aktivitäten, acht Sportarten, 30 fiktive Angebote. Vollständiges Raster: 2.600 Nutzerwochen, davon 2.042 aktiv und 558 Nullwochen (21,4615 %). Quellen: `data/raw/*.csv`, `data/processed/user_weekly_activities.csv`, `outputs/tables/simulation_weekly_check.csv`, `documentation/active_data_version.json`. Erneut durch Inhaltsaudit geprüft.

| Tatsächliche Datei | Zeilen / Schema | Qualitätsbefund |
| --- | --- | --- |
| `data/raw/users_simulated.csv` | 100; `user_id`, `interest_sport`, `interest_outdoor`, `interest_wellness`, `interest_leisure` | Eindeutige Text-IDs, Booleanwerte True/False, keine Leerfelder |
| `data/raw/activities_simulated.csv` | 6.465; `activity_id`, `user_id`, `date`, `sport_type`, `duration_min`, `distance_km` | Eindeutige Aktivitäten, bekannte Nutzer, gültige Datums-/Sport-/Dauerwerte |
| `data/raw/offers_simulated.csv` | 30; `offer_id`, `category`, `title`, `price_eur`, `discount_pct` | Eindeutiger fiktiver Katalog; vier Kategorien, Preise/Rabatte als Angebotsinformationen |
| `data/processed/user_weekly_activities.csv` | 2.600; `user_id`, `week_index`, `week_start`, `week_end`, `activities_count`, `total_duration_min` | Eindeutiges vollständiges Nutzer-Wochen-Raster; Counts und Minuten direkt aus Rohdaten rekonstruiert |

CSV hat keine physischen Typdeklarationen. IDs sind Text, Counts Ganzzahlen, Minuten/Distanz Dezimalzahlen, Datumswerte ISO-Daten. Acht Sportarten: Running, Cycling, Strength, Swimming, Walking, Hiking, Tennis, Padel. Insgesamt 422.829,9 Minuten. Genau 1.698 fehlende Distanzen sind strukturell nicht anwendbar: Strength 851, Tennis 434, Padel 413. Keine Distanzimputation; bei den fünf Distanzsportarten keine fehlenden Distanzen. Quellen: Rohaktivitäten, `data_dictionary.md`, Inhaltsaudit.

**Entscheidung:** aktive V2, Master-Seed 42, getrennte Zufallsströme 42–49, Präferenzexponent 1,3. Interne überlappende Profile, Häufigkeits-/Trend-/Pausenannahmen und sportabhängige Dauer-/Distanzverteilungen sind generative Annahmen. Interessen sind unabhängig erzeugte Bernoulliwerte, keine erhobenen Präferenzen. Quelle: `simulation_config.md`, `src/simulation_v2.py`.

**Grenze:** Keine tatsächlich beobachteten Garmin-Daten in der geprüften Modellbasis. Vollständige Aufzeichnung und echte Inaktivität sind hier aufgrund der Simulation bekannt. Bei realen Wearables wäre eine fehlende Aktivität nicht ohne Weiteres eine Nullwoche (Nichttragen, fehlende Synchronisation, Messausfälle). Wetter, Verletzungen und reale Messfehler sind nicht empirisch abgebildet. Ein Seed und 100 Nutzer begrenzen externe Validität; plausible Konstruktion ersetzt keine Realitätsvalidierung.

## 3. Data Preparation

**Implementierung/Messung:** Vollständige Kette anhand der Exporte und `src/data_preparation_*.py` geprüft; das vorhandene unabhängige Inhaltsaudit rekonstruiert Werte im Speicher ohne Export oder Fit.

1. Auswahl/Bereinigung: `activities_selected.csv` enthält dieselben 6.465 Aktivitäten mit fünf unveränderten Werten pro Zeile; nur `distance_km` wird als für die ersten Modelle unnötig weggelassen. Validierung statt stiller Imputation oder Löschung gültiger Aktivitäten.
2. Wochenaggregation: Montag–Sonntag, Nutzer × relative Projektwochen 1–26. Ergänzung von 558 unbelegten gültigen Gruppen mit Count und Minuten 0, ohne neue Rohaktivitäten zu erzeugen. Alle Counts gegen separate Wochenkontrolle geprüft.
3. K-Means-Nutzerfeatures: `kmeans_user_features.csv`, 100 × 12. Eingang: Gesamtaktivitäten/26 sowie acht Sportcounts/Gesamtaktivitäten. Minuten/Woche und Sportvielfalt ausschließlich zur Interpretation; Nutzer-ID kein X. Alle aktiven Profile haben definierte Anteile mit Summe 1. Zukünftig vollständig Inaktive hätten undefinierten Sportmix und müssten separat behandelt werden.
4. Standardisierung: `kmeans_user_features_scaled.csv`, 100 × 10 inklusive ID. Häufigkeit `(x−mean)/scale`; jeder Sportanteil zusätzlich mit `1/√8 = 0,35355339059327373` gewichtet. Gespeicherte StandardScaler-Parameter, Populationsvarianz ddof=0, deskriptiver damaliger Fit auf allen 100 Profilen. Keine neue Anpassung. Blockvarianzsummen erneut jeweils ≈1 geprüft. Gewichtung ist fachliche Startannahme, keine optimierte empirische Gewichtung; skalierte Sportwerte sind keine Wahrscheinlichkeiten. Quelle: `outputs/models/kmeans_scaling_params.json`.
5. Regressionsfeatures: `regression_weekly_features.csv`, 2.200 × 7. X1=`activities_current_week`=c(t), X2=`avg_activities_last_4_weeks`=Mittel c(t−3)…c(t), y=`activities_next_week`=c(t+1). Dazu vier Zuordnungsfelder `user_id`, `week_index`, `week_start`, `week_end`. Keine K-Means-Features, Interessen oder IDs als Regressoren; keine Skalierung. Die ersten drei Eingabewochen haben keine vollständige Historie, Woche 26 kein beobachtetes Folgeziel; diese 400 Rasterzeilen werden nicht künstlich aufgefüllt. Sie bleiben im Grundraster.
6. Chronologischer Split: `regression_train.csv` 1.800, Eingabewochen 4–21, Zielwochen 5–22 (02.02.–07.06.2026); `regression_test.csv` 400, Eingabewochen 22–25, Zielwochen 23–26 (08.06.–05.07.2026). Alle 100 Nutzer in beiden Teilen, disjunkte Zielzeiträume. Rollierende Einwochenprognose: beim jeweiligen Zeitpunkt bereits abgeschlossene Testwochen dürfen spätere Eingaben bilden; Modell unverändert. Kein Test neuer Nutzer. Quelle: `regression_split_manifest.json`.

**Messung zur Nullwochenwirkung:** 6.465/2.600 = **2,4865384615** Aktivitäten pro Nutzerwoche. Ohne Nullen: 6.465/2.042 = **3,1660137120**; relative Überschätzung `(3,1660137120/2,4865384615−1)×100` = **27,3261508325 %**. Der Effekt betrifft den Nenner, keine Verbesserung der Aktivität. Quelle: Wochenraster, erneut geprüft; vorhandener Bericht `outputs/tables/data_preparation_audit_report.md`.

## 4. K-Means

**Eingänge/Entscheidung:** neun bereits skalierte und gewichtete Merkmale aus Abschnitt 3, kein erneuter Scaler-Fit. `kmeans_k_selection.csv` belegt tatsächlich getestete k=1–8, wobei für k=1 keine Silhouette definiert ist. Vertiefter Seedvergleich betrifft k=2,3,6,8, nicht alle acht k-Werte.

| Gespeicherter Vergleich | k=2 | k=3 | k=6 | k=8 |
| --- | ---: | ---: | ---: | ---: |
| Silhouette bei Seed 42 (`kmeans_k_selection.csv`) | 0,303337 | 0,184642 | 0,194309 | 0,206130 |
| Mittlere paarweise ARI, 20 Seeds (`kmeans_candidate_comparison.csv`) | 1,000000 | 0,922837 | 0,657272 | 0,673694 |

**Messung:** `kmeans_stability_results.csv` enthält 80 Ergebnisse: vier k-Werte × Seeds 0–18 und 42. Bei k=2 eine Partition, 190 Seedpaare mit ARI=1; mögliche Labelvertauschungen ändern die Partition nicht. Diese Stabilität gilt für Initialisierung auf demselben Datenbestand, nicht für Resampling oder reale neue Populationen.

**Entscheidung:** k=2 wegen höchster beobachteter Silhouette, Stabilität und einfacher Interpretation. Finales gespeichertes Modell `outputs/models/kmeans_final.joblib`, Metadaten `kmeans_final_metadata.json`, Labels `data/processed/user_clusters.csv`. Parameter: k-means++, n_init=20, random_state=42, Lloyd; Inertia 126,4979065295. **Messung:** 57/43 Nutzer, Silhouette **0,30333715184382104**. Gespeicherte Labels durch predict des vorhandenen Modells und Silhouette erneut trainingsfrei geprüft.

**Interpretation:** „Geringere Trainingshäufigkeit“ (57, im Mittel 1,5351 Aktivitäten/Woche) und „Höhere Trainingshäufigkeit“ (43, 3,7478). Quelle: `kmeans_final_cluster_profiles.csv`. Relative Häufigkeit dominiert die Deutung; keine sauberen acht Sportsegmente, keine Fitness-, Gesundheits- oder Erfahrungsdiagnose. **Grenze:** moderate Trennung, überlappende synthetische Sportprofile, k=2 nur innerhalb untersuchter Darstellung/Kandidaten begründet; keine extern validierten Nutzertypen. Keine neuen Clustertrainings durchgeführt.

## 5. Lineare Regression

**Implementierung:** vorhandenes globales `outputs/models/regression_linear.joblib`, keine Anpassung. Modellgleichung aus `regression_linear_metadata.json` und `regression_linear_coefficients.csv`:

`ŷ(t+1) = 0,8397931020190079 + 0,22819007785063997 × c(t) + 0,42396047869339204 × mean(c(t−3),…,c(t))`.

Ziel: gesamte Aktivitätszahl der nächsten Woche über alle Sportarten. Split wie Abschnitt 3; keine Zukunft in X. Koeffizienten sind bedingte Modellparameter mit korrelierten Eingängen, keine kausalen Wirkungen. Unveränderte kontinuierliche Prognosen, keine Rundung/Nullregel zur Testoptimierung.

| Messung auf 400 Testfällen | Regression | Persistence-Baseline c(t) |
| --- | ---: | ---: |
| MAE, Aktivitäten/Woche | 1,4898770575225395 | 1,7100000000 |
| RMSE, Aktivitäten/Woche | 1,9085376545370092 | 2,3108440016582685 |

Absolute MAE-Differenz **0,22012294247746045**, relativ **12,8726866946 %**. Quellen: `regression_test_predictions.csv` (400 tatsächliche gespeicherte Prognosen), `regression_test_metrics.json`, `regression_baseline_metrics.json`, `regression_baseline_comparison.csv`. Vorhandene Modellinferenz und Testkennzahlen erneut im Speicher geprüft; Tests rechnen Fehler unabhängig aus Exporten nach. Beispiel U001, Eingabewoche 22: c(t)=1, Vierwochenmittel 2,25, Ist Folgewoche=2, Prognose=2,0218942569297802, Baseline=1.

**Bekannte Schwäche:** 92 später tatsächlich inaktive Zielwochen: MAE Regression **1,8782923959526365**, Baseline **1,3804347826086956** (relative MAE-Verschlechterung 36,0653 %). RMSE derselben Untergruppe dagegen **2,0312668199362336** versus **2,149317384052738**. „Schlechter bei Nullwochen“ bezieht sich präzise auf MAE, nicht auf jede Metrik. Bei 308 positiven Zielwochen MAE 1,3738568915 versus 1,8084415584. Quelle: `regression_baseline_metrics.json`, `modeling_evaluation.md`.

**Grenze:** Ein positiver Intercept und positive Koeffizienten liefern bei nichtnegativen Eingängen keine exakten Nullprognosen. Die Gruppierung nach künftigem Istwert ist ausschließlich nachträgliche Fehlerdiagnose. Sie ist zum Prognosezeitpunkt unbekannt und darf keine Umschaltregel oder Modellauswahl begründen. Nur vier Testzielwochen derselben synthetischen Nutzer, kein externer Holdout, keine individuellen Prognosegarantien oder kausalen Aussagen. Für die Demo-Zielwoche 06.–12.07.2026 gibt es keine gemessenen Istwerte.

## 6. Empfehlungssystem

**Implementierung:** `src/recommendation_engine.py`; nur positiv ausgewählte und simuliert freigegebene Interessenkategorien bilden Kandidaten. Separater Garmin-Schalter erlaubt Sportprofil/Modellkontext. Beide Freigaben sind simuliert, kein realer Einwilligungsnachweis. Ohne Interessenfreigabe keine personalisierte Angebotsliste; Sporthistorie umgeht die Vorauswahl nicht.

Stufe A: manuell bestätigter Angebotstag und positiver historischer Sportanteil. Stufe B: übrige zulässige Angebote. A vor B; innerhalb A höchster passender Sportanteil absteigend, Gleichstände und B nach offer_id. Maximal fünf Angebote; kein Preis-/Rabatt-/Cluster-/Regressionsscore. K-Means ist getrennte gespeicherte Segmentinformation, Regression getrennte Modellinferenz; beide beeinflussen das Ranking nicht.

**Manuelle Entscheidung:** `offer_sport_tags_approved.csv` enthält acht bestätigte Angebotszuordnungen: O001 Running, O003 Swimming, O004 Tennis, O005 Padel, O006 Cycling, O007 Strength, O009/O010 Hiking. Präzisierung: acht Angebote, sieben unterschiedliche Sportarten; Walking ohne bestätigten Angebotstag. `offer_sport_mapping_review.csv` ist Vorschlagsmaterial, keine automatische Freigabe.

**Messung:** kontrollierter Vorher-Nachher-Vergleich desselben Katalogs, derselben 100 Nutzer und gleicher simulierter Freigaben, nur Tagfreigabe verändert. Quelle: `recommendation_before_after_summary.json`, zugehörige Nutzer-/Angebots-CSVs, `src/recommendation_comparison.py`; erneut mit bestehender Engine im Speicher geprüft.

| Kennzahl | Ergebnis |
| --- | ---: |
| Unveränderte geordnete Top-5-Listen | 36 |
| Veränderte Zusammensetzung | 64 |
| Nur Umordnung ohne Austausch | 0 |
| Empfehlungsslots vorher / nachher | 475 / 475 |
| A-Slots vorher / nachher | 0 / 344 |
| A-Anteil nachher | 344/475 = 72,4210526316 % |

Fünf Nutzer ohne positive Interessen erhalten keine personalisierten Angebote; 95 × 5 erklärt 475 Slots je Variante. U001: O001/O002/O003/O004/O005 → O001/O006/O009/O010/O002. **Grenze:** gemessen ist die Wirkung deterministischer Regeln auf Listen, keine Relevanz, Akzeptanz, bessere Empfehlungsqualität oder wirtschaftliche Wirksamkeit. Die Sportanteile sind Verhaltenshäufigkeiten der Simulation, keine Kaufpräferenzen.

## 7. Dashboard

**Implementiert:** `app.py`, Module `dashboard/`, Streamlit 1.66.1 und Plotly 6.4.0 (Lockdatei). User View mit gemeinsamer Wahl aus 100 Nutzern, Aktivitäten/Minuten, 26-Wochen-Verlauf inklusive Nullen, Sportmix, gespeichertem Segment, Python-Regressionsinferenz und Angeboten. Analytics Lab mit sieben Bereichen: Data Understanding, Data Preparation, K-Means, Regression, Evaluation, Empfehlungssystem, CRISP-DM.

Vier zentrale interaktive Experimente: (1) Nennerwirkung der Nullwochen, (2) gespeicherte k=2/3/6/8 vergleichen, (3) einen der 400 Testfälle mit Ist/Regression/Baseline untersuchen, (4) Tagfreigabe und U001-Listenvergleich. Keine neuen Modelle bei Interaktion. Getrennte simulierte Freigaben standardmäßig aus und bei Nutzerwechsel zurückgesetzt. Personenbezogene Detailzugriffe sind vor Quellenzugriff begrenzt. Quellen: `dashboard/state.py`, `services.py`, `analytics_data.py`, `user_view.py`, `analytics_view.py`, Tests und `dashboard_execution.md`.

**Historisch dokumentierte Abnahme:** AP 7.5a/7.5b prüfte alle 100 Nutzer, 400 Freigabekombinationen, alle sieben Lab-Bereiche und vier Experimente; Chromium auf Desktop/Laptop/Mobil ohne dokumentierte Seitenfehler oder horizontalen Seitenüberlauf. Screenshots unter `documentation/screenshots/`. AP 8 übernimmt diese Browsernachweise als historische Belege; keine erneute physische Laptop-/Browserabnahme behauptet.

**Lokaler Start:** vollständiger Clone mit Git-Historie, Python 3.12, `python -m venv .venv`, danach über den Interpreter der Umgebung `python -m pip install -r requirements-dashboard-lock.txt` und `python -m streamlit run app.py`. Unter Windows `.venv\Scripts\python.exe`, unter Linux/macOS `.venv/bin/python`. Anleitung und 15-Minuten-Demo: `dashboard_demo_guide.md`. Die dort genannte Branchwahl `ap7-dashboard` ist historisch; der hier bestätigte main enthält AP 7 vollständig. Git-Basisobjekte `23ac008651de490d59e9ec5ceae590ba97daf0e5` und `a8f97ad75c378329a614a322bd541f372de0b072` werden für Integritätsverträge benötigt; ZIP oder kopierter Worktree ersetzt keinen vollständigen Clone.

## 8. Tests und Reproduzierbarkeit

AP-7-Gesamtabnahme laut `dashboard_execution.md`, Abschnitt 35: **178 entdeckt, 157 bestanden, 21 ausdrücklich ausgeschlossen**, keine Fehler. Aktueller AP-8-Lauf und Integritätsabschluss werden unten protokolliert.

Der vorhandene Runner `tests/run_without_training.py` wurde gelesen und verwendet. Aktive Sperren auf `KMeans.fit`, `LinearRegression.fit`, `StandardScaler.fit`; übersehene Trainingspfade müssen fehlschlagen. Ausgeschlossen vor trainierendem Setup: neun Tests aus `test_modeling_kmeans_k_selection.KSelectionTests`, neun aus `test_modeling_kmeans_stability.StabilityTests`; außerdem `FinalKMeansTests.test_no_scaling_and_exact_input_reproduction` und die Regressionstests `test_training_without_test_access_scaling_or_scoring`, `test_loaded_training_predictions_equal_fresh_fit`. Diese 21 sind keine in AP 8 ausgeführten Trainingsnachweise.

Ausgeführt werden Daten-/Leakage-/Splitprüfungen, gespeicherte Modell-/Metadaten-/Hashverträge, trainingsfreie Regressionsevaluation und Baseline, Empfehlungstests sowie Dashboard-AppTests und Freigabesperren. Vorhandene Negativtests verwenden manipulierte Kopien ausschließlich als temporäre technische Fixtures, keine neue synthetische Projektpopulation. Kein Generator-CLI, kein Transformations-/Modelltraining-CLI und keine Exportfunktion aufgerufen.

Zusätzlich: vorhandenes unabhängiges Data-Preparation-Inhaltsaudit direkt im Speicher, alle gespeicherten K-Means-Labels per predict, Silhouette und vorhandene Regressionsevaluation geprüft; Empfehlungssummary mit unveränderter Engine vollständig abgeglichen. 200 bisherige Dateien vor und nach diesem Audit bytegleich. Temporärer Prüfcode/Logs unter `work/`; daraus werden keine neuen wissenschaftlichen Ergebnisse abgeleitet.

**Umgebung:** Python 3.12.14. Für aktuelle AppTests temporäre Umgebung `work/ap8-venv` mit vorhandenen Systempaketen plus Installation der Dashboard-Lockdatei; `pip check` erfolgreich. Dies ist keine neue Prüfung einer vollständig sauberen Installation. Historisch wurde ein eigenständiger verschobener vollständiger Clone unter Linux mit laufendem Streamlit-Server und Chromium erfolgreich geprüft, dabei wurde eine vorhandene Python-Umgebung wiederverwendet (`dashboard_execution.md`, Abschnitt 32). Windows/macOS und der konkrete Präsentationslaptop sind weiterhin nicht praktisch abgenommen.

## 9. Tatsächliche CRISP-DM-Iterationen

**Genau eine belegte fachliche Iteration: MOVA-ITER-001**, dokumentiert in `crisp_dm_log.md`, `decisions.md`, `simulation_config.md` und `outputs/simulation_comparison/comparison_report.md`:

1. Erste synthetische Generierung V1 mit Präferenzexponent 1,0.
2. Analyse: 59 Nutzer mit acht Sportarten, mittlere Vielfalt 7,47; gewünschte persönliche Schwerpunkte trotz Überschneidungen weiter prüfen.
3. Rücksprung von Data Understanding zu Construct Data: Exponent auf 1,3 erhöhen.
4. Erneute Generierung, Qualitätsprüfung und Vergleich; anschließende verbindliche Übernahme V2.

Die technische Aufteilung der Zufallsströme erforderte eine gepaarte Kontrolle mit Exponent 1,0. **Nur Kontrolle→V2 isoliert den Exponenteneffekt:** Nutzer mit acht Sportarten 58→40, mittlere Vielfalt 7,32→6,95, Top-2-Mittel 57,61→64,12 %. Aktivitätscounts in diesem Vergleich unverändert (6.465). Historisch V1 6.665 Aktivitäten/545 Nullwochen gegenüber V2 6.465/558 enthält zusätzlich den technischen Zufallsstromwechsel; diese Häufigkeitsänderung ist kein isolierter Exponenteneffekt.

**Abgrenzung:** k-/Seedvergleiche begründen eine Modellauswahl innerhalb Modeling; Regression-Baseline- und Fehlergruppenvergleiche führten nicht zu nachgelagerter Modelländerung und belegen keine weitere fachliche Rücksprungiteration. Fehlerbehebungen, Portabilitäts-/Freigabeprüfungen, manuelle Angebotstags und Dokumentationsfortschreibungen sind keine zusätzliche belegte fachliche CRISP-DM-Iteration. AP 8 hat nichts neu generiert.

## 10. Wissenschaftliche Stärken

- Transparente Datenherkunft und explizite synthetische Annahmen; historische V1 von aktiver V2 getrennt.
- Vollständiges Wochenraster mit quantifiziertem Nullwochen-Auslassungseffekt; nachvollziehbare Feature-/Skalierungsverträge.
- Chronologische Prognosebewertung mit einfacher Persistence-Baseline und offengelegter Nullzielschwäche.
- Dokumentierter k-Vergleich und Initialisierungsstabilität; Clusterinterpretation auf relative Häufigkeit begrenzt.
- Kontrollierter Vergleich der Regelwirkung; Trennung von Ranking, ML-Kontext und simulierten Freigaben.
- Hash-/Git-Verträge, gespeicherte Artefakte, trainingsfreie Negativtests und interaktive Erklärungen unterstützen technische Nachvollziehbarkeit. Diese Stärken belegen interne Konsistenz, keine externe Wirksamkeit.

## 11. Wissenschaftliche Grenzen

| Bereich | Nachweisgrenze / Konsequenz |
| --- | --- |
| Synthetische Daten | Ein Seed, kleine konstruierte Population; keine Repräsentativität oder Validierung realer Garmin-Nutzer |
| Cluster | Silhouette ≈0,3033, überlappende Sportprofile; Seedstabilität ersetzt keine robuste externe Nutzertypologie |
| Prognose | Nur vier Testwochen derselben Nutzer; Restfehler, keine individuellen Garantien, keine Unsicherheitsintervalle oder externe Generalisierung nachgewiesen |
| Zukünftige Nullwochen | MAE schlechter als Persistenz; Zielgruppen nach Zukunft nur retrospektiv analysierbar |
| Präferenzen/Nutzung | Simulierte Interessen, keine echten Relevanzlabels, Klicks, Buchungen oder Akzeptanzdaten |
| Geschäftswirkung | Keine Conversion-, Provisions- oder Umsatzdaten; keine wirtschaftliche Erfolgsaussage |
| Einwilligung | Getrennte Demo-Schalter ohne reale Einwilligungsinfrastruktur, OAuth oder produktive Garmin-Anbindung |
| Deployment | Lokaler Hochschuldemonstrator; keine produktive Betriebs-/Mehrnutzerabnahme; Windows/macOS und Präsentationslaptop offen |

Technische Funktionsfähigkeit und interne Konsistenz sind nachweisbar. Wissenschaftlich belegter realer Nutzer- oder Geschäftsnutzen ist damit nicht erreicht.

## 12. Offene Fragestellungen und Konsistenzbefunde

**Nicht untersucht:** Übertragbarkeit auf reale Garmin-Nutzer und fehlende Aufzeichnungen; externe Clusterqualität; Prognose über andere Zeiträume/neue Nutzer und Unsicherheiten; reale Präferenzen und Empfehlungsrelevanz; tatsächliche Nutzung/Conversion/Umsatz; belastbare Einwilligungsprozesse; praktische Abnahme auf Präsentationshardware und Windows/macOS. Diese Punkte sind künftige Fragestellungen, keine Aufträge für neue Modellierung in AP 8.1.

**Dokumentationsabweichungen, bewusst nicht stillschweigend geändert:**

- `README.md` behauptet noch ausschließlich Projektstruktur, keine Daten/Modelle/UI und unfixierte Versionen; tatsächlich sind synthetische Dateien, zwei Modelle, Dashboard und Lockdatei in main vorhanden. README ist als aktueller Status veraltet, als Zielbeschreibung nutzbar.
- `data_dictionary.md` enthält „Modelle stehen aus“, `simulation_config.md` noch „keine vollständige Modellaufbereitung“, `kmeans_scaling_params.json` den damaligen Status „AP-4-Skripte uncommitted“. Diese historischen Formulierungen widersprechen als Gegenwartsbeschreibung dem Git-/Artefaktbestand.
- `regression_linear_metadata.json` hält `test_evaluation_performed=false` aus der Trainingsphase fest; separate spätere Testmetriken/Prognosen belegen die tatsächlich ausgeführte Evaluation. Kein fehlender Testlauf aus diesem historischen Flag ableiten.
- `crisp_dm_log.md` enthält zuerst „keine Iterationen“, danach ausdrücklich MOVA-ITER-001 und die finale V2-Entscheidung. Späterer datierter Eintrag löst den historischen Status auf.
- `recommendation_concept.md` beschreibt noch ungeprüfte Tags und offene Top-N-Ausgabe; `offer_sport_tags_approved.csv` und Engine belegen den späteren Stand mit acht Freigaben und höchstens fünf Angeboten.
- `dashboard_execution.md` enthält frühere Zwischenzahlen (60/137/155 Tests, alte main-Basis, uncommittete App). Maßgeblich für AP-7-Endstand: Abschnitt 35 und bestätigter PR-Merge; 157 erfolgreiche plus 21 ausgeschlossene Tests sind 178 entdeckte Fälle.
- Historische V1-Berichte mit 6.665 Aktivitäten sind keine widersprüchlichen V2-Messungen. Acht Angebotsfreigaben sind keine acht unterschiedlichen freigegebenen Sportarten. „Nullwochen schlechter“ ist auf MAE zu präzisieren (Abschnitt 5).

Die zentralen vorgegebenen V2-Zahlen sind durch Daten-/Artefaktabgleich bestätigt. Bekannte Grenzen bleiben offen; keine zusätzlichen fachlichen Iterationen oder Ergebnisse ergänzt.

## 13. Nachweisbare Quellen innerhalb des Repositorys

Alle folgenden Pfade sind relativ zum Repository; Dokumentationsnamen in vorigen Abschnitten ohne Präfix liegen unter `documentation/`. Sie beziehen sich auf die oben genannte unveränderte main-Basis.

| AP / Thema | Geprüfte Belege |
| --- | --- |
| AP 1 / Ziele | `README.md`, `documentation/decisions.md`, `documentation/crisp_dm_log.md`, Git-Historie |
| AP 2 / Simulation | `src/data_generation.py`, `src/simulation_v2.py`, `documentation/simulation_config.md`, `documentation/active_data_version.json`, `outputs/tables/active_data_validation.md`, `outputs/tables/simulation_report_v2.md`, `outputs/simulation_comparison/comparison_report.md`, `outputs/simulation_comparison/v1_snapshot/` |
| AP 3 / Verständnis und Konzepte | `documentation/data_dictionary.md`, `documentation/kmeans_feature_concept.md`, `documentation/regression_feature_concept.md`, `documentation/data_preparation_plan.md` |
| AP 4 / Aufbereitung | `src/data_preparation_*.py`, alle acht CSVs unter `data/processed/`, `documentation/data_preparation_execution.md`, `documentation/regression_split_manifest.json`, `outputs/tables/data_preparation_audit_report.md`, `outputs/models/kmeans_scaling_params.json` |
| AP 5 / K-Means | `outputs/models/kmeans_final.joblib`, `outputs/models/kmeans_final_metadata.json`, `outputs/tables/kmeans_k_selection.csv`, `outputs/tables/kmeans_candidate_comparison.csv`, `outputs/tables/kmeans_stability_results.csv`, `outputs/tables/kmeans_final_cluster_profiles.csv`, `documentation/kmeans_modeling_execution.md`, `documentation/kmeans_inference_contract.md` |
| AP 5 / Regression und Evaluation | `outputs/models/regression_linear.joblib`, `outputs/models/regression_linear_metadata.json`, `outputs/tables/regression_linear_coefficients.csv`, `outputs/tables/regression_test_predictions.csv`, `outputs/tables/regression_test_metrics.json`, `outputs/tables/regression_test_metrics_by_week.csv`, `outputs/tables/regression_baseline_metrics.json`, `outputs/tables/regression_baseline_comparison.csv`, `outputs/tables/modeling_evaluation_summary.json`, `documentation/modeling_evaluation.md`, `documentation/modeling_versioning_validation.md`, `documentation/regression_modeling_execution.md` |
| AP 6 / Empfehlungen | `src/recommendation_engine.py`, `src/recommendation_comparison.py`, `documentation/offer_sport_tags_approved.csv`, `documentation/offer_sport_mapping_review.csv`, `documentation/recommendation_execution.md`, `documentation/recommendation_dashboard_contract.md`, `outputs/tables/recommendation_before_after_{summary.json,users.csv,offers.csv}` |
| AP 7 / Dashboard und Abnahme | `app.py`, `dashboard/`, `requirements-dashboard-lock.txt`, `.gitattributes`, `documentation/dashboard_concept.md`, `documentation/dashboard_execution.md`, `documentation/dashboard_demo_guide.md`, `documentation/screenshots/`, `tests/test_dashboard*.py`, `tests/run_without_training.py` |

Die Bestandsvollständigkeit umfasst die dokumentierte technische AP-1–7-Kette und ihre gespeicherten Belege. Nicht versionierte lokale Kontroll-/V2-Rohdatenkopien aus früheren Vergleichsläufen sind laut `simulation_config.md` absichtlich nicht Teil eines frischen Checkouts; sie wurden wegen Generierungsverbot nicht neu erzeugt. Das ist kein Nachweis verlorener aktiver Projektdaten.

### AP-8-Prüfabschluss

**Aktueller AP-8-Lauf am 03.11.2026: 178 entdeckt, 157 bestanden, 21 planmäßig übersprungen, keine Fehler/Fehlschläge.** Laufzeit des unittest-Runners: 15,882 Sekunden. Befehl aus dem Worktree:

```bash
MPLCONFIGDIR=/workspace/MOVA-AP8/work/matplotlib \
XDG_CACHE_HOME=/workspace/MOVA-AP8/work/cache \
OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 \
work/ap8-venv/bin/python tests/run_without_training.py
```

Prüfprotokoll: `work/ap8-tests.log`; Inhaltsaudit: `work/ap8_audit.py`, `work/ap8_audit_results.json`, `work/ap8-audit.log`; Ausgangshashes: `work/ap8_original_hashes.json`. Diese technischen Zwischenbelege sind ignoriert und nicht für einen Commit vorgemerkt. `pip check`: keine defekten Anforderungen. Die erste Paketinstallation ohne Netzwerkfreigabe scheiterte; Installation in der temporären Umgebung über den vorgesehenen Proxy mit Netzwerkzugriff gelang. Keine Einschränkung des Testresultats daraus.

Abschließender SHA-256-/HEAD-Vergleich aller 200 bisherigen versionierten Dateien nach der Suite: unverändert; insbesondere Rohdaten und beide Modelle. `git fsck --full` und `git diff --check` ohne Befund. Einzige neue nicht ignorierte Datei: `documentation/final_evaluation_evidence.md`; nicht vorgemerkt, kein Commit, kein PR. Der Branch verbleibt auf dem bestätigten Basiscommit.

**AP 8.2 kann beginnen:** Die quellenbezogene Ergebnisgrundlage ist konsistent und für die wissenschaftliche Gesamtevaluation verwendbar, sofern sie synthetische interne Ergebnisse, technische Implementierung und unbewiesenen realen Nutzen getrennt hält. Keine kritischen technischen Prüfprobleme festgestellt. Offene Sachfragen und Präsentationshardware-Abnahme aus Abschnitt 12 bleiben bestehen; der Dokumentationsrückstand der historischen Statusformulierungen wird hier ausdrücklich offengelegt.
