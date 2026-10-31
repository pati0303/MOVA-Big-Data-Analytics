# MOVA – AP 5.7: abschließende Modellbewertung

Stand: 31.10.2026. Worktree `/workspace/MOVA-AP5`, Branch `ap5-machine-learning`,
Basis `1b26533d2ceea30478577bd519244c245dd3e558`. Aktive synthetische V2.
CRISP-DM 4.4 Assess Model, 5.1 Evaluate Results, 5.2 Review Process,
5.3 Determine Next Steps. Dieser Bericht bewertet ausschließlich gespeicherte
Ergebnisse. Keine neuen Modelle, Parameter, Prognosen oder Empfehlungsregeln.

## 1. Ziel, Evidenz und Gesamtentscheidung

Prüfen, ob die zwei Modelle für den synthetischen MOVA-Prototyp nutzbar sind,
welche Grenzen daraus für AP 6 folgen und welche Aussagen weiterhin unbelegt sind.
Quellen: K-Means-Ausführungsnachweis und Inferenzvertrag, Regressions-Ausführungsnachweis,
beide Modellmetadaten, Clusterzahlanalyse, Stabilitätsvergleich, finale Profile,
Testkennzahlen, Baselinekennzahlen und Einzelvergleich. Iterationsnachweise:
`crisp_dm_log.md` und `decisions.md`. Herkunftshashes dieser Quellen stehen in
`outputs/tables/modeling_evaluation_summary.json`.

| Modell | Entscheidung für synthetischen Prototyp | Produktiver Einsatz mit realen Garmin-Nutzern |
| --- | --- | --- |
| K-Means, k=2 | Für erste grobe Segmentierung geeignet, unter Inferenzvertrag | Noch nicht validiert |
| Globale lineare Regression | Nur eingeschränkt geeignet: unverbindliche Niveauprognose, keine präzise individuelle Zusage | Noch nicht validiert |

Dies ist eine begründete Freigabeempfehlung zur Prototyp-Konzeption, keine
Implementierung von AP 6 und kein Nachweis fachlicher Mindestgüte. Es wurde bisher
kein verbindlicher geschäftlicher Akzeptanzgrenzwert für individuelle Fehler festgelegt.
Die endgültige fachliche Abnahme bleibt eine gemeinsame Projektentscheidung.

## 2. Übersicht und tatsächlich erreichte Modellierungsziele

K-Means gruppiert 100 Nutzer anhand neun bereits standardisierter und gewichteter
Aktivitätsmerkmale. Regression verwendet zwei unskalierte Vergangenheitsmerkmale
(aktuelle Aktivitäten, Vierwochenmittel) für die Aktivitätszahl der nächsten Woche,
alle Sportarten gemeinsam. Ein globales Modell wurde auf 1.800 Nutzerwochen trainiert,
anschließend auf 400 chronologisch zurückgehaltenen Nutzerwochen bewertet.
Segmentierung, Regression und Baselinevergleich sind damit technisch und methodisch
im geplanten synthetischen Umfang umgesetzt. Personalisierte Empfehlungen und
Monetarisierung sind dadurch noch nicht nachgewiesen.

## 3. Abschließende K-Means-Bewertung

| Kennzahl | Gespeichertes Ergebnis |
| --- | --- |
| k | 2 |
| Nutzer | 100 |
| Silhouette | 0.30333715184382104 |
| Inertia | 126.49790652947819 |
| Clustergrößen | 57 / 43 |
| Paarweiser ARI Mittel/Minimum/Maximum | 1 / 1 / 1 |
| Seeds / Seed-Paare | 20 / 190 |

Die Kombination aus Elbow-Abflachung, höchstem untersuchten Silhouette-Score,
identischen Partitionen über 20 Seeds und ausreichend großen Gruppen begründet die
Teamentscheidung für k=2. Silhouette rund 0,3033 zeigt jedoch keine stark getrennten
natürlichen Nutzertypen. Inertia beschreibt Kompaktheit im gewählten gewichteten Raum,
keine allgemein interpretierbare Qualitätsquote. ARI=1 belegt Initialisierungsstabilität
bei unveränderten Daten und n_init=20, weder Stichprobenstabilität noch Generalisierung.

| Technische ID | Segment | n | Aktivitäten/Woche | Minuten/Woche | Vielfalt |
| --- | --- | --- | --- | --- | --- |
| 0 | Geringere Trainingshäufigkeit | 57 | 1.535088 | 97.054386 | 6.578947 |
| 1 | Höhere Trainingshäufigkeit | 43 | 3.747764 | 249.548569 | 7.441860 |

Die Gruppentexte wurden aus der tatsächlichen unskalierten Häufigkeitsrangfolge
abgeleitet, nicht aus einer angenommenen Bedeutung technischer IDs. Beide Gruppen
haben gemischte Sportartenanteile; K-Means beschreibt überwiegend das Aktivitätsniveau.
Es identifiziert keine Fitness, gesundheitliche Leistungsfähigkeit oder sportliche
Erfahrung und keine klar sportartspezialisierten Nutzergruppen.

Für eine erste grobe Einordnung ist das Modell geeignet. Es ersetzt weder die
persönlichen Sportpräferenzen noch eine fachlich geprüfte Empfehlungslogik.
Sportanteile sind kompositionell, Standardisierung und 1/√8-Blockgewichtung eine
fachliche Startannahme. K-Means bevorzugt kompakte Gruppen, reagiert auf extreme
Werte und wurde intern auf denselben 100 Nutzern bewertet, auf denen es angepasst
wurde. Keine unabhängige neue Nutzerpopulation wurde hierfür verwendet.

## 4. Regression und Persistenz-Baseline

| Kennzahl | Regression | Persistenz |
| --- | --- | --- |
| MAE | 1.489877057523 | 1.710000000000 |
| RMSE | 1.908537654537 | 2.310844001658 |
| Mittlerer Fehler, Prognose minus Ziel | 0.041382906274 | 0.020000000000 |
| Größter absoluter Fehler | 6.312285940594 | 10.000000000000 |

Absolute MAE-Verbesserung: 0.220122942477 Aktivitäten pro Nutzerwoche.
Relative MAE-Verbesserung: **12.872686695 %**.

Die Regression verbessert die durchschnittliche absolute Abweichung gegenüber der
vorab festgelegten Persistenzregel. Der niedrigere RMSE spricht zusätzlich für eine
Verringerung großer Fehler im Mittel. Der leicht positive Gesamtfehler bedeutet eine
kleine gepoolte Überschätzung; er kann hohe gegenläufige Einzelabweichungen verdecken.
Die Baseline hat sogar den kleineren Betrag des Gesamt-Vorzeichenfehlers.

| Zielwoche | n | MAE Regression | MAE Persistenz | Relative MAE-Verbesserung |
| --- | --- | --- | --- | --- |
| 23 | 100 | 1.568914442 | 1.630000000 | 3.747580 % |
| 24 | 100 | 1.336618421 | 1.760000000 | 24.055772 % |
| 25 | 100 | 1.536849076 | 1.690000000 | 9.062185 % |
| 26 | 100 | 1.517126291 | 1.760000000 | 13.799643 % |

In allen vier Testwochen sind MAE und RMSE der Regression niedriger; der MAE-Vorteil
schwankt zwischen rund 3,75 % und 24,06 %. Das ist ein konsistenter deskriptiver Vorteil
innerhalb dieser vier Wochen, keine nachgewiesene statistische Signifikanz oder
Garantie für spätere Zeiträume.

Bei 229 von 400 Einzelprognosen (57,25 %) ist die Regression besser, bei 171
(42,75 %) Persistenz; keine Gleichstände. Median des absoluten Regressionsfehlers
rund 1,233754, 95-%-Quantil 3,766682, Maximum 6,312286; elf Fehler überschreiten fünf
Aktivitäten. U036/Zielwoche 26: tatsächlich acht, Prognose rund 1,687714. Individuelle
Zusagen lassen sich aus dem besseren Gesamt-MAE deshalb nicht begründen. Keine
negativen Prognosen beobachtet, aber die lineare Modellfamilie garantiert allgemein
weder ganzzahlige noch nichtnegative Zählungen. Keine Nachbearbeitung eingeführt.

## 5. Nullwochen-Schwäche und ergänzende Diagnose

### Gruppierung nach tatsächlich bekannt gewordenem Ziel

| Zielgruppe | n | MAE Regression | MAE Persistenz | Relative MAE-Verbesserung |
| --- | --- | --- | --- | --- |
| Ziel = 0 | 92 | 1.878292396 | 1.380434783 | -36.065276 % |
| Ziel > 0 | 308 | 1.373856891 | 1.808441558 | 24.030894 % |

Bei den 92 tatsächlichen Nullzielen ist die Regression nach MAE **36,07 % schlechter**;
bei 308 positiven Zielen verbessert sie den MAE um **24,03 %**. Dies ist ein wichtiger
fachlicher Nachteil, der im Gesamtergebnis nicht verschwinden darf. Der Nullziel-RMSE
ist dennoch etwas niedriger (2,031267 statt 2,149317); die Verfahren unterscheiden
sich somit je nach Fehlermaß. Keine uneingeschränkte Überlegenheit behauptet.

**Hypothesen, keine nachgewiesenen Ursachen:** Der positive Intercept und das geglättete
Vierwochenniveau können nach Ruhephasen positive Prognosen erzeugen. Persistenz
trifft bei aufeinanderfolgenden Nullwochen exakt. Kurzfristige Rückgänge, längere
Pausen, globale Mittelung und individuelle Dynamiken könnten zur Schwäche beitragen.
Es wurden weder konkrete Pausengründe noch reale fehlende Aufzeichnungen untersucht.
Eine beobachtete Null belegt weder Krankheit noch Motivation oder Fitness.

### Rein diagnostisch: zum Prognosezeitpunkt bekannte aktuelle Woche

Gruppierung aus der vorhandenen Vergleichstabelle; keine neuen Merkmale, Modelle,
Prognosen oder Auswahlregeln. Diese zusätzliche Analyse ist post hoc und explorativ.

| Bekannter Eingang | n | MAE Regression | MAE Persistenz | RMSE Regression | RMSE Persistenz | Relative MAE-Verbesserung |
| --- | --- | --- | --- | --- | --- | --- |
| activities_current_week = 0 | 96 | 1.113851161 | 1.302083333 | 1.482046803 | 2.007797301 | 14.456231 % |
| activities_current_week > 0 | 304 | 1.608622077 | 1.838815789 | 2.024639319 | 2.398601566 | 12.518585 % |

Bei aktuell null Aktivitäten hat die Regression hier niedrigeren MAE und RMSE als
Persistenz, ebenso bei aktuell positiven Aktivitäten. Die bekannten aktuellen
Nullwochen (96) sind nicht dieselbe Gruppe wie die zukünftigen Nullziele (92).
Die aktuelle Null als einfache Umschaltregel auf Persistenz wird durch diese
Ergebnisse nicht gestützt. Eine solche Regel wird ausdrücklich nicht entwickelt.

Der Vergleich nach dem aktuellen Eingang ist für eine Anwendung relevanter, weil
Woche t zum Prognosezeitpunkt abgeschlossen und bekannt ist; das Ziel t+1 ist es
noch nicht. Die nach Ziel gebildeten Fehlergruppen sind zur Problemdiagnose sinnvoll,
können aber nicht zur Auswahl einer Prognose genutzt werden. Auch die Eingangsanalyse
liefert keine belastbare Regel für neue Nutzer: sie ist auf demselben eingesehenen
Test durchgeführt und darf nicht zur nachträglichen Optimierung missbraucht werden.

## 6. Nutzen und fehlende Bausteine für MOVA

K-Means kann eine grobe relative Aktivitätseinordnung bereitstellen, Regression
allenfalls ein unverbindliches erwartetes Wochenaktivitätsniveau. Kein Modell
prognostiziert konkrete Sportarten oder passende Angebote. K-Means und Regression
erzeugen noch keine konkreten Empfehlungen. Das regelbasierte Empfehlungssystem
wird erst in **AP 6** umgesetzt. **Ein zusätzlicher finanzieller Nutzen ist noch nicht
nachgewiesen**: keine Umsatz-, Zahlungsbereitschafts-, Nutzungs- oder Wirkungsprüfung.

Für Individualisierung fehlen insbesondere die explizite Verknüpfung individueller
Sportpräferenzen mit Angeboten und freiwillig angegebenen Interessen, eine transparente
Regelpriorisierung und eine spätere Bewertung der Empfehlungsrelevanz. Sportanteile
beschreiben tatsächlich beobachtetes Verhalten, freiwillige Interessen zusätzliche
Selbstauskünfte; beides ist auseinanderzuhalten. Nicht angegebene Interessen bedeuten
nicht automatisch Ablehnung. Interessen wurden nicht für Modelltraining verwendet.

K-Means benötigt nach dem Inferenzvertrag 26 verlässlich vollständig erfasste Wochen.
Vollständig inaktive Nutzer haben undefinierte Sportanteile und erhalten einen
separaten Status ohne erfundene Zuordnung. Weniger oder unvollständig beobachtete
Nutzer dürfen nicht automatisch in eine Standardgruppe fallen. Regression benötigt
vier vollständig beobachtete Eingabewochen einschließlich t und korrekte zeitliche
Verfügbarkeit; bei fehlender Historie keine erfundene Nullauffüllung. Ein eigenständiger
produktiver Regressionsvertrag mit Importprüfung ist noch nicht implementiert.

App-Integration muss Vollständigkeit und Kalender-/Zeitzonengrenzen nachweisen,
K-Means exakt mit gespeicherten Parametern transformieren, Regression ohne zusätzliche
Skalierung mit ihren zwei Eingängen versorgen und technische IDs über gespeicherte
Metadaten auflösen. Eine ausreichende Historienlänge beweist keine Ähnlichkeit zu den
synthetischen Trainingsdaten. Beobachtete Aktivitätszahl ist keine physiologische
Intensität, Fitnessmessung oder gesundheitliche Trainingsvorgabe.

## 7. CRISP-DM-Rückblick und tatsächliche Iteration

| Phase | Nachweis und Bewertung |
| --- | --- |
| Business Understanding | Hochschulziel: nachvollziehbarer datenbasierter Personal Advisor. Segmentierung und Wochenprognose als technische Teilziele erreicht; Empfehlungssystem und finanzieller Nutzen offen. |
| Data Understanding | Synthetische Nutzerunterschiede, Sportmix und Nullwochen beschrieben. Grenzen künstlicher Daten und fehlender realer Messbedingungen transparent. |
| Data Preparation | AP 4: vollständiges 100×26-Raster, Nullwochen, neun gewichtete K-Means-Eingänge sowie zeitlich getrennte Regressionsfenster/Labels; unabhängiges Inhaltsaudit und Hashnachweise. Kein erneutes Datenaufbereiten hier. |
| Modeling | k-Vergleich und Initialisierungsstabilität, empirisch begründete Wahl k=2; globale OLS nur auf 1.800 Trainingsbeobachtungen; Inferenzvertrag dokumentiert. |
| Evaluation | K-Means intern bewertet, kein unabhängiger Nutzertest. Regression auf 400 chronologisch zurückgehaltenen Beobachtungen und identischer Persistenzbaseline bewertet. Fachliche Abnahme bleibt auf synthetischen Prototyp begrenzt. |

Alle Artefakte und Auswertungen sind in ihrer dokumentierten Umgebung reproduzierbar;
frühere Tests umfassen Solver-/Profilkontrollen und Model-Reload. Unabhängige
Kontrollrechnungen sind technische Korrektheitsnachweise und ersetzen keine unabhängige
Population. Für Regression sind die Testziele zeitlich zurückgehalten, die Nutzer aber
bekannt; Testbeobachtungen innerhalb eines Nutzers sind abhängig. Modelle wurden
nicht nachträglich auf dem Test angepasst.

**Tatsächlich dokumentiert: MOVA-ITER-001 am 29.10.2026.** Data Understanding/AP 2.4
führte zurück zu Construct Data/AP 2.3 und erneuter Qualitätsprüfung: persönliche
Sportpräferenzen moderat mit Exponent 1,3 verstärkt; V2 später verbindlich übernommen.
Die Trennung der Zufallsquellen wurde durch eine Kontrolle mit Exponent 1,0 geprüft.
Nur der gepaarte Kontrolle→V2-Vergleich isoliert den Exponenteneffekt; Änderungen der
Aktivitäts-/Nullwochenzahlen gegenüber V1 stammen aus der technischen Zufallsumstellung.
Die Iteration validiert keine reale Modellqualität. Historische Einleitungstexte in
Vorlagen dokumentieren den damaligen Stand und widersprechen späteren Einträgen nicht.

GitHub-/Proxy-/Worktree-Probleme sind technische Korrekturen, keine zusätzlichen
fachlichen CRISP-DM-Iterationen. K-Auswahl und Stabilitätsanalyse sind geplante
Modellierungsschritte, keine hier neu behaupteten Rücksprünge. AP 5.7 hat keine
weitere Iteration durchgeführt.

## 8. Potenzielle spätere Iterationen – nicht umgesetzt

- Trainingspausen und Aufzeichnungslücken fachlich unterscheiden und einen prüfbaren Umgang planen.
- Weitere vergangenheitsbezogene Merkmale vorab begründen, ohne zukünftige Information.
- Längere Beobachtungszeiträume und zusätzliche spätere Testperioden untersuchen.
- Evaluation auf vollständig neuen Nutzern, getrennt vom bisherigen Known-User-Szenario.
- Reale Daten nur nach freiwilliger Einwilligung, geeigneter Datenqualität und Datenschutzkonzept validieren.

Keine dieser Verbesserungen wurde in AP 5.7 implementiert. Das jetzt mehrfach
betrachtete Testset ist für unkontrollierte weitere Optimierung verbraucht.
Mögliche Änderungen müssen als kontrollierte spätere Iteration mit zeitlicher
Validierung innerhalb des Trainingsbestands und neuer unberührter Abschlussbewertung
geplant werden. Keine Garantie, dass diese Vorschläge die Güte verbessern.

## 9. Technische Validierung und Reproduzierbarkeit

Neues Skript `src/modeling_evaluation_summary.py` liest die Quellen, prüft
K-Means-Metadaten gegen k-Analyse/Stabilität/Profile, Regression gegen AP 5.5/5.6,
Gruppen-/Wochenkennzahlen gegen die vorhandene Vergleichstabelle sowie Modell- und
Quellhashes. Es lädt keine Modellobjekte, ruft kein predict auf und führt keinen Fit
aus. Keine ursprünglichen Ergebnisdateien überschrieben.

`tests/test_modeling_evaluation_summary.py`: fünf Tests für Auswertung ohne
Joblib-Load/Training/Predict, exakte Übernahme ursprünglicher Kennzahlen, unabhängige
Berechnung der Eingangsdagnose und Erkennung widersprüchlicher K-Means-/Regressionswerte.
`python -m unittest discover -s tests -p 'test_modeling_evaluation_summary.py' -v`:
**fünf neue Tests bestanden**. Frühere Trainings-Tests nicht erneut gestartet.

Zwei vollständige Auswertungen tatsächlich ausgeführt. Die Kennzahlendatei ist
**bytegleich**; auch die Diagnoseprotokolle (`work/ap57_run1.json`, `work/ap57_run2.json`)
sind identisch. Bei abweichender vorhandener Zusammenfassung erfolgt Abbruch ohne
Überschreiben. Alle vor AP 5.7 vorhandenen Dateien wurden abschließend per SHA-256
als unverändert bestätigt, einschließlich beider Modelle und aller bisherigen
Evaluationsdateien. Kein Commit und kein Pull Request.

## 10. Freigabeempfehlung für AP 6 und offene Entscheidung

**AP 6 kann mit der Konzeption des regelbasierten synthetischen Prototyps fortfahren.**
K-Means als grobe Aktivitätssegmentierung verwenden, Regression nur eingeschränkt
als optionales Kontextsignal mit transparenten Grenzen. Keine individuelle
Aktivitätsvorgabe aus dem Modell ableiten und kein finanzielles Ergebnis versprechen.
Persönliche Sportpräferenzen und freiwillige Interessen müssen die spätere
Individualisierung tragen; Fälle mit unzureichender Datenlage gesondert behandeln.

Vor Umsetzung gemeinsam fachliche Ziele, akzeptable Fehlertoleranz, Behandlung
unzureichender Historie und die Rolle der unsicheren Wochenprognose festlegen.
Keine Baseline-Umschaltung nach unbekannten zukünftigen Nullzielen. Kein produktiver
Einsatz mit echten Garmin-Nutzern freigegeben. Die Modelle bleiben unverändert;
die abschließende gemeinsame Modellbewertung und AP-6-Regeln stehen als fachliche
Projektentscheidungen noch aus.
