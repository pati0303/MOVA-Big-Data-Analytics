# MOVA – AP 6.2: Ausführung des regelbasierten Demonstrators

Stand: 31.10.2026; V2; Worktree `/workspace/MOVA-AP6`, Branch
`ap6-recommendations`; Basis `a8f97ad75c378329a614a322bd541f372de0b072`.
Keine UI, keine Modelländerung, kein Commit oder PR.

> Fortschreibung AP 6.3b: Die Abschnitte 1–10 dokumentieren den historischen
> AP-6.2-Stand mit leerer Freigabetabelle. Der aktuelle Freigabestand und die
> erneute technische Validierung stehen in Abschnitt 11.

## 1. Ziel und Dateien

Implementiert: deterministische Auswahl von maximal fünf Katalogangeboten mit
Begründung, getrennt von gespeichertem K-Means-Kontext und neu berechneter Regression.

Neue Dateien dieses Schritts:

- `src/recommendation_engine.py`: Datenzugriff, Freigaben, reines Matching,
  Orchestrierung, optionale Regression, CLI.
- `tests/test_recommendation_engine.py`: 24 automatisierte Tests.
- `documentation/offer_sport_tags_approved.csv`: separate, absichtlich leere
  Freigabestruktur mit Kopfzeile.
- Dieser Ausführungsbericht.

AP-6.1-Konzept und Review-Tabelle bleiben unverändert historische Konzeptstände.
Der AP-6.2-Auftrag entscheidet die dort offenen Punkte Top-5 und Sortierung nach
maximalem positiv beobachtetem Sportanteil. Die dort vorgeschlagenen Freigabenamen
werden in der Implementierung durch `interests_permission` und `garmin_permission`
ersetzt. Ausstehende manuelle Tagfreigaben verhindern den Kategorienbetrieb nicht.

## 2. Tatsächlich verwendete Daten

`data/raw/users_simulated.csv` (100 Nutzer), `offers_simulated.csv` (30 Angebote);
bei Garmin-Freigabe zusätzlich `activities_simulated.csv`,
`data/processed/kmeans_user_features.csv`, `user_clusters.csv` und
`user_weekly_activities.csv`. Keine zusätzlichen Nutzer-/Angebotsattribute erzeugt.
Interessen werden strikt als True/False gelesen; False ist nicht positiv ausgewählt,
kein belegtes ausdrückliches Desinteresse. Eindeutige IDs und Katalogkategorien
werden beim Laden geprüft.

Aktivitätsquellen werden gegen vorhandene V2-Hashes bzw. bei fehlendem Manifesthash
gegen den festen Basis-Git-Baum geprüft. Daraus folgt nur die dokumentierte
Vollständigkeit der synthetischen V2. Der Loader kann keine Vollständigkeit echter
Garmin-Aufzeichnungen beweisen. Er ist ein Projektloader mit lokalem Git-Bestand,
noch kein eigenständiges Deployment-Paket.

## 3. Technischer Datenfluss und Regeln

1. `run`: beide Simulationsparameter strikt als Boolean prüfen; Nutzer- und
   Katalogdaten laden. Aktivitätsquellen nur bei Garmin-Freigabe laden.
2. `select_user`: Nutzer muss eindeutig existieren; unbekannte ID führt zu Fehler.
3. Optional `sport_profile`: verifizierte, bekannte V2-Sportdaten und gültige
   unskalierte Anteile verwenden; bei fehlenden/ungültigen Daten keine Sportvorteile.
4. K-Means-Zuordnung separat abrufen; Regression separat berechnen, wenn möglich.
5. `interest_categories`: nur Kategorien mit True; bei fehlenden/ungültigen Feldern
   leere personalisierte Ausgabe mit Status, keine Imputation.
6. `filter_offers`: Kandidaten ausschließlich aus positiven Interessenkategorien.
7. `rank_offers`: A vor B; A nach höchstem positiv beobachtetem Anteil eines
   bestätigten Tags absteigend; dann offer_id aufsteigend. B nur nach offer_id.
8. `recommendations`: erste maximal fünf, fortlaufende Position ab 1, Preise und
   Rabatte unverändert aus Katalog; keine Verwendung als Rankingfaktor.
9. `match_reason`: ausgewählte Kategorie und bei A beobachtete Sportart plus
   manuell bestätigter Angebotsbezug. Keine Fitness-, Kauf- oder Eignungsbehauptung.

Die reinen Filter-/Rankingfunktionen arbeiten auf bereits autorisierten Eingaben.
Für Dashboard-Zugriff ist die freigabeprüfende API `run` bzw. `recommend_user`
vorgesehen. Ergebnis ist ein JSON-kompatibles Dictionary mit `permissions_simulated`,
`personalization_status`, separatem `profile` und `recommendations`. Herkunft wird
als `stored_user_clusters` oder `new_inference_saved_regression_model` ausgewiesen.
Fehlende Kontexte verwenden null und Status; kein künstlicher Null-Prognosewert.

## 4. Sporttag-Freigabe

Die Review-Datei wird von der Engine bewusst nicht geladen. Ihre 8 eindeutigen,
2 mehrdeutigen und 20 nicht zuordenbaren Vorschläge bleiben sämtlich pending_review.
Der tatsächliche Freigabekatalog hat aktuell **null Einträge**.

Nur ein Datensatz in `offer_sport_tags_approved.csv` mit exakt
`review_status=manually_confirmed` kann einen Sportvorteil ermöglichen. Er benötigt
`offer_id`, den exakt übereinstimmenden `title`, `sport_tags` (bekannte Sportnamen,
mehrere durch `|`), `reviewed_by` und `reviewed_at` (ISO-Datum). Unbekannte Tags,
fehlende Reviewerangabe, ungültiges Datum, doppelter Eintrag oder abweichender Titel
sind Fehler; fehlende Datei oder nicht bestätigter Status bewirken keinen Vorteil.
Die Datei ist eine manuell gepflegte Vertrauensgrenze, kein automatischer
Authentizitäts- oder Einwilligungsnachweis. Niemand wurde als tatsächlicher
Freigebender eingetragen. Fachliche Bestätigungen erfolgen erst gemeinsam.

## 5. Simulierte Berechtigungen und Fallbacks

Beide Berechtigungen sind explizite API-Pflichtparameter, keine aus CSVs abgeleiteten
Einwilligungen. Nicht-Booleanwerte werden abgewiesen. CLI verlangt für beide yes/no.
`permissions_simulated` weist `simulated=true` und `real_consent_record=false` aus.
Zustände werden nicht zwischen Nutzern gespeichert oder automatisch übernommen.

| Situation | Verhalten |
| --- | --- |
| Interessen ja, Garmin nein | Nur Kategorien; alle Ergebnisse B; kein persönlicher Aktivitäts-/Modellzugriff |
| Beide ja | Kategorien plus optional freigegebene Sporttags; unabhängige Profilkontexte |
| Interessen nein | Keine personalisierten Angebote; separat erlaubter Garmin-Kontext kann verfügbar sein |
| Keine positive Kategorie | Leere Liste, no_positive_interests; allgemeiner Katalog wäre später separat |
| Fehlende/ungültige Interessen | Leere Liste, invalid_or_missing_interests |
| Keine Clusterzuordnung | Segment null; Kategorien und geeignete Regression bleiben möglich |
| Ungültiges/unverifiziertes Sportprofil | Keine Sportpriorisierung; Interessenweg bleibt möglich |
| Frequenz null | Keine Sportanteile verwendet, kein reguläres Segment; keine Präferenzen erfunden |
| Unbekannte Sportarten | Sportpfad und Regression gesperrt, bis Aktivitätsumfang fachlich geklärt |
| Fehlende/ungültige vier Wochen | Prognose null mit nachvollziehbarem Status |
| Modellhash/Parameter ungültig | model_unavailable_or_invalid; Interessenweg bleibt möglich |

Bei beschädigtem Katalog oder ungültigem bestätigtem Freigabeeintrag wird ein klarer
Validierungsfehler ausgelöst, anstatt unbemerkt falsche Empfehlungen zu liefern.

## 6. Gespeichertes K-Means-Ergebnis

Es erfolgt kein Clustering oder predict auf dem K-Means-Modell. Die vorhandene
Zuordnung wird aus `user_clusters.csv` gelesen und gegen das bekannte ID-/Textmapping
validiert. Beide Segmente beschreiben relative Trainingshäufigkeit. Sie wirken
nicht auf Ranking oder Regression. Die V2-Sportprofile/Labels über 26 Wochen werden
vor dem 05.07.2026 nicht für frühere Stichtage ausgegeben. Ohne Garmin-Freigabe
bleiben Segment und Cluster-ID null.

## 7. Neu berechnete Regression

Wiederverwendet: `outputs/models/regression_linear.joblib`, Modellmetadaten und
Versionen aus der vorhandenen Modellierungsumgebung. Lazy Import erst bei zulässiger
Inferenz; Hash, Parameter, Koeffizienten und Feature-Reihenfolge werden geprüft.
Kein Fit, keine Skalierung, Rundung oder Kappung; ein numerischer Thread.

Die letzten vier vorhandenen, vor/zu `as_of` abgeschlossenen Wochen des Nutzers
werden gewählt. Ihre Montag–Sonntag-Intervalle müssen vollständig und ohne Lücken
aufeinanderfolgen; Counts müssen endlich, nichtnegativ und ganzzahlig sein. Eine
fehlende Woche wird nicht durch eine ältere fünfte ersetzt. Die synthetische
Verlässlichkeit folgt aus der Quellenprüfung, nicht allein aus vier CSV-Zeilen.

Merkmale in dieser Reihenfolge:

1. `activities_current_week = c(t)`.
2. `avg_activities_last_4_weeks = (c(t−3)+c(t−2)+c(t−1)+c(t))/4`.

Nur `model.predict` erzeugt den neuen Wert. Zielwerte, vorbereitete Train/Test-Tabellen,
Cluster und Interessen sind keine Regressoren. Ein Modell, dessen Trainingsziele
nach dem ausgewählten Eingabe-Wochenende liegen, wird mit
`model_training_after_cutoff` gesperrt. Das gespeicherte Modell wurde auf Zielwochen
bis einschließlich 07.06.2026 trainiert. Spätere Beobachtungen werden nicht verwendet.

Standard ist ausdrücklich der historische Demo-Stichtag 05.07.2026, nicht die
heutige Kalenderwoche. Fenster: 08.06.–05.07.2026 (Wochen 23–26); Prognoseziel:
06.–12.07.2026. Für andere Cutoffs werden tatsächlich verwendetes Wochenende und
Zielzeitraum ausgegeben; ein älterer Datenstand wird nicht als aktuelle Prognose
umetikettiert. K-Means benötigt 26 Wochen, Regression nur vier geeignete Wochen.

Die Prognose ist unverbindlicher Aktivitätskontext. Synthetische AP-5-Evaluation,
große individuelle Fehler, keine reale Generalisierung, keine Kaufwahrscheinlichkeit
oder Fitnessbewertung. Sie hat keinen Einfluss auf Angebotsrang oder Begründung.

## 8. Ausgeführte Tests

Zweimal tatsächlich ausgeführt:

```bash
PYTHONDONTWRITEBYTECODE=1 python -m unittest discover -s tests -p test_recommendation_engine.py -v
```

**24 Tests in beiden Läufen bestanden.** Ergebnisprotokolle sind bis auf die
Laufzeit identisch. Die gesamte ältere Suite wurde nicht ausgeführt, weil sie
teilweise Training aufruft. Diese Angabe behauptet keinen neuen AP-5-Gesamttest.

Abgedeckt: striktes Interessenparsing, mehrere/keine Interessen, beide Freigaben,
keine Garmin-Datenzugriffe bei fehlender Freigabe, bestätigte vs. unbestätigte Tags,
Maximalanteil bei Mehrfachtags, Nullanteile, ungetaggte Angebote, Reihenfolge und
Gleichstand bei vertauschten Eingangszeilen, Top-5, fehlendes Cluster, ungültige oder
fehlende Historie, Modellgleichung unabhängig nachgerechnet, aktuelle Woche im
Mittel, Zukunftsbeobachtungen, zeitliche Trainingsgrenze, Inaktivität, unbekannte
Sportdaten, ungültige Profile, unbekannter Nutzer, Wiederholung und Quellenintegrität.
Fit-Aufrufe von KMeans und LinearRegression sind beim Integrationstest gesperrt.
Alle 153 bereits versionierten Dateien werden gegen ihre tatsächlichen Git-Blobhashes
geprüft, einschließlich sämtlicher Rohdaten und Modellartefakte.

Sportpriorisierung ist mit ausdrücklich künstlichen F001–F004-Testangeboten und
TEST-Nutzerkennung geprüft. Diese Fixtures existieren nur im Testspeicher und sind
keine zusätzlichen V2-Produktivdaten. Ein Test-Freigabedatensatz in einem temporären
Verzeichnis unter work/ wird danach entfernt; keine tatsächliche Tagfreigabe.

## 9. Drei tatsächliche V2-Beispiele und Reproduzierbarkeit

Alle Beispiele tatsächlich mit der Engine ausgeführt, keine manuell freigegebenen
Sporttags. Deshalb liegen alle Angebote in B und werden nach offer_id geordnet.
Beide simulierten Freigaben ja, Stichtag 05.07.2026:

| Nutzer | Positive Kategorien | Top-5-IDs | Gespeichertes Segment | c(t) / Vierwochenmittel | Neue Prognose |
| --- | --- | --- | --- | --- | --- |
| U001 | Sport, Outdoor, Freizeit | O001, O002, O003, O004, O005 | Geringere Trainingshäufigkeit | 3 / 2,75 | 2,6902546519777557 |
| U002 | Outdoor, Freizeit | O009, O010, O011, O012, O013 | Höhere Trainingshäufigkeit | 6 / 3,5 | 3,6927952445497203 |
| U003 | Wellness | O017, O018, O019, O020, O021 | Geringere Trainingshäufigkeit | 0 / 2,75 | 2,005684418425836 |

Die Running-Anteile unterscheiden sich tatsächlich: U001 0,5; U002
0,03409090909090909; U003 0,24074074074074073. Sie erzeugen ohne bestätigte Tags
keinen Rankingvorteil. Insbesondere erlaubt U002s Sportprofil keine Sport-Angebote,
weil interest_sport dort False ist.

Jeder Nutzer wurde außerdem mit nur Interessenfreigabe sowie ohne Interessenfreigabe
(bei Garmin-Freigabe) ausgeführt. Nur Interessen: dieselben Kategorien-Ergebnisse,
Segment/Prognose null, permission_denied. Ohne Interessenfreigabe: null Empfehlungen.
Insgesamt neun Ausgaben wurden mit erneut geladenen Quellen wiederholt und als
kanonisches JSON verglichen: **bytegleich**. Rechenwerte wurden nicht gerundet.

Reproduzierbarer Aufruf im Repository:

```bash
PYTHONDONTWRITEBYTECODE=1 python src/recommendation_engine.py U001 --interests-permission yes --garmin-permission yes --as-of 2026-07-05
```

Lokale Prüfprotokolle und Beispielausgaben stehen ignoriert unter `work/ap62-*`;
keine neuen Empfehlungen wurden in bestehende Datendateien geschrieben.

## 10. Grenzen und nächste fachliche Entscheidungen

Keine Angebotsnutzung, Kaufabsicht, sportliche Eignung oder Empfehlungsqualität
nachgewiesen. Keine strukturierten Sportanforderungen, Orte, Termine oder
Verfügbarkeiten vorhanden; diese werden nicht ergänzt. Keine simulierten Umsätze
oder unbelegten CRISP-DM-Iterationen. Der projektgebundene Loader ersetzt keine
reale Import-/Einwilligungsinfrastruktur.

Die offer_id-Gleichstandsregel ist reproduzierbar, aber keine Relevanzbewertung:
bei mehreren Kategorien können frühe IDs die Top-5 dominieren. Eine ausgewogene
Kategorieverteilung wäre eine zusätzliche fachliche Entscheidung und ist nicht
heimlich implementiert.

Nächster Schritt: tatsächliche Tagvorschläge gemeinsam prüfen und nur ausdrücklich
bestätigte Zuordnungen mit Reviewer/Datum in der separaten Freigabestruktur erfassen.
Danach fachliche Abnahme anhand realer V2-Ausgaben mit aktivierter Sportpriorisierung.
UI-Entwicklung bleibt separat. Kein Commit und kein PR erstellt.


## 11. AP 6.3b – fachliche Tagfreigabe und technische Validierung

Stand: 31.10.2026. Freigabegrundlage ist die explizite Auswahl im Nutzerauftrag
AP 6.3b. **Fachliche Zuordnung für den synthetischen Prototyp, keine extern
geprüften Produktdaten.** Es wurde kein externer Prüfer oder Personenname erfunden.
`reviewed_by` lautet „Projektteam – expliziter Nutzerauftrag AP 6.3b“;
`reviewed_at` ist 2026-10-31, Status jeweils `manually_confirmed`.

Vor dem Schreiben wurden alle acht Kennungen, tatsächlichen Titel, Kategorien,
Tagvorschläge und Review-Status mit Angebotskatalog und Review-Tabelle abgeglichen.
Die vorhandene Engine-Struktur war eindeutig; es gab keinen Widerspruch.

| offer_id | Tatsächlicher Titel | Freigegebener Tag | Nachvollziehbarer Titelbezug |
| --- | --- | --- | --- |
| O001 | FIKTIV – Laufschuhe | Running | Laufschuhe benennen Ausrüstung für Laufen. |
| O003 | FIKTIV – Schwimmkurs | Swimming | Schwimmkurs nennt Schwimmen. |
| O004 | FIKTIV – Tennistraining | Tennis | Tennistraining nennt Tennis. |
| O005 | FIKTIV – Padelturnier | Padel | Padelturnier nennt Padel. |
| O006 | FIKTIV – Fahrradhelm | Cycling | Fahrradhelm benennt Radsportausrüstung. |
| O007 | FIKTIV – Hantelset | Strength | Hanteln sind Krafttrainingsausrüstung. |
| O009 | FIKTIV – Wanderrucksack | Hiking | Wanderrucksack nennt Wanderausrüstung. |
| O010 | FIKTIV – Wanderführung | Hiking | Wanderführung bezeichnet Wandern. |

O002 (Fitnesskurs) erhält keinen Tag: Der Titel legt keine der acht Sportarten
fest. O011 (Trekkingstöcke) erhält keinen Tag: Hiking oder Walking bleiben anhand
des Titels mehrdeutig. Auch die übrigen 20 Angebote erhalten keinen Sporttag.
Alle 22 ungetaggten Angebote bleiben innerhalb positiv ausgewählter Kategorien
als Stufe B grundsätzlich empfehlbar; Top-5 bedeutet keine Garantie der Ausgabe
jedes einzelnen Kandidaten. Fehlende Tags bedeuten keine negative Präferenz.

### Technische Verwendung und Validierung

Die separate `offer_sport_tags_approved.csv` enthält exakt acht Datensätze mit
acht eindeutigen offer_id, exakt den acht beauftragten Angebot-Tag-Paaren, bekannten
Sportbezeichnungen und unveränderten Katalogtiteln. Keine Doppelzuordnung und kein
zusätzlich freigegebener Tag. Die acht Einträge verwenden sieben unterschiedliche
Sportarten aus dem zugelassenen Acht-Sportarten-Vokabular; Walking und Hiking werden
nicht gleichgesetzt. Hiking kommt bei zwei ausdrücklich bestätigten Angeboten vor.

Die Engine bleibt unverändert: Nur `manually_confirmed` in der separaten
Freigabedatei zählt. Die ursprüngliche Review-Tabelle bleibt unverändert als
historischer Vorschlagsstand mit pending_review erhalten. Ein gezielter Test
bestätigt, dass diese Review-Datei allein weiterhin keinerlei Tags freigibt.

Kategorienfilter und simulierte Interessenfreigabe gelten weiterhin zuerst.
Bei Garmin-Freigabe und gültigem Sportprofil: A bei bestätigtem Tag mit Anteil >0,
sonst B. Sortierung A zuerst, maximaler positiver passender Anteil absteigend,
Gleichstand offer_id aufsteigend; B ausschließlich offer_id aufsteigend. Keine
neuen Gewichte und keine Nutzung von K-Means oder Regression als Rankingfaktor.

### Tatsächlich ausgeführte Tests

```bash
PYTHONDONTWRITEBYTECODE=1 python -m unittest discover -s tests -p test_recommendation_engine.py -v
```

**25 Tests bestanden.** Die frühere Annahme einer leeren tatsächlichen
Freigabedatei wurde durch die Prüfung der exakt acht freigegebenen Datensätze
ersetzt. Die frühere Ranking-Gleichheit mit/ohne Garmin war nur bei leerer
Tagfreigabe gültig: Dieser Test variiert jetzt ausschließlich Clusterkontext und
Prognose im Speicher bei unverändertem zulässigem Sportprofil. So prüft er die
Unabhängigkeit vom ML-Kontext auch nach aktiver Tagfreigabe korrekt.

Ein zusätzlicher Integrationstest prüft am tatsächlichen U001-Profil die
Kategoriengrenze, Stufen A/B, den maximalen beobachteten passenden Anteil,
ID-Gleichstände und Top-5-Übernahme aus der geordneten Kandidatenliste.
O002/O011 bleiben dabei B. Bestehende Fixturetests prüfen weiterhin unbestätigte
Tags, Mehrfachtags und deterministische Gleichstände. Tests ohne Garmin-Freigabe
belegen ausschließlich B sowie fehlenden Zugriff auf persönliche Aktivitätsdaten;
ohne Interessenfreigabe bleibt die Empfehlungsliste leer. Fit-Aufrufe werden im
Modellintegrationstest weiterhin gesperrt.

Der Integritätstest bestätigt sämtliche 153 bereits versionierten Dateien gegen
Git-Blobhashes. Angebotskatalog, andere Rohdaten und beide ML-Modelle sind unverändert.
Ein zusätzlicher SHA-256-Abgleich mit dem Stand vor diesem Arbeitsschritt bestätigt
auch die unveränderte Engine und Review-Datei. Keine Modellparameter angepasst.

Geändert wurden ausschließlich die Freigabetabelle, die gezielt fortgeschriebenen
Empfehlungstests und dieser Bericht; lokale Prüfprotokolle stehen ignoriert unter
`work/ap63b-*`. Kein vollständiger Vorher-Nachher-Vergleich, keine fachliche
Wirksamkeitsevaluation und keine neuen Empfehlungserfolge behauptet. Keine neuen
Produktivdaten, kein Training, keine UI, kein Commit und kein PR.

**AP 6.3c kann mit diesem validierten Freigabestand beginnen.**

## 12. AP 6.3c – kontrollierter Vorher-Nachher-Vergleich

Stand: 31.10.2026. CRISP-DM 5.1 Evaluate Results und 5.2 Review Process:
Evaluation der **Regelwirkung**, keine neue ML-Evaluation und keine behauptete
zusätzliche CRISP-DM-Iteration.

### Ziel, Architektur und kontrollierte Bedingungen

Untersucht wird ausschließlich der Einfluss der acht in AP 6.3b bestätigten
Angebotstags auf die Top-5-Listen der 100 vorhandenen synthetischen V2-Nutzer.

- A/Vorher: leeres Dictionary bestätigter Tags.
- B/Nachher: exakt die acht tatsächlichen Freigaben aus der separaten CSV.
- In beiden Varianten: simulierte Interessen- und Garmin-Freigabe True,
  Stichtag 05.07.2026, identische 100 Nutzer, Interessen, unskalierte Sportanteile,
  30 Katalogangebote, Sortierlogik und Top-5-Grenze.

`src/recommendation_comparison.py` verwendet `permission_flags`, `select_user`,
`interest_categories`, `sport_profile` und `recommendations` der bestehenden Engine.
Für jeden Nutzer werden Kategorien und geprüftes Sportprofil einmal bestimmt und
mit demselben Katalogobjekt beiden Engine-Aufrufen übergeben. Nur das Argument
`approved_tags` unterscheidet sich. Die vorhandene reine Matching-Schnittstelle
reicht aus; **keine Änderung der Empfehlungsengine** war erforderlich.

Es erfolgen 200 Matching-Aufrufe (2 × 100); die Freigabedatei wird weder vorübergehend
verändert noch ersetzt. K-Means und Regression sind nicht Teil der Rangberechnung.
Es werden auch keine neuen Regressionsprognosen oder Clusterzuordnungen berechnet.
Der bestehende V2-Loader validiert Quellen; seine zusätzlich geladenen Cluster- und
Wocheninformationen werden für das Ranking nicht verwendet.

### Erzeugte Dateien und Definitionen

- `src/recommendation_comparison.py`
- `tests/test_recommendation_comparison.py`
- `outputs/tables/recommendation_before_after_users.csv`: 100 eindeutige Nutzer,
  Kategorien, zulässige Kandidatenzahl, Listenlängen, geordnete Angebots-IDs,
  Stufe-A-Zahlen, Veränderungsflags, gemeinsame Angebote und exklusive Fallgruppe.
- `outputs/tables/recommendation_before_after_offers.csv`: alle 30 Angebote mit
  Häufigkeiten, Differenz, Neueintritten, Austritten, behaltenen Angeboten mit
  gleicher/geänderter Position sowie Stufe-A-Zahl nachher.
- `outputs/tables/recommendation_before_after_summary.json`: Varianten,
  Berechtigungen, Stichtag, Kennzahlen, Kategorien-/Sportanalyse, tatsächliche
  Beispiele und SHA-256 der Eingaben, Quellskripte und Modellartefakte.
- `outputs/figures/recommendation_before_after_users.png`
- `outputs/figures/recommendation_before_after_tiers.png`

Listenfelder sind JSON-Arrays in CSV-Feldern. `ordered_list_changed` bedeutet
unterschiedliche geordnete Liste einschließlich anderer Zusammensetzung.
`shared_offer_position_changed` erfasst Positionsänderungen gemeinsamer Angebote,
auch wenn gleichzeitig Angebote ein-/austreten. Die exklusive Fallgruppe ist:
identische Liste; sonst gleiche Angebotsmenge = nur Reihenfolge; sonst veränderte
Zusammensetzung. Leere Listen sind identisch und zählen zur unveränderten Gruppe.

### Tatsächliche Gesamtkennzahlen

| Kennzahl | Ergebnis / Bezugsgröße |
| --- | --- |
| Unveränderte geordnete Liste | 36 Nutzer |
| Ausschließlich andere Reihenfolge | 0 Nutzer |
| Andere Top-5-Zusammensetzung | 64 Nutzer |
| Summe exklusiver Gruppen | 100 Nutzer |
| Irgendeine Listenveränderung | 64 / 100 = 64 % |
| Ausgegebene Slots vorher / nachher | 475 / 475 |
| Stufe A vorher / nachher | 0 / 344 Slots |
| Stufe B vorher / nachher | 475 / 131 Slots |
| Stufe-A-Anteil nachher | 344 / 475 = 72,42105263157895 % |
| Mindestens eine Stufe A nachher | 81 Nutzer |
| Durchschnittlich gemeinsame Angebote | 3,48 je Nutzer, Nenner alle 100 einschließlich leerer Listen |
| Keine positive Interessenkategorie | 5 Nutzer, jeweils null Empfehlungen |
| Weniger als fünf zulässige Angebote | 5 Nutzer, sämtlich ohne positive Kategorie |
| Positive Interessen, aber weniger als fünf Kandidaten | 0 Nutzer |

Alle 64 Nutzer mit positivem Sportinteresse wechseln die Zusammensetzung. Bei den
übrigen 36 bleibt sie gleich. 81 Nutzer mit Stufe A sind nicht gleichbedeutend mit
81 veränderten Listen: Bei 17 Nutzern mit Outdoorinteresse ohne Sportinteresse
stehen die Hiking-Angebote schon vorher zuerst; ihre Stufe ändert sich, ihre
Position nicht. Die anderen unveränderten Fälle entfallen auf Wellness-/Freizeit-
Ausgaben und fünf leere Listen. Eine reine Umordnung wurde nicht beobachtet und
wird nicht als tatsächlicher Fall erfunden.

### Veränderungen je Angebot und Kategorie

| Angebot | Slots vorher → nachher | Differenz | Neueintritte / Austritte | Behalten, aber Position verändert |
| --- | --- | --- | --- | --- |
| O001 Laufschuhe | 64 → 55 | −9 | 0 / 9 | 44 |
| O002 Fitnesskurs | 64 → 8 | −56 | 0 / 56 | 8 |
| O003 Schwimmkurs | 64 → 41 | −23 | 0 / 23 | 35 |
| O004 Tennistraining | 64 → 42 | −22 | 0 / 22 | 30 |
| O005 Padelturnier | 64 → 47 | −17 | 0 / 17 | 33 |
| O006 Fahrradhelm | 0 → 52 | +52 | 52 / 0 | 0 |
| O007 Hantelset | 0 → 43 | +43 | 43 / 0 | 0 |
| O009 Wanderrucksack | 17 → 35 | +18 | 18 / 0 | 0 |
| O010 Wanderführung | 17 → 31 | +14 | 14 / 0 | 0 |

Alle übrigen Angebotshäufigkeiten bleiben gleich. Neueintritte und Austritte sind
Nutzer-Angebot-Paare, keine neuen Produktivangebote. Ein bereits vorhandenes Angebot
mit anderer Position zählt nicht zusätzlich als Neueintritt. Beispielsweise
bleibt O001 häufig in der Liste und verschiebt sich bei 44 Nutzern; die Nettozahl
−9 beschreibt ausschließlich die Häufigkeitsdifferenz. O002 bleibt trotz fehlendem
Tag achtmal in den Top 5. O011 bleibt 17-mal enthalten. Kein ungetaggtes Angebot
wird allein wegen des fehlenden Tags aus der zulässigen Kandidatenmenge entfernt.

Stufe-A-Slots nach Sportart (je ausgegebenem Angebot genau eine Zuordnung):
Hiking 66, Running 54, Cycling 52, Padel 47, Strength 43, Tennis 42, Swimming 40;
Summe 344. Hiking umfasst zwei freigegebene Angebote, alle anderen genannten
Sportarten jeweils eines. Diese Zählung ist keine Nutzerzahl und kein fairer
Sportarten-Popularitätsvergleich. Walking hat keinen bestätigten Angebotstag.
Am häufigsten in Stufe A: O001 (54), O006 (52), O005 (47), O007 (43).
O001 ist insgesamt 55-mal enthalten, davon einmal B – beobachteter Anteil null
bleibt grundsätzlich empfehlbar und ist kein Desinteresse.

| Kategorie | Slots vorher → nachher | Nutzer mit Eintritt/Austritt/Positionsänderung innerhalb der Kategorie |
| --- | --- | --- |
| Sport | 320 → 288 | 64 |
| Outdoor | 85 → 117 | 18 |
| Wellness | 25 → 25 | 0 |
| Freizeit | 45 → 45 | 0 |

Die Kategorie-Nutzerzahlen zählen jeden Nutzer je Kategorie höchstens einmal;
sie sind wegen Überschneidungen nicht zu einer Gesamtzahl veränderter Nutzer zu
addieren. Gleiche Slotzahl könnte grundsätzlich Positionsänderungen verdecken;
deshalb wird beides separat ausgewiesen.

### Drei tatsächlich ausgeführte Beispiele

**U001 – Zusammensetzung verändert.** Positive Kategorien: Sport, Outdoor, Freizeit.
Relevante Anteile: Running 0,5; Cycling und Hiking jeweils
0,08823529411764706; Swimming/Tennis/Padel/Strength jeweils 0.
Vorher: O001, O002, O003, O004, O005.
Nachher: O001(A), O006(A), O009(A), O010(A), O002(B).
Running kommt vor den gleich hohen Cycling-/Hiking-Anteilen; deren Gleichstand
löst die offer_id. Drei neue Angebote treten ein. Die weiteren Sporttags erzeugen
bei beobachtetem Anteil null keinen Vorteil. O002 bleibt als Kategorieangebot B.

**U002 – Liste identisch trotz Stufenänderung.** Positive Kategorien: Outdoor,
Freizeit. Hiking-Anteil 0,11363636363636363.
Vorher und nachher: O009, O010, O011, O012, O013.
Nachher sind O009/O010 A, die übrigen B. Die zwei Hiking-Angebote standen vorher
bereits wegen ihrer offer_id zuerst. Trotz anderer Sportanteile bleibt die Kategorie
Sport ausgeschlossen, weil sie nicht positiv ausgewählt ist.

**U003 – Liste identisch ohne passenden Kategorietag.** Positive Kategorie: Wellness.
Beobachtet werden unter anderem Running 0,24074074074074073 und Hiking
0,018518518518518517, aber keines der Wellnessangebote besitzt einen freigegebenen
Sporttag. Vorher/nachher: O017, O018, O019, O020, O021; alle bleiben B.
Ein beobachteter Sportanteil überstimmt die Interessen-Vorauswahl nicht.

Es gibt keine dritte tatsächlich beobachtete exklusive Veränderungsgruppe;
stattdessen zeigen die beiden unveränderten Beispiele unterschiedliche Ursachen.

### Diagramme, Tests und Reproduzierbarkeit

Das Nutzerdiagramm zeigt die drei exklusiven Gruppen als absolute Nutzerzahlen
bei N=100. Das gestapelte Stufendiagramm zeigt 475 Empfehlungsslots je Variante
mit A/B-Zahlen; die Bezugsgröße ist Empfehlungsslots, nicht Nutzer.
Beide Grafiken wurden visuell auf vollständige Beschriftung geprüft.

```bash
PYTHONDONTWRITEBYTECODE=1 python src/recommendation_comparison.py
PYTHONDONTWRITEBYTECODE=1 python -m unittest discover -s tests -p 'test_recommendation*.py' -v
```

Tatsächlich bestanden: **36 Tests = 25 bestehende Engine-Tests + 11 neue
Vergleichstests**. Kontrolliert werden unter anderem 100 eindeutige Nutzer,
200 Engine-Aufrufe mit denselben Katalog-/Kategorien-/Sportprofilobjekten,
identische simulierte Berechtigungen, leere vs. exakt acht Freigaben, unveränderte
Datenobjekte/Freigabedatei, Listenlängen und Eindeutigkeit, alle drei Fallgruppen,
Gruppensumme, unabhängige Angebots-/Nutzeraggregation, Prozente und Nenner,
Kategorien ohne doppelte Nutzerzählung, Hashes und gespeicherte Resultate.
Ein Vergleich mit vertauschter Eingangsreihenfolge liefert dieselben Ergebnisse.
Modellladen, Modellinferenz und Fit sind im Vergleichstest gesperrt;
Modellartefakt-Hashes bleiben gleich. Der bestehende Integritätstest bestätigt
zusätzlich alle 153 Basisdateien gegen ihre Git-Blobhashes.

Der vollständige Vergleich wurde in der finalen Skriptversion zweimal ausgeführt.
Beide CSVs, die JSON-Datei und beide PNGs sind jeweils **bytegleich** (5/5).
SHA-256-Nachweis und lokale Protokolle stehen ignoriert unter `work/ap63c-*`.
Die JSON-Ausgabe enthält keine wechselnden Laufzeit-/Erstellungszeitstempel.
Bytegleichheit gilt für diese geprüfte Umgebung, nicht als Garantie für beliebige
Matplotlib-/Schrift-/Bibliotheksversionen auf anderen Rechnern.

### Interpretation und Bedeutung für den Demonstrator

Interessenbasierte Vorauswahl → zusätzliche bestätigte Sportarten-Zuordnung →
verändertes Ranking bei 64 Nutzern. Sichtbar werden insbesondere zuvor durch die
ID-Sortierung nicht erreichbare Angebote O006/O007 sowie Hiking-Angebote über
Kategorien hinweg innerhalb der zulässigen Interessenmenge.

Das ist **kein Nachweis besserer Empfehlungen**. Es fehlen Nutzerfeedback,
Klicks, Buchungen und Relevanzurteile. Weder Umsatz- noch Conversionwirkung wird
behauptet. Die acht Tags decken nur einen kleinen, ungleich über Kategorien und
Sportarten verteilten Teil des fiktiven Katalogs ab. Ungetaggte Angebote besitzen
keine vergleichbare Sportinformation; die ID-Sortierung und Top-5-Grenze bestimmen
weiterhin viele Ergebnisse. Ein hoher Anteil A misst Regelanwendung, keine Güte.

K-Means und Regression bleiben unabhängig gespeicherter bzw. berechneter
Aktivitätskontext aus AP 5, ohne Einfluss auf die hier gemessene Rangfolge. Ihre
Modellgüte wurde hier nicht erneut evaluiert. Für ein späteres Dashboard bieten
sich nebeneinander dargestellte Top-5-Listen mit Stufen, erklärten Sportanteilen und
markierten Neueintritten an; eine Oberfläche wurde nicht implementiert.

Nächster technischer Schritt: gemeinsame Abnahme von Ergebnisdateien und
Ausgabe-/Begründungsvertrag vor einer separaten Dashboard-Anbindung. Keine
zusätzlichen Sporttags, Gewichte oder Modelle eingeführt. Keine Rohdaten oder
bestehenden Modelle geändert, kein Commit und kein PR.

## 13. AP 6.3d – technische Abnahme und Dashboard-Vertrag

Stand: 31.10.2026. Ergebnis: Die Engine ist für die spätere lokale Dashboard-
Integration des synthetischen V2-Demonstrators technisch abgenommen. Noch keine UI
oder produktive Garmin-/Einwilligungsinfrastruktur implementiert.

### Ausgabeprüfung und minimale Ergänzung

Alle Anforderungen A–J sind verfügbar: user_id; positive Kategorien; erlaubte und
geprüfte acht Sportanteile; gespeichertes Segment; geeignete Regressionsprognose;
maximal fünf Angebote mit Titel/Kategorie/Preis/Rabatt, A/B, Begründung und Status.

Die bisherige JSON-Ausgabe enthielt Kategorien und Sportanteile noch nicht explizit.
Minimal ergänzt wurden `interest_categories` (sortierte Liste an der Wurzel) und
`profile.sport_shares` (Dictionary der bereits validierten und freigegebenen Anteile).
Bei fehlender Freigabe/ungültigen Daten bleiben sie [] bzw. {} mit bestehendem
Status. Keine Rohattribute, Funktionen, Rankinggewichte oder Modellberechnungen
hinzugefügt; bestehende Felder unverändert. Tatsächliche Typen, Statuswerte,
Fehlerverhalten und Aufruf sind in `recommendation_dashboard_contract.md` dokumentiert.

### Tatsächliche Szenarien mit bestätigten acht Tags

Stichtag 05.07.2026, Prognoseziel 06.–12.07.2026, beide Freigaben True:

| Nutzer | Positive Kategorien | Gespeichertes Segment | Top 5 mit Stufen | Prognose, ungerundet |
| --- | --- | --- | --- | --- |
| U001 | Freizeit, Outdoor, Sport | Geringere Trainingshäufigkeit | O001(A), O006(A), O009(A), O010(A), O002(B) | 2,6902546519777557 |
| U002 | Freizeit, Outdoor | Höhere Trainingshäufigkeit | O009(A), O010(A), O011(B), O012(B), O013(B) | 3,6927952445497203 |
| U003 | Wellness | Geringere Trainingshäufigkeit | O017(B), O018(B), O019(B), O020(B), O021(B) | 2,005684418425836 |

Interessen und alle ausgegebenen Anteile wurden gegen vorhandene Dateien geprüft;
Segmenttexte und IDs entsprechen der gespeicherten Zuordnung. Titel, Kategorie,
Preise/Rabatte stammen unverändert aus dem Katalog. Erklärungen benennen Kategorie
und bei A beobachtete Sportart plus bestätigten Angebotsbezug. Regression wird mit
den beiden bisherigen Merkmalen aus dem zulässigen Vierwochenfenster berechnet,
kein Fit. Die bestehende unabhängige Prüfung gegen die gespeicherte Modellgleichung
besteht weiterhin.

U001 mit Interessenfreigabe True und Garmin-Freigabe False: O001–O005, alle B;
Kategorien sichtbar, Sportanteile {}, Segment und Prognose null, permission_denied.
U001 mit Interessenfreigabe False und Garmin-Freigabe True: Kategorien [] und keine
Empfehlungen; unabhängig erlaubter Aktivitäts-/Modellkontext bleibt verfügbar.
Die Freigaben werden ausdrücklich als simuliert ausgegeben.

### Tests, Kompatibilität und Quellenintegrität

Ausgeführt:

```bash
PYTHONDONTWRITEBYTECODE=1 python -m unittest discover -s tests -p 'test_recommendation*.py' -v
```

**42 Tests bestanden:** 25 Engine-, 11 Vergleichs- und 6 neue gezielte
Dashboard-Vertragstests. Geprüft sind JSON-Kompatibilität mit allow_nan=False,
alle tatsächlichen Felder der drei Nutzer, Übereinstimmung mit Katalog/Profil,
Freigaben und ausbleibende Aktivitätsausgabe ohne Garmin-Freigabe,
fehlende Cluster-/Regressionsdaten, ungültige Sportwerte und deterministische Ausgabe.
Bisherige Tests kontrollieren weiter Top-5, ML-Kontext-Unabhängigkeit, Modellparameter,
keinen Fit, Trainingszeitgrenze, Zukunftsdaten und unveränderte 153 Basisdateien.

Die fünf tatsächlichen Szenarien wurden vor und nach der additiven Änderung geprüft:
Nach Entfernen der zwei neuen Felder sind sämtliche bisherigen Felder identisch.
Jedes Szenario wurde mit erneut geladenen Daten wiederholt: kanonische JSON-Ausgabe
bytegleich. Lokaler Nachweis: ignorierte Dateien `work/ap63d-*`.

Die AP-6.3c-Auswertung enthält die Engine-Prüfsumme. Für konsistente Provenienz
wurde das bestehende Vergleichsskript ohne Modellinferenz erneut ausgeführt.
In dessen Summary-JSON ändert sich ausschließlich der SHA-256-Eintrag der Engine;
alle Kennzahlen und Beispiele bleiben identisch. Beide Vergleichs-CSVs und beide
Diagramme bleiben bytegleich. Keine neue fachliche Evaluation.

### Verlauf, Grenzen und nächste Integration

AP 6.1: kompaktes Regelkonzept und manuelle Titelprüfung; AP 6.2: schlanke Python-
Engine mit getrennten Freigaben und Modellkontexten; AP 6.3a/b: Sichtung und explizite
fachliche Freigabe von acht Zuordnungen; AP 6.3c: kontrollierte Regelwirkungsanalyse
(64 veränderte, 36 unveränderte Listen); AP 6.3d: Ausgabe-/Schnittstellenabnahme.
Keine zusätzliche CRISP-DM-Iteration oder bessere Empfehlungsrelevanz behauptet.

Offen bleiben die projektgebundene Daten-/Git-Abhängigkeit, unabhängige Prüfung
realer Erfassung, reale Einwilligungen, Deployment und verständliche Behandlung
weitergereichter Infrastrukturfehler. Stichtag und Zielwoche müssen sichtbar bleiben:
Die V2-Demo prognostiziert keine heutige Woche. Sportanteile sind beobachtetes
Verhalten; Cluster relative Häufigkeit; Regression unverbindliche Aktivitätszahl.
Die UI darf daraus keine Fitness-, Kauf- oder Eignungsaussagen ableiten.

Empfehlung: Späterer Dashboard-Adapter verwendet den bestehenden `run`-Einstieg,
zeigt Empfehlungen und Aktivitätskontext getrennt, wertet Status vor Zahlenanzeige
aus und trennt Nutzer/Freigaben bei Sitzungszustand oder Cache. Das ist eine
Integrationsvorgabe, keine bereits gebaute Oberfläche. Modelle, Rohdaten und
Tagfreigaben unverändert. Kein Training, Commit oder PR.
