# MOVA – KI-Einsatz, Irrwege und menschliche Qualitätskontrolle

**Neue quellenbasierte Rekonstruktion; redaktionell präzisiert am 04.11.2026.** Dieses Audit behandelt ausschließlich die vier vom Team bestätigten Fälle. Die Kennungen K1–K3 und K5 bleiben für bestehende Verweise erhalten. Es werden keine zusätzlichen Fehler, Ursprungs-Prompts oder KI-Ursachen rekonstruiert.

## 1. Belegrahmen und gemeinsame Verantwortung

Hanna und Patricia nutzten nach eigener Angabe ChatGPT und Codex gemeinsam zur fachlichen Reflexion, Entwicklung und Dokumentation. Beide übernahmen die Verantwortung für die Prüfung der Vorschläge und Ergebnisse; eine künstliche Aufteilung einzelner Debugging-Handlungen wird nicht vorgenommen. Die gemeinsame Arbeitsweise ist eine Teamangabe. Die Repositoryberichte belegen die technischen Ereignisse und Korrekturen, aber nicht, wer jeden einzelnen Prüfschritt ausführte.

Drei Belegebenen sind zu unterscheiden: **Teamangabe** zum Entstehungs- und Entscheidungsverlauf, **Repositorynachweis** zum technischen Ereignis bzw. Ergebnis und **Primärbeleg der KI-Zuschreibung** wie ein ursprünglicher Gesprächsausschnitt. Ein technischer Fehler im KI-unterstützten Projekt ist nicht automatisch ein nachgewiesener Fehler eines bestimmten KI-Systems. Die frühere Buchstabentaxonomie wird hier nicht benötigt und nicht als Bewertungsregel ausgegeben.

## 2. Übersicht der vier Fälle

| Fall | Art | Nachweis des Ereignisses und der Korrektur | Status der KI-Zuschreibung |
| --- | --- | --- | --- |
| K5 Methodischer Vorschlag: Empfehlungssystem als zweiter Zyklus | Konkreter ChatGPT-Vorschlag laut Team | Teamangabe zum Vorschlag; Repository belegt den stattdessen durchgeführten Regressionszyklus | ChatGPT als Urheber vom Team ausdrücklich benannt; ursprünglicher Chat noch nicht archiviert, daher kein unabhängig prüfbarer Primärbeleg |
| K1 Nicht öffentliche Streamlit-Test-API | Technischer Fehlversuch in KI-unterstützter Entwicklung | Ausführungsbericht und korrigierter Testbestand | Konkreter KI-Ursprung nicht abschließend belegt |
| K2 Nicht vorgesehene README-Änderung | Überschreitung des vereinbarten Änderungsumfangs | Integritätsbefund und Rücknahme im Ausführungsbericht dokumentiert | KI-Verursachung möglich, nicht eindeutig nachgewiesen |
| K3 Mobile Phasenüberlagerung | Visueller Fehler in KI-unterstützt entwickelter Ansicht | Bericht über Befund/Korrektur und aktuelle vertikale Darstellung | Konkreter KI-Ursprung nicht eindeutig belegt |

## 3. K5 – Methodischer KI-Vorschlag und fachliche Gegenprüfung

**Ausgangssituation und KI-Unterstützung:** Nach der ersten Evaluation diskutierten Hanna und Patricia mit ChatGPT mögliche Weiterentwicklungen. Nach ihrer ausdrücklichen Schilderung schlug ChatGPT eine Erweiterung des regelbasierten Empfehlungssystems als möglichen zweiten CRISP-DM-Zyklus vor.

**Problem und kritische Prüfung:** Das Team wollte die bekannte Schwäche der Aktivitätsprognose durch eine erneute datengetriebene Modellierung untersuchen. Eine Änderung von Angebotsregeln kann fachlich sinnvoll sein, weist aber allein keine neue Schätzung und Evaluation eines Prognosemodells nach. Hanna und Patricia prüften deshalb, welche Forschungsfrage die vorgeschlagene Regeländerung tatsächlich beantworten würde. Sie verwarfen sie als Weg für diese konkrete erneute Modellierungsfrage, nicht als generell unzulässiges Verfahren.

**Korrektur und Ergebnis:** Stattdessen wurde die Zahl historischer Nullwochen in t−3 bis t als zusätzliches Regressionsmerkmal untersucht. Beide OLS-Varianten wurden in drei chronologischen Folds neu geschätzt. Die Erweiterung wurde wegen des höheren gepoolten MAE gemäß der vorab definierten UND-Regel verworfen. Der fachliche Anlass war die Nullzielschwäche aus Zyklus 1; die Prüfungsanforderung ersetzt diese Begründung nicht.

**Lerneffekt:** Ein plausibler Entwicklungsvorschlag muss auf Zielvariable, Lernverfahren und Aussagekraft seiner Evaluation geprüft werden. Eine Regelwirkungsanalyse und eine neue Modellgüteprüfung beantworten unterschiedliche Fragen.

**Repositorynachweis:** [recommendation_execution.md, §12](recommendation_execution.md) grenzt die Regelwirkung ausdrücklich von neuer ML-Evaluation ab. [cycle2/report.md, §§1, 4 und 5](cycle2/report.md), [Foldparameter](../outputs/cycle2/models/fold_parameters.json) und [Entscheidung](../outputs/cycle2/decision.json) belegen den tatsächlich gewählten Weg und sein Ergebnis. Sie beweisen nicht rückwirkend den ursprünglichen ChatGPT-Vorschlag.

**Nachweisstatus der KI-Zuschreibung:** Konkrete Zuschreibung an ChatGPT durch das Team; Originalgespräch, Datum und Wortlaut sind noch nicht als Primärbeleg archiviert. Keine wörtliche Aussage oder automatische Einstufung als KI-Halluzination wird erfunden.

## 4. K1 – Nicht öffentliche Streamlit-Test-API

**Ausgangssituation und KI-Unterstützung:** Im KI-unterstützten Aufbau der Streamlit-Prüfungen sollte das Verhalten des Session State kontrolliert werden. Ein früher Test verwendete laut Ausführungsbericht eine nicht öffentliche Session-State-Eigenschaft.

**Problem und kritische Prüfung:** Der Zugriff band die Testimplementierung an ein internes Detail statt an eine zugesicherte Schnittstelle. In der gemeinsamen Qualitätskontrolle wurde der fehlgeschlagene Ansatz anhand der verwendeten Streamlit-Version und des nachfolgenden Testverhaltens geprüft. Die Teamverantwortung ist gemeinsam; ein vollständiger persönlicher Debugging-Verlauf liegt nicht vor.

**Korrektur und Ergebnis:** Die Testimplementierung wurde auf die öffentliche Mapping-Schnittstelle umgestellt. Der historische Bericht dokumentiert anschließend bestandene Dashboardtests. Eine Änderung des Prognosemodells war dafür nicht erforderlich. Der Testcode und der Bericht werden in diesem Redaktionsauftrag nicht neu ausgeführt oder verändert.

**Lerneffekt:** Syntaktisch plausible Bibliotheksaufrufe müssen gegen Version und öffentliche API geprüft werden. Eine technische Testkorrektur ist keine neue fachliche Modellierungsiteration.

**Repositorynachweis:** [dashboard_execution.md](dashboard_execution.md), Absatz „Ein früher Dashboard-Testlauf …“ bei Zeilen 205–206 im vorhandenen Stand; aktuelle Zugriffe über `session_state[...]` in [tests/test_dashboard.py](../tests/test_dashboard.py).

**Nachweisstatus der KI-Zuschreibung:** Fehlversuch und Korrektur sind im Repository dokumentiert. Ob der konkrete interne Zugriff durch einen KI-Vorschlag, menschliche Bearbeitung oder ihr Zusammenwirken entstand, ist nicht abschließend belegt. Originalprompt und erster fehlerhafter Testzustand fehlen als gesonderter Primärbeleg.

## 5. K2 – Nicht vorgesehene README-Änderung

**Ausgangssituation und KI-Unterstützung:** Im KI-unterstützten Entwicklungsprozess wurde die README ergänzt, obwohl der betreffende Arbeitsschritt einen begrenzten Änderungsumfang und die Erhaltung des bestehenden Bestands vorsah.

**Problem und kritische Prüfung:** Ein AP6-Integritätstest erkannte die Abweichung. Hanna und Patricia behandeln diesen Befund als Qualitätskontrolle des vereinbarten Umfangs: Eine inhaltlich möglicherweise hilfreiche Ergänzung ist nicht automatisch im aktuellen Schritt zulässig. Die Schlussfolgerung folgt dem Integritätsvertrag, nicht einem Wunsch nach einer besseren Bewertung.

**Korrektur und Ergebnis:** Die README-Ergänzung wurde vollständig zurückgenommen; die Startanleitung blieb im vorgesehenen Dashboardbericht. Die bestehenden AP6-Tests wurden nicht umgeschrieben, um die Abweichung zu verdecken. Der heutige README-Inhalt allein wäre kein ausreichender Nachweis des früheren Rücknahmevorgangs.

**Lerneffekt:** Änderungsumfang, Integrität und technische Funktion müssen gemeinsam geprüft werden. Dokumentation darf bestehende Reproduzierbarkeitsverträge nicht stillschweigend verletzen.

**Repositorynachweis:** [dashboard_execution.md](dashboard_execution.md), Absatz zum „AP-6-Integritätstest“ bei Zeilen 207–208; die dort dokumentierte Startanleitung. Die spätere retrospektive Sportpassungsanalyse hat eine eigene, separat offengelegte Testausnahme und ist nicht mit diesem historischen Fall zu verwechseln.

**Nachweisstatus der KI-Zuschreibung:** Änderung, Testbefund und Rücknahme sind dokumentiert. Eine KI-Verursachung ist möglich, aber ohne ursprünglichen Vorschlag oder entsprechend zuordenbaren Änderungsverlauf nicht eindeutig nachgewiesen.

## 6. K3 – Mobile Phasenüberlagerung

**Ausgangssituation und KI-Unterstützung:** Die KI-unterstützt entwickelte Dashboardansicht sollte die CRISP-DM-Phasen verständlich darstellen. Die Desktopdarstellung allein reichte nicht als Nachweis der Lesbarkeit auf kleinen Bildschirmen.

**Problem und kritische Prüfung:** Bei der visuellen Mobilprüfung wurden überlagerte Beschriftungen der sechs Phasen erkannt. Die gemeinsame Qualitätskontrolle bezog deshalb neben dem erfolgreichen Programmstart die tatsächliche Lesbarkeit und den horizontalen Seitenüberlauf ein. Die konkrete Reihenfolge persönlicher Bedienhandlungen ist nicht einzeln protokolliert.

**Korrektur und Ergebnis:** Eine vertikale Phasendarstellung ersetzte die problematische Anordnung. Laut Bericht wurde anschließend auf Desktop und Mobil erneut geprüft, unter anderem bei 390 × 1000 Pixeln. Die aktuelle Funktion `crisp` verwendet eine vertikale Anordnung. Eine neue Browserprüfung wird hier nicht behauptet.

**Lerneffekt:** Erfolgreiche Ausführung und visuelle Nutzbarkeit sind verschiedene Qualitätsdimensionen. Automatisierte Funktionsprüfungen müssen für responsive Darstellungen durch Sichtkontrollen bei relevanten Bildschirmgrößen ergänzt werden.

**Repositorynachweis:** [dashboard_execution.md](dashboard_execution.md), Mobilprüfung bei Zeilen 775–783; aktuelle Funktion `crisp` in [dashboard/analytics_view.py](../dashboard/analytics_view.py). Historische temporäre Screenshots werden nicht als garantiert verfügbarer Repositorybeleg ausgegeben.

**Nachweisstatus der KI-Zuschreibung:** Darstellungsfehler und Korrektur sind dokumentiert. Der konkrete KI-Ursprung der ursprünglichen Anordnung ist nicht eindeutig nachgewiesen; aus der allgemeinen KI-Unterstützung folgt keine gesicherte Einzelursache.

## 7. Abgleich mit LN B und verbleibende Nachweisgrenzen

Die Originalunterlagen erlauben KI uneingeschränkt, verlangen im Lab-Log aber eine Reflexion von KI-Irrwegen und ihrer Prüfung. Kriterium 5 nennt außerdem begründete Entscheidungen und sichtbare Beiträge beider Teammitglieder; Kriterium 6 fordert die ehrliche Darstellung von Irrwegen. Die Kalibrierung unterscheidet fehlerfreie Reproduktion von eigenem tiefem Verständnis in der Live-Situation. Diese Kriterien werden zur Prüfung der Darstellung verwendet, nicht als nachträgliche Motivation der damaligen fachlichen Entscheidungen.

Die vier Fälle enthalten Ausgangssituation, Problem, gemeinsame Gegenprüfung, Korrektur, Ergebnis und Lernpunkt. Ihre technische Beleglage ist konkretisiert. **Vollständig abgesicherte KI-Zuschreibungen liegen dennoch nicht für alle Fälle vor:** Beim methodischen Vorschlag fehlt der archivierte Originalchat trotz ausdrücklicher Teamzuschreibung; bei den drei technischen Problemen ist die konkrete KI-Verursachung offen. Deshalb bleibt der entsprechende Teil des Qualitätschecks teilweise erfüllt. Es gibt keine Mindestanzahl erfundener Irrwege und keine automatische Notenverbesserung durch die Anzahl der Fälle.

Vor Abgabe können vorhandene Originalgespräche bzw. erste Diffs datensparsam ergänzt werden. Beide Autorinnen sollten unabhängig voneinander erklären können, warum der jeweilige Vorschlag oder Ansatz problematisch war und welche Kontrolle die Korrektur trägt. Ein schriftlicher Fallbericht wird nicht mit bereits nachgewiesener Live-Kompetenz gleichgesetzt. Die Identität der zwei Original-PDFs und der vollständige Kriterienabgleich sind im [Qualitätscheck](final_lab_log_quality_check.md) dokumentiert.
