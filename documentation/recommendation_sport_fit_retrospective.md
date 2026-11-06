# MOVA – Retrospektive technische Sportpassung der Empfehlungslisten

Stand: 04.11.2026. Ergänzende Auswertung nach beiden Modellierungszyklen und nach der Rekonstruktion des Lab-Logs; kein weiterer Modellierungszyklus. Das Kriterium wurde **nachträglich** formuliert, nachdem die Listen und ihre ursprünglichen Vergleichsergebnisse bereits vorlagen. Es war kein ursprüngliches, prospektiv festgelegtes Geschäfts- oder Erfolgskriterium. Eine spätere wirtschaftliche Prüfung wird dadurch nicht ersetzt.

## 1. Fragestellung und Messdefinition

Untersucht wird, ob die bereits implementierte Sportpriorisierung im vorhandenen synthetischen Bestand mehr regelbasiert passende Angebote in die Top-5-Listen bringt als die vorherige Kategorien-/ID-Auswahl. Es werden ausschließlich gespeicherte Listen ausgewertet. Die Empfehlungsengine wird weder importiert noch geändert; keine Modelle werden geladen, inferiert oder trainiert.

Ein **Empfehlungsslot** ist ein tatsächlich ausgegebenes Angebot in einer gespeicherten Liste eines Nutzers. Dasselbe Angebot bei mehreren Nutzern sind mehrere Slots. Ein Slot gilt als **sportbezogen passend**, wenn mindestens einer der endgültig manuell bestätigten Angebotstags zu einer Sportart gehört, für die derselbe Nutzer im historischen Profil einen Anteil **größer null** hat. Mehrere passende Tags zählen denselben Slot nur einmal. Ein Angebot ohne bestätigten Tag ist nach dieser Definition kein Sportmatch, kann aber als Kategorienangebot zulässig bleiben. Die Kategorie muss separat zu den im gespeicherten Vergleich positiv ausgewählten Interessen gehören.

Für beide Varianten wird **dieselbe endgültige Tagtabelle und dasselbe Profil je Nutzer** verwendet. Gemessen wird nicht die formale frühere A/B-Kennzeichnung. Ohne aktivierte Sporttags waren vorher alle Slots B; das bedeutet nicht, dass kein Angebot bereits sportbezogen passte. Ein Vergleich „0 → 344 passende Slots“ wäre daher falsch. Die neue, symmetrische Nachbewertung ergibt 251 → 344.

Technischer Anteil = passende Slots / alle ausgegebenen Slots × 100. Die Differenz wird in **Prozentpunkten** angegeben. Nutzer mit leeren Listen bleiben Teil der 100 Nutzer, tragen jedoch null Slots und null Matches bei; sie erhalten keinen fiktiven Matchanteil. Nutzerabdeckung = Nutzer mit mindestens einem Match / alle 100 Nutzer. Die unterschiedlichen Nenner werden nicht vermischt.

## 2. Eingabedateien und tatsächliche Formate

| Datei, relativ zum Repository | Umfang | Verwendete Felder / Zweck |
| --- | ---: | --- |
| [Gespeicherter Nutzervergleich](../outputs/tables/recommendation_before_after_users.csv) | 100 Zeilen | `user_id`, `categories`, `eligible_offers`, `count_before`, `count_after`, `top5_before`, `top5_after`, `tier_a_before`, `tier_a_after`; Listen und Kategorien als JSON-Arrays innerhalb von CSV-Feldern |
| [Historische Nutzerprofile](../data/processed/kmeans_user_features.csv) | 100 Zeilen | `user_id`, `avg_activities_per_week`, acht `share_*`-Spalten; unskalierte Sportanteile, keine Clusterzuordnung |
| [Angebotskatalog](../data/raw/offers_simulated.csv) | 30 Zeilen | `offer_id`, `category`, `title`; Preis/Rabatt werden nicht als Ranking-/Matchfaktor verwendet |
| [Endgültige Tagfreigabe](offer_sport_tags_approved.csv) | 8 Zeilen | `offer_id`, `title`, `sport_tags`, `review_status`, `reviewed_by`, `reviewed_at`; nur `manually_confirmed`, mehrere Tags ggf. mit `|` getrennt |

Die Dateien sind UTF-8-CSV mit Komma als Trennzeichen. JSON-Listen müssen mit `json.loads` gelesen werden, nicht durch Aufteilen an Kommas. Der CSV-Reader verwendet `newline=''` und verarbeitet LF beziehungsweise CRLF. Alle vollständigen tatsächlichen Spaltenfolgen und Quellhashes sind im [Auswertungsskript](../src/recommendation_sport_fit.py) festgelegt. Die Ausgabe speichert die Quellhashes zusätzlich als Provenienz.

Der Kategoriennachweis bezieht sich auf die im ursprünglichen Nutzervergleich gespeicherten positiven Kategorien; es werden keine neuen Interessen erhoben. Das Skript prüft diese Grenze gegenüber dem Katalog, liest aber nicht zusätzlich die Nutzer-Rohdatei zur unabhängigen erneuten Interessenprüfung. Die frühere Engine-/Vergleichsvalidierung ist in [recommendation_execution.md](recommendation_execution.md), insbesondere §12, dokumentiert.

## 3. Zeitliche Abgrenzung

Die Profile beschreiben die abgeschlossenen synthetischen Wochen bis zum Demo-Stichtag **05.07.2026**. Es werden keine späteren Aktivitäten oder zukünftigen Zielwerte eingelesen. Der Eingangsbestand ist durch feste Hashes an den vorhandenen V2-Stand gebunden; die zugrunde liegende Wochenherkunft folgt dem vorhandenen Aufbereitungsnachweis.

Die manuelle Tagfreigabe ist vom **31.10.2026**. Sie wird hier ausdrücklich als endgültige Annotation rückblickend auf beide Listen angewendet. Es wird **nicht** behauptet, dass die Freigabetabelle bereits am historischen Beobachtungsstichtag existierte oder diese Auswertung eine damalige Live-Entscheidung reproduziert. Diese Unterscheidung ist bei einer retrospektiv formulierten Metrik notwendig. Die Ergebnisse sind keine Prognose künftiger Nutzerreaktionen.

## 4. Berechnung und Validierung

1. Genau die vier Quell-CSVs lesen; SHA-256 und vollständige Spaltenfolgen prüfen.
2. Eindeutige Schlüssel und dieselben 100 Nutzer im Listen- und Profilbestand sicherstellen.
3. Endgültige Tags anhand Status, Angebotstitel, Sportvokabular, Reviewer und Datum prüfen.
4. Profile auf endliche Anteile 0–1, Anteilssumme ungefähr 1 und verfügbare positive Häufigkeit prüfen; keine Imputation.
5. Kategorien und gespeicherte Listen als eindeutige JSON-Stringarrays lesen. Angebots-IDs, Kandidatenzahl, Listenlänge und positive Kategorien prüfen.
6. Die vorhandene Reihenfolge unabhängig gegen die dokumentierte Kategorien-/ID-Regel vorher bzw. Sportanteil-/ID-Regel nachher kontrollieren. Diese Referenzrechnung dient nur der Validierung; keine neue Liste wird exportiert oder anstelle der gespeicherten Liste gemessen.
7. Für jeden gespeicherten Slot mit derselben finalen Tagzuordnung zählen; formale Tierzahlen als separate Konsistenzprüfung verwenden.
8. Je Nutzer identische Listenlängen sicherstellen, leere Listen berücksichtigen und die gepoolten Anteile sowie Differenzen aus ganzen Zählwerten berechnen. `Decimal` vermeidet unnötige Rundung bei Anteilen; Ausgabe enthält ungerundete numerische Prozentwerte.
9. Neue JSON-Ergebnisdatei anlegen. Eine Wiederholung akzeptiert nur bytegleichen Inhalt; abweichende bestehende Ausgabe wird nicht überschrieben.

## 5. Tatsächlich reproduzierte Ergebnisse

| Kennzahl | Ohne Sportpriorisierung | Mit Sportpriorisierung |
| --- | ---: | ---: |
| Berücksichtigte Nutzer | 100 | 100 |
| Nutzer mit Empfehlungen | 95 | 95 |
| Nutzer ohne Empfehlungen | 5 | 5 |
| Empfehlungsslots | 475 | 475 |
| Sportbezogen passende Slots | 251 | 344 |
| Anteil passender Slots | 52,8421052631579 % | 72,42105263157895 % |
| Nutzer mit mindestens einem Match | 81 | 81 |
| Anteil dieser Nutzer an allen 100 | 81 % | 81 % |
| Kategorienverletzungen | 0 | 0 |

**Differenz:** +93 passende Slots und **+19,57894736842105 Prozentpunkte**. Dies ist keine relative Verbesserung um 19,58 Prozent. Die Nutzerabdeckung steigt nicht. Beim tatsächlich vorhandenen U001 enthält die alte Liste ein Sportmatch und die neue vier; die frühere formale A-Zahl ist dennoch null.

Das **nachträgliche technische Kriterium** lautet: höherer Sportmatchanteil bei unverändert eingehaltenen positiven Kategorien und unveränderten individuellen Listenlängen. Es ist im bestehenden Bestand erfüllt. Eine zusätzliche Schwelle wie „mindestens 70 %“ wird nicht aus dem erreichten Resultat abgeleitet. `prospective_success_threshold` bleibt in der Ergebnisdatei ausdrücklich `null`.

Übereinstimmung mit bestehenden Ergebnissen: 475 Slots je Variante, 344 nachher als A klassifizierte Slots, 81 Nutzer mit einem A-Angebot und fünf leere Nutzerlisten stimmen mit der ursprünglichen Summary überein. Die 251 vorherigen Sportmatches sind eine **neue retrospektive Kennzahl**, kein ersetzter ursprünglicher Tierwert. Die 64 geänderten Listenzusammensetzungen aus dem ursprünglichen Vergleich bleiben unverändert.

## 6. Reproduktion und Tests

Das Skript benötigt ausschließlich Python-Standardbibliothek. Reproduktion vom Repository-Stamm:

```bash
python src/recommendation_sport_fit.py
python -m unittest discover -s tests -p 'test_recommendation_sport_fit.py' -v
```

Ausgabe: [recommendation_sport_fit_retrospective.json](../outputs/tables/recommendation_sport_fit_retrospective.json), mit Definition, Datenstand, Quellenhashes, Skripthash, zeitlicher Einordnung, Gesamtergebnissen und gepaarten Matchzählungen aller 100 Nutzer. Ein Codewechsel führt bewusst zu einem anderen Skripthash; die vorhandene Datei würde dann ohne explizite neue Version nicht überschrieben.

**Zwölf neue Tests bestanden:** bekannte Summen und Prozentrechnung, leere Listen, U001 und Unterschied zwischen Tier und Match, Übereinstimmung mit ursprünglicher Summary, Kategorienverletzung, fehlende/doppelte Nutzer, ungültige Profile, veränderte/duplizierte/unbekannte Listen, JSON-Schema, unbestätigte/falsche Tags, Mehrfachtags ohne Doppelzählung, begrenzter Quellzugriff, Quellhash-/CSV-Schemaprüfung, deterministische Ausgabe und Überschreibschutz. Mehrere Aspekte werden innerhalb einzelner Testmethoden gemeinsam geprüft.

Die Skriptausführung wurde mit identischem Ergebnis wiederholt. Temporäre Negativtests verwenden ausschließlich isolierte Speicherkopien bzw. temporäre Dateien, keine Änderung der Projektquellen. Der abschließende Integritätsvergleich und gegebenenfalls breitere Regressionstests werden unten als tatsächlicher Prüfabschluss festgehalten.

## 7. Wissenschaftliche Reichweite

Die Metrik weist die technische Nutzung einer fachlich begründeten Aktivitätsinformation zur Priorisierung nach. Sie bewertet jedoch mit den Regeln, die bereits das Ranking bestimmen; es handelt sich um interne Regelpassung und nicht um unabhängige externe Relevanzvalidierung. Eine Sportart mit Anteil größer null beweist weder aktuellen Bedarf noch Kaufabsicht. Nicht getaggte Angebote können real hilfreich sein, ohne in dieser Metrik als passend zu zählen. Umfang und Güte der manuellen Annotation beeinflussen den Wert.

Die Daten sind synthetisch; es wurden **keine echten Nutzer befragt**. Weder Zufriedenheit noch Suchzeitersparnis, Klickrate, Conversion, Kaufwahrscheinlichkeit, Umsatz, Provision oder Deckungsbeitrag wurden gemessen. Technische Personalisierung ist damit demonstriert, Geschäftswirkung bleibt eine Hypothese. Für Unternehmen wären künftig unabhängige Relevanzurteile, geeignete Kontrollvergleiche tatsächlicher Nutzung und eine Kosten-/Erlösbetrachtung notwendig. Diese Größen werden nicht erfunden.

Die Auswertung ändert keine Prognosegüte und keine Modellentscheidung aus Zyklus 2. Eine nachträgliche Kennzahl kann das fehlende ursprünglich vereinbarte geschäftliche Nutzenkriterium nicht rückwirkend ersetzen. Sie ergänzt lediglich die transparente Bewertung des vorhandenen Demonstrators.

## 8. Tatsächlicher Prüfabschluss

- Zwölf neue Tests bestanden; zwei vollständige Skriptläufe ergaben bytegleiche Ergebnisdateien. Die automatisierten Tests prüfen die Bytegleichheit zusätzlich im Speicher.
- Breiter Lauf `test_recommendation*.py`: zunächst 54 Tests, davon ein Fehlschlag im alten `test_original_tracked_files_unchanged`. Dieser verlangt alle HEAD-Dateien unverändert und beanstandete die ausdrücklich autorisierte Änderung am Lab-Log-Entwurf. Es war kein fehlerhaftes Empfehlungsergebnis.
- Erneuter Lauf mit genau diesem alten Test zur Laufzeit als nicht anwendbar markiert: **53 bestanden, 1 übersprungen** (54 entdeckt), darunter die zwölf neuen Tests. Keine bestehende Testdatei verändert. Während beider breiteren Läufe waren `LinearRegression.fit`, `KMeans.fit` und `StandardScaler.fit` durch Fehler auslösende Sperren ersetzt. Die übrigen 41 bestehenden Empfehlungstests bestanden.
- Ersatz für den pauschalen Alt-Test: SHA-256 aller 240 zu Arbeitsbeginn versionierten Dateien verglichen. Ausschließlich die drei beauftragten Dokumente (Entwurf, Nachweismatrix, Qualitätscheck) sind verändert. Daten, Engine, Modelle, Grafikdateien, bisherige Ergebnisse und bestehende Tests sind unverändert.
- 145 relative Verweise der vier neuen/geänderten fachlichen Dokumente auf vorhandene Ziele geprüft; alle im Entwurf verwendeten E-IDs auflösbar.
- `git diff --check` ohne Befund. Keine Dateien vorgemerkt, kein Commit, Push oder PR. Branch weiterhin `feature/final-lab-log`.

Die drei neu dokumentierten Matchwerte (vorher 251, Differenz 93, Differenz 19,58 Prozentpunkte) stammen aus der nachträglichen Analyse und werden nicht als historische Summaryfelder ausgegeben. Die fachliche Lücke eines prospektiven geschäftlichen Nutzenkriteriums bleibt bestehen. Reale Relevanz- und Wirtschaftlichkeitsmessungen sind weiterhin offen.
