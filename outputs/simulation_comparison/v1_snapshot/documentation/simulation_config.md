# MOVA – Einstellungen der ersten synthetischen Simulation (AP 2.3)

## Zweck und Ausführung

Diese Simulation liefert konstruierte Ausgangsdaten für CRISP-DM 2.1 Collect Initial Data und 3.3 Construct Data. Sie bildet Annahmen ab, keine gemessene Bevölkerung. Erste synthetische Datensimulation – noch keine vollständige Data Preparation oder Modellierung durchgeführt.

Aus dem Repository-Verzeichnis: `python src/data_generation.py`. Benötigt wird Python ab 3.10, ohne zusätzliche Pakete. Das Skript überschreibt seine vier CSV-Dateien und den Ergebnisbericht, liest die CSVs zur Qualitätsprüfung wieder ein und bricht bei einem Fehler mit `ValueError` ab. Der Bericht wird erst nach erfolgreicher Kontrolle erstellt. Die Konfiguration in dieser Datei ist eine verständliche Dokumentation; die ausführbaren Parameter stehen am Anfang des Skripts, nicht in einer separat eingelesenen Konfigurationsdatei.

- 100 Nutzer: U001 bis U100; IDs werden in Aktivitäten mehrfach referenziert.
- 05.01.2026 bis einschließlich 05.07.2026: 182 Tage, 26 vollständige Wochen, ISO-KW 02–27.
- Lokaler Zufallsgenerator `random.Random(42)`; Angebote verwenden den festen abgeleiteten Seed 43, damit ihr Zufall unabhängig bleibt.
- Identische Skriptversion und Python-Laufzeit erzeugen dieselben Ergebnisse. Python-Version bei Vergleichen festhalten; eine bitgenaue Garantie über unterschiedliche Python-Versionen besteht nicht.

## Nutzer und Sportarten

Jeder Nutzer erhält intern eines von sieben gleichwahrscheinlichen Profilen. Das sind Simulationshilfen, keine empirischen Gruppen oder späteren Clusterlabels. Die Zahlen in der Tabelle sind relative Auswahlgewichte in der Reihenfolge der Sportarten. Zum Beispiel bedeutet 7 gegenüber 2 eine stärkere Vorliebe, keine feste Zahl von Aktivitäten.

| Profil | Running | Cycling | Strength | Swimming | Walking | Hiking | Tennis | Padel |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| Laufaffin | 7 | 2 | 3 | 1 | 3 | 2 | 1 | 1 |
| Radaffin | 2 | 7 | 2 | 1 | 2 | 3 | 1 | 1 |
| Kraftorientiert | 2 | 1 | 7 | 1 | 3 | 1 | 2 | 2 |
| Schwimmorientiert | 2 | 2 | 2 | 7 | 2 | 1 | 1 | 1 |
| Outdoororientiert | 3 | 4 | 1 | 1 | 5 | 7 | 1 | 1 |
| Multisport | 3 | 3 | 3 | 3 | 3 | 2 | 3 | 3 |
| Gelegenheitsaktiv | 2 | 2 | 1 | 1 | 6 | 3 | 2 | 2 |

Jedes Gewicht wird zusätzlich mit einer individuellen lognormalverteilten Zahl multipliziert: Log-Mittelwert 0, Log-Standardabweichung 0,7. Diese Verteilung erzeugt positive, oft mäßige und gelegentlich größere Abweichungen. Anschließend wird jede Sportart proportional zu den Gewichten gezogen. Alle Sportarten bleiben möglich; Profile überlappen. Vorlieben bleiben für einen Nutzer im Zeitraum gleich.

Die Grundrate wird gleichverteilt aus 0,4–2 Aktivitäten/Woche für Gelegenheitsaktive und 1,3–5 für alle übrigen gezogen. Gleichverteilt bedeutet: Jeder Wert im Intervall ist gleich wahrscheinlich. Das sind erwartete Grundraten vor Trend, Pausen und Zufall, keine garantierten Wochenzahlen.

## Wochen, Trends und Trainingspausen

Jeder Nutzer erhält unabhängig einen der vier gleichwahrscheinlichen Mechanismen steigend, konstant, sinkend oder schwankend. Die tatsächlichen Häufigkeiten dieser Zuweisungen stehen ausschließlich aggregiert im Bericht.

1. Die individuelle Trendstärke A liegt gleichverteilt zwischen 0,2 und 0,55. Mit t = Woche/25 wächst der Trendfaktor von 1−A auf 1+A oder fällt umgekehrt. Beim konstanten Mechanismus ist er 1. Schwankende Verläufe folgen 1 + A × sin(2π × Woche/Periode + Phase), mit einer individuellen Periode von 6–12 Wochen und einer Phase von 0–2π.
2. Ein zeitlich zusammenhängendes Zufallssignal überlagert den Trend: neuer Zustand = 0,65 × voriger Zustand + normalverteilte Störung (Mittel 0, Standardabweichung 0,2). Startwert 0, Begrenzung auf −0,7 bis 0,7. Ein Teil der Abweichung bleibt damit in der Folgewoche erhalten. Diese einfache AR(1)-Logik ist ausschließlich ein Generator, kein trainiertes Prognosemodell.
3. Wochenrate = Grundrate × Trendfaktor × exp(Zustand), begrenzt auf 0,1–8. Daraus wird eine Poisson-Zahl gezogen: eine Verteilung nichtnegativer Anzahlen, deren Mittelwert die jeweilige Rate ist. Auch ohne Pause kann eine Null auftreten. Maximal zehn Aktivitäten werden zugelassen; das Abschneiden verändert die theoretische Poisson-Verteilung.
4. In jeder Woche ohne laufende Pause beginnt mit 4,5 % Wahrscheinlichkeit eine vollständige Pause. Sie dauert 1, 2 oder 3 Wochen mit Wahrscheinlichkeiten 50 %, 25 %, 25 %. Pausen am Beobachtungsende werden abgeschnitten. Währenddessen entstehen keine Aktivitäten. Die 4,5 % sind eine Startwahrscheinlichkeit, nicht der Anteil aller Nullwochen.
5. Aktivitäten werden auf Wochentage verteilt. Samstag und Sonntag erhalten jeweils Gewicht 1,3, die übrigen Tage Gewicht 1; höchstens zwei Aktivitäten pro Tag. Mehrere Einträge am selben Tag sind eigenständige Aufzeichnungen, keine doppelten IDs.

Auch die steigenden und sinkenden Grundmechanismen haben deshalb keine perfekt linearen beobachteten Verläufe. Unvorhersehbare Änderungen und externe Faktoren fehlen weiterhin; synthetische Daten können spätere Prognosegüte nicht belegen.

## Dauer und Distanz

Die Dauer wird lognormal verteilt gezogen, mit dem sportartspezifischen Basismedian mal einem festen individuellen Faktor (gleichverteilt 0,75–1,3), Log-Standardabweichung 0,3. Danach wird sie auf die Grenzen der Tabelle begrenzt und auf eine Nachkommastelle gerundet. Begrenzung bedeutet Abschneiden, keine neu gezogene, bedingte Verteilung; Randhäufungen sind möglich.

Für Distanzsportarten wird die Geschwindigkeit normalverteilt (Mittelwert und Standardabweichung SD unten) gezogen und auf ihre Grenzen begrenzt. Distanz = Dauer / 60 × Geschwindigkeit, gerundet auf zwei Nachkommastellen. Die technische Kontrolle berücksichtigt 0,0051 km Rundungstoleranz. Dies sind breite Modellannahmen und keine medizinisch oder empirisch validierten Grenzen.

| Sportart | Basismedian Dauer (min) | Dauergrenzen (min) | Geschwindigkeit Mittel ± SD (km/h) | Geschwindigkeitsgrenzen (km/h) |
|---|---:|---:|---:|---:|
| Running | 40 | 10–150 | 9 ± 1,8 | 5–16 |
| Cycling | 65 | 15–240 | 20 ± 4 | 8–35 |
| Strength | 50 | 15–120 | entfällt | entfällt |
| Swimming | 35 | 10–100 | 2 ± 0,4 | 0,8–3,5 |
| Walking | 45 | 10–180 | 4,5 ± 0,7 | 2,5–6,5 |
| Hiking | 120 | 30–360 | 3,8 ± 0,8 | 1,5–6 |
| Tennis | 65 | 20–180 | entfällt | entfällt |
| Padel | 65 | 20–150 | entfällt | entfällt |

Bei Strength, Tennis und Padel bleibt `distance_km` absichtlich leer. Das ist „für das Modell nicht benötigt“, keine gemessene Distanz von null und kein Fehler. Unabhängig von Dauer und Distanz werden keine Leistungs- oder Erfolgslabels erzeugt.

## Interessen und Angebote

Die vier freiwilligen Interessen werden unabhängig voneinander als Bernoulli-Ziehungen erzeugt: Sport mit Wahrscheinlichkeit 65 %, Outdoor 50 %, Wellness 40 %, Freizeit 60 %. Eine Bernoulli-Ziehung liefert True oder False. Alle Kombinationen einschließlich viermal False sind möglich. Interessen werden nicht aus Profilen abgeleitet und beeinflussen keine Aktivitätsrate. Sie sind für die spätere Empfehlungslogik vorgesehen, nicht als direkte Merkmale für K-Means oder Regression.

Der feste Angebotskatalog enthält acht Sport-, acht Outdoor-, sieben Wellness- und sieben Freizeitangebote: Produkte, Dienstleistungen und Veranstaltungen. Preise sind feste fiktive Annahmen zwischen 10 und 250 Euro (Preis vor Rabatt); der Rabatt wird gleichwahrscheinlich aus 5, 10, 15, 20, 25, 30 Prozent gewählt. Jeder Titel beginnt mit „FIKTIV –“. Es werden keine echten Anbieter oder verfügbaren Angebote behauptet.

## Dateien und technische Kontrolle

| Datei | Inhalt |
|---|---|
| `src/data_generation.py` | Generator, CSV-Prüfungen und Berichtsausgabe |
| `data/raw/activities_simulated.csv` | Einzelaktivitäten mit den sechs angeforderten Spalten |
| `data/raw/users_simulated.csv` | Nutzer-ID und vier boolesche Interessen |
| `data/raw/offers_simulated.csv` | 30 ausdrücklich fiktive Angebote |
| `outputs/tables/simulation_weekly_check.csv` | Vollständiges Raster mit user_id, week_start (Montag), activity_count |
| `outputs/tables/simulation_report.md` | Tatsächlich berechnete Kennzahlen und Prüfergebnis |
| `documentation/simulation_config.md` | Diese Dokumentation |

Die Wochenübersicht enthält genau 100 × 26 = 2.600 Zeilen. Eine Woche ohne Aktivität wird explizit als 0 gezählt. Sämtliche Zählungen werden gegen die erneut eingelesenen Einzelaktivitäten geprüft. Zusätzlich werden Nutzerzahl, IDs, Referenzen, Datum, Zeitraum, Sportarten, Pflichtfelder, boolesche Interessen, Dauern, Distanzen und Angebote kontrolliert. Die Prüfung der beobachteten Sportartenabdeckung und insgesamt aktiven Nutzer ist eine zusätzliche Kontrolle dieser konkreten ersten Simulation, keine erzwungene Nachgenerierung.

Der Bericht gibt die minimale und maximale Aktivitätszahl pro Nutzerwoche einschließlich Nullwochen an. Er trennt interne Mechanismen vom beobachteten Vergleich der ersten und letzten sechs Wochen. Eine Differenz größer als 0,5 gilt dort deskriptiv als steigend, kleiner als −0,5 als sinkend; der Rest hat ein ähnliches Anfangs-/Endniveau. Diese einfache Übersicht erkennt keine Schwankungsmuster und ersetzt keine Modellierung.

## Grenzen und nächster fachlicher Review

Zu prüfen sind besonders die Verteilung der Sportarten, innerhalb von Profilen überlappende Vorlieben, Nullwochen, Dauergrenzen und die Obergrenze von zehn Wochenaktivitäten. Eine Betrachtung einzelner Wochenreihen sollte klären, ob die Verläufe zum Projektziel passen. Saison, Wetter, Feiertage, Krankheit und reale Messfehler sind nicht modelliert. Keine dieser Annahmen wurde anhand realer Garmin-Daten kalibriert.

Ein fachlicher Review kann einen echten CRISP-DM-Rücksprung auslösen: Auffälligkeit festhalten, Annahme begründet ändern, erneut generieren und Ergebnisse vergleichen. Dieser Schritt steht aus. Bislang wurden nur Generierung und technische Kontrolle durchgeführt; es werden keine abgeschlossenen fachlichen Iterationen behauptet.

Hinweis zum vorgefundenen Stand: Der lokale Checkout enthielt bei Arbeitsbeginn nur README und .gitignore im Initial-Commit. Die in der Anfrage erwähnte, über PR #1 integrierte AP-1-Struktur war lokal nicht vorhanden. Bestehende Dateien wurden nicht verändert; die benötigten Verzeichnisse wurden ergänzt. Es wurde kein Pull Request erstellt.
