# MOVA – Kontrollierte Präferenziteration V1 / V2

## Ziel und Baseline

Zielgruppe: aktive Smartwatch-Nutzer mit unterschiedlichen sportlichen Schwerpunkten; breite und konzentrierte Repertoires sollen nebeneinander möglich bleiben. Keine Zielquote für Sportartenvielfalt und keine vorgegebenen Cluster.

Die historische V1 wurde unverändert unter `v1_snapshot/` gesichert, einschließlich Generator, Konfiguration, vorhandenen Qualitätsberichten und Abbildungen. SHA256.json enthält die Prüfsummen von 31 gesicherten Dateien. Ursprüngliche Parameter: 100 Nutzer, 26 Wochen vom 05.01.–05.07.2026, Seed 42, sieben interne Profile, individuelle Gewichte = Profilgewicht × Lognormal(0; 0,7), Exponent implizit 1,0. Grundraten 0,4–2 bzw. 1,3–5, vier Trendmechanismen, Poisson-Zählung, AR(1)-Rauschen, Pausenstart 4,5 %, Wochenobergrenze 10. Vollständige Parameter stehen im gesicherten Generator und simulation_config.md.

## Kontrolliertes Design

Die einzige fachliche Änderung: `weights = [weight ** exponent for weight in weights]` nach der individuellen Gewichterzeugung. Exponent V2 = 1,3. Die gewichtete Auswahl normalisiert implizit durch die Gewichtssumme. Alle Gewichte bleiben positiv; keine Sportart wird ausgeschlossen. Trends und Häufigkeitsparameter bleiben unverändert.

Zusätzliche technische Änderung: getrennte Random-Instanzen. Master-Seed bleibt 42. Abgeleitete Seeds: Häufigkeit/Trend/Pausen 42, Profile 43, Präferenzfaktoren 44, Sportartenwahl 45, Dauer 46, Distanz 47, Interessen 48, Wochentage 49. Profil- und Präferenzzuweisungen bleiben pro Nutzer in Kontrolle und V2 gleich. Dauer und Distanz werden getrennt, weil nur Distanzsportarten entsprechende Ziehungen auslösen. Identische numerische Seeds in separaten ursprünglichen Angebots- und Profilgeneratoren stellen keine fachliche Verbindung her; Angebote werden unverändert kopiert.

**Die historische V1 ist nicht mit dem umgestellten Zufallsstrom identisch.** Deshalb gibt es drei Spalten: V1 original, technische Kontrolle mit Exponent 1,0 und getrennten Zufallsquellen, V2 mit Exponent 1,3 und denselben getrennten Quellen. V1→V2 beschreibt den Gesamtwechsel; nur Kontrolle→V2 isoliert hier den Exponenteneffekt. Der Kontrolllauf ist keine dritte fachliche Anpassungsvariante.

Die Sportartenwahl verwendet bei Kontrolle und V2 dieselben Zufallszahlen; durch geänderte Intervallgrenzen können dennoch einzelne Aktivitäten in beide Richtungen wechseln. Daher sind beobachtete Nutzerkennzahlen nicht zwingend für jeden Nutzer monoton. Zweimalige Generierung jeder Variante im Speicher wurde auf vollständige Gleichheit geprüft. Neue Dateien werden nur angelegt; bei Wiederholung werden ausschließlich identische Inhalte akzeptiert.

## Tatsächlich berechnete Ergebnisse

| index | V1_original | Kontrolle_1.0 | V2_1.3 |
| --- | --- | --- | --- |
| Nutzer_1_Sportarten | 0.000 | 0.000 | 0.000 |
| Nutzer_2_Sportarten | 0.000 | 0.000 | 0.000 |
| Nutzer_3_Sportarten | 0.000 | 0.000 | 0.000 |
| Nutzer_4_Sportarten | 0.000 | 0.000 | 2.000 |
| Nutzer_5_Sportarten | 2.000 | 6.000 | 12.000 |
| Nutzer_6_Sportarten | 8.000 | 14.000 | 15.000 |
| Nutzer_7_Sportarten | 31.000 | 22.000 | 31.000 |
| Nutzer_8_Sportarten | 59.000 | 58.000 | 40.000 |
| Mittlere_Sportartenanzahl | 7.470 | 7.320 | 6.950 |
| Top2_Mittel_% | 59.410 | 57.611 | 64.117 |
| Top2_Median_% | 59.016 | 58.236 | 63.733 |
| Top2_Min_% | 32.653 | 38.168 | 41.221 |
| Top2_Max_% | 86.792 | 82.143 | 91.860 |
| Aktivitaeten | 6665.000 | 6465.000 | 6465.000 |
| Aktivitaeten_pro_Nutzer_Woche | 2.563 | 2.487 | 2.487 |
| Nullwochen | 545.000 | 558.000 | 558.000 |
| Nullwochen_% | 20.962 | 21.462 | 21.462 |
| Max_Aktivitaeten_pro_Woche | 10.000 | 10.000 | 10.000 |

Top-2-Anteil: Summe der zwei häufigsten Sportarten eines Nutzers geteilt durch seine gesamte Aktivitätszahl. Mittelwerte gewichten Nutzer gleich. Nullwochen werden im vollständigen 100×26-Raster berücksichtigt. Alle Sportartenanzahlen von 1 bis 8 werden ausgewiesen, damit neu auftretende kleinere Repertoires nicht fehlen.

### Sportartenverteilung

| ('sport_type', '') | ('V1_original', 'Anzahl') | ('V1_original', 'Anteil_%') | ('Kontrolle_1.0', 'Anzahl') | ('Kontrolle_1.0', 'Anteil_%') | ('V2_1.3', 'Anzahl') | ('V2_1.3', 'Anteil_%') |
| --- | --- | --- | --- | --- | --- | --- |
| Running | 974 | 14.614 | 996 | 15.406 | 1005 | 15.545 |
| Cycling | 1207 | 18.110 | 1068 | 16.520 | 1128 | 17.448 |
| Strength | 873 | 13.098 | 814 | 12.591 | 851 | 13.163 |
| Swimming | 584 | 8.762 | 622 | 9.621 | 592 | 9.157 |
| Walking | 1109 | 16.639 | 1100 | 17.015 | 1125 | 17.401 |
| Hiking | 863 | 12.948 | 884 | 13.674 | 917 | 14.184 |
| Tennis | 525 | 7.877 | 493 | 7.626 | 434 | 6.713 |
| Padel | 530 | 7.952 | 488 | 7.548 | 413 | 6.388 |

Häufigste Sportart V2: Cycling (17.45 %); seltenste: Padel (413 Aktivitäten, 6.39 %). Kein globaler Mehrheitsanteil; alle acht Sportarten bleiben tatsächlich vertreten.

### Nachgewiesener Exponenteneffekt im gepaarten Vergleich

- Nutzer mit acht Sportarten: 58 → 40.
- Mittlere Sportartenanzahl: 7.320 → 6.950.
- Mittlerer Top-2-Anteil: 57.611 % → 64.117 %; Differenz 6.507 Prozentpunkte.
- Individueller Top-2-Anteil: 89 höher, 1 niedriger, 10 gleich.
- Individuelle Sportartenanzahl: 6 höher, 34 niedriger, 60 gleich.
- Nutzerinteressen, sämtliche 2.600 Wochenzählungen, Trendzuweisungen sowie IDs/Nutzer/Datum jeder Aktivität sind zwischen Kontrolle und V2 exakt identisch geprüft. Der Exponent verändert hier keine Aktivitätshäufigkeit.

## Plausibilität, Nebenwirkungen und Grenzen

Die sieben Profilvorlagen und individuellen lognormalen Abweichungen bleiben erhalten. Unterschiedliche beobachtete Sportanteile bestehen weiterhin; keine Nutzerprofile werden als Modelllabels gespeichert. Häufigkeiten und Trends sind bewusst unverändert modelliert. Die Verstärkung bildet klarere persönliche Schwerpunkte ab, erhält aber seltene Sportarten und Überschneidungen.

Eine stärkere Konzentration ist eine fachlich motivierte Annahme, kein empirischer Realismusnachweis. Der niedrigere Anteil von Nutzern mit acht Sportarten darf nicht allein als Qualitätsmaß dienen. Seltene Sportarten können Anteile verlieren. Mehr Konzentration kann künstlich klarere Gruppen begünstigen; späteres K-Means darf nicht als Bestätigung der Generatorannahme interpretiert werden. Unverändert positive Gewichte erlauben langfristig weiterhin große Repertoires.

Dauern und Distanzen ändern sich mit dem Sportartenmix trotz unveränderter Parameter; aggregierte Trainingsminuten können daher abweichen. Der technische Wechsel der Zufallsquellen verändert gegenüber historischer V1 zusätzlich Nutzerzuweisungen, Zeitreihen und Gesamtzahlen. Diese Unterschiede werden nicht als Wirkung des Exponenten ausgegeben. Ein Seed und 100 Nutzer zeigen nur diesen konkreten Simulationsfall; keine statistische oder empirische Validierung und keine Garantie für andere Seeds.

## Technische Qualität und Integrität

V1, Kontrolle und V2 bestehen die vorhandenen technischen CSV-Prüfungen: 100 eindeutige Nutzer, 26 Wochen, 2.600 vollständige Nutzerwochen, Abgleich der Aktivitäten, IDs, Referenzen, Datumswerte, acht Sportarten, sportartspezifische Dauer-/Distanzgrenzen, nicht anwendbare Distanzen, Interessen und 30 fiktive Angebote. V1-Snapshot und Originaldateien sind per SHA-256 unverändert geprüft. Nur das CRISP-DM-Protokoll darf um den tatsächlichen Iterationseintrag ergänzt werden; sein ursprünglicher Inhalt bleibt erhalten.

## Empfehlung und weitere Verwendung

**B – V2 übernehmen**, als fachlich bevorzugte Version für die nächste Datenaufbereitung nach Prüfung dieses Vergleichs. Der gepaarte Vergleich zeigt die gewünschte moderate Verstärkung persönlicher Schwerpunkte bei identischen Häufigkeiten und erhaltenen Auswahlmöglichkeiten. Es gibt keinen Nachweis einer besseren ML-Leistung.

V2 bleibt vorerst unter `v2_exponent_1_3/`; die historischen Standarddateien und der ursprüngliche Generator werden nicht ersetzt. Bei der späteren AP-4-Umsetzung muss die verwendete Datenversion ausdrücklich ausgewählt werden. Nullwochen erhalten, nicht anwendbare Distanzen bewusst behandeln, aggregierte Merkmale skalieren und mögliche Redundanzen prüfen. Kein Modell wurde trainiert, kein Commit oder Pull Request erstellt.

## Ausführung und Artefakte

`python src/simulation_preference_comparison.py` aus dem Worktree. Python 3.12.14, pandas 2.2.3, NumPy 2.3.5, Matplotlib 3.10.8. Neue CSVs liegen jeweils in den Variantenverzeichnissen. Vergleichsdateien: comparison_metrics.csv, sport_distribution_comparison.csv, user_metrics_comparison.csv, paired_user_changes.csv. Grafiken: figures/diversity_and_top2_comparison.png und figures/sports_and_weekly_comparison.png. Die Top-2-Kurve ist eine kumulierte Verteilung: Sie zeigt den Anteil der Nutzer bis zum jeweiligen Top-2-Wert; eine Verschiebung nach rechts bedeutet stärkere Konzentration.
