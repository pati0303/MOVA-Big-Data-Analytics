# CRISP-DM-Protokoll

Dieses Protokoll erfasst künftig tatsächlich durchgeführte Arbeitsschritte und Rücksprünge zwischen den CRISP-DM-Phasen: Business Understanding, Data Understanding, Data Preparation, Modeling, Evaluation und Deployment.

Die Einrichtung der Projektstruktur ist keine abgeschlossene Analyseiteration. Bisher wurden keine Analyseiterationen oder Rücksprünge durchgeführt.

## Vorlage für eine tatsächlich durchgeführte Iteration

- Datum / Iterationskennung:
- Ausgangsphase und Ziel:
- Durchgeführte Schritte und verwendete Datenversion:
- Beobachtung / nachprüfbares Ergebnis:
- Rücksprung: von welcher Phase zu welcher Phase?
- Konkreter Anlass und daraus folgende Änderung:
- Erneute Prüfung und Ergebnis:
- Reproduktionsschritte / Konfiguration / gegebenenfalls Zufallsseed:
- Verweise auf Code, Tabellen und Abbildungen:


## MOVA-ITER-001 – Moderate Verstärkung persönlicher Sportpräferenzen

Datum: 2026-10-29 (UTC). Rücksprung von Data Understanding / AP 2.4 (2.2 Describe Data, 2.3 Explore Data, 2.4 Verify Data Quality) zu Data Preparation / 3.3 Construct Data (AP 2.3), danach erneute Qualitätsprüfung. Die einleitende Aussage dieses Dokuments, dass noch keine Iterationen vorliegen, beschreibt den damaligen AP-1-Stand; der folgende Eintrag dokumentiert die jetzt tatsächlich durchgeführte erste Iteration.

### 1. Ausgangssituation

**Ursprüngliche Annahme:** positive Gewichte für alle acht Sportarten und individuelle lognormale Faktoren sollen realistische Überschneidungen ermöglichen. Zielgruppe sind aktive Smartwatch-Nutzer mit unterschiedlichen Schwerpunkten. V1: 100 Nutzer, 26 Wochen, Seed 42, 6.665 Aktivitäten, 545 Nullwochen (20,96 %). V1 wurde einschließlich bestehender Berichte und Grafiken unter outputs/simulation_comparison/v1_snapshot gesichert; SHA256.json dokumentiert die Integrität. Die Originaldateien bleiben vollständig bestehen.

### 2. Beobachtete Auffälligkeit

**Tatsächlich beobachtet:** 59 Nutzer üben alle acht Sportarten aus; 90 mindestens sieben. Mittlere Sportartenanzahl 7,47, mittlerer Top-2-Anteil 59,41 %, Median 59,02 %. Breites Repertoire bedeutet nicht gleichmäßige Verteilung, persönliche Schwerpunkte bestanden bereits.

### 3. Ursachenanalyse

Alle Profilgewichte und ihre lognormalen Multiplikatoren sind positiv. Jede Aktivität zieht erneut aus allen acht Sportarten mit festen individuellen Wahrscheinlichkeiten. Bei vielen Aktivitäten werden auch seltene Sportarten mindestens einmal beobachtet. Es gibt keinen Wechsel zu einem begrenzten persönlichen Sportartenrepertoire.

### 4. Begründete Anpassungsentscheidung

**Beschlossene Maßnahme:** individuelle Gewichte moderat mit Exponent 1,3 verstärken. Keine festen Sportartenlimits, keine Clusterlabels, keine Änderung an Trends oder Häufigkeitsparametern. Hypothese: stärker konzentrierte Sportanteile und etwas weniger breite Repertoires, bei erhaltenen Überschneidungen. Es wurde keine Zielquote erzwungen.

### 5. Tatsächlich durchgeführte Codeänderung

Neues eigenständiges Skript src/simulation_preference_comparison.py; ursprüngliches src/data_generation.py unverändert. Nach Bildung der individuellen Gewichte ergänzt: `weights = [weight ** exponent for weight in weights]`. rng.choices normalisiert die relativen Auswahlwahrscheinlichkeiten implizit.

**Zusätzliche technische Maßnahme:** acht getrennte Random-Instanzen mit Master-Seed 42 und festen Ableitungen 42–49: Frequenz/Trends/Pausen, Profil, Präferenzfaktoren, Sportwahl, Dauer, Distanz, Interessen und Wochentag. Diese Trennung verändert den historischen Zufallsstrom. Daher wurde zusätzlich ein technischer Kontrolllauf mit Exponent 1,0 auf demselben neuen Zufallsaufbau ausgeführt. Er ist eine Kontrolle, keine zweite fachliche Anpassung.

Neue Datensätze unter outputs/simulation_comparison/control_exponent_1_0 und v2_exponent_1_3. Angebote werden unverändert aus V1 kopiert. Vorhandene Ergebnisse und Prüfberichte wurden nicht verändert.

### 6. Vergleich V1 gegenüber V2

| Kennzahl | V1 historisch | Kontrolle 1,0 | V2 1,3 |
|---|---:|---:|---:|
| Nutzer mit 4 Sportarten | 0 | 0 | 2 |
| Nutzer mit 5 Sportarten | 2 | 6 | 12 |
| Nutzer mit 6 Sportarten | 8 | 14 | 15 |
| Nutzer mit 7 Sportarten | 31 | 22 | 31 |
| Nutzer mit 8 Sportarten | 59 | 58 | 40 |
| Mittlere Sportartenanzahl | 7,47 | 7,32 | 6,95 |
| Mittlerer Top-2-Anteil | 59,41 % | 57,61 % | 64,12 % |
| Median Top-2-Anteil | 59,02 % | 58,24 % | 63,73 % |
| Aktivitäten | 6.665 | 6.465 | 6.465 |
| Aktivitäten/Nutzer/Woche | 2,563 | 2,487 | 2,487 |
| Nullwochen | 545 | 558 | 558 |
| Nullwochenanteil | 20,96 % | 21,46 % | 21,46 % |
| Maximale Aktivitäten/Nutzerwoche | 10 | 10 | 10 |

Nutzer mit ein bis drei Sportarten: jeweils 0. Alle Varianten enthalten 100 Nutzer und 2.600 Nutzerwochen.

**Nachgewiesene Auswirkungen des Exponenten:** Kontrolle→V2: Top-2-Mittel +6,507 Prozentpunkte; Nutzer mit acht Sportarten 58→40; mittlere Vielfalt 7,32→6,95. Nutzerinteressen, Trendzuweisungen, alle Wochenzählungen sowie Aktivitäts-IDs/Nutzer/Datum sind in diesem gepaarten Vergleich exakt gleich. Häufigkeitsunterschiede gegenüber V1 sind Auswirkungen der technischen Umstellung, kein nachgewiesener Exponenteneffekt.

### 7. Ergebnis und fachliche Bewertung

Die Hypothese wird für diesen Seed und diese Population deskriptiv gestützt: stärkere individuelle Schwerpunkte, dennoch unterschiedliche Repertoires. Alle acht Sportarten bleiben vorhanden. Technische Prüfungen für V1, Kontrolle und V2 bestanden; neue Varianten bei wiederholter Generierung vollständig gleich. Originale und Snapshot über SHA-256 geprüft.

Nebenwirkungen: veränderte globale Sportanteile sowie sportartenbedingt andere Dauern und Distanzen; einzelne Nutzerkennzahlen müssen trotz gemeinsamer Zufallszahlen nicht monoton reagieren. Positive Gewichte erlauben weiterhin breite Repertoires. Keine empirische Validierung, keine Prognose- oder Clusteringgüte untersucht. Nicht allein auf eine geringe Zahl vollständig multisportiver Nutzer optimieren.

### 8. Entscheidung über die weitere Verwendung

**Fachliche Empfehlung B: V2 übernehmen** als bevorzugte Datenversion für die nachfolgende Aufbereitung. Die endgültige Auswahl durch das Projektteam steht aus. Technisch bleibt V2 separat: keine Ersetzung der V1-Standardpfade und keine Änderung bisheriger Analyseberichte. AP 4 muss nach der Auswahl explizit auf die gewählte Version verweisen. Keine ML-Modelle trainiert, keine Empfehlungsregeln entwickelt, kein Commit und kein Pull Request erstellt.

Reproduktion: `python src/simulation_preference_comparison.py` im Worktree /workspace/MOVA-AP2-3. Bestehende Vergleichsdateien werden nur akzeptiert, wenn ihre Inhalte identisch sind; andernfalls Abbruch ohne Überschreiben. Vollständige Ergebnisse: outputs/simulation_comparison/comparison_report.md sowie comparison_metrics.csv, sport_distribution_comparison.csv, user_metrics_comparison.csv und paired_user_changes.csv. Vorher-Nachher-Grafiken unter outputs/simulation_comparison/figures/.


### Abschließende Projektentscheidung zu MOVA-ITER-001 – 29.10.2026

Das Projektteam hat V2 mit Exponent 1,3 verbindlich angenommen; die zuvor offene Versionsauswahl ist damit abgeschlossen. Die aktive Quelle sind die drei CSVs unter data/raw sowie die passende Nutzer-Wochen-Kontrolle unter outputs/tables. Vor Ersetzung wurde die vollständige V1-Sicherung per SHA-256 geprüft; anschließend wurden aktive Dateien mit den zuvor erzeugten V2-Dateien verglichen. Historische Analysen und sämtliche Vergleichsmesswerte bleiben unverändert bestehen. Der Standardgenerator wurde auf die bereits geprüfte V2-Logik umgestellt; keine weitere Simulationsvariante entwickelt. Technische Endkontrolle und Prüfsummen: documentation/active_data_version.json und outputs/tables/active_data_validation.md. V2 enthält 100 Nutzer, 26 Wochen, 2.600 Nutzerwochen, 6.465 Aktivitäten, 30 fiktive Angebote und 558 Nullwochen. Die Auswahl impliziert noch keine vollständige Data Preparation oder Modellierung.
