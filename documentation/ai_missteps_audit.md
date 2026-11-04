# MOVA – Audit von KI-Irrwegen und deren Prüfung

**Neue Rekonstruktion, 04.11.2026.** Grundlage sind vorhandene Projektberichte, Code und der in diesem Chat ausdrücklich bereitgestellte Teamkontext. Keine originalgetreue Wiederherstellung des früheren Audits. Der Zweck ist eine ehrliche Trennung zwischen technischem Fehlversuch, methodischer Kontrolle, fachlich hinterfragtem Vorschlag und tatsächlich belegter KI-Ursache.

## 1. Bewertungs- und Belegrahmen

Die Originalvorgaben für LN B erlauben KI uneingeschränkt, ohne allgemeinen Nutzungsnachweis zu verlangen. Gleichzeitig verlangt Kriterium 5 des Bewertungsbogens dokumentierte KI-Irrwege und deren Prüfung. Ein nachträgliches Erfinden von Irrwegen wäre weder fachlich hilfreich noch mit diesem Anspruch vereinbar. Eine genaue Produkt-/Modellversion oder ein wörtlicher Prompt wird nur genannt, wenn er vorliegt; für die historischen Fälle liegt dies aktuell nicht vollständig vor.

Die Buchstaben **B** und **C** werden entsprechend der verbindlichen Teamvorgabe übernommen: Streamlit-Test-API, README-Rücknahme und mobile Überlagerung = B; Zufallsstromkontrolle = C. Die ursprüngliche Definition einer übergeordneten A/B/C-Taxonomie liegt nicht vor. Deshalb wird keine formale Bedeutung als Professorenvorgabe oder Evidenzskala erfunden. Der Belegstatus wird separat ausgeschrieben.

## 2. Historische Fälle

| Fall | Vorgegebene Kategorie | Ereignis belegt? | Korrektur/Prüfung belegt? | KI-Ursache belegt? |
| --- | --- | --- | --- | --- |
| K1 Streamlit-Test-API | B | Ja, Bericht | Ja, öffentliche Mapping-Schnittstelle und nachfolgende Tests | Teilweise; Originalprompt/Initialdiff fehlt |
| K2 README-Änderung und Rücknahme | B | Ja, Bericht | Ja, Integritätstest und Rücknahme | Teilweise; ursprünglicher Vorschlag fehlt |
| K3 Mobile Phasenüberlagerung | B | Ja, Bericht | Ja, vertikale Darstellung und Desktop-/Mobilkontrolle | Teilweise; Layoutursprung nicht aus Code allein zurechenbar |
| K4 Zufallsstromkontrolle | C | Ja, Code und Vergleichsdaten | Ja, gepaarter Kontrolllauf | Kein KI-Fehler nachgewiesen |
| K5 Empfehlungs-Erweiterung als zweiter Zyklus | Nicht vorgegeben | Teamangabe | Regressionszyklus tatsächlich umgesetzt | Originalgespräch fehlt; offener Kandidat |

### K1 – Nicht öffentliche Streamlit-Test-API

**Problem:** Laut [Dashboard-Ausführungsbericht](dashboard_execution.md), Passage bei Zeilen 205–206 im Referenzstand, verwendete ein früher Test eine nicht öffentliche Session-State-Eigenschaft der neuen Streamlit-Version. Der Ansatz band die Prüfung an ein nicht zugesichertes Implementierungsdetail statt an die öffentliche Schnittstelle.

**Korrektur und Kontrolle:** Der Test wurde auf die öffentliche Mapping-Schnittstelle umgestellt. Nachfolgende Dashboardtests bestanden laut demselben Bericht. Das ist ein konkreter technischer Fehlversuch mit nachgewiesener Korrektur. Der damalige Stacktrace und der erste Codezustand sind nicht als gesonderter Chatbeleg archiviert.

**Lernpunkt:** Vermeintlich plausible Bibliotheksaufrufe müssen an der verwendeten Version und der öffentlichen API geprüft werden. Der Bericht belegt die Fehlverwendung, nicht aus sich heraus deren alleinige Verursachung durch KI. Für eine explizite KI-Zuschreibung sollte der ursprüngliche Vorschlag ergänzt werden.

### K2 – README-Ergänzung gegen bestehenden Integritätsvertrag

**Problem:** Der [Dashboardbericht](dashboard_execution.md), Passage bei Zeilen 207–208, hält fest, dass ein AP6-Integritätstest eine eigene README-Ergänzung erkannte. Die Ergänzung war im betreffenden Arbeitsschritt nicht zulässig; die technische Fehlannahme bestand darin, eine allgemeine Dokumentationsverbesserung unabhängig vom vereinbarten Änderungsumfang vorzunehmen.

**Korrektur und Kontrolle:** Die Ergänzung wurde vollständig zurückgenommen. Die Startanleitung wurde in den vorgesehenen Dashboardbericht aufgenommen; der bestehende Testcode blieb unverändert. Der heutige veraltete README-Status allein beweist den Rücknahmevorgang nicht. Der Ausführungsbericht ist dafür der konkrete historische Beleg.

**Lernpunkt:** Auch gut gemeinte Textänderungen benötigen einen passenden Auftrag und dürfen Reproduzierbarkeitsverträge nicht still verändern. Nicht jede angezeigte Testabweichung ist ein Modellfehler. Ein ursprünglicher Chat-/Diffnachweis der KI-Beteiligung bleibt offen.

### K3 – Überlagerte CRISP-DM-Phasenbeschriftungen auf Mobilbreite

**Problem:** Die [visuelle Dashboardprüfung](dashboard_execution.md), Passage bei Zeilen 775–783, beschreibt überlagerte Phasenbeschriftungen bei mobiler Darstellung. Die Anwendung konnte technisch laufen, während die Visualisierung bei kleiner Breite unleserlich wurde. Ein Starttest allein hätte diesen Fehler nicht zuverlässig erfasst.

**Korrektur und Kontrolle:** Die Darstellung wurde für Mobilbreite vertikal angeordnet und auf Desktop sowie Mobil erneut geprüft. Der Bericht nennt insbesondere 390 × 1000 Pixel und Kontrollen gegen horizontalen Seitenüberlauf. Die früheren temporären Screenshots unter `work/` sind nicht als allgemeiner dauerhafter Checkoutnachweis zu behandeln.

**Lernpunkt:** Erfolgreiche Ausführung und visuelle Nutzbarkeit sind verschiedene Qualitätsdimensionen. Responsive Layouts benötigen Prüfung bei Zielauflösungen. Die KI-Verursachung ist ohne ursprünglichen Layoutvorschlag nicht vollständig nachgewiesen; der Fehler selbst ist dokumentiert.

### K4 – Zufallsstromkontrolle als methodische Absicherung

**Problem:** Präferenzexponent und technische Zufallsstromstruktur änderten sich zwischen historischem V1 und V2. Ein unkontrollierter Vergleich hätte Häufigkeitsunterschiede möglicherweise fälschlich der Präferenzverstärkung zugeordnet.

**Prüfung:** [Kontrollskript](../src/simulation_preference_comparison.py), [Vergleichstabelle](../outputs/simulation_comparison/comparison_metrics.csv) und [Iterationsprotokoll](crisp_dm_log.md) belegen den Vergleich Exponent 1,0 gegen 1,3 bei gleichem neuen Zufallsaufbau. Die Wochenzählungen sind dabei identisch; der Top-2-Anteil steigt um etwa 6,507 Prozentpunkte. Die Unterschiede 6.665→6.465 Aktivitäten im historischen V1/V2-Vergleich sind kein isolierter Exponenteneffekt.

**Einordnung:** Kategorie C laut Team. Der Fall illustriert eine erkannte Konfundierung und ihre methodische Kontrolle. Es ist nicht belegt, dass eine KI zuvor die falsche Kausalaussage formuliert hatte. Daher wird daraus kein künstlicher zusätzlicher KI-Fehler konstruiert.

### K5 – Regelbasierte Empfehlungserweiterung als möglicher zweiter Zyklus

**Teamangabe:** In einer ChatGPT-Diskussion wurde zunächst eine Erweiterung des regelbasierten Empfehlungssystems als zweiter Zyklus erwogen. Hanna und Patricia hinterfragten den Vorschlag, weil sie eine erneute datengetriebene Modellierung und Evaluation durchführen wollten. Der tatsächlich folgende [Regressionszyklus](cycle2/report.md) ist im Repository belegt.

**Fachliche Prüfung:** Eine kontrollierte Regeländerung kann eine sinnvolle CRISP-DM-Arbeit sein. Sie weist aber nicht automatisch eine neue Schätzung eines datengetriebenen Modells nach. Für MOVA wurde deshalb die historische Nullwochenzahl als begrenzte Modellierungshypothese untersucht. Der Weg ist fachlich durch die erste Fehleranalyse motiviert; die Bewertungsanforderung erklärt den Projektumfang, ersetzt aber nicht die fachliche Begründung.

**Offen:** Originalgespräch, Datum, Wortlaut, anschließende Rückfrage und Prüfentscheidung. Ohne diese Belege bleibt K5 ein plausibler, ausdrücklich vom Team berichteter Kandidat; keine wörtliche KI-Aussage wird erfunden. Eine allgemeine Ablehnung regelbasierter Verfahren wäre aus diesem Fall nicht gerechtfertigt.

## 3. Zusätzliche Fälle im sichtbaren aktuellen Arbeitsverlauf

Diese Fälle sind in diesem Chat nachvollziehbar, aber noch nicht als dauerhaftes Gesprächsartefakt im Repository archiviert. Sie werden von K1–K5 getrennt und erhalten keine frei erfundene B/C-Einstufung.

**K6 – Dateiexistenz mit nutzbarer Bereitstellung verwechselt.** Die drei PNGs waren gültig, dekodierbar und in der Cloud vorhanden. Die direkte Chatdarstellung bot dem Team jedoch keinen funktionierenden Download. Die technische Prüfung beantwortete zunächst nicht die praktische Übertragungsfrage. Korrigiert wurde die Aussage durch explizite Trennung von Cloudpfad und lokalem Speicherort; später wurden die Grafiken auf den autorisierten Dokumentationsbranch übertragen. Ursache der fehlenden UI-Vorschau ist nicht gesichert. Kein beschädigtes Bild und keine bewiesene Halluzination über die Dateiexistenz.

**K7 – Unvollständiger Lieferumfang und verspätete Klärung.** Der Commit `7282cef20cdcc871ff78b2c9e879b98cd880f4f5` trägt auf Wunsch den Titel „docs: Add MOVA lab log draft and CRISP-DM figures“, enthält aber ausschließlich zehn Dateien unter `documentation/figures/`. Die fünf genannten Lab-Log-Dokumente waren lokal nicht auffindbar. Der Grafikstand wurde vor Eingang der Antwort auf die Rückfrage bereits gepusht. Das Team erhielt anschließend den tatsächlichen Umfang offengelegt. Der Titel kann Vollständigkeit suggerieren; Commitinhalt und Übergabestatus müssen deshalb ausdrücklich geprüft werden. Der Vorgang beweist nicht, wann oder weshalb die früheren fünf Dateien verloren gingen.

**K8 – Veralteter trainingsfreier Runner nach Suite-Erweiterung.** Ein statischer Abgleich zeigt, dass [run_without_training.py](../tests/run_without_training.py) ältere Trainingstests überspringt, den neuen Fit-Test in [test_cycle2.py](../tests/test_cycle2.py) aber nicht. Eine ungeprüfte Übernahme der alten Gesamtprüfanleitung könnte daher scheitern. Die Fit-Sperre verhindert unerlaubtes Training, macht die neue Suite jedoch nicht automatisch erfolgreich. Der aktuelle Entwurf weist darauf hin; es wurde kein neuer Fehlerlauf ausgeführt und kein Code verändert. Eine ursächliche KI-Zuschreibung wird nicht behauptet.

## 4. Konsequenz für Lab-Log und Vortrag

Für die schriftliche Darstellung sind K1–K3 als belegte technische Fehlversuche mit dokumentierter Kontrolle verwendbar, jeweils mit begrenzter KI-Zuschreibung. K4 ist eine methodische Qualitätskontrolle. K5 benötigt den ursprünglichen Chat, K6/K7 einen archivierten Ausschnitt des aktuellen Verlaufs. K8 ist eine aktuelle statische Wartungsfeststellung. Eine ausreichende Zahl vermeintlicher Irrwege wird nicht durch Umdeklarieren methodischer Kontrollen erreicht.

Beide Teammitglieder sollten an einem konkreten Fall erklären können, woran der Fehler erkennbar war, welche Alternative gewählt wurde, wie die Korrektur überprüft wurde und welche Grenze des Nachweises bleibt. Das entspricht eigenem methodischem Verständnis; es wird hier als Lernziel formuliert, nicht als bereits bestandene Live-Leistung. Vor der Abgabe sind geeignete Gesprächsausschnitte ohne persönliche oder vertrauliche Nebeninhalte zu sichern.
