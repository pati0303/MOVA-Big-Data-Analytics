# MOVA – Merkmalskonzept für K-Means (AP 3.2)

Stand: 31.10.2026. CRISP-DM: 2.3 Explore Data, 3.1 Select Data und Planung von 3.3 Construct Data.

## Ziel und Datenbasis

Nutzer anhand von Aktivitätsniveau und persönlichem Sportartenmix gruppieren. K-Means soll Ähnlichkeiten ohne vorgegebene Labels erkennen. Es wird weder eine Zahl sinnvoller Cluster noch deren Existenz vorausgesetzt.

Ausschließlich aktive V2: data/raw/activities_simulated.csv, users_simulated.csv und offers_simulated.csv. 100 Nutzer, 6.465 Aktivitäten, 30 Angebote; 26 vollständige Wochen vom 05.01. bis 05.07.2026. 2.600 Nutzerwochen, davon 558 ohne Aktivität. Alle im Manifest documentation/active_data_version.json aufgeführten SHA-256-Werte wurden vor und nach der Arbeit bestätigt. Master-Seed 42, Exponent 1,3 sind dokumentierte Herkunftsparameter; keine Neugenerierung.

Die Berechnungen wurden für alle 100 Nutzer tatsächlich ausgeführt, ausschließlich im Arbeitsspeicher. Python 3.12 mit pandas 2.2.3 und NumPy 2.3.5; Stichproben-SD (ddof=1), linear interpolierte Quartile, Pearson-Korrelation; ergänzend Spearman für Häufigkeit/Umfang. Reproduktionscode: work/document_features.py (lokales Arbeitsskript, kein Modellartefakt). Es wurden keine Modelle, Labels, Grafiken oder vollständigen Merkmalstabellen gespeichert. Historische V1-Berichte wurden nicht als V2-Ergebnisse verwendet.

## Geplante Merkmale und Formeln

Sei N_u die Anzahl Aktivitäten von Nutzer u im Gesamtzeitraum, T_u deren summierte Dauer in Minuten und N_us die Aktivitätszahl der Sportart s.

- avg_activities_per_week = N_u / 26 (Aktivitäten/Woche).
- avg_duration_per_week = T_u / 26 (Minuten/Woche).
- share_running, share_cycling, share_strength, share_swimming, share_walking, share_hiking, share_tennis, share_padel: jeweils N_us / N_u (Anteil 0–1).
- sport_diversity = Anzahl Sportarten mit N_us > 0 (Ganzzahl 0–8).

Alle 100 Nutzer haben mindestens eine Aktivität: sämtliche Merkmale sind ohne Imputation berechenbar und haben keine fehlenden Werte. Nullwochen bleiben über den festen Nenner 26 enthalten; nicht durch die Zahl aktiver Wochen teilen. Bei künftigen Nutzern ohne Aktivität sind Sportanteile undefiniert: nicht automatisch acht Nullen als normalen Sportmix verwenden; gesonderte Entscheidung in AP 4.

## Tatsächliche deskriptive Ergebnisse

Alle Angaben beziehen sich auf die Verteilung über 100 Nutzer; Sportanteile sind Bruchteile, beispielsweise 0,20 = 20 %. Mittelwerte der Nutzeranteile sind keine gepoolten Anteile aller Aktivitäten.

| Merkmal | Mittel | SD | Minimum | Q1 | Median | Q3 | Maximum |
| --- | --- | --- | --- | --- | --- | --- | --- |
| avg_activities_per_week | 2.4865 | 1.2934 | 0.3462 | 1.5288 | 2.2115 | 3.4327 | 6.1923 |
| avg_duration_per_week | 162.6269 | 98.2414 | 21.7000 | 88.5769 | 141.5923 | 223.7183 | 432.5192 |
| share_running | 0.1528 | 0.1638 | 0.0000 | 0.0503 | 0.0991 | 0.1926 | 0.8023 |
| share_cycling | 0.1636 | 0.1598 | 0.0000 | 0.0371 | 0.1237 | 0.2374 | 0.7143 |
| share_strength | 0.1240 | 0.1622 | 0.0000 | 0.0243 | 0.0690 | 0.1521 | 0.7432 |
| share_swimming | 0.0926 | 0.1452 | 0.0000 | 0.0106 | 0.0377 | 0.0928 | 0.6835 |
| share_walking | 0.1951 | 0.1582 | 0.0000 | 0.0695 | 0.1600 | 0.2656 | 0.7241 |
| share_hiking | 0.1370 | 0.1310 | 0.0000 | 0.0313 | 0.1000 | 0.2026 | 0.5641 |
| share_tennis | 0.0689 | 0.0824 | 0.0000 | 0.0061 | 0.0405 | 0.1000 | 0.3793 |
| share_padel | 0.0658 | 0.0767 | 0.0000 | 0.0133 | 0.0396 | 0.0850 | 0.3684 |
| sport_diversity | 6.9500 | 1.1044 | 4.0000 | 6.0000 | 7.0000 | 8.0000 | 8.0000 |

Sportartenvielfalt:

| Sportarten | Nutzer |
| --- | --- |
| 4 | 2 |
| 5 | 12 |
| 6 | 15 |
| 7 | 31 |
| 8 | 40 |

### Notwendige Zusammenhänge

- Häufigkeit ↔ Umfang: Pearson r = 0,9073; Spearman rho = 0,9243. Starke Überlappung, aber keine Identität: Dauer je Aktivität und Sportmix unterscheiden sich.
- Vielfalt ↔ Häufigkeit: r = 0,5408; Vielfalt ↔ Umfang: r = 0,4810. Mehr Aktivitäten erhöhen auch die Chance, seltene Sportarten wenigstens einmal zu beobachten.
- Umfang ↔ Hiking-Anteil: r = 0,2797; Umfang ↔ Cycling: 0,2011. Wochenminuten enthalten zusätzlich sportartspezifische Dauereffekte und sind kein Maß physiologischer Intensität.
- Paarweise Korrelationen zwischen Sportanteilen liegen zwischen −0,2712 (Running/Tennis) und +0,0836 (Padel/Tennis). Geringe paarweise Werte beseitigen die exakte Summenabhängigkeit nicht: alle acht Anteile summieren sich pro Nutzer auf 1 (numerisch bis auf Gleitkommafehler).

### Ausreißerhinweise

Regel: Werte außerhalb [Q1 − 1,5 × IQR; Q3 + 1,5 × IQR], IQR = Q3 − Q1. Das sind univariate Prüfhinweise, keine bestätigten Fehler und keine multivariate Ausreißerprüfung.

| Merkmal | Anzahl IQR-Hinweise |
| --- | --- |
| avg_activities_per_week | 0 |
| avg_duration_per_week | 1 |
| share_running | 9 |
| share_cycling | 4 |
| share_strength | 7 |
| share_swimming | 11 |
| share_walking | 3 |
| share_hiking | 2 |
| share_tennis | 5 |
| share_padel | 8 |
| sport_diversity | 0 |

Beim Umfang liegt U045 mit 432,5192 Minuten/Woche knapp oberhalb der oberen IQR-Grenze von 426,4303. Für Häufigkeit und Vielfalt gibt es keine IQR-Hinweise. Hohe Sportanteile bis 0,8023 (Running) zeigen ausgeprägte Präferenzen; sie sind fachlich gerade für das Clustering relevant. Keine automatische Entfernung oder Kappung. K-Means reagiert aufgrund quadrierter Abstände empfindlich auf extreme Beobachtungen; Einfluss später anhand der Profile prüfen.

## Kritische Bewertung und Skalierung

K-Means minimiert quadrierte euklidische Abstände. Ohne Skalierung dominieren Wochenminuten (21,70–432,52) gegenüber Häufigkeit (0,35–6,19) und Anteilen (0–1). Standardisierung bedeutet z = (x − Mittelwert) / Standardabweichung: Mittelwert 0 und Varianz 1 pro nicht konstantem Merkmal. Für die geplante Transformation verwenden wir Populations-SD (ddof=0, wie StandardScaler); die oben berichtete beschreibende SD verwendet ddof=1. Konstanten vor Skalierung prüfen.

Acht Anteile sind kompositionell: ihre Summe ist exakt 1, sie enthalten nur sieben unabhängige Freiheitsgrade. Ein höherer Anteil erzwingt niedrigere andere Anteile. Alle acht können dennoch in K-Means eingehen; es wird keine invertierbare Kovarianzmatrix benötigt. Das willkürliche Weglassen einer Sportart verändert euklidische Abstände und bevorzugt die verbleibenden Koordinaten. Es ist daher keine neutrale Reparatur. Standardisierung jedes Anteils vergrößert außerdem Unterschiede in Sportarten mit kleiner SD (beispielsweise Padel SD 0,0767 gegenüber Running 0,1638); gleiche Prozentpunktunterschiede erhalten dann unterschiedliche Bedeutung.

Häufigkeit und Umfang parallel betonen das Aktivitätsniveau doppelt. Vielfalt ist aus den positiven Sportanteilen bereits ableitbar, hängt von der Beobachtungsmenge ab und zeigt eine Deckennähe (71 Nutzer mit sieben/acht Sportarten). Distanz wäre sportartenübergreifend schwer vergleichbar und fehlt fachlich bei Strength, Tennis und Padel. Aktivitätszahl oder Gesamtminuten zusätzlich zu ihren Wochenmitteln wären bei identischen 26 Wochen exakt redundant.

### Fachlich sinnvolle Gewichtungsoptionen

| Option | Wirkung und Abwägung |
| --- | --- |
| Alle Merkmale einzeln standardisieren, gleich gewichten | Einfach, aber acht Anteilsspalten erhalten zusammen deutlich mehr Gewicht als eine Niveauspalte; seltene/klein streuende Anteile werden verstärkt. Nur bewusste Vergleichsvariante. |
| Standardisierung plus Bereichsgewichtung | Empfohlener erster Ansatz: Häufigkeit als Niveau; acht Anteile als Sportmix. Nach Standardisierung Anteilsspalten jeweils mit 1/√8 multiplizieren. Beide Bereiche haben so dieselbe Summe ihrer Koordinatenvarianzen. |
| Anteile im ursprünglichen Maßstab mit gemeinsamem Bereichsfaktor | Gleiche Prozentpunktabstände bleiben gleichwertig. Einen gemeinsamen Faktor für den gesamten Anteilblock verwenden, etwa inverse Wurzel der Summe seiner Varianzen, und Häufigkeit standardisieren. Häufigere/stärker streuende Sportanteile prägen dann den Mix stärker. Sinnvolle Sensitivitätsvariante. |
| Log-Verhältnisse (z. B. ILR) | Berücksichtigen kompositionelle Geometrie; vorhandene Nullanteile benötigen eine fachlich begründete Nullwertbehandlung. Komplexer und deshalb vorerst zurückgestellt. |

Vorgesehener Start: z(Häufigkeit) sowie z(share_s)/√8 für alle acht Sportarten. Im quadrierten Abstand ergeben sich ein Niveau-Beitrag und der mittlere Beitrag der acht standardisierten Sportkoordinaten. Dies gleicht die aggregierte Streuung aus, garantiert aber keine identische fachliche Wirkung oder unabhängige Informationen. Gewichtung 50:50 ist eine transparente Startannahme, kein datengetriebenes Optimum. Es wurde weder skaliert gespeichert noch eine Clusterlösung optimiert.

## Empfohlene Merkmalsauswahl

### A – Für unseren ersten Ansatz erforderlich

- avg_activities_per_week: verständliches Maß des Aktivitätsniveaus, einschließlich Nullwochen.
- Alle acht share_*-Merkmale: vollständiger und symmetrischer Sportmix, zentrale Information für das Projektziel. Als ein Merkmalsbereich gewichten.

Damit neun Eingabespalten für das erste Modell. „Erforderlich“ bezieht sich auf dieses fachliche Konzept, nicht auf eine mathematische Voraussetzung von K-Means.

### B – Sinnvolle zusätzliche Merkmale

- avg_duration_per_week: tatsächlich berechenbar und fachlich nützlich als Umfang. Zunächst zur Beschreibung späterer Gruppen, dann gegebenenfalls als vorab begründete Sensitivitätsvariante. Bei gemeinsamer Aufnahme mit Häufigkeit beide innerhalb eines einzigen Niveaublocks mit jeweils 1/√2 gewichten, damit der Block nicht allein durch seine Spaltenzahl gewinnt; dies entfernt die Korrelation nicht.
- sport_diversity: zunächst ergänzende Profilkennzahl zur Interpretation; nur bei explizitem Ziel „Repertoirebreite“ als zusätzliches Eingabemerkmal erwägen. Gefahr doppelter Gewichtung und Deckeneffekt dokumentieren.

### C – Zunächst aus den K-Means-Eingaben ausschließen

- avg_duration_per_week und sport_diversity aus dem Basismodell: Gründe wie oben; keine Löschung der Rohinformationen.
- user_id, activity_id, offer_id, rohe Datumswerte: Identifikatoren beziehungsweise zeitliche Zuordnung, keine sinnvollen numerischen Distanzen zwischen Nutzern.
- Interessen: unabhängige freiwillige Selbstauskünfte, kein beobachtetes Sportverhalten; später allenfalls externe Beschreibung, keine Ziel- oder Clusterlabels.
- Angebotsvariablen: Katalog ohne nutzerspezifische Interaktionen; keine Grundlage für Verhaltenscluster.
- Distanz: Sportarten nicht direkt vergleichbar, strukturell nicht anwendbare Werte; zunächst kein Gesamt-Distanzmerkmal.
- Gesamtaktivitäten/Gesamtminuten zusätzlich zu Wochenmitteln: exakt redundante Skalierungen bei gleichem Zeitraum.
- Interne Simulationsprofile und Trendmechanismen: keine vorhandenen Rohdatenspalten und keine vorgegebenen Labels verwenden.

## Offene Fragen für AP 4

1. Bestätigt das Team die gleiche Startgewichtung von Niveau und Sportmix, oder soll ein Bereich fachlich wichtiger sein? Vor Modellergebnissen festlegen und begrenzte Sensitivitätsvarianten dokumentieren.
2. Neun Basismerkmale verbindlich festlegen; Umfang/Vielfalt zunächst nur zur Interpretation oder als zusätzliche Modellvarianten? Keine nachträgliche Optimierung auf gewünschte Gruppen.
3. Nullwochen im 26-Wochen-Nenner bewahren; Umgang mit zukünftigen vollständig inaktiven Nutzern sowie kürzeren Beobachtungsfenstern definieren.
4. Transformation, Nullvarianzprüfung, ID-Zuordnung und Datenherkunft reproduzierbar implementieren; skalierte und unskalierte Merkmale sauber trennen. Bei zeitlicher Evaluation Transformationen nur auf dem jeweiligen Trainingsbestand anpassen.
5. Empfindlichkeit gegenüber hohen Präferenzanteilen und U045 prüfen; keine automatische Ausreißerbereinigung.
6. Erst im Modellierungsschritt Clusterzahl, Initialisierungen, Stabilität und Interpretierbarkeit prüfen. Keine vorhandene Clusterstruktur oder reale Übertragbarkeit aus synthetischen Daten ableiten.

AP 3.2 plant Merkmale und beschreibt bestehende Daten. Vollständige Data Preparation, Modelltraining und Clusterlabels stehen aus.
