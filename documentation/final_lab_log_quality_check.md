# MOVA – Vollständiger Qualitätsabgleich mit den Originalvorgaben für LN B

**Neue Rekonstruktion; aktualisiert am 04.11.2026 nach Eingang der Original-PDFs.** Prüfgegenstand ist [final_lab_log_draft.md](final_lab_log_draft.md) samt [Nachweismatrix](final_lab_log_evidence.md), [offenen Punkten](final_lab_log_open_items.md), [KI-Audit](ai_missteps_audit.md) und vorhandenen Projektartefakten. Referenz des vorhandenen Repositorybestands: `7282cef20cdcc871ff78b2c9e879b98cd880f4f5`. Keine Note, kein bestätigter Abgabestatus und keine Zusage einer sehr guten Bewertung.

## 1. Verbindliche Originalquellen und Geltungsbereich

Beide vollständig gelesenen PDFs haben jeweils eine Seite. Der Bewertungsbogen wurde zusätzlich als gerenderte Seite kontrolliert, damit Spalten, Gewichte, Fußnoten und K.-o.-Zeile nicht allein aus einer Textauslese interpretiert werden.

| Kürzel | Originaldokument | Verwendeter Bereich | SHA-256 der hochgeladenen Datei |
| --- | --- | --- | --- |
| R | „Rahmen und Ablauf der Leistungsnachweise – Big Data Analytics“, Dateiname `Bewertungsboegen4_LN_Rahmen und Ablauf.pdf`, S. 1 | LN B vollständig; gemeinsame Regeln, soweit sie für LN B gelten; LN-B-Zeilen der Fragenvorlage | `cddadad901004d8c133a97960769046ff3de8bd6922aa2a9e442964ee0c63aa0` |
| B | „Bewertungsbogen LN B – Datenanalyseprojekt“, Dateiname `Bewertungsboegen2_LN_Datenanalyseprojekt.pdf`, S. 1 | Rahmen, alle zehn Teilkompetenzen einschließlich Unterkriterien und aller Stufen, Fragenmaßstab, fünf K.-o.-Kriterien, Ergebnis- und Fußnotenregeln | `948d7c7a53493c041b9ec5caae8f70462d923b72ce627ed19e2c03c734694495` |

Die PDFs sind Uploadquellen dieser Sitzung und noch nicht als dauerhafte Abgabequellen im Repository abgelegt. Ihre Identität ist durch Dateiname und Hash dokumentiert. Die Gültigkeit der konkreten Prüfungsfassung und die individuelle Abgabefrist sind vom Team zu bestätigen. **Keine LN-A-/LN-C-Vorgaben übernommen:** keine acht Folien als Grenze, keine HTML-Ein-Datei-Pflicht, keine Szenariokarte, keine Plenumskontrollfragen, keine LN-A-Handrechnungspflicht, keine auf einen Teilzyklus reduzierte LN-C-Ausnahme und kein LN-C-Zeitprotokoll.

## 2. Statuslogik und Bewertungsgrenzen

- **ERFÜLLT:** Der bezeichnete schriftliche Teilaspekt ist im aktuellen Entwurf bzw. durch vorhandene Artefakte konkret nachgewiesen. Das belegt noch keine mündliche Leistung oder fristgerechte Abgabe.
- **TEILWEISE ERFÜLLT:** Substanz vorhanden, aber mindestens ein Unteraspekt, Primärbeleg oder Abgabeformat fehlt.
- **OFFEN:** Kein ausreichender Nachweis bzw. nur eine zukünftige Prüfung möglich.

Die Überprüfung trennt fachliche Begründung und Bewertungsabgleich. Nullwochenmerkmal, zeitlicher Split und Verwerfung werden im Entwurf aus der Daten-/Prognosefrage begründet. Die Originalkriterien dienen hier dazu, Lücken zu finden; sie sind keine nachträgliche fachliche Ursache einer bereits getroffenen Entscheidung. Aus fehlendem Nachweis wird nicht automatisch geschlossen, eine Handlung habe nie stattgefunden.

## 3. Rahmen, Ablauf, Formalia und Abgabe – Einzelprüfung

| ID | Originalanforderung | Konkreter Stand / Nachweis | Status | Noch erforderlich |
| --- | --- | --- | --- | --- |
| R01 | LN B als Zweierteam | Entwurf §1.2 nennt Hanna und Patricia und gemeinsame Bearbeitung | ERFÜLLT | Vollständige Namen und Matrikelnummern für Abgabedeckblatt ergänzen |
| R02 | Selbst gewählte Fragestellung | Entwurf §1.1–2: Aktivitätsanalyse, Prognose und Angebote | ERFÜLLT | Keine künstliche Ergebnisfrage nachschieben |
| R03 | Selbst gewählter Datensatz; öffentlich oder freigegeben | Entwurf §3.1 und Anhang A.1: synthetische V2, Generator, Manifeste | TEILWEISE ERFÜLLT | Dozentenzustimmung zur synthetischen Datengrundlage dokumentieren; eigene Generierung ersetzt keine externe Quellenangabe |
| R04 | Richtwert 500–50.000 Zeilen | 6.465 aktive Aktivitätszeilen; weitere Modelltabellen transparent anders aggregiert | ERFÜLLT | Richtwert ist keine Forderung, jede Tabelle müsse mindestens 500 Zeilen haben |
| R05 | Keine personenbezogenen Daten ohne Freigabe | Aktive Modell-/Angebotsdaten synthetisch; Garmin nur Strukturreferenz laut Konzept | TEILWEISE ERFÜLLT | Finales Abgabepaket auf nicht versehentlich enthaltene persönliche Referenzdaten prüfen; ggf. Freigabe klären |
| R06 | Problemstellung und Datensatz vorab beim Dozenten angemeldet | Keine Anmeldung im geprüften Bestand | OFFEN | Vorhandene Bestätigung/Datum nachreichen; nicht rückwirkend behaupten |
| R07 | Iterativ-inkrementell nach CRISP-DM | Entwurf §§2–13; Datenrücksprung und zweite Hypothese | ERFÜLLT | Live nachvollziehbar erklären |
| R08 | Mindestens zwei vollständige Zyklen | Zyklus 1 §§2–7, Zyklus 2 §§9–13; beide mit Modellierung/Evaluation | ERFÜLLT | Nicht nur sechs Fits oder Generatorvarianten als Zyklen zählen |
| R09 | Werkzeug frei | Python, Streamlit; vorhandener Code und Anhang A | ERFÜLLT | Keine zusätzliche Werkzeugpflicht aus LN A ableiten |
| R10 | Lab-Log als PDF oder Web-App | Aktuell Markdown; Lab zeigt Ergebnisse, ersetzt nicht automatisch vollständiges Lab-Log | TEILWEISE ERFÜLLT | Finale PDF-Fassung oder vollständige zugängliche Lab-Log-Web-App bereitstellen |
| R11 | Keine feste Seitenvorgabe; Richtwert 6–12 Seiten-Äquivalent | Entwurf Anhang B korrigiert vorherigen Teamzielumfang 12–15 Seiten; Haupttext ca. 5.390 Wörter nach einfacher Wortzählung | TEILWEISE ERFÜLLT | Satz/Lesedauer prüfen, Hauptfassung ggf. straffen; Anhänge auslagern. Kein K.-o. allein wegen Überschreitung des Richtwerts behaupten |
| R12 | Chronologisch entlang aller sechs Phasen je Zyklus | Datumsrahmen und vollständige Phasen im Entwurf; DU/DP in Zyklus 2 durch Unterkapitel 10.1/10.2 getrennt erläutert | ERFÜLLT | Phasen bei der finalen PDF-Navigation klar beibehalten |
| R13 | Entscheidungen und Begründungen | Fenster, Gewichtung, Split, Modellwahl, Baseline, UND-Regel mit Problem/Alternative/Kontrolle/Folge | ERFÜLLT | Keine hypothetischen Alternativen als getestet ausgeben |
| R14 | Verworfene Wege | Größere k gegen k=2; Zusatzmerkmal verworfen; abgelehnte Zukunfts-/Zufallssplitregeln als methodische Ausschlüsse | ERFÜLLT | Empfehlungszyklus als Entstehungsgeschichte noch primär belegen |
| R15 | Beiträge beider Teammitglieder | §1.2: gemeinsame Arbeit, keine klassische Trennung; Videoorganisation separat | TEILWEISE ERFÜLLT | Team bestätigt konkrete gemeinsame Entscheidungs-/Prüfbeispiele; keine erfundenen Einzelrollen |
| R16 | KI-Irrwege und deren Prüfung im Lab-Log | §14 und Audit K1–K8; technische Ereignisse von KI-Zuschreibung getrennt | TEILWEISE ERFÜLLT | Ursprüngliche KI-Vorschläge und Reaktionen archivieren; K5-Originalchat fehlt |
| R17 | Vortrag 15 Minuten | Historische Video-/Demoanleitung vorhanden; keine finale Live-Probe belegt | OFFEN | Live-Vortrag planen und stoppen; Video ist ohne ausdrückliche Freigabe kein Ersatz |
| R18 | Höchstens zwölf Inhaltsfolien | Kein finaler Foliensatz vorliegend | OFFEN | Inhaltsfolien zählen und finalen Satz bereitstellen |
| R19 | Unterhaltsam, aussagekräftig; Frage→Irrwege→Erkenntnis | Entwurf hat Erzählbogen; Grafiken vorhanden | TEILWEISE ERFÜLLT | Folien, Dramaturgie, Publikumsaktivierung und freie Erzählung praktisch proben |
| R20 | Empfehlung mit Grenzen | §15; bisheriges Modell, reale Wirkung offen, nächste unabhängige Prüfung | ERFÜLLT | In Folien als eine Kernbotschaft verdichten |
| R21 | Lab-Log abgeben | Nur lokaler Entwurf, keine finale Einreichung | OFFEN | PDF/Web-App finalisieren und Moodle-Einreichung belegen |
| R22 | Code/Workflow abgeben | Versionierter Code vorhanden | TEILWEISE ERFÜLLT | Vollständigen erreichbaren Referenzstand im Paket/Link nennen, nicht nur Screenshots |
| R23 | Daten oder Datenlink abgeben | Synthetische Daten versioniert und in Anhang A verlinkt | TEILWEISE ERFÜLLT | Zugriff für Prüfer auf privates Repo bzw. mitgelieferte CSVs sicherstellen |
| R24 | Folien abgeben | Nicht vorhanden | OFFEN | Endgültige Folien bereitstellen |
| R25 | Alle Unterlagen vor Termin über Moodle; Frist separat bekannt | Keine Frist-/Abgabebestätigung vorliegend | OFFEN | Frist erfragen/übernehmen, Paket vor Termin einreichen |
| R26 | Bearbeitungszeit 2–3 Wochen; Aufwand ca. 30 h je Person, Teilrichtwerte je 10 h | Dokumentierte Repochronologie 29.10.–04.11.; tatsächlicher persönlicher Beginn/Aufwand unbekannt | OFFEN | Tatsächliche Angaben bestätigen. Richtwerte sind kein Anlass, Arbeitszeiten zu erfinden; kürzere Commitspanne beweist keinen Regelverstoß |
| R27 | 5 Minuten Fragenrunde | Noch keine Probe/Prüfung | OFFEN | Fragenwechsel und Antworten vorbereiten |
| R28 | Drei Fragetypen: Methode, Live-Nachweis, Entscheidung/Transfer | Inhalte für alle drei vorhanden; Check §7 konkretisiert Vorbereitung | TEILWEISE ERFÜLLT | Beide Autorinnen praktisch mit fremdem Präsentationsteil prüfen |
| R29 | Fragen gezielt an Teammitglied, das betreffenden Teil nicht präsentiert hat | Gemeinsamkeitskonzept unterstützt Verständnis, beweist es nicht | OFFEN | Cross-Teaching-Probe und spätere Live-Leistung |
| R30 | Gemeinsame Note; abweichende Einzelnote bei offensichtlich ungleicher Beteiligung begründen | Teamarbeit im Entwurf offengelegt; tatsächliche Vortragsteile fehlen | TEILWEISE ERFÜLLT | Gleichwertige sichtbare Beteiligung im Vortrag sicherstellen |
| R31 | KI uneingeschränkt, allgemeiner Nutzungsnachweis nicht erforderlich | §14.1 korrekt eingeordnet | ERFÜLLT | Nicht mit der gesonderten Pflicht zu reflektierten KI-Irrwegen verwechseln |
| R32 | 1,0 erfordert eigenes tiefes Verständnis in Live-Situation; fehlerfreie Reproduktion = 2,0 | Im Entwurf und diesem Check ausdrücklich getrennt | OFFEN | Nachweis ist nur in Probe/Prüfung, nicht durch längeren Text möglich |
| R33 | Bewertungsbogenfelder Team, Projekt/Datensatz, Datum; gelbe Felder ausfüllen | Team nur Vornamen, MOVA und V2 benannt; Termin unbekannt | TEILWEISE ERFÜLLT | Angaben mit Team klären; benotende Felder und Unterschrift dem Prüfer belassen, keine Selbstbenotung |

## 4. Alle zehn gewichteten Teilkompetenzen – Unterkriterienabgleich

### 4.1 Business Understanding – 8 % (B1)

| Unterkriterium | Beleg im Entwurf / Repository | Status | Lücke gegenüber vollständiger 1,0-Beschreibung |
| --- | --- | --- | --- |
| Klare Fragestellung und Entscheidungsbezug | §§1–2, 9, 15; E01/E24/E25 | ERFÜLLT | Fachlich begrenzte Entscheidung erläutern: Modell übernehmen oder verwerfen |
| Fachliches Erfolgskriterium: Nutzen und Schwelle | Geschäftsvision und Nutzenhypothese vorhanden | TEILWEISE ERFÜLLT | Keine validierte vorab festgelegte Nutzer-/Geschäftsnutzenschwelle. Für sehr gute Bewertung offen benennen und künftigen fachlichen Prüfplan begründen; keine Rückdatierung |
| Analytisches Erfolgskriterium | Persistenzvergleich; Zyklus 2 geringerer gepoolter MAE UND ≥2 Foldgewinne | ERFÜLLT | Keine nachträgliche RMSE-Optimierung |
| Rahmen | Synthetische Daten, bekannte Nutzer, Zeit-/Datenschutzgrenzen | ERFÜLLT | Persönliche organisatorische Angaben aus R06/R26 offen |
| Risiken benannt | §§3, 6, 12, 15: Messausfall, Synthetik, Testkenntnis, Abhängigkeit | ERFÜLLT | Risiken live auf Managemententscheidung übertragen |
| Fragestellung im Verlauf geschärft | Nullzielanalyse→historische Nullzählung | ERFÜLLT | Geschäftsfrage nicht mit rein analytischer Verbesserung gleichsetzen |

**Gesamtstand B1: TEILWEISE ERFÜLLT.** Die analytische Entscheidung ist präzise; ein fachlich operationalisiertes Nutzenkriterium ist nicht vollständig belegt. Eine mögliche 1,0 wird nicht aus der MAE-Regel allein abgeleitet.

### 4.2 Data Understanding und Preparation – 12 % (B2)

| Unterkriterium | Nachweis | Status | Grenze / Ergänzung |
| --- | --- | --- | --- |
| Fehlwerte systematisch prüfen | §3.1, §4.1; E07/E10: strukturelle Distanzleerwerte, keine pauschale Imputation | ERFÜLLT | Reale Aufzeichnungslücken bleiben ununtersucht |
| Ausreißer prüfen | Datenwörterbuch, Qualitätsbericht, Auswahlcode und Aufbereitungsaudit prüfen Werte-/Sportgrenzen | ERFÜLLT | Konstruierte Extremwerte nicht als empirisch realistisch validiert darstellen |
| Verteilungen prüfen | §3.2, §4.1, §5.1; E08/E09/E11/E15 | ERFÜLLT | Keine Normalverteilung oder Repräsentativität unterstellen |
| Jeden wesentlichen Aufbereitungsschritt begründen | §§4 und 10; Auswahl, Raster, Standardisierung, Gewichtung, Fenster | ERFÜLLT | Keine bloße Standardpipeline als Begründung |
| Leakage bedacht | §4.3 und §10–11; E13/E14/E26/E28 | ERFÜLLT | Vollständiges Dateihashing von zulässiger Verwendung der Zeilen unterscheiden |
| Eigene Merkmale mit fachlicher Begründung | Häufigkeit/Sportmix, Niveau/Jüngstwert und Nullzählung | ERFÜLLT | Zusätzliche Information nicht mit bewiesenem Prognosenutzen verwechseln |
| Annahmen kritisch geprüft | Zufallsstromkontrolle, Nennerwirkung, Zukunftsinvarianz | ERFÜLLT | Datenplausibilität ist keine externe Validität |

**Gesamtstand B2: ERFÜLLT im schriftlichen/artefaktbezogenen Umfang.** Eine Live-Erklärung bleibt separat zu prüfen.

### 4.3 Modeling und Evaluation – 12 % (B3)

| Unterkriterium | Nachweis | Status | Grenze / Ergänzung |
| --- | --- | --- | --- |
| Begründete Verfahrenswahl | §5: verständliche Startmodelle, K-Means-Profiling, globale OLS | ERFÜLLT | Keine optimale Modellfamilie behaupten |
| Baseline | Persistenz, gleiche Fälle/Informationsstände; E18/E30 | ERFÜLLT | Keine zusätzliche ungetestete Baseline erfinden |
| Saubere Training/Test-Trennung | Ziele 5–22/23–26; Zyklus-2-Folds nur intern | ERFÜLLT | Zyklus 2 ist kein neuer unabhängiger Test, obwohl alte Fälle ausgeschlossen sind |
| Passende Gütemaße | MAE/RMSE; Silhouette/Inertia/ARI für andere Fragestellung | ERFÜLLT | MAE/RMSE-Abweichung bei Nullzielen ausdrücklich erklärt |
| Ergebnis gegen Erfolgskriterium geprüft | §12, E31: UND-Regel, Verwerfung | ERFÜLLT | Keine günstige sekundäre Kennzahl nachträglich zum Hauptkriterium machen |
| Alternativen kritisch geprüft | k-Auswahl, Persistenz, 2-/3-Merkmalsvergleich | ERFÜLLT | Nicht getestete Modellfamilien nur Ausblick |
| Nachvollziehbare Modellartefakte | Metadaten, Koeffizienten, Foldparameter und Prognosen | ERFÜLLT | Externe Nutzbarkeit und Unsicherheit begrenzt |

**Gesamtstand B3: ERFÜLLT im schriftlichen Umfang.** Die Stufe der tatsächlichen Methodenkompetenz entscheidet sich auch mündlich.

### 4.4 Iteratives Vorgehen – 8 % (B4)

| Unterkriterium | Nachweis | Status | Grenze / Ergänzung |
| --- | --- | --- | --- |
| Mindestens zwei vollständige Zyklen | §§2–7 und §§9–13, zwei Detailgrafiken | ERFÜLLT | Deployment als Forschungsübergabe, nicht produktiver Betrieb |
| Erkenntnis steuert nächsten Zyklus | §8: Nullzielschwäche→begrenzt begründetes Merkmal | ERFÜLLT | Kein neuer Zyklus allein wegen sechs Fits |
| Verworfene Wege dokumentiert | Größere k, erweiterte OLS, unzulässige Zukunftsinputs | ERFÜLLT | Originalchat zum Regelzyklus fehlt, daher als Teamangabe |
| Rücksprünge in frühere Phasen | Datenverständnis→Construct Data→Prüfung; Evaluation→neue Geschäfts-/Modellfrage | ERFÜLLT | Frühe Dateniteration nicht fälschlich zweiter vollständiger Zyklus |
| Lerneffekt | Kontrollvergleich isoliert Ursache; Vorabregel verhindert Übernahme ohne Gesamtgewinn | ERFÜLLT | Live an einem konkreten Gegenbeispiel erklären |

**Gesamtstand B4: ERFÜLLT im dokumentierten Umfang.** Die Modelländerung allein wäre zu wenig; der Entwurf stellt Ziel, Datenvorbereitung, neue Modellierung, Evaluation und Übergabe dar.

### 4.5 Lab-Log – 15 % (B5)

| Unterkriterium | Nachweis | Status | Grenze / Ergänzung |
| --- | --- | --- | --- |
| Chronologie statt reiner Ergebnisbericht | Datumsrahmen, Problem→Entscheidung→Kontrolle→Folge | ERFÜLLT | Rekonstruktion als solche gekennzeichnet, keine tagesgenauen Arbeitszeiten erfunden |
| Alle sechs Phasen je Zyklus | §§2–13 und Grafiken | ERFÜLLT | Unterkapitel 10.1/10.2 trennen Datenverständnis und Merkmalskonstruktion |
| Entscheidungen mit Begründung | Nachweismatrix E08–E34 | ERFÜLLT | Originalschwelle für Geschäftsnutzen bleibt offen |
| Reproduzierbarkeit: Code/Workflow und Daten | Anhang A mit Versionen, Seeds, Reihenfolge, Pfaden, Splits und Artefakten | TEILWEISE ERFÜLLT | Frischer unabhängiger Checkout/Abgabepaket nicht heute getestet; privater Zugriff und Trainingsschutz beachten |
| Beiträge beider sichtbar | §1.2, konkrete gemeinsame Arbeitsweise | TEILWEISE ERFÜLLT | Teambeispiele bestätigen, keine künstlichen Zuständigkeiten erzeugen |
| KI-Irrwege und Prüfung dokumentiert | Audit K1–K8, fachliche Kontrolle vorhanden | TEILWEISE ERFÜLLT | Originalprompts/Chats für KI-Zuschreibung fehlen teilweise |
| PDF/Web-App tatsächlich fertig und abgegeben | Nur Markdown-Zwischenstand | OFFEN | Finales Format und Abgabe; siehe K.-o.-Prüfung |

**Gesamtstand B5: TEILWEISE ERFÜLLT.** Die aktuelle lokale Markdownfassung ist keine abgeschlossene Abgabe.

### 4.6 Aussagekraft – 12 % (B6, Vortrag)

| Unterkriterium | Schriftlicher Stand | Status | Ergänzung für Vortrag |
| --- | --- | --- | --- |
| Eine Kernbotschaft | §15: begründete Verwerfung statt Komplexität ohne Nutzen | ERFÜLLT | Auf eine prägnante Abschlussfolie verdichten |
| Antwort auf Geschäftsfrage | Interne Machbarkeit gezeigt, wirtschaftlicher Nutzen offen | ERFÜLLT | „Nicht nachgewiesen“ ist keine bewiesene Wirkungslosigkeit |
| Empfehlung mit Grenzen und Unsicherheit | Reale Daten, unabhängige Prüfung, Einwilligung, kein produktiver Einsatz | ERFÜLLT | Unsicherheit sprachlich statt erfundener Intervalle erklären |
| Zahlen richtig einordnen | Test vs. Validierung, MAE vs. RMSE, Regelwirkung vs. Relevanz | ERFÜLLT | Darstellungen im finalen Foliensatz kontrollieren |
| Irrwege ehrlich gezeigt | Evidenzstatus im Audit | TEILWEISE ERFÜLLT | Belegbare Fälle auswählen und in Vortrag integrieren |
| Aussagekräftige tatsächliche Präsentation | Noch nicht geprüft | OFFEN | Live-Erklärung, keine Ableseprüfung aus Markdown ableiten |

**Gesamtstand B6: TEILWEISE ERFÜLLT; schriftliche Vorbereitung weitgehend vorhanden, Vortragsleistung offen.**

### 4.7 Dramaturgie und Unterhaltungswert – 13 % (B7, Vortrag)

| Unterkriterium | Nachweis / Stand | Status | Nächster Nachweis |
| --- | --- | --- | --- |
| Erzählbogen Frage→Irrwege→Erkenntnis | Entwurf und Gesamtgrafik | TEILWEISE ERFÜLLT | Auf maximal zwölf Inhaltsfolien übertragen |
| Visualisierung trägt die Aussage | Drei PNG/SVGs, gespeicherte Lab-Diagramme | TEILWEISE ERFÜLLT | Große Detailgrafiken nicht unlesbar auf eine Folie quetschen; Kernpfad/Ergebnis im Vortrag zeigen |
| Publikum aktiviert | Keine konkrete Aktivierung ausgearbeitet | OFFEN | Z. B. vor Auflösung des UND-Kriteriums begründete Übernahmeentscheidung abfragen; Vorschlag, nicht bereits durchgeführt |
| Zusammenspiel; beide gleichwertig | Teamangabe gemeinsame Arbeit | OFFEN | Tatsächliche Redeanteile und Übergaben proben; keine festen Fachzuständigkeiten daraus ableiten |
| 15 Minuten ±30 Sekunden für 1,0 | Kein gestoppter Probelauf vorliegend | OFFEN | Ziel 14:30–15:30, danach fünf Minuten Fragen |
| Unterhaltsam und frei statt monoton/abgelesen | Nicht aus Dokumenten beweisbar | OFFEN | Probelauf mit Rückmeldung |

**Gesamtstand B7: OFFEN für die benotete Live-Leistung, teilweise vorbereitet.** Eine attraktive Grafik allein erfüllt keine Dramaturgieprüfung.

### 4.8 Methodenfrage – 7 % (B8, Fragenrunde)

| Unterkriterium | Vorbereitungsgrundlage | Status | Was beide erklären können müssen |
| --- | --- | --- | --- |
| Warum dieses Verfahren? | §§5, 11 | TEILWEISE ERFÜLLT | OLS als erklärbarer Start, Grenzen bei Zähldaten; K-Means-Distanz und Gewichtung |
| Warum dieses Maß und diese Aufbereitung? | §§4, 6, 12 | TEILWEISE ERFÜLLT | MAE/RMSE, strukturelle Fehlwerte, Nullnenner, zeitliche Fenster |
| Alternative und warum verworfen? | §§5, 12 | TEILWEISE ERFÜLLT | k-Varianten und Zusatzmerkmal; keine erfundenen Modellvergleiche |
| Sofort korrekt, vollständig, begründet und über Frage hinaus | Keine Live-Prüfung | OFFEN | Nebenbedingung, Alternative oder Grenze selbstständig ergänzen |

### 4.9 Live-Nachweis im Werkzeug – 7 % (B9, Fragenrunde)

| Unterkriterium | Vorbereitungsgrundlage | Status | Noch erforderlich |
| --- | --- | --- | --- |
| Workflow/Code öffnen | Vollständiger Code vorhanden | TEILWEISE ERFÜLLT | Präsentationsrechner offline/mit vollständiger Git-Historie testen |
| Training/Test-Trennung konkret zeigen | `src/data_preparation_split.py`, `documentation/regression_split_manifest.json` | TEILWEISE ERFÜLLT | Beide finden und erklären die Stelle selbstständig |
| Fehlwerte konkret zeigen | `src/data_preparation_selection.py`, `src/data_preparation_regression.py` | TEILWEISE ERFÜLLT | Strukturelles NA vs. echte Null vs. fehlende Historie unterscheiden |
| Parameter ändern und Wirkung erklären | Lab-Interaktionen existieren, kein Nachtraining bei Anzeige | OFFEN | Mit Dozent klären, ob Anzeige gespeicherter k-Varianten ausreicht oder Codeparameter demonstriert werden soll; Probe separat, Referenzartefakte nicht überschreiben |
| Sofort korrekt, vollständig, begründet, Grenze/Alternative ergänzen | Keine tatsächliche Prüfung | OFFEN | Live-Probe beider Autorinnen |

### 4.10 Entscheidungs- und Transferfrage – 6 % (B10, Fragenrunde)

| Unterkriterium | Vorbereitungsgrundlage | Status | Noch erforderlich |
| --- | --- | --- | --- |
| Managementempfehlung bei geänderten Bedingungen | §15; bewusste Wirkungsgrenzen | TEILWEISE ERFÜLLT | Antwort auf geändertes Szenario üben |
| Neuer Standort / neue Nutzerpopulation | Grenzen bekannter synthetischer Nutzer benannt | TEILWEISE ERFÜLLT | Verteilungs-/Messprozessänderung, unabhängige Datenprüfung erklären |
| Doppeltes Datenvolumen | Skalierungsnachweis ausdrücklich nicht behauptet | TEILWEISE ERFÜLLT | Mehr Daten ≠ automatisch bessere Güte; Laufzeit/Abhängigkeit begründet diskutieren |
| Verschobene Kostenstruktur | Kein Umsatz-/Kostenmodell vorhanden | TEILWEISE ERFÜLLT | MAE vs. geschäftliche Fehlerkosten unterscheiden; keine neue Rendite erfinden |
| Selbstständige vollständige Begründung über Frage hinaus | Keine Live-Prüfung | OFFEN | Cross-Teaching-Probe |

## 5. Vollständige Stufenlogik des Bewertungsbogens

Diese Tabelle gibt die Abstufungen inhaltlich wieder; sie vergibt keine Selbstnote. Die ausführliche Unterkriterienmatrix oben orientiert sich an der 1,0-Spalte. Der Bogen verlangt je Teilkompetenz eine ganze Stufe 1–5. Laut Fußnote sind 2 und 4 anzusetzen, wenn die bessere Stufe überwiegend, aber nicht vollständig erfüllt ist. Originalformulierungen und diese Kalibrierungsregel sind gemeinsam zu beachten; aus der dreistufigen Checkliste lässt sich keine mechanische Notenberechnung ableiten.

| Teilkompetenz | 1,0 | 2,0 | 3,0 | 4,0 | 5,0 |
| --- | --- | --- | --- | --- | --- |
| B1 Business Understanding | Entscheidungsfrage, fachliches und analytisches Kriterium, Risiken, Schärfung | Klare Frage, beide Kriterien, Rahmen knapp | Nutzen vage oder Kriterium nur analytisch | Frage unscharf oder nachträglich ans Ergebnis angepasst | Keine Frage |
| B2 Datenverständnis/-aufbereitung | Systematische Qualität, jeder Schritt begründet, Leakage, eigene fachliche Merkmale | Geprüft/aufbereitet, teilweise Begründungen | Standardschritte, ungeprüfte Annahmen | Lücken/übersehene verzerrende Qualitätsprobleme | Daten unbesehen |
| B3 Modellierung/Evaluation | Begründete Wahl, Baseline, Trennung, passende Maße, kritische Alternativen-/Kriterienprüfung | Sauber/begründet, Baseline fehlt oder Maß unpassend | Bewertung oberflächlich, nur Genauigkeit/kein Holdout | Methodische Fehler oder ungeprüftes Ergebnis | Kein/nicht nachvollziehbares Modell |
| B4 Iteration | ≥2 vollständige Zyklen, Lernen steuert nächsten, verworfene Wege und Rücksprünge | Zwei Zyklen, Lerneffekt, Verworfene knapp | Iteration nur behauptet/eine Variante, Lernen unklar | Linear, Phasen nachträglich | Nicht erkennbar |
| B5 Lab-Log | Chronologisch, alle Phasen, begründete Entscheidungen, reproduzierbar, beide Beiträge, KI-Prüfung | Vollständig/nachvollziehbar, Reproduktion oder Rollen eingeschränkt | Ergebnisbericht statt Log | Phasen/Schritte fehlen | Kein Lab-Log abgegeben, K.-o. |
| B6 Aussagekraft | Eine Kernbotschaft, Geschäftsantwort, Empfehlung mit Unsicherheit/Grenzen, Zahlen/Irrwege ehrlich | Klare Botschaft/Empfehlung, Grenzen angedeutet | Ergebnisse ohne Empfehlung/Einordnung | Zahlenlastig, Botschaft fehlt, Interpretationsfehler | Keine verwertbare Aussage |
| B7 Dramaturgie | Frage→Irrwege→Erkenntnis, tragende Visualisierung, Aktivierung, beide gleichwertig, 15 min ±30 s | Spannend/gut visualisiert, kleine Längen, ±1 min | Solide Berichtsform, textlastig, ±2 min | Monoton/abgelesen, über ±2 min oder ein Mitglied kaum beteiligt | Kein Vortrag/Abbruch |
| B8/B9/B10 gemeinsamer Fragenmaßstab | Sofort korrekt, vollständig, begründet, über Frage hinaus mit Nebenbedingung/Alternative/Grenze | Korrekt/begründet, kleine Lücke oder eine Nachfrage | Im Kern richtig erst mit Hilfe oder nur teilweise begründet | Bruchstücke mit starker Hilfe, Falschbehauptung nicht erkannt | Keine/falsche Antwort |

## 6. K.-o.-Kriterien – alle fünf gesondert geprüft

Die Schwellen sind von normalen Stufenabzügen zu unterscheiden. Ein K.-o. begrenzt laut Originalbogen die Endnote auf 4,0. Die vorbedruckten „Nein“-Felder der Vorlage sind **kein Nachweis**, dass die Kriterien bei MOVA bereits ausgeschlossen wären.

| K.-o. | Originalkriterium | Aktueller Befund | Status des Nachweises / Maßnahme |
| --- | --- | --- | --- |
| KO1 | Kein Lab-Log abgegeben | Lokaler Markdownentwurf vorhanden; keine finale PDF/Web-App oder Einreichung nachgewiesen | OFFEN bis tatsächliche rechtzeitige Abgabe; vorhandene Datei allein genügt nicht |
| KO2 | CRISP-DM-Phasen nicht erkennbar oder nur ein einziger Durchlauf | Zwei vollständige Zyklen schriftlich und durch Modellevaluation belegt | ERFÜLLT hinsichtlich Vermeidung des K.-o.; deutlich in Endfassung beibehalten |
| KO3 | Vortragsdauer unter 10 oder über 20 Minuten | Kein gestoppter Live-Lauf | OFFEN; dies ist die K.-o.-Schwelle, nicht das Zielintervall für gute/sehr gute Note |
| KO4 | Personenbezogene Daten ohne Freigabe **oder** Datensatz ohne Quellenangabe | Aktive Daten synthetisch und Generator/Version belegt; finales Abgabepaket noch ungeprüft | TEILWEISE ERFÜLLT hinsichtlich Vermeidung; persönliche Referenzexporte ausschließen und Quellen/Generator mit abgeben |
| KO5 | Code/Workflow nicht abgegeben – Ergebnis nicht reproduzierbar | Vollständige Dateien und historische Reproduktion vorhanden; Übergabe/Zugriff noch nicht bestätigt | TEILWEISE ERFÜLLT hinsichtlich Vermeidung; Code/Daten/Version erreichbar abgeben und fremden Zugriff prüfen |

Aus diesem Zwischenstand lässt sich weder ein bestehender K.-o.-Verstoß noch die endgültige Vermeidung aller K.-o.-Risiken behaupten. Vor allem Abgabe und Vortragszeit sind zukünftige Ereignisse.

## 7. Vorbereitung auf die drei Fragetypen – konkrete Nachweispfade

Dies sind Übungsvorschläge auf Basis der Originalfragetypen, keine zusätzlichen Professorenpflichten oder bereits absolvierte Übungen.

1. **Methodenfrage:** Warum kein zufälliger Split? An den Zielwochen 5–22/23–26 und Fold 1 erklären, wann ein Label bekannt ist. Warum kein K-Means-Label als früher Regressor? Gesamtzeitraum enthält Zukunft. Warum steigt Nullziel-MAE trotz niedrigerem Nullziel-RMSE nicht automatisch mit demselben Muster? Unterschiedliche Fehlergewichtung erklären.
2. **Live-Nachweis:** Splitkonstanten und Featurefenster im Code zeigen; gespeicherte MAE-Werte im Lab öffnen. Bei vier Nullwochen die zulässigen Eingänge und unbekannte Zielwoche erklären. Eine Parameteränderung nur in einer vorher vereinbarten Demonstrationskopie erwägen; dieser Dokumentationsauftrag führt keine Änderung oder neuen Fit aus.
3. **Transfer:** Bei realem Messausfall kann eine scheinbare Nullwoche keine echte Null sein. Bei neuer Nutzerpopulation sind die bisherigen Kennzahlen nicht übertragbar. Bei asymmetrischen Geschäftskosten reicht MAE möglicherweise nicht als Nutzenkriterium. Beides verlangt neue fachliche Festlegung und Validierung, keine rückwirkend günstigere Auswahl.

Die Originalvorlage enthält LN-B-Felder „Methodenfrage an“, „Live-Nachweis an“ und „Entscheidungs-/Transferfrage an“. Die tatsächlichen Prüfungsfragen erstellt der Dozent; das Team soll keine endgültige Fragezuteilung oder bevorzugte Zuständigkeit erfinden.

## 8. Gewichtung, Ergebnisregeln und sehr gute Bewertung

| Gruppe | Kriterien | Gewichte | Summe |
| --- | --- | --- | ---: |
| Projekt und Lab-Log | B1–B5 | 8 % + 12 % + 12 % + 8 % + 15 % | 55 % |
| Vortrag | B6–B7 | 12 % + 13 % | 25 % |
| Fragenrunde | B8–B10 | 7 % + 7 % + 6 % | 20 % |
| Gesamt | B1–B10 | Alle zehn | 100 % |

Der Bogen verwendet den gewichteten Mittelwert der Stufen und Rundung auf 1,0 / 1,3 / 1,7 / 2,0 / 2,3 / 2,7 / 3,0 / 3,3 / 3,7 / 4,0; ein Mittelwert über 4,15 führt laut Fußnote zu 5,0. K.-o.-Deckelung gesondert beachten. Die Angaben werden hier dokumentiert, nicht zur Prognose einer Note eingesetzt. Rückmeldefeld und Prüferunterschrift bleiben dem Prüfer vorbehalten.

Für eine **sehr gute Bewertung** fehlen vor allem überprüfbare Eigenleistung und vollständige Übergabe: beide müssen Methoden und Code selbstständig erklären, Parameterwirkungen und Grenzen übertragen, gleichwertig präsentieren und das 15-Minuten-Ziel praktisch einhalten. Inhaltlich sollte das Team den fehlenden fachlichen Nutzenschwellen-Nachweis offen diskutieren, die KI-Zuschreibungen belegen und die Datenherkunft samt Einwilligungsabgrenzung sauber abschließen. Ein längeres Lab-Log oder mehr Grafiken kompensiert diese Punkte nicht automatisch.

## 9. Technischer Dokumentencheck dieses Auftrags

Geprüft werden die fünf neuen Markdowndateien, vorhandene Zielpfade/Abbildungen, E-Verweise, Zahlenabgleich mit Ergebnisdateien und Hashgleichheit des bisherigen versionierten Bestands. Es werden keine Modelle trainiert, keine Daten oder Grafiken verändert und keine neuen Dashboardtests/Modelltests gestartet. Tatsächlicher Prüflauf am 04.11.2026:

- Alle fünf angeforderten Markdowndateien neu vorhanden, ohne bestehende Dokumente zu überschreiben.
- 134 relative Dokument-/Dateiverweise auf vorhandene Ziele geprüft; kein fehlendes Ziel.
- 40 E-Nachweise definiert; alle im Entwurf verwendeten E-IDs auflösbar.
- In den Reproduktionsbefehlen genannte Python-Skripte existieren. Befehle wurden nicht ausgeführt.
- Zentrale Zyklus-1-Zahlen gegen gespeicherte JSONs, Zyklus-2-Zahlen gegen gespeicherte CSVs abgeglichen; keine neue Modellauswertung.
- 235 vor Beginn versionierte Dateien per SHA-256 unverändert, einschließlich Daten, Modelle, Dashboard und aller Grafikdateien. Zusätzlich alle zehn im Zyklus-2-Laufmanifest verzeichneten Experimentartefakte unverändert.
- Git-Status zeigt ausschließlich die fünf neuen Dokumente als unversionierte Ergänzungen. Keine Datei vorgemerkt, kein Commit, kein Push und kein PR.
- Beide Original-PDFs vollständig textuell gelesen; Bewertungsbogen zusätzlich visuell kontrolliert. Alle zehn Gewichte ergeben 100 %; alle fünf K.-o.-Kriterien sind gesondert erfasst.
- Kein neues Modelltraining, keine Modell-/Dashboardtests und keine Datengenerierung ausgeführt. Historische Prüfzahlen sind als historische Nachweise gekennzeichnet.

Die Qualität der gerenderten PDF-Seiten bleibt bis zum tatsächlichen Export offen. Auch eine automatisierte Linkprüfung belegt weder die Richtigkeit einer persönlichen Teamangabe noch bestandene Live-Kompetenz.
