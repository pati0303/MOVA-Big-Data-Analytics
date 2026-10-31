# MOVA – Data-Preparation-Plan (AP 3.4 → AP 4)

Stand: 31.10.2026. Dieser Plan beschreibt die spätere Umsetzung der fünf CRISP-DM-Artefakte 3.1–3.5. Die Transformation wird erst in AP 4 implementiert. Keine Modelle, Clusterlabels, Prognosen oder vollständigen Modellierungstabellen wurden für diesen Plan erzeugt. Keine neue CRISP-DM-Iteration wird behauptet.

Verbindliche Grundlagen: [K-Means-Konzept](kmeans_feature_concept.md), [Regressionskonzept](regression_feature_concept.md), [Datenwörterbuch](data_dictionary.md), [aktive Version](active_data_version.json), [Konfiguration](simulation_config.md). Die Entscheidungen aus AP 3.2 und AP 3.3 bleiben bestehen.

## Datenvertrag und Reproduzierbarkeit

Ausschließlich aktive V2 aus data/raw/activities_simulated.csv, users_simulated.csv und offers_simulated.csv. Erwartet: 100 Nutzer, 6.465 Aktivitäten, acht Sportarten, 26 vollständige Montag-bis-Sonntag-Wochen vom 05.01. bis 05.07.2026. Vollständiges Raster: 2.600 Nutzerwochen, davon 558 Nullwochen. Master-Seed 42 und Exponent 1,3 sind Herkunftsparameter, keine Aufforderung zur Generierung.

AP 4 soll zuerst documentation/active_data_version.json lesen und die vier dokumentierten SHA-256-Werte einschließlich outputs/tables/simulation_weekly_check.csv prüfen. Bei abweichender Version oder Prüfsumme abbrechen, nicht auf historische V1 oder Vergleichskopien ausweichen. Die Wochenkontrolle dient als unabhängiger Vergleich; Aggregationen aus den aktiven Einzelaktivitäten neu ableiten. Keine Generatoren oder historischen Analyseskripte ausführen.

Eingangsdateien schreibgeschützt behandeln. Vorhandene Qualitätsberichte unverändert lassen. Ausgaben in einem eigenen Verzeichnis data/processed/ap4_v2/ planen; Berichte unter outputs/data_preparation/ap4_v2/. Vor Ausgabe Existenz und Herkunft prüfen; fremde oder abweichende Ergebnisse nicht still überschreiben. Validierung zuerst, Ausgabe erst danach. Deterministische Sortierung und Spaltenreihenfolge, UTF-8, ISO-Daten, Dezimalpunkt, keine zusätzliche CSV-Indexspalte; Floatwerte nicht vorzeitig runden. Versionen von Python und verwendeten Bibliotheken, Quell-Commit, Eingangs-/Ausgabehashes und Parameter im Laufmanifest dokumentieren. Ausgabedateien sind geplant, noch nicht vorhanden; neue Git-Freigaben/Ignore-Regeln vor späterer Versionierung prüfen.

## 3.1 Select Data

| Variable/Quelle | K-Means | Globale Regression | Begründung |
| --- | --- | --- | --- |
| users.user_id | Vollständige Nutzerliste und Join-Schlüssel | Vollständige Nutzerliste für Raster | Nutzer nicht durch innere Joins verlieren; niemals numerischer Modelleingang |
| activities.activity_id | Zählen und Eindeutigkeit prüfen | Zählen und Eindeutigkeit prüfen | Eine valide Zeile entspricht einer Aktivität |
| activities.user_id | Nutzeraggregation | Nutzer-Wochen-Aggregation | Fremdschlüssel vor Join prüfen |
| activities.date | Beobachtungszeitraum prüfen | Montag und week_index ableiten | Vollständiger gemeinsamer Zeitraum, zeitliche Korrektheit |
| activities.sport_type | Acht Anteile und Vielfalt | Alle Sportarten gemeinsam zählen, nur Qualitätskontrolle | Keine getrennte Sportartenregression |
| activities.duration_min | Wochenumfang zur Interpretation | Nur Eingangsqualität prüfen, kein erster Regressor | Nicht zusätzlich das Aktivitätsniveau doppelt gewichten |
| activities.distance_km | Nur Qualitätskontrolle | Nur Qualitätskontrolle | Sportartenübergreifend nicht vergleichbar, strukturell nicht anwendbar |
| users.interest_* | Außerhalb der Modellmatrix behalten | Kein Eingang | Freiwillige, unabhängig erzeugte Interessen sind kein beobachtetes Sportverhalten |
| offers.* | Keine Integration | Keine Integration | Katalog ohne Nutzerinteraktionen; kein Join auf Nutzer möglich |

Interessen bleiben in den unveränderten Rohdaten verfügbar und können später getrennt zur externen Beschreibung verbunden werden. Nicht als Labels verwenden und fehlende freiwillige Angaben künftig nicht als False auslegen. Datum, IDs, Umfang und Vielfalt gelangen nicht versehentlich durch Auswahl „aller numerischen Spalten“ in eine Modellmatrix: explizite Positivlisten verwenden. K-Means verwendet neun Eingänge; Regression zunächst zwei. Interne Profile, Trends und Cluster aus dem Gesamtzeitraum sind keine Regressionsmerkmale.

## 3.2 Clean Data

Grundsatz: prüfen, Fehler eindeutig berichten, bei harten Fehlern abbrechen. Kein automatisches Löschen, Imputieren, Winsorisieren oder Deduplizieren. Fachliche Korrekturen erfordern dokumentierte Ursache und Vorher-Nachher-Nachweis; aktive V2 nicht überschreiben.

| Prüfung | Geplante Umsetzung / Reaktion |
| --- | --- |
| Schema und Typen | Erwartete Spalten prüfen; IDs als Text; date strikt als gültiges ISO-Datum; Minuten/Distanz endlich numerisch, keine Inf-Werte; Interessen ausschließlich True/False; Angebotsrabatte ganzzahlig. Keine stillschweigende Umwandlung fehlerhafter Werte zu NaN. |
| Pflichtwerte | Leere activity_id, user_id, date, sport_type oder duration_min als Fehler melden. Nutzer- und Angebotskennungen ebenfalls Pflicht. |
| Doppelte IDs | activity_id, users.user_id und offer_id jeweils eindeutig. Identische Inhalte mit unterschiedlichen Aktivitäts-IDs nur markieren: zwei Aktivitäten am selben Tag sind möglich. Nicht anhand Datum/Nutzer deduplizieren. |
| Datum | Alle Aktivitäten innerhalb 05.01.–05.07.2026; Wochenmontage in definierter Liste; exakt 26 Projektwochen. Außerhalb liegende Zeilen nicht still wegfiltern. |
| Dauer | Negative oder nicht endliche Minuten als Fehler; 0 ist ein echter Zahlenwert, aber für aktive V2 außerhalb dokumentierter Sportgrenzen ebenfalls Fehler. Sportgrenzen anhand simulation_config.md prüfen; keine neuen Grenzwerte erfinden. |
| Nutzerreferenzen | Alle Aktivitäten müssen auf genau einen Nutzer der Nutzerdatei zeigen; unbekannte IDs abbrechen. Nutzer ohne Aktivitäten separat behandeln. |
| Sportarten | Genau Running, Cycling, Strength, Swimming, Walking, Hiking, Tennis, Padel zulässig; unbekannte Schreibweisen nicht unprotokolliert normalisieren. Alle acht in V2 erwartet. |
| Distanz | Bei Strength/Tennis/Padel leeres Feld = nicht anwendbar; nicht auf 0 setzen. Bei fünf Distanzsportarten fehlende, negative oder nicht endliche Distanz als Fehler. Unerwartete gemessene Distanz bei nicht anwendbarer Sportart markieren/abklären. Dokumentierte Geschwindigkeits-/Dauergrenzen inklusive Rundungstoleranz übernehmen. |
| Nullwochen | Abwesenheit einer Aktivitätsgruppe im vollständigen, verifizierten Raster bedeutet Zahl 0; keine fehlende Pflichtangabe einer Aktivitätszeile. Alle 558 bewahren. Bei künftigen realen Daten setzt diese Interpretation bestätigte Aufzeichnungsvollständigkeit voraus. |
| Ausreißer | Bestehende Hinweise aus AP 3.2 nutzen: U045 und hohe Präferenzanteile sind Prüfhinweise. Werte nicht allein aufgrund IQR entfernen oder begrenzen. Datenfehler von plausibler Besonderheit unterscheiden. |

Drei unterschiedliche Zustände: **fehlend/unbekannt** (z. B. ungültige Pflichtangabe oder unbekanntes Folgeziel), **nicht anwendbar** (leere Distanz bei Strength), **echte Null** (keine aufgezeichnete Aktivität in einer vollständig beobachteten Woche). Nur der letzte Fall ist als 0 zu zählen. Unbekannte Historie und unbekannte Zukunft niemals mit 0 füllen.

## 3.3 Construct Data

### A. K-Means – eine Zeile je Nutzer

Für Nutzer u: N_u = Anzahl Aktivitäten, T_u = summierte Minuten, N_us = Anzahl Aktivitäten der Sportart s. Alle Sportkategorien explizit in festgelegter Reihenfolge anlegen, fehlende Nutzer-Sport-Kombinationen mit Anzahl 0 ergänzen.

| Merkmal | Formel | Rolle |
| --- | --- | --- |
| avg_activities_per_week | N_u / 26 | Modelleingang |
| share_running, share_cycling, share_strength, share_swimming, share_walking, share_hiking, share_tennis, share_padel | jeweils N_us / N_u | Acht Modelleingänge, ein Sportmixbereich |
| avg_duration_per_week | T_u / 26 | Nur spätere Interpretation |
| sport_diversity | Anzahl Sportarten mit N_us > 0 | Nur spätere Interpretation |

Nicht durch aktive Wochen teilen. Aktive V2: alle 100 Nutzer haben N_u > 0; je Nutzer ergibt die Anteilssumme 1. Rohsummen N_u und T_u können im Validierungsprotokoll nachgewiesen werden, werden keine zusätzlichen Eingänge.

Regel für künftig vollständig inaktive Nutzer: in der vollständigen Nutzerübersicht behalten; Häufigkeit = 0, Umfang = 0, Vielfalt = 0, acht Anteile = fehlend/undefiniert, eligibility_status = inactive_no_sport_mix. Nicht in Sportmix-K-Means oder dessen Skalierungsfit aufnehmen; separat berichten, keinen künstlichen Nullmix oder Clusterlabel erzeugen. Aktuelle V2 bleibt dadurch unverändert: 100 berechtigte Nutzer. Ein kürzerer Beobachtungszeitraum erfordert einen neuen dokumentierten Datenvertrag; den Nenner nicht unbemerkt ändern.

### B. Regression – Raster vor Fenstern

1. user_id-Liste × 26 Montagen bilden: 2.600 eindeutige Schlüssel. Projektwoche 1 = 05.01.2026, Woche 26 = 29.06.2026; week_index = 1 + ganze Wochen seit 05.01.2026.
2. Aktivitäten je Nutzer/Montag über alle Sportarten zählen. In Raster einfügen, nur fehlende aggregierte Counts zu 0 ergänzen und als Ganzzahl speichern. Gegen die separate Wochenkontrolle vergleichen: 558 Nullen und Summe 6.465.
3. Nach user_id, week_start sortieren. c(u,t) = Wochenzahl. activities_current_week = c(u,t); avg_activities_last_4_weeks = [c(u,t)+c(u,t−1)+c(u,t−2)+c(u,t−3)]/4; optional activities_previous_week = c(u,t−1).
4. Gruppenbezogen trailing rolling(window=4, min_periods=4), kein zentriertes Fenster. Gruppenbezogen shift(−1) nur für activities_next_week = c(u,t+1). Zielwert nicht in Eingangsspalten übernehmen. Zielmontag = Eingabemontag + 7 Tage.
5. Eingabewochen 1–3 mangels Historie, Woche 26 mangels Folgeziel von verwendbaren Modellzeilen ausschließen. Im Grundraster verbleiben alle 2.600 Zeilen; Ausschlussgründe separat zählen (300 und 100). Wochen 1–3 dienen weiter als Historie; Woche 26 dient weiter als Ziel.

### Zeitliche Aufteilung und Verfügbarkeit

| Split | Eingabewochen t | Zielwochen t+1 | Zielzeitraum | Zeilen / Nutzer |
| --- | --- | --- | --- | --- |
| train | 4–21 | 5–22 | 02.02.–07.06.2026 | 1.800 / 18 |
| test | 22–25 | 23–26 | 08.06.–05.07.2026 | 400 / 4 |

2.200 verwendbare Zeilen, 81,82/18,18 %. Split nach Zielwoche für alle 100 Nutzer gleich, keine zufällige Zeilenmischung. Im Test rollierende Einwochenprognosen nach vollständigem Abschluss von t: beim ersten Testfall sind Wochen 19–22 bekannt; spätere tatsächlich beobachtete Testwochen dürfen frühere Historie für die nächste Prognose sein. Das ist keine gleichzeitige Vierwochenprognose am Ende von Woche 22. Kein Fit oder Nachtrainieren auf Testzielen; Modell-/Parameterwahl nur innerhalb chronologischer Trainingsvalidierung. Keine Gesamtzeitraum-Nutzermittel oder K-Means-Gruppen als Regressoren.

## 3.4 Integrate Data

K-Means: geprüfte Nutzerliste als führende Tabelle; Nutzeraggregate mit validierter 1:1-Beziehung links verbinden. Anzahl Zeilen und Nutzer vor/nach Join identisch, unbekannte Referenzen zuvor ausschließen durch Fehlerprüfung. Fehlende Aktivitätsaggregate erst dann gemäß Inaktivitätsregel behandeln.

Regression: vollständiges Nutzer-Wochen-Raster führend; aggregierte Counts über (user_id, week_start) in einer 1:1-Beziehung verbinden. Kalenderdimension 26 Wochen ist eindeutig; keine kartesische Vervielfachung außer dem beabsichtigten Raster. Wochenkontrolle nur unabhängig abgleichen, nicht zusätzlich als zweite Countquelle integrieren. Angebote und freiwillige Interessen gelangen nicht in die Modellmatrix.

IDs und Zeitreferenzen durch alle Stufen mitführen; sie sichern Nachvollziehbarkeit und Rückverknüpfung, werden vor Modellaufruf explizit aus X entfernt. K-Means- und Regressionstabellen bleiben getrennt. Alle 26 Wochen des K-Means-Datensatzes dürfen dessen exploratives Ziel beschreiben; dieselben aggregierten Informationen wären für frühere Regressionsprognosen Zukunftswissen.

## 3.5 Format Data

### K-Means: Skalierung und Bereichsgewichtung

Unskalierte Nutzertabelle mit 100 Zeilen und user_id + neun Eingängen + zwei Interpretationsmerkmalen (12 Spalten) planen. eligibility_status bei künftigen Daten gesondert im Prüfprotokoll führen. Exakte Eingangsreihenfolge: avg_activities_per_week, share_running, share_cycling, share_strength, share_swimming, share_walking, share_hiking, share_tennis, share_padel.

Auf den 100 berechtigten V2-Nutzern für jede Eingangsspalte Mittelwert μ und Populations-SD σ (ddof=0) bestimmen. z = (x−μ)/σ. Häufigkeit als z belassen; alle acht z-Anteile zusätzlich durch √8 teilen. Interpretation: eine Häufigkeitsdimension und ein aus acht Koordinaten bestehender Sportmix erhalten dieselbe aggregierte Varianzgewichtung, solange alle neun Spalten variieren. Dies ist die vereinbarte Startgewichtung, keine Garantie gleicher fachlicher Wirkung.

Nullvarianzregel: σ=0 vor Division erkennen, technischen Skalenfaktor 1 verwenden, konstante Spalte nach Zentrierung auf exakt 0 setzen und im Protokoll kennzeichnen. Nicht durch 0 dividieren; keine NaN/Inf-Ausgabe. Nahezu konstante Spalten gesondert markieren und anhand einer dokumentierten numerischen Toleranz prüfen. Den Faktor √8 nicht still anpassen. Wenn ein Anteil konstant ist, beträgt die Blockvarianz weniger als 1; falls die Häufigkeit konstant ist, entfällt ihr Beitrag. Dann fachliche Neubewertung protokollieren, keine automatische Optimierung. AP 3.2 weist für die aktuelle V2 bei allen neun Merkmalen positive SD aus; Nullvarianzbehandlung in AP 4 zusätzlich mit kleinen schematischen Testvektoren prüfen, ohne Simulationsdaten zu ändern.

Alle acht Anteile behalten: Summe 1 bedeutet sieben unabhängige Freiheitsgrade; Standardisierung entfernt diese Abhängigkeit nicht. K-Means benötigt keine invertierbare Kovarianzmatrix. Keine beliebige Sportart streichen. Gleiche Prozentpunktunterschiede können nach Einzelstandardisierung unterschiedlich wirken, besonders bei klein streuenden Sportarten. Umfang und Vielfalt nicht skalieren und nicht in X aufnehmen, sondern unskaliert für Interpretation behalten. Später Clusterstabilität und Interpretierbarkeit bei vorab begrenzten Gewichtungsvarianten prüfen; jede Änderung begründen, nicht gewünschte Labels erzwingen.

Skalierungsparameter, Spaltenreihenfolge und Faktor persistent dokumentieren. Neue Nutzer nur transformieren, nicht unbemerkt neu fitten. Bei späteren Teilmengen-/Stabilitätsstudien auf jeweils vorgesehenem Fitbestand skalieren. Rücktransformation von Zentren muss zunächst Anteilgewichtung rückgängig machen (×√8), dann Standardisierung umkehren.

### Regression: Schema und getrennte Rollen

| Spalte | Typ | Rolle |
| --- | --- | --- |
| user_id | Text | Identifikation, nicht X |
| week_index | Ganzzahl | Relative Eingabewoche, nicht X |
| week_start | ISO-Datum | Audit/Zuordnung, nicht X |
| target_week_start | ISO-Datum | Audit/Split, nicht X |
| activities_current_week | Nicht negative Ganzzahl | X |
| avg_activities_last_4_weeks | Endliche Dezimalzahl | X |
| activities_next_week | Nicht negative Ganzzahl | y |
| split | Text: train oder test | Auswahl, nicht X |

Damit acht Spalten im geplanten Basisexport; numerischer Modellkern sind exakt die zwei X-Spalten und y, Metadaten sind bewusst nicht numerisch. Optional activities_previous_week nur in explizit benannter Variante hinzufügen. Kein One-Hot-Encoding der IDs. Keine notwendige Skalierung für diesen ersten linearen Ansatz; falls später verwendet, nur am Training fitten. Zielvariable nicht standardisieren, runden oder in Float-Vorhersagen umdeuten. Lineare Regression kann später reelle und negative Vorhersagen erzeugen; primären MAE auf unveränderten reellen Vorhersagen planen, Nachbearbeitung nur als separat vorab definierte Variante. Jetzt keine Prognosen oder MAE berechnen.

## Automatisierbare Validierung und Abnahmekriterien für AP 4

Alle folgenden Regeln sind geplante Assertions, noch kein ausgeführter AP-4-Abnahmebericht.

| Stufe | Konkrete Assertion |
| --- | --- |
| Herkunft | active_version=V2; vier SHA-256-Prüfsummen stimmen; Rohdateien und bestehende Reports vor/nach Lauf unverändert |
| Rohdaten | 100 eindeutige Nutzer, 6.465 eindeutige Aktivitäts-IDs, acht zugelassene Sportarten; keine fehlenden Pflichtwerte/ungültigen Typen; bekannte Nutzerreferenzen; gültiger Zeitraum |
| Wochenaggregation | Exakte Übereinstimmung mit allen 2.600 Kontrollzählungen; Summe Counts=6.465; Counts ganzzahlig und ≥0 (V2 zusätzlich ≤10) |
| Raster | 100×26=2.600 Zeilen, jede Nutzer-Woche genau einmal, pro Nutzer 26 chronologische Wochen in 7-Tage-Schritten; genau 558 Counts=0 |
| Nullwochen-Erhalt | 558 gilt für das vollständige Raster, nicht zwingend für die gefilterten 2.200 Modellzeilen; deren Nullzahlen separat berichten, keinen falschen Sollwert erzwingen |
| Nutzertabelle | 100 Zeilen, eine je Nutzer, vollständige ID-Menge; 100 V2-Nutzer berechtigt; Häufigkeit=N_u/26, Umfang=T_u/26; Summen rekonstruieren Gesamtdaten |
| Sportmix | Alle acht Spalten; Anteile in [0,1], Summe mit absoluter Toleranz 1e−10 gleich 1; diversity entspricht Anzahl positiver Sportcounts, in V2 4–8; keine Nullaktivitätsdivision |
| Modellmatrix K-Means | 100×9 numerische Werte plus separat geführte IDs; keine NaN/Inf; Reihenfolge explizit; Umfang/Vielfalt/IDs nicht in X |
| Skalierung | Mittelwerte der transformierten Spalten näherungsweise 0; Varianz(ddof=0) bei variierenden Häufigkeiten 1, je variierendem gewichteten Anteil 1/8 (numerische Toleranz z. B. 1e−10); Konstanten exakt 0; Parameter-/Inverse-Rundlauf prüfen |
| Fenster | Für jede verwendbare Zeile Mittel exakt aus t−3…t; Vorwoche aus t−1; Ziel exakt aus t+1 desselben Nutzers; keine Nutzergrenzüberschreitung; mindestens vier bekannte Wochen |
| Verwendbarkeit | 300 frühe und 100 letzte Grundrasterzeilen nicht verwendbar; 2.200 eindeutige Modellzeilen, 22 je Nutzer; t=4…25 |
| Split | 1.800 train/400 test; je Nutzer 18/4; Trainingsziele Wochen 5…22, Testziele 23…26; maximale Trainingszielwoche vor minimaler Testzielwoche |
| Leakage | X-Positivliste exakt zwei Spalten; alle vier Eingangsdatenzeitpunkte ≤t, Zielzeitpunkt=t+1; keine Ziel-/Split-/ID-Spalte in X; Fit-/Parameterwahl nur auf Training |
| Kausalitätstest | Bei testweisen Änderungen künftiger Counts im isolierten Speicher dürfen frühere Eingangsmerkmale unverändert bleiben; Ziel darf sich nur an korrekter Vorzeile ändern. Keine Änderung der CSV-Quellen |
| Ausgabe | CSV erneut laden: Typvertrag, Schlüssel, Zeilenzahlen, Spaltenreihenfolge und numerische Übereinstimmung prüfen; keine Cluster-/Prognosespalten; zweite identische Ausführung liefert identische Dateninhalte |

Zusätzlich kleine handgeprüfte Fälle für fehlende Wochen, Nutzerwechsel, konstante Features und abgeschnittene Historie vorsehen. Dies sind technische Tests, keine neuen synthetischen Forschungsdatensätze. Keine Modelltrainingstests in AP 4.

## Vorher-Nachher-Beispiele für Präsentation und späteren Bericht

Die Beispiele 1–5 stammen **tatsächlich aus aktiver V2**. U001 ist eine bereits synthetische Nutzerkennung ohne Realpersonenbezug. Abgeleitete Ergebnisse wurden nur für diesen Nutzer anhand der Quelldaten nachgerechnet; sie sind keine gespeicherten Modellierungstabellen. AP 4 soll die späteren Skriptausgaben gegen diese Beispiele prüfen. Beispiel 6 ist ausdrücklich schematisch.

### 1. Rohdaten → ausgewählte Variablen (tatsächlich)

- Ausgang: activity_id=A000521, user_id=U001, date=2026-01-19, sport_type=Running, duration_min=43.7, distance_km=5.72.
- Verarbeitung: Nach Qualitätsprüfung für den Regressionszweig activity_id/user_id/date zur Zählung und Datierung auswählen; sport_type zur Gültigkeitsprüfung behalten, aber alle Sportarten gemeinsam zählen. Distanz/Dauer nicht in X übernehmen.
- Ergebnis: A000521, U001, 2026-01-19 → eine zu zählende Aktivität. Für K-Means bleibt Running zur Anteilsberechnung und 43.7 zur Umfangsinterpretation erhalten.
- Begründung: Modellzwecke benötigen unterschiedliche Information; keine willkürliche numerische Kodierung von IDs oder Sportnamen.

### 2. Aktivitäten → Wochenaggregation (tatsächlich)

- Ausgang: U001 hat am 19.01.2026 Running (A000521, 43.7 Minuten) und am 22.01.2026 Cycling (A000651, 102.3 Minuten); dies sind sämtliche Aktivitäten dieses Nutzers in dieser Woche.
- Verarbeitung: Beide Daten dem Montag 19.01.2026 zuordnen und Zeilen zählen.
- Ergebnis: user_id=U001, week_start=2026-01-19, week_index=3, activity_count=2. Beide Sportarten zählen gleich als Aktivität.
- Begründung: Gemeinsame Wochenzählung für das globale Regressionsziel.

### 3. Fehlende Aktivitätsgruppe → ergänzte Nullwoche (tatsächlich)

- Ausgang: U001 besitzt keine Aktivitätszeile für 05.–11.01.2026. Eine allein aus Aktivitäten gruppierte Tabelle enthält diesen Schlüssel nicht.
- Verarbeitung: Vollständiges Nutzerraster links mit Wochenzählungen verbinden; fehlende Countgruppe im bestätigten Zeitraum zu 0 ergänzen.
- Ergebnis: U001, week_start=2026-01-05, week_index=1, activity_count=0. Entspricht der vorhandenen Wochenkontrolle.
- Begründung: Keine Aktivität ist eine Beobachtung, keine aus dem Nenner zu entfernende Woche. Es wird keine künstliche Aktivitätszeile mit Null-Dauer angelegt.

### 4. Aktivitäten → K-Means-Nutzermerkmale (tatsächlich)

- Ausgang: U001 hat insgesamt 34 Aktivitäten und 2.086,0 Minuten: Running 17, Cycling 3, Walking 11, Hiking 3; übrige vier Sportarten 0.
- Verarbeitung: Anzahl und Minuten durch 26, Sportcounts durch 34 teilen; positive Sportcounts zählen.
- Ergebnis: avg_activities_per_week=34/26=1,307692; share_running=17/34=0,5; share_cycling=3/34=0,088235; share_strength=0; share_swimming=0; share_walking=11/34=0,323529; share_hiking=3/34=0,088235; share_tennis=0; share_padel=0. Interpretation: avg_duration_per_week=2086/26=80,230769; sport_diversity=4. Exakte Brüche summieren sich zu 1, Anzeigerundungen können minimal abweichen.
- Begründung: Nullwochen über den Nenner erhalten; Sportmix von Aktivitätsniveau trennen. Noch keine skalierten Ergebnisse behaupten.

### 5. Wochenwerte → Regressionsmerkmale (tatsächlich)

- Ausgang U001: Wochen 1–5 haben Counts [0, 0, 2, 0, 1]; Montage 05.01., 12.01., 19.01., 26.01., 02.02.2026.
- Verarbeitung für t=4: trailing Mittel aus Wochen 1–4; Folgewoche separat als Ziel verschieben.
- Ergebnis: user_id=U001, week_index=4, week_start=2026-01-26, activities_current_week=0, avg_activities_last_4_weeks=(0+0+2+0)/4=0,5, optional activities_previous_week=2; target_week_start=2026-02-02, activities_next_week=1, split=train.
- Begründung: Das Ziel 1 darf nicht in den Mittelwert eingehen. Wochen 1–3 liefern keine vollständigen Modellzeilen, bleiben aber für diesen Rückblick notwendig.

### 6. Standardisierung/Nullvarianz (nur schematisch)

- Ausgang: Eine Merkmalsspalte hat bei allen berechtigten Nutzern Wert 0,2, daher μ=0,2 und σ=0.
- Verarbeitung: Konstante erkennen, Skalenfaktor 1, z=(0,2−0,2)/1=0; bei Sportanteil danach 0/√8=0.
- Ergebnis: Endliche Nullspalte und protokollierter Nullvarianzhinweis, kein NaN/Inf. Dies ist kein beobachteter V2-Befund.
- Begründung: Technisch definierte Behandlung ohne Null-Division; abweichende Bereichsgewichtung fachlich sichtbar machen.

## Geplante Python-Skripte und Ausgabedateien – erst AP 4

| Geplante Datei | Aufgabe |
| --- | --- |
| src/data_preparation.py | CLI-Orchestrierung: Pfade relativ zum Repository, V2-Gate, Qualitätsprüfung, getrennte Zweige, Validierung vor Export; keine Generator-/Trainingsaufrufe |
| src/preparation_validation.py | Wiederverwendbare Datenverträge, Summen-/Zeit-/Leakage-Prüfungen und Vorher-Nachher-Protokollierung |
| tests/test_data_preparation.py | Fachliche Prüfungen mit den obigen realen Beispielen und kleinen isolierten Grenzfällen; Rohdaten unverändert |
| data/processed/ap4_v2/kmeans_users.csv | 100 Zeilen, ID + neun unskalierte Eingänge + zwei Interpretationsmerkmale |
| data/processed/ap4_v2/kmeans_input_scaled.csv | 100 Zeilen, ID + neun standardisierte/gewichtete Spalten; ID vor Modellaufruf entfernen |
| data/processed/ap4_v2/kmeans_scaling.json | Fitpopulation, Spaltenfolge, μ, σ, technischer Skalenfaktor, Nullvarianzstatus, ddof=0 und Faktor 1/√8 |
| data/processed/ap4_v2/user_week_grid.csv | 2.600 Zeilen; user_id, week_start, week_index, activity_count; alle 558 Nullwochen |
| data/processed/ap4_v2/regression_modeling.csv | 2.200 Zeilen mit acht Basisspalten und train/test-Kennzeichen; keine optionalen Eingänge still hinzufügen |
| outputs/data_preparation/ap4_v2/validation_report.md | Soll/Ist, Bestanden/Fehler, Ausschlussgründe, Nullzahlen pro Stufe und Abweichungen |
| outputs/data_preparation/ap4_v2/transformation_examples.md | Mindestens fünf reale Vorher-Nachher-Nachweise mit Herkunft/Schlüsseln und Formeln |
| outputs/data_preparation/ap4_v2/run_manifest.json | Eingangs-/Ausgabehashes, Quell-Commit und Arbeitsstand, Bibliotheksversionen, Schema, Parameter und Zeilenzahlen |

Keine zusätzlichen Train/Test-Kopien nötig: Auswahl über split reicht. CSV-Typen im Manifest verbindlich definieren, da CSV keine Typdeklarationen speichert. Optionale Vorwochenvariante nur separat benennen, falls beschlossen. Keine dieser geplanten Dateien oder Skripte wurde in AP 3.4 implementiert.

## Risiken, offene Entscheidungen und Übergabe an AP 4

Festgelegt: aktive V2, 26-Wochen-Nenner, neun K-Means-Eingänge plus zwei Interpretationsmerkmale; Startskalierung z und z/√8; Regressionsbasis mit zwei Eingängen, globalem Ziel und unverändertem 1.800/400-Split. Vollständig inaktive künftige Nutzer werden separat dokumentiert und nicht mit undefiniertem Sportmix geclustert.

Offen: optionale Aufnahme der Vorwoche als separate Regressionsvariante; spätere begrenzte Gewichtungssensitivität anhand Clusterstabilität/Interpretation; konkreter Softwareversions-Lock und gewünschte Versionierung generierter AP-4-Ausgaben. Testzielwerte dürfen keine dieser Entscheidungen steuern. Negative Prognosen sind eine spätere Modellgrenze, kein jetzt zu bereinigendes Ziel. Synthetische Daten und nur vier Testwochen begrenzen jede spätere Aussage; 2.200 zeitabhängige Zeilen sind keine unabhängigen Fälle. Noch keine Modellgüte vorwegnehmen.

Empfohlene Implementierungsreihenfolge:

1. V2-Eingangskontrolle, Schema und nicht destruktive Qualitätsprüfungen implementieren.
2. Gemeinsame Kalenderzuordnung, Wochenaggregation und vollständiges Raster aufbauen und gegen Kontrolle prüfen.
3. Unskalierte K-Means-Nutzermerkmale und Interpretation berechnen; IDs/Anteile/Summen prüfen.
4. Neun K-Means-Eingänge skalieren/gewichten, Parameter und Nullvarianzbehandlung prüfen.
5. Nutzerbezogene Regressionsfenster/Ziele und chronologischen Split aufbauen; Beispiele, Zeilen und zeitliche Verfügbarkeit prüfen.
6. Erst nach allen Prüfungen deterministisch exportieren, erneut einlesen, Vorher-Nachher-Bericht und Manifest schreiben; Datenwörterbuch um tatsächlich erzeugte Variablen/Pfade ergänzen.

Abnahme von AP 4 erfolgt anhand überprüfter Datenartefakte und Dokumentation, nicht anhand trainierter Modelle. Modellierung und Vergleich mit der Persistenzbaseline gehören erst in AP 5.
