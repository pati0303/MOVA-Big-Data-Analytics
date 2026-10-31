# MOVA – Datenwörterbuch

Stand: 31.10.2026, aktive V2. Die folgenden Rohvariablen existieren tatsächlich in den drei CSV-Dateien unter data/raw. Die später aufgeführten K-Means-Merkmale sind geplant und nur für AP 3.2 im Arbeitsspeicher geprüft; sie sind keine bestehenden CSV-Spalten und keine gespeicherte Modellierungstabelle.

CSV besitzt keine verbindlichen Typdeklarationen; angegeben sind die aus den tatsächlichen Inhalten abgeleiteten logischen Datentypen. Alle Beobachtungen sind synthetisch. Zeitraum 05.01.–05.07.2026, 26 Wochen; 100 Nutzer, 6.465 Aktivitäten und 30 Angebote.

## Vorhandene Rohvariablen: activities_simulated.csv

Eine Zeile entspricht einer Aktivität. user_id verbindet Aktivitäten mit Nutzern; nicht mit Angeboten.

| Name | Bedeutung | Datentyp | Einheit | Fehlende Werte | Geplante Verwendung |
| --- | --- | --- | --- | --- | --- |
| activity_id | Aktivitätskennung | Text | keine | keine | Identifikation und Eindeutigkeitsprüfung; kein Clusteringmerkmal |
| user_id | Nutzerkennung | Text | keine | keine | Verknüpfung und Gruppierung; kein numerischer Eingang |
| date | Datum der Aktivität | ISO-Datum YYYY-MM-DD | Kalendertag | keine | Zeitraum-/Wochenzuordnung; kein direkter Eingang |
| sport_type | Ausgeübte Sportart | kategorialer Text | eine von acht Sportarten | keine | Sportanteile und Vielfalt ableiten |
| duration_min | Trainingsdauer | Dezimalzahl | Minuten je Aktivität | keine | Wochenumfang ableiten, vorerst beschreibend |
| distance_km | Zurückgelegte Distanz | nullable Dezimalzahl | Kilometer je Aktivität | 1.698 leere Felder: Strength 851, Tennis 434, Padel 413; dort nicht anwendbar | Vorerst kein Clusteringmerkmal; fehlend weder pauschal 0 noch imputieren |

Sportarten: Running, Cycling, Strength, Swimming, Walking, Hiking, Tennis, Padel. Bei den fünf Distanzsportarten fehlen keine Distanzen. Dauern sind auf eine, Distanzen auf zwei Nachkommastellen gerundet. Eine Nutzerwoche ohne Aktivität ist keine Rohdatenzeile mit leerer Distanz.

## Vorhandene Rohvariablen: users_simulated.csv

Eine Zeile pro Nutzer. Die Interessen sind unabhängig erzeugte freiwillige Interessenangaben, keine Sportprofile oder Clusterlabels.

| Name | Bedeutung | Datentyp | Einheit | Fehlende Werte | Geplante Verwendung |
| --- | --- | --- | --- | --- | --- |
| user_id | Eindeutige Nutzerkennung | Text | keine | keine | Grundgesamtheit und Verknüpfung; kein Clusteringmerkmal |
| interest_sport | Interesse an Sport | Boolean (True/False) | ja/nein | keine | Allenfalls externe Beschreibung; kein Eingang im ersten K-Means |
| interest_outdoor | Interesse an Outdoor | Boolean (True/False) | ja/nein | keine | Allenfalls externe Beschreibung; kein Eingang im ersten K-Means |
| interest_wellness | Interesse an Wellness | Boolean (True/False) | ja/nein | keine | Allenfalls externe Beschreibung; kein Eingang im ersten K-Means |
| interest_leisure | Interesse an Freizeit | Boolean (True/False) | ja/nein | keine | Allenfalls externe Beschreibung; kein Eingang im ersten K-Means |

## Vorhandene Rohvariablen: offers_simulated.csv

Eine Zeile pro fiktivem Angebot; keine beobachtete Nutzung oder Nutzer-Angebot-Verknüpfung.

| Name | Bedeutung | Datentyp | Einheit | Fehlende Werte | Geplante Verwendung |
| --- | --- | --- | --- | --- | --- |
| offer_id | Eindeutige Angebotskennung | Text | keine | keine | Katalogidentifikation, kein Clusteringmerkmal |
| category | Angebotsbereich Sport/Outdoor/Wellness/Freizeit | kategorialer Text | Kategorie | keine | Spätere Angebotszuordnung; kein Verhaltensmerkmal |
| title | Als FIKTIV gekennzeichneter Angebotstitel | Text | keine | keine | Anzeige/Beschreibung; kein Clusteringmerkmal |
| price_eur | Angebotspreis | Dezimalzahl | Euro | keine | Kataloginformation; kein Clusteringmerkmal |
| discount_pct | Rabatt in Prozent | Ganzzahl | Prozentpunkte des Preises | keine | Kataloginformation; kein Clusteringmerkmal |

## Geplante abgeleitete K-Means-Merkmale – noch keine gespeicherten Variablen

Granularität: ein Wert pro Nutzer über alle 26 Wochen. N_u = Gesamtaktivitäten, T_u = gesamte Minuten, N_us = Aktivitäten der Sportart s. Berechnungsquelle sind Aktivitäten und die vollständige Nutzerliste. Keine internen Simulationslabels.

| Geplanter Name | Bedeutung / Formel | Datentyp | Einheit | Fehlende Werte / Sonderfälle | Geplante Verwendung |
| --- | --- | --- | --- | --- | --- |
| avg_activities_per_week | N_u / 26 | Dezimalzahl | Aktivitäten/Woche | V2 keine; Nullwochen im Nenner enthalten | Basismodell: Niveau |
| avg_duration_per_week | T_u / 26 | Dezimalzahl | Minuten/Woche | V2 keine; Nullwochen im Nenner enthalten | Ergänzende Beschreibung; optionale Umfangsvariante |
| share_running | N_u,running / N_u | Dezimalzahl | Anteil 0–1 | V2 keine; 0 = nicht beobachtet; bei N_u=0 undefiniert | Basismodell: Sportmix, gemeinsam gewichteter Block |
| share_cycling | N_u,cycling / N_u | Dezimalzahl | Anteil 0–1 | V2 keine; 0 = nicht beobachtet; bei N_u=0 undefiniert | Basismodell: Sportmix, gemeinsam gewichteter Block |
| share_strength | N_u,strength / N_u | Dezimalzahl | Anteil 0–1 | V2 keine; 0 = nicht beobachtet; bei N_u=0 undefiniert | Basismodell: Sportmix, gemeinsam gewichteter Block |
| share_swimming | N_u,swimming / N_u | Dezimalzahl | Anteil 0–1 | V2 keine; 0 = nicht beobachtet; bei N_u=0 undefiniert | Basismodell: Sportmix, gemeinsam gewichteter Block |
| share_walking | N_u,walking / N_u | Dezimalzahl | Anteil 0–1 | V2 keine; 0 = nicht beobachtet; bei N_u=0 undefiniert | Basismodell: Sportmix, gemeinsam gewichteter Block |
| share_hiking | N_u,hiking / N_u | Dezimalzahl | Anteil 0–1 | V2 keine; 0 = nicht beobachtet; bei N_u=0 undefiniert | Basismodell: Sportmix, gemeinsam gewichteter Block |
| share_tennis | N_u,tennis / N_u | Dezimalzahl | Anteil 0–1 | V2 keine; 0 = nicht beobachtet; bei N_u=0 undefiniert | Basismodell: Sportmix, gemeinsam gewichteter Block |
| share_padel | N_u,padel / N_u | Dezimalzahl | Anteil 0–1 | V2 keine; 0 = nicht beobachtet; bei N_u=0 undefiniert | Basismodell: Sportmix, gemeinsam gewichteter Block |
| sport_diversity | Anzahl Sportarten mit N_us > 0 | Ganzzahl | Sportarten, theoretisch 0–8 | V2 keine, beobachtet 4–8 | Zunächst ergänzende Beschreibung, kein Basiseingang |

Alle acht Anteile summieren sich auf 1. Geplante Transformation: Häufigkeit standardisieren; jeden Anteil standardisieren und anschließend durch √8 teilen. Keine Skalierung wurde als Datensatz gespeichert. Umfang und Vielfalt bleiben zunächst außerhalb der neun Basiseingaben. Identifikatoren werden nur zur Zuordnung mitgeführt.

Die vollständige technische Wochenkontrolle outputs/tables/simulation_weekly_check.csv ist ein separates Prüfartefakt mit user_id, week_start und activity_count; sie gehört nicht zu den drei Rohdaten-CSVs. Ihre 2.600 Zeilen einschließlich 558 Nullwochen sind kein bereits gespeicherter K-Means-Datensatz.

Details, Kennzahlen, Grenzen und offene Fragen: kmeans_feature_concept.md. Herkunft und Annahmen: simulation_config.md; Versionsentscheidung: decisions.md; Integrität: active_data_version.json. Historische V1-Berichte beschreiben keine aktive V2.


## Geplante Regressionsmerkmale und Zielvariable – AP 3.3

Diese Namen sind konzeptionell definierte, im Arbeitsspeicher deskriptiv geprüfte Größen. Sie sind keine Spalten der Rohdaten und keine bereits gespeicherte Modellierungstabelle. Ein globales Modell zählt alle acht Sportarten gemeinsam. Granularität: Nutzer u und abgeschlossene Eingabewoche t; c(u,t) ist deren gesamte Aktivitätszahl. relative Projektwoche 1 beginnt am 05.01.2026.

| Geplanter Name | Bedeutung / Formel | Datentyp | Einheit | Fehlende Werte / Grenzen | Geplante Verwendung |
| --- | --- | --- | --- | --- | --- |
| activities_current_week | c(u,t) | Ganzzahl ≥ 0 | Aktivitäten/Woche | Gültige Nullwochen = 0; V2 0–10 | Empfohlener Eingang |
| activities_previous_week | c(u,t−1) | Ganzzahl ≥ 0 | Aktivitäten/Woche | Erste Nutzerwoche hat unbekannte Vorwoche, nicht 0 | Optionaler zusätzlicher Eingang |
| avg_activities_last_4_weeks | Mittel aus c(u,t), c(u,t−1), c(u,t−2), c(u,t−3) | Dezimalzahl | Aktivitäten/Woche | Erste drei Eingabewochen ohne vollständige Historie, nicht auffüllen | Empfohlener Eingang; trailing Fenster einschließlich t |
| week_index | t, relative Nummer 1–26 | Ganzzahl | Woche im Projektzeitraum | Keine; nicht ISO-KW | Zuordnung/Split; zunächst kein Basiseingang |
| activities_next_week | c(u,t+1), gruppenbezogenes shift(−1) | Ganzzahl ≥ 0 | Aktivitäten/Woche | Letzte Woche ohne beobachtetes Folgeziel, nicht 0 | Ausschließlich Zielvariable, niemals Eingang |

Geplante Zuordnungsschlüssel: user_id (vorhandene Nutzerkennung), week_start (abgeleitetes Montagsdatum der Eingabewoche), target_week_start (abgeleitet: week_start + 7 Tage). Die beiden Datumsfelder sind keine Rohspalten der Aktivitäten und keine Basiseingänge; week_start ist bereits in der separaten Wochenkontrolle vorhanden.

Vollständiges Grundraster: 2.600 Nutzerwochen. Verwendbare Eingabewochen 4–25: 2.200 Beispiele. Training mit Zielwochen 5–22: 1.800; Test mit Zielwochen 23–26: 400. Nullwochen verbleiben vollständig im Raster. Gruppenbezogene Sortierung und Fenster sind zwingend. Trainings- und Testmerkmale verwenden nur beim jeweiligen Prognosezeitpunkt bekannte Werte.

## Status später tatsächlich erzeugter Modellierungsvariablen

Aktuell keine vollständige K-Means- oder Regressions-Modellierungstabelle gespeichert. Die geplanten Variablen sind daher nicht als bereits persistierte Modellierungsvariablen zu behandeln. Bei Umsetzung in AP 4 sind tatsächlicher Speicherpfad, Schema, Datentypen, Transformationen, Zeilenzahlen, Zeitgrenzen und Herkunft zu ergänzen. Die bestehende Wochenkontrolle bleibt ein Prüfartefakt.

Details: regression_feature_concept.md (Formeln, Korrelationen, Split, MAE-Konzept und Leakage-Risiken). Noch keine Prognosebewertung und keine Modelllabels.
