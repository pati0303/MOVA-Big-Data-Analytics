# MOVA – Zweiter CRISP-DM-Modellierungszyklus

Ausführung: 04.11.2026, Branch `feature/crispdm-cycle-2`.
Status: technische Implementierung und interne Evaluation abgeschlossen.

## 1. Business Understanding – freigegebene Hypothese

Aus der Fehlerdiagnose des ersten Zyklus entsteht die Hypothese, dass die Anzahl historischer Nullwochen zusätzliche Prognoseinformation liefert. Ziel bleibt die sportartenübergreifende Einwochenprognose für bekannte synthetische Nutzer unmittelbar nach Abschluss von Woche t.

Vor Umsetzung verbindlich freigegeben: genau Persistenz, globale OLS mit zwei Merkmalen und globale OLS mit drei Merkmalen. Übernahme nur bei strikt geringerem gepooltem MAE UND geringerem MAE in mindestens zwei von drei Folds. Keine zusätzlichen Varianten, Hyperparametersuche, Rundung, Begrenzung oder Dashboardänderung.

## 2. Data Understanding – Datenzugang und Grenzen

Entwicklungsquelle ist ausschließlich der unveränderte ursprüngliche Trainingsbestand: 1.800 Fälle, 100 Nutzer, Eingabewochen 4–21, Ziele 5–22. Quellhashes sind im Laufmanifest verankert. Der bestehende 400-Fälle-Testbestand, gespeicherte Testprognosen und Testergebnisse werden von der Pipeline nicht geöffnet.

Die gemeinsame historische Wochen-CSV enthält auch spätere Wochen. Die Datei wird zur Integritätsprüfung vollständig gehasht; beim CSV-Einlesen werden nur Wochen 1–22 behalten. Spätere Werte werden weder analysiert noch zur Merkmalsbildung oder Entscheidung verwendet. Woche 22 ist als letztes ursprüngliches Trainingsziel zulässig. Die neuen Merkmale benötigen höchstens Woche 21.

Eine Null bezeichnet eine Woche ohne aufgezeichnete Aktivitäten. Aus ihr folgt keine gesicherte reale Inaktivität oder bekannte Pausenursache. Die Hypothese wurde nach Kenntnis früherer Testergebnisse entwickelt; die interne Evaluation ist keine neue unabhängige Bestätigung.

## 3. Data Preparation – historische Merkmale und Zuordnung

`zero_weeks_last_4_weeks` zählt exakt die Werte gleich null je Nutzer in t-3 bis t. Vollständige und eindeutige Wochen, Kalenderzuordnung und Wertebereiche werden geprüft. Keine Imputation fehlender Historie. Aktuelle Aktivität und Vierwochenmittel sowie Folgeziel werden gegen die Wochenquelle abgeglichen. Nutzer-ID und Kalenderfelder bleiben ausschließlich Metadaten.

Unabhängige kalenderbasierte Tests prüfen sämtliche Fenster; ein Gegenfaktualtest ändert spätere Wochen und bestätigt unveränderte frühere Eingänge. Fehlende/doppelte Wochen, falsche Kalender und widersprüchliche alte Merkmale führen zum Abbruch.

## 4. Modeling – tatsächliche Durchführung

| Fold | Training t | Training Ziele | Validierung t | Validierung Ziele | Fälle Training / Validierung |
| --- | --- | --- | --- | --- | --- |
| 1 | 4–9 | 5–10 | 10–13 | 11–14 | 600 / 400 |
| 2 | 4–13 | 5–14 | 14–17 | 15–18 | 1000 / 400 |
| 3 | 4–17 | 5–18 | 18–21 | 19–22 | 1400 / 400 |

Beide Regressionen werden je Fold neu trainiert: sechs Fits je vollständigem Experimentlauf. Innerhalb jedes Validierungsblocks bleiben die Koeffizienten unverändert. Bereits beobachtete Wochen werden später als Eingänge verwendet; es handelt sich um rollierende Einwochenprognosen. Trainingziele sind beim ersten Prognosezeitpunkt vollständig bekannt. Kein zufälliger Zeilensplit und kein unnötiger Abstand für zulässige historische Fensterüberlappung.

OLS verwendet die bisherigen Parameter einschließlich Intercept, ohne Skalierung und mit einem numerischen Thread. Matrixrang und Parameter werden je Fold gegen eine unabhängige numpy.linalg.lstsq-Lösung geprüft. Die Parameter aller sechs Modelle, Feature-Korrelationen und Konditionszahlen sind gespeichert. Alle Designmatrizen haben vollen Rang. Kein Koeffizientenvorzeichen wird erzwungen.

Nullwochen-Koeffizienten der erweiterten Regression: Fold 1: 0.00327359; Fold 2: 0.05340218; Fold 3: 0.01897643.

## 5. Evaluation – tatsächlich gemessene Ergebnisse

Jedes Verfahren wird auf denselben 1.200 unterschiedlichen Nutzerwochen bewertet. Die 3.600 Prognosezeilen enthalten drei Verfahren pro Fall. Fehlerdefinition: Prognose minus Ziel. Einheit: Aktivitäten pro Nutzerwoche.

### Gesamtvergleich

| model | n | mae | rmse | mean_signed_error | negative_predictions |
| --- | --- | --- | --- | --- | --- |
| linear_2 | 1200 | 1.522613 | 1.962287 | -0.068672 | 0 |
| linear_3 | 1200 | 1.523105 | 1.962666 | -0.068500 | 0 |
| persistence | 1200 | 1.729167 | 2.365551 | -0.029167 | 0 |

### Kennzahlen je Fold

| fold | model | n | mae | rmse | mean_signed_error | negative_predictions |
| --- | --- | --- | --- | --- | --- | --- |
| 1 | linear_2 | 400 | 1.462700 | 1.904902 | -0.122422 | 0 |
| 1 | linear_3 | 400 | 1.462623 | 1.904769 | -0.122360 | 0 |
| 1 | persistence | 400 | 1.607500 | 2.197157 | -0.052500 | 0 |
| 2 | linear_2 | 400 | 1.528382 | 1.965926 | -0.053228 | 0 |
| 2 | linear_3 | 400 | 1.530127 | 1.967481 | -0.050887 | 0 |
| 2 | persistence | 400 | 1.812500 | 2.445915 | 0.007500 | 0 |
| 3 | linear_2 | 400 | 1.576756 | 2.014496 | -0.030366 | 0 |
| 3 | linear_3 | 400 | 1.576566 | 2.014211 | -0.032253 | 0 |
| 3 | persistence | 400 | 1.767500 | 2.444893 | -0.042500 | 0 |

### Historische und zukünftige Nullwochen

| model | grouping | group | n | mae | rmse | mean_signed_error | negative_predictions |
| --- | --- | --- | --- | --- | --- | --- | --- |
| linear_2 | actual_target | actual_zero | 259 | 1.708690 | 1.899720 | 1.708690 | 0 |
| linear_2 | actual_target | actual_positive | 941 | 1.471397 | 1.979161 | -0.557872 | 0 |
| linear_2 | zero_weeks_last_4_weeks | 0 | 614 | 1.695847 | 2.130539 | -0.006210 | 0 |
| linear_2 | zero_weeks_last_4_weeks | 1 | 293 | 1.507806 | 1.945522 | -0.100490 | 0 |
| linear_2 | zero_weeks_last_4_weeks | 2 | 173 | 1.275588 | 1.738826 | -0.285892 | 0 |
| linear_2 | zero_weeks_last_4_weeks | 3 | 88 | 1.105844 | 1.408155 | -0.009698 | 0 |
| linear_2 | zero_weeks_last_4_weeks | 4 | 32 | 0.815832 | 0.919125 | 0.036328 | 0 |
| linear_3 | actual_target | actual_zero | 259 | 1.713798 | 1.900893 | 1.713798 | 0 |
| linear_3 | actual_target | actual_positive | 941 | 1.470619 | 1.979330 | -0.559058 | 0 |
| linear_3 | zero_weeks_last_4_weeks | 0 | 614 | 1.695425 | 2.132272 | -0.016780 | 0 |
| linear_3 | zero_weeks_last_4_weeks | 1 | 293 | 1.507920 | 1.945838 | -0.102556 | 0 |
| linear_3 | zero_weeks_last_4_weeks | 2 | 173 | 1.275566 | 1.733843 | -0.271550 | 0 |
| linear_3 | zero_weeks_last_4_weeks | 3 | 88 | 1.114474 | 1.408622 | 0.025338 | 0 |
| linear_3 | zero_weeks_last_4_weeks | 4 | 32 | 0.817751 | 0.915107 | 0.090626 | 0 |
| persistence | actual_target | actual_zero | 259 | 1.204633 | 1.949161 | 1.204633 | 0 |
| persistence | actual_target | actual_positive | 941 | 1.873539 | 2.467859 | -0.368757 | 0 |
| persistence | zero_weeks_last_4_weeks | 0 | 614 | 2.001629 | 2.580622 | 0.340391 | 0 |
| persistence | zero_weeks_last_4_weeks | 1 | 293 | 1.651877 | 2.347026 | -0.238908 | 0 |
| persistence | zero_weeks_last_4_weeks | 2 | 173 | 1.369942 | 2.012964 | -0.641618 | 0 |
| persistence | zero_weeks_last_4_weeks | 3 | 88 | 1.159091 | 1.745123 | -0.454545 | 0 |
| persistence | zero_weeks_last_4_weeks | 4 | 32 | 0.718750 | 1.159202 | -0.718750 | 0 |

Es gibt 259 tatsächliche Nullziele und 941 positive Ziele im Validierungsbestand. Die Nullziel-MAE verschlechtert sich durch das Zusatzmerkmal von 1,708690 auf 1,713798; bei positiven Zielen sinkt der MAE geringfügig von 1,471397 auf 1,470619. Die Zukunftsgruppen sind ausschließlich nachträgliche Diagnosen und keine bei Prognose bekannten Selektionsregeln.

Die historischen Nullzahlen 0/1/2/3/4 haben 614/293/173/88/32 Validierungsfälle. Unterschiede zwischen diesen Gruppen beschreiben unterschiedliche Fälle und sind keine kausalen Effekte zusätzlicher Nullwochen. Besonders die Gruppe mit vier Nullen ist klein. Die vollständige Tabelle berichtet MAE, RMSE, vorzeichenbehafteten Fehler und Fallzahlen für alle Verfahren und Gruppen.

### Vorab festgelegte Modellentscheidung

Die Erweiterung gewinnt beim MAE in Fold 1 und 3 geringfügig, verliert jedoch stärker in Fold 2. Ihr gepoolter MAE ist um 0,0004926958533926218 höher. Damit ist die UND-Regel nicht erfüllt: **Erweiterung nicht übernehmen; bisherige Zwei-Merkmals-Struktur beibehalten.** Der gepoolte RMSE verschlechtert sich ebenfalls geringfügig. Keine Signifikanz oder praktische Gleichwertigkeit behauptet. Die zusätzliche historische Information allein garantiert keinen Prognosenutzen.

### Technische Prüfung und Reproduktion

- Acht neue Tests in `tests/test_cycle2.py`: Kalenderreferenz, Zukunftsinvarianz/Nutzerisolation, ungültige Historie, Kalender/alte Merkmale, Wochenfolds/Labelverfügbarkeit, Eingabezugriffssperre, sechs korrekte Fits samt Kennzahlen/Entscheidung, Überschreibschutz. Alle bestanden.
- Sieben bestehende Tests in `tests/test_data_preparation_regression.py`: alle bestanden; ausschließlich Aufbereitungsprüfungen, kein Modellfit.
- Neues Experiment zweimal vollständig ausgeführt. Zweiter Lauf mit identischen Ausgabe-Bytes erfolgreich; abweichende vorhandene Dateien würden abgewiesen. Neue Vergleichstests führen zusätzliche isolierte Fits im Speicher durch.
- Keine vollständige Legacy-Suite ausgeführt: sie enthält andere Trainingsläufe und alte Testauswertungen außerhalb des freigegebenen Experiments.
- Prüfsummen sämtlicher vor Beginn versionierter Dateien gegen den Arbeitsbeginn geprüft; keine Änderung. Prüfbericht unter `outputs/cycle2/integrity_verification.json`.

Reproduktion vom Repository-Stamm mit der dokumentierten Umgebung aus `requirements-modeling.txt`:

```bash
python -m unittest discover -s tests -p 'test_cycle2.py' -v
python -m unittest discover -s tests -p 'test_data_preparation_regression.py' -v
python src/cycle2_compare.py
```

`run_manifest.json` enthält Softwareversionen, Quell- und Codehash, Basiscommit und Hashes der Experimentartefakte. Identische numerische/bytegenaue Ergebnisse wurden in dieser Umgebung geprüft; plattformübergreifende Bytegleichheit ist nicht garantiert. Die Basiscommit-ID bezeichnet den Ausgangsstand; der neue Skriptinhalt wird separat durch seinen Hash identifiziert.

## 6. Deployment – Forschungsübergabe und nächster Schritt

Der Forschungsstand wird mit isolierten CSV-/JSON-Artefakten, gespeicherten Foldparametern, Tests und diesem Bericht übergeben. Die Foldmodelle sind über Parameter und feste Feature-Reihenfolge nachvollziehbar; es wird kein neues produktives Modell ausgerollt. Kein erneuter Fit auf allen 1.800 Fällen ist erforderlich, da die bisherige Struktur ausgewählt bleibt und das vorhandene Modell erhalten wird. Das Dashboard bleibt unverändert. Kein Merge und keine Veröffentlichung durchgeführt.

Nächster Schritt ist die fachliche Abnahme und Übernahme dieses negativen Ergebnisses in Projektbericht und Präsentation: ein vollständiger zweiter Zyklus muss keine Verbesserung liefern. Eine weitere Untersuchung benötigt eine neue vorab begründete Hypothese und ein neues Validierungsprotokoll; für unabhängige Bestätigung sind neue zurückgehaltene Daten nötig.

## Wissenschaftliche Grenzen

Synthetische V2-Daten, bekannte Nutzer und kurzer Zeitraum; keine Aussage über neue reale Nutzer. Wiederholte Nutzer, gemeinsame Wochen und überlappende Fenster erzeugen Abhängigkeiten. Die 1.200 Fälle sind keine 1.200 unabhängigen Experimente. Spätere Folds dürfen frühere Validierungsziele als inzwischen bekannte Trainingsdaten verwenden; die Folds sind daher ebenfalls nicht unabhängig. Keine unkritischen IID-Signifikanztests durchgeführt. OLS bildet Zähldaten und Nullprozesse nur begrenzt ab. Die Diagnose am alten Testset hat die Hypothese angeregt, weshalb die interne Evaluation keine unberührte externe Testleistung darstellt.
