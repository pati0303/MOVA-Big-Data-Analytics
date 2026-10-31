# MOVA – Merkmalskonzept für die globale lineare Regression (AP 3.3)

Stand: 31.10.2026. CRISP-DM: 2.3 Explore Data, 3.1 Select Data, 3.3 Construct Data (Planung), 4.2 Generate Test Design (Planung).

## 1. Ziel

Ein einziges globales lineares Regressionsmodell soll für die bereits beobachteten Nutzer die Anzahl aufgezeichneter Aktivitäten in der folgenden vollständigen Woche prognostizieren. Alle acht Sportarten werden gemeinsam gezählt; keine separate Regression je Sportart. Keine vorgegebenen Nutzergruppen oder Simulationslabels. Vorhersagezeitpunkt ist unmittelbar nach Abschluss von Woche t, wenn deren Aufzeichnungen vollständig vorliegen. Keine Mehrwochenprognose aus einem einzigen Stichtag.

## 2. Ausgangsdaten und notwendige deskriptive Prüfung

Ausschließlich aktive V2: 100 Nutzer, 6.465 Aktivitäten, 26 Montag-bis-Sonntag-Wochen vom 05.01. bis 05.07.2026. Nutzerliste aus data/raw/users_simulated.csv, Einzelaktivitäten aus data/raw/activities_simulated.csv. Angebote sind für dieses Ziel irrelevant. Die vollständige Wochenkontrolle outputs/tables/simulation_weekly_check.csv wurde gegen die Einzelaktivitäten abgeglichen: alle 2.600 Nutzerwochen stimmen überein. Alle vier Prüfsummen aus documentation/active_data_version.json stimmen vor und nach der Arbeit überein.

Wiederverwendete V2-Ergebnisse: outputs/tables/simulation_report_v2.md, active_data_validation.md und documentation/kmeans_feature_concept.md. Die historischen Berichte simulation_quality_report.md und simulation_report.md beschreiben V1 und wurden nicht als V2-Nachweis verwendet. Das K-Means-Konzept zeigt bereits Nutzerunterschiede: mittlere Aktivitäten/Woche je Nutzer 0,3462–6,1923 (Mittel 2,4865; Stichproben-SD 1,2934).

Notwendige zusätzliche V2-Berechnungen, keine Modellbewertung:

- Über alle 2.600 Wochenzahlen: Mittel 2,4865, Median 2, Q1 1, Q3 4, Stichproben-SD 2,2868, Minimum 0, Maximum 10.
- 558 Nullwochen = 21,46 %; 95 Nutzer haben mindestens eine Nullwoche.
- Wochenmittel über alle Nutzer: 2,15–3,13 Aktivitäten/Nutzer. Erste sechs Wochen im Mittel 2,6317; letzte sechs 2,4200. Deskriptiver Vergleich, kein Nachweis eines einheitlichen linearen Trends.
- 327 maximal zusammenhängende Nullfolgen: 201 mit Länge 1, 66 mit Länge 2, 37 mit Länge 3, 15 mit Länge 4, vier mit Länge 6, drei mit Länge 7 und eine mit Länge 9 Wochen. Median 1, Maximum 9; 39 Folgen berühren den Beobachtungsrand und können außerhalb länger sein.
- Eine beobachtete Nullfolge erlaubt keine Unterscheidung zwischen echter Trainingspause, zufälliger Inaktivität oder fehlender Aufzeichnung. Interne Pausenmechanismen sind keine beobachtbaren Merkmale.

Berechnung mit Python, pandas 2.2.3 und NumPy 2.3.5; nur im Arbeitsspeicher. Lokaler Reproduktionscode: work/document_regression.py. Keine vollständige Modellierungstabelle gespeichert. Beschreibungen des gesamten Zeitraums sind ausdrücklich Exploration und keine nachgewiesene Prognoseleistung.

## 3. Geplante Modellierungsstruktur

Grundlage ist ein sortiertes vollständiges Raster aus Nutzer-ID × 26 Wochen, insgesamt 2.600 Zeilen. Fehlende Aktivitätsgruppen im gültigen Raster werden als Anzahl 0 ergänzt; fehlende Historie oder unbekannte Zukunft dagegen nicht als 0 auffüllen. Eine Zeile bezeichnet Nutzer u und abgeschlossene Eingabewoche t. Nutzer-ID, week_start und target_week_start bleiben Zuordnungsschlüssel, keine numerischen Regressoren.

Wochennummern hier sind relative Projektwochen 1–26, keine ISO-Kalenderwochen. Woche 1 beginnt am 05.01.2026 (ISO-KW 02).

## 4. Merkmale und Formeln

Sei c(u,t) die Anzahl aller aufgezeichneten Aktivitäten eines Nutzers in Woche t.

| Geplanter Name | Formel | Bedeutung / Bewertung |
| --- | --- | --- |
| activities_current_week | c(u,t) | Jüngster bekannter Zustand; für den ersten Ansatz empfohlen. |
| activities_previous_week | c(u,t−1) | Zusätzlicher kurzfristiger Rückblick; sinnvoll, aber zunächst optionale Erweiterung. |
| avg_activities_last_4_weeks | [c(u,t)+c(u,t−1)+c(u,t−2)+c(u,t−3)] / 4 | Lokales Niveau einschließlich aktueller Woche und Nullwochen; für den ersten Ansatz empfohlen. |
| week_index | t, beginnend bei 1 | Gemeinsame Zeitposition; vorerst nur Zuordnung und Split, kein Basiseingang. |

Empfohlener erster Umfang: activities_current_week und avg_activities_last_4_weeks plus geschätzter Achsenabschnitt. activities_previous_week als vorab definierte Erweiterungsvariante, nicht durch Auswahl am finalen Test optimieren. Der Vierwochenmittelwert enthält aktuelle und vorherige Woche, ist aber mit beiden allein nicht exakt rekonstruierbar: t−2 und t−3 liefern weitere Information. Überlappung bedeutet daher partielle Redundanz, keine exakte lineare Abhängigkeit dieser drei Spalten.

Notwendige Pearson-Korrelationen der Eingangsmerkmale auf den vorgesehenen 1.800 Trainingszeilen (keine Zielkorrelationen, keine Güteberechnung):

| Merkmal | activities_current_week | activities_previous_week | avg_activities_last_4_weeks | week_index |
| --- | --- | --- | --- | --- |
| activities_current_week | 1.0000 | 0.4556 | 0.7217 | -0.0057 |
| activities_previous_week | 0.4556 | 1.0000 | 0.7655 | -0.0341 |
| avg_activities_last_4_weeks | 0.7217 | 0.7655 | 1.0000 | -0.0367 |
| week_index | -0.0057 | -0.0341 | -0.0367 | 1.0000 |

Das geglättete Niveau hängt deutlich mit Einzelwochen zusammen (r etwa 0,72 und 0,77). Potenziell instabile einzelne Koeffizienten sind bei überlappenden Merkmalen zu prüfen. Diese gepoolten Korrelationen enthalten Unterschiede zwischen Nutzern und dürfen nicht als rein innerhalb eines Nutzers geltende Dynamik interpretiert werden.

week_index erzwingt in einer globalen Regression einen gemeinsamen linearen Zeitbeitrag. Unterschiedliche individuelle Entwicklungen können sich aufheben; der Index bildet weder Saison noch individuelle Trends ab. Im Test liegen zudem größere Indizes als im Training: lineare Extrapolation. Deshalb kein Basiseingang; eine fachlich begründete Variante erst über zeitliche Validierung im Training prüfen. Kleine Korrelationen mit Eingängen beweisen weder Nutzlosigkeit noch Prognosewert.

Fehlende Informationen: längerfristiges individuelles Niveau, Ende oder Ursache von Pausen, saisonale/äußere Einflüsse, Aufzeichnungsvollständigkeit und individuelle Trendunterschiede. Vier Wochen sind ein begrenzter Rückblick. Kein über alle 26 Wochen berechnetes Nutzermittel aus AP 3.2 als Regressor übernehmen: es enthält am früheren Prognosezeitpunkt Zukunft. Nutzer-IDs weder als Zahlen kodieren noch Simulationsprofile einsetzen. Zusätzliche Merkmale sind für dieses Konzept nicht konstruiert.

## 5. Zielvariable

activities_next_week = c(u,t+1), ganzzahlig und nicht negativ, in V2 0–10. Die Zielwoche ist vollständig nach der Eingabewoche. Die Begrenzung 10 ist eine Simulationsannahme, keine natürliche allgemeine Obergrenze.

## 6. Zeitliche Reihenfolge und Leakage

1. Innerhalb jedes Nutzers nach week_start aufsteigend sortieren und vollständige, eindeutige Wochen prüfen.
2. Wochenzählungen auf dem vollständigen Raster erzeugen. Gruppenbezogen shift(1) für die Vorwoche; trailing rolling(window=4, min_periods=4) auf c(u,t) für den Mittelwert. Kein zentriertes Fenster.
3. Gruppenbezogen shift(−1) erzeugt das Label der Folgewoche; es darf ausschließlich in die Zielspalte gelangen. Ohne Gruppierung würden Nutzergrenzen vermischt.
4. Unvollständige Historie und letzte Woche ohne beobachtetes Ziel von verwendbaren Modellzeilen ausschließen; echte Nullwochen behalten.
5. Split anhand target_week_start für alle Nutzer identisch. Keine zufällige Zeilenaufteilung, die spätere Wochen zum Training früherer Testziele verwendet.

Leakage-Beispiele: Zielwoche im rollierenden Fenster; Rückwärtsauffüllen mit Zukunftswerten; Gesamtzeitraum-Nutzermittel; Skalierung oder Imputation auf dem gesamten Datensatz lernen; Feature-/Modellwahl anhand des finalen Tests; Cluster aus sämtlichen 26 Wochen als frühe Regressionsmerkmale übernehmen. Deterministische vergangenheitsbezogene Fenster dürfen vor dem Split konstruiert werden, sofern die zeitliche Verfügbarkeit strikt stimmt. Gelernte Transformationen ausschließlich am Trainingsbestand anpassen. Lineare Regression benötigt hier keine zwingende Skalierung; eine optionale Skalierung muss diese Regel ebenfalls einhalten.

## 7. Konkreter chronologischer Train/Test-Plan

Vier Historienwochen bedeuten hier t, t−1, t−2, t−3, nicht vier Wochen zusätzlich vor t. Daher frühestes t = 4, spätestes t = 25 (Ziel Woche 26). Pro Nutzer 22, insgesamt 2.200 vollständige Beispiele.

| Verwendung | Eingabewoche t | Zielwochen t+1 | Zielzeitraum | Zeilen |
| --- | --- | --- | --- | --- |
| Training | 4–21 | 5–22 | 02.02.–07.06.2026 | 18 × 100 = 1.800 |
| Test | 22–25 | 23–26 | 08.06.–05.07.2026 | 4 × 100 = 400 |
| Nicht verwendbare frühe Eingabezeilen | 1–3 | keine vollständige Vierwochenhistorie | — | 300 |
| Nicht verwendbare letzte Eingabezeile | 26 | Woche 27 nicht beobachtet | — | 100 |

Aufteilung verwendbarer Beispiele: 81,82 % / 18,18 %, bestmögliche Annäherung an 80/20 bei 22 gemeinsamen Wochen und ganzen Wochenblöcken. Insgesamt 2.600 − 300 − 100 = 2.200. Wochen 1–3 bleiben als Historie nutzbar; Woche 26 bleibt als Testziel nutzbar. Auch bei einem kleineren Merkmalsumfang für vergleichbare Varianten dieselben Zeilen verwenden.

Rollierende Einwochenprognosen mit nach Trainingsabschluss festgehaltenem Modell: Nach Abschluss von Woche 22 wird für Woche 23 prognostiziert; Training verwendet Ziele bis einschließlich Woche 22. Der erste Testmittelwert enthält Wochen 19–22, alle dann bekannt. Nach Abschluss von Woche 23 darf deren tatsächlich beobachtete Aktivitätszahl als Eingang für die Vorhersage von Woche 24 dienen. Frühere Testbeobachtungen sind zu späteren Prognosezeitpunkten bekannt und daher kein Leakage. Das gilt nicht für eine gleichzeitige Vierwochenprognose am Ende von Woche 22; diese wäre eine andere Aufgabe. Kein Nachtrainieren auf Testzielen in diesem geplanten Vergleich.

## 8. MAE und Baseline – ausschließlich Bewertungskonzept

MAE = (1/n) × Summe |y_i − Vorhersage_i|. Er misst die mittlere absolute Abweichung der prognostizierten Wochenaktivitätszahl. Einheit: Aktivitäten pro prognostizierter Nutzerwoche (Aktivitäten/Woche), nicht Prozent. Ein nur zur Erklärung gedachter MAE von 1 würde durchschnittlich eine Aktivität Abweichung pro Nutzerwoche bedeuten; das ist kein berechnetes MOVA-Ergebnis.

Persistenzbaseline: Vorhersage für t+1 = c(u,t). Regression und Baseline auf exakt denselben 400 Testzeilen, denselben Zielwochen und demselben Einwochen-Informationsstand vergleichen. Nullwochen einschließen, keine nachträgliche Auswahl günstiger Nutzer. Ein gepoolter MAE gewichtet jede Nutzerwoche gleich; bei vier Testwochen pro Nutzer entspricht er dem Mittel der 100 Nutzer-MAEs. Es wurde weder für Baseline noch Regression ein MAE berechnet.

Regression liefert reelle Werte, auch Bruchteile und möglicherweise negative Zahlen, obwohl y ganzzahlig und nicht negativ ist. Primärbewertung mit unveränderten reellen Modellvorhersagen festlegen; nicht stillschweigend runden oder auf 0–10 begrenzen. Nichtnegative Nachbearbeitung oder Rundung gegebenenfalls vorab als separate Variante mit eigenem klar bezeichnetem MAE definieren. Negative Werte später als Modellgrenze berichten. Nichtnegative Baselinewerte sind aus aktuellen ganzzahligen Beobachtungen direkt gegeben.

## 9. Risiken und Einschränkungen

- Nur 26 Wochen und vier gemeinsame Testwochen: Ergebnisse stark vom Zeitraum abhängig; kein unabhängiger Test auf neuen Nutzern.
- 2.200 Zeilen sind keine 2.200 unabhängigen Beobachtungen: wiederholte Nutzer und überlappende Fenster; Nutzer- und Wochenabhängigkeiten beachten. Klassische unabhängige Fehlerannahmen nicht ungeprüft für Signifikanztests verwenden.
- Zähldaten mit vielen Nullen, begrenzter Simulation und möglicherweise variierender Streuung passen nicht ideal zu linearer Regression. Ein didaktischer Start, keine behauptete optimale Modellfamilie.
- Personenunterschiede und gegensätzliche Trends werden von einem gemeinsamen Koeffizientensatz nur begrenzt erfasst; Nutzer-ID ist kein numerisches Ersatzmerkmal.
- Nullfolgen nicht entfernen: sonst verzerrte Lernaufgabe und Bewertung. Nicht jede Null bedeutet eine fachlich bekannte Pause.
- Synthetische Daten liefern keinen Nachweis realer Prognoseleistung; Wetter, Saison und reale Messfehler sind nicht enthalten.

## 10. Offene Fragen für AP 4 und AP 5

AP 4: Zeitraster und gruppenbezogene Fenster implementieren und gegen Kontrollzählungen prüfen; Einwochen-Prognosezeitpunkt und Aufzeichnungsvollständigkeit festhalten; Schlüssel von Eingaben trennen; die 1.800/400 Zeilen und Zielgrenzen explizit prüfen. Festlegen, ob die optionale Vorwoche zusätzlich verwendet wird; keine Parameter anhand des finalen Tests wählen.

AP 5: Modell mit Achsenabschnitt nur auf Training fitten; bei Variantenvergleich zeitlich geordnete Validierung innerhalb der 18 Trainingszielwochen nutzen. Historie darf jeweils aus früheren Blöcken stammen. Baseline und Regression fair auf gleichen Testzeilen bewerten; Umgang mit negativen Vorhersagen vorab festlegen. Stabilität, Nutzerunterschiede und Fehler bei Nullwochen beschreiben, ohne weitere Modelle oder Güte jetzt vorwegzunehmen.

Keine Regression trainiert, kein K-Means ausgeführt, keine Labels, keine Modellgüte berechnet; keine synthetischen Daten, Simulationsparameter oder bestehenden Qualitätsberichte verändert. Kein Commit oder Pull Request.
