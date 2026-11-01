# MOVA – kompakter Demo-Leitfaden (AP 7.5a)

Ziel: ungefähr 15 Minuten, vorhandene Funktionen vorführen. Kein vollständiger
Sprechtext. Ausschließlich synthetische Daten; keine echten Garmin-Verbindungen.

## 1. Vollständigen Projektbestand vorbereiten

**Stand AP 7.5b:** Die vollständige Anwendung wird auf `ap7-dashboard` gesichert.
Den veröffentlichten Branch verwenden; `main` enthält sie erst nach einer separat
geprüften Zusammenführung des Pull Requests.

Für die Demo einen vollständigen AP-7-Projektbestand als eigenständiges Git-Repository
verwenden. Nur eine ZIP-Datei oder eine Kopie des Worktrees mit einem `.git`-Verweis
auf die Codex-Umgebung genügt nicht. Datenverifikation benötigt lokale Git-Objekte.
Ein normaler vollständiger Clone des veröffentlichten Branches ist der
bevorzugte Weg, ohne `--depth` und ohne Sparse Checkout:

```bash
git clone --branch ap7-dashboard https://github.com/pati0303/MOVA-Big-Data-Analytics.git
cd MOVA-Big-Data-Analytics
```

Erforderlich: Python **3.12** (geprüft 3.12.14), Git im PATH, `app.py`, `dashboard/`,
`.streamlit/`, Requirements-Dateien und der vollständige bestehende Bestand unter
`src/`, `data/`, `outputs/`, `documentation/` sowie die Git-Historie.
`.gitattributes` erhält die geprüften LF-Dateibytes auch bei Windows-Git-Einstellungen.

Im Repository-Stamm prüfen:

```bash
python --version
git --version
git cat-file -e '23ac008651de490d59e9ec5ceae590ba97daf0e5^{commit}'
git cat-file -e 'a8f97ad75c378329a614a322bd541f372de0b072^{commit}'
```

Beide Git-Prüfungen müssen ohne Fehler enden. `.venv` niemals zwischen Rechnern
kopieren, sondern auf dem Präsentationsrechner neu erstellen.

## 2. Installation und lokaler Start

Linux/macOS, im Repository-Stamm mit Python 3.12:

```bash
python -m venv .venv
.venv/bin/python -m pip install -r requirements-dashboard-lock.txt
.venv/bin/python -m pip check
.venv/bin/python -m streamlit run app.py
```

Windows PowerShell, ebenfalls Python 3.12 und Repository-Stamm:

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements-dashboard-lock.txt
.\.venv\Scripts\python.exe -m pip check
.\.venv\Scripts\python.exe -m streamlit run app.py
```

Die Aktivierung der Umgebung ist bei diesen Befehlen nicht nötig. Direkte
Projektanforderungen stehen ergänzend in `requirements-dashboard.txt`; für die
Demo reproduzierbar die vollständigen Lock-Versionen verwenden. Streamlit 1.66.1,
Plotly 6.4.0 und die bestehenden Modellbibliotheken bleiben festgelegt.

**Nur auf dem Rechner, auf dem dieser Befehl läuft**, im Browser die lokale Adresse
`http://127.0.0.1:8501` öffnen. Das ist kein externer Link zum Codex-Server.
Terminal offen lassen; `Ctrl+C` beendet den Server. Ist Port 8501 belegt, mit
`--server.port 8502` starten und die lokale Adresse entsprechend ändern.

Installation benötigt Paketdownload-Zugriff; der danach geprüfte App-Betrieb benötigt
keine externen Dienste oder Assets. Vorher vollständige Installation und Start testen.
Keine Paketaktualisierung direkt vor der Präsentation. Der verschobene eigenständige
Clone wurde unter Linux tatsächlich geprüft; Windows/macOS wurden in dieser
Umgebung nicht ausgeführt und sollten auf dem konkreten Laptop vorher getestet werden.

## 3. Orientierung und Ausgangszustand

- Oben zwischen **USER VIEW** und **ANALYTICS LAB** wechseln.
- Gemeinsame Nutzerwahl zunächst **U001**. Im Lab führt die linke Navigation zu sieben Bereichen.
- Beide Schalter sind anfangs aus. Für persönliche Beispiele explizit **simulierte
  Garmin-Freigabe** und für Angebote zusätzlich **simulierte Interessenfreigabe** aktivieren.
- Ein Nutzerwechsel setzt beide Freigaben zurück. Ein Moduswechsel behält Nutzer
  und Freigaben desselben Nutzers; er erteilt keine neuen Rechte.
- Aggregierte Lab-Ergebnisse bleiben ohne Freigaben sichtbar. Gesamtübersichten bei
  Regression/Empfehlungen lassen sich aufklappen; freigegebene Einzelfälle stehen im Fokus.

Kurzer Einstieg User View: U001 mit beiden Freigaben zeigt 34 Aktivitäten, Ø1,31
Aktivitäten/Woche, Ø80,2 Minuten/Woche, 16 aktive und 10 Nullwochen. Die dortige
Prognose **2,69** betrifft **06.–12.07.2026**, nicht den historischen Regressionstest.

## 4. Reihenfolge der vier Hauptexperimente

### 1 – Nullwochen (Analytics Lab → Data Preparation → Nullwochen)

Keine persönliche Freigabe nötig. Zwischen **Mit Nullwochen** und **Ohne Nullwochen**
wechseln. Erwartete Werte:

| Variante | Nutzerwochen | Nullwochen in Auswahl | Aktivitäten/Woche |
| --- | ---: | ---: | ---: |
| Vollständig | 2.600 | 558 | 2,4865 |
| Nur aktive Wochen | 2.042 | 0 | 3,1660 |

Aktivitätssumme bleibt 6.465; kleinerer Nenner erzeugt **+27,33 %**. Histogramm und
Erklärung ändern sich. Fachliche Aussage: Auslassungsverzerrung beim Mittelwert,
kein Nachweis besserer Modelle. Bei Rückfragen **Skalierung** (U001, Garmin an,
`share_running`, Schritt 3) oder **Zeitlicher Split** zeigen.

### 2 – K-Means (linke Navigation → K-Means)

**Silhouette** auswählen; k=2 und anschließend k=3/6/8 vergleichen, danach zu k=2
zurückkehren. Gespeicherte Seed-42-Silhouetten: **0,303337 / 0,184642 / 0,194309 /
0,206130**. Unter **Finale Segmente · k=2** die Größen **57/43** und das Profilmerkmal
`avg_activities_per_week` zeigen.

Fachliche Aussage: k=2 hat in diesen Ergebnissen die beste Silhouette und hohe
Stabilität, aber nur moderate Trennung. Andere k werden nicht live trainiert.
Für k=6/8 fehlen Profile/Zuordnungen. Segmente beschreiben relative Häufigkeit,
keine Fitness oder Gesundheit. Garmin ist nur für den individuellen Kontext nötig.

### 3 – Regression (linke Navigation → Regression)

**U001**, Garmin an, **Test-Zielwoche 23**, **Berechnungsschritt 3**.
Die zugehörige Eingabewoche 22 endet am 07.06.2026; Ziel ist 08.–14.06.2026.

| Sichtbarer Wert | Ergebnis |
| --- | ---: |
| Aktuelle Wochenaktivität | 1 |
| Vierwochenmittel einschließlich aktueller Woche | 2,25 |
| Tatsächliche Zielaktivitäten | 2 |
| Gespeicherte Regression | 2,0219 |
| Persistence-Baseline | 1 |
| Absoluter Regressionsfehler / Baselinefehler | 0,0219 / 1,0000 |

Die drei Koeffizientenbeiträge ergeben die gespeicherte Prognose. Bei Bedarf
Schritt 1 für die vier vergangenen Wochen, Schritt 2 für X oder eine andere
Zielwoche wählen. Gesamtübersicht bleibt aufklappbar. Fachliche Aussage: historische
Einwochenprognose ohne Zukunft in X; kein neues Training. Dieser Testfall und die
User-View-Demo für Juli sind unterschiedliche Zielwochen.

### 4 – Empfehlungen (linke Navigation → Empfehlungssystem)

**U001**, beide simulierten Freigaben an. Die kompakten Listen zeigen:

- **Ohne Tags:** O001, O002, O003, O004, O005 (alle B).
- **Mit acht bestätigten Tags:** O001(A), O006(A), O009(A), O010(A), O002(B).

Eintritte/Austritte, behaltene Positionen und Rangstufen erklären. Die Begründungen
sind unter jeder Liste aufklappbar. Nur die bestehende Engine bestimmt die
Reihenfolge; acht manuell bestätigte Sporttags ergänzen die Kategorienvorauswahl.
Ein ungetaggtes Angebot wie O002 bleibt zulässig.

**Gesamtergebnis** aufklappen: 64/100 veränderte Zusammensetzungen, 344/475 A-Slots
(**72,42 %**), 81 Nutzer mit mindestens einem A-Angebot. Unterschiedliche Nenner
benennen. Das belegt Regelwirkung, keine höhere Empfehlungsqualität oder Umsätze.
Optional U002 zeigen: Liste unverändert, aber teilweise Rangstufe B→A; dabei nach
Nutzerwechsel beide Freigaben erneut aktivieren.

## 5. Zeitplan und Abschluss

| Teil | Richtwert |
| --- | ---: |
| Orientierung und kurze User View | 1,5 min |
| Nullwochen; Skalierung/Split nur kurz bei Bedarf | 3 min |
| K-Means | 2 min |
| Regression | 3 min |
| Empfehlungen | 2,5 min |
| Evaluation und Nullzielgruppen | 2 min |
| CRISP-DM und Grenzen | 1 min |

Evaluation: Gesamt-MAE **1,489877 gegen 1,71**, Verbesserung **12,87 %**. Bei
**Zielwoche=0** nur 92 Fälle: **1,878292 gegen 1,380435**; Regression ist schlechter.
Die zukünftige Nullzielgruppe ist vorher unbekannt und darf kein Modell auswählen
(Data Leakage). CRISP-DM: tatsächliche Simulation 1,0→1,3 mit technischer Kontrolle;
Git-Probleme sind keine fachliche Iteration.

## 6. Stabile Vorführung und bekannte Grenzen

- Vorab lokal starten und die vier Experimente einmal durchgehen; Notebook am Strom,
  Browserzoom 100 %, unnötige Tabs schließen. Laptopansicht ist geprüft; längere
  Rechenwege/Quellen bleiben scrollbar oder aufklappbar.
- Nach jedem Klick das fertige Ergebnis abwarten; nicht während eines Reruns weiterklicken.
- Wenn etwas fehlt: sichtbaren Status nennen, Projektdateien/Git-Basis/Umgebung prüfen;
  keine alten Werte als aktuelles Ergebnis ausgeben, keine Freigaben automatisch setzen.
- Synthetische Daten, begrenzte Übertragbarkeit, moderate Clustertrennung und individuelle
  Prognosefehler. Keine echten Einwilligungen, Kausal-, Fitness- oder Umsatznachweise.
- Keine Istwerte oder Unsicherheitsintervalle für die Demo-Zielwoche im Juli vorhanden.
- Vollständiger Abnahmenachweis und Testausnahmen: `dashboard_execution.md`.
