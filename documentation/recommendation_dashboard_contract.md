# MOVA – Dashboard-Vertrag der Empfehlungsengine (AP 6.3d)

Stand: 31.10.2026. Technisch abgenommen für den lokalen synthetischen V2-Demonstrator.
Keine produktive Garmin-Anbindung, reale Einwilligung oder UI implementiert.

## 1. Tatsächlich vorhandene Python-Schnittstelle

```python
from datetime import date
from recommendation_engine import run

result = run(
    'U001',
    interests_permission=True,
    garmin_permission=True,
    as_of=date(2026, 7, 5),
)
```

Das Modul liegt in `src/` (beispielsweise `PYTHONPATH=src` setzen).
`run` lädt die Daten und ruft `recommend_user` auf. Alternativ existiert
`recommend_user(data, user_id, *, interests_permission, garmin_permission,
as_of=PROFILE_END)` für bereits geladenes `ProjectData`. Für eine erste
Dashboard-Anbindung ist `run` der einfachere freigabeprüfende Einstieg.
Die reinen Matching-Funktionen sind keine eigenständige Berechtigungsgrenze.

| Eingabe | Typ / tatsächliches Verhalten |
| --- | --- |
| user_id | Text; muss in den vorhandenen Nutzerkennungen existieren |
| interests_permission | Pflichtargument, exakt Python bool; kein True-Default |
| garmin_permission | Pflichtargument, exakt Python bool; kein True-Default |
| as_of | optional, exakt datetime.date (kein datetime/String); Default 2026-07-05 |
| root | optional bei run; pathlib.Path-kompatibler Projektpfad, Default Modul-Projektwurzel |

Die beiden Freigaben sind unabhängig übergebene **Simulationsparameter**. Nicht aus
Interessen oder vorhandenen Datensätzen ableiten und nicht als echte Zustimmung
anzeigen. Die Engine speichert keinen Sitzungszustand. Ein späteres Dashboard muss
sie für den ausgewählten Nutzer explizit übergeben und nach Nutzerwechsel neu
abfragen; ein sicherer Ausgangszustand sind False/False.

## 2. JSON-Ausgabe

`run` liefert ein Dictionary, serialisierbar mit
`json.dumps(result, ensure_ascii=False, allow_nan=False)`. Es enthält keine
Python-Datumsobjekte, NumPy-Werte oder NaN/Infinity. Nullwerte werden JSON null,
leere Listen/Objekte werden []/{}. Keine neue DataFrame-/CSV-Spalte wird behauptet.

| Wurzelfeld | JSON-Typ | Bedeutung |
| --- | --- | --- |
| user_id | string | ausgewählter vorhandener Nutzer |
| as_of | string YYYY-MM-DD | angefragter historischer Cutoff |
| permissions_simulated | object | Interessen-/Garmin-Freigabe als bool plus simulated=true und real_consent_record=false |
| interest_categories | array[string] | alphabetisch sortierte positive Kategorien; bei gesperrten/ungültigen Interessen [] |
| personalization_status | string | Status des Interessen-/Empfehlungswegs |
| profile | object | voneinander getrennter Sport-, Cluster- und Regressionskontext |
| recommendations | array[object] | maximal fünf eindeutig identifizierte Angebote, bereits endgültig geordnet |

`interest_categories` verwendet nur Sport, Outdoor, Wellness, Freizeit. Ein leeres
Array ist mit dem Status zu interpretieren: fehlende Freigabe ist etwas anderes
als keine positiv ausgewählte Kategorie. False belegt kein ausdrückliches Desinteresse.

### Profilfelder

| Feld unter profile | JSON-Typ | Bedeutung |
| --- | --- | --- |
| sport_shares | object[string,number] | acht unskalierte Anteile bei gültiger und erlaubter Historie; sonst {} |
| sport_profile_status | string | Verfügbarkeit des historischen Profils |
| cluster_id | integer oder null | gespeicherte technische ID 0/1, keine neue Zuordnung |
| segment_label | string oder null | Geringere Trainingshäufigkeit / Höhere Trainingshäufigkeit |
| segment_status | string | Verfügbarkeit der gespeicherten Zuordnung |
| segment_source | string | stored_user_clusters bei verfügbarer Zuordnung, sonst not_loaded |
| segment_period_end | string, optional | 2026-07-05; wird nur bei verfügbarem Segment ausgegeben |
| regression_prediction | number oder null | unveränderte neu berechnete Modellschätzung |
| prediction_status | string | Status des separaten Prognosewegs |
| source | string | new_inference_saved_regression_model bei erfolgreicher Inferenz, sonst not_computed |
| input_features | object oder null | activities_current_week und avg_activities_last_4_weeks, numerisch |
| input_week_end | string YYYY-MM-DD oder null | tatsächlich verwendetes abgeschlossenes Wochenende |
| target_week_start | string YYYY-MM-DD oder null | Montag der geschätzten Folgewoche |
| target_week_end | string YYYY-MM-DD oder null | Sonntag der geschätzten Folgewoche |
| limitation | string | Hinweis auf unverbindliche Schätzung und individuelle Fehler |

Sportanteil-Schlüssel: Running, Cycling, Strength, Swimming, Walking, Hiking,
Tennis, Padel. Bei gültigem Profil jeweils [0,1], Summe 1. Das Profil bezieht sich
auf 05.01.–05.07.2026. Die Anteile werden nur zusätzlich ausgegeben, nicht neu
berechnet. Ein Nullanteil ist kein ausdrückliches Desinteresse.

`source` im Profil bezeichnet ausschließlich die Regression; `segment_source`
bezeichnet ausschließlich die gespeicherte Clusterzuordnung. Bei fehlgeschlagener
Regression können gültige Eingabemerkmale/Datumsfelder bereits vorhanden sein;
entscheidend für eine Prognoseanzeige sind prediction_status=available und ein
numerischer regression_prediction-Wert. Keine null-Werte durch 0 ersetzen.

### Empfehlungen

| Feld je recommendations-Eintrag | JSON-Typ |
| --- | --- |
| user_id | string |
| ranking_position | integer, fortlaufend 1–5 |
| offer_id | string |
| offer_title | string, unveränderter fiktiver Katalogtitel |
| category | string |
| price_eur | number, Euro |
| discount_pct | integer, Prozentangabe aus Katalog |
| ranking_tier | string A oder B |
| match_reason | string, bereits formulierte Erklärung |

Preise und Rabatte sind Katalogangaben, keine zusätzlich berechneten Endpreise.
Nicht zur Sortierung im Dashboard verwenden, wenn die abgenommene Engine-Rangfolge
angezeigt werden soll. Kein Match-Score oder Kaufwahrscheinlichkeitsfeld vorhanden.

## 3. Vollständige implementierte Statuswerte

| Kontext | Statuswerte |
| --- | --- |
| personalization_status | available; interests_permission_denied; invalid_or_missing_interests; no_positive_interests |
| sport_profile_status | permission_denied; unverified_activity_data; profile_not_yet_available; missing_profile; inactive; invalid_profile; available |
| segment_status | permission_denied; missing_or_ineligible; available |
| prediction_status | permission_denied; unverified_activity_data; insufficient_history; invalid_history; model_training_after_cutoff; model_unavailable_or_invalid; available |

`available` des Interessenwegs bedeutet validierte positive Kategorien, kein
Nachweis tatsächlicher Empfehlungsrelevanz. Für eine leer bleibende Liste immer
Status und tatsächliche Listengröße anzeigen, keinen Erfolg erfinden.

Ohne Garmin-Freigabe: sport_shares={}, Segment/Cluster-ID/Prognose/Eingabemerkmale
und Datumsfelder null, segment_period_end fehlt; keine persönlichen Aktivitätsdaten
werden geladen oder ausgegeben. Modelllimitation und permission_denied sind
allgemeine Statusinformationen. Kategorienempfehlungen sind mit Interessenfreigabe
weiterhin möglich, ausschließlich Stufe B.

Ohne Interessenfreigabe: interest_categories=[] und recommendations=[];
bei unabhängiger Garmin-Freigabe kann der Aktivitäts-/Modellkontext weiterhin
angezeigt werden. Ohne beide Freigaben sind beide Wege gesperrt.

Fehlendes Cluster: null und missing_or_ineligible, kein Ersatzcluster; Interessen-
weg und geeignete Regression bleiben möglich. Fehlende Prognose: null mit Status;
Angebote und zulässiger gespeicherter Clusterkontext bleiben davon unabhängig.

## 4. Ranking und fachliche Trennung

Interessen bestimmen zuerst die zulässigen Kategorien. Stufe A verlangt zusätzlich
manuell bestätigten Sporttag und beobachteten positiven Anteil. A wird nach dem
höchsten passenden Anteil absteigend, dann offer_id aufsteigend geordnet. Stufe B
enthält alle übrigen zulässigen Angebote, nur nach offer_id aufsteigend.
Die Top-5-Grenze gilt nach der Sortierung.

Aktuell acht bestätigte Zuordnungen in `offer_sport_tags_approved.csv`; die Review-
Vorschläge allein wirken nicht. Kein Tag ist eine negative Präferenz. Die 22
ungetaggten Angebote bleiben grundsätzlich über ihre Kategorien empfehlbar.
K-Means beschreibt relative Trainingshäufigkeit; Regression schätzt Gesamtaktivitäten
in der Folgewoche. Beide beeinflussen weder Ranking noch Angebotsbegründung.
Keine Fitness-, Gesundheits-, Erfahrungs-, Leistungs- oder Kaufbewertung suggerieren.

## 5. Zeitbezug, Daten- und Modellvoraussetzungen

Default ist ausdrücklich der **historische** Demo-Stichtag 05.07.2026, nicht das
heutige Datum. Verwendete Regressionswochen 23–26: 08.06.–05.07.2026.
Ziel: 06.–12.07.2026. Die aktuelle Eingabewoche ist im Vierwochenmittel enthalten.
Vor dem Ende des 26-Wochen-Profils werden dessen Anteile und Segment nicht ausgegeben.

Bei anderen Cutoffs: letzte vier bis dahin vorhandene, abgeschlossene, verlässlich
erfasste aufeinanderfolgende Montag–Sonntag-Wochen. Fehlende Wochen sind keine
Nullwochen. Das Modell wird für Eingabewochen vor dem Ende seiner Trainingsziele
(07.06.2026) gesperrt. Ein späteres as_of erzeugt keine neueren Daten: immer
input_week_end und Zielzeitraum anzeigen; bei veraltetem Datenbestand keine
aktuelle Wochenprognose versprechen. Inferenz bleibt ohne Rundung oder Kappung.

Die V2-Verlässlichkeit folgt nur aus dokumentierter synthetischer Herkunft und
Hashprüfungen. Der lokale Loader benötigt Projektdateien, Modellabhängigkeiten und
teilweise den festen Basis-Git-Baum; kein eigenständiges Deployment implementiert.
Joblib nur aus der vertrauenswürdigen Projektquelle laden. requirements-modeling.txt
beschreibt die Modellierungsumgebung; eine frische Dashboard-Installation wurde
hier nicht nachgewiesen.

## 6. Fehlerbehandlung und Integrationsgrenzen

- Fehlende Pflichtargumente: Python TypeError.
- Ungültige bool-Parameter, falscher as_of-Typ oder unbekannter Nutzer: ValueError.
- Fehlerhafte IDs, Katalogwerte oder bestätigte Tagdatensätze: Validierungsfehler,
  keine stillschweigende Reparatur.
- Fehlende/ungültige Interessen: leerer Interessenweg mit Status.
- Nicht verifizierbare Aktivitätsdateien: betroffener Kontext bleibt gesperrt;
  fehlende/ungültige Cluster-/Profildatei wird separat behandelt.
- Abgefangene Daten-/Modellfehler der Regression: null mit prediction_status.
- Nicht alle Infrastruktur-/Abhängigkeitsfehler werden von der Engine abgefangen:
  Dateizugriff, Git-Verfügbarkeit, CSV-Struktur oder beschädigte Pickle-Dateien
  können Ausnahmen weiterreichen. Es existiert kein HTTP- oder Frontend-Fehleradapter.

Ein späteres Dashboard muss Validierungs-/Systemfehler verständlich anzeigen und
bei Ausnahme keine alte Nutzerantwort weiterverwenden. Die Engine besitzt keine
Authentifizierung, reale Einwilligungsverwaltung oder Sitzungs-/Cacheisolierung.
Caching darf Freigaben und Nutzerkontext nicht vermischen. Diese Infrastruktur
bleibt Aufgabe der späteren UI-Anbindung, keine hier implementierte Fähigkeit.

## 7. Abnahmenachweis

U001/U002/U003 am 05.07.2026 mit beiden simulierten Freigaben sowie U001 ohne
Garmin- und ohne Interessenfreigabe tatsächlich geprüft. 42 Empfehlungstests
bestehen einschließlich Vergleichs-, Zeitgrenzen- und Schnittstellentests.
Für alle fünf Szenarien wurden Ausgabeidentität bei Wiederholung und unveränderte
bisherige Felder nachgewiesen. Ausschließlich interest_categories und
profile.sport_shares wurden rückwärtskompatibel ergänzt. Kein neues Feature,
Ranking oder zusätzlicher Modellaufruf entsteht durch diese Felder.

Die Engine ist für eine spätere lokale Dashboard-Integration des synthetischen
Demonstrators technisch bereit, unter den dokumentierten Daten- und Laufzeitgrenzen.
Keine Aussage über reale Empfehlungsqualität oder Produktionseignung.
