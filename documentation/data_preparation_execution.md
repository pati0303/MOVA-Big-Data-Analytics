# MOVA – AP 4.1: ausgeführte Data Selection und Data Cleaning

Stand: 31.10.2026. CRISP-DM 3.1 Select Data und 3.2 Clean Data.

## Ziel, Basis und Umfang

Aktive synthetische V2 unverändert prüfen und eine Arbeitsdatei mit fünf Aktivitätsvariablen erzeugen. Arbeitsbereich `/workspace/MOVA-AP4`, Branch `ap4-data-preparation`, Quell-Commit `ed52949cb8b688bc64c0793be0e407950314769e`. Das neue Skript ist noch nicht committed.

Eingaben: `data/raw/activities_simulated.csv` und `data/raw/users_simulated.csv`. Datenvertrag: `active_data_version.json`; fachliche Regeln: `simulation_config.md` und `data_preparation_plan.md`. Keine V1, Vergleichskopien oder Generatoren verwendet. 100 Nutzer, 6.465 Aktivitäten, acht Sportarten; Beobachtungszeitraum 05.01.–05.07.2026 umfasst 26 vollständige Wochen.

Die konkrete Benutzeranweisung präzisiert den früheren AP-3-Plan: Ausgabe unter `data/processed/activities_selected.csv`, nicht unter dem dort geplanten Unterordner `ap4_v2`. Der Plan bleibt unverändert. Angebote werden nicht fachlich verarbeitet; Angebotsdatei und vorhandene Wochenkontrolle werden ausschließlich per dokumentiertem Hash auf Integrität geprüft.

## Reproduktion und Datenvertrag

Im Repository: `python src/data_preparation_selection.py`. Nur Python-Standardbibliothek; verwendete Python-Version: 3.12.14. Das Skript bestimmt den Projektpfad aus seinem eigenen Speicherort. UTF-8, Komma, Dezimalpunkt, LF-Zeilenenden, Kopfzeile ohne Index, unveränderte Quellreihenfolge. CSV speichert keine Typdeklarationen: IDs und Kategorien bleiben Text, Datum wird strikt als Kalenderdatum geprüft und als identisches ISO-Datum exportiert; Zahlen werden mit Decimal validiert, aber als unveränderte Originalzeichenfolgen geschrieben. Keine Rundung oder implizite Float-Konvertierung.

Ein zweiter tatsächlicher Lauf lieferte dieselbe CSV-Prüfsumme und denselben Prüfbericht. Eine bestehende identische Ausgabe wird akzeptiert; eine abweichende Ausgabe wird nicht überschrieben. Bei kritischen Befunden erfolgt Abbruch mit Meldung auf stderr und Exitcode 1; keine automatische Löschung, Ersetzung, Imputation oder Deduplizierung. Befunde sind dann im Laufprotokoll zu sichern und anhand der Quelle fachlich zu klären, bevor eine separat dokumentierte Korrektur erfolgt.

## Tatsächlich ausgeführte Prüfungen

| Prüfung | Regel | Tatsächliches Ergebnis |
| --- | --- | --- |
| Version und Integrität | V2, Sollzahlen, alle vier Manifest-Hashes vor/nach Lauf | bestanden |
| Schema und CSV-Struktur | exakt sechs Rohspalten, fünf Nutzerspalten, keine verkürzten/überzähligen Felder | bestanden |
| Pflichtwerte | fünf ausgewählte Aktivitätsfelder nicht leer/Whitespace | 0 fehlende Pflichtwerte |
| Identifikatoren | Textformat A + 6 Ziffern / U + 3 Ziffern; eindeutige Aktivitäts- und Nutzer-IDs | 6.465 / 100 eindeutige IDs |
| Fremdschlüssel | jede Aktivität verweist auf bekannten Nutzer | 0 unbekannte Nutzer |
| Nutzerattribute | Interessen ausschließlich True oder False | bestanden; nicht übernommen |
| Sportarten | genau acht dokumentierte Kategorien, keine Normalisierung | bestanden |
| Datum | gültiges Datum, exakte ISO-Rückdarstellung, innerhalb 05.01.–05.07.2026 | 0 ungültige/außerhalb liegende Daten; beide Randtage vorhanden |
| Dauer | endliche nicht negative Dezimalzahl; sportabhängige Grenzen | 0 ungültige oder unplausible Dauern |
| Distanz | strukturell leer bei Strength/Tennis/Padel, sonst endlich numerisch und plausibel | bestanden; 1.698 strukturell leere Felder |
| Export | erneutes Einlesen; exakte Spaltenfolge, Zeilen, IDs und sämtliche ausgewählten Werte | vollständig identisch |
| Summenkontrolle | Decimal-Summe aller Minuten vor/nach Export | jeweils 422.829,9 Minuten |
| Reproduzierbarkeit | zwei echte Skriptausführungen | identischer Inhalt und SHA-256 |

Dauergrenzen in Minuten: Running 10–150, Cycling 15–240, Strength 15–120, Swimming 10–100, Walking 10–180, Hiking 30–360, Tennis 20–180, Padel 20–150. Distanzsportarten verwenden Geschwindigkeitsgrenzen aus der Konfiguration: 5–16 / 8–35 / 0,8–3,5 / 2,5–6,5 / 1,5–6 km/h für Running/Cycling/Swimming/Walking/Hiking. Zulässige Distanz liegt zwischen `(Minuten−0,05)/60 × Mindestgeschwindigkeit−0,005` und `(Minuten+0,05)/60 × Höchstgeschwindigkeit+0,005`: berücksichtigt beide bereits erfolgten Quellrundungen. Nicht endliche Werte und negative Zahlen werden abgelehnt.

Leere Distanzen: Strength 851, Tennis 434, Padel 413. Fachlich nicht anwendbar, weder Fehler noch echte Null. Keine Bereinigung notwendig. Kein Entfernen statistischer Ausreißer allein aufgrund ungewöhnlicher Nutzerprofile.

## Auswahl und Ergebnis

Beibehalten: `activity_id` für Identifikation/Vollständigkeit, `user_id` für spätere Zuordnung, `date` für spätere zeitliche Einordnung, `sport_type` für spätere Sportanteile und Qualitätskontrolle, `duration_min` für spätere Umfangsbeschreibung. `distance_km` entfällt nur aus der Arbeitsdatei: für die ersten K-Means- und Regressionsmodelle nicht benötigt und sportartenübergreifend nicht unmittelbar vergleichbar. Rohdistanzen bleiben erhalten. Nutzerinteressen und Angebote werden nicht in diese Aktivitätstabelle integriert.

Ergebnis: `data/processed/activities_selected.csv`, 6.465 Datenzeilen × fünf Spalten, keine verlorene Aktivität, kein veränderter ausgewählter Wert. Noch keine Nutzer- oder Wochenaggregation, kein Zeitraster, keine K-Means-/Regressionsmerkmale, keine Skalierung und kein Modelltraining. Die 558 Nullwochen sind ein dokumentierter V2-Vertragswert; in AP 4.1 werden sie nicht neu aggregiert oder als Aktivitätszeilen angelegt. Die unveränderte vollständige Aktivitätsbasis und der Hash der bestehenden Wochenkontrolle bleiben erhalten.

## Tatsächliche Vorher-Nachher-Beispiele aus V2

### Beispiel 1: A000001

VORHER:

```json
{"activity_id": "A000001", "user_id": "U015", "date": "2026-01-05", "sport_type": "Hiking", "duration_min": "74.1", "distance_km": "5.69"}
```

VERARBEITUNG:

Qualitätsregeln prüfen; fünf Variablen in festgelegter Reihenfolge auswählen, `distance_km` ausschließen. Keine Werte verändern.

NACHHER:

```json
{"activity_id": "A000001", "user_id": "U015", "date": "2026-01-05", "sport_type": "Hiking", "duration_min": "74.1"}
```

Begründung: Identität, Nutzerzuordnung, Datum, Sportart und Dauer bleiben vollständig erhalten. Die Distanz ist für den ersten Modellansatz entbehrlich und bleibt in der Rohdatei verfügbar.

### Beispiel 2: A000022

VORHER:

```json
{"activity_id": "A000022", "user_id": "U069", "date": "2026-01-05", "sport_type": "Strength", "duration_min": "25.6", "distance_km": ""}
```

VERARBEITUNG:

Qualitätsregeln prüfen; fünf Variablen in festgelegter Reihenfolge auswählen, `distance_km` ausschließen. Keine Werte verändern.

NACHHER:

```json
{"activity_id": "A000022", "user_id": "U069", "date": "2026-01-05", "sport_type": "Strength", "duration_min": "25.6"}
```

Begründung: Identität, Nutzerzuordnung, Datum, Sportart und Dauer bleiben vollständig erhalten. Die Distanz ist für den ersten Modellansatz entbehrlich und bleibt in der Rohdatei verfügbar.

### Beispiel 3: A000521

VORHER:

```json
{"activity_id": "A000521", "user_id": "U001", "date": "2026-01-19", "sport_type": "Running", "duration_min": "43.7", "distance_km": "5.72"}
```

VERARBEITUNG:

Qualitätsregeln prüfen; fünf Variablen in festgelegter Reihenfolge auswählen, `distance_km` ausschließen. Keine Werte verändern.

NACHHER:

```json
{"activity_id": "A000521", "user_id": "U001", "date": "2026-01-19", "sport_type": "Running", "duration_min": "43.7"}
```

Begründung: Identität, Nutzerzuordnung, Datum, Sportart und Dauer bleiben vollständig erhalten. Die Distanz ist für den ersten Modellansatz entbehrlich und bleibt in der Rohdatei verfügbar.

## Integritätsnachweis und CRISP-DM-Status

| Eingabe | SHA-256 vor und nach beiden Läufen |
| --- | --- |
| `data/raw/activities_simulated.csv` | `c3789d26f00cba3ba14952cf99909b091cb263045b8993ed366fe5aa64a4ee6b` |
| `data/raw/users_simulated.csv` | `6ba9f8398707412bf922c76e352d2a6a7f86857e7a54dbbf1421555b1dbf99f9` |
| `data/raw/offers_simulated.csv` | `83748cb66918c08e3061889834e24452d0dc9feb6581690c4959cb3ba3775fa6` |
| `outputs/tables/simulation_weekly_check.csv` | `70c290c2913ea976fe0bb370b1debf4d78febb5896247f5e02a1f8aa0b1381b8` |

Ausgabe-SHA-256: `1dc3617cc2f9640bede26cae532bf2231fa3d7a7b3e97adc42d4d830a7f81fa1`.

AP 4.1 setzt die geplanten Schritte 3.1 und 3.2 tatsächlich um. Es trat kein Befund auf, der einen fachlichen Rücksprung erforderte; daher keine neue CRISP-DM-Iteration. Die bestehende historische Iteration bleibt unverändert dokumentiert. Für AP 4.2 wird die kontrollierte Wochenaggregation mit vollständigem Nutzerraster und Abgleich gegen die vorhandene Wochenkontrolle empfohlen.

## Zusätzliche technische Fehlerpfadprüfung

Zehn isolierte In-Memory-Varianten echter V2-Zeilen geprüft: leerer Pflichtwert, doppelte ID, unbekannter Nutzer, unbekannte Sportart, unmögliches Datum, Datum außerhalb des Zeitraums, negative Dauer, NaN, Dauer außerhalb Sportgrenzen und unplausible Distanz. Alle zehn führten zum erwarteten Abbruch vor dem Export. Die Varianten wurden nicht in Roh- oder Ergebnisdateien geschrieben; keine neuen synthetischen Forschungsdaten erzeugt. Die Ergebnisdatei blieb bytegleich. Dies ist ein technischer Test, keine fachliche CRISP-DM-Iteration. Ein Hashvergleich aller zuvor vorhandenen versionierten Dateien bestätigt: ausschließlich das ausdrücklich zu ergänzende Datenwörterbuch wurde verändert; bestehende Pläne, Rohdaten und Qualitätsberichte sind unverändert.


# AP 4.2 – ausgeführte Wochenaggregation und vollständiges Raster

Stand: 31.10.2026. CRISP-DM 3.3 Construct Data und 3.4 Integrate Data. Basis weiterhin Commit `ed52949cb8b688bc64c0793be0e407950314769e`, Branch `ap4-data-preparation`, Worktree `/workspace/MOVA-AP4`. Die vorherigen Abschnitte beschreiben den damaligen Stand von AP 4.1; die Wochenaggregation wurde erst in diesem Schritt erzeugt.

## Ziel und tatsächlich ausgeführte Verarbeitung

Eingaben: `data/processed/activities_selected.csv` und vollständige aktive Nutzerliste `data/raw/users_simulated.csv`. Unabhängige Kontrolle: `outputs/tables/simulation_weekly_check.csv`, tatsächlich geprüftes Schema `user_id,week_start,activity_count`. Aktive V2 und alle vier Manifest-Hashes werden vor/nach jedem Lauf geprüft; die ausgewählte AP-4.1-Datei wird zusätzlich gegen ihren dokumentierten SHA-256 `1dc3617cc2f9640bede26cae532bf2231fa3d7a7b3e97adc42d4d830a7f81fa1` geprüft. Kein V1-Zugriff.

1. Eingaben laden und Schema, Pflichtwerte, eindeutige IDs, Nutzerreferenzen, Sportarten und Dauergrenzen prüfen. Keine fehlerhaften Eingaben durch Null ersetzen.
2. Strikte ISO-Daten zu Kalenderdaten konvertieren und auf 05.01.–05.07.2026 begrenzen.
3. Montag als Datum minus Wochentag ableiten; `week_index = 1 + (week_start − 2026-01-05)/7`. `week_end = week_start + 6 Tage`. Jede Aktivität muss im zugeordneten Montag-Sonntag-Intervall liegen.
4. Alle Sportarten gemeinsam je Nutzer/Woche zählen und die ausgewählten Originalminuten mit Decimal summieren.
5. Vollständige Nutzerliste × 26 Wochen aufbauen; nach Nutzer und relativem Wochenindex sortieren.
6. Aggregate anhand eindeutiger Nutzer-Wochen-Schlüssel in das Raster integrieren. Fehlende Gruppen erhalten ausschließlich hier 0 Aktivitäten und 0 Minuten.
7. Alle Abnahmekriterien vor Export prüfen; CSV kontrolliert exportieren, erneut einlesen und nochmals validieren. Jede Wochenzeile zusätzlich über einen unabhängigen Datumsintervallfilter gegen die Einzelaktivitäten prüfen.

Ergebnis: `data/processed/user_weekly_activities.csv`, sechs Spalten in Reihenfolge `user_id,week_index,week_start,week_end,activities_count,total_duration_min`. Der konkrete Benutzerauftrag präzisiert die früher geplanten Pfade/Spaltennamen: `activities_count` heißt im neuen Export bewusst anders als `activity_count` in der unveränderten Kontrolltabelle. Keine zweite Zählquelle integriert; Kontrolle nur verglichen.

## Tatsächliche Qualitätsprüfungen und Ergebnisse

| Prüfung | Tatsächliches Ergebnis |
| --- | --- |
| Belegte Nutzerwochen vor Rasterergänzung | 2.042 |
| Ergänzte Nullwochen | 558 |
| Vollständiges Ergebnis | 2.600 Zeilen × sechs Spalten |
| Nutzer / Wochen je Nutzer | 100 / exakt 26 |
| Eindeutige Nutzer-Wochen-Schlüssel / fehlende Rasterkombinationen | 2.600 / 0 |
| Erste Woche | Index 1, 2026-01-05 bis 2026-01-11 |
| Letzte Woche | Index 26, 2026-06-29 bis 2026-07-05 |
| Intervalllänge | Jede Woche sieben Kalendertage einschließlich beider Grenzen |
| Sortierung / Schema | exakt vorgegeben |
| Negative oder ungültige Zahlen | keine; Counts ganzzahlig und in V2 höchstens 10 |
| Aktivitäten insgesamt | 6.465, entspricht allen Eingabeaktivitäten |
| Trainingsminuten insgesamt | 422.829,9, exakt mit Decimal erhalten |
| Minuten bei Nullwochen | in allen 558 Fällen 0 |
| Kalenderzuordnung | alle Aktivitäten korrekt; unabhängiger Intervallabgleich für jede Wochenzeile bestanden |
| Wochenkontrolle | alle 2.600 Schlüssel und Counts identisch, keine Abweichung |
| Eingabeintegrität | vier V2-Hashes und ausgewählte Arbeitsdatei unverändert |
| Reproduzierbarkeit | zwei protokollierte Läufe mit identischen SHA-256-Werten; zusätzlicher Lauf mit direktem Bytevergleich bestanden |

Echte Nullwochen bezeichnen fehlende Aktivitätsgruppen innerhalb des bestätigten vollständigen Beobachtungszeitraums; sie sind keine fehlenden Pflichtwerte. Keine neuen Aktivitätszeilen angelegt. `week_index` ist eine relative Projektwoche und keine ISO-Kalenderwochennummer. `week_end` ist ausschließlich zeitliche Zuordnung/Visualisierung, kein Machine-Learning-Eingangsmerkmal.

## Reproduktion und zusätzliche technische Prüfungen

Aufruf: `python src/data_preparation_weekly.py`. Python 3.12.14, ausschließlich Standardbibliothek. UTF-8, LF, Komma, Dezimalpunkt, ISO-Daten, kein Indexexport; deterministische Sortierung. Identische vorhandene Ausgabe wird akzeptiert, abweichende nicht überschrieben. Bei Fehlern Abbruch mit Befund auf stderr/Exitcode 1. Bereits vor AP 4.2 vorhandene Daten, Skripte, Pläne und Qualitätsberichte wurden per Hashvergleich auf Unverändertheit geprüft; lediglich die ausdrücklich zu ergänzenden Dokumentationsdateien werden anschließend erweitert.

Technische Prüfung (`work/verify_ap42.py`): Sonntag 11.01. → Montag 05.01., Montag 12.01. → gleiche Woche, letzter Sonntag 05.07. → Montag 29.06. Zusätzlich zehn Fehlerfälle mit In-Memory-Kopien echter V2-Daten: fehlende Dauer, unbekannter Nutzer, unmögliches Datum, Datum außerhalb Zeitraum, negative Dauer, NaN, doppelte Aktivitäts-ID, falsche Kontrollzählung, falscher Kontrollschlüssel, falsches week_end. Alle wurden erwartungsgemäß abgelehnt. Keine Forschungsdaten verändert oder neu simuliert.

Ausgabe-SHA-256: `c34a7bd16d1cdc3e91388cc35b8c784afde0b53c1dbfdd24de97148350359b74`.

## Tatsächliche Vorher-Nachher-Beispiele aus V2

### A – mehrere Einzelaktivitäten

VORHER:

```json
[
  {
    "activity_id": "A000521",
    "user_id": "U001",
    "date": "2026-01-19",
    "sport_type": "Running",
    "duration_min": "43.7"
  },
  {
    "activity_id": "A000651",
    "user_id": "U001",
    "date": "2026-01-22",
    "sport_type": "Cycling",
    "duration_min": "102.3"
  }
]
```

VERARBEITUNG:

Alle Aktivitäten dieses Nutzers im Intervall zählen und Minuten addieren. Beide Sportarten zählen als Aktivitäten.

NACHHER:

```json
{
  "user_id": "U001",
  "week_index": "3",
  "week_start": "2026-01-19",
  "week_end": "2026-01-25",
  "activities_count": "2",
  "total_duration_min": "146.0"
}
```

Fachliche Bedeutung: Die Kalenderwoche bildet eine einheitliche Beobachtungseinheit; Aktivitätszahl und Minuten gehen nicht verloren.

### B – fehlende Aktivitätsgruppe

VORHER:

```json
[]
```

VERARBEITUNG:

Für U001 existiert vom 05.–11.01.2026 keine Aktivitätszeile. Das vollständige Raster liefert den Schlüssel; nur diese fehlende Gruppe wird mit 0 Aktivitäten und 0 Minuten ergänzt.

NACHHER:

```json
{
  "user_id": "U001",
  "week_index": "1",
  "week_start": "2026-01-05",
  "week_end": "2026-01-11",
  "activities_count": "0",
  "total_duration_min": "0"
}
```

Fachliche Bedeutung: Abwesenheit einer Aktivitätsgruppe bleibt als echte Nullwoche im gemeinsamen Kalender erhalten.

### C – tatsächliche Sonntagsaktivität

VORHER:

```json
[
  {
    "activity_id": "A000204",
    "user_id": "U003",
    "date": "2026-01-11",
    "sport_type": "Padel",
    "duration_min": "43.3"
  }
]
```

VERARBEITUNG:

Die gezeigte Sonntagsaktivität wird dem vorangehenden Montag zugeordnet. Die Ergebniszeile umfasst sämtliche Aktivitäten dieses Nutzers in dieser Woche, nicht nur die gezeigte Aktivität.

NACHHER:

```json
{
  "user_id": "U003",
  "week_index": "1",
  "week_start": "2026-01-05",
  "week_end": "2026-01-11",
  "activities_count": "2",
  "total_duration_min": "90.4"
}
```

Fachliche Bedeutung: Die Kalenderwoche bildet eine einheitliche Beobachtungseinheit; Aktivitätszahl und Minuten gehen nicht verloren.

## Grenzen und CRISP-DM-Status

Keine Datenfehler oder Kontrollabweichungen aufgetreten. Kein fachlicher Rücksprung nötig und keine neue CRISP-DM-Iteration behauptet. Keine K-Means-Nutzermerkmale, Regressionsfenster/Zielvariablen oder Skalierungen erstellt; keine Modelle trainiert. Die Wochenwerte sind tatsächlich erzeugte vorbereitete Daten und noch keine vollständige Modellierungstabelle. Keine Simulationsparameter, Rohdaten, AP-4.1-Arbeitsdatei oder vorhandenen Qualitätsberichte verändert. Kein Commit oder Pull Request erstellt.


# AP 4.3 – tatsächlich konstruierte unskalierte K-Means-Nutzermerkmale

Stand: 31.10.2026. CRISP-DM 3.3 Construct Data und 3.4 Integrate Data. Ausführung ausschließlich in `/workspace/MOVA-AP4`, Branch `ap4-data-preparation`, Basiscommit `ed52949cb8b688bc64c0793be0e407950314769e`. Frühere Abschnitte dokumentieren den Stand der jeweiligen abgeschlossenen Schritte; die Nutzermerkmalstabelle wurde erst jetzt erzeugt.

## Ziel, Eingaben und Entscheidungen

Das vorhandene K-Means-Konzept praktisch als unskalierte Tabelle umsetzen: ein Aktivitätsniveau und acht Sportartenanteile als neun spätere Eingänge, zusätzlich Wochenminuten und Sportvielfalt ausschließlich zur Interpretation. Keine Interessen, Angebote, IDs oder Datumsfelder als Modelleingänge. Umfang würde das Aktivitätsniveau zusätzlich gewichten; Vielfalt ist bereits aus positiven Anteilen ableitbar und bleibt deshalb ebenfalls außerhalb der Basiseingänge.

Eingaben: `data/processed/activities_selected.csv`, `data/processed/user_weekly_activities.csv` und `data/raw/users_simulated.csv`. V2-Manifest und Konzept/Plan gelesen. Alle vier V2-Manifest-Prüfsummen sowie die dokumentierten AP-4.1-/AP-4.2-Ausgabehashes vor und nach jedem Lauf geprüft. Vorhandene Wochen einschließlich Kontrollzählungen nur validiert; keine neue Wochenaggregation konzipiert oder gespeichert. Keine V1-Dateien verwendet.

## Tatsächlich ausgeführte Transformationen

1. Quellen und deren Schema, Integrität und V2-Sollzahlen prüfen; vorhandenes vollständiges Wochenraster einschließlich Kalender-/Intervallprüfung validieren.
2. Einzelaktivitäten pro Nutzer zählen: N_u.
3. Originalminuten mit Decimal je Nutzer summieren: T_u.
4. Je Sportart zählen: N_us; acht Anteile N_us/N_u berechnen. Ein nicht beobachteter Sport bei aktivem Nutzer hat Anteil 0.
5. Verschiedene tatsächlich beobachtete Sportarten zählen.
6. Vollständige Nutzerliste als führende Menge verwenden, Aggregate je Nutzer verbinden und nach user_id sortieren.
7. Nutzermerkmale gegen Einzelaktivitäten und nutzerbezogene Summen der Wochenaggregate prüfen.
8. Erst nach erfolgreicher Prüfung deterministisch exportieren; Ergebnis erneut laden und vollständig validieren.

Formeln: `avg_activities_per_week = N_u/26`; `share_s = N_us/N_u`; `avg_duration_per_week = T_u/26`; `sport_diversity = Anzahl Sportarten mit N_us > 0`. Immer 26 Wochen im Nenner, einschließlich Nullwochen. Keine Beschränkung auf aktive Wochen und keine weitere Rundung für die Anzeige im CSV. Das Skript führt explizite Positivlisten `MODEL_FEATURES` (neun) und `INTERPRETATION_FEATURES` (zwei); es erzeugt noch keine skalierte Eingabematrix.

## Ergebnis und tatsächlich bestandene Validierungen

Datei: `data/processed/kmeans_user_features.csv`, exakt 100 Datenzeilen und zwölf Spalten in vorgegebener Reihenfolge. user_id ist ein Zuordnungsschlüssel, kein elftes/zwölftes Modellmerkmal.

| Prüfung | Tatsächliches Ergebnis |
| --- | --- |
| Vollständigkeit / Eindeutigkeit / Sortierung | Alle 100 Nutzer, genau eine Zeile je Nutzer, aufsteigend |
| Fehlende / negative / nicht endliche Werte | Keine in aktiver V2 |
| Anteilgrenzen / Anteilssummen | Alle acht Anteile je Nutzer in [0,1]; Summe 1 innerhalb Toleranz |
| Einzelne Sportanteile | Für jede Nutzer-Sport-Kombination gegen N_us/N_u geprüft |
| Häufigkeit × 26 | Rekonstruiert für jeden Nutzer N_u innerhalb Toleranz |
| Wochenminuten × 26 | Rekonstruiert für jeden Nutzer T_u innerhalb Toleranz |
| Wochenvergleich | Aktivitätszahlen und Decimal-Minuten für alle 100 Nutzer identisch |
| Gesamtsummen | 6.465 Aktivitäten, 422.829,9 Minuten, auch aus Wochenmitteln rekonstruierbar |
| Sportvielfalt | Exakt Zahl positiver Sportcounts, tatsächlich 4–8 |
| Berechtigte / vollständig inaktive Nutzer | 100 / 0 |
| CSV-Rücklesen | Schema, zwölf Spalten und sämtliche Werte identisch |
| Reproduzierbarkeit | Zwei echte Läufe; direkter Bytevergleich und identische Prüfberichte bestanden |
| Eingaben / ältere Skripte / Pläne / Qualitätsberichte | Unverändert; vor Dokumentationsergänzung alle vorhandenen Projektdateien per Hash verglichen |

Numerik: Aktivitätscounts als Integer, Minutenaggregate als Decimal; Wochenmittel und Anteile als Float mit vollständiger Python-Repräsentation exportiert. Rekonstruktions- und Anteiltests verwenden `math.isclose` mit absoluter Toleranz 1e−9 und relativer Toleranz 1e−12. Rationale Quotienten wie 34/26 haben keine endliche Dezimaldarstellung; deshalb keine Forderung nach bitgenauer Float-Multiplikation. Exakte Quellsummen werden zusätzlich unabhängig kontrolliert.

## Vollständig inaktive künftige Nutzer

Die wiederverwendbare Konstruktion behält jeden Nutzer aus der vollständigen Liste. Bei N_u=0: Häufigkeit 0, Wochenminuten 0 und Sportvielfalt 0; acht Anteile intern `None`, im CSV leere Felder. Diese stehen für **undefinierte Sportpräferenz**, nicht acht echte Nullanteile. Kein künstlicher Mix und keine Division durch 0.

Der Rückgabewert führt gesondert `eligibility_status=inactive_no_sport_mix` je betroffenem Nutzer. Dieser Status steht im Prüfbericht, nicht als zusätzliche dreizehnte CSV-Spalte. In der späteren Modellierung und beim Skalierungsfit müssen diese Nutzer separat ausgewiesen und vom Sportmix-K-Means ausgeschlossen werden; fehlende Anteile nicht mit Null imputieren. Aktuelle V2 enthält ausschließlich aktive Nutzer: der konkrete V2-CLI-Vertrag bricht bei unerwarteter Inaktivität ab, statt den freigegebenen Datensatz still umzudeuten. Andere zukünftige Daten benötigen einen neuen freigegebenen Datenvertrag, während die generische Konstruktionsfunktion diese Regel bereits unterstützt.

Technischer Test: echte U001-Aktivitäten ausschließlich aus einer Speicherkopie entfernt und entsprechende Speicherkopie der Wochenwerte auf Null gesetzt. Konstruktion/Validierung bestanden mit weiterhin 100 Nutzern, korrekt leeren Anteilen und separatem Status; CSV-Leerfeldrepräsentation explizit geprüft. Keine neue synthetische Forschungsdatei, keine Änderung an aktiven Daten. Fünf weitere Fehlerfälle (falscher Sportmix trotz erhaltener Anteilssumme, falsche Vielfalt, falsche nutzerbezogene Wochenzählung, fehlender Nutzer, NaN) wurden erwartungsgemäß abgelehnt. Reproduktionsprüfung lokal: `python work/verify_ap43.py`.

## Drei tatsächliche Vorher-Nachher-Beispiele aus aktiver V2

Alle drei Beispiele verwenden U001, unverändert aus der ausgewählten V2-Aktivitätsdatei berechnet. Die vollständigen 34 Quellaktivitäten sind über user_id auffindbar; hier werden ihre tatsächlichen Aggregate ausgewiesen, keine hypothetischen Daten.

### A – Einzelaktivitäten → mittlere Aktivitäten pro Woche

VORHER: U001 hat tatsächlich 34 Einzelaktivitäten im gesamten Beobachtungszeitraum; beispielsweise A000521 am 19.01.2026 und A000651 am 22.01.2026.

VERARBEITUNG: Alle 34 Aktivitäts-IDs zählen und durch die vollständigen 26 Wochen teilen.

NACHHER: `avg_activities_per_week = 34/26 = 1.3076923076923077`.

Bedeutung: Beschreibt das Aktivitätsniveau für das spätere Clustering einschließlich der Nullwochen, ohne aktive Wochen überzugewichten.

### B – Sportaktivitäten → acht Sportartenanteile

VORHER: Tatsächliche Counts U001: Running 17, Cycling 3, Strength 0, Swimming 0, Walking 11, Hiking 3, Tennis 0, Padel 0.

VERARBEITUNG: Jeden Count durch 34 teilen; alle acht Kategorien in festgelegter Reihenfolge erhalten.

NACHHER:

```json
{
  "share_running": "0.5",
  "share_cycling": "0.08823529411764706",
  "share_strength": "0.0",
  "share_swimming": "0.0",
  "share_walking": "0.3235294117647059",
  "share_hiking": "0.08823529411764706",
  "share_tennis": "0.0",
  "share_padel": "0.0"
}
```

Anteilssumme innerhalb Toleranz 1; `sport_diversity = 4`. Bedeutung: Sportpräferenz getrennt vom Aktivitätsniveau darstellen; nicht ausgeübte Sportarten bei aktivem Nutzer sind echte Nullanteile. Vielfalt bleibt nur Interpretation.

### C – Einzelminuten → mittlere Wochenminuten

VORHER: Summe der Originalminuten aller U001-Aktivitäten = 2086.0 Minuten; beispielsweise 43.7 Minuten für A000521 und 102.3 für A000651.

VERARBEITUNG: Exakte Minutensumme durch 26 teilen.

NACHHER: `avg_duration_per_week = 2086.0/26 = 80.23076923076923`.

Bedeutung: Beschreibt den zeitlichen Trainingsumfang für die spätere Interpretation; bewusst kein zusätzlicher Eingang des ersten K-Means-Modells.

## Reproduktion, Herkunft und Übergabe

Aufruf: `python src/data_preparation_kmeans.py`. Python 3.12.14, ausschließlich Standardbibliothek. CSV: UTF-8/LF, Komma, Dezimalpunkt, keine Indexspalte; unveränderte Eingaben. Identische vorhandene Ausgabe wird akzeptiert, eine abweichende nicht überschrieben. Kritische Fehler führen zum Abbruch mit Befund auf stderr und Exitcode 1.

Ausgabe-SHA-256: `bb6b0c4e9307ab286f9f6e76d04b9b1446a9ab322e31784c8883a6a596ca7a28`.

Keine Datenfehler oder Kontrollabweichungen festgestellt. Bestehende Hinweise aus AP 3 (z. B. hoher Umfang U045 und hohe Sportanteile) bleiben bestehen, sind keine automatisch zu korrigierenden Datenfehler. Keine statistische Ausreißerbereinigung durchgeführt. Keine neue CRISP-DM-Iteration ohne Anlass. Keine Skalierung, keine Clusterlabels und keine K-Means- oder Regressionsmodelle. Kein Commit oder Pull Request.

AP 4.4 kann die neun explizit benannten Eingänge gemäß bestehendem Konzept standardisieren/gewichten und Parameter dokumentieren; user_id sowie Wochenminuten und Sportvielfalt bleiben außerhalb der Eingabematrix. Die tatsächlichen elf Nutzermerkmale sind jetzt gespeichert, ihre Skalierung und Modellverwendung stehen weiterhin aus.


# AP 4.4 – tatsächliche Standardisierung und Gewichtung für K-Means

Stand: 31.10.2026. CRISP-DM 3.5 Format Data. Ausschließlich `/workspace/MOVA-AP4`, Branch `ap4-data-preparation`, Basis `ed52949cb8b688bc64c0793be0e407950314769e`. Die AP-4-Skripte sind noch uncommitted. Frühere Abschnitte beschreiben den damaligen Stand; diese Standardisierung wurde erst in AP 4.4 ausgeführt.

## Ziel, Grundlage und tatsächlich ausgeführte Verarbeitung

Input: unveränderte aktive V2-Datei `data/processed/kmeans_user_features.csv`, 100 Zeilen × zwölf Spalten. Bestehende Entscheidungen aus K-Means-Konzept und Data-Preparation-Plan übernommen. Ausschließlich neun Eingänge in fester Reihenfolge: avg_activities_per_week, share_running, share_cycling, share_strength, share_swimming, share_walking, share_hiking, share_tennis, share_padel. user_id bleibt Identifikation; avg_duration_per_week und sport_diversity ausschließlich Interpretation. Interessen und interne Simulationsprofile sind keine Eingänge.

1. V2-Vertrag, vier Manifest-Prüfsummen und dokumentierten Hash der unskalierten Tabelle prüfen.
2. Eindeutige/vollständige Nutzer, Schema, fehlende Werte, numerische Endlichkeit, positive Aktivität und Sportanteile prüfen.
3. Neun Merkmale explizit auswählen.
4. `sklearn.preprocessing.StandardScaler(with_mean=True, with_std=True)` auf allen 100 berechtigten Profilen fitten.
5. `transform` mit z=(x−mean_)/scale_ anwenden.
6. Nur acht share_*-Spalten mit 1/√8 multiplizieren; standardisierte Häufigkeit bleibt unverändert.
7. Mittelwerte, Populationsvarianzen, Endlichkeit, Konstanten und inverse Transformation validieren.
8. Erst nach Prüfungen CSV und JSON speichern; vorhandene abweichende Ausgaben werden nicht überschrieben. Beide erneut einlesen und Parameterwiederverwendung validieren.

Dies ist ein deskriptives unüberwachtes Profiling der vorhandenen Nutzer: keine Zielvariable und kein Regressions-Train/Test-Split. Fit aller 100 Nutzer gilt für diesen Zweck; es ist kein Prognoseexperiment und keine Evaluation neuer Nutzer. Standardisierung stellt verschiedene Skalen vergleichbar dar. Die acht Anteile bleiben kompositionell abhängig; Standardisierung hebt die Summenabhängigkeit nicht auf.

## Tatsächliche Parameter

Populationsvarianz ddof=0. Standardabweichung = sqrt(var_), bei normalen Merkmalen zugleich scale_. Die folgenden Werte sind tatsächliche Fitparameter (Anzeige auf 12 signifikante Stellen, volle Präzision im JSON):

| Merkmal | mean_ | sqrt(var_) | scale_ | Gewicht |
| --- | --- | --- | --- | --- |
| avg_activities_per_week | 2.48653846154 | 1.28689773068 | 1.28689773068 | 1 |
| share_running | 0.152777883728 | 0.162942587756 | 0.162942587756 | 0.353553390593 |
| share_cycling | 0.163644386169 | 0.158959542165 | 0.158959542165 | 0.353553390593 |
| share_strength | 0.124040233467 | 0.161379978437 | 0.161379978437 | 0.353553390593 |
| share_swimming | 0.0925986813324 | 0.144493959498 | 0.144493959498 | 0.353553390593 |
| share_walking | 0.195142313686 | 0.157446084273 | 0.157446084273 | 0.353553390593 |
| share_hiking | 0.137038791683 | 0.130328342819 | 0.130328342819 | 0.353553390593 |
| share_tennis | 0.0689465669346 | 0.0819892456506 | 0.0819892456506 | 0.353553390593 |
| share_padel | 0.0658111429996 | 0.076275481997 | 0.076275481997 | 0.353553390593 |

StandardScaler behandelt Nullvarianz mit technischem scale_=1, nicht mit Division durch 0. Numerisch von konstant nicht unterscheidbare Merkmale behandelt scikit-learn ebenfalls so. Geprüfte Schranke: `var <= n*eps*var + (n*mean*eps)^2`, eps der float64-Maschinentyp; Status und echte Standardabweichung werden getrennt von scale_ gespeichert. Konstante Fitwerte ergeben nach Zentrierung numerisch 0 (Rundungstoleranz beachten); neue abweichende Werte werden regulär mit derselben Skala 1 transformiert, nicht pauschal auf 0 gesetzt.

Aktive V2: keine konstanten oder numerisch konstanten Eingänge. Isolierte technische Testvektoren mit konstanten und numerisch nahezu konstanten Werten bestanden: endliche Ergebnisse, scale_=1 bei Konstanten und keine Division durch 0. Keine Forschungsdaten erzeugt/geändert. Wenn künftig Koordinaten konstant werden, sinkt die zugehörige Blockvarianz; dies erfordert eine dokumentierte fachliche Neubewertung, keine automatische Änderung von √8.

## Gewichtung und tatsächliche Validierung

1/√8 = 0.35355339059327373. Alle neun Eingänge besitzen in V2 positive Varianz. Vor Gewichtung: jede standardisierte Koordinate hat Populationsvarianz ungefähr 1. Nach Gewichtung: Häufigkeit ungefähr 1, jede Sportkoordinate ungefähr 1/8. Somit ist die Summe der Einzelvarianzen je Block 1: Niveau 1 und Sportmix 8×1/8. Dies bedeutet gleiche aggregierte Streuungsgewichtung, keine garantierte gleiche fachliche Wirkung oder Unabhängigkeit. Fachliche Startannahme, keine empirisch optimierte Clustergewichtung; tatsächliche Clusterwirkung erst in AP 5 prüfen.

| Prüfung | Tatsächliches Ergebnis |
| --- | --- |
| Nutzer / Zeilen / Spalten | 100 vollständig und eindeutig / 100 / 10 |
| Schema / Sortierung | user_id + exakt neun Eingänge, user_id aufsteigend |
| Interpretation, Interessen, Profile in Matrix | keine |
| Fehlende / nicht endliche Werte | keine |
| Standardisierte Mittelwerte | größter absoluter Mittelwert 4.3631764867768654e-16 |
| Varianzen vor Gewichtung | alle neun ungefähr 1 |
| Varianzen nach Gewichtung | Häufigkeit ungefähr 1, Sportanteile jeweils ungefähr 0,125 |
| Blockvarianzsummen | 1.0000000000000002 und 0.9999999999999998 |
| Konstanten / numerisch konstante Merkmale | keine in aktiver V2; technische Tests bestanden |
| Inverse Transformation | Gewichtung rückgängig machen, inverse_transform liefert ursprüngliche neun Werte innerhalb Toleranz |
| JSON-Parameter → CSV | ursprüngliche neun Werte mit tatsächlich gespeicherten Parametern transformiert; alle Ausgabewerte innerhalb Toleranz reproduziert |
| Parameter für einzelne Profile | U001, U045, U100 ohne Refit reproduziert |
| Reproduzierbarkeit | CSV und JSON nach zwei tatsächlichen Skriptläufen jeweils bytegleich |
| Eingabeintegrität | vier V2-Hashes und unskalierte Tabelle unverändert; zusätzlich alle vorher vorhandenen Projektdateien per Hash geprüft |

Vergleichstoleranz: atol=rtol=1e−10. CSV-Rücklesen zusätzlich elementweise bitgleich mit exportierter Matrix geprüft. Negative standardisierte Werte sind zulässig: sie bedeuten einen Wert unter dem jeweiligen Mittelwert, keine negative rohe Trainingshäufigkeit oder Sportpräferenz. Standardisierte/gewichtete Sportkoordinaten sind keine ursprünglichen Anteile oder Wahrscheinlichkeiten und summieren sich nicht mehr notwendigerweise auf 1.

## Wiederverwendung und Reproduktion

Skriptaufruf: `python src/data_preparation_scaling.py`. Software: {"numpy": "2.3.5", "python": "3.12.14", "scikit_learn": "1.8.0"}. CSV UTF-8/LF, Komma, Dezimalpunkt, kein Index, unveränderte Quell-IDs. JSON ohne Zeitstempel, mit deterministischer Schlüsselreihenfolge und vollständiger numerischer Präzision.

Ausgaben: `data/processed/kmeans_user_features_scaled.csv` und `outputs/models/kmeans_scaling_params.json`. Kein K-Means-Modell gespeichert. Der präzisierte Benutzerauftrag legt diese Pfade fest; die früher im AP-3-Plan genannten Pfade bleiben als historische Planung unverändert.

`transform_saved(rows, params)` wählt exakt feature_order, berechnet (x−mean)/scale und multipliziert je Merkmal mit dem gespeicherten Faktor. Keine Anpassung der Parameter und kein Refit für neue aktive Profile. Fehlende/undefinierte Sportanteile inaktiver Nutzer vorher separat ausweisen; nicht als künstliche Nullprofile transformieren. Tests lehnen fehlende Eingänge und NaN ab. Parameterdatei enthält Fitnutzer, Merkmalsfolge, Mittelwerte, var_, Standardabweichung, scale_, Faktoren, Konstantenstatus, Softwareversionen und Eingangs-/Ausgabehashes. Die Funktion kann einzeln neue berechtigte Profile transformieren; die CLI bleibt auf den freigegebenen V2-Fit zugeschnitten.

Lokale technische Reproduktion: `python work/verify_ap44.py`.

## Drei tatsächliche V2-Vorher-Nachher-Beispiele

Die folgenden Nutzer und Ursprungswerte stammen tatsächlich aus `kmeans_user_features.csv`. z-Werte sind mit den echten Parametern berechnet. Anzeige auf neun Nachkommastellen; CSV/JSON enthalten volle Präzision.

### Tatsächlicher Nutzer U001

VORHER → VERARBEITUNG → NACHHER:

| Merkmal | Ursprünglich | Standardisiert z | Nach Gewichtung / Export |
| --- | --- | --- | --- |
| avg_activities_per_week | 1.307692308 | -0.916037169 | -0.916037169 |
| share_running | 0.500000000 | 2.130947600 | 0.753403749 |
| share_cycling | 0.088235294 | -0.474391729 | -0.167722804 |
| share_strength | 0.000000000 | -0.768622196 | -0.271748984 |
| share_swimming | 0.000000000 | -0.640848113 | -0.226574023 |
| share_walking | 0.323529412 | 0.815435320 | 0.288299922 |
| share_hiking | 0.088235294 | -0.374465726 | -0.132393627 |
| share_tennis | 0.000000000 | -0.840922079 | -0.297310852 |
| share_padel | 0.000000000 | -0.862808615 | -0.305048911 |

Bedeutung: Einheiten und Größenordnungen ändern sich durch Zentrierung und Skalierung; der individuelle Rohwert bleibt unverändert in der Quelldatei. Häufigkeit wird relativ zum Nutzerkollektiv dargestellt, Sportkoordinaten zusätzlich mit dem gemeinsamen Faktor gewichtet. Dies bereitet euklidische Abstände für K-Means vor, ohne bereits eine Clusterzuordnung vorzunehmen.

### Tatsächlicher Nutzer U045

VORHER → VERARBEITUNG → NACHHER:

| Merkmal | Ursprünglich | Standardisiert z | Nach Gewichtung / Export |
| --- | --- | --- | --- |
| avg_activities_per_week | 6.192307692 | 2.879614395 | 2.879614395 |
| share_running | 0.068322981 | -0.518310796 | -0.183250539 |
| share_cycling | 0.031055901 | -0.834102085 | -0.294899620 |
| share_strength | 0.596273292 | 2.926218376 | 1.034574429 |
| share_swimming | 0.037267081 | -0.382933659 | -0.135387493 |
| share_walking | 0.099378882 | -0.608229999 | -0.215041778 |
| share_hiking | 0.012422360 | -0.956172915 | -0.338058176 |
| share_tennis | 0.099378882 | 0.371174473 | 0.131229993 |
| share_padel | 0.055900621 | -0.129930636 | -0.045937417 |

Bedeutung: Einheiten und Größenordnungen ändern sich durch Zentrierung und Skalierung; der individuelle Rohwert bleibt unverändert in der Quelldatei. Häufigkeit wird relativ zum Nutzerkollektiv dargestellt, Sportkoordinaten zusätzlich mit dem gemeinsamen Faktor gewichtet. Dies bereitet euklidische Abstände für K-Means vor, ohne bereits eine Clusterzuordnung vorzunehmen.

### Tatsächlicher Nutzer U100

VORHER → VERARBEITUNG → NACHHER:

| Merkmal | Ursprünglich | Standardisiert z | Nach Gewichtung / Export |
| --- | --- | --- | --- |
| avg_activities_per_week | 3.769230769 | 0.996732123 | 0.996732123 |
| share_running | 0.040816327 | -0.687122739 | -0.242934574 |
| share_cycling | 0.132653061 | -0.194963602 | -0.068930043 |
| share_strength | 0.122448980 | -0.009860293 | -0.003486140 |
| share_swimming | 0.132653061 | 0.277204528 | 0.098006601 |
| share_walking | 0.153061224 | -0.267273012 | -0.094495280 |
| share_hiking | 0.387755102 | 1.923728215 | 0.680140633 |
| share_tennis | 0.000000000 | -0.840922079 | -0.297310852 |
| share_padel | 0.030612245 | -0.461470674 | -0.163154522 |

Bedeutung: Einheiten und Größenordnungen ändern sich durch Zentrierung und Skalierung; der individuelle Rohwert bleibt unverändert in der Quelldatei. Häufigkeit wird relativ zum Nutzerkollektiv dargestellt, Sportkoordinaten zusätzlich mit dem gemeinsamen Faktor gewichtet. Dies bereitet euklidische Abstände für K-Means vor, ohne bereits eine Clusterzuordnung vorzunehmen.

## Integrität, Auffälligkeiten und Übergabe

- `data/processed/kmeans_user_features_scaled.csv`: SHA-256 `73f1694e865c8f65b0eabb45f7a80bd439bbc9bfd4b6f281cffaa15da491d78f`
- `outputs/models/kmeans_scaling_params.json`: SHA-256 `1794271bbfaf53818511002a13247c8cb251d5871b0b62e62729d817356a24b4`

Alle Prüfungen bestanden. Keine Datenfehler, Kontrollabweichungen oder konstanten Eingänge in V2. Negative skalierte Werte sind erwartbar. Kein Anlass für eine neue CRISP-DM-Iteration; bestehende historische Iterationen unverändert. Keine Regression vorbereitet, keine Modelle trainiert, keine Clusterlabels/Modellgüte erzeugt. Keine bestehenden Modellierungstabellen oder Qualitätsberichte überschrieben. Kein Commit und kein Pull Request. AP 4.5 kann auf diesen geprüften Artefakten fortgesetzt werden.


# AP 4.5 – tatsächlich konstruierte Regressionsmerkmale und Zielvariable

Stand: 31.10.2026. CRISP-DM 3.3 Construct Data, 3.4 Integrate Data und 3.5 Format Data. Worktree `/workspace/MOVA-AP4`, Branch `ap4-data-preparation`, Quellbasis `ed52949cb8b688bc64c0793be0e407950314769e`; AP-4-Änderungen weiterhin uncommitted. Die vorherigen Abschnitte dokumentieren jeweils den damaligen Bearbeitungsstand.

## Ziel, Quellen und Präzisierung des bestehenden Plans

Aus der vorhandenen vollständigen Wochenstruktur zwei vergangenheitsbezogene Eingänge und ein beobachtetes Einwochen-Folgeziel konstruieren. Ausgang: ausschließlich aktive V2 in `data/processed/user_weekly_activities.csv`, 100 Nutzer × 26 Wochen = 2.600 Nutzerwochen, 558 Nullwochen, 6.465 Aktivitäten und 422.829,9 Minuten. Nutzerliste und V2-Manifest dienen der Integritätskontrolle; keine neue Wochenaggregation und keine K-Means-Merkmale als Regressoren.

Vor jedem Lauf werden die vier V2-Manifest-Hashes und der dokumentierte Wochen-Dateihash `c34a7bd16d1cdc3e91388cc35b8c784afde0b53c1dbfdd24de97148350359b74` geprüft. Die Wochenzeilen sind fachliche Berechnungsquelle, die vollständige aktive Nutzerliste prüft ihre Vollständigkeit. Konzept und Vorbereitungsplan wurden berücksichtigt.

Der aktuelle Benutzerauftrag präzisiert den früheren Gesamtplan: AP 4.5 exportiert sieben Spalten einschließlich week_end, ohne split und ohne target_week_start. Die Zielwoche wird intern als week_start + 7 Tage geprüft. Train/Test-Zuordnung ausdrücklich erst AP 4.6; historische Planungsdokumente werden nicht geändert. activities_previous_week bleibt optionale, nicht erzeugte Erweiterung.

## Tatsächlich ausgeführte Verarbeitung und Formeln

1. Wochendaten unverändert einlesen, Schema und V2-Integrität prüfen.
2. Vollständige bekannte Nutzer, genau 26 eindeutige Wochen je Nutzer, strikte ISO-Daten, Montag-Sonntag-Intervalle, endliche nicht negative Minuten und ganzzahlige nicht negative Counts prüfen. Lücken oder ungültige Eingaben führen zum Abbruch, niemals zur Auffüllung.
3. Innerhalb jedes Nutzers nach relativem week_index sortieren. Projektwochen sind keine ISO-Kalenderwochennummern.
4. Vierwochenmittel ausschließlich aus c(u,t−3), c(u,t−2), c(u,t−1), c(u,t) berechnen; echte Nullen bleiben enthalten.
5. Folgeziel c(u,t+1) innerhalb derselben sortierten Nutzergruppe zuordnen (gruppenbezogene Verschiebung um eine Position).
6. Nur Zeitpunkte mit vier bekannten Historienwochen und beobachteter Folgewoche auswählen.
7. Jede der 2.200 Ergebniszeilen unabhängig über Datumsadressen gegen die Wochenquelle prüfen; keine Zukunft in X und keine Nutzervermischung.
8. Erst nach Prüfungen deterministisch exportieren, erneut laden und vollständig validieren. Bestehende abweichende Ausgabe wird nicht überschrieben.

Für c(u,t) = Aktivitätszahl von Nutzer u in Woche t:

- `activities_current_week = c(u,t)` – Eingang.
- `avg_activities_last_4_weeks = [c(u,t−3)+c(u,t−2)+c(u,t−1)+c(u,t)]/4` – Eingang.
- `activities_next_week = c(u,t+1)` – ausschließlich Zielvariable.

Prognosezeitpunkt ist nach vollständigem Abschluss von Woche t. Nur dann sind die vier Eingabewochen bekannt. Zielwerte sind beobachtete spätere Aktivitätszahlen, keine erzeugten Prognosen. Explizite X-Positivliste im Skript enthält genau die zwei Eingänge, nie Ziel/ID/Datumsfelder.

## Tatsächliches Ergebnis und Validierung

Ergebnis: `data/processed/regression_weekly_features.csv` mit 2.200 Datenzeilen × sieben Spalten, sortiert nach user_id und week_index. Die vollständige Wochentabelle bleibt mit allen 2.600 Zeilen unverändert.

| Prüfung | Tatsächliches Ergebnis |
| --- | --- |
| Nutzer / Modellierungszeilen pro Nutzer | 100 / exakt 22 |
| Zeilen / Spalten | 2.200 / sieben in vorgegebener Reihenfolge |
| Eindeutige Nutzer-Wochen-Schlüssel / doppelte Schlüssel | 2.200 / 0 |
| Verwendbare Eingabewochen | ausschließlich 4–25 |
| Zielwochen | ausschließlich 5–26, jeweils derselbe Nutzer in t+1 |
| Nicht als Eingabe exportierte frühe Wochen | 300 Zeilen, Wochen 1–3; bleiben als Historie nutzbar |
| Nicht als Eingabe exportierte letzte Wochen | 100 Zeilen, Woche 26; bleiben als Zielwoche nutzbar |
| Fehlende / nicht endliche / negative Modellwerte | keine |
| Aktuelle Counts / Zielwerte | nicht negative Integer, jeweils exakt aus Wochenquelle |
| Vierwochenfenster | für alle 2.200 Zeilen ausschließlich t−3 bis t geprüft |
| Nutzergrenzen / fehlende Wochen | keine Vermischung und keine Lücken |
| Nullwochen im Grundraster | weiterhin 558 |
| Modellierungszeilen mit aktueller Nullwoche | 478 |
| Modellierungszeilen mit Zielwert 0 | 474 |
| Modellierungszeilen mit mindestens einer Nullwoche im Vierwochenfenster | 1.100 |
| Rücklesen des CSV | Spalten, Typen und alle Werte identisch |
| Zwei tatsächliche Skriptläufe | bytegleiche CSV und identische Prüfberichte |
| Eingabeintegrität | Wochenquelle und alle vier V2-Hashes unverändert |

558 ist die Nullwochenzahl des vollständigen Grundrasters, kein Sollwert der gefilterten 2.200 Zeilen. Keine Nullwochen wegen ihres Werts entfernt; Ausschlüsse erfolgen ausschließlich aufgrund fehlender Historie bzw. unbeobachteten Folgeziels am Rand.

Numerische Vergleichstoleranz: absolut und relativ 1e−10. Integercounts und deren Division durch 4 ergeben hier exakt darstellbare Viertelschritte; unabhängige Referenz verwendet zusätzlich Decimal. Alle 2.200 Zeilen per datumsbasiertem Join statt positionsbasiertem Fenster nachgeprüft.

## Technische Tests und Leakage-Nachweis

Versioniertes Testskript: `tests/test_data_preparation_regression.py`. Ausgeführt mit `python -m unittest discover -s tests -p 'test_data_preparation_regression.py' -v`; alle sieben Tests bestanden:

1. Unabhängiger datumsbasierter Referenzvergleich sämtlicher 2.200 Zeilen.
2. Kausalitätstest: echte Woche U001/5 nur in einer Speicherkopie geändert. Eingänge sämtlicher früherer Zeitpunkte und anderer Nutzer bleiben unverändert; das Ziel ändert sich ausschließlich in U001/4. Spätere Eingänge dürfen die dann bekannte Woche regulär verwenden.
3. Absichtlich falsches Fenster mit t+1 statt t−3 erzeugt; Validator erkennt die Zukunftsinformation und lehnt ab.
4. Fehlende Historienwoche und doppelte Woche führen zum Abbruch ohne künstliche Auffüllung.
5. Echter U001-Nullwochenfall sowie erste/letzte verwendbare Eingabewoche für alle Nutzer geprüft.
6. Drei Nutzer (U001, U045, U100) jeweils an Wochen 4, 13, 21 und 25 unabhängig geprüft, einschließlich Monatsgrenzen März/April und Mai/Juni sowie letzter beobachteter Zielwoche. Umgekehrte Quellreihenfolge liefert dasselbe Ergebnis nach Sortierung.
7. Falsches Folgeziel sowie leere, negative, nicht endliche und nicht ganzzahlige Counts abgelehnt.

Tests verwenden echte V2-Daten; fehlerhafte Varianten und Änderungen ausschließlich isoliert im Speicher, keine neuen synthetischen Forschungsdateien und keine Änderung aktiver Quellen. Diese technischen Tests sind keine fachliche CRISP-DM-Iteration.

## Drei tatsächliche V2-Vorher-Nachher-Beispiele

### A – vier aufeinanderfolgende Wochen – U045, Eingabewoche 13

VORHER (tatsächliche Wochen aus V2):

| Nutzer | Woche | Wochenbeginn | Wochenende | Aktivitäten |
| --- | --- | --- | --- | --- |
| U045 | 10 | 2026-03-09 | 2026-03-15 | 6 |
| U045 | 11 | 2026-03-16 | 2026-03-22 | 9 |
| U045 | 12 | 2026-03-23 | 2026-03-29 | 6 |
| U045 | 13 | 2026-03-30 | 2026-04-05 | 6 |
| U045 | 14 | 2026-04-06 | 2026-04-12 | 8 |

VERARBEITUNG: Eingangsfenster [6, 9, 6, 6], Summe 27 / 4 = 6.75; aktueller Wert 6. Ziel separat aus Woche 14: 8.

NACHHER:

```json
{
  "user_id": "U045",
  "week_index": "13",
  "week_start": "2026-03-30",
  "week_end": "2026-04-05",
  "activities_current_week": "6",
  "avg_activities_last_4_weeks": "6.75",
  "activities_next_week": "8"
}
```

Fachliche Begründung: Das Vierwochenmittel beschreibt das zuletzt beobachtete Niveau aus vier vollständig abgeschlossenen Wochen, ohne Zukunftsinformation.

### B – aktuelle Woche und beobachtetes Folgeziel – U100, Eingabewoche 25

VORHER (tatsächliche Wochen aus V2):

| Nutzer | Woche | Wochenbeginn | Wochenende | Aktivitäten |
| --- | --- | --- | --- | --- |
| U100 | 22 | 2026-06-01 | 2026-06-07 | 6 |
| U100 | 23 | 2026-06-08 | 2026-06-14 | 5 |
| U100 | 24 | 2026-06-15 | 2026-06-21 | 4 |
| U100 | 25 | 2026-06-22 | 2026-06-28 | 6 |
| U100 | 26 | 2026-06-29 | 2026-07-05 | 3 |

VERARBEITUNG: Eingangsfenster [6, 5, 4, 6], Summe 21 / 4 = 5.25; aktueller Wert 6. Ziel separat aus Woche 26: 3.

NACHHER:

```json
{
  "user_id": "U100",
  "week_index": "25",
  "week_start": "2026-06-22",
  "week_end": "2026-06-28",
  "activities_current_week": "6",
  "avg_activities_last_4_weeks": "5.25",
  "activities_next_week": "3"
}
```

Fachliche Begründung: Woche 25 ist der letzte verwendbare Eingabezeitpunkt. Woche 26 bleibt als beobachtetes Ziel nutzbar; eine Woche 27 wird nicht erfunden.

### C – echte Nullwoche im Vierwochenfenster – U001, Eingabewoche 4

VORHER (tatsächliche Wochen aus V2):

| Nutzer | Woche | Wochenbeginn | Wochenende | Aktivitäten |
| --- | --- | --- | --- | --- |
| U001 | 1 | 2026-01-05 | 2026-01-11 | 0 |
| U001 | 2 | 2026-01-12 | 2026-01-18 | 0 |
| U001 | 3 | 2026-01-19 | 2026-01-25 | 2 |
| U001 | 4 | 2026-01-26 | 2026-02-01 | 0 |
| U001 | 5 | 2026-02-02 | 2026-02-08 | 1 |

VERARBEITUNG: Eingangsfenster [0, 0, 2, 0], Summe 2 / 4 = 0.5; aktueller Wert 0. Ziel separat aus Woche 5: 1.

NACHHER:

```json
{
  "user_id": "U001",
  "week_index": "4",
  "week_start": "2026-01-26",
  "week_end": "2026-02-01",
  "activities_current_week": "0",
  "avg_activities_last_4_weeks": "0.5",
  "activities_next_week": "1"
}
```

Fachliche Begründung: Die drei echten Nullen in [0,0,2,0] gehören in den Nenner 4. Der Mittelwert ist 0,5; nur aktive Wochen zu mitteln wäre fachlich falsch.

## Reproduzierbarkeit, Metadaten und Übergabe

Aufruf: `python src/data_preparation_regression.py`. Python 3.12.14, nur Standardbibliothek. UTF-8/LF, Komma, Dezimalpunkt, keine Indexspalte; feste Spaltenfolge und Sortierung. SHA-256 der Ausgabe: `4fc681eaa1a042a1b44cf6bc742a27f3277eafb7a9c54f5ff78736d998b70914`.

`user_id` identifiziert; `week_index`, `week_start` und `week_end` sind zeitliche Metadaten für Nachvollziehbarkeit/Visualisierung, keine Modelleingänge. Datumspaare bezeichnen die aktuelle Eingabewoche, nicht die Zielwoche. Der Zielwochenbeginn ist eindeutig week_start + 7 Tage und intern geprüft. Noch keine Splitspalte oder separate Train/Test-Dateien.

Alle zuvor vorhandenen Projektdateien wurden per Hashvergleich geprüft: vor Dokumentationsergänzung keine Veränderungen; anschließend ausschließlich der autorisierte Ausführungsnachweis und das Datenwörterbuch ergänzt. Keine Datenfehler oder zeitlichen Abweichungen festgestellt, kein Anlass für eine neue CRISP-DM-Iteration. Keine Prognosen, Modellgüte, Modelle oder Clusterlabels erzeugt; kein Commit und kein Pull Request. AP 4.6 kann den geplanten chronologischen Split umsetzen; dieser ist in AP 4.5 ausdrücklich noch nicht erstellt.


# AP 4.6 – tatsächlich erstellter chronologischer Regressionssplit

Stand: 31.10.2026. CRISP-DM 3.5 Format Data und 4.2 Generate Test Design. Worktree `/workspace/MOVA-AP4`, Branch `ap4-data-preparation`, Quellbasis `ed52949cb8b688bc64c0793be0e407950314769e`; weiterhin kein Commit. Frühere Abschnitte beschreiben jeweils den damaligen Stand; die Aufteilung wurde erst in AP 4.6 erstellt.

## Ziel, Grundlage und tatsächlich ausgeführte Verarbeitung

Eingabe: aktive V2 in `data/processed/regression_weekly_features.csv`, 2.200 Zeilen, 100 Nutzer mit 22 Zeitpunkten, sieben Spalten. Eingabe-SHA-256 `4fc681eaa1a042a1b44cf6bc742a27f3277eafb7a9c54f5ff78736d998b70914`. Vorhandenes Regressionskonzept, Vorbereitungsplan, Ausführungsnachweis und Datenwörterbuch gelesen; bestehende Merkmalsdefinitionen unverändert übernommen.

1. Quelle laden; V2-Manifest und vier Roh-/Kontrollhashes, Quellenhash und dokumentierten Hash der vorhandenen Wochentabelle prüfen.
2. Schema, Pflichtwerte, endliche nicht negative Modellwerte, Integerziele, vollständige Nutzer-Wochen-Schlüssel und Kalender prüfen. Zusätzlich alle vorhandenen X/y-Zeilen gegen die unveränderte Wochentabelle validieren, einschließlich Fenster t−3 bis t und Ziel t+1. Keine neuen Merkmale/Zeilenwerte erzeugen.
3. Feste Eingabewochen definieren, Aufteilung ausschließlich anhand week_index. Anders als der historische Plantext wird kein zusätzliches target_week_start-Feld für die Auswahl benötigt; die äquivalente Zielwoche ist stets t+1 und wird unabhängig geprüft.
4. Training aus t=4–21 auswählen, nach user_id und week_index sortieren.
5. Test aus t=22–25 auswählen, identisch sortieren.
6. Disjunkte Schlüssel/Zielwochen, vollständige unveränderte Rekonstruktion der Ausgangstabelle und Nutzerverteilungen validieren.
7. Erst nach allen Prüfungen zwei CSVs und ein deterministisches Split-Manifest speichern; erneut laden und prüfen. Abweichende bestehende Ausgaben niemals überschreiben.

Chronologische Trennung entspricht einer späteren Vorhersage zukünftiger Wochen bereits bekannter Nutzer. Zufälliges Mischen würde spätere Ziele für die Beurteilung früherer Prognosezeitpunkte verfügbar machen und passt nicht zu dieser Aufgabe. Kein Test auf völlig neuen Nutzern und keine Behauptung unabhängiger Modellierungszeilen.

## Tatsächliche Ergebnisse und Zeitgrenzen

| Größe | Training | Test |
| --- | --- | --- |
| Datei | data/processed/regression_train.csv | data/processed/regression_test.csv |
| Zeilen × Spalten | 1.800 × sieben | 400 × sieben |
| Nutzer | alle 100 | alle 100 |
| Zeilen je Nutzer | genau 18 | genau vier |
| Eingabewochen | 4–21 | 22–25 |
| Eingabezeitraum einschließlich Wochenenden | 26.01.–31.05.2026 | 01.06.–28.06.2026 |
| Zielwochen | 5–22 | 23–26 |
| Zielzeitraum einschließlich Wochenenden | 02.02.–07.06.2026 | 08.06.–05.07.2026 |

Insgesamt 2.200 Zeilen, Aufteilung 81,82 % / 18,18 % (ganze gemeinsame Wochenblöcke). Keine verlorenen Nutzer oder Beobachtungen. Alle sieben ursprünglichen Spalten in ursprünglicher Reihenfolge; keine zusätzliche Splitspalte und keine neuen Modellmerkmale.

| Validierung | Tatsächliches Ergebnis |
| --- | --- |
| Nutzer- und Zeilenzahlen, Wochen je Nutzer | vollständig wie oben |
| Fehlende / doppelte Schlüssel | keine |
| Identische Schlüssel in Training/Test | keine |
| Überlappende Prognose-Zielwochen | keine; max. Trainingsziel 22 < min. Testziel 23 |
| Kalender-Zielgrenze | Training endet 07.06.2026, Test beginnt 08.06.2026 |
| Fehlende / unendliche / negative Modellwerte | keine |
| Zielwerte | alle nicht negative Integer, unverändert übernommen |
| Zeitliche Merkmalsverfügbarkeit | jede Zeile gegen Wochenquelle geprüft: X ausschließlich t−3…t, y exakt t+1 desselben Nutzers |
| Vierwochenmittelwerte und alle anderen Quellwerte | unverändert, inklusive originaler CSV-Zahlendarstellung |
| Rekonstruktion | Training + Test ergeben sortiert exakt alle 2.200 ursprünglichen Zeilen |
| Sortierung / Eingabereihenfolge | eindeutig; umgekehrte und deterministisch gemischte Quelle liefern denselben Split |
| Reproduzierbarkeit | zwei echte Skriptläufe; beide CSVs und Manifest jeweils bytegleich |
| Eingabedateien | unverändert; alle vorher vorhandenen Daten/Skripte/Berichte/Tests per Hash geprüft |

## Modellierungsrollen und rollierende Einwochenprognosen

X ausschließlich `activities_current_week` und `avg_activities_last_4_weeks`. y ausschließlich `activities_next_week`, niemals ein Eingang. `user_id`, `week_index`, `week_start`, `week_end` sind Zuordnung/Visualisierung und nicht X.

Beim ersten Testzeitpunkt nach Abschluss von Woche 22 sind Wochen 19–22 als Historie bekannt; Ziel ist Woche 23. Nach Abschluss von Woche 23 darf deren tatsächlich beobachtete Zahl als aktuelle Eingabe für das Ziel Woche 24 genutzt werden. Ein in der Testphase festgehaltenes späteres Modell darf diese neuen Beobachtungen entgegennehmen, aber nicht auf Testzielen nachtrainiert oder anhand des finalen Tests optimiert werden.

Überlappende historische Eingabewochen sind deshalb zulässig. Auch das letzte Trainingsziel (Woche 22) ist am ersten Testprognosezeitpunkt als Beobachtung abgeschlossen. Unzulässig wäre, Woche 23 bereits für die Prognose von Woche 23 in X aufzunehmen. Es handelt sich nicht um eine gleichzeitige Vierwochenprognose am Ende von Woche 22. Hier wurden ausschließlich Daten aufgeteilt, keinerlei Prognosen oder Modelle erzeugt.

## Automatisierte technische Tests

Neu: `tests/test_data_preparation_split.py`, sieben Tests. Ausführung `python -m unittest discover -s tests -v`: alle 14 Tests bestanden, einschließlich der sieben vorhandenen AP-4.5-Tests.

Neue Prüfungen: vollständige wertgleiche Partition/Nutzerzahlen; zufällig umgeordnete und umgekehrte Eingabe (nur Reihenfolge, keine Datengenerierung); bewusst falsche Grenzen, überlappende und lückenhafte Regeln abgelehnt; echte Zielkalendergrenze; fehlende/doppelte/geänderte Zeilen abgelehnt; ungültige Ziele/NaN/Inf/falsches Datum abgelehnt; Rollen und echte rollierende Testhistorie geprüft. Die vorhandenen AP-4.5-Tests prüfen weiterhin die gezielte Zukunftsänderung und ein absichtlich mit t+1 kontaminiertes Fenster. Fehlerfälle ausschließlich in Speicherkopien, keine Änderungen an V2.

## Drei tatsächliche V2-Vorher-Nachher-Beispiele: U001

Die folgenden unveränderten Zeilen stammen aus der V2-Regressionstabelle. Der Split ändert nur ihre Dateizuordnung.

### A – letzte Trainingsbeobachtung

VORHER: tatsächliche Quellzeile:

```json
{
  "user_id": "U001",
  "week_index": "21",
  "week_start": "2026-05-25",
  "week_end": "2026-05-31",
  "activities_current_week": "3",
  "avg_activities_last_4_weeks": "2.0",
  "activities_next_week": "1"
}
```

VERARBEITUNG: week_index=21 anhand fester Regel → Training. Bekannte Historie Wochen 18–21: [0, 3, 2, 3]; Mittel 2.0. Zielwoche 22 (2026-06-01 bis 2026-06-07) enthält tatsächlich 1 Aktivitäten.

NACHHER: Dieselbe siebenfeldrige Zeile unverändert in `data/processed/regression_train.csv`.

Fachliche Begründung: Eingabewoche 21 verwendet ausschließlich Wochen 18–21. Zielwoche 22 ist die letzte Trainings-Zielwoche.

### B – erste Testbeobachtung

VORHER: tatsächliche Quellzeile:

```json
{
  "user_id": "U001",
  "week_index": "22",
  "week_start": "2026-06-01",
  "week_end": "2026-06-07",
  "activities_current_week": "1",
  "avg_activities_last_4_weeks": "2.25",
  "activities_next_week": "2"
}
```

VERARBEITUNG: week_index=22 anhand fester Regel → Test. Bekannte Historie Wochen 19–22: [3, 2, 3, 1]; Mittel 2.25. Zielwoche 23 (2026-06-08 bis 2026-06-14) enthält tatsächlich 2 Aktivitäten.

NACHHER: Dieselbe siebenfeldrige Zeile unverändert in `data/processed/regression_test.csv`.

Fachliche Begründung: Historie Wochen 19–22 ist nach Abschluss von Woche 22 bekannt. Zielwoche 23 liegt vollständig nach sämtlichen Trainings-Zielwochen.

### C – spätere Testbeobachtung mit abgeschlossener Testwoche

VORHER: tatsächliche Quellzeile:

```json
{
  "user_id": "U001",
  "week_index": "23",
  "week_start": "2026-06-08",
  "week_end": "2026-06-14",
  "activities_current_week": "2",
  "avg_activities_last_4_weeks": "2.0",
  "activities_next_week": "4"
}
```

VERARBEITUNG: week_index=23 anhand fester Regel → Test. Bekannte Historie Wochen 20–23: [2, 3, 1, 2]; Mittel 2.0. Zielwoche 24 (2026-06-15 bis 2026-06-21) enthält tatsächlich 4 Aktivitäten.

NACHHER: Dieselbe siebenfeldrige Zeile unverändert in `data/processed/regression_test.csv`.

Fachliche Begründung: Die beobachtete Woche 23 war Ziel der ersten Testbeobachtung und ist zum neuen Prognosezeitpunkt abgeschlossen. Sie darf für das Ziel Woche 24 als aktueller Eingang und Teil des Mittels aus Wochen 20–23 dienen. Kein Data Leakage: Woche 24 gelangt nicht in die Eingänge. Das spätere Modell bleibt während der Testphase unverändert.

## Reproduktion, Manifest und Übergabe

Aufruf: `python src/data_preparation_split.py`. Python 3.12.14, nur Standardbibliothek. CSV UTF-8/LF, Komma, Dezimalpunkt, kein Index. Manifest: `documentation/regression_split_manifest.json`; V2, Quellhash, feste Wochenregeln/Zielzeiträume, Zeilen-/Nutzerzahlen, exakte X/y-/Metadatenrollen, rollierendes Prognoseprotokoll und Ausgabehashes gespeichert. JSON deterministisch ohne Zeitstempel.

- `data/processed/regression_train.csv`: SHA-256 `e984a547de12aca7d53ce908dd5051992bbd21aa83895a67bcd6fc0b541fb0b8`
- `data/processed/regression_test.csv`: SHA-256 `b0c11c94209323c01f098042261349a3ed506c408af5303a4ac9d5e84715c1fa`
- `documentation/regression_split_manifest.json`: SHA-256 `536137414d579a30fef9fb946ac04e114fac50ffaff6462861fdb69cc984caff`

Keine Auffälligkeiten oder Kontrollabweichungen. Kein Anlass für eine neue CRISP-DM-Iteration. Außer den autorisierten Dokumentationsfortschreibungen keine bestehenden Projektdateien verändert. Keine Modelle, Prognosen, MAE, Baselinebewertung oder Clusterlabels. Kein Commit und kein Pull Request. AP 4.7 kann auf den geprüften Artefakten fortgesetzt werden.


# AP 4.7 – unabhängiges Gesamtaudit und wissenschaftliche Visualisierung

Stand: 31.10.2026. CRISP-DM 3.5 Format Data / Qualitätssicherung der gesamten Data Preparation. Ausschließlich Worktree `/workspace/MOVA-AP4`, Branch `ap4-data-preparation`, Quellbasis `ed52949cb8b688bc64c0793be0e407950314769e`. Kein Commit und kein Pull Request.

## Ziel und Unabhängigkeit

Alle bestehenden AP-4.1–AP-4.6-Ergebnisse anhand der tatsächlichen Dateien erneut prüfen und für die Hochschulpräsentation visualisieren. Neues Skript `src/data_preparation_audit.py`: keine Imports aus bestehenden Transformationsskripten und keine Übernahme früherer Prüfberichte als Beweis. Quellen werden neu geladen; Kontrollwerte im Speicher aus echten V2-Daten rekonstruiert. Keine bestehenden Daten oder Transformationsskripte verändert.

## Tatsächlich ausgeführte Kontrollen und Ergebnisse

Zehn CSVs einschließlich Rohaktivitäten/Nutzerliste, aller sieben vorbereiteten Tabellen und vorhandener Wochenkontrolle geprüft; zusätzlich drei JSON-Dateien (aktive Version, Skalierungsparameter, Split-Manifest). Die Angebotsdatei wird als vierte V2-Manifestquelle ausschließlich per Hash geprüft. Der Auditbericht führt alle 14 tatsächlich geprüften Dateien mit SHA-256 auf.

- 6.465 Rohaktivitäten und 6.465 ausgewählte Aktivitäten; alle ausgewählten Werte exakt identisch. Rohpflichtwerte, IDs, Sportarten, Datum, Dauer-/Distanzplausibilität und strukturell nicht anwendbare Distanzen unabhängig überprüft.
- 100 eindeutige bekannte Nutzer in allen relevanten Tabellen. Vollständiges Wochenraster aus 100×26 eindeutigen Nutzerwochen geprüft. Wochenzuordnung, jede Aktivitätszahl und jede Minutensumme direkt aus Rohaktivitäten neu nachgerechnet; 2.042 belegte Gruppen und 558 ergänzte Nullwochen. Alle 2.600 Counts stimmen mit der separaten Wochenkontrolle überein.
- 422.829,9 Minuten auf Roh-, Auswahl- und Wochenebene exakt mit Decimal erhalten; Nutzerwochenmittel rekonstruieren die ursprünglichen Nutzer- und Gesamtsummen innerhalb Toleranz.
- 100 unskalierte und 100 skalierte K-Means-Profile, exakt neun Eingänge. Alle acht Sportanteile und beide Interpretationsmerkmale unabhängig per Nutzer/Sport nachgerechnet. Anteilssummen 1 und keine Interpretationsspalten in skalierter Matrix.
- Gespeicherte StandardScaler-Mittelwerte, Varianzen, Standardabweichungen, scale_ und Gewichtungsfaktoren gegen eigene Populationsstatistiken geprüft. JSON reproduziert alle 100×9 skalierten Werte; inverse Transformation und Blockvarianzsummen ≈1 bestanden. Alle neun Eingänge variieren tatsächlich.
- Alle 2.200 Regressionszeilen mit eigener Nutzer-/Wochenadressierung geprüft: Fenster ausschließlich t−3…t, Ziel t+1, keine Nutzervermischung oder künstliche Historie. 478 aktuelle Nullwochen, 474 Nullziele und 1.100 Zeilen mit mindestens einer Null im Fenster bestätigt.
- 1.800 Training / 400 Test, je Nutzer 18 / vier Zeilen; alle ursprünglichen Zeilen und Werte vollständig erhalten. Eingabewochen 4–21 / 22–25, disjunkte Zielwochen 5–22 / 23–26. Manifestregeln, Rollen, Kalenderzielgrenzen und Ausgabewerte geprüft.
- Vier V2-Manifest-Prüfsummen und dokumentierte Provenienzhashes stimmen. Alle vor AP 4.7 vorhandenen Projektdateien vor Dokumentationsergänzung bytegleich geprüft; anschließend ausschließlich dieser autorisierte Ausführungsnachweis ergänzt.

Keine Datenfehler oder Kontrollabweichungen festgestellt. Die sieben unabhängigen Prüfgruppen umfassen zahlreiche Einzelprüfungen; numerische Toleranz atol=rtol=1e−10. Regressionsfenster enthalten wiederholte Aktivitäten über die Zeit und Rand-Ausschlüsse: ihre Werte dürfen nicht als neue Aktivitäts-Gesamtsumme addiert und mit 6.465 gleichgesetzt werden.

## Tatsächlich berechneter Effekt der Nullwochen

Gepoolter Mittelwert über das vollständige Raster: **6.465/2.600 = 2,48653846 Aktivitäten je Nutzerwoche**. Ohne die 558 Nullwochen: **6.465/2.042 = 3,16601371**. Würde der zweite Wert als Durchschnitt über den gesamten Beobachtungszeitraum berichtet, wäre das eine tatsächliche Überschätzung um **27,3262 %**. Formel: ((6.465/2.042)/(6.465/2.600)−1)×100. Die Nullwochen machen 21,4615 % des Rasters aus.

Dies ist ein gepoolter Nutzerwochenvergleich, keine Modellgüte und keine geschätzte kausale Wirkung. Der Mittelwert nur aktiver Wochen ist für die bedingte Fragestellung „wie viele Aktivitäten in aktiven Wochen?“ korrekt; er beschreibt jedoch nicht die vollständigen 26 Beobachtungswochen. Ohne Nullwochen unterscheiden sich die Nutzergewichte.

## Vier tatsächlich erzeugte und visuell geprüfte Abbildungen

1. `outputs/figures/data_preparation_pipeline.png`: Datenfluss mit tatsächlichen Zeilenzahlen und klar unterschiedenen Einheiten. Nutzer-/Sportmerkmale kommen aus Einzelaktivitäten, vollständige Nutzerliste führt Integration an; Wochenwerte liefern Summenabgleich. Boxgrößen kodieren keine vergleichbaren Stichprobengrößen.
2. `outputs/figures/data_preparation_zero_weeks.png`: 2.042 aktive + 558 Nullwochen = 2.600; daneben exakt berechneter Häufigkeitsvergleich mit/ohne Nullwochen.
3. `outputs/figures/data_preparation_scaling.png`: Tatsächliche Verteilungen von Wochenhäufigkeit und Running-Anteil über 100 Nutzer, jeweils roh, standardisiert und nach Gewichtung. Getrennte x-Skalen, keine Vermischung unterschiedlicher Einheiten. Negative z-Werte ausdrücklich als erwartbar erklärt.
4. `outputs/figures/data_preparation_train_test_split.png`: Wochen 1–26, Eingabe- und Zielzeiträume getrennt. Frühe Historie und fehlende Zukunft am Beobachtungsende erklärt; rollierende Einwochenprognose mit später unverändertem Modell gekennzeichnet.

Vollständiger Bericht: `outputs/tables/data_preparation_audit_report.md`. Keine bisherigen Qualitätsberichte überschrieben.

## Geprüfte Begründungen A–I: Befund oder fachliche Annahme?

| Entscheidung | Begründung und Status |
| --- | --- |
| A: distance_km ausschließen | Für die ersten festgelegten Modelle nicht benötigt; Sportartenübergreifende Distanz schwer vergleichbar. 1.698 strukturelle Leerfelder bei Strength/Tennis/Padel tatsächlich geprüft. Ausschluss aus X ist eine fachliche Designentscheidung; Rohwerte unverändert erhalten. |
| B: 558 Nullwochen ergänzen | Tatsächlich fehlende Aktivitätsgruppen im vollständigen bestätigten Nutzerraster. Vollständige 26-Wochen-Zeitreihen erhalten; der gepoolte Nenner-Effekt wurde hier tatsächlich nachgerechnet. Bei realen Daten müsste Aufzeichnungsvollständigkeit erst belegt sein. |
| C: week_end hinzufügen | Sonntag = Montag + sechs Tage tatsächlich geprüft. Macht vollständige Intervalle für Zuordnung/Visualisierung verständlich, ohne zusätzlicher Modelleingang zu sein. Fachliche Darstellungsentscheidung. |
| D: neun K-Means-Eingänge | Ein Maß des Aktivitätsniveaus und acht vollständige Sportkoordinaten. Gleicher Umgang mit allen Sportarten; keine willkürliche Kategorie entfernen. Fachliches Basiskonzept, keine empirisch optimierte Merkmalsauswahl. Acht Anteile enthalten nur sieben unabhängige Freiheitsgrade. |
| E: Umfang/Vielfalt nur Interpretation | Umfang überschneidet sich stark mit Häufigkeit, Vielfalt ist aus positiven Sportcounts ableitbar und hängt von Beobachtungsmenge ab. Bereits deskriptiv im AP-3-Konzept untersucht; keine erneuten Modelltests hier. Ausschluss vermeidet zunächst eine zusätzliche Gewichtung dieser Aspekte und ist eine Designentscheidung. |
| F: Faktor 1/√8 | Tatsächlich nachgewiesen: je Sportkoordinate Varianz ≈1/8, Blocksumme ≈1 wie Häufigkeitsblock. Gleiche Streuungsgewichtung ist eine transparente Startannahme, keine nachgewiesen optimale fachliche Wirkung. |
| G: frühe/letzte Eingabewochen ausschließen | Tatsächlicher Datenvertrag: Wochen 1–3 haben noch keine vollständige Vierwochenhistorie, Woche 26 keine beobachtete Folgewoche 27. 300 + 100 Eingabezeilen ausgeschlossen, Quellen vollständig erhalten. |
| H: chronologischer Split | Passt zur Vorhersage künftiger Wochen bekannter Nutzer. Tatsächlich disjunkte Zielzeiträume geprüft; zufällige Aufteilung würde diese zeitliche Aufgabe nicht abbilden. Methodische Designentscheidung. |
| I: bekannte frühere Testwochen nutzen | Zum jeweiligen Prognosezeitpunkt bereits abgeschlossene Wochen sind beobachtbare Eingänge. Tatsächlich nur t−3…t verwendet. Kein t+1 in X; ein späteres Modell bleibt in der Testphase unverändert. Gilt für rollierende Einwochenprognosen, nicht für gleichzeitige Mehrwochenprognosen ab einem Stichtag. |

## Technische Tests und Reproduzierbarkeit

Neu: `tests/test_data_preparation_audit.py`, acht Tests: unveränderte V2, manipulierte Gesamtsumme, entfernte Nullwoche, falsche Splitgrenze bei unveränderten Zeilenzahlen, unzulässiges Interpretationsmerkmal in skalierter Tabelle, Zukunft im Mittelwert, falscher Gewichtungsparameter und falsche Manifest-Zielgrenze. Änderungen nur an Speicherkopien. Dadurch werden Inhaltsfehler tatsächlich erkannt, statt allein auf alte Hashes/Prüfberichte zu vertrauen.

`python -m unittest discover -s tests -v`: **22 Tests bestanden** (acht neue Audit-Tests plus 14 bestehende Zeit-/Splittests). `python src/data_preparation_audit.py` nach Abschluss aller Änderungen zweimal tatsächlich ausgeführt. Der vollständige neue Bericht und alle vier PNGs waren **bytegleich**; zusätzlich identische JSON-Konsolenberichte. Keine abweichenden PNG-Metadaten, visuelle Reproduzierbarkeit daher durch Bytevergleich mit abgedeckt. Alle vier Abbildungen außerdem visuell auf Beschriftung und Einheiten geprüft. Konstante Metadaten und deterministische Renderparameter; andere Bibliotheks-/Schriftversionen können abweichen.

Python 3.12.14, pandas 2.2.3, NumPy 2.3.5, Matplotlib 3.10.8. Schrift-/Renderingcache liegt unter work, keine Projekt-Rohdaten werden geändert.

## Einschränkungen und Übergabe

100 synthetische Nutzer, 26 Wochen, wiederholte Nutzer und überlappende Fenster. Noch keine Modellgüte untersucht. K-Means-Gewichtung nicht empirisch optimiert; keine Aussage zur Generalisierbarkeit auf echte Garmin-Nutzer. Ein bestandener Datenqualitätscheck ist kein Nachweis guter Modellgüte. Historische fachliche Auffälligkeiten aus AP 3 bleiben erhalten, werden nicht automatisch bereinigt.

Kein Anlass für eine neue CRISP-DM-Iteration; keine behauptet. Keine neuen Modellierungsmerkmale, Daten, Transformationen oder Modelle erzeugt; hier neu berechnete Aggregate sind ausschließlich Audit-Kontrollwerte im Speicher. Keine Clusterlabels, Prognosen, MAE oder Baselinebewertung. Bestehende Transformationsskripte und Daten unverändert, kein Commit oder Pull Request. AP 4.8 kann auf dieser intern konsistenten und reproduzierbar auditierten Datenbasis fortgesetzt werden.

### SHA-256 der neuen Audit-Ausgaben

- `outputs/tables/data_preparation_audit_report.md`: `db68d2d752924085c6dc9d96f1feb677bd45df8cbd730a2e8e8eb010887b49d4`
- `outputs/figures/data_preparation_pipeline.png`: `cbcd981a3f5333a7dfd9c7bc8e164b04567d619d6cb6fa599eea2fa26a93bf92`
- `outputs/figures/data_preparation_scaling.png`: `225d88e85eb64b337e0a8e54f5a3a0f252a0ec32dfc54f6c31e29a76e7f75570`
- `outputs/figures/data_preparation_train_test_split.png`: `52a8b0ace11ab5acf4b5a65f081e8bf4986795852a9cd0d35f89c5b08ae2d3c0`
- `outputs/figures/data_preparation_zero_weeks.png`: `8ce58d210aa0240e60293673b8463c0057b054e5ee7052e63374fbccf9a5af5d`
