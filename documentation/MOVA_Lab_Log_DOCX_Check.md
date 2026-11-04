# MOVA – Prüfprotokoll der Word-Fassung

Prüfdatum: 04.11.2026. Branch: `feature/final-lab-log`. Bestätigte Ausgangsfassung: Commit `73216b47249b884e67d682ebaff3d1f6e5299d49`.

Erzeugtes Dokument: [MOVA_Lab_Log.docx](MOVA_Lab_Log.docx). Dies ist eine vollständige bearbeitbare Lesefassung, keine gekürzte Neufassung und kein bereits eingereichtes Lab-Log. Es wurden keine Ergebnisse neu berechnet und keine Modellläufe durchgeführt.

## 1. Quellen und Verfahren

Vollständig übernommen wurden:

- [Lab-Log-Entwurf](final_lab_log_draft.md) als Haupttext einschließlich der bisherigen Anhänge A/B.
- [Nachweismatrix](final_lab_log_evidence.md) als Anhang C.
- [KI-Audit](ai_missteps_audit.md) als Anhang D.
- [Offene Punkte](final_lab_log_open_items.md) als Anhang E.
- [Qualitätsabgleich](final_lab_log_quality_check.md) als Anhang F.

Anhang G ergänzt ausschließlich Hinweise zur Word-Bearbeitung, Quellenlücken und zeitlichen Einordnung historischer Arbeitsstände. Die Markdown-Dateien wurden nicht verändert. Ihre historischen Aussagen über frühere Commitstände, damals uncommittete Ergänzungen oder das damalige Markdown-Format wurden erhalten und in Anhang G ausdrücklich eingeordnet.

Konvertierung: Pandoc 3.1.11.1 über einen Markdown-AST, anschließend python-docx 1.2.0 für Formatvorlagen, Tabellen, Abschnitte, Felder und Verweise. Prüfung des ZIP-/OOXML-Pakets mit Python/lxml; Textvergleich gegen die AST-Textbausteine der fünf Quellen. Vorschau mit LibreOfficeDev 26.8 Alpha und Prüfung der resultierenden Seiten mit PyMuPDF sowie gerenderten Seitenübersichten. Die PDF-Vorschau ist nur ein internes Prüfmittel und keine finale Abgabe-PDF.

Die beiden hochgeladenen Originaldokumente wurden vollständig im Originaltext und der Bewertungsbogen zusätzlich als gerenderte Seite berücksichtigt:

- `Bewertungsboegen4_LN_Rahmen und Ablauf.pdf`: ausschließlich LN B und darauf anwendbare gemeinsame Regeln.
- `Bewertungsboegen2_LN_Datenanalyseprojekt.pdf`: vollständiger LN-B-Bewertungsbogen, alle zehn Teilkompetenzen, Unterkriterien, Stufen, Fußnoten und fünf K.-o.-Kriterien.

Die vorhandene detaillierte Anforderungsmatrix mit Quellenidentifikation und Hashes ist vollständig in Anhang F enthalten. LN-A-/LN-C-Sonderanforderungen wurden nicht übertragen. Die Upload-PDFs selbst sind keine dauerhaft im Repository verfügbaren Quellen.

## 2. Tatsächlicher Umfang und Seitengestaltung

**Die geprüfte LibreOffice-Vorschau hat 59 Seiten.** Das ist eine gemessene Seitenzahl dieser Renderumgebung; Microsoft Word kann durch andere Schrift-/Layoutbehandlung anders umbrechen. DOCX speichert fließenden Inhalt und garantiert keine rendererunabhängige Seitenzahl.

| Bestandteil | Seiten der geprüften Vorschau |
| --- | --- |
| Deckblatt | 1 |
| Automatisches Inhaltsverzeichnis mit sichtbarem Feldinhalt | 2–3 |
| Haupttext, Kapitel 1–15 einschließlich drei Grafiken | 4–22; Anhang A beginnt auf Seite 22 |
| Bisherige Anhänge A/B: Reproduktion und Quellen | 22–25 |
| Anhang C: vollständige Nachweismatrix | 26–31 |
| Anhang D: vollständiger KI-Audit | 32–35 |
| Anhang E: vollständige offene Punkte | 36–39 |
| Anhang F: vollständiger Originalanforderungsabgleich | 40–58 |
| Anhang G: Quellenstand und Word-Bearbeitung | 59 |

Der Umfang liegt über dem unverbindlichen Richtwert von 6–12 Seiten-Äquivalent. Die Originalvorgaben setzen keine feste Seitenobergrenze. Auch der Haupttext liegt über dem bisherigen redaktionellen Teamziel von 12–15 Seiten. Vollständigkeit hatte hier Vorrang; eine spätere Kürzung bzw. Auslagerung von Prüfanlagen wäre eine gesonderte redaktionelle Entscheidung und wurde nicht stillschweigend vorgenommen.

Einheitliche Schrift Liberation Sans, farblich zurückhaltende MOVA-Akzente, echte Überschriftenformatvorlagen, Kopfzeilen und automatische PAGE-/NUMPAGES-Felder. Insgesamt zwölf Abschnitte. Das Deckblatt zeigt keine sichtbare Seitenzahl. A4-Hochformat für den Fließtext, Querformat für umfangreiche Nachweistabellen; abweichende Grafikformate wie unten beschrieben.

## 3. Vollständigkeits- und Strukturprüfung

| Prüfung | Tatsächliches Ergebnis |
| --- | --- |
| Textabgleich der fünf vollständigen Quellen | 1.358 von 1.358 normalisierten Textbausteinen im DOCX gefunden; keine fehlenden Bausteine |
| Überschriften | 82 Quellüberschriften plus eine zusätzliche Überschrift für Anhang G; echte Word-Überschriften |
| Tabellen | Alle 30 Quelltabellen als native bearbeitbare Word-Tabellen vorhanden |
| Codeblöcke | Alle fünf Quellcodeblöcke als bearbeitbarer Text erhalten |
| Grafiken | Drei eingebettete Bilder; alle drei eingebetteten PNG-Daten stimmen per SHA-256 mit den Originaldateien überein |
| Internes Inhaltsverzeichnis | Natives TOC-Feld für Ebenen 1–2, 73 sichtbare verlinkte Einträge; Seitenzahlen nach Rendern aktualisiert und erneut gerendert |
| Interne Verweise | Sämtliche internen Hyperlink-Anker besitzen ein vorhandenes Bookmarkziel; keine doppelten Bookmarknamen |
| Externe Verweise | 88 externe Link-Beziehungen; Repository-Dateiziele existieren lokal; Repositorylinks auf den bestätigten Commit bezogen |
| Dateiintegrität | DOCX-ZIP-Prüfung ohne Fehler; erfolgreich mit python-docx und LibreOffice geöffnet |
| Erhalt bestehender Dateien | SHA-256-Abgleich aller 244 zuvor erfassten versionierten Dateien: keine Abweichung |

Der Textabgleich prüft Vollständigkeit, nicht die wissenschaftliche Wahrheit jeder Aussage. Die wissenschaftlichen Belege und ihre Grenzen bleiben durch die unverändert übernommenen Nachweise nachvollziehbar. Die Funktionsfähigkeit privater GitHub-Links für den Prüfer wurde nicht durch einen fremden Account nachgewiesen.

## 4. Grafiken und Bearbeitbarkeit

| Grafik | Platzierung | Prüfung |
| --- | --- | --- |
| Gesamtprozess | Seite 6, A4 quer, etwa 250 mm breit | Beide Zyklen und iterative Übergänge eingebettet; Bild vollständig sichtbar |
| Zyklus 1 | Seite 13, A2 quer, etwa 550 mm breit | Unverändertes vorhandenes Sechs-Spalten-Layout nach bereitgestellter Schieder-Vorlage; sechs Phasen und 24 Arbeitsschritte sichtbar |
| Zyklus 2 | Seite 18, A2 quer, etwa 550 mm breit | Dasselbe Layout; sechs Phasen und 24 Arbeitsschritte sichtbar |

Alle drei bestehenden Abbildungsbeschriftungen und Quellenhinweise sind erhalten. Die Detailgrafiken wurden bewusst nicht auf A4 verkleinert: Ihre Beschriftungen wären sonst zu klein. A2-Seiten sind in Word/PDF bei passendem Zoom gut lesbar; beim Ausdruck auf A4 würde diese Lesbarkeit verloren gehen. Die Übersicht hat kleineren Text und benötigt bei Bildschirmbetrachtung gegebenenfalls Vergrößerung.

**Bearbeitbarkeitsgrenze:** Fließtext, Tabellen, Überschriften und Code sind native Word-Inhalte. Die unverändert übernommenen PNG-Grafiken sind austauschbare Bilder, keine einzelnen bearbeitbaren Word-Zeichenobjekte. Ihre Beschriftungen bleiben in den vorhandenen SVG-/Grafikquellen editierbar. Eine Umzeichnung in Word wurde nicht vorgenommen und wäre mit der Vorgabe unveränderter Grafiken nicht gleichzusetzen.

## 5. Sicht- und Umbruchprüfung

Alle 59 Seiten wurden über gerenderte Seitenübersichten kontrolliert; Inhaltsverzeichnis, Detailgrafik und repräsentative umfangreiche Nachweistabelle wurden zusätzlich vergrößert geprüft. Fließtext, Tabellen und Grafiken weisen dabei keine erkennbaren abgeschnittenen Ränder oder Überlagerungen auf. Eine zusätzliche Koordinatenprüfung fand keine Textspannen außerhalb der Seitenfläche. Keine textleeren Seiten.

Tabellen haben feste passende Spaltenbreiten, wiederholte Kopfzeilen und gegen Teilung gesperrte Einzelzeilen. Längere Tabellen dürfen über Seiten laufen. Überschriften bleiben mit dem folgenden Absatz verbunden; Grafikabschnitte besitzen eigene Seitenwechsel. Die sichtbaren TOC-Seitenzahlen stimmen mit den Überschriftenseiten der letzten Vorschau überein.

Diese Sichtprüfung ersetzt keine abschließende Kontrolle in Microsoft Word. LibreOfficeDev ist eine Entwicklungsversion; die Konvertierung war erfolgreich, es wurden lediglich Fontconfig-Hinweise zum nicht beschreibbaren Schriftcache ausgegeben. Die verwendete Schrift war verfügbar.

## 6. Wissenschaftliche und bewertungsbezogene Prüfung

Die Word-Konvertierung bewahrt die nachvollziehbare Kette aus Fragestellung, Entscheidung, Begründung, Prüfung, Ergebnis und Erkenntnis. Beide vollständigen CRISP-DM-Zyklen, der Datengenerierungsrücksprung, die Nullwochenhypothese und die begründete Verwerfung bleiben enthalten. Es wurden keine neuen Mindestschwellen, Signifikanzbefunde oder wirtschaftlichen Wirkungen ergänzt.

Insbesondere erhalten:

- Synthetische Datengrundlage; Garmin-Export ausschließlich als persönlich bestätigte Strukturorientierung, keine empirische Kalibrierung oder echten Garmin-Trainingsdaten.
- Trennung der ursprünglichen Testauswertung von der internen Zyklus-2-Validierung und deren Leakage-Prüfungen.
- Projektspezifische, vor dem zweiten Vergleich übernommene UND-Heuristik; kein statistischer Signifikanztest.
- Retrospektiver Status der übergreifenden Erfolgskriterien und der Sportpassungsmetrik; keine Gleichsetzung mit Zufriedenheit, Conversion oder Umsatz.
- Vier KI-Reflexionsfälle mit begrenzter Ursachenzuschreibung; Zufallsstromkontrolle ausschließlich als methodischer Gegenstand.
- Gemeinsame fachliche Arbeit sowie die begrenzte Ausnahme bei der Videoproduktion; keine erfundenen Einzelzuständigkeiten.
- Sämtliche Reproduktionsangaben und Hinweise, welche historischen Befehle Modellfits auslösen würden. Diese Befehle wurden hier nicht ausgeführt.

Die zehn Bewertungskompetenzen einschließlich aller Unterpunkte bleiben im vollständigen Qualitätsabgleich nachweisbezogen als erfüllt, teilweise erfüllt oder offen dokumentiert. Keine Note wird zugesagt. Die Word-Erstellung weist weder Vortragsleistung noch Live-Kompetenz nach.

Die fünf K.-o.-Bereiche bleiben getrennt: tatsächliche Lab-Log-Abgabe; erkennbare Phasen und mindestens zwei Zyklen; zulässige Vortragsdauer; Datenschutz/Datenquelle; tatsächliche Codeübergabe und Reproduzierbarkeit. Das Dokument belegt Struktur und dokumentierte Analyse, aber noch keine fristgerechte Abgabe, Vortragsdauer oder Zugriffsmöglichkeit des Prüfers. DOCX allein ist zudem noch nicht das verlangte PDF-/Web-Abgabeformat.

## 7. Noch offene Punkte vor der Abgabe

1. **Microsoft Word:** Datei öffnen, alle Felder aktualisieren und das Inhaltsverzeichnis vollständig aktualisieren. Seitenzahlen, sämtliche Formatwechsel, Tabellen und die beiden A2-Seiten anschließend erneut kontrollieren. Erst dann selbst als PDF exportieren und die PDF prüfen.
2. **Deckblatt:** Nachnamen, Matrikelnummern und Prüfungstermin ergänzen; gelbe Platzhalter stehen sichtbar im Dokument. Frist und Einreichungsweg bestätigen.
3. **Quellen:** Konkrete tatsächlich verwendete Fachliteratur und Zitierstil ergänzen. Die genaue Schieder-Grafikquelle mit Foliensatz, Jahr und Seiten-/Folienzahl fehlt weiterhin und ist ausdrücklich markiert. Keine Literatur wurde erfunden. E-Nachweise sind verlinkte Textnachweise, keine Word-Literaturverwaltungsfelder.
4. **Quellenzugang:** Original-PDFs dauerhaft und datenschutzgerecht verfügbar machen; Quellen persönlicher Bestätigungen und ursprüngliche KI-Gesprächsbelege nach Möglichkeit sichern. Die technischen Fehler sind belegt, ihre KI-Ursache teilweise weiterhin nicht abschließend.
5. **Organisatorisches:** Einordnung der fachlichen Themenabstimmung zur geforderten Vorabanmeldung klären; keine gesonderte formale Anmeldung behaupten. Code-/Datenzugang für den Prüfer und abschließenden Paket-/Datenschutzcheck sicherstellen.
6. **Vortrag:** Finalen Foliensatz, Laufzeit, gleichwertige Beteiligung, Aktivierung und Methoden-/Live-/Transferfragen separat prüfen. Eine Videoerlaubnis ersetzt keine bloße Annahme.
7. **Aussagegrenzen:** Keine realen Nutzerbefragungen oder wirtschaftliche Wirkungsnachweise; keine unabhängige Realweltevaluation oder nachträglich erfundene Unsicherheitsintervalle. Dies sind wissenschaftliche Grenzen, keine durch Formatierung behebbaren Lücken.
8. **Umfang:** Gegebenenfalls eine spätere konzentrierte Hauptfassung mit separat gehaltenen Prüfanlagen abstimmen; derzeit bleiben alle Inhalte aus Vollständigkeitsgründen enthalten.

## 8. Änderungsumfang

Neu erstellt wurden ausschließlich die angeforderte Word-Datei und dieses Prüfprotokoll im versionierbaren Projektbereich. Konvertierungs-, Render- und Prüfzwischenstände liegen unter dem bereits ignorierten `work/`-Verzeichnis. Die 244 bestehenden versionierten Dateien einschließlich Markdown, Daten, Modelle, Grafiken und Dashboard blieben unverändert. Keine Trainingsläufe, kein Commit, kein Push, kein Pull Request.
