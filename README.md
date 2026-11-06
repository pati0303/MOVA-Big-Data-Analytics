# MOVA-Big-Data-Analytics
MOVA – Move beyond: CRISP-DM Big Data Analytics Project

## Projekt und Ziele

MOVA – Move beyond ist ein Hochschulprojekt im Modul Big Data Analytics. Die geplante datenbasierte Personal-Advisor-Plattform soll synthetische Smartwatch-Aktivitätsdaten analysieren und personalisierte Empfehlungen für Sport, Freizeit, Outdoor, Wellness und weitere Lebensbereiche ableiten.

Das Projekt folgt CRISP-DM. Im Mittelpunkt stehen nachvollziehbare Data Preparation, verständliche theoretische Erklärungen, transparente Modelllogik sowie reproduzierbare Ergebnisse und Visualisierungen. Tatsächlich durchgeführte Iterationen und Rücksprünge werden dokumentiert.

Geplant sind K-Means zur Erkennung ähnlicher Aktivitätsprofile, eine sportartenübergreifende lineare Regression zur Prognose der Anzahl der Trainingseinheiten in der folgenden Woche und einfache regelbasierte Empfehlungen.

## Projektstruktur

- `data/reference/`: lokale Referenzdaten; Inhalte werden nicht versioniert.
- `data/raw/`: lokale Rohdaten; Inhalte werden nicht versioniert.
- `data/processed/`: später aufbereitete synthetische Daten.
- `src/`: späterer Python-Code für Aufbereitung und Analyse.
- `outputs/figures/`: spätere Abbildungen.
- `outputs/tables/`: spätere Ergebnistabellen.
- `outputs/models/`: spätere gespeicherte Modelle.
- `documentation/`: Entscheidungen, CRISP-DM-Protokoll und Datenwörterbuch.
- `app/`: Platzhalter für eine spätere Anwendung.

Leere Verzeichnisse enthalten `.gitkeep`, damit Git sie abbildet.

## Python-Umgebung

Die benötigten Bibliotheken stehen in `requirements.txt`. Installation bei Bedarf:

```bash
python -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
```

Die Versionsliste ist noch nicht fixiert. Für spätere reproduzierbare Analysen müssen die verwendeten Python- und Bibliotheksversionen sowie Konfigurationen und Zufallsseeds dokumentiert werden.

## Datenschutz und aktueller Stand

Persönliche Garmin-Originaldaten gehören ausschließlich in die lokal ignorierten Verzeichnisse `data/raw/` oder `data/reference/` und dürfen nicht in GitHub veröffentlicht werden. Zusätzliche Ignore-Regeln erfassen typische Garmin-Exportformate und Dateien mit „garmin“ im Namen. `.gitignore` schützt nicht bereits versionierte Dateien und kann nicht jede beliebig benannte Exportdatei erkennen; vor Commits deshalb die vorgemerkten Dateien prüfen.

Der aktuelle Demonstrator enthält synthetische V2-Daten, gespeicherte Modelle, die Streamlit-Oberfläche und die Ergebnisse zweier CRISP-DM-Zyklen. Die ML-gestützte Empfehlungsintegration ist nachfolgend beschrieben.


## Aktuelle Empfehlungsengine · AP 2.2

Die User View verwendet 38 fiktive Angebote: 30 unveränderte Bestandsangebote und
acht separat gespeicherte Ergänzungen. Interessen filtern verbindlich; historische
Sportartenanteile bestimmen die übergeordnete Reihenfolge. Innerhalb vergleichbarer
Varianten wählen gespeicherte K-Means-Segmente die vorgesehene langfristige
Nutzungshäufigkeit und die bestehende Regression passende Terminformate.
Je Angebotsgruppe erscheint höchstens eine Variante. Es gibt keinen ML-Gesamtscore.
Die Zuordnungen und Schwellen sind dokumentierte Demonstrationsannahmen, keine
Aussagen über Fitness, Terminzusagen oder nachgewiesene Empfehlungsqualität.

- Implementierung und Ergebnisse: `documentation/ml_recommendations_ap22.md`
- Abschluss und robuste Rückfälle: `documentation/ml_recommendations_ap24.md`
- Katalogergänzung und versionierte Regeln: `data/catalog/`
- Vierfachvergleich: `outputs/ml_recommendations_v1/`
- Reproduktion ohne Training: `python src/ml_recommendation_evaluation.py`
- Tests ohne Modelltraining: `python tests/run_without_training.py`

Der historische AP-6-Vergleich im Analytics Lab bleibt bei 30 Angeboten.
Die öffentliche Engine-Funktion `run()` und der Dashboard-Adapter nutzen die neue
Logik. `load_data()` lädt standardmäßig weiterhin den Referenzkatalog; neue
Analyseaufrufe verwenden ausdrücklich `include_catalog_extension=True`.
