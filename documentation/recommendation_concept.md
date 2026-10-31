# MOVA – AP 6.1: Technisches Empfehlungskonzept

Stand: 31.10.2026. Aktive synthetische V2. Worktree `/workspace/MOVA-AP6`,
Branch `ap6-recommendations`, Basis `a8f97ad75c378329a614a322bd541f372de0b072`.
Nur Konzeption; Umsetzung und gemeinsame Freigabe folgen in AP 6.2.

Kennzeichnung: **Fakt** = in vorhandenen Dateien nachgesehen;
**Entscheidung** = Vorgabe dieses Auftrags; **Vorschlag** = noch abzustimmen.
Nicht belegte Annahmen werden ausdrücklich benannt, nicht als Daten verwendet.

## 1. Ziel

**Entscheidung:** Einfaches, deterministisches Regelwerk für passende Angebote aus
30 fiktiven Katalogeinträgen. Die Regeln sollen später einzeln im Dashboard erklärbar
sein. Kein weiteres ML-Modell, keine gewichtete Gesamtformel und kein 0–100-Score.
Die praktische Verwendung bestehender Datenaufbereitung und Modelle wird sichtbar;
ein nachgewiesener Empfehlungsnutzen wird dadurch nicht behauptet.

## 2. Daten und Voraussetzungen

**Fakt:** Die vier CSV-Dateien wurden tatsächlich gelesen; alle Nutzerdateien
enthalten 100 Zeilen, der Katalog 30. In diesen Dateien gibt es keine Leerfelder.
UTF-8, Kommatrennung, Dezimalpunkt; CSV-Typen sind logisch aus Werten abgeleitet.

| Datei | Tatsächliche Spalten / Formate |
| --- | --- |
| `data/raw/users_simulated.csv` | `user_id` Text; `interest_sport`, `interest_outdoor`, `interest_wellness`, `interest_leisure`: True/False |
| `data/raw/offers_simulated.csv` | `offer_id`, `category`, `title`: Text; `price_eur`: Dezimalzahl; `discount_pct`: Ganzzahl |
| `data/processed/user_clusters.csv` | `user_id`: Text; `cluster_id`: Ganzzahl 0/1; `segment_label`: Text |
| `data/processed/kmeans_user_features.csv` | `user_id`; `avg_activities_per_week`; `share_running`, `share_cycling`, `share_strength`, `share_swimming`, `share_walking`, `share_hiking`, `share_tennis`, `share_padel`; `avg_duration_per_week`; `sport_diversity` |

Im letzten Datensatz sind Häufigkeit, Anteile und Minuten Dezimalzahlen, Vielfalt
eine Ganzzahl. Das Profil beschreibt 26 vollständige Wochen, 05.01.–05.07.2026;
die acht Anteile sind unskaliert und summieren sich je aktivem V2-Nutzer auf 1.
Zusätzlich werden später `data/processed/user_weekly_activities.csv` und das
gespeicherte Regressionspaket benötigt. Keine neuen Rohspalten werden vorausgesetzt.

**Vorschlag:** IDs und referenzielle Integrität beim Laden prüfen; doppelte IDs,
unbekannte Kategorien und widersprüchliche Joins melden. Booleanwerte strikt parsen:
der Text `False` darf nicht durch allgemeine String-Wahrheitsprüfung zu True werden.
Ungültige Interessenfelder nicht stillschweigend ergänzen.

## 3. Interessenbasierte Vorauswahl

**Entscheidung:** Nur positiv ausgewählte Kategorien sind personalisierte Kandidaten:

| Interessenfeld | Kategorie |
| --- | --- |
| interest_sport | Sport |
| interest_outdoor | Outdoor |
| interest_wellness | Wellness |
| interest_leisure | Freizeit |

False bedeutet nur nicht positiv ausgewählt, kein belegtes ausdrückliches
Desinteresse. Ohne True keine personalisierten Ergebnisse; separater allgemeiner
Katalog möglich. Das betrifft tatsächlich U023, U032, U059, U087 und U094.
Sporthistorie, Cluster, Preis oder Prognose dürfen diese Vorauswahl nicht umgehen.

## 4. Sportartenbezogenes Matching und manuelle Prüfung

**Vorschlag:** `offer_sport_mapping_review.csv` enthält für alle 30 tatsächlichen
Angebote unveränderte Kennung, Kategorie und Titel, einen Tagvorschlag, Titelbeleg
und Prüfstatus. Tags verwenden ausschließlich Running, Cycling, Strength, Swimming,
Walking, Hiking, Tennis und Padel; mehrere spätere Tags wären mit `|` getrennt.
Leeres Tagfeld bedeutet keine vorgeschlagene Zuordnung, keine fehlende CSV-Zeile.

| Prüfergebnis | Anzahl | Angebote |
| --- | --- | --- |
| Eindeutiger Titelbezug vorgeschlagen | 8 | O001 Running; O003 Swimming; O004 Tennis; O005 Padel; O006 Cycling; O007 Strength; O009/O010 Hiking |
| Mehrdeutig, ohne Tag | 2 | O002 Fitnesskurs; O011 Trekkingstöcke |
| Kein zuordenbarer Bezug zu den acht Sportarten | 20 | Übrige Titel |

Hantelset bezeichnet Krafttrainingsausrüstung, daher Vorschlag Strength. Ein
Fitnesskurs legt dagegen keine der acht Sportarten fest. Trekkingstöcke lassen
Hiking/Walking offen. Regenjacke, Zelt und Outdoor-Messe benennen keine eindeutige
Sportart. Yoga und Klettern sind keine der acht vorhandenen Sportarten und werden
nicht in Strength umgedeutet. Stadtführung wird nicht automatisch Walking.

**Entscheidung:** Alle CSV-Status enden auf `pending_review`; auch eindeutige
Vorschläge sind noch nicht bestätigt. Keine Zeile ist derzeit Matching-Grundlage.
Vor AP 6.2 muss eine manuelle Freigabe einzelne Tags bestätigen oder ablehnen und
nachvollziehbar dokumentieren. Bis dahin ist nur die Kategorienlogik freigabefähig.
Nicht belegte Annahmen zu Schwierigkeit, Ort, Termin oder Anforderungen entfallen.

## 5. Rankinglogik

**Entscheidung:** Vorauswahl zuerst, danach zwei Stufen:

- A: mindestens ein manuell bestätigter Sporttag mit gültigem historischem Anteil >0.
- B: alle übrigen Angebote aus positiv ausgewählten Kategorien.

B bleibt grundsätzlich empfehlbar. Ohne bestätigte Tags oder ohne zulässiges
Sportprofil liegen alle Kandidaten in B. Nullanteile schließen Angebote nicht aus.
Die Stufen sind eine explizite Bevorzugung nach belegtem Sportbezug, kein Nachweis,
dass Angebote ohne Sportbezug weniger nützlich sind. Keine weiteren Abzüge für B.

**Vorschlag:** Innerhalb A kann der höchste Anteil der tatsächlich positiv
beobachteten bestätigten Angebotstags absteigend sortieren. Bei genau einem Tag ist
dies unmittelbar dessen Anteil. Maximum vermeidet eine automatische Bevorzugung
von Angeboten nur wegen vieler Tags; diese Mehrfach-Tag-Regel bleibt offen.
Der Anteil ist ein beobachteter Sortierschlüssel, kein Match-Score und keine
Kaufwahrscheinlichkeit. Alternative vorerst: innerhalb A ausschließlich offer_id.

Innerhalb B sowie bei Gleichstand in A: offer_id aufsteigend (O001–O030), ohne
Zufall. Kein Einfluss von Preis, Rabatt, Cluster oder Prognose. Keine erfundenen
Gewichte. Zunächst alle Kandidaten ordnen; eine spätere Top-N-Anzeige ist offen.

## 6. K-Means als getrennte Dashboard-Information

**Fakt:** k=2; 57 Nutzer mit „Geringere Trainingshäufigkeit“, 43 mit „Höhere
Trainingshäufigkeit“. Neun Eingänge: Häufigkeit plus acht standardisierte und
gewichtete Anteile. Minuten und Vielfalt sind beschreibend.

**Entscheidung:** Für den ausgewählten V2-Nutzer vorhandenes Label aus
`user_clusters.csv` abrufen, keinen neuen Fit und keine neue Clusterberechnung.
Mapping gegen `outputs/models/kmeans_final_metadata.json` prüfen. Anzeigevorschlag:
„Aktivitätssegment (synthetische 26-Wochen-Historie)“ mit Zeitraum und Hinweis auf
relative Trainingshäufigkeit. Keine Fitness-, Gesundheits- oder Erfahrungswertung.
Kein Rankingkriterium. Fehlende Zuordnung verhindert Interessenempfehlungen nicht.
Bei späterer neuer Zuordnung gilt unverändert `kmeans_inference_contract.md`.

## 7. Regression als getrennte Dashboard-Information

**Fakt:** `outputs/models/regression_linear.joblib` mit zugehörigen
`regression_linear_metadata.json`; globales Modell, keine Skalierung. Reihenfolge:
`activities_current_week`, `avg_activities_last_4_weeks`. Gemäß Metadaten:

ŷ(t+1) = 0,8397931020190079 + 0,22819007785063997 × c(t)
         + 0,42396047869339204 × mean(c(t−3), c(t−2), c(t−1), c(t)).

**Vorschlag für spätere Berechnung:** Nutzer und abgeschlossene Woche t explizit
wählen; aus `user_weekly_activities.csv` dessen vier lückenlos vollständige,
verlässliche Montag–Sonntag-Wochen t−3…t laden, nach Datum prüfen, nicht bloß vier
beliebige Zeilen nehmen. `activities_count` muss endlich, nichtnegativ und
ganzzahlig sein. Mittel einschließlich t bilden; Eingaben in exakter Modellreihenfolge
an das hashgeprüfte gespeicherte Modell übergeben. Nur `predict`, niemals Fit.
Keine Cluster, Interessen oder Folgezielwerte als Eingänge; keine neue Skalierung.

Konkreter späterer V2-Stichtag: t=26 endet am 05.07.2026, Fenster Wochen 23–26,
Ziel 06.–12.07.2026. Das ist ein historischer Demo-Ausblick, keine Prognose für die
heutige Kalenderwoche. `regression_weekly_features.csv` endet wegen benötigtem
Folgeziel bei Eingabewoche 25; für t=26 daher das vollständige Wochenraster nutzen.
Für andere Stichtage nur zum jeweiligen Zeitpunkt bekannte Wochen verwenden.

**Entscheidung:** Ergebnis separat als unverbindliche geschätzte Aktivitätszahl
anzeigen, mit Stichtag, Zielwoche und synthetischer Herkunft. Keine Fitness- oder
Kaufwahrscheinlichkeit, kein Rankinggewicht, keine individuellen Versprechen.
Rechenwert unverändert speichern; keine Rundung zum Modellinput oder automatische
Kappung. Eventuelle Anzeigerundung ist eine offene UI-Frage.

**Fakt:** AP-5-MAE rund 1,49 gegenüber Persistenz 1,71; bei zukünftigen Nullwochen
war das Modell rund 36 % schlechter nach MAE. Vier Testwochen derselben synthetischen
Nutzer belegen keine reale Generalisierung und liefern kein individuelles
Unsicherheitsintervall. Fehlende Regressionseignung getrennt von K-Means behandeln:
vier Wochen können ausreichen, auch wenn 26 Wochen für K-Means fehlen.

## 8. Technischer Datenfluss (erst später auszuführen)

| Schritt | Quelle und Ergebnis |
| --- | --- |
| 1 Nutzer wählen | user_id aus users_simulated.csv; eindeutige Existenz prüfen |
| 2 Zulässigkeit prüfen | separate simulierte Laufzeitfreigaben aus Abschnitt 10 |
| 3 Interessen laden | vier True/False-Felder; Kategorienmenge bilden |
| 4 Sportprofil optional laden | kmeans_user_features.csv; unskalierte acht Anteile nur bei zulässiger, valider Historie |
| 5 Segment optional abrufen | user_clusters.csv plus Metadaten-Mapping; bestehendes Ergebnis, keine Inferenz |
| 6 Prognose optional berechnen | Wochenraster, Regressionsmodell und Metadaten; neue Inferenz aus genau zwei zulässigen Merkmalen |
| 7 Angebote filtern | offers_simulated.csv; nur positive Interessenkategorien |
| 8 Sportbezug berücksichtigen | ausschließlich separat manuell bestätigtes Mapping; aktuelle Review-CSV reicht nicht |
| 9 Ordnen und erklären | Stufen A/B, freigegebener Sortierschlüssel, offer_id; regelbasierte Auswahl |

Die Empfehlungsfunktion erhält zulässigen Kontext; sie trainiert oder betreibt
selbst keine ML-Modelle. Gespeicherte Clusterlabels, später neu berechnete
Regressionsprognosen und regelbasierte Angebote behalten getrennte Herkunft.

## 9. Fallback-Regeln

| Fall | Vorgesehenes Verhalten |
| --- | --- |
| Keine positive Kategorie | Keine personalisierten Angebote; allgemeiner Katalog getrennt |
| Interessen fehlen/ungültig | Keine Interessen erfinden; Personalisierung aussetzen, Angabe/Validierung ermöglichen |
| Keine zulässige Sporthistorie | Nur zulässige Interessen nutzen; alle Kandidaten B |
| Vollständig inaktiv bei verlässlicher Historie | Anteile undefiniert lassen; kein reguläres Cluster; Interessenweg möglich |
| Fehlendes/ungültiges Cluster | Segment null mit Status; Kategorienweg bleibt möglich |
| Weniger als vier vollständige Wochen | Prognose null mit Grund; kein Auffüllen |
| Vier bestätigte Nullwochen | Regression technisch zulässig; positiver Intercept ist keine garantierte Aktivität |
| Unbekannte Sportarten | Sportprofil nicht durch stilles Entfernen/Umdeuten reparieren; Clustervertrag sperrt Zuordnung |
| Ungültige Zahlen/Anteilssumme | Betroffenen Profil-/Modellpfad sperren, zulässigen Interessenweg erhalten |
| Kein bestätigter Angebotstag | Angebot bleibt B, sofern Kategorie positiv |

Bei unbekannten Sportarten ist eine Gesamtzählung für Regression nur nach separater
fachlicher Klärung des Aktivitätsumfangs zulässig; bis dahin Prognose aussetzen.
Clusterstatus gemäß vorhandenem Vertrag verwenden; keine künstliche Zuordnung.

## 10. Datenschutz und simulierte Freigabe

**Fakt:** Die CSV-Dateien dokumentieren keine Einwilligung. Interessen sind kein
Einwilligungsnachweis. Synthetische Aktivitäten sind keine echten Garmin-Importe.

**Vorschlag:** Später zwei getrennte, standardmäßig nicht bestätigte Demo-Freigaben
im Laufzeitkontext, ohne bestehende CSVs zu erweitern:
`simulated_interest_release` und `simulated_garmin_release` (Boolean).
Kennzeichnung: „Simulierte Freigabe für diese Demonstration, keine reale Einwilligung“.
Je ausgewähltem Nutzer und Sitzung prüfen; bei Nutzerwechsel zurücksetzen. Fehlend
ist nicht freigegeben. Rücknahme entfernt die betreffenden abgeleiteten Anzeigen.

Ohne Garmin-Freigabe weder Sportanteile zur Personalisierung nutzen noch
aktivitätsbasierte Segmente/Prognosen für den ausgewählten Nutzer bereitstellen.
Ohne Interessenfreigabe keine personalisierten Angebote. Bei Interessenfreigabe
und fehlender Garmin-Freigabe ist ausschließlich der Interessenweg möglich.
Allgemeiner Katalog bleibt separat unpersonalisiert. Keine echte Einwilligung,
Garmin-Anbindung oder rechtliche Zulässigkeit wird durch den Demo-Schritt behauptet.

## 11. Vorgesehenes Ausgabeformat

**Vorschlag:** Ein Python-Dictionary mit `user_id`, `personalization_status`,
`recommendations` (Liste), `kmeans_context` und `regression_context`.
Dies sind künftige Ausgabefelder, keine behaupteten bestehenden Datenspalten.

Jeder Empfehlungsdatensatz enthält mindestens:

| Feld | Typ / Inhalt |
| --- | --- |
| user_id | Text, ausgewählter Nutzer |
| offer_id | Text aus Katalog |
| offer_title | Text, unveränderter Katalogtitel |
| category | Text aus Katalog |
| match_reason | Text: positive Kategorie; bei A zusätzlich bestätigter Tag und beobachteter Anteil |
| ranking_position | Ganzzahl ab 1, nach endgültiger Sortierung |

Optional `ranking_stage` A/B zur Prüfung. Keine Gründe aus Segment oder Prognose.
Bei leerem Ergebnis leere Liste und erklärender Status, keine erfundenen Angebote.
`kmeans_context`: Status, nullable cluster_id/segment_label, Herkunft gespeicherte
Zuordnung und Beobachtungszeitraum. `regression_context`: Status, nullable
predicted_activities, Eingabewoche, vierwöchiges Fenster, Zielwoche, Modellherkunft
und Hinweis auf synthetische Evaluation. Nicht berechnet/gesperrt wird null mit
Grund ausgegeben; keine 0 als Ersatz. Kontexte werden nicht je Angebot dupliziert.

## 12. Geplante technische Testszenarien

Keine Tests ausgeführt, die Empfehlungen berechnen. Folgende Fälle sind ein
Abnahmeplan. Fehlersituationen sind geplante Tests mit Laufzeiteingaben oder
Test-Doubles, keine Änderungen an V2. Ein bestätigter Angebotstag in einem
Testszenario ist eine ausdrückliche Testvoraussetzung, keine Freigabe der Review-CSV.

| Fall / Ausgangsdaten | Erwartetes Verhalten | Regel |
| --- | --- | --- |
| U001: Sportinteresse True, share_running >0; beide Freigaben; O001-Tag im Test bestätigt | O001 innerhalb zulässiger Kategorien in A, Erklärung nennt Running; keine Ergebnisliste hier berechnet | Vorauswahl + Sportbezug |
| U003: Wellness True; O017 Saunatag ohne Tag; Interessenfreigabe | O017 bleibt B und grundsätzlich empfehlbar | Kein Sporttag erforderlich |
| U001: mehrere True-Kategorien | Vereinigte Kategorien, jede offer_id höchstens einmal; übrige Kategorien ausgeschlossen | Mehrfachinteressen |
| U023: alle Interessen False | Leere personalisierte Liste, separater allgemeiner Katalog möglich | Kein True |
| Auswahl eines vorhandenen Nutzers, Clusterlookup im Test ohne Ergebnis, Interessenfreigabe | Interessenweg bleibt möglich, Segment null mit Grund | Unabhängigkeit vom Cluster |
| O008 Sportfestival ohne eindeutigen Tag, Kategorie Sport positiv | B, keine erfundene Sportart oder Zusatzabwertung | Ungetaggtes Angebot |
| U001, Interessenfreigabe ja, Garmin-Freigabe fehlt | Nur B nach Kategorien; Sportprofil, Segment und Prognose gesperrt | Simulierte Freigabe |
| Garmin-Freigabe ja, Interessenfreigabe fehlt | Keine personalisierten Angebote | Getrennte Zulässigkeit |
| Historie nur vier vollständige verlässliche Wochen, gültige Counts | Kein reguläres K-Means-Segment; Regression separat möglich | Getrennte Historienverträge |
| Nachgewiesene 26-Wochen-Inaktivität als Test-Duble | Kein Cluster, undefinierte Sportanteile; Interessenweg; Regression separat prüfen | Keine künstlichen Präferenzen |
| Woche fehlt oder laufende Woche im Viererfenster | Keine Prognose, kein Nullersatz | Regressionseignung |
| Unbekannte Sportart oder NaN/negative Anteile/Anteilssumme ungleich 1 | Betroffenen Pfad sperren; kein stilles Umdeuten/Imputieren | Eingabevalidierung |
| O001-Tag steht weiterhin auf pending_review | Keine Stufe A aufgrund dieser CSV | Manuelle Freigabe |
| Gleichrangige Kandidaten, Eingangszeilen unterschiedlich sortiert | Identische Reihenfolge nach offer_id | Reproduzierbarkeit |

## 13. Grenzen und Einordnung

Keine Empfehlungsqualität, Kaufabsicht oder Umsatzwirkung nachgewiesen. Titelmapping
ist fachliche Interpretation, keine beobachtete Nutzer-Angebot-Beziehung. Angebote
haben keine strukturierten Orts-, Termin-, Verfügbarkeits- oder Anforderungsmerkmale.
Historische Häufigkeit ist kein erklärter Wunsch; null kein Desinteresse. Die
Stufenentscheidung ist einfach erklärbar, aber noch nicht empirisch validiert.
26-Wochen-Profile dürfen nicht mit Zukunftsinformation in frühere Evaluationen
eingehen. Keine neue CRISP-DM-Iteration oder Evaluation wird behauptet.

Quellen: `kmeans_inference_contract.md`, `modeling_evaluation.md`,
`regression_modeling_execution.md`, `data_dictionary.md`, aktive V2-Dateien und
Modellmetadaten. Historische Planungsformulierungen ersetzen keine Artefaktprüfung.

## 14. Offene Entscheidungen vor AP 6.2

1. Acht eindeutige Tagvorschläge manuell bestätigen/ablehnen; zwei mehrdeutige Fälle
   klären oder ungetaggt lassen; Freigabeformat und Verantwortlichkeit festlegen.
2. Innerhalb A Sportanteil oder nur offer_id? Bei mehreren bestätigten Tags den
   vorgeschlagenen Maximalanteil ausdrücklich bestätigen oder zunächst ausschließen.
3. Demo-Freigaben, Rücknahme und unabhängigen Interessenweg gemeinsam abnehmen.
4. Zulässigkeitsanforderungen für Sportprofile bestätigen: vorgeschlagen zunächst
   geprüfte vollständige V2-26-Wochen-Profile; keine verkürzten Profile erfinden.
5. Ausgabeanzahl/Top-N und spätere Prognose-Anzeige abstimmen. Fachlichen Nutzen
   anhand nachvollziehbarer Fälle prüfen; noch kein Erfolgsmaß als erreicht behaupten.

AP 6.1 endet mit diesem Konzept und einer nicht freigegebenen Review-Tabelle.
Keine Empfehlungsimplementierung, Prognosen, Scores, Trainingsläufe, UI, Commits
oder PRs in diesem Arbeitsschritt.
