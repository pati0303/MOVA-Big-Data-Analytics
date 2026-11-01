# MOVA – Dashboard-Ausführung AP 7.2

Stand: 01.11.2026. Worktree `/workspace/MOVA-AP7`, Branch `ap7-dashboard`, Basis
`23ac008651de490d59e9ec5ceae590ba97daf0e5`. Verbindliche Grundlage:
[dashboard_concept.md](dashboard_concept.md).

## 1. Implementierte Struktur

- `app.py`: Streamlit-Einstieg, Kopfbereich, Moduswahl, globale Nutzerwahl und Freigaben.
- `dashboard/state.py`: Initialisierung, Nutzerwechsel, Freigabewechsel, Zugriffsstatus; unabhängig von Streamlit testbar.
- `dashboard/data_access.py`: Projektpfade, validierte Nutzer-IDs und lokale Git-Basisprüfung.
- `dashboard/services.py`: vorbereiteter Aufruf der bestehenden Engine, keine eigene Fachlogik.
- `dashboard/components.py`: Karten, Abschnittstitel und wiederverwendbarer Experimentrahmen.
- `dashboard/design.py`, `dashboard/styles.css`: zentrale Designwerte und lokale Darstellung.
- `dashboard/views.py`: User View und sieben vorbereitete Lab-Bereiche.
- `.streamlit/config.toml`: dunkles Theme, lokaler Server, deaktivierte Nutzungsstatistik.
- `requirements-dashboard.txt`: direkte UI-Versionen und unveränderte Modellanforderungen.
- `requirements-dashboard-lock.txt`: vollständig aufgelöste Paketversionen der geprüften Umgebung.
- `tests/test_dashboard.py`: Daten-, Zustands-, Integrationsadapter- und Streamlit-Tests.
- Dieses Dokument enthält die geprüfte lokale Startanleitung; die bestehende README bleibt unverändert.

Die vorhandenen AP-1–AP-6-Quellen werden nicht verändert. Das AP-7.1-Konzept bleibt erhalten.
Es gibt keine Datenbank, API-Schicht, Cloud-Anbindung oder zusätzliche Modellimplementierung.

## 2. Technologien und Installation

Streamlit für UI und Session State; Plotly für die spätere interaktive Visualisierung.
In AP 7.2 wird kein künstliches Demonstrationsdiagramm erzeugt. Der gemeinsame
Plotly-Stil ist vorbereitet und nutzt später tatsächliche Projektdaten.
Python 3.12.14; isolierte `.venv` im AP-7-Worktree. Die Pakete des System-Python und
vorherige Arbeitsbereiche werden nicht verändert.

Der erste Paketdownload scheiterte am eingeschränkten Netzwerkzugriff. Die Installation
wurde anschließend über den vorgesehenen Netzwerkzugang mit erhaltenen Proxy-/TLS-Einstellungen
wiederholt. Ein echter Abhängigkeitskonflikt wurde erkannt: Streamlit 1.51.0 verlangt
`packaging<26`, während die validierte Modellumgebung `packaging==26.3` festlegt.
Daher wurde Streamlit 1.66.1 gewählt, ohne Modellbibliotheken oder deren Requirements
zu ändern. Plotly ist auf 6.4.0 festgelegt.

## 3. Versionsstände und Reproduzierbarkeit

Direkte UI-Pakete: `streamlit==1.66.1`, `plotly==6.4.0`.
Modellumgebung: NumPy 2.3.5, SciPy 1.17.0, pandas 2.2.3, scikit-learn 1.8.0,
joblib 1.5.3; alle weiteren Vorgaben aus `requirements-modeling.txt` unverändert.
Die separate Dashboard-Requirements-Datei inkludiert diese Datei. Die bisherige
allgemeine `requirements.txt` bleibt als historischer Projektbestand unverändert;
für das Dashboard ist ausdrücklich die neue Datei zu verwenden.

`requirements-dashboard-lock.txt` fixiert zusätzlich die transitiven Versionen.
Der Lock beschreibt die geprüfte Python-3.12-Linux-Installation; er ist kein
plattformunabhängiger Wheel-/Hash-Lock. Pip prüft für andere Systeme die Verfügbarkeit.
Für eine Wiederholung dieselbe Python-Haupt-/Nebenversion verwenden.

## 4. Designsystem

MOVA / Move beyond. mit lokalem Wort-/Pfeilzeichen. Hintergrund `#0B1110`, Karten
`#14201C`, Text `#F2F7F4`, sekundär `#B4C6BC`, Akzent `#7DE2A6` und Rahmen `#30483B`.
Dezenter Verlauf im Begrüßungsbereich, großzügige Abstände, abgerundete Karten,
klare Ebenen und wiederverwendbare Abschnittskennungen. Systemschrift statt externem
Fontdownload; keine Fotos, CDN-Assets oder Animationen. Die CSS-Regeln betreffen
ausschließlich eigene MOVA-Klassen; native Widgets nutzen das öffentliche Theme.

User View betont Aktivität und Möglichkeiten. Analytics Lab hat eine eigene Leitfrage,
Forschungsnavigation, Rechenschritte, Erkenntnis-Karte und Quellenbereich. Einheitliche
Plotly-Farben sind vorbereitet. Responsive Streamlit-Spalten und eine CSS-Regel für
kleine Fenster ergänzen das Desktoplayout. Status wird immer auch als Text gezeigt.

## 5. Navigation

Permanenter Kopf mit Modusumschalter `USER VIEW` / `ANALYTICS LAB` und Nutzerwahl.
Streamlit-Reruns erfolgen innerhalb desselben Servers. Im Lab führt die Seitenleiste
zu Data Understanding, Data Preparation, K-Means, Regression, Evaluation,
Empfehlungssystem und CRISP-DM. Nur die gewählte Ansicht und der gewählte Bereich
werden dargestellt. Keine vorgetäuschten Live-Berechnungen: Rechenwege und Quellen
sind als Planung für AP 7.4 gekennzeichnet.

## 6. Nutzerauswahl und Datenvalidierung

Die Auswahl liest ausschließlich echte Kennungen aus `data/raw/users_simulated.csv`.
Die aktive V2, deren Nutzerdatei-SHA-256, exakte Spalten, 100 eindeutige Kennungen
U001…U100 und gültige Interessenbooleans werden geprüft. Zurückgegeben werden nur
IDs; Interessen werden vom Grundgerüst nicht angezeigt. Kein Ersatzdatensatz und
keine erfundenen Profile bei Fehlern. Ein Quellenfehler zeigt eine verständliche
Meldung und beendet die Darstellung vor den Bedienelementen.

Pfadermittlung relativ zu `dashboard/data_access.py` statt relativ zum Prozessverzeichnis.
Alle wissenschaftlichen und persönlichen Dateien bleiben im bestehenden Projektbestand.
Keine Aktivitäts-, Cluster- oder Modelldatei wird vom Grundgerüst eingelesen.

## 7. Session State

Dauerhafte Schlüssel: `selected_user_id`, `mode`, `lab_section`,
`interests_permission`, `garmin_permission`. Der Lab-Radiowidget-Schlüssel
`lab_widget` ist von `lab_section` getrennt, damit Streamlits Bereinigung ausgeblendeter
Widgets den gewählten Forschungsbereich nicht verliert.

Moduswechsel erhält Nutzer und Freigaben desselben Nutzers. Nutzerwechsel setzt beide
Freigaben vor dem nächsten Rendern auf False und entfernt vorgesehene persönliche
Antwort-/Aktivitäts-/Fehlerfelder. Jede Freigabeänderung entfernt alte persönliche
Antworten vor dem neuen Rendern. Die zentralen Zustandsfunktionen sind der verbindliche
Pfad für die spätere Integration; zukünftige persönliche Session-Felder müssen in
deren Löschliste aufgenommen werden. Derzeit werden keine persönlichen Resultate gespeichert.

Keine globalen persönlichen Caches. Nutzer-IDs werden bei jedem Rerun erneut geprüft.
Dadurch kann kein vorheriger Engine-Response aus einem Cache erscheinen. Persönliche
Daten in AP 7.3 nur nach expliziter Freigabe über den gemeinsamen Service laden.

## 8. Simulierte Freigaben und Abgrenzung des Labs

Initial False/False; zwei unabhängige, permanent sichtbare Schalter mit eindeutiger
Simulationsbeschriftung. Kein echter Einwilligungsnachweis, OAuth oder Garmin-Zugriff.
Ohne Garmin-Freigabe sind Aktivität, Sportprofil, Segment und Prognose in der User
View als gesperrt markiert. Ohne Interessenfreigabe bleibt der Angebotsbereich gesperrt.
Mit Freigabe erscheint weiterhin nur der klare Hinweis auf die noch fehlende Integration,
keine erfundene Kennzahl, Prognose oder Angebotsliste.

Das Lab erhält durch den Moduswechsel keine Rechte. In AP 7.2 zeigt es ausschließlich
fachliche Beschreibungen und Quellenpfade. Zukünftige aggregierte Forschungsauswertungen
müssen von individuellen Informationen getrennt sein; individuelle Testfall-/Engine-
Demonstrationen dürfen die gleichen Freigabesperren nicht umgehen. Ein historischer
AP-6-Vergleich unter festen True/True-Bedingungen muss später explizit als solcher
ausgewiesen werden. Sein Experimentzustand darf niemals die aktuellen persönlichen
Freigaben verändern.

## 9. Vorbereitete Engine-Anbindung und Git-Basis

`dashboard/services.py:recommendation_context` verlangt zwei explizite Python-bools
und delegiert an `recommendation_engine.run` mit Projektwurzel und historischem
`date(2026, 7, 5)`. Featurebildung, Modelle, Status, Rangfolge und Top-5-Grenze bleiben
allein in der bestehenden Engine. Der Adapter implementiert keine Matchingformel,
keinen Fit und keine eigene Prognose. Bei Ausnahmen liefert er einen verständlichen
Fehler, keine alte Nutzerantwort. Das Grundgerüst ruft diesen Adapter noch nicht auf.

Der Dashboard-Vertrag `documentation/recommendation_dashboard_contract.md` wurde
berücksichtigt: unabhängige Freigaben, Status vor Zahlendarstellung, null nicht durch
0 ersetzen, unveränderte Rangfolge und getrennte Modellkontexte. Die vollständige
Statusübersetzung und Resultatdarstellung erfolgen in AP 7.3.

Die vorhandene Engine benötigt für manche Quellen lokale Objekte des Basiscommits
`a8f97ad75c378329a614a322bd541f372de0b072`. Die App prüft mit lokalen
`git cat-file -e`-Aufrufen die drei benötigten Pfade ohne Netzwerkzugriff. Diese
Objekte liegen im aktuellen Worktree-Verbund vor. Daher ist keine Loaderänderung
nötig. Für Kopien den vollständigen Repository-/Git-Bestand erhalten; kein flacher
CSV-/App-Export. Bei fehlender Git-Basis bleibt das Grundgerüst nutzbar und zeigt
im technischen Status eine Warnung. Vor AP 7.3 muss die Basis wiederhergestellt sein;
Prüfungen werden nicht deaktiviert und Hashwerte nicht ersetzt.

## 10. Lokaler Start

Vom Repository-Stammverzeichnis `/workspace/MOVA-AP7`:

```bash
python --version  # geprüft mit Python 3.12.14
python -m venv .venv
.venv/bin/python -m pip install -r requirements-dashboard.txt
.venv/bin/python -m pip check
.venv/bin/python -m streamlit run app.py
```

Für die vollständige Wiederholung der aufgelösten Versionen stattdessen:

```bash
.venv/bin/python -m pip install -r requirements-dashboard-lock.txt
```

Windows: `.venv\Scripts\python.exe` statt `.venv/bin/python`. Ein Shell-`PYTHONPATH`
ist für den App-Start nicht notwendig. Die Engine-Anbindung fügt den bestehenden
`src`-Pfad erst bei ihrem expliziten Aufruf hinzu.

Lokale URL `http://127.0.0.1:8501`. Beenden mit `Ctrl+C`. Der Server ist absichtlich
an die lokale Loopback-Adresse gebunden. Eine lokale URL innerhalb dieser Cloud-
Umgebung ist nicht automatisch im Browser des eigenen Laptops erreichbar; dort
Projekt und Umgebung lokal starten. Kein öffentlicher Deployment-Schritt durchgeführt.

Bei belegtem Port: `... streamlit run app.py --server.port 8502` und entsprechende
URL verwenden. Bei `ModuleNotFoundError` die `.venv` und Dashboard-Requirements prüfen.
Bei Nutzerquellenfehlern Originaldatei und V2-Manifest wiederherstellen. Bei Git-Warnung
vollständige Historie prüfen; keine Rohdaten oder Modelle zur Fehlerbehebung ändern.
Nach erfolgreicher Installation werden für die App keine externen Dienste benötigt.

## 11. Tests und Startprüfung

Prüfbefehle:

```bash
mkdir -p work
PYTHONDONTWRITEBYTECODE=1 OPENBLAS_NUM_THREADS=1 .venv/bin/python -m unittest discover -s tests -p 'test_dashboard.py' -v
PYTHONDONTWRITEBYTECODE=1 OPENBLAS_NUM_THREADS=1 .venv/bin/python -m unittest discover -s tests -p 'test_recommendation*.py' -v
```

Die AP-6-Tests benötigen das ignorierte temporäre Verzeichnis `work/`.
Keinen vollständigen ungeprüften Modelltestlauf starten: einzelne vorhandene Tests
könnten Trainingspfade ausführen. Die gezielten AP-6-Tests prüfen ausbleibenden Fit.

Tatsächlich ausgeführt: **18 Dashboardtests bestanden**, einschließlich vier
Streamlit-AppTest-Fällen. Die Reruns prüfen User View, alle sieben Lab-Bereiche,
Nutzererhalt und Bereichserhalt beim Moduswechsel, unabhängige Schalter, Zurücksetzen
beim Nutzerwechsel, Entfernen alter persönlicher Session-Daten bei Freigabeentzug
und verständlichen Quellenfehler ohne Ersatzdaten. Adaptertests prüfen die exakte
Delegation an die vorhandene Engine und deren Fehlerpfad.

**42 vorhandene AP-6-Tests bestanden** (25 Engine-, 11 Vergleichs-, 6 Vertragstests).
Gesamt: **60 bestandene Tests, keine übersprungenen Tests, kein Fehler**.
`pip check`: keine defekten Anforderungen. Ein früher Dashboard-Testlauf nutzte
zunächst eine nicht öffentliche Session-State-Eigenschaft der neuen Streamlit-Version;
der Test verwendet jetzt die öffentliche Mapping-Schnittstelle. Ein AP-6-Integritätstest
wies auf eine ergänzte README hin; diese eigene Ergänzung wurde vollständig
zurückgenommen, die Startanleitung steht ausschließlich hier. AP-6-Testcode bleibt
unverändert.

Der tatsächliche Start mit `.venv/bin/python -m streamlit run app.py` funktioniert.
Die Umgebung benötigt für lokale Sockets den vorgesehenen Netzwerkzugang; ein erster
Start unter engerem Prozess-Sandboxprofil scheiterte mit `PermissionError`, der
anschließende Start mit verfügbarem Netzwerkzugang läuft auf `127.0.0.1:8501`.
Das ist eine Ausführungsbeschränkung dieser Cloud-Sandbox, keine zusätzliche lokale
App-Abhängigkeit.

Chromium wurde über das vorhandene Playwright und `/usr/bin/chromium` verwendet,
ohne diese Testwerkzeuge als App-Abhängigkeiten hinzuzufügen. User View, Analytics Lab
und dessen Data-Preparation-Navigation wurden tatsächlich im Browser geprüft.
Zusätzlich wurde im Browser U042 ausgewählt, beide Freigaben einzeln aktiviert,
der Nutzer beim Ansichtswechsel erhalten und anschließend beim Wechsel zu U003
das Zurücksetzen beider Freigaben geprüft. Der Health-Endpunkt
`/_stcore/health` antwortete mit HTTP 200.
Screenshots in 1440×1100, 1366×900 und 390×844 wurden erzeugt und visuell gelesen: beide
Ansichten gut lesbar, Mobilansicht gestapelt, kein horizontaler Überlauf und keine
JavaScript-Seitenfehler. Temporäre Browserbilder und Prüfprotokolle stehen ignoriert
unter `work/ap72-*`; sie sind keine neuen Fachdaten.

## 12. Offene Punkte und Übergabe

AP 7.3 verbindet echte Aktivitätskennzahlen/-charts, gespeichertes Segment, Engine-
Prognose für 06.–12.07.2026 und maximal fünf tatsächliche Empfehlungen. AP 7.4
implementiert die fachlichen Experimente. Die Platzhalter werden dabei durch
statusabhängige echte Ausgaben ersetzt, nicht mit Beispieldaten gefüllt.

Git-Objektabhängigkeit bleibt eine bewusste lokale Projektvoraussetzung. Die
Simulation ist keine produktive Garmin-Anbindung und besitzt keine echte
Authentifizierungs-/Einwilligungsverwaltung. Das Gerüst ist kein Nachweis für reale
Modell- oder Empfehlungsqualität. Keine Modelle trainiert, keine Rohdaten erzeugt,
kein Commit und kein Pull Request erstellt.

**AP 7.3 kann mit diesem getesteten Grundgerüst beginnen.**

## Abschließende Integrität

Nach Installation, Tests und Browserprüfung wurden alle 168 versionierten Dateien
gegen den Basiscommit per Git-Blobhash geprüft: **keine Abweichung**. Damit sind
Rohdaten, Modellartefakte, Engine, Angebote, Tagfreigaben, bestehende Tests und
Dokumentationen aus AP 1–6 unverändert. Der vorherige Worktree ist sauber.
AP 7.2 fügt 14 neue Dateien hinzu; zusammen mit dem noch unversionierten AP-7.1-Konzept
liegen 15 neue Dateien vor. `.venv/`, Protokolle, Browser-Skripte und Screenshots
sind durch die vorhandenen Ignore-Regeln ausgeschlossen. HEAD und Branch bleiben
auf der angegebenen Basis; kein Commit, Push oder PR durchgeführt.

# Fortschreibung AP 7.3 – integrierte MOVA User View

Stand: 01.11.2026. Die vorstehenden AP-7.2-Abschnitte bleiben als historischer
Ausführungsnachweis erhalten. Die dort noch geplante User-View-Integration ist mit
folgendem Stand umgesetzt. Aktueller Branch `ap7-dashboard`, HEAD
`33e889c11837a8e878b039835f0e9faf4de21850` enthält den separat beauftragten früheren
Screenshot-Commit, keine App-Implementierung. In AP 7.3 wurde kein neuer Commit,
Push oder Pull Request erstellt.

## 13. Verwendete Quellen und tatsächliche Schemas

- `data/raw/users_simulated.csv`: 100 Zeilen; `user_id`, `interest_sport`,
  `interest_outdoor`, `interest_wellness`, `interest_leisure`. Weiterhin validierte
  IDs für die gemeinsame Auswahl; freigegebene Kategorien stammen aus der Engine.
- `data/raw/activities_simulated.csv`: 6.465 Aktivitäten; `activity_id`, `user_id`,
  `date`, `sport_type`, `duration_min`, `distance_km`. Acht tatsächlich vorkommende
  Sportarten. Die Sportverteilung zählt beobachtete Aktivitäten, nicht Vorlieben.
- `data/processed/user_weekly_activities.csv`: 2.600 vollständige Nutzerwochen;
  `user_id`, `week_index`, `week_start`, `week_end`, `activities_count`,
  `total_duration_min`. Exakt 26 aufeinanderfolgende Wochen je Nutzer.
- `data/processed/kmeans_user_features.csv`: 100 Profile mit ID, Häufigkeit,
  acht Sportanteilen und zwei Interpretationsmerkmalen. Verwendung durch die
  vorhandene Engine, kein neues Feature Engineering im Dashboard.
- `data/processed/user_clusters.csv`: 100 gespeicherte Zuordnungen mit `user_id`,
  `cluster_id`, `segment_label`. Abruf durch die bestehende Engine.
- `outputs/models/regression_linear.joblib` und `regression_linear_metadata.json`:
  unverändertes gespeichertes Modell, Parameter und Feature-Reihenfolge.
- `data/raw/offers_simulated.csv`: 30 fiktive Angebote; `offer_id`, `category`,
  `title`, `price_eur`, `discount_pct`. Acht tatsächliche manuelle Sporttag-
  Bestätigungen aus `documentation/offer_sport_tags_approved.csv`.

Keine Spaltennamen angenommen: aktive CSV-Header wurden geprüft. Die neue
Aktivitätsdarstellung nutzt zusätzlich die bestehende Engine-Funktion
`verify_tracked_bytes` zur Verifikation von Rohaktivitäten und Wochenquelle.
Die lokale Git-Basis bleibt dafür erforderlich. Erst danach werden die Zeilen
des ausgewählten Nutzers gelesen, das 26-Wochen-Raster auf Vollständigkeit und
Kalenderintervalle geprüft sowie Count-/Minutensummen gegen seine Einzelaktivitäten
abgeglichen. Fehlende Wochen werden nicht als Nullen ergänzt.

## 14. Umgesetzte Funktionen und Berechnungen

Die große Begrüßungskarte wurde in der User View durch eine kompakte Begrüßungszeile
mit Nutzerkennung und Zeitraum ersetzt. Die Freigaben stehen in einer kompakten
Zeile neben ihrem Simulationshinweis; auf kleinen Fenstern werden sie gestapelt.
KPI-Karten und Diagramme haben Vorrang vor erklärenden Detailbereichen. Das dunkle
Design mit grünen Akzenten bleibt erhalten; Quellen-/Berechnungsdetails sind
aufklappbar. Die Analytics-Lab-Experimente bleiben für AP 7.4 vorbereitet.

Persönliche Kennzahlen über **alle 26 Wochen vom 05.01.–05.07.2026**:

- Aktivitäten gesamt: Summe `activities_count`.
- Aktivitäten/Woche: diese Summe / 26, ausdrücklich einschließlich Nullwochen.
- Trainingsminuten/Woche: Summe `total_duration_min` / 26; Dezimalwerte werden
  für Summen und Mittel in Decimal verarbeitet, erst zur Anzeige numerisch formatiert.
- Aktive Wochen: Anzahl Wochen mit Count > 0; Nullwochen: 26 minus aktive Wochen.
- Häufigste beobachtete Sportart: Maximum der tatsächlichen Aktivitätscounts.
  Bei Gleichstand werden alle gleich häufigen Sportarten genannt.

Plotly-Wochenbalken zeigen 26 Werte; Umschaltung zwischen Aktivitätszahl und Minuten.
Nullwochen sind zusätzlich mit blauen Rauten bei 0 markiert und bleiben damit
sichtbar. Tooltips enthalten Wochenindex, Montag–Sonntag-Intervall und Wert.
Das Sportdiagramm zeigt ausschließlich tatsächlich ausgeübte Sportarten, mit
Anzahl sowie Anteil an den beobachteten Aktivitäten im Tooltip. Deutsche
Sportbezeichnungen sind reine Darstellungslabels; Datenwerte bleiben unverändert.
Die gesamte 26-Wochen-Tabelle ist aufklappbar.

Angebotskarten übernehmen alle Engine-Einträge in ihrer vorhandenen Reihenfolge,
maximal fünf. Titel, Kategorie, Preis, Rabatt, Rangstufe A/B, Rangposition, ID und
`match_reason` stammen unverändert aus dem bestehenden Vertrag. Keine Neusortierung,
kein eigener Score und kein neues Matching. Preis und Rabatt sind getrennte
Katalogangaben; ein rabattierter Endpreis oder reale Verfügbarkeit wird nicht behauptet.
Alle Angebote bleiben ausdrücklich fiktiv.

## 15. ML- und Engine-Integration

`dashboard/services.py:user_context` orchestriert einen frischen Anfragekontext.
`recommendation_context` delegiert an `recommendation_engine.run` mit expliziten
Freigaben, Projektwurzel und `date(2026, 7, 5)`. Das Dashboard lädt oder trainiert
kein Modell selbst und implementiert keine zweite Regression.

K-Means: gespeicherte Zuordnung und Label werden aus der Engine-Antwort übernommen;
keine neue Clusterberechnung und kein Laden/Fit des K-Means-Modells durch die UI.
Der Erklärungstext beschränkt sich auf relative Trainingshäufigkeit in der
synthetischen Gruppe; keine Fitness-, Gesundheits- oder Erfahrungsbewertung.

Regression: die Engine verwendet das unveränderte gespeicherte Modell. Eingänge
sind die Aktivitätszahl der letzten abgeschlossenen Woche und das Vierwochenmittel
inklusive dieser Woche, nur aus 08.06.–05.07.2026. Ziel bleibt 06.–12.07.2026.
Angezeigt wird der numerische Wert ausschließlich bei `prediction_status=available`;
Rundung auf zwei Stellen betrifft nur die Anzeige. Der Originalwert und die beiden
Eingänge sind in einem Detailbereich verfügbar. Keine Kappung, kein Neutraining,
kein erfundenes Unsicherheitsintervall und keine Istwerte der Zielwoche.

Fehlende Segmente/Modelle werden mit lesbarem Status erläutert; kein Ersatzcluster
und kein künstlicher Nullwert. Verfügbare Teilkontexte bleiben unabhängig:
ein fehlendes Segment macht zulässige Angebote nicht ungültig, und ein Fehler der
Aktivitätstabellen verhindert nicht automatisch die separat gültige Engine-Ausgabe.
Systemfehler führen zu einer Fehlermeldung statt einer alten Nutzerantwort.
Segment und Prognose beeinflussen die Empfehlungssortierung nicht.

## 16. Tatsächlich berechnete Beispiele

Alle folgenden Werte stammen aus erneuten tatsächlichen Aufrufen mit beiden
simulierten Freigaben; Mittelwerte und Prognosen sind hier zur Lesbarkeit gerundet.

| Wert | U001 | U002 | U003 |
| --- | ---: | ---: | ---: |
| Aktivitäten gesamt | 34 | 88 | 54 |
| Aktivitäten/Woche, Nenner 26 | 1,307692 | 3,384615 | 2,076923 |
| Trainingsminuten gesamt | 2.086,0 | 5.227,7 | 2.901,9 |
| Trainingsminuten/Woche | 80,230769 | 201,065385 | 111,611538 |
| Aktive Wochen | 16 | 24 | 19 |
| Nullwochen | 10 | 2 | 7 |
| Häufigste beobachtete Sportart | Running (17) | Walking (24) | Walking (22) |
| Segment | Geringere Trainingshäufigkeit | Höhere Trainingshäufigkeit | Geringere Trainingshäufigkeit |
| Prognose 06.–12.07.2026 | 2,690254651978 | 3,692795244550 | 2,005684418426 |

Empfehlungen in exakt ausgegebener Reihenfolge:

- U001: O001(A), O006(A), O009(A), O010(A), O002(B).
- U002: O009(A), O010(A), O011(B), O012(B), O013(B).
- U003: O017(B), O018(B), O019(B), O020(B), O021(B).

U001 mit Interessenfreigabe, ohne Garmin-Freigabe: O001…O005, ausschließlich B.
Kein persönlicher Sport-, Aktivitäts-, Segment- oder Prognosekontext wird angezeigt.
Die historischen Prognosereferenzen werden mit numerischer Toleranz verglichen,
nicht durch künstliches Anpassen letzter Gleitkommastellen.

## 17. Freigaben, Session und fehlende Daten

False/False bleibt der Initialzustand. Solange beide Freigaben fehlen, ruft die
User View keinen persönlichen Engine-Kontext auf. Mit Interessenfreigabe allein
läuft die vorhandene Engine ohne Aktivitätszugriff: zulässige positive Kategorien,
nur Stufe B. Mit Garmin-Freigabe allein erscheinen Aktivitäts-/Modellkontexte,
aber keine personalisierten Angebote oder Interessenkategorien.

Der zusätzliche Aktivitätsloader gibt bei False bereits vor Dateizugriff oder
Hashprüfung None zurück. Sämtliche Kennzahlen, Diagramme, Sportcounts, Segmente
und Prognosen werden im Renderer zusätzlich durch die Garmin-Freigabe begrenzt.
Die Angebotsdarstellung wird separat durch die Interessenfreigabe begrenzt.

Es gibt weder persönlichen Cache noch im Session State gespeicherte Ergebnisobjekte.
Jeder Render erhält einen frischen lokalen Anfragekontext. Die vorhandenen
Callbacks entfernen zusätzlich die vorgesehenen persönlichen Session-Felder bei
Freigabeänderung und setzen bei Nutzerwechsel beide Freigaben zurück. Die reine
Darstellungsauswahl Aktivitäten/Minuten ist kein persönlicher Datenwert.
Der Moduswechsel behält Nutzer und dessen Freigaben; das Lab lädt in AP 7.3
keinen individuellen Kontext und zeigt keine neuen personenbezogenen Ergebnisse.

Fehlende/veränderte Aktivitätsdateien oder unvollständige Wochen ergeben einen
Fehlerstatus; keine Ergänzung, Imputation oder Anzeige alter Kennzahlen. Ein Fehler
auf Engine-Ebene führt zu verständlicher Fehlermeldung ohne alten Nutzerresponse.
Ein fehlendes gespeichertes Segment oder Modell bleibt None mit seinem jeweiligen
Status; keine erfundenen Ersatzergebnisse.

## 18. Tests und bewusst ausgeschlossene Trainingsfälle

Neu: `tests/test_dashboard_user_view.py`, 15 Tests. Geprüft sind reale U001/U002/U003-
Kennzahlen, jede ihrer 26 Wochen gegen einen unabhängigen Rohdatenfilter,
Sportcounts/-anteile, Nullwochenmarker, Einheitenwechsel, gespeicherte Labels,
Prognosen, exakte Angebotsreihenfolgen, alle vier Freigabekombinationen,
Session-/Anfrageisolation, fehlende Dateien/Wochen, fehlende Modelle/Cluster,
Fehlerdarstellung und fehlender individueller Datenzugriff im Lab.

Der neue Runner `tests/run_without_training.py` entdeckt die **gesamte** vorhandene
Testsammlung und dokumentiert die vom Trainingsverbot erzwungenen Ausnahmen.

```bash
PYTHONDONTWRITEBYTECODE=1 OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 \
  .venv/bin/python tests/run_without_training.py
```

Tatsächliches Endergebnis: **158 Testfälle entdeckt, 137 bestanden, 21 übersprungen,
0 Fehler und 0 Fehlschläge**. Darin enthalten sind alle 42 AP-6-Tests und insgesamt
33 Dashboardtests (18 AP-7.2-Tests + 15 neue). Die 15 neuen Tests wurden zusätzlich
zuerst separat ausgeführt und bestanden vollständig.

Die 21 Ausnahmen sind ausdrücklich kein Nachweis ausgeführter Trainingsprüfungen:

- Neun Fälle von `test_modeling_kmeans_k_selection.KSelectionTests`: gemeinsames
  `setUpClass` trainiert bereits k=1…8.
- Neun Fälle von `test_modeling_kmeans_stability.StabilityTests`: gemeinsames
  `setUpClass` trainiert die 80 Stabilitätsmodelle.
- `FinalKMeansTests.test_no_scaling_and_exact_input_reproduction`: neuer K-Means-Fit.
- `test_training_without_test_access_scaling_or_scoring` und
  `test_loaded_training_predictions_equal_fresh_fit` der Regressionstrainings-Tests:
  jeweils neuer Regressions-Fit.

Wegen der ausdrücklichen Anweisung „keine Modelle neu trainieren“ wurden diese
Fälle vor Ausführung ihrer Setups markiert. Vorhandene Testdateien und
Trainingsmodule wurden nicht verändert. Zusätzlich blockiert der Runner während
des Laufs `KMeans.fit`, `LinearRegression.fit` und `StandardScaler.fit`, sodass ein
übersehener Trainingspfad fehlschlagen würde. Die tatsächlich ausgeführten Tests
umfassen weiterhin gespeicherte Modellparameter, Inferenz, Feature-/Zeitgrenzen,
Baseline, Audit, Quellenintegrität und Matching.

## 19. Tatsächlicher Start, Chromium und Screenshots

Die Anwendung wurde mit der bestehenden `.venv` lokal neu gestartet, damit neue
Module im Serverprozess sicher geladen sind. Startbefehl unverändert:
`.venv/bin/python -m streamlit run app.py`. Interner Health-Endpunkt HTTP 200.
Der Server ist weiterhin eine lokale Codex-Anwendung, kein extern erreichbarer
localhost-Link und kein öffentliches Deployment.

Chromium/Playwright prüfte die wirkliche App: U001/U002/U003, Nutzerwechsel mit
Reset beider Freigaben, beide Schalter unabhängig, reine Kategorieempfehlungen
ohne Garmin, persönliche Diagramme mit Garmin, Aktivitäts-/Minutenumschaltung,
Segment-/Prognose-/Angebotsanzeige, Freigabeentzug, Moduswechsel mit Nutzererhalt
und ausbleibenden individuellen Charts im Lab. Keine JavaScript-Seitenfehler und
keine sichtbare Streamlit-Python-Ausnahme. Mobilprüfung 390×1000 ohne horizontalen
Überlauf; Desktopprüfung 1440×1100. Asynchrones Plotly-Rendering und vorübergehend
parallel vorhandene alte/neue DOM-Elemente bei Reruns wurden im Browsertest mit
geeigneten Wartezuständen berücksichtigt; keine Daten aus vorherigen Nutzern im
fertig gerenderten Zustand.

Neue Screenshots, tatsächlich erzeugt und visuell gelesen, unter
`work/ap73-screenshots/`:

- `mova-user-u001-desktop.png`: kompakter Kopf, echte Kennzahlen, beide Diagramme.
- `mova-user-u001-insights-offers.png`: Segment und Prognose mit Unsicherheit.
- `mova-user-u001-offers.png`: tatsächliche fünf Angebote mit Reihenfolge und Begründung.
- `mova-user-u001-mobile.png`: gestapelte Mobilansicht mit Freigaben und Kennzahlen.
- `mova-user-u001-mobile-charts.png`: Kennzahlen und Trainingsverlauf auf Mobilbreite.

Die PNGs sind temporäre lokale Prüfarbeitsdateien, keine neuen fachlichen Daten.
Es erfolgt **keine neue GitHub-Veröffentlichung**, da dieser Auftrag keinen neuen
Commit erlaubt. Die früheren GitHub-Screenshots unter `documentation/screenshots/`
zeigen weiterhin den unveränderten AP-7.2-Stand. Direkte Bildanhänge sind in der
aktuellen Chatoberfläche nach vorheriger Prüfung nicht zuverlässig verfügbar;
keine nicht vorhandene Downloadmöglichkeit behauptet.

## 20. Dateien, Grenzen und Übergabe

Seit AP 7.2 neu: `dashboard/user_view.py`, `dashboard/charts.py`,
`tests/test_dashboard_user_view.py`, `tests/run_without_training.py`.
Geändert: `app.py`, `dashboard/views.py`, `dashboard/data_access.py`,
`dashboard/services.py`, `dashboard/styles.css` und diese Ausführungsdokumentation.
Keine zusätzlichen Paketanforderungen. `dashboard/state.py` und die bestehenden
AP-7.2-Tests bleiben unverändert; die getestete Reset-Logik wird weiterverwendet.

Alle persönlichen Daten sind synthetisch. Beobachtete Sportarten sind keine
Interessens-/Fitness-/Gesundheitsbewertung. Die Schätzung betrifft nur die historische
Demo-Zielwoche, deren Istwerte fehlen. Keine garantierte Prognosegenauigkeit oder
nachgewiesene Empfehlungsqualität. CSV-/Modell-/Git-Bestand bleibt Voraussetzung
der lokalen Anwendung; kein neuer API-/Datenbank-/Backenddienst.

**AP 7.3 ist abgeschlossen; AP 7.4 kann beginnen.** Es bestehen keine blockierenden
Probleme für die User View. Die wissenschaftlichen Lab-Experimente und eine spätere
GitHub-Sicherung der App bleiben Aufgaben der folgenden separat beauftragten Schritte.

Abschließende Integritätsprüfung AP 7.3: Alle **171** bereits versionierten Dateien
(168 AP-1–AP-6-Dateien plus drei separat veröffentlichte AP-7.2-Screenshots) gegen
den aktuellen HEAD per Git-Blobhash geprüft: **0 Abweichungen**. Der Git-Index ist
leer; HEAD bleibt `33e889c11837a8e878b039835f0e9faf4de21850`. Die fünf neuen
PNG-Prüfaufnahmen wurden zusätzlich mit Pillow auf Lesbarkeit geprüft. Rohdaten,
Modelle, Tags, Angebotskatalog, Engine und vorhandene Tests bleiben bytegleich.

# Fortschreibung AP 7.4 – vollständiges interaktives Analytics Lab

Stand: 01.11.2026, Worktree `/workspace/MOVA-AP7`, Branch `ap7-dashboard`.
Ursprüngliche fachliche Basis bleibt `23ac008651de490d59e9ec5ceae590ba97daf0e5`;
der aktuelle HEAD ist weiterhin der separate Screenshot-Commit
`33e889c11837a8e878b039835f0e9faf4de21850`. Die vorherigen Abschnitte beschreiben
die historischen AP-7.2-/AP-7.3-Stände. Die dort noch vorgesehenen Lab-Experimente
sind jetzt wie folgt implementiert. Kein neuer Commit, Push oder Pull Request.

## 21. Architektur, Datenzugriff und Zugriffsgrenzen

Die bestehende Streamlit-Anwendung, ihr Designsystem und die linke Navigation
mit sieben Bereichen werden weiterverwendet. Kein zusätzlicher Server und keine
zweite Webanwendung. Der große Lab-Begrüßungsbereich ist durch dieselbe kompakte
Überschriftenstruktur wie in der User View ersetzt. Interaktive Auswahl und
tatsächliche Diagramme stehen direkt darunter.

Neue Module:

- `dashboard/analytics_data.py`: wissenschaftliche Tabellenansichten, Validierung,
  deskriptive Aggregate und explizit freigabegebundene Detailmethoden.
- `dashboard/analytics_view.py`: sieben Seiten mit wiederverwendbaren Diagramm-,
  Kennzahl-, Erkenntnis-, Quellen- und Freigabekomponenten.
- `tests/test_dashboard_analytics.py`: 18 neue Backend- und AppTest-Prüfungen.

Geändert: `app.py` (aktueller Status), `dashboard/views.py` (gemeinsame View-Einstiege),
`tests/test_dashboard.py` (Navigation gezielt über Sidebar statt über beliebigen
Radio-Index), `tests/test_dashboard_user_view.py` (Lab darf nun aggregierte Charts
zeigen, weiterhin keinen persönlichen User-View-Kontext laden), diese Dokumentation.
Keine neuen Pakete, kein neuer Scaler oder Predictor und keine zweite Rankinglogik.
Die fachlichen Python-Module und vorhandenen AP-1–AP-6-Tests bleiben unverändert.

`ResearchData` ist ein Objekt für genau einen Seitenaufruf. Eingangsbytes werden
gegen den vollständigen bestätigten Git-Basisbaum geprüft; fehlende oder veränderte
Dateien liefern `DataAccessError` statt Ersatzdaten. Tabellen besitzen explizite
Spaltenprüfungen an den zentralen Berechnungsstellen. Zwischenbytes werden nur
innerhalb dieses lokalen Objekts wiederverwendet, nicht global, nicht über
`st.cache` und nicht im Session State. Keine personenbezogenen Ergebnis-Caches.
Es werden keine CSV-/JSON-/Modellergebnisse neu exportiert.

Aggregierte Analysen sind ohne Freigaben sichtbar. Die Rohdatensatzansicht in
Data Understanding liefert der UI keine Nutzer- oder Aktivitätskennungen; dargestellt
werden ausschließlich Häufigkeiten, Verteilungen und Kennzahlen. Pipeline-Schritte
zeigen Schema und Dimension, keine ungeprüften individuellen Tabellenproben.

Individuelle Methoden `scaling`, `cluster_for_user`, `regression_case` und
`recommendation_case` prüfen die Garmin-Freigabe **vor** dem Zugriff auf ihre
Detailquellen. Der individuelle Angebotsvergleich verlangt zusätzlich die
Interessenfreigabe, ebenfalls vor Quellenzugriff und Replay. Die UI wiederholt diese
Sperre mit verständlicher Meldung. Persönliche Analyse verwendet immer den global
ausgewählten Nutzer, keine versteckte zweite Nutzerauswahl. Nutzerwechsel setzt
wie bisher beide Freigaben zurück; Moduswechsel erteilt keine Freigabe.

## 22. Tatsächlich verwendete Daten und Schemata

Die in AP 7.3 beschriebenen Roh- und Wochenquellen bleiben unverändert: 100 Nutzer,
6.465 Aktivitäten, acht Sportarten, 2.600 Nutzerwochen über 26 Wochen.
Zusätzlich werden folgende gespeicherte Artefakte geprüft und verwendet:

| Quelle | Tatsächlicher Umfang / wichtige Felder | Verwendung |
| --- | --- | --- |
| `data/processed/activities_selected.csv` | 6.465 × 5, ohne Distanzfeld | Tatsächliche Auswahlstufe, keine entfernten Aktivitätszeilen |
| `data/processed/kmeans_user_features.csv` | 100 × 12 einschließlich ID und zwei Interpretationsmerkmalen | Beobachtete Merkmale und individuelle Skalierung |
| `data/processed/kmeans_user_features_scaled.csv` | 100 × 10 einschließlich ID | Gespeicherte neun gewichtete Modellwerte |
| `outputs/models/kmeans_scaling_params.json` | Feature-Reihenfolge, mean, scale, weight, ddof | Tatsächliche Standardisierung ohne Fit |
| `outputs/tables/kmeans_k_selection.csv` | Acht k-Zeilen; Silhouette ab k=2, Inertia | Kandidatenvergleich k=2,3,6,8 |
| `outputs/tables/kmeans_candidate_comparison.csv` | Vier Kandidaten × 18 Spalten | 20-Seed-Mittel und ARI, getrennt vom Seed-42-Einzellauf |
| `outputs/tables/kmeans_candidate_profiles.csv` | Fünf Zeilen, ausschließlich k=2/3 | Vorläufige k=3-Profile; keine neuen Labels |
| `outputs/tables/kmeans_final_cluster_profiles.csv` | Zwei finale Profile × 15 Spalten | Größen, unskalierte Modell- und Interpretationsmerkmale |
| `outputs/models/kmeans_final_metadata.json` | Finale Parameter, k=2, Zentren, Silhouette und Zuordnungstexte | Begründung und Grenzen des gespeicherten Modells |
| `data/processed/user_clusters.csv` | 100 gespeicherte Zuordnungen | Individueller Kontext ausschließlich mit Garmin-Freigabe |
| `data/processed/regression_weekly_features.csv` | 2.200 × 7 | X aus aktueller Woche/Vierwochenmittel, Ziel der Folgewoche |
| `data/processed/regression_train.csv`, `regression_test.csv` | 1.800 / 400 Zeilen | Tatsächlicher chronologischer Split |
| `documentation/regression_split_manifest.json` | Eingangs-/Zielwochen und Datumsgrenzen | Zeitleiste und Splitnachweis |
| `outputs/models/regression_linear_metadata.json` | Exakter Intercept und zwei Koeffizienten | Erklärung der gespeicherten Regressionsgleichung |
| `outputs/tables/regression_test_predictions.csv` | 400 × 10; X, Ist, Prognose, Fehler | Auswahl jedes gespeicherten Testfalls |
| `outputs/tables/regression_baseline_comparison.csv` | 400 × 11; beide Prognosen und absolute Fehler | Aggregierte/individuelle Baselinevergleiche, MAE, RMSE |
| `outputs/tables/recommendation_before_after_users.csv` | 100 × 14, Top-5 als JSON-Listenfelder | Nachweis des kontrollierten individuellen Engine-Replays |
| `outputs/tables/recommendation_before_after_summary.json` | Gesamtzahlen, Bezugsgrößen, Beispiele und Hashes | Nur whitelisted Gesamtfelder an die aggregierte UI; keine individuellen Beispiele ohne Freigabe |
| `outputs/simulation_comparison/comparison_metrics.csv` | 18 × 4; erste Metrikspalte tatsächlich `Unnamed: 0` | V1, technische Kontrolle 1,0 und V2 1,3 |
| `documentation/crisp_dm_log.md`, bestehende Ausführungsberichte | Tatsächlicher Projekt- und Iterationsverlauf | Nachprüfbare Phasen und Artefaktverweise |

## 23. Implementierte Bereiche und Interaktionen

### A – Data Understanding

Sportauswahl filtert tatsächliche Aktivitäten. Anzahl und Anteil beziehen sich auf
die Gesamtzahl 6.465; die Zeitreihe enthält alle 26 Wochen, einschließlich leerer
Sport-Wochen. Eine Merkmalsauswahl für Dauer, Distanz, Sportart oder Datum zeigt
Bedeutung, tatsächlich eingelesenen pandas-Datentyp, fehlende Werte und geeignete
Verteilung/Kennzahlen. Strukturelle Distanzleerwerte bleiben fehlend, nicht 0 km.
Es werden keine individuellen Rohdatensätze an die aggregierte Darstellung gegeben.

### B – Data Preparation

Vier direkt auswählbare Experimente:

1. **Pipeline:** Schieberegler führt durch Rohdaten, Auswahl/Prüfung, Wochenraster,
   K-Means-Features, K-Means-Skalierung, Regressionsfenster und Modellinputs/Split.
   Je Stufe: reale Eingangs-/Ausgangspfade, Zeilen/Spalten, Schema und fachliche
   Begründung. K-Means- und Regressionspfad sind ausdrücklich getrennt.
2. **Nullwochen:** Umschalter verändert tatsächlichen Nenner, Nullwochenzahl,
   Häufigkeitsmittel, Histogramm und Schlussfolgerung. Die Aktivitätssumme bleibt
   6.465; Formel und Vergleich nennen beide Bezugsgrößen. Der Auslassungseffekt
   misst keine verbesserte Modellgüte.
3. **Skalierung:** Nutzer aus globaler Auswahl, Modellfeature und vier Rechenschritte
   wählen. Zeigt bei Freigabe Originalaktivitäten, Nutzerfeatures, Zwischenwerte
   und gespeicherte gewichtete Features. Ohne Freigabe bleiben lediglich die
   aggregierten Skalerparameter sichtbar. Der finale Transformationswert kommt
   aus der bestehenden Funktion `data_preparation_scaling.transform_saved` und
   wird gegen den gespeicherten Wert geprüft; kein Scaler-Fit. Angezeigt werden
   x, μ, scale_, z=(x−μ)/scale_, Gewicht und finaler Modellwert.
4. **Zeitlicher Split:** Eingabewoche t=4…25 wählen; historische Wochen t−3…t,
   Ziel t+1 und Trainings-/Testzielwochen werden gleichzeitig markiert. Individuelle
   X-/y-Zeile nur mit Garmin-Freigabe. Frühe unvollständige Historie und fehlendes
   Zukunftsziel am Rand werden erläutert. Keine zufällige Aufteilung.

### C – K-Means

Auswahl k=2,3,6,8 und Vergleichsmaß Silhouette/Inertia. Je Auswahl gespeicherte
Seed-42-Kennzahlen und 20-Seed-Stabilität; keine neue Anpassung. Unterschied zwischen
Einzellauf und Seedmittel sichtbar. Bei k=6/8 expliziter Hinweis auf fehlende
Profile/Zuordnungen. Bei k=3 sind nur vorhandene vorläufige Aggregate aufklappbar.

Der darunter klar abgegrenzte finale k=2-Bereich zeigt Größen 57/43 und einen
interaktiven Vergleich unskalierter Profilmerkmale. Modelleingänge sind von Minuten
und Vielfalt als reinen Interpretationsmerkmalen unterschieden. Die neun Eingänge
und Gewichtung sind aufklappbar. Individuelle gespeicherte Zuordnung nur mit
Garmin-Freigabe; keine Nutzerlabels für andere k erzeugt.

### D – Lineare Regression

Exakte Gleichung aus Modellmetadaten, Zielvariable und beide X erklärt. Zielwoche
23…26 wählen; ein aggregierter Überblick zeigt Mittelwerte über jeweils 100 Fälle.
Das ist ausdrücklich kein Ersatz für die mittleren absoluten Einzelfehler.

Mit Garmin-Freigabe lässt sich über die globale Nutzerwahl und Zielwoche jeder der
400 gespeicherten Fälle untersuchen. Vier Rechenschritte zeigen Historie, Inputs,
Koeffizientenbeiträge und Fehler. Summe der Beiträge wird numerisch gegen die
bestehende gespeicherte Prognose geprüft, nicht als neue produktive Regressionslogik
verwendet. Ist, Regression, Persistence und beide absoluten Fehler sind sichtbar.
Die vier Testwochen des ausgewählten Nutzers werden mit der gewählten Woche
markiert als Linienvergleich gezeigt. Keine neuen Prognosen nötig, kein Modellladen
oder Fit für das Lab; die bestehende User-View-Inferenz bleibt unverändert.

### E – Evaluation

Zeitraum und Diagnosegruppe (alle Fälle, beobachtetes Ziel=0, Ziel>0) wählen;
MAE/RMSE umschalten. Kennzahlen und Wochenmittel/-fehler stammen aus den gespeicherten
400 Vergleichsfällen. Relative Verbesserung verwendet den Baseline-MAE als Nenner;
Nenner 0 wäre nicht definiert. Jede Auswahl zeigt ihr N.

Die Nullzielgruppen sind ausschließlich nachträgliche Diagnosen. Die zukünftige
Zielaktivität ist am Prognosezeitpunkt unbekannt und darf keine Modellumschaltung
steuern. Ein entsprechender Leakage-Hinweis ist dauerhaft sichtbar. Methodische
Grenzen umfassen synthetische Daten, bekannte wiederholte Nutzer, überlappende
Fenster, Prognosefehler und fehlende kausale/ökonomische Nachweise.

### F – Empfehlungssystem

Gesamtvergleich ohne Freigaben zeigt ausschließlich gruppierte Nutzer-/Slotgrößen.
Individueller Vergleich erfordert beide Freigaben. Er verwendet dieselben Engine-
Funktionen wie AP 6.3c: Kategorien und geprüftes Sportprofil einmal bestimmen;
`engine.recommendations` zweimal mit identischem Kontext, allein die bestätigte
Tagmenge wechselt von leer auf acht. Kein zweites Matching, keine Modellinferenz
und keine Änderung der Freigabedatei. Beide Listen werden gegen die gespeicherten
JSON-ID-Arrays des Nutzers geprüft.

Eintritte, Austritte, behaltene Angebote und Positionsänderungen sind markiert.
Bei gleicher Position wird eine mögliche Änderung B→A zusätzlich ausgewiesen:
Listenidentität und Rangstufenidentität sind verschiedene Dinge. Die tatsächliche
Engine-Begründung ist aufklappbar. Leere Listen bleiben leer und werden erklärt.
Kein Beleg für höhere Relevanz oder Empfehlungsqualität behauptet.

### G – CRISP-DM

Phase auswählen; sechs Phasen visuell verbunden. Je Auswahl Ziel, tatsächlich
durchgeführte Schritte und existierende Artefakte. Deployment beschreibt die lokale
Demo und weiterhin ausstehende AP-7.5-Gesamtabnahme, keinen Produktivbetrieb.

MOVA-ITER-001 zeigt Data Understanding → Construct Data → erneute Prüfung.
Metrikauswahl vergleicht V1, technische Kontrolle 1,0 und V2 1,3. Gepaarter
Kontrolle→V2-Vergleich isoliert den Exponenteneffekt; historische Unterschiede
V1→V2 können durch veränderte Zufallsströme mitbestimmt sein. Git-Probleme/Bugfixes
werden ausdrücklich nicht als fachliche Iterationen dargestellt. Es wurde keine
Simulation oder neue fachliche Iteration in AP 7.4 gestartet.

## 24. Tatsächliche Kontrollwerte

- Nullwochen: 558/2.600; Mittel vollständig 2,4865384615384616,
  Mittel nur aktive Wochen 3,166013712047013; relative Überschätzung 27,3261508325 %.
- U001, `share_running`: x=0,5; μ=0,1527778837284182;
  scale_=0,16294258775607925; z=2,1309475997236778;
  Gewicht=0,35355339059327373; final 0,7534037490589046.
- Regressionsbeispiele: 2.200; Training 1.800, Test 400.
  Trainings-X 4…21/Ziele 5…22; Test-X 22…25/Ziele 23…26.
- Silhouette Seed 42 für k=2/3/6/8:
  0,30333715184382104 / 0,18464238109971873 /
  0,19430902295353497 / 0,20612962999737008.
- Final k=2: 57/43 Nutzer; mittlere Wochenhäufigkeit 1,5350877193 / 3,7477638640.
- Regression: Intercept 0,8397931020190079;
  aktuelle Woche 0,22819007785063997; Vierwochenmittel 0,42396047869339204.
- U001, Eingabewoche 22 → Zielwoche 23: X=(1; 2,25), Ist 2,
  Prognose ≈2,02189425693, Baseline 1; absolute Fehler ≈0,02189425693 / 1.
- Gesamt-MAE Regression 1,4898770575225395 gegen Baseline 1,71;
  relative Verbesserung 12,8726866946 %. RMSE 1,9085376545370092 / 2,3108440016582685.
- 92 Nullzielwochen: MAE 1,8782923959526365 / 1,3804347826086956;
  negative relative Verbesserung −36,0652759273 %. 308 positive Zielwochen:
  MAE 1,3738568914979652 / 1,8084415584415585.
- AP 6: 100 Nutzer, 36 unveränderte Listen, 64 andere Zusammensetzungen,
  0 reine Umordnungen; 475 Slots je Variante; nachher 344 A-Slots =72,4210526316 %;
  81 Nutzer mit mindestens einem A-Angebot. Keine dieser Bezugsgrößen gleichsetzen.
- Iteration Kontrolle→V2: Top-2-Mittel 57,6105951313→64,1173339900 %
  (+6,5067388587 Prozentpunkte), acht Sportarten 58→40; Aktivitäten bleiben 6.465.

## 25. Tests und Reproduktionsbefehle

```bash
PYTHONDONTWRITEBYTECODE=1 OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 \
  .venv/bin/python tests/run_without_training.py
```

Die vollständige Sammlung umfasst nach AP 7.4 **176 Fälle**. **155 bestanden,
21 übersprungen, 0 Fehler, 0 Fehlschläge**. Darin alle 42 AP-6-Tests und alle
51 Dashboardtests (18 AP 7.2, 15 AP 7.3, 18 neue AP 7.4).

Die gleichen 21 historischen Trainingsfälle wie in Abschnitt 18 bleiben ausdrücklich
ausgeschlossen: je neun Fälle mit trainierendem Klassen-Setup für k-Auswahl und
Stabilität sowie ein finaler K-Means-Neufit und zwei Regressions-Neufits. Keine
stillen Ausschlüsse. Der bestehende Runner blockiert während des Laufs zusätzlich
`KMeans.fit`, `LinearRegression.fit` und `StandardScaler.fit`.

Die neuen Tests prüfen Population/Sportaggregation, beide Nullwochenvarianten,
reale Pipeline-Dimensionen, Skalierung für alle neun Features bei U001/U002/U003,
Splitgrenzen, alle vier k-Werte und finale Größen, genaue Modellparameter,
**alle 400 Regressionsfälle** einschließlich vergangener Historie und gespeicherter
Prognose, MAE/RMSE und Nullzielgruppen, **alle 100 Nutzer-Replays** gegen gespeicherte
Angebotslisten, Freigabesperren vor individuellen Quellenzugriffen, fehlende oder
geänderte Dateien, Anfrageisolation, alle sieben Streamlit-Seiten, Experimentschalter,
Nutzerwechsel und ausbleibende Trainingsaufrufe.

Die Quellen sind unverändert; alle Berechnungen erfolgen im Speicher. Testkopien und
Browserprotokolle liegen ausschließlich unter den vorhandenen Ignore-Pfaden.

## 26. Tatsächliche Browserprüfung und Screenshots

Die bestehende App wurde mit der vorhandenen `.venv` neu gestartet; keine neue
Installation oder Infrastruktur. Der interne Health-Endpunkt antwortet mit HTTP 200.
Chromium/Playwright hat alle sieben Seiten tatsächlich geöffnet und insbesondere
Sport-/Merkmalsfilter, Pipeline-/Nullwochen-/Skalierungs-/Splitnavigation,
Feature-Auswahl, k=8 und k=2, Zielwoche 26 des U001-Testfalls, Nullzielgruppen-
Evaluation, freigabegebundenen Vorher-Nachher-Vergleich und CRISP-Phasen-/Metrikwechsel
bedient. Nutzerwechsel zu U002 setzte beide Freigaben zurück; alte individuelle
Empfehlungen verschwanden. Wechsel User View ↔ Analytics Lab behielt den Nutzer,
erteilte keine Freigabe und zeigte im gesperrten Zustand keine persönlichen Resultate.

Die Prüfung wartete auf echte Rerun-/Plotly-Zustände und nutzte die öffentlich
beschrifteten Streamlit-Bedienelemente. Eine versteckte Canvas-Tabellenzelle wurde
nicht fälschlich als sichtbarer Browsertext vorausgesetzt. Die responsive
Seitenleiste wurde auf Mobilbreite über ihre echten Expand-/Collapse-Schaltflächen
bedient; keine App-Manipulation oder Screenshot-Montage.

Desktop 1440×1100 und Mobil 390×1000 geprüft. Alle sieben Mobilseiten wurden
zusätzlich in frischen Browserseiten mit bereits initialer Mobilbreite geöffnet.
Dabei blieben Dokument- und Hauptbereich ohne horizontalen Überlauf
(`main.scrollWidth == main.clientWidth == 390`). Tabellen können innerhalb ihres
eigenen Containers horizontal scrollen. Kein kritischer JavaScript-Seitenfehler,
keine sichtbare Python-Ausnahme. Eine bei der visuellen Kontrolle erkannte
Überlagerung der sechs CRISP-DM-Phasenbeschriftungen auf Mobilbreite wurde durch
eine vertikale Phasendarstellung korrigiert und erneut auf Desktop/Mobil geprüft.
Nach der letzten Änderung bestehen weiterhin 155 Tests bei 21 dokumentierten
Trainingsausschlüssen. `pip check` ohne defekte Anforderungen.

15 tatsächlich erzeugte, lokal lesbare PNGs unter `work/ap74-screenshots/`:

- `mova-lab-nullwochen-desktop.png`
- `mova-lab-skalierung-desktop.png`
- `mova-lab-split-desktop.png`
- `mova-lab-kmeans-desktop.png`
- `mova-lab-regression-desktop.png`
- `mova-lab-regression-rechenweg.png`
- `mova-lab-evaluation-desktop.png`
- `mova-lab-empfehlungen-desktop.png`
- `mova-lab-crisp-desktop.png`
- `mova-lab-mobile.png`
- `mova-lab-mobile-data-preparation.png`
- `mova-lab-mobile-k-means.png`
- `mova-lab-mobile-regression.png`
- `mova-lab-mobile-evaluation.png`
- `mova-lab-mobile-crisp.png`

Die Hauptaufnahmen zu Nullwochen, Skalierung, K-Means und Regression sowie
Evaluation und die korrigierten Mobilansichten wurden visuell gelesen. Screenshots
und Prüfskripte bleiben unter dem ignorierten `work/`. Keine neuen Bilder nach
GitHub kopiert oder veröffentlicht, kein neuer Commit; die dort bereits vorhandenen
AP-7.2-Bilder bleiben unverändert. Die bekannte fehlende direkte Dateianhang-/
Downloadfunktion dieser Chatoberfläche ist kein Appfehler und wird nicht als
funktionierende Bildbereitstellung dargestellt.

## 27. Methodische Grenzen und Präsentationsroute

Es fehlen weiterhin k=6/8-Profile und alternative Nutzerzuordnungen; diese werden
nicht erzeugt. Individuelle Fälle sind gesperrt, solange die entsprechenden
simulierten Freigaben fehlen. Regression ist global für bekannte synthetische
Nutzer evaluiert, nicht prospektiv an neuen realen Garmin-Nutzern. Historische
Testziele enden am 05.07.2026; für die User-View-Demowoche danach gibt es keine
Istwerte und keine behaupteten Prognoseintervalle. Die Nullzielgruppe ist eine
nachträgliche Diagnose, niemals ein Eingang oder eine Umschaltregel. K-Means ist
moderat getrennt, die Featuregewichtung eine Startannahme. Simulation, Modellgüte
und Regelwirkung sind verschiedene Nachweise; keine kausale oder wirtschaftliche
Wirkung abgeleitet.

Für eine 15-Minuten-Demo empfiehlt sich diese Route (Planungswerte):

| Bereich | Zeit | Fokus |
| --- | --- | --- |
| Data Understanding | 1 Minute | Sportfilter und strukturelle Distanzleerwerte |
| Data Preparation | 4 Minuten | Nullwochen-Nenner, U001-Skalierung, zeitlicher Split |
| K-Means | 2 Minuten | Gespeicherte k-Scores, finale Größen/Profile, Grenzen |
| Regression | 3 Minuten | U001-Testfall, vier Eingangswochen, Beiträge und Baseline |
| Evaluation | 2 Minuten | Gesamtvorteil gegen Schwäche in Nullzielwochen, Leakage |
| Empfehlungen | 1,5 Minuten | Regelwirkung und zwei tatsächlich erzeugte Listen |
| CRISP-DM | 1,5 Minuten | Kontrollvergleich 1,0→1,3 und fachlicher Rücksprung |

Vor dem individuellen Teil für den aktuellen Nutzer die jeweils benötigten
Simulationsschalter aktivieren. Bei Nutzerwechsel bewusst den Reset demonstrieren.
Die Pipeline- und Quellenansichten dienen als Reserve für Nachfragen. Keine
Animation oder neue Modellanpassung muss während der Präsentation gestartet werden.

**AP 7.4 ist abgeschlossen. AP 7.5 kann beginnen.** Offen bleiben die geplante
Gesamtabnahme/Präsentationsoptimierung und eine separat beauftragte GitHub-Sicherung
der bisher uncommitteten App-Dateien. Kein fachlicher Datenmangel blockiert die
implementierten Experimente. Die lokale vollständige Git-Historie bleibt technische
Voraussetzung der Verifikation; es wurde kein eigenständiges Deployment-Paket gebaut.

Abschließender Integritätsnachweis AP 7.4: **171/171** bereits versionierte Dateien
bytegleich zum aktuellen HEAD (168 AP-1–AP-6-Dateien und drei frühere Screenshots).
Rohdaten, Modelle, Engine, bestätigte Tags und Angebotskatalog unverändert. Alle
15 neuen PNGs per Pillow erfolgreich geöffnet/verifiziert. Git-Index leer, HEAD
unverändert `33e889c11837a8e878b039835f0e9faf4de21850`; vorheriger Worktree sauber.

# AP 7.5a – Gesamtabnahme und Vorbereitung der lokalen Demo

Stand: 01.11.2026. Bestehender Worktree und Branch unverändert. Dieser Abschnitt
ist der aktuelle Abnahmenachweis; AP-7.2–AP-7.4-Abschnitte bleiben historische
Nachweise. Keine neue fachliche Funktion und keine neue Analyse implementiert.

## 28. Bestandsaufnahme und Einstufung

| Kategorie | Befund | Behandlung |
| --- | --- | --- |
| Kritische fachliche/technische Fehler | In der geprüften Gesamtabnahme keine reproduziert: Daten, Modelle, Rankings und Freigaben konsistent | Bestehende Logik unverändert; vollständige Tests und zusätzliche Abnahmeläufe |
| Portabilitätsrisiko | Ein bloß kopierter Git-Worktree verweist möglicherweise auf das ursprüngliche gemeinsame Git-Verzeichnis | Eigenständigen vollständigen Clone geprüft; ZIP/Worktree-Kopie ohne Git-Basis ausdrücklich nicht als Laptop-Paket ausgeben |
| Portabilitätsrisiko | Git kann bei Windows-Konfiguration Textdateien nach CRLF umwandeln; das verletzt die absichtlich bytegenauen Quellhashes | Neue `.gitattributes` erzwingt LF für Text und erhält PNG/joblib binär; tatsächliche Git-Filter unter `core.autocrlf=true` geprüft |
| Wesentliche Darstellung | Große Gesamtübersichten schoben freigegebene Regressionstestfälle und Angebotslisten nach unten | Bestehende Gesamtansichten aufklappbar, ohne Freigabe weiterhin standardmäßig geöffnet; Einzelfälle mit Freigabe priorisiert |
| Wesentliche Darstellung | Einzelne Angebotsblöcke mit jeweils eigener Begründungszeile waren für den Vergleich sehr lang | Dieselben fünf Einträge je Variante kompakt gegenübergestellt; Begründungen je Liste gemeinsam aufklappbar |
| Darstellung | Wiederholter Simulationshinweis, separate Kontrollzeilen und große Zwischenräume beanspruchten Laptop-Höhe | Kompaktere Freigabezeile/Überschrift; k-/Metriksteuerung nebeneinander; redundante sichtbare Gruppenlabels reduziert, zugängliche Beschriftung bleibt |
| Optional | Weitere Animationen, Bilder, neue Analyse-/Präsentationsoberflächen oder pixelgenaue Kosmetik | Bewusst nicht umgesetzt; Stabilität und wissenschaftliche Kernaussagen haben Vorrang |

Die vier Kernelemente sind unverändert über die vorhandene Navigation erreichbar:
Data Preparation → Nullwochen, K-Means, Regression, Empfehlungssystem. Es gibt
keinen neuen Präsentationsmodus und keine neue Modellvariante.

## 29. Gezielte Optimierungen und unveränderte Fachlogik

- `app.py`: kompakter Freigabebereich ohne wiederholten Untertext; aktueller
  Abnahmestatus und verständlicher Git-Hinweis statt historischer AP-7.3-Aufforderung.
  Der synthetische Charakter und beide unabhängigen Simulationsschalter bleiben sichtbar.
- `dashboard/styles.css`: kleinere eigene Überschriften/Abstände und klar umrahmte
  kompakte Vergleichslisten. Bestehende MOVA-Farben, Systemschrift und native Widgets;
  keine externe Designbibliothek und keine Selektoren auf interne Streamlit-CSS-Klassen.
- `dashboard/analytics_view.py`: bestehende Gesamt-/Einzelansichten angeordnet,
  unveränderte Regressionsergebnisse vor Rechentabelle hervorgehoben; Listenposition,
  Angebot, ID, Rangstufe und vorhandene Änderungsmarkierung kompakt dargestellt.
  Alle ursprünglichen Gründe bleiben erreichbar. Keine neue Sortierung oder Berechnung.
- `.gitattributes`: reine Checkout-/Zeilenendenregel, keine vorhandene Quelldatei
  umgeschrieben. Auch unter Windows-Git-Konfiguration bleiben die geprüften Bytes erhalten.

Die zentralen Textfarbkontraste wurden rechnerisch für die Design-Tokens geprüft:
primärer Text auf Hintergrund/Karten 17,59:1 / 15,47:1; sekundärer Text
10,66:1 / 9,37:1; Grün 12,07:1 / 10,61:1. Das ist eine Prüfung dieser Tokenpaare,
keine vollständige automatisierte Barrierefreiheitszertifizierung. Die tatsächlichen
Diagramme, Beschriftungen und Mobilansichten wurden zusätzlich im Browser gesichtet.
Auf kleinen Laptopfenstern bleibt normales vertikales Scrollen bei langen Ansichten
notwendig; Quellen und Details können auf- und zugeklappt werden.

## 30. Wissenschaftliche Plausibilitätsprüfung

Die Werte wurden erneut aus den bestehenden Artefakten kontrolliert:

| Prüfgröße | Bestätigt |
| --- | --- |
| Aktivitäten / Nutzerwochen / Nullwochen | 6.465 / 2.600 / 558 |
| Mittel mit / ohne Nullwochen | 2,4865384615384616 / 3,166013712047013 |
| Auslassungseffekt | +27,3261508325 %; keine Modellgütebehauptung |
| Finale Cluster | k=2; Größen 57/43; Silhouette 0,30333715184382104 |
| Kandidaten k=2/3/6/8 | Gespeicherte Score-/Inertia-Werte unverändert, keine neuen Profile |
| Regressions-Test | 400 echte gespeicherte Fälle; MAE 1,4898770575225395 gegen 1,71; Verbesserung 12,8726866946 % |
| Gleichung | Intercept 0,8397931020190079; Koeffizienten 0,22819007785063997 und 0,42396047869339204 |
| Nullzielgruppen | 92 Fälle; MAE 1,8782923959526365 gegen 1,3804347826086956; nur Post-hoc-Diagnose, keine Modellauswahl mit Zukunftswissen |
| AP-6-Regelwirkung | 100 Nutzer, 64 andere Top-5-Zusammensetzungen, 344/475 Slots A, acht tatsächlich bestätigte Tags |

Keine höhere Empfehlungsqualität, Fitness, Gesundheit, Kausalität oder reale
Umsatzwirkung behauptet. Keine zukünftigen Demo-Istwerte und keine erfundenen
Prognoseintervalle. Die Skalerparameter und historischen Regressionsfenster bleiben
unverändert. Segment und Prognose beeinflussen weiterhin nicht das Angebotsranking.

## 31. Automatisierte Gesamtabnahme

Der vorhandene trainingsfreie Runner wurde mit seinen Fit-Sperren ausgeführt:

```bash
PYTHONDONTWRITEBYTECODE=1 OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 \
  .venv/bin/python tests/run_without_training.py
```

**178 Fälle entdeckt: 157 bestanden, 21 ausdrücklich übersprungen, 0 Fehler,
0 Fehlschläge.** Alle 42 AP-6-Tests sind enthalten. Zu den bisherigen 51
Dashboardtests kommen genau zwei gezielte Abnahmeregressionen in
`tests/test_dashboard_acceptance.py` hinzu:

1. Tatsächliche Git-Checkout-Filter mit `core.autocrlf=true` erhalten die bytegenauen
   CSV-/JSON-/joblib-Quellen durch die neue Attributregel.
2. Kompakte Vergleichslisten behalten beide tatsächlichen Top-5-Reihenfolgen und
   verschwinden nach Nutzerwechsel mit zurückgesetzten Freigaben.

Keine Tests für reine kosmetische Implementierungsdetails hinzugefügt. Die gleichen
21 Ausschlüsse bleiben wie in Abschnitt 18/25 begründet: je neun Fälle mit
trainierendem Klassen-Setup für k-Auswahl/Stabilität, ein finaler K-Means-Neufit,
zwei Regressions-Neufits. Sie werden nicht als bestanden gezählt und wurden nicht
aktiviert. Der Runner blockiert weiterhin K-Means-, Regressions- und Scaler-Fit.

Zusätzliche Abnahmeläufe, keine neuen produktiven Verfahren:

- **100 Nutzer über AppTest:** jede Kennung tatsächlich gewählt, Reihe mit exakt
  26 Wochen gegen die vorhandenen Wochenwerte geprüft, Aktivitätssumme/Sportcounts
  gegen Rohdaten, gespeichertes Segment und maximal fünf Angebote geprüft.
  **400 Freigabekombinationen** kontrollieren getrennte Interessen-/Garmin-Wege,
  fehlende persönliche Charts/Angebote und Rücksetzen beim Nutzerwechsel.
- **100 Modellkontexte:** Segment und numerische Prognose für alle Nutzer verfügbar;
  Ziel 06.–12.07.2026 konsistent; kein Fit. U001/U002/U003 stimmen mit den
  bestätigten Beispielen überein.
- **Alle vorhandenen Lab-Steuerelemente:** alle Sport-/Feldoptionen, sieben
  Pipeline-Schritte, beide Nullwochenvarianten, neun Skalierungsfeatures/vier
  Schritte, 22 Split-Eingabewochen, vier k-Werte/beide Vergleichsmetriken, elf
  Profilmerkmale, vier Zielwochen/vier Rechenschritte, fünf Evaluationszeiträume/
  drei Gruppen/zwei Fehlermaße, U001/U002/U003-Vergleiche sowie sechs CRISP-Phasen/
  fünf Iterationsmetriken. Keine leeren oder funktionslosen Bedienelemente gefunden.
- `pip check`: keine defekten Anforderungen. Temporäre Protokolle und JSON-
  Abnahmezusammenfassungen unter `work/ap75a/`; keine neuen synthetischen Datensätze.

## 32. Tatsächliche lokale Ausführung und Portabilität

Maßgebliche kompakte Anleitung: `documentation/dashboard_demo_guide.md`.
Python 3.12.14, Streamlit 1.66.1, Plotly 6.4.0 und die unveränderten Modellpakete.
Das bestehende isolierte `.venv` wurde verwendet; die frühere vollständige
Installation und der aktuelle Konsistenzcheck sind nachgewiesen. Keine neue
Paketauflösung oder Aktualisierung in AP 7.5a.

Vom Repository-Stamm nach Installation des Locks starten:

```bash
python -m venv .venv
.venv/bin/python -m pip install -r requirements-dashboard-lock.txt
.venv/bin/python -m pip check
.venv/bin/python -m streamlit run app.py
```

Windows PowerShell verwendet entsprechend `.\.venv\Scripts\python.exe`.
Die lokale Adresse `http://127.0.0.1:8501` gehört zum **eigenen Rechner, auf dem
der Befehl läuft**, nicht als externer Link zur Codex-Instanz. Terminal offen lassen.
Bei belegtem Port `--server.port 8502`. Keine externen Dienste im Betrieb nötig;
Paketinstallation vorher mit Netz durchführen. Keine Updates direkt vor der Demo.

Portabilität tatsächlich getestet: eigenständigen vollständigen lokalen Clone mit
kopierten vorhandenen uncommitteten App-Dateien unter einem **anderen Pfad mit
Leerzeichen** eingerichtet, keine Modelle/Daten generiert. `.git` ist ein echtes
Verzeichnis, keine Objekt-Alternates und kein Remote vorhanden. Damit besteht keine
Verbindung zur alten gemeinsamen Worktree-Git-Struktur. Projektpfade werden relativ
zu Moduldateien aufgelöst; im aktiven App-Code gibt es keine Codex-spezifischen
absoluten Pfade.

Im verschobenen Bestand wurden Nutzer-/Git-Basisprüfung, U001-Kennzahlen,
Regression/Ranking, Nullwochen und ein Regressionstestfall sowie beide Ansichten
mit AppTest geprüft. Zusätzlich wurde dort ein **wirklicher Streamlit-Server** auf
einem separaten Testport gestartet und mit Chromium bedient: Health HTTP 200,
U001 mit beiden Freigaben und gespeicherter Prognose erfolgreich. Die vorhandene
installierte Python-Umgebung wurde für diesen Linux-Test wiederverwendet; eine
`.venv` wurde nicht als portabel kopiert. Die Laptop-`.venv` muss neu erstellt werden.
Windows/macOS wurden nicht auf echten Betriebssystemen getestet; die Zeilenenden-
prüfung simuliert Windows-Git-Konfiguration, keine komplette Windows-Installation.
Vor dem Vortrag ist ein Probelauf auf dem konkreten Laptop erforderlich.

Erforderliche lokale Git-Objekte: `a8f97ad75c378329a614a322bd541f372de0b072`
für die unveränderte Engine und `23ac008651de490d59e9ec5ceae590ba97daf0e5`
für die Lab-Verifikation. Vollständigen Clone verwenden, keinen flachen Checkout,
keine reine ZIP-/Worktree-Dateikopie. `.gitattributes` verhindert unerwünschte
Zeilenendenkonvertierung. Die Integritätsprüfungen wurden nicht abgeschwächt.

**Wichtig vor AP 7.5b:** Die App-Dateien sind weiterhin uncommittet. Ein Clone des
jetzigen GitHub-Branches liefert noch nicht die vollständige Anwendung; dort liegen
bislang die früher veröffentlichten Screenshots. Der Demo-Leitfaden nennt diese
Grenze ausdrücklich. Die Veröffentlichung des vollständigen Projektstands ist ein
separater nächster Schritt, keine in dieser Abnahme behauptete Fähigkeit.

## 33. AP 7.5a – Tatsächliche Browser- und Bildabnahme

Die optimierte Anwendung wurde mit Chromium gegen den tatsächlich gestarteten
Streamlit-Server geprüft. User View, Moduswechsel, Nutzerauswahl U001/U002/U003/U100,
Freigabeentzug und Rückkehr aus dem Lab wurden bedient. Die vier Hauptexperimente
wurden mit ihren realen Ergebnissen geprüft: beide Nullwochenvarianten, gespeicherte
k-Werte, U001-Testfall Zielwoche 23 und die exakten fünf Vorher-/Nachher-Angebote.
Alle sieben Lab-Bereiche und die Navigation dazwischen wurden geöffnet.

Desktop-Bilder verwenden 1366 × 1000 Pixel. Zusätzlich wurde das Laptop-Layout mit
1366 × 768 geprüft. In einem frischen mobilen Browserkontext mit 390 × 1000 wurden
User View und alle sieben Lab-Bereiche samt Sidebar-Navigation geprüft. Dokument
und Hauptbereich hatten keine horizontalen Seitenüberläufe; keine JavaScript-
Seitenfehler, keine angezeigten Python-Ausnahmen. Die Browserprüfung protokollierte
keine externen HTTP-Anfragen. Details: `work/ap75a/browser-result.json` und
`work/ap75a/browser.log`. Dies ersetzt keine vollständige WCAG-Zertifizierung.

Sechs aktuelle PNG-Dateien wurden nach der Optimierung erstellt, visuell geprüft
und mit Pillow auf Lesbarkeit validiert. Desktop-Aufnahmen zeigen gezielt den
jeweiligen Ergebnisbereich, keine vollständigen langen Seiten:

- `work/ap75a/screenshots/mova-user-desktop.png`
- `work/ap75a/screenshots/mova-lab-data-preparation.png`
- `work/ap75a/screenshots/mova-lab-kmeans.png`
- `work/ap75a/screenshots/mova-lab-regression.png`
- `work/ap75a/screenshots/mova-lab-empfehlungssystem.png`
- `work/ap75a/screenshots/mova-user-mobile.png`

Diese Bilder sind neue AP-7.5a-Aufnahmen; die bereits auf GitHub vorhandenen
AP-7.2-Bilder wurden nicht als aktuelle Abnahmebilder verwendet oder ersetzt.
Die verfügbare Bildansicht dient der internen Prüfung, eine für den Nutzer sichtbare
Bildanlage oder Dateivorschau lässt sich hier nicht zuverlässig bereitstellen.
Die GitHub-Integration konnte ein früher veröffentlichtes PNG lesend abrufen;
der bereits erprobte Weg über GitHub-Dateien ist daher für AP 7.5b verfügbar.
In AP 7.5a wurden keine neuen Dateien hochgeladen oder veröffentlicht. Der
Codex-Server ist keine automatisch vom eigenen Rechner erreichbare Webvorschau.

## 34. AP 7.5a – Demo-Leitfaden und abschließende Integrität

Neu: `documentation/dashboard_demo_guide.md` mit Python 3.12, vollständigem Git-
Bestand und benötigten Objekten, Installation aus dem Lockfile, Startbefehlen für
Unix und PowerShell, lokaler Adresse auf dem eigenen Laptop, vier Experimenten,
Nutzern/Einstellungen, erwarteten Zahlen, Grenzen und einem 15-Minuten-Ablauf.
Der temporäre zusätzliche Portabilitätsserver wurde nach erfolgreicher Prüfung
beendet; der reguläre Dashboard-Server bleibt bestehen.

Abschließend wurden alle **171 versionierten Dateien bytegenau gegen die Git-
Blobs von HEAD geprüft**: unverändert. Damit sind insbesondere Rohdaten, Modelle,
Engine und bisher veröffentlichte Screenshots unverändert. HEAD bleibt
`33e889c11837a8e878b039835f0e9faf4de21850`; der Index ist leer und
`git diff --check` meldet keine Fehler. Kein Training, Commit, Pull Request oder
GitHub-Schreibzugriff wurde durchgeführt.

In diesem Arbeitsschritt veränderte vorhandene AP-7-Dateien:
`app.py`, `dashboard/styles.css`, `dashboard/analytics_view.py`,
`documentation/dashboard_execution.md`.
Neue dauerhafte Dateien: `.gitattributes`,
`tests/test_dashboard_acceptance.py`, `documentation/dashboard_demo_guide.md`.
Prüfskripte, Protokolle, der isolierte Portabilitätsbestand und sechs Bilder liegen
nur im ignorierten temporären Bereich `work/ap75a/`. Die übrigen bereits vorhandenen
uncommitteten AP-7-Dateien wurden nicht als neue AP-7.5a-Änderungen gezählt.

**Abnahmeentscheidung:** AP 7.5a ist bestanden; alle sieben Analysebereiche und
vier Präsentationsexperimente sind geprüft. AP 7.5b zur gezielten GitHub-Sicherung
kann beginnen. Verbleibende Voraussetzungen sind die separate Veröffentlichung
des vollständigen App-Stands sowie der Probelauf auf dem tatsächlichen
Präsentationslaptop. Windows/macOS wurden nicht auf echter Hardware getestet.
Es gibt keinen festgestellten kritischen Funktionsfehler; die bekannten
wissenschaftlichen Einschränkungen bleiben ausdrücklich sichtbar.

## 35. AP 7.5b – Vollständige GitHub-Sicherung vorbereitet

GitHub-main wurde über die GitHub-Integration erneut geprüft und steht unverändert
auf `23ac008651de490d59e9ec5ceae590ba97daf0e5`. Feature-Branch vor Sicherung:
`ap7-dashboard`, HEAD `33e889c11837a8e878b039835f0e9faf4de21850`.
Keine neuen Basisänderungen oder Konflikte. Kein Reset und kein Force-Push.

Die vollständige trainingsfreie Suite wurde erneut ausgeführt: **178 entdeckt,
157 bestanden, 21 ausgeschlossen**, keine Fehler. Unveränderte Ausschlussgründe:
9 K-Auswahltests und 9 Stabilitätstests mit trainierendem Klassen-Setup sowie
1 K-Means-Reproduktionstest und 2 Regressionstrainingstests. KMeans.fit,
LinearRegression.fit und StandardScaler.fit waren gesperrt. `pip check` erfolgreich.
Die Suite prüft erneut die tatsächlichen wissenschaftlichen Ergebnisse,
400 Regressionstestfälle, 100 Empfehlungsvergleiche und Freigabesperren.
Browsernachweise aus AP 7.5a gelten weiterhin: kein Anwendungscode verändert.

Alle 171 bisherigen versionierten Dateien wurden vor der gezielten Übernahme der
finalen Screenshots bytegenau gegen HEAD verifiziert. Anschließend wurden nur die
beiden bisherigen User-View-PNGs durch die finalen Bilder ersetzt; vier Lab-PNGs
kommen hinzu. Das frühere Analytics-Desktop-PNG bleibt als historisches Bild bestehen.
Die sechs aktuellen Bilder stammen unverändert aus `work/ap75a/screenshots/`,
sind lesbare PNGs (je 53–142 kB) und zeigen ausschließlich synthetische Nutzer,
fiktive Angebote und Projektkennzahlen; keine sichtbaren Zugangsdaten.

Die Veröffentlichungsauswahl umfasst Anwendung, beide Ansichten, alle sieben
Lab-Bereiche, Konfiguration, LF-Attribute, Requirements/Lock, fünf neue Testdateien
inklusive trainingsfreiem Runner, Konzept, Ausführungsprotokoll, Demo-Leitfaden und
sechs finale Bilder. Keine .venv, Caches, Logs, Browserprofile oder temporären
Testdaten. Quelltext-/Dokumentationsprüfung und Suche nach typischen Geheimnissen
ergaben keine Zugangsdaten oder echten Garmin-Daten in der Auswahl. Das ist eine
Prüfung des konkreten Dateibestands, keine allgemeine Datenschutz-Zertifizierung.

Der Demo-Leitfaden beschreibt nun den vollständigen Clone des Feature-Branches.
Python 3.12, Neuinstallation der .venv aus Lockfile und die beiden benötigten
historischen Git-Objekte bleiben Voraussetzung. Linux-Start im verschobenen Clone
ist geprüft; Windows/macOS bleiben praktisch ungeprüft. K-Means/Regression ändern
keine Angebotsreihenfolge; keine neuen Modelle, kein Training, keine Istwerte für
die Demo-Prognosewoche und kein Qualitätsnachweis für die Empfehlungen.

Die GitHub-Veröffentlichung und der Pull Request werden nach dieser Prüfung
separat anhand von Commit, vollständigem Git-Baum und sechs abrufbaren PNGs
verifiziert. Der Pull Request wird nicht automatisch zusammengeführt; main bleibt
unverändert. Commit-/PR-IDs werden im Abschlussbericht genannt, damit dieser
Commit keine selbstreferenzierende Commit-ID benötigt.
