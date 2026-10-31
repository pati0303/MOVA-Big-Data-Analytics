# MOVA – Nutzungsvertrag K-Means, erste V2-Version (AP 5.3a)

Stand: 31.10.2026. Gültig für das lokal geprüfte finale k=2-Modell. Technisch
abgenommen für die synthetische V2 und die hier beschriebenen Eingabebedingungen;
keine Freigabe für produktive Garmin-Nutzerdaten und keine Generalisierungsaussage.

## Artefakte und Voraussetzungen

Vertrauenswürdiges Paket aus `outputs/models/kmeans_final.joblib`,
`kmeans_final_metadata.json` und `kmeans_scaling_params.json`. Nur lokal erzeugte,
vertrauenswürdige Joblib-Artefakte laden; Joblib kann Code ausführen. SHA-256 sichert
Konsistenz, nicht Authentizität unbekannter Dateien. Paket gemeinsam versionieren.
Getestet: Python 3.12.14, scikit-learn 1.8.0, NumPy 2.3.5, pandas 2.2.3,
Joblib 1.5.3. Modellparameter bleiben unverändert: k=2, k-means++, Seed 42,
n_init=20, max_iter=300, Lloyd, tol=1e-4. Keine fit-/fit_predict-Aufrufe bei Inferenz.

`load_artifacts` in `src/modeling_kmeans_inference.py` prüft die lokalen Artefakte
und Quellhashes, Merkmalsreihenfolge, Modellparameter, Zentren, Gewichte und Mapping.
Der aktuelle Loader ist ein Projektprüfer mit vorhandenen V2-Referenzdateien;
ein eigenständiges Deployment ohne Trainingsdateien ist noch nicht implementiert.

## A–C: Eingaben, Merkmalsreihenfolge und 26-Wochen-Berechnung

Für jeden Nutzer werden eindeutige, vollständig erfasste Aktivitäten mit Nutzer-ID,
eindeutiger Aktivitäts-ID, gültigem Datum und einer der acht bekannten Sportarten
benötigt: Running, Cycling, Strength, Swimming, Walking, Hiking, Tennis, Padel.
Nutzer-ID ist nur Zuordnungsschlüssel. Dauer ist für das Clustering nicht erforderlich,
aber für spätere Profilbeschreibung in Minuten gültig zu erfassen. Interessen und
Angebote sind keine Clustering-Eingaben. Doppelte Aktivitäten sind vorgelagert zu
klären; keine automatische Deduplizierung oder Sportartenumdeutung.

Ein Profil muss sich auf **26 aufeinanderfolgende vollständige Kalenderwochen**
(Montag bis Sonntag, insgesamt 182 Tage) beziehen. Für V2: 05.01.–05.07.2026.
Für spätere Daten ist ein dokumentierter abgeschlossener 26-Wochen-Zeitraum mit
festgelegter lokaler Kalenderzeitzone erforderlich. Bei längerer Historie genau das
vereinbarte Fenster auswählen, nicht durch die gesamte Historienlänge teilen.
Eine laufende Woche zählt nicht als vollständige Woche. Die App muss Zeitgrenzen,
Zeitzone und lückenlose verlässliche Erfassung nachweisen; der vorhandene technische
Kern kann diese Nachweise nicht selbst aus Garmin-Daten ableiten.

Sei N die Aktivitätszahl im Fenster, N_s die Aktivitätszahl der Sportart s.

| Position | Merkmal | Berechnung für aktive Nutzer |
| --- | --- | --- |
| 1 | avg_activities_per_week | N / 26 |
| 2 | share_running | N_running / N |
| 3 | share_cycling | N_cycling / N |
| 4 | share_strength | N_strength / N |
| 5 | share_swimming | N_swimming / N |
| 6 | share_walking | N_walking / N |
| 7 | share_hiking | N_hiking / N |
| 8 | share_tennis | N_tennis / N |
| 9 | share_padel | N_padel / N |

Zählungen beziehen sich auf Aktivitäten, nicht auf Minuten. Bestätigt trainingsfreie
Wochen gehen mit null Aktivitäten in den festen Nenner 26 ein. Fehlende Aufzeichnungen
belegen keine trainingsfreie Woche. Für aktive Nutzer sind alle neun Werte endlich,
Häufigkeit >0, Anteile jeweils in [0,1] und Summe 1 (atol=1e-10). Merkmale nicht runden,
nicht kappen, fehlende Merkmale nicht imputieren. Wochenminuten und Sportartenvielfalt
sind ausschließlich nachträgliche Beschreibung, keine Eingänge.

## D–E: gespeicherte Transformation einmal wiederverwenden

Für jeden Rohwert x_j:

`z_j = (x_j − features[j].mean) / features[j].scale`

`X_j = z_j × features[j].weight`

Alle Werte kommen aus `kmeans_scaling_params.json`. Für Häufigkeit ist weight=1,
für jede der acht Sportarten weight=1/√8 ≈0,35355339059327373. Der Faktor wirkt
nach der Standardisierung genau einmal. Gespeicherte scale-Werte verwenden, keine
Standardabweichungen neuer Nutzer berechnen; kein erneuter Scaling-Fit. Die AP-4-
Konstantenregel ist bereits in scale enthalten (gegebenenfalls 1), keine neue Regel
anpassen. Die aktuelle V2 hat neun variierende Merkmale.

`transform_saved` erwartet ausschließlich unskalierte aktive Profile in exakter
Tabellenreihenfolge und liefert die gewichtete Modellmatrix mit denselben Spalten.
`kmeans_user_features_scaled.csv` ist bereits transformiert und darf nicht erneut
an `transform_saved` übergeben werden. Es gibt keinen automatischen Roh-/Skaliert-
Detektor; Aufrufer müssen die Eingabeart sicher kennen. Modell erwartet nur fertiges X.

## F–G: Zuordnung und Bezeichnungen

Nach erfolgreicher Eignungsprüfung: `model.predict(X[feature_order])`. Kein Training,
keine Anpassung von Zentren, Parametern oder Gewichtung. Ergebnis ist eine technische
ID. Den Text ausschließlich über `metadata['cluster_id_to_segment'][str(id)]`
auflösen, nicht aus der numerischen ID ableiten. Aktueller Paketstand:

| ID | Segment | Gemessene Aktivitäten/Woche | V2-Nutzer |
| --- | --- | --- | --- |
| 0 | Geringere Trainingshäufigkeit | 1,5350877193 | 57 |
| 1 | Höhere Trainingshäufigkeit | 3,7477638640 | 43 |

Das Mapping wurde in AP 5.3 anhand der unskalierten Gruppenmittelwerte festgelegt.
Neue Nutzer ändern dieses Mapping nicht. Die Zuordnung erfolgt nach neun Distanzen,
nicht nach einem allgemeinen Wochenhäufigkeits-Grenzwert. Die beiden Cluster
beschreiben ausschließlich das relative Aktivitätsniveau innerhalb der untersuchten
synthetischen Nutzer. Keine unmittelbare Aussage über Fitness, Gesundheit oder
sportliche Erfahrung.

## Sonderfälle und technische Statuswerte

Bei verweigerter Zuordnung sind `cluster_id` und `segment_label` immer None;
bei CSV-/API-Integration später als null/leer übertragen, niemals als reguläre ID.

| Fall | Fachliche Regel | Implementierter Status |
| --- | --- | --- |
| Weniger als 26 vollständige Wochen, fehlende Wochenzahl | Keine reguläre Zuordnung; weitere Historie abwarten | insufficient_history |
| Fehlende, unvollständige oder nicht verlässlich bestätigte Erfassung | Keine Nullwochen erfinden; Datenlage klären | incomplete_or_unverified_records |
| Unbekannte Sportart oder ungeprüfter Sportartenkatalog | Keine Aktivität stillschweigend entfernen oder umbenennen | unknown_or_unverified_sports |
| Vollständige verlässliche Historie, aber N=0 | Häufigkeit 0; acht Sportanteile bleiben undefiniert; separates fachliches Inaktivitätsmerkmal | inactive |
| Fehlende Features, falsche Reihenfolge, NaN/∞ bei aktiven Nutzern, negative Werte, ungültige Anteilssumme | Keine Imputation oder Zuordnung; Ursache klären | invalid_features |
| Vollständige verlässliche Historie und gültiges aktives Profil | Transformation und predict, Mapping aus Metadaten | assigned |

Für inaktive Nutzer werden None/NaN als undefinierte Anteile erwartet, niemals acht
künstliche Nullen oder ein gleichverteilter Mix. Vor dem Inaktivitätsstatus wird die
Historieneignung geprüft: N=0 bei lückenhaften Daten ist kein Nachweis von Inaktivität.
Die Gründe werden in der Reihenfolge Historie, Erfassung, Sportkatalog, Merkmale
geprüft; dies ist keine vollständige Liste paralleler Fehler.

## Implementiert und tatsächlich getestet

Schlanker Kern ohne Anwendung/UI:

- `load_artifacts`: geprüfte lokale Artefakte laden, Abweichungen führen zum Abbruch.
- `transform_saved`: Rohprofile validieren und gespeicherte Transformation anwenden.
- `assign_profile`: ein Profil plus Pflichtnachweise `complete_weeks=26`,
  `records_complete=True`, `records_reliable=True`, `known_sports=True`; sichere
  Statusausgabe oder Zuordnung. Keine positiven Defaults für fehlende Nachweise.
- `audit_existing`: alle 100 bestehenden V2-Zuordnungen aus gespeicherten Rohmerkmalen
  und Artefakten reproduzieren, gegen skalierten Export und user_clusters.csv prüfen.

Sechs automatisierte Tests in `tests/test_modeling_kmeans_inference.py`: alle 100
Zuordnungen über Audit und Profil-API ohne Fit reproduziert, gespeicherte Transformation,
Feature-Reihenfolge/fehlende/zusätzliche Merkmale, ungültige Zahlen/Anteile,
Inaktivität ohne künstliche Präferenzen sowie Historien-/Sportarten-Sperren.
Kein bestehendes Modell neu trainiert; ältere Tests mit Trainingsaufrufen deshalb
in AP 5.3a bewusst nicht erneut ausgeführt. Die sechs neuen Tests sind bestanden.

## Erst bei App-Integration umzusetzen und vor Produktion zu prüfen

Noch nicht implementiert: Garmin-Import, Kalender-/Zeitzonenfenster, Nachweis der
Verlässlichkeit/Vollständigkeit jeder Woche, Erkennung unbekannter Sportarten aus
Einzelaktivitäten, Aktivitätsvalidierung und Aggregation zu N/N_s, Umgang mit
Sync-Ausfällen und Duplikaten, Speicherung/Anzeige der fachlichen Statuswerte sowie
Deployment-Paketversionierung. `known_sports` und Vollständigkeitsflags sind derzeit
bestätigte vorgelagerte Angaben, keine vom Kern automatisch belegten Tatsachen.
Die App darf sie nicht pauschal auf True setzen. Alle Sonderfallregeln müssen vor
produktiver Nutzung mit echten Garmin-Nutzern erneut fachlich und technisch geprüft
werden; eine vollständige Historie beweist keine Nähe zur Trainingsverteilung.

Die Cluster sind eine erste Beschreibung des Aktivitätsniveaus. Individuelle
Sportpräferenzen und freiwillige Interessen sollen später die Personalisierung
innerhalb der Segmente ergänzen. Noch keine Empfehlungslogik oder Regression
implementiert. Lineare Regression kann als separater Arbeitsschritt auf den bereits
vorbereiteten zeitlich getrennten Regressionsdaten fortgesetzt werden.
