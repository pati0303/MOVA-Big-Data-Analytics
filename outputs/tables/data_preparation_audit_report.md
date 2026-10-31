# MOVA – unabhängiges Data-Preparation-Audit (AP 4.7)

Stand: 31.10.2026. Aktive synthetische V2. CRISP-DM 3.5 Format Data / Qualitätssicherung.
Basiscommit: `ed52949cb8b688bc64c0793be0e407950314769e`, Branch `ap4-data-preparation`; AP-4-Arbeit weiterhin uncommitted.

## Ziel und unabhängige Methode

Alle tatsächlichen CSV-/JSON-Artefakte erneut einlesen. Keine früheren Prüfberichte als Beweis und keine Imports aus Transformationsskripten. Wochenwerte direkt aus Rohaktivitäten rekonstruieren, Nutzer-/Sportaggregate mit Groupby/Crosstab unabhängig nachrechnen, Skalierungsparameter gegen Populationsstatistiken vergleichen, Regressionsfenster per Nutzer/Wochenadresse nachprüfen. Keine bestehenden Daten oder Transformationsskripte ändern. Kritische Fehler stoppen vor Visualisierung und Berichterstellung.

## Tatsächlich geprüfte Dateien und SHA-256

| Datei | SHA-256 |
| --- | --- |
| `data/processed/activities_selected.csv` | `1dc3617cc2f9640bede26cae532bf2231fa3d7a7b3e97adc42d4d830a7f81fa1` |
| `data/processed/kmeans_user_features.csv` | `bb6b0c4e9307ab286f9f6e76d04b9b1446a9ab322e31784c8883a6a596ca7a28` |
| `data/processed/kmeans_user_features_scaled.csv` | `73f1694e865c8f65b0eabb45f7a80bd439bbc9bfd4b6f281cffaa15da491d78f` |
| `data/processed/regression_test.csv` | `b0c11c94209323c01f098042261349a3ed506c408af5303a4ac9d5e84715c1fa` |
| `data/processed/regression_train.csv` | `e984a547de12aca7d53ce908dd5051992bbd21aa83895a67bcd6fc0b541fb0b8` |
| `data/processed/regression_weekly_features.csv` | `4fc681eaa1a042a1b44cf6bc742a27f3277eafb7a9c54f5ff78736d998b70914` |
| `data/processed/user_weekly_activities.csv` | `c34a7bd16d1cdc3e91388cc35b8c784afde0b53c1dbfdd24de97148350359b74` |
| `data/raw/activities_simulated.csv` | `c3789d26f00cba3ba14952cf99909b091cb263045b8993ed366fe5aa64a4ee6b` |
| `data/raw/offers_simulated.csv` | `83748cb66918c08e3061889834e24452d0dc9feb6581690c4959cb3ba3775fa6` |
| `data/raw/users_simulated.csv` | `6ba9f8398707412bf922c76e352d2a6a7f86857e7a54dbbf1421555b1dbf99f9` |
| `documentation/active_data_version.json` | `f032e5898c1e4ead10da30f0f39d4a327df3e16a9adeddde457d24db6ddd18a5` |
| `documentation/regression_split_manifest.json` | `536137414d579a30fef9fb946ac04e114fac50ffaff6462861fdb69cc984caff` |
| `outputs/models/kmeans_scaling_params.json` | `1794271bbfaf53818511002a13247c8cb251d5871b0b62e62729d817356a24b4` |
| `outputs/tables/simulation_weekly_check.csv` | `70c290c2913ea976fe0bb370b1debf4d78febb5896247f5e02a1f8aa0b1381b8` |

Alle vier aktiven V2-Manifest-Prüfsummen und dokumentierten Eingangs-/Ausgabehashes in Skalierungsparametern und Split-Manifest stimmen. Alle aufgelisteten Dateien vor/nach Audit auf bytegleiche Integrität geprüft. Angebote werden ausschließlich per Hash geprüft, nicht in Modellierungsdaten integriert.

## Tatsächliche Qualitätsprüfungen

| Prüfung | Ergebnis |
| --- | --- |
| Schemas, Zeilenzahlen, Schlüssel und Nutzerlisten | BESTANDEN: Alle zehn CSVs vollständig; skalierter Export exakt ID + neun Eingänge |
| Aktivitätsauswahl und Rohqualität | BESTANDEN: Alle 6.465 Aktivitätszeilen und fünf Werte exakt erhalten; 1698 strukturell nicht anwendbare Distanzen |
| Wochenraster und Rohdatenrekonstruktion | BESTANDEN: 2.600 eindeutige Nutzerwochen; 2.042 aktive Gruppen + 558 echte Nullen; jede Count-/Minutensumme stimmt |
| Nutzeraggregate und neun K-Means-Merkmale | BESTANDEN: 100 vollständige Profile; alle Sportanteile und zwei Interpretationsmerkmale unabhängig rekonstruiert |
| Standardisierung und Gewichtung | BESTANDEN: Alle Parameter unabhängig nachgerechnet; JSON reproduziert 100×9 Werte; Blockvarianzsummen jeweils ≈1 |
| Regression und Zeitverfügbarkeit | BESTANDEN: Alle 2.200 Zeilen: X nur t−3…t, y t+1 desselben Nutzers; keine künstliche Historie |
| Train/Test und Manifest | BESTANDEN: 1.800/400 unveränderte Zeilen; 18/4 pro Nutzer; disjunkte Zielwochen 5–22 / 23–26 |

## Neu berechnete Kennzahlen

| Kennzahl | Tatsächlicher Wert |
| --- | --- |
| raw_activities | 6465 |
| selected_activities | 6465 |
| users | 100 |
| weekly_rows | 2600 |
| active_weeks | 2042 |
| zero_weeks | 558 |
| kmeans_rows | 100 |
| scaled_rows | 100 |
| regression_rows | 2200 |
| train_rows | 1800 |
| test_rows | 400 |
| total_minutes | 422829.9 |
| mean_with_zero_weeks | 2.4865384615384616 |
| mean_without_zero_weeks | 3.166013712047013 |
| overestimation_pct | 27.32615083251715 |
| zero_week_pct | 21.461538461538463 |
| regression_current_zeros | 478 |
| regression_target_zeros | 474 |
| regression_zero_history_rows | 1100 |
| weight | 0.35355339059327373 |
| max_abs_scaled_mean | 3.9190872769268024e-16 |
| block_variance_sums | [1.0000000000000002, 0.9999999999999998] |

## Vergleich mit und ohne Nullwochen

Gepoolte Trainingshäufigkeit über das vollständige Raster: 6.465 / 2.600 = **2.48653846 Aktivitäten je Nutzerwoche**. Nach Weglassen der 558 Nullwochen: 6.465 / 2.042 = **3.16601371**. Relative Überschätzung gegenüber der vollständigen Beobachtungszeit: **27.3262 %** ((Mittel ohne Nullen / Mittel mit Nullen − 1) × 100).

Das sind gepoolte Nutzerwochenmittel, keine mittlere Trainingsdauer und keine durchschnittliche Aktivitätszahl ausschließlich aktiver Nutzer. Im vollständigen Raster haben alle Nutzer denselben Nenner 26; deshalb entspricht dieser Mittelwert dort auch dem Mittel ihrer individuellen Wochenhäufigkeiten. Ohne Nullwochen ist die Gewichtung je Nutzer unterschiedlich. Der aktive-Wochen-Mittelwert beschreibt eine andere bedingte Größe und überschätzt bei Verwendung als Häufigkeit über den gesamten Zeitraum systematisch den hier tatsächlich beobachteten Wert.

## Vier Abbildungen

1. [Datenfluss](../figures/data_preparation_pipeline.png): echte Verarbeitung und verschiedene Zeileneinheiten. Nutzer-Sportmix kommt aus Einzelaktivitäten, Nutzerliste führt die Integration an; Wochenwerte liefern den Summenabgleich. Boxgrößen kodieren keine Stichprobengröße.
2. [Nullwochen](../figures/data_preparation_zero_weeks.png): 2.042 aktive + 558 Nullwochen und der exakt berechnete Nenner-Effekt.
3. [Standardisierung](../figures/data_preparation_scaling.png): dieselben 100 Nutzer, Häufigkeit und Running-Anteil jeweils roh, z-standardisiert und nach Gewichtung. Panels mit eigenen x-Skalen; negative z-Werte sind erwartbar. Jeder Sportanteil wird zusätzlich durch √8 geteilt.
4. [Chronologischer Split](../figures/data_preparation_train_test_split.png): getrennte Eingabe-/Zielwochen. Wochen 1–3 liefern Historie; Woche 26 hat kein beobachtetes Folgeziel. Rollierende Einwochenprognosen mit später unverändertem Modell; keine tatsächliche Modellbewertung in diesem Audit.

## Reproduktion und Software

`python src/data_preparation_audit.py`; Python 3.12.14, pandas 2.2.3, NumPy 2.3.5, Matplotlib 3.10.8. Numerische Vergleiche atol=rtol=1e−10; Minuten mit Decimal. Matplotlib Agg, feste Farben/Größen/Schrift und konstante PNG-Metadaten, kein Laufzeitstempel. Ein zweiter Lauf prüft identische Report-/PNG-Bytes; vorhandene fremde/abweichende Audit-Ausgaben werden nicht überschrieben. Reproduzierbarkeit gilt für diese Software-/Schriftumgebung; andere Rendering-Versionen können Pixelunterschiede erzeugen.

## Technische Audit-Tests

`python -m unittest discover -s tests -v`: acht Audit-Tests plus 14 bestehende Zeit-/Splittests bestanden. Audit-Tests prüfen unveränderte V2, manipulierte Wochensummen, entfernte Nullwochen, falsche Train/Test-Grenzen bei unveränderten Zeilenzahlen, unzulässige Interpretationsspalten im skalierten Export, Zukunft im Mittelwert, falsche Gewichtungsparameter und falsche Manifest-Zielgrenzen. Änderungen ausschließlich an Speicherkopien; nicht nur Hashprüfungen, sondern Inhaltskontrollen lösen bei Manipulation aus.

## Auffälligkeiten, Annahmen und Grenzen

Keine Qualitätsabweichung festgestellt. 558 Nullwochen sind echte fehlende Aktivitätsgruppen im bestätigten Raster, keine Imputation fehlerhafter Pflichtwerte. Skalierte share-Werte sind keine Wahrscheinlichkeiten; negative Werte zulässig. Neun positive V2-Merkmalsvarianzen führen nach Gewichtung zu Blockvarianzsummen ≈1; diese gleiche Streuungsgewichtung ist eine fachliche Startannahme, keine empirisch optimierte Clustergewichtung und kein Beleg einer Clusterstruktur.

100 synthetische Nutzer und nur 26 Wochen; wiederholte Nutzer und überlappende Fenster erzeugen Abhängigkeiten. Keine Aussage zur Generalisierbarkeit auf echte Garmin-Nutzer. Testzielzeiträume sind getrennt, historische Eingabewochen dürfen sich überlappen. Neue frühere Testbeobachtungen dürfen erst nach ihrem Abschluss in spätere Eingaben gelangen; kein späteres Nachtrainieren auf Testzielen. Roh-, Auswahl-, Wochen- und Nutzeraggregate bewahren die Gesamtminuten. Regressionszeilen sind dagegen überlappende Fenster mit Rand-Ausschlüssen: ihre Counts oder Mittelwerte dürfen nicht als neue Aktivitäts-Gesamtsumme interpretiert werden.

## Fazit

**Die vorliegenden Datensätze sind intern konsistent und für die geplante nachfolgende Modellierung vorbereitet. Ein bestandener Datenqualitätscheck ist kein Nachweis guter Modellgüte.** Keine Modelle, Labels, Prognosen oder Gütemaße erzeugt; keine neue CRISP-DM-Iteration ohne tatsächlichen Anlass.
