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

Aktuell ist ausschließlich die Projektstruktur eingerichtet. Es wurden keine synthetischen Daten, Modelle, Benutzeroberflächen, Analyseergebnisse oder CRISP-DM-Iterationen erstellt. Die Dokumentationsdateien enthalten Vorlagen für die spätere Arbeit.
