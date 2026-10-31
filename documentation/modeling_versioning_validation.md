# MOVA – AP 5.8: Prüfung vor Versionierung

Stand: 31.10.2026. Worktree `/workspace/MOVA-AP5`, Branch `ap5-machine-learning`.
Bestätigte GitHub-main- und lokale Basis: `1b26533d2ceea30478577bd519244c245dd3e558`.
Alle 103 versionierten AP-1–AP-4-Dateien sind bytegleich mit dieser Basis.
AP 5 wird als separate Ergänzung versioniert, kein Eingriff in bestehende Modelle/Daten.

## Umfang und fachliche Dokumentationsprüfung

Tatsächlich vorhandene AP-5-Dateien: acht Modellierungs-/Prüfskripte, acht zugehörige
Testdateien, zwei Modelle und deren Metadaten, finale synthetische Nutzerzuordnungen,
Ergebnistabellen, elf PNGs sowie Modellierungsberichte, Nutzungsvertrag und Abschlussbericht.
Hinzu kommen dieser Prüfbericht und eine separate versionierte Modellierungsabhängigkeitsdatei.
Keine work-Dateien, Caches, virtuellen Umgebungen oder Rohdatenkopien aufnehmen.

| Erforderliche Begründung | Vorhandener Nachweis |
| --- | --- |
| K-Means für ähnliche Aktivitätsprofile; k=2 | kmeans_modeling_execution.md, modeling_evaluation.md: Algorithmus, Elbow/Silhouette und Teamentscheidung |
| Stabilität über Initialisierungen | kmeans_modeling_execution.md AP 5.2: 20 Seeds, jeweils n_init=20, 190 ARI-Paare je k |
| Relative Aktivitätssegmente statt Fitness/Erfahrung | Beide K-Means-Berichte und kmeans_inference_contract.md |
| Vollständige 26-Wochen-Historie, Inaktivität ohne künstliche Anteile | kmeans_inference_contract.md: Nenner/Erfassung, Sonderstatus, keine Nullimputation |
| Globale Regression und genau zwei Eingänge | regression_modeling_execution.md AP 5.4: gemeinsame Schätzung, jüngster Zustand und geglättetes Niveau |
| Chronologischer Split, keine Cluster als Regressoren | regression_modeling_execution.md: später beobachtete Ziele und Leakage-Grenzen |
| Persistenz als einfache bekannte Vergleichsregel | regression_modeling_execution.md AP 5.6: identische Fälle/Informationsstände, kein Training |
| Vorsicht trotz Gesamtverbesserung, große Einzelfehler | modeling_evaluation.md und AP 5.5/5.6: MAE/RMSE vs. individuelle Fehler |
| Zukünftige Nullziele und bekannte aktuelle Aktivitäten unterscheiden | modeling_evaluation.md: Zielgruppen nur Diagnose; aktuelle Eingänge bekannt, keine neue Umschaltregel |
| Grenzen synthetischer Daten und mögliche spätere Iterationen | modeling_evaluation.md: reale Validierung fehlt, Vorschläge nicht umgesetzt |

Geprüfte Kennzahlen: K-Means k=2, 100 Nutzer, Größen 57/43,
Silhouette 0,30333715184382104, Inertia 126,49790652947819; ARI=1 über 190 Paare.
Regression: 1.800 Training / 400 Test, MAE 1,4898770575225395;
Persistenz-MAE 1,71; relative Verbesserung 12,872686694588332 %.
Zukünftige Nullziele: 36,06527592727762 % Verschlechterung nach MAE.
Bekannte aktuelle Nullwoche: MAE 1,1138511612496416 vs. 1,3020833333333333;
aktuell positive Woche: 1,6086220773981914 vs. 1,8388157894736843.
Diese Zahlen stammen aus vorhandenen Ergebnisdateien, keine neue Modellvariante.

## Technische Tests und Artefakte

`python -m unittest discover -s tests -v`: **83 Tests bestanden**
(22 AP 4 + 61 AP 5). Die vorhandenen Tests überprüfen teilweise die deterministische
Trainingslogik erneut im Speicher; es wurden keine neuen Modellvarianten erstellt,
keine gespeicherten Modelle ersetzt und keine fachlichen Änderungen vorgenommen.
Gespeicherte Modelle separat gegen SHA-256, Parameter und Feature-Reihenfolge der
Metadaten geprüft und mit Joblib geladen. K-Means-Inferenz und reproduzierte Nutzerlabels
sowie Regression/Test-/Baselinewerte sind durch die Suite abgedeckt.

## Minimal ergänzte Modellierungsumgebung

Die bestehende requirements.txt ist für eine Wiederherstellung der Modellumgebung
unzureichend, weil sie keine Versionen bindet. Sie bleibt als frühere App-/Projektliste
unverändert. Neu: `requirements-modeling.txt` bindet die tatsächlich installierten
Modellierungs- und relevanten transitiven Laufzeitpakete einschließlich scikit-learn
1.8.0. Keine Paketinstallation oder Aktualisierung wurde durchgeführt.

Wiederherstellung mit **Python 3.12.14** in einer separaten Umgebung:

```bash
python3.12 -m venv work/modeling-venv
work/modeling-venv/bin/python -m pip install -r requirements-modeling.txt
work/modeling-venv/bin/python -m unittest discover -s tests -v
```

Die exakte Python-Patchversion ist vorher zu prüfen. Das ist eine dokumentierte
Wiederherstellungsanleitung, kein bereits ausgeführter Neuinstallationsnachweis.
Eine paketquellen-/plattformübergreifende Binär- oder Rendergleichheit ist damit
nicht garantiert. Die Originalumgebung ist anhand der Metadaten und Pins dokumentiert.
Für das spätere Dashboard benötigte Plotly-/Streamlit-Pakete sind nicht Teil dieser
schlanken Modellierungsumgebung. Joblib nur aus vertrauenswürdiger Projektquelle laden.

## Datenschutz und Umfangskontrolle

Alle ausgewählten Texte auf typische Zugangsdaten-/Token-/Private-Key-Muster geprüft:
keine Befunde. Synthetische Nutzerkennungen und Herkunft gegen V2-Metadaten bestätigt;
keine persönlichen Garmin-Originaldaten in den vorgesehenen Dateien festgestellt.
Binärartefakte stammen aus der eigenen hashgeprüften Modellierung; PNGs sind die
bereits geprüften synthetischen Ergebnisgrafiken. Ein Musterscan allein wäre kein
vollständiger Geheimnisnachweis; zusätzlich wurden Pfade, Datenrollen und Provenienz geprüft.
.gitignore schließt work, Caches, Umgebungen, lokale Credentials sowie typische
Garmin-Exporte aus; keine Änderung notwendig. Größte neue Datei rund 261 KB,
Gesamtumfang der Ergänzungen rund 1,34 MB. Keine unnötigen großen Dateien.

## Veröffentlichung

GitHub-main über Integration bestätigt. Direkter Git-Zugriff scheitert am nicht
verbindbaren Proxy auf Port 8080. Sichere Alternative: überprüfte lokale Blobs und
Git-Baum über GitHub-Integration übertragen; vollständige Baum- und Commit-Identität
vor Branchveröffentlichung kontrollieren. Kein Force-Push, kein Reset, kein automatisches
Merge. Verbindliche veröffentlichte Commit-ID und PR-Link werden nach erfolgreicher
Veröffentlichung im Abschluss ausgegeben, hier nicht vorweggenommen.
