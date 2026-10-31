# MOVA – Datenwörterbuch

Stand: 31.10.2026, aktive V2. Die folgenden Rohvariablen existieren tatsächlich in den drei CSV-Dateien unter data/raw. Die elf K-Means-Nutzermerkmale wurden in AP 4.3 tatsächlich unskaliert berechnet und als `data/processed/kmeans_user_features.csv` gespeichert. Neun sind als spätere K-Means-Eingänge vorgesehen, zwei ausschließlich zur Interpretation. Die neun Eingänge wurden in AP 4.4 zusätzlich standardisiert und gewichtet gespeichert. AP 4.5 hat außerdem zwei Regressionsmerkmale und die Folgewoche-Zielvariable tatsächlich gespeichert; Der chronologische Train/Test-Split wurde in AP 4.6 tatsächlich erstellt; Modelle stehen aus.

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

## Tatsächlich berechnete K-Means-Nutzermerkmale – AP 4.3

Granularität: ein Wert pro Nutzer über alle 26 Wochen. N_u = Gesamtaktivitäten, T_u = gesamte Minuten, N_us = Aktivitäten der Sportart s. Berechnungsquelle sind Aktivitäten und die vollständige Nutzerliste. Keine internen Simulationslabels.

| Berechneter Name | Bedeutung / Formel | Datentyp | Einheit | Fehlende Werte / Sonderfälle | Vorgesehene Verwendung |
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

Alle acht Anteile summieren sich auf 1. Geplante Transformation: Häufigkeit standardisieren; jeden Anteil standardisieren und anschließend durch √8 teilen. AP 4.4 hat die Standardisierung und Gewichtung tatsächlich gespeichert; Details im entsprechenden Abschnitt unten. Umfang und Vielfalt bleiben zunächst außerhalb der neun Basiseingaben. Identifikatoren werden nur zur Zuordnung mitgeführt.

Die vollständige technische Wochenkontrolle outputs/tables/simulation_weekly_check.csv ist ein separates Prüfartefakt mit user_id, week_start und activity_count; sie gehört nicht zu den drei Rohdaten-CSVs. Ihre 2.600 Zeilen einschließlich 558 Nullwochen sind kein bereits gespeicherter K-Means-Datensatz.

Details, Kennzahlen, Grenzen und offene Fragen: kmeans_feature_concept.md. Herkunft und Annahmen: simulation_config.md; Versionsentscheidung: decisions.md; Integrität: active_data_version.json. Historische V1-Berichte beschreiben keine aktive V2.


## Regressionsmerkmale und Zielvariable – AP-3.3-Konzept und Umsetzungsstand AP 4.5

Die beiden Basiseingänge activities_current_week und avg_activities_last_4_weeks sowie die Zielvariable activities_next_week sind seit AP 4.5 tatsächlich in regression_weekly_features.csv gespeichert. activities_previous_week bleibt eine geplante optionale Erweiterung. Keine dieser Größen ist eine Rohspalte der Einzelaktivitäten; zeitliche Metadaten werden aus der bestehenden Wochentabelle übernommen. Ein globales Modell zählt alle acht Sportarten gemeinsam. Granularität: Nutzer u und abgeschlossene Eingabewoche t; c(u,t) ist deren gesamte Aktivitätszahl. relative Projektwoche 1 beginnt am 05.01.2026.

| Geplanter Name | Bedeutung / Formel | Datentyp | Einheit | Fehlende Werte / Grenzen | Geplante Verwendung |
| --- | --- | --- | --- | --- | --- |
| activities_current_week | c(u,t) | Ganzzahl ≥ 0 | Aktivitäten/Woche | Gültige Nullwochen = 0; V2 0–10 | Empfohlener Eingang |
| activities_previous_week | c(u,t−1) | Ganzzahl ≥ 0 | Aktivitäten/Woche | Erste Nutzerwoche hat unbekannte Vorwoche, nicht 0 | Optionaler zusätzlicher Eingang |
| avg_activities_last_4_weeks | Mittel aus c(u,t), c(u,t−1), c(u,t−2), c(u,t−3) | Dezimalzahl | Aktivitäten/Woche | Erste drei Eingabewochen ohne vollständige Historie, nicht auffüllen | Empfohlener Eingang; trailing Fenster einschließlich t |
| week_index | t, relative Nummer 1–26 | Ganzzahl | Woche im Projektzeitraum | Keine; nicht ISO-KW | Zuordnung/Split; zunächst kein Basiseingang |
| activities_next_week | c(u,t+1), gruppenbezogenes shift(−1) | Ganzzahl ≥ 0 | Aktivitäten/Woche | Letzte Woche ohne beobachtetes Folgeziel, nicht 0 | Ausschließlich Zielvariable, niemals Eingang |

Tatsächlich übernommene Zuordnungsfelder: user_id, week_index, week_start und week_end. target_week_start bleibt ein geplantes separates Feld; intern wird die Zielwoche als week_start + 7 Tage geprüft. Datumsfelder sind keine Rohspalten der Einzelaktivitäten und keine Modelleingänge. Der konkrete AP-4.5-Export enthält genau sieben Spalten ohne Split; siehe Dateischema unten.

Vollständiges Grundraster: 2.600 Nutzerwochen. Verwendbare Eingabewochen 4–25: 2.200 Beispiele. In AP 4.6 tatsächlich erzeugte Aufteilung: Training mit Zielwochen 5–22 (1.800), Test mit Zielwochen 23–26 (400). Nullwochen verbleiben vollständig im Raster. Gruppenbezogene Sortierung und Fenster sind zwingend. Trainings- und Testmerkmale verwenden nur beim jeweiligen Prognosezeitpunkt bekannte Werte.

## Status später tatsächlich erzeugter Modellierungsvariablen

AP 4.3 hat die unskalierte K-Means-Nutzermerkmalstabelle tatsächlich gespeichert (Details unten). AP 4.4 hat die skalierte und gewichtete K-Means-Tabelle gespeichert; AP 4.5 hat die Regressionsmerkmalstabelle tatsächlich gespeichert; Train/Test-Dateien seit AP 4.6 tatsächlich erzeugt; Details unten. Die bestehende Wochenkontrolle bleibt ein Prüfartefakt.

Details: regression_feature_concept.md (Formeln, Korrelationen, Split, MAE-Konzept und Leakage-Risiken). Noch keine Prognosebewertung und keine Modelllabels.


## Tatsächlich aufbereitete Daten – AP 4.1

`data/processed/activities_selected.csv` wurde tatsächlich erzeugt: 6.465 Datenzeilen, fünf Spalten, eine Zeile je Aktivität. Quelle ausschließlich aktive V2 aus `data/raw/activities_simulated.csv`; bekannte Nutzer gegen `data/raw/users_simulated.csv` geprüft. Rohdaten bleiben unverändert. Keine Aggregation, Skalierung oder Modellierung; die oben aufgeführten Modellierungsmerkmale bleiben geplant.

| Spalte (Exportreihenfolge) | Bedeutung / Rolle | Logischer Datentyp | Einheit / zulässige Werte | Fehlende Werte / Verarbeitung |
| --- | --- | --- | --- | --- |
| activity_id | Eindeutige Aktivitätskennung; Schlüssel | Text | A + sechs Ziffern | Keine; unverändert übernommen, Eindeutigkeit geprüft |
| user_id | Bekannte Nutzerkennung; Fremdschlüssel | Text | U + drei Ziffern aus aktiver Nutzerdatei | Keine; unverändert übernommen |
| date | Aktivitätsdatum; spätere zeitliche Zuordnung | ISO-Datum YYYY-MM-DD | Kalendertag, 05.01.–05.07.2026 | Keine; strikt geprüft und unverändert exportiert |
| sport_type | Ausgeübte Sportart; Kategorie | Text | Running, Cycling, Strength, Swimming, Walking, Hiking, Tennis, Padel | Keine; geprüft, unverändert übernommen |
| duration_min | Trainingsdauer; späterer Umfang | Dezimalzahl | Minuten je Aktivität, dokumentierte Sportgrenzen | Keine; mit Decimal geprüft, Originaldarstellung unverändert |

CSV enthält keine physischen Typdeklarationen. IDs sind beim späteren Einlesen als Text zu behandeln. `distance_km` ist ausschließlich aus dieser Arbeitsdatei ausgeschlossen, da für die ersten Modelle nicht benötigt; vollständig in Rohdaten erhalten. 1.698 strukturell nicht anwendbare Rohdistanzen wurden nicht imputiert. Alle ausgewählten Werte stimmen mit der Quelle überein; Minutensumme 422.829,9. Prüfregeln, SHA-256-Werte und reale Vorher-Nachher-Beispiele: [Ausführungsnachweis](data_preparation_execution.md).


## Tatsächlich aufbereitete Daten – AP 4.2

`data/processed/user_weekly_activities.csv` ist tatsächlich erstellt: 2.600 Zeilen und sechs Spalten, eine Zeile je Kombination aus vollständiger Nutzerliste und relativer Projektwoche. Quelle: aktive V2 über `activities_selected.csv` und `users_simulated.csv`. 2.042 belegte Gruppen + 558 ergänzte Nullwochen. Sortierung: user_id, week_index aufsteigend. Keine vollständige Modellierungstabelle; geplante K-Means- und Regressionsmerkmale sind inzwischen in AP 4.5 tatsächlich gespeichert; der Split erfolgt erst in AP 4.6. Diese Fortschreibung ersetzt für das Wochenraster den früheren Planungsstatus, nicht die historischen AP-3-Befunde.

| Spalte (Exportreihenfolge) | Bedeutung / Herkunft | Logischer Datentyp | Einheit / zulässige Werte | Fehlende Werte / Rolle |
| --- | --- | --- | --- | --- |
| user_id | Nutzer aus vollständiger aktiver Nutzerliste | Text | U + drei Ziffern | Keine; Zuordnungsschlüssel, kein Modelleingang |
| week_index | 1 + ganze Wochen seit 05.01.2026 | Ganzzahl | Relative Projektwoche 1–26, keine ISO-KW | Keine; Kalenderschlüssel |
| week_start | Montag der Projektwoche | ISO-Datum YYYY-MM-DD | 05.01.–29.06.2026 in 7-Tage-Schritten | Keine; zeitliche Zuordnung |
| week_end | Automatisch week_start + 6 Tage | ISO-Datum YYYY-MM-DD | Sonntag, 11.01.–05.07.2026 | Keine; ausschließlich Zuordnung/Visualisierung, kein Machine-Learning-Eingangsmerkmal |
| activities_count | Anzahl Einzelaktivitäten dieser Nutzerwoche, alle Sportarten | Ganzzahl ≥ 0 | Aktivitäten/Woche, aktive V2 0–10 | Fehlende gültige Gruppe = 0; keine Imputation fehlerhafter Eingaben |
| total_duration_min | Summe der ausgewählten Originalminuten dieser Nutzerwoche | Dezimalzahl ≥ 0 | Minuten/Woche, exakt mit Decimal summiert | Fehlende gültige Gruppe = 0; bei allen Nullwochen 0 |

Jede Woche umfasst Montag bis Sonntag einschließlich (sieben Kalendertage). CSV enthält keine physischen Typdeklarationen. Kein Indexexport, UTF-8/LF/Dezimalpunkt. Summen: 6.465 Aktivitäten und 422.829,9 Minuten. Alle 2.600 Counts anhand eindeutiger `(user_id, week_start)`-Schlüssel gegen `simulation_weekly_check.csv` geprüft; dessen bestehende Spalte heißt `activity_count`. Details und echte Beispiele: [Ausführungsnachweis](data_preparation_execution.md).


## Tatsächlich aufbereitete Daten – AP 4.3: kmeans_user_features.csv

Pfad: `data/processed/kmeans_user_features.csv`. Tatsächlich erzeugt: 100 Zeilen × zwölf Spalten; eine Zeile je Nutzer, nach user_id aufsteigend. Berechnung aus aktiver V2: `activities_selected.csv`, vollständige Nutzerliste `users_simulated.csv`; nutzerbezogene Counts und Minuten gegen `user_weekly_activities.csv` geprüft. Zeitraum 05.01.–05.07.2026, Nenner immer 26 einschließlich Nullwochen. Keine Skalierung, Gewichtung, Labels oder Modelle.

Die obige Formeltabelle beschreibt nun tatsächlich gespeicherte Variablen. Das CSV enthält folgende feste Spaltenreihenfolge:

| Spalte | Tatsächlicher Status / spätere Rolle | Logischer Typ / Einheit | Werte und Fehlwertregel |
| --- | --- | --- | --- |
| user_id | Vorhandener Zuordnungsschlüssel; kein Modelleingang | Text | Alle 100 bekannten Nutzer, eindeutig |
| avg_activities_per_week | Berechnet; geplanter Eingang 1 von 9 | Dezimalzahl, Aktivitäten/Woche | N_u/26 ≥ 0 |
| share_running | Berechnet; geplanter Eingang 2 von 9 | Dezimalzahl, Anteil | N_u,Running/N_u, [0,1] |
| share_cycling | Berechnet; geplanter Eingang 3 von 9 | Dezimalzahl, Anteil | N_u,Cycling/N_u, [0,1] |
| share_strength | Berechnet; geplanter Eingang 4 von 9 | Dezimalzahl, Anteil | N_u,Strength/N_u, [0,1] |
| share_swimming | Berechnet; geplanter Eingang 5 von 9 | Dezimalzahl, Anteil | N_u,Swimming/N_u, [0,1] |
| share_walking | Berechnet; geplanter Eingang 6 von 9 | Dezimalzahl, Anteil | N_u,Walking/N_u, [0,1] |
| share_hiking | Berechnet; geplanter Eingang 7 von 9 | Dezimalzahl, Anteil | N_u,Hiking/N_u, [0,1] |
| share_tennis | Berechnet; geplanter Eingang 8 von 9 | Dezimalzahl, Anteil | N_u,Tennis/N_u, [0,1] |
| share_padel | Berechnet; geplanter Eingang 9 von 9 | Dezimalzahl, Anteil | N_u,Padel/N_u, [0,1] |
| avg_duration_per_week | Berechnet; ausschließlich Interpretation | Dezimalzahl, Minuten/Woche | T_u/26 ≥ 0 |
| sport_diversity | Berechnet; ausschließlich Interpretation | Ganzzahl, Anzahl Sportarten | Zahl positiver Sportcounts, V2 tatsächlich 4–8 |

CSV enthält keine physischen Typdeklarationen. Elf neue Merkmale sind berechnet; user_id ist der mitgeführte Schlüssel. In aktiver V2 keine fehlenden Werte; alle 100 Nutzer aktiv, acht Anteile je Nutzer summieren sich innerhalb Toleranz zu 1. Nicht ausgeübte Sportart bei aktivem Nutzer = Anteil 0. Zukünftig vollständig inaktiv: Wochenhäufigkeit/Minuten/Vielfalt 0; acht Anteile undefiniert (`None`, CSV-leer), kein künstlicher Nullmix. Status `inactive_no_sport_mix` separat im Prüfprotokoll, nicht im 12-Spalten-CSV; diese Nutzer vom späteren Skalierungsfit/Sportmix-K-Means ausschließen und separat ausweisen. Aktuelle V2-CLI verlangt weiterhin 100 aktive Nutzer; neue Daten benötigen einen freigegebenen Datenvertrag.

Validierung: 6.465 Aktivitäten und 422.829,9 Minuten erhalten; alle 100 Nutzer mit Wochenaggregaten abgeglichen. Float-Vergleiche absolut 1e−9, relativ 1e−12; Minutenaggregate mit Decimal. Datenherkunft, tatsächliche Beispiele, technische Tests, Reproduzierbarkeit und Ausgabehash im [Ausführungsnachweis](data_preparation_execution.md). Dieser Absatz dokumentiert den damaligen AP-4.3-Stand; tatsächliche Skalierung siehe AP 4.4, Regressionsmerkmale siehe AP 4.5.


## Tatsächlich aufbereitete Daten – AP 4.4: skalierte K-Means-Eingänge

`data/processed/kmeans_user_features_scaled.csv`: tatsächlich erzeugte 100 Zeilen × zehn Spalten, nach user_id sortiert. Quelle: unveränderte `kmeans_user_features.csv`. Die früheren AP-4.3-Statusangaben beschreiben den damaligen unskalierten Verarbeitungsschritt. Vollständige Transformationsparameter: `outputs/models/kmeans_scaling_params.json`. StandardScaler wurde auf allen 100 aktiven V2-Profilen gefittet (deskriptiv/unüberwacht, kein Regressionssplit).

| Exportspalte | Logischer Typ / Rolle | Tatsächlich ausgeführte Transformation / Werte |
| --- | --- | --- |
| user_id | Text, Identifikation | Unverändert übernommen; kein Modelleingang |
| avg_activities_per_week | Endliche Dezimalzahl, Eingang | (x−mean)/scale; StandardScaler, ddof=0 |
| share_running | Endliche Dezimalzahl, Eingang | StandardScaler-z / √8 |
| share_cycling | Endliche Dezimalzahl, Eingang | StandardScaler-z / √8 |
| share_strength | Endliche Dezimalzahl, Eingang | StandardScaler-z / √8 |
| share_swimming | Endliche Dezimalzahl, Eingang | StandardScaler-z / √8 |
| share_walking | Endliche Dezimalzahl, Eingang | StandardScaler-z / √8 |
| share_hiking | Endliche Dezimalzahl, Eingang | StandardScaler-z / √8 |
| share_tennis | Endliche Dezimalzahl, Eingang | StandardScaler-z / √8 |
| share_padel | Endliche Dezimalzahl, Eingang | StandardScaler-z / √8 |

Die neun numerischen Werte sind dimensionslos und standardisiert; Sportanteile zusätzlich mit 1/√8 gewichtet. Negative Werte sind zulässig und kein Datenfehler. Skalierte share_*-Werte sind keine Wahrscheinlichkeiten, können außerhalb [0,1] liegen und müssen sich nicht zu 1 summieren. Ursprüngliche Anteile, Wochenhäufigkeit und Interpretationsmerkmale bleiben unverändert in der unskalierten Datei. `avg_duration_per_week` und `sport_diversity` sind bewusst nicht im skalierten Export enthalten.

Aktuelle V2: keine fehlenden/nicht endlichen Werte und keine konstanten Eingänge. Häufigkeit Mittelwert ≈0/Populationsvarianz ≈1; gewichtete Sportkoordinaten Mittelwert ≈0/Varianz ≈1/8. Beide Blockvarianzsummen ≈1, fachliche Startannahme, keine optimierte Gewichtung. Nullvarianz behandelt StandardScaler mit scale_=1; echte Standardabweichung dann 0. Numerisch ununterscheidbare Konstanten ebenfalls geschützt. Inaktive Profile mit undefinierten Anteilen separat halten und weder fitten noch imputieren.

JSON dokumentiert Reihenfolge, mean, variance, std_ddof0, scale, Faktoren, Konstantenstatus, Fitnutzer/Versionen und Herkunft. Wiederverwendung: (x−gespeicherter mean)/gespeicherter scale, danach gespeichertes Gewicht; kein Refit für neue berechtigte Profile. Keine Modellparameter von K-Means, keine Clusterlabels. Vollständige tatsächliche Parameter und drei reale V2-Beispiele im [Ausführungsnachweis](data_preparation_execution.md). Regressionsmerkmale sind inzwischen in AP 4.5 tatsächlich gespeichert; der Split erfolgt erst in AP 4.6.


## Tatsächlich aufbereitete Daten – AP 4.5: regression_weekly_features.csv

Pfad: `data/processed/regression_weekly_features.csv`; 2.200 Zeilen × sieben Spalten, 100 Nutzer mit jeweils 22 Prognosezeitpunkten, aufsteigend nach user_id und week_index. Quelle ausschließlich vorhandene V2-Wochenwerte aus `user_weekly_activities.csv`. Das komplette Raster bleibt mit allen 2.600 Zeilen erhalten. Kein Train/Test-Split, keine Prognosen, keine Modelle.

| Spalte (Exportreihenfolge) | Rolle | Logischer Typ / Einheit | Herkunft, Werte und Fehlwertregel |
| --- | --- | --- | --- |
| user_id | Identifikation, kein X | Text | Übernommene bekannte Nutzerkennung; eindeutig je Woche |
| week_index | Zeitliche Metadaten, kein X | Ganzzahl, relative Projektwoche | Eingabewoche t, ausschließlich 4–25; keine ISO-KW |
| week_start | Zeitliche Metadaten, kein X | ISO-Datum YYYY-MM-DD | Montag der Eingabewoche, 26.01.–22.06.2026; Zuordnung/Visualisierung |
| week_end | Zeitliche Metadaten, kein X | ISO-Datum YYYY-MM-DD | Sonntag der Eingabewoche, 01.02.–28.06.2026; Zuordnung/Visualisierung |
| activities_current_week | Eingang X | Nicht negative Ganzzahl, Aktivitäten/Woche | c(u,t), V2 0–10; echte Null bleibt 0 |
| avg_activities_last_4_weeks | Eingang X | Endliche Dezimalzahl, Aktivitäten/Woche | [c(u,t−3)+c(u,t−2)+c(u,t−1)+c(u,t)]/4; vollständige Historie erforderlich, Nullen enthalten |
| activities_next_week | Ausschließlich Ziel y, niemals X | Nicht negative Ganzzahl, Aktivitäten/Woche | c(u,t+1) desselben Nutzers, Zielwochen 5–26, V2 0–10 |

user_id dient der Rückverknüpfung, week_index der relativen Einordnung. week_start und week_end bleiben für zeitliche Zuordnung und spätere Visualisierung erhalten, sind keine numerischen Basiseingänge; ihre Verwendung als X würde eine andere Modellannahme einführen. Diese Daten beziehen sich auf die Eingabewoche; die Zielwoche beginnt sieben Tage nach week_start. target_week_start ist intern ableitbar/geprüft, nicht als achte Spalte exportiert.

Keine fehlenden oder unendlichen Modellwerte. 300 frühe Eingabezeilen ohne vollständige Historie und 100 letzte Eingabezeilen ohne beobachtete Folgewoche werden nur vom Modellierungsexport ausgeschlossen; keine Auffüllung unbekannter Vergangenheit oder Zukunft. Die Wochen 1–3 bleiben als Historie und Woche 26 als Ziel nutzbar. 558 Nullwochen bleiben im Grundraster; im Modellierungsexport 478 aktuelle Nullwochen, 474 Nullziele und 1.100 Zeilen mit mindestens einer Null im Historienfenster. Diese Mengen sind keine neuen Aktivitätszeilen.

CSV ohne physische Typdeklarationen; Counts als Integer lesen. Nur zwei Basiseingänge; activities_previous_week bleibt optional/geplant und wurde nicht erzeugt. Keine K-Means-Nutzermerkmale als Regressoren, keine Skalierung. Die tatsächlichen Berechnungen, Leakagetests, sieben erfolgreichen technischen Tests, drei reale Beispiele und Hashwerte stehen im [Ausführungsnachweis](data_preparation_execution.md).


## Tatsächlich aufbereitete Daten – AP 4.6: chronologischer Regressionssplit

Tatsächlich erstellt: `data/processed/regression_train.csv` (1.800 Zeilen × sieben Spalten) und `data/processed/regression_test.csv` (400 × sieben). Quelle: unveränderte `regression_weekly_features.csv`. Beide enthalten alle 100 Nutzer; Training 18, Test vier Zeilen je Nutzer. Sortierung user_id, week_index aufsteigend. Frühere AP-4.5-Angaben beschreiben den Stand vor dieser Aufteilung.

Auswahl ausschließlich nach week_index: Training 4–21, Test 22–25. Abgeleitete Zielwochen: Training 5–22 (02.02.–07.06.2026), Test 23–26 (08.06.–05.07.2026), keine Zielüberschneidung. Zusammen ergeben beide Dateien exakt alle 2.200 unveränderten Ausgangszeilen, keine zusätzlichen Merkmale.

| Spalte (in beiden Dateien, Exportreihenfolge) | Logischer Datentyp / Einheit | Rolle / Bedeutung |
| --- | --- | --- |
| user_id | Text | Identifikation, kein Modelleingang |
| week_index | Ganzzahl, relative Projektwoche | Zeitliche Zuordnung und Splitregel, kein Modelleingang |
| week_start | ISO-Datum YYYY-MM-DD | Montag der Eingabewoche, Zuordnung/Visualisierung, kein Modelleingang |
| week_end | ISO-Datum YYYY-MM-DD | Sonntag der Eingabewoche, Zuordnung/Visualisierung, kein Modelleingang |
| activities_current_week | Nicht negative Ganzzahl, Aktivitäten/Woche | Eingang X1: c(u,t) |
| avg_activities_last_4_weeks | Endliche Dezimalzahl, Aktivitäten/Woche | Eingang X2: Mittel aus t−3 bis t, einschließlich echter Nullwochen |
| activities_next_week | Nicht negative Ganzzahl, Aktivitäten/Woche | Ausschließlich Ziel y: c(u,t+1), niemals Modelleingang |

Alle Werte und ursprünglichen Zahlendarstellungen unverändert übernommen. Keine fehlenden/unendlichen Modellwerte. CSV ohne physische Typdeklarationen; Counts als Integer lesen. Es gibt keine zusätzliche split-Spalte; die Dateizuordnung kennzeichnet die Teilmenge. Manifest `documentation/regression_split_manifest.json` dokumentiert Datenversion, Quellhash, Regeln, Zielwochen, Rollen, Nutzerzahlen, Ausgabehashes und rollierende Einwochenprognose.

Frühere abgeschlossene Testwochen dürfen in späteren Testeingaben vorkommen; Zukunft aus t+1 darf niemals für X in t verwendet werden. Gemeinsame historische Eingabewochen sind kein automatisches Leakage. Ein späteres Modell bleibt während der Testphase unverändert. Keine Modelle trainiert, keine Prognosen oder Modellgüte berechnet. Ausführungsnachweis einschließlich drei echter V2-Grenzbeispiele: [AP-4-Dokumentation](data_preparation_execution.md).
