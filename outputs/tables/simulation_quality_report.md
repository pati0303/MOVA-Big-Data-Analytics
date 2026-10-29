# MOVA – Fachliche Qualitätsprüfung AP 2.4

## 1. Ziel und Datenbasis

Untersucht werden fachliche Plausibilität und Eignung für spätere Arbeitspakete (CRISP-DM 2.2 Describe Data, 2.3 Explore Data, 2.4 Verify Data Quality). Es wurden keine Daten neu generiert, keine Parameter geändert, keine Cluster erzeugt und keine Modelle trainiert.

Vorhandene Daten: 100 Nutzer, 6,665 Aktivitäten, 26 vollständige Wochen vom 05.01. bis 05.07.2026 (ISO-KW 02–27), 2.600 Nutzerwochen und 30 fiktive Angebote. Schwerpunkt dieser Prüfung sind Aktivitäten und Nutzerwochen. Die bestehende technische Prüfung umfasst auch Nutzerinteressen und Angebote. Interessen werden nicht als Clustering- oder Regressionsmerkmale ausgewertet.

## 2. Methoden und Reproduzierbarkeit

Aufruf: `python src/simulation_quality_analysis.py`. Python 3.12.14, pandas 2.2.3, NumPy 2.3.5, Matplotlib 3.10.8. Die Analyse verwendet keine Zufallsziehung. Alle ursprünglichen sieben Dateien sowie .gitignore werden vor und nach der Analyse über SHA-256 auf unveränderte Inhalte geprüft.

Das Nutzer-Wochen-Raster wird aus allen 100 Nutzer-IDs und 26 Montagen unabhängig rekonstruiert. Fehlende Aktivitäten werden dort als 0 berücksichtigt und mit der vorhandenen Kontrolltabelle verglichen. Nutzer-Mittelwerte werden stets durch 26 geteilt. Sportartenanteile verwenden die Gesamtzahl der Aktivitäten des jeweiligen Nutzers als Nenner.

Der Median ist der mittlere sortierte Wert. Standardabweichung (SD, Stichprobenformel mit n−1) beschreibt Streuung um den Mittelwert; IQR ist der Abstand zwischen dem 25. und 75. Perzentil und weniger empfindlich gegenüber Extremwerten. Ein IQR-Ausreißer liegt außerhalb Q1−1,5×IQR bis Q3+1,5×IQR und ist zunächst ein Prüfhinweis, kein Datenfehler.

Zeitliche Entwicklung wird durch den Mittelwert der letzten sechs minus der ersten sechs Wochen beschrieben. Über +0,5 Aktivitäten/Woche heißt deskriptiv steigend, unter −0,5 sinkend. Sonst gilt SD > 1,5 als schwankend, der Rest als stabil/geringe Schwankung. Diese heuristischen Schwellen sind nicht empirisch validiert, Kategorien sind priorisiert und werden ausschließlich als deskriptive Prüfkennzahlen gespeichert, nicht als Clusterlabels oder Modellmerkmale. Steigende Nutzer können stark schwanken. Anfangs-/Endvergleich kann zwischenzeitliche Wellen übersehen. Interne Generatorlabels werden nicht herangezogen.

## 3. Sportartenverteilung

| sport_type | Anzahl | Anteil_% |
| --- | --- | --- |
| Running | 974 | 14.614 |
| Cycling | 1207 | 18.110 |
| Strength | 873 | 13.098 |
| Swimming | 584 | 8.762 |
| Walking | 1109 | 16.639 |
| Hiking | 863 | 12.948 |
| Tennis | 525 | 7.877 |
| Padel | 530 | 7.952 |

Häufigste Sportart: Cycling (18.11 %); seltenste: Tennis (7.88 %). Verhältnis häufigste/seltenste: 2.30:1. Alle acht Sportarten sind ausreichend oft für deskriptive Vergleiche vertreten; keine dominiert die Gesamtaktivitäten mit einer Mehrheit. Die Gleichmäßigkeit ist eine Eigenschaft der Konstruktionsannahmen, kein Nachweis einer realen Population.

Grafik: `outputs/figures/sport_distribution.png`.

## 4. Unterschiede zwischen Nutzern

| index | min | median | max | mean | std | IQR |
| --- | --- | --- | --- | --- | --- | --- |
| Aktivitaeten_pro_Woche | 0.462 | 2.346 | 5.154 | 2.563 | 1.164 | 1.865 |
| Minuten_pro_Woche | 17.381 | 151.417 | 439.977 | 166.964 | 89.946 | 122.223 |
| Sportartenanzahl | 5.000 | 8.000 | 8.000 | 7.470 | 0.731 | 1.000 |
| Nullwochen | 0.000 | 5.000 | 17.000 | 5.450 | 3.705 | 4.000 |
| groesster_Sportanteil_% | 17.347 | 36.257 | 77.895 | 38.750 | 13.443 | 19.000 |

Verteilung der Zahl unterschiedlicher Sportarten:

| Sportartenanzahl | Nutzeranzahl |
| --- | --- |
| 5 | 2 |
| 6 | 8 |
| 7 | 31 |
| 8 | 59 |

Sportartenanteile innerhalb eines Nutzers, über alle Nutzer zusammengefasst (Prozent, mit Nullanteilen):

| sport_type | min | median | max | mean | std | IQR |
| --- | --- | --- | --- | --- | --- | --- |
| Running | 0.000 | 10.781 | 73.585 | 14.458 | 13.665 | 14.693 |
| Cycling | 0.000 | 11.018 | 77.895 | 15.981 | 15.455 | 15.680 |
| Strength | 0.000 | 9.360 | 73.846 | 12.857 | 12.073 | 11.649 |
| Swimming | 0.000 | 5.582 | 50.575 | 8.340 | 9.702 | 6.799 |
| Walking | 0.000 | 14.947 | 77.143 | 18.884 | 15.329 | 19.326 |
| Hiking | 0.000 | 8.333 | 56.098 | 13.198 | 13.374 | 13.155 |
| Tennis | 0.000 | 5.826 | 41.176 | 8.056 | 7.467 | 8.258 |
| Padel | 0.000 | 5.455 | 50.617 | 8.224 | 8.509 | 7.469 |

Die Häufigkeit und Trainingsminuten unterscheiden sich deutlich. Breite Sportmischungen und überlappende Vorlieben verhindern jedoch die Annahme sauber getrennter Gruppen. K-Means kann später auf geeigneten aggregierten Merkmalen demonstriert werden; die Existenz sinnvoller Cluster ist damit nicht belegt. Skalierung ist nötig, weil Minuten größere Zahlenbereiche haben als Häufigkeiten oder Anteile. Anteilsmerkmale summieren sich zu 100 % und sind abhängig; Häufigkeit und Minuten können dieselbe Aktivität mehrfach gewichten. Anzahl Sportarten kann nahe acht wenig Trennkraft liefern. Feature-Auswahl, Skalierung, Clusterstabilität und fachliche Interpretation bleiben offen.

Grafik: `outputs/figures/activity_frequency_distribution.png`.

## 5. Zeitliche Entwicklungen

| week_start | Aktivitaeten | Aktivitaeten_pro_Nutzer | Nullwochen | ISO_KW |
| --- | --- | --- | --- | --- |
| 2026-01-05 00:00:00 | 256 | 2.560 | 20 | 2026-KW02 |
| 2026-01-12 00:00:00 | 239 | 2.390 | 22 | 2026-KW03 |
| 2026-01-19 00:00:00 | 247 | 2.470 | 21 | 2026-KW04 |
| 2026-01-26 00:00:00 | 297 | 2.970 | 18 | 2026-KW05 |
| 2026-02-02 00:00:00 | 265 | 2.650 | 28 | 2026-KW06 |
| 2026-02-09 00:00:00 | 237 | 2.370 | 25 | 2026-KW07 |
| 2026-02-16 00:00:00 | 251 | 2.510 | 26 | 2026-KW08 |
| 2026-02-23 00:00:00 | 255 | 2.550 | 23 | 2026-KW09 |
| 2026-03-02 00:00:00 | 229 | 2.290 | 26 | 2026-KW10 |
| 2026-03-09 00:00:00 | 240 | 2.400 | 28 | 2026-KW11 |
| 2026-03-16 00:00:00 | 260 | 2.600 | 21 | 2026-KW12 |
| 2026-03-23 00:00:00 | 244 | 2.440 | 22 | 2026-KW13 |
| 2026-03-30 00:00:00 | 288 | 2.880 | 15 | 2026-KW14 |
| 2026-04-06 00:00:00 | 285 | 2.850 | 18 | 2026-KW15 |
| 2026-04-13 00:00:00 | 272 | 2.720 | 22 | 2026-KW16 |
| 2026-04-20 00:00:00 | 242 | 2.420 | 15 | 2026-KW17 |
| 2026-04-27 00:00:00 | 269 | 2.690 | 18 | 2026-KW18 |
| 2026-05-04 00:00:00 | 264 | 2.640 | 18 | 2026-KW19 |
| 2026-05-11 00:00:00 | 268 | 2.680 | 16 | 2026-KW20 |
| 2026-05-18 00:00:00 | 262 | 2.620 | 18 | 2026-KW21 |
| 2026-05-25 00:00:00 | 217 | 2.170 | 27 | 2026-KW22 |
| 2026-06-01 00:00:00 | 253 | 2.530 | 22 | 2026-KW23 |
| 2026-06-08 00:00:00 | 236 | 2.360 | 21 | 2026-KW24 |
| 2026-06-15 00:00:00 | 248 | 2.480 | 22 | 2026-KW25 |
| 2026-06-22 00:00:00 | 279 | 2.790 | 18 | 2026-KW26 |
| 2026-06-29 00:00:00 | 262 | 2.620 | 15 | 2026-KW27 |

Wochenmittel über alle Nutzer: Minimum 2.17, Maximum 2.97 Aktivitäten/Nutzer. Aggregation glättet gegenläufige individuelle Entwicklungen.

Deskriptive Verlaufskategorien gemäß der oben erklärten Heuristik:

| deskriptiver_Verlauf | Nutzeranzahl |
| --- | --- |
| sinkend | 41 |
| steigend | 35 |
| schwankend | 16 |
| stabil/geringe_Schwankung | 8 |

Fünf anhand tatsächlicher Zeitreihen ausgewählte Nutzer; je Kriterium wird der extremste noch nicht ausgewählte Nutzer gewählt:

| user_id | Aktivitaeten_pro_Woche | Wochen_SD | Ende_minus_Anfang | Nullwochen | Auswahlgrund |
| --- | --- | --- | --- | --- | --- |
| U070 | 3.423 | 2.817 | 5.000 | 4 | stärkste Zunahme |
| U038 | 4.462 | 2.874 | -4.667 | 0 | stärkste Abnahme |
| U081 | 0.577 | 0.703 | -0.333 | 14 | stabil, geringe Schwankung |
| U033 | 3.385 | 3.348 | -1.000 | 8 | größte Schwankung |
| U076 | 0.846 | 1.255 | 1.333 | 17 | meiste Nullwochen |

Exakte Wochenzahlen dieser Nutzer von KW 02 bis KW 27:

- U070 (stärkste Zunahme): 4, 1, 0, 3, 0, 2, 0, 1, 1, 0, 3, 4, 4, 3, 7, 3, 2, 7, 1, 3, 8, 9, 4, 7, 9, 3
- U038 (stärkste Abnahme): 3, 10, 10, 5, 10, 10, 3, 4, 3, 6, 2, 1, 1, 3, 4, 2, 3, 2, 6, 8, 3, 5, 4, 2, 3, 3
- U081 (stabil, geringe Schwankung): 0, 2, 1, 1, 0, 1, 1, 1, 0, 2, 0, 0, 1, 0, 0, 0, 1, 1, 0, 0, 0, 0, 1, 0, 0, 2
- U033 (größte Schwankung): 7, 3, 3, 8, 10, 0, 5, 2, 0, 0, 1, 0, 0, 5, 10, 8, 0, 0, 1, 0, 2, 5, 2, 6, 3, 7
- U076 (meiste Nullwochen): 0, 0, 0, 0, 0, 0, 0, 0, 2, 2, 0, 0, 3, 0, 0, 0, 0, 3, 0, 4, 2, 2, 0, 0, 2, 2

Wochentage (jeder Wochentag ist im Zeitraum genau 26-mal vorhanden):

| index | Aktivitaeten | Anteil_Prozent |
| --- | --- | --- |
| Mo | 908 | 13.623 |
| Di | 852 | 12.783 |
| Mi | 841 | 12.618 |
| Do | 858 | 12.873 |
| Fr | 889 | 13.338 |
| Sa | 1124 | 16.864 |
| So | 1193 | 17.899 |

Wochenendanteil: 34.76 %, gegenüber 28,57 % bei gleichmäßiger Tagesverteilung. Das passt zu den höheren Wochenendgewichten im Generator. Es ist kein gemessener realer Verhaltenseffekt.

Für eine spätere Folgewoche-Prognose sind Schwankungen, Nullen und unterschiedliche Niveaus vorhanden. Die deskriptive Pearson-Korrelation benachbarter Wochen beträgt gepoolt 0.420, nach Abzug des jeweiligen Nutzermittels 0.221. Eine Korrelation beschreibt gemeinsamen Verlauf, keine Prognosegüte. Die Zentrierung nutzt hier rein deskriptiv alle 26 Wochen und darf so nicht in spätere Trainings-/Testmerkmale übernommen werden. Der Unterschied beider Korrelationen zeigt den Einfluss verschiedener Grundniveaus.

Maximal 100×25 = 2.500 benachbarte Nutzer-Wochen-Paare stehen vor zusätzlichen Rückblickfenstern zur Verfügung; diese sind innerhalb von Nutzern abhängig. 26 Wochen pro Nutzer sind kurz. Lineare Regression ist als Demonstration grundsätzlich möglich, aber Zähldaten, Nullwochen und nichtlineare Schwankungen verletzen möglicherweise einfache lineare Annahmen. Zeitlich trennen, Merkmale ausschließlich aus vorher bekannten Wochen bilden und später mit einfachen Vorhersagen (Vorwoche bzw. bisheriges Mittel) vergleichen. Negative Prognosen und Residuen kritisch prüfen. Es wird keine erreichbare Güte behauptet.

Grafiken: `outputs/figures/user_activity_trends.png`, `outputs/figures/weekly_activity_overview.png`.

## 6. Nullwochen und Aktivitätspausen

545 von 2.600 Nutzerwochen (20.96 %) sind null. 96 Nutzer haben mindestens eine Nullwoche. Verteilung je Nutzer:

| Nullwochen | Nutzeranzahl |
| --- | --- |
| 0 | 4 |
| 1 | 8 |
| 2 | 8 |
| 3 | 11 |
| 4 | 17 |
| 5 | 16 |
| 6 | 5 |
| 7 | 7 |
| 8 | 3 |
| 9 | 8 |
| 10 | 4 |
| 12 | 2 |
| 13 | 1 |
| 14 | 4 |
| 15 | 1 |
| 17 | 1 |

Eine beobachtete Pause ist jede maximal zusammenhängende Folge von Nullwochen, unabhängig von ihrer Ursache. Die Daten erlauben keine Unterscheidung zwischen intern erzeugter Pause und zufällig null gezogenen Aktivitäten. Verteilung der 330 beobachteten Folgen:

| Laenge_Wochen | Pausenanzahl |
| --- | --- |
| 1 | 204 |
| 2 | 73 |
| 3 | 30 |
| 4 | 16 |
| 5 | 4 |
| 6 | 1 |
| 7 | 1 |
| 8 | 1 |

Längste beobachtete Nullfolge: 8 Wochen; Median 1.0. 35 Folgen berühren den Beobachtungsrand und können außerhalb des Zeitraums länger sein. Folgen können länger als die im Generator vorgesehenen Einzelpausen sein, weil zufällige Nullwochen und weitere Pausen anschließen können.

Wöchentliche Nullnutzerzahl: 15–28; Maximum in 2026-KW06, 2026-KW11. Die vollständige zeitliche Verteilung steht in Abschnitt 5. Daraus allein lässt sich kein Kalender- oder Saisonproblem ableiten.

21 % Nullwochen sind für eine bewusst heterogene Demonstrationspopulation einschließlich Gelegenheitsaktiven vertretbar. Für ausschließlich regelmäßig trainierende Nutzer wäre dieser Anteil kritisch. Ohne empirischen Vergleich ist er nicht validiert. Entscheidend sind individuelle Konzentration und Pausenlängen, nicht nur der Gesamtanteil. Die Nullwochen dürfen später nicht aus der Regressionstabelle entfernt werden.

## 7. Sportartspezifische Plausibilität

Dauern in Minuten, Distanzen in Kilometern. `nan` bedeutet in der folgenden Tabelle nicht anwendbar, wenn die gesamte Sportart keine Distanzen besitzt.

| Sport | Dauer_min | Dauer_Median | Dauer_max | Distanz_min_km | Distanz_Median_km | Distanz_max_km | Distanz_fehlt | Dauer_unterer_Rand | Dauer_oberer_Rand | Dauer_IQR_Ausreisser | Distanz_IQR_Ausreisser |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Running | 15.000 | 39.100 | 114.500 | 1.630 | 5.840 | 22.060 | 0 | 0 | 0 | 23 | 19.000 |
| Cycling | 19.300 | 66.400 | 226.700 | 5.060 | 22.120 | 75.610 | 0 | 0 | 0 | 25 | 30.000 |
| Strength | 19.300 | 51.200 | 120.000 | nan | nan | nan | 873 | 0 | 8 | 18 | nan |
| Swimming | 12.600 | 35.500 | 100.000 | 0.330 | 1.160 | 4.300 | 0 | 0 | 1 | 15 | 12.000 |
| Walking | 17.700 | 45.200 | 146.700 | 1.100 | 3.430 | 9.910 | 0 | 0 | 0 | 25 | 36.000 |
| Hiking | 44.500 | 122.600 | 360.000 | 1.580 | 7.790 | 24.230 | 0 | 0 | 1 | 24 | 23.000 |
| Tennis | 20.100 | 65.900 | 175.000 | nan | nan | nan | 525 | 0 | 0 | 15 | nan |
| Padel | 22.100 | 67.250 | 150.000 | nan | nan | nan | 530 | 0 | 4 | 12 | nan |

Bei Strength, Tennis und Padel sind insgesamt 1928 leere Distanzfelder fachlich beabsichtigt. Bei den fünf Distanzsportarten fehlt keine Distanz. Nicht anwendbare Werte werden weder als gemessene 0 interpretiert noch pauschal imputiert. Spätere Aggregationen müssen zwischen Sportart ohne Distanz und Nutzerwoche ohne Aktivität unterscheiden.

Die sportartspezifischen Dauer- und Geschwindigkeitsgrenzen des vorhandenen Generators wurden erneut technisch geprüft und eingehalten (einschließlich Rundungstoleranz bei Distanzen). IQR-Ausreißer sind bei rechtsschiefen Trainingsdauern erwartbar und hier kein bestätigter Fehler. Lange Ausdauereinheiten und hohe Geschwindigkeiten benötigen dennoch fachliche Einordnung. Grenzwerte sind Simulationsannahmen, keine universellen menschlichen Leistungsgrenzen. Die exakten Randhäufigkeiten sind oben ausgewiesen; Häufungen können durch Abschneiden entstehen. Wochen mit genau zehn Aktivitäten: 36 (1.38 %). Der Einfluss dieser Obergrenze sollte im späteren Modellvergleich beachtet werden.

## 8. Erneute technische Datenqualität

| index | Fehleranzahl |
| --- | --- |
| Fehlende Pflichtwerte | 0 |
| Ungueltige Datumswerte/Format | 0 |
| Unbekannte Nutzer | 0 |
| Doppelte Aktivitaets-IDs | 0 |
| Negative/nicht endliche Dauer | 0 |
| Negative/nicht endliche vorhandene Distanz | 0 |
| Ausserhalb Zeitraum | 0 |
| Unbekannte Sportart | 0 |
| Fehlende notwendige Distanz | 0 |
| Unerwartete Distanz bei nicht anwendbar | 0 |

BESTANDEN: 100 eindeutige Nutzer; vollständiges und eindeutiges 100×26-Raster; jede Wochenzählung stimmt mit unabhängig gezählten Einzelaktivitäten überein. Vorhandene Generatorprüfung `validate()` ebenfalls bestanden; der Generator selbst wurde nicht ausgeführt. Keine bestätigten technischen Fehler. Fachliche Modellannahmen werden dadurch nicht empirisch bestätigt.

## 9. Gesamtbewertung und nächste Schritte

**B – Grundsätzlich geeignet, aber Verbesserungen sinnvoll.** Die Daten sind technisch konsistent, enthalten Nutzerunterschiede, überlappende Sportarten und unregelmäßige Zeitreihen. Sie eignen sich für eine didaktische Pipeline. Reale Clusterstruktur, reale Prognoseleistung oder Übertragbarkeit lassen sich daraus nicht ableiten.

1. Vor einer möglichen zweiten Simulation Zielpopulation und gewünschte Häufigkeits-/Pausenbereiche fachlich festlegen. Insbesondere Nullwochenkonzentrationen und lange Nullfolgen prüfen; nicht allein auf 21 % optimieren.
2. Den hohen Sportartenmix und die Trennkraft der Sportartenanzahl prüfen. Falls fachlich nötig, später begründete und weiterhin überlappende Vorlieben anpassen; in diesem Arbeitsschritt wurde nichts verändert.
3. Randhäufungen, lange Einheiten und die Wochenobergrenze anhand der Tabellen besprechen. Alternative Verteilungen nur bei fachlichem Bedarf in einem dokumentierten Folgeschritt testen.
4. Für spätere Modelle Nullwochen erhalten, Anteile und fehlende Distanzen bewusst behandeln, Features skalieren und redundante Merkmale vermeiden. Zeitbasierte Evaluation und einfache Vergleichsvorhersagen planen.
5. Saison und Messfehler sind bislang nicht enthalten. Vor ihrer Ergänzung prüfen, ob sie dem Hochschulziel dienen; keinen empirischen Realismus behaupten.

Tatsächlich abgeschlossen ist diese deskriptive Qualitätsprüfung. Noch kein Rücksprung mit geänderten Simulationsannahmen durchgeführt; eine solche Iteration würde erst nach beschlossener Änderung und erneutem Vergleich dokumentiert. Keine vollständige Data Preparation für AP 4 und keine Modellierung erfolgt.

## 10. Artefakte und Integrität

Zusätzlich zum Bericht und den vier PNG-Grafiken entstehen `simulation_user_quality_metrics.csv`, `simulation_user_sport_shares.csv`, `simulation_weekly_quality_metrics.csv` und `simulation_zero_runs.csv` unter outputs/tables. Dies sind beschreibende Auswertungen, keine neuen simulierten Beobachtungen oder Modellmerkmale für AP 4.

SHA-256 der unveränderten Quelldateien:

- `src/data_generation.py`: `8dc53768e0388ccf7de13fce6d99c88655a76f185705be10dc4ec63961e59425`
- `documentation/simulation_config.md`: `1006101bdda42753a2d74513789ed0df2f20507601c397d5f99b1144f14294e9`
- `data/raw/activities_simulated.csv`: `537e3f0ffbe2bf0a5f93c02e5c579604f2a8caea74ebd3cf06cfacbe63ae1598`
- `data/raw/users_simulated.csv`: `df247555fecdb69bcade37f7649342859a381c9e6b66fc4ff548b84e629f4b12`
- `data/raw/offers_simulated.csv`: `83748cb66918c08e3061889834e24452d0dc9feb6581690c4959cb3ba3775fa6`
- `outputs/tables/simulation_weekly_check.csv`: `8e7407ee83e8658075e0ab66c157088109dfa3c833a1d7780b1514e0f788821d`
- `outputs/tables/simulation_report.md`: `896d56a41811e9d55186acfdcb5965301514e81c9b7eab422e270b7369f14b82`
- `.gitignore`: `fd1b3c546a91718f74464b7d4833a42b69f71a8c66e78d3a9e7c2fed2b30aae8`
