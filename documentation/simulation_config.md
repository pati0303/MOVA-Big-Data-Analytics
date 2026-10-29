# MOVA – Aktive Simulationskonfiguration V2

## Verbindliche Datenversion und Ausführung

Das Projektteam hat V2 mit Präferenzexponent 1,3 verbindlich als Datengrundlage der folgenden Arbeitspakete ausgewählt. Die aktive Quelle besteht aus:

- data/raw/activities_simulated.csv
- data/raw/users_simulated.csv
- data/raw/offers_simulated.csv

Die passende vollständige Nutzer-Wochen-Kontrolle steht unter outputs/tables/simulation_weekly_check.csv. Die Datei documentation/active_data_version.json hält Version, Quellpfade und SHA-256-Prüfsummen fest.

**Aktive Daten reproduzieren:** `python src/data_generation.py` im Repository-Verzeichnis. Dieser Standardaufruf erzeugt ausschließlich V2, überschreibt die aktiven Daten und ihre Wochenkontrolle reproduzierbar und schreibt outputs/tables/simulation_report_v2.md. Er benötigt Python >= 3.10 und nur die Standardbibliothek. Die freigegebenen Gesamtzahlen werden nach der CSV-Prüfung ausdrücklich kontrolliert. Reproduzierbarkeit wurde mit Python 3.12.14 nachgewiesen; andere Python-Versionen sind nicht als bytegleich garantiert.

src/data_generation.py delegiert die Generierung an src/simulation_v2.py mit festem Exponenten 1,3. Dieses Modul enthält unverändert die bereits getestete getrennte Generatorlogik. Es gibt keinen V1-Standardmodus. Der historische V1-Generator bleibt ausschließlich im Snapshot erhalten.

## Einstellungen und Zufallsquellen

- Master-Seed: 42; 100 Nutzer; 26 vollständige Montag-bis-Sonntag-Wochen.
- Zeitraum: 05.01.2026 bis einschließlich 05.07.2026, ISO-KW 02–27.
- Acht Sportarten: Running, Cycling, Strength, Swimming, Walking, Hiking, Tennis, Padel.
- Sieben überlappende interne Profile, keine gespeicherten Clusterlabels.
- Ausgangsgewicht je Sportart: Profilgewicht × lognormaler individueller Faktor mit Log-Mittel 0 und Log-SD 0,7.
- Einzige fachliche Änderung gegenüber V1: jedes individuelle Gewicht wird anschließend mit 1,3 potenziert. Die Auswahlwahrscheinlichkeit entspricht dem neuen Gewicht geteilt durch die Gewichtssumme. Alle Sportarten bleiben möglich; keine festen Repertoiregrenzen.

Die technische Trennung verwendet unabhängige Random-Instanzen mit festen abgeleiteten Seeds:

| Zweck | Seed |
|---|---:|
| Grundhäufigkeit, Trend, Wochenrauschen und Pausen | 42 |
| Nutzerprofil | 43 |
| Individuelle Präferenzfaktoren | 44 |
| Auswahl der Sportart | 45 |
| Dauer und individueller Dauerfaktor | 46 |
| Distanz/Geschwindigkeit | 47 |
| Freiwillige Interessen | 48 |
| Wochentag | 49 |

Der unveränderte Angebotskatalog verwendet wie bisher Seed 43 in einer eigenen Random-Instanz; er beeinflusst den Profilgenerator nicht. Die Zahlen 43–49 sind feste Ableitungen vom Master-Seed, keine neuen frei gewählten Experiment-Seeds.

## Unveränderte fachliche Annahmen

Grundraten: gleichverteilt 0,4–2 Aktivitäten/Woche für Gelegenheitsaktive, sonst 1,3–5. Die vier Trendmechanismen steigend, konstant, sinkend und schwankend bleiben gleichwahrscheinlich. Trendstärke 0,2–0,55, Sinusperiode 6–12 Wochen, AR(1)-Wochenrauschen mit Faktor 0,65 und normaler Störung SD 0,2. Wochenrate wird auf 0,1–8 begrenzt, Poisson-Zahl auf maximal zehn Aktivitäten abgeschnitten. Pausenstart 4,5 % pro Woche ohne laufende Pause; Länge 1/2/3 Wochen mit 50/25/25 %. Zufällige Nullwochen sind zusätzlich möglich. Maximal zwei Aktivitäten/Tag; Wochenendgewicht 1,3 gegenüber 1 unter der Woche.

Dauern werden lognormal gezogen (Log-SD 0,3), mit individuellem Faktor 0,75–1,3. Geschwindigkeiten werden normalverteilt gezogen und begrenzt. Distanzen = Minuten/60 × Geschwindigkeit, auf zwei Nachkommastellen gerundet; Dauern auf eine Nachkommastelle. Grenzen und Verteilungsparameter bleiben unverändert:

| Sport | Dauermedian min | Dauergrenzen min | Geschwindigkeit Mittel ± SD km/h | Grenzen km/h |
|---|---:|---|---|---|
| Running | 40 | 10–150 | 9 ± 1,8 | 5–16 |
| Cycling | 65 | 15–240 | 20 ± 4 | 8–35 |
| Strength | 50 | 15–120 | entfällt | entfällt |
| Swimming | 35 | 10–100 | 2 ± 0,4 | 0,8–3,5 |
| Walking | 45 | 10–180 | 4,5 ± 0,7 | 2,5–6,5 |
| Hiking | 120 | 30–360 | 3,8 ± 0,8 | 1,5–6 |
| Tennis | 65 | 20–180 | entfällt | entfällt |
| Padel | 65 | 20–150 | entfällt | entfällt |

Fehlende Distanz bei Strength, Tennis und Padel bedeutet nicht anwendbar. Interessen werden unabhängig als Bernoulli-Werte mit Wahrscheinlichkeiten 65/50/40/60 % für Sport/Outdoor/Wellness/Freizeit erzeugt; sie sind keine direkten K-Means- oder Regressionsmerkmale. 30 ausdrücklich fiktive Angebote umfassen Sport, Outdoor, Wellness und Freizeit, feste Preise 10–250 Euro und Rabatte aus 5/10/15/20/25/30 %.

## Historische Versionen, Befunde und Entscheidung

V1 bleibt vollständig unter outputs/simulation_comparison/v1_snapshot erhalten. SHA256.json enthält die Prüfsummen der 31 ursprünglichen Dateien. Die damalige vollständige Konfiguration und das damalige Skript liegen dort ebenfalls. Die ursprünglichen V1-Berichte unter outputs/tables/simulation_report.md und simulation_quality_report.md bleiben historische Ergebnisse; ihre Zahlen dürfen nicht als Beschreibung der aktiven V2 gelesen werden. Der alte Qualitätsanalyseaufruf ist bewusst auf die V1-Snapshot-Daten und historische Ergebnisse festgelegt.

| Kennzahl | Historische V1 | Getrennte Kontrolle 1,0 | Aktive V2 1,3 |
|---|---:|---:|---:|
| Aktivitäten | 6.665 | 6.465 | 6.465 |
| Nullwochen | 545 | 558 | 558 |
| Nutzer mit 8 Sportarten | 59 | 58 | 40 |
| Mittlere Sportartenanzahl | 7,47 | 7,32 | 6,95 |
| Top-2-Mittel | 59,41 % | 57,61 % | 64,12 % |
| Top-2-Median | 59,02 % | 58,24 % | 63,73 % |

Kontrolle→V2 isoliert den Exponenteneffekt bei identischen 2.600 Wochenzählungen. V1→V2 enthält zusätzlich Änderungen durch den umgestellten Zufallsstrom. Trends und Häufigkeitsparameter wurden nicht verändert. V2 wurde ausgewählt, weil individuelle Schwerpunkte deutlicher werden und alle Sportarten sowie natürliche Überschneidungen erhalten bleiben. Die ursprüngliche Bewertung und die gemessenen Vergleichsergebnisse bleiben im comparison_report.md unverändert nachvollziehbar.

Vergleich reproduzieren: `python src/simulation_preference_comparison.py`. Dieser Aufruf liest historische V1 explizit aus dem Snapshot, rekonstruiert getrennte Kontrolle und V2 separat und akzeptiert vorhandene Vergleichsdateien nur bei identischem Inhalt. Aktive Rohdaten werden dabei nicht verändert. Relevante Kennzahlen und Grafiken bleiben in Git; zusätzliche identische V2-/Kontroll-Rohdatenkopien und ihre Wochenkontrollen bleiben lokal erhalten, werden aber nicht zusätzlich versioniert. Auf einem frischen Checkout werden sie bei diesem Aufruf wieder erstellt.

## Einschränkungen und nächste Arbeitspakete

Synthetische Annahmen sind keine empirischen Befunde. Ein Seed und 100 Nutzer garantieren keine allgemeine Wirkung. Wetter, Saison, reale Messfehler und Verletzungen fehlen; Grenzwerte können Randhäufungen erzeugen. Seltene Sportarten können Anteile verlieren. Positive Gewichte erlauben weiterhin breite Repertoires. Klarere Sportanteile belegen weder echte Cluster noch bessere Prognosegüte.

AP 4 verwendet ausschließlich die aktiven data/raw-Pfade, erhält Nullwochen, behandelt nicht anwendbare Distanzen bewusst und prüft Skalierung sowie redundante Merkmale. Es wurde noch keine vollständige Modellaufbereitung durchgeführt und kein Modell trainiert. Die erste tatsächliche CRISP-DM-Iteration und ihre abschließende Annahme von V2 stehen in crisp_dm_log.md und decisions.md.
