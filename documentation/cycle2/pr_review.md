# AP9 – Prüfung für den Pull Request

Stand: 04.11.2026. Branch `feature/crispdm-cycle-2`, Ziel `main`.
Remote-main vor Veröffentlichung geprüft: dd8208abda5371b178d39095b25f6f6140681167.

## Umfang

Bestehende Änderungen ausschließlich in app.py, dashboard/state.py,
dashboard/analytics_view.py und tests/test_dashboard.py. Die Änderungen registrieren
den achten Lab-Bereich, passen den Navigationszähler und die Erwartung der letzten
registrierten Seite an. Keine Änderung an User View, bestehenden Modellen, Daten
oder Ergebnissen. Neue Daten, Dokumentation und Ergebnisse ausschließlich unter
cycle2-Verzeichnissen. Neue Implementierung und Tests besitzen eigene Dateien.
Keine work-Dateien, lokalen Umgebungen oder zusätzlichen Rohdaten im PR.

## Wissenschaftliche und technische Prüfung

Historisches Merkmal zählt exakt Nullaktivitäten in t-3 bis t pro Nutzer.
Ziele t+1 bleiben getrennt; Trainingsziele sind beim jeweiligen Fit verfügbar.
Drei freigegebene Folds, genau drei Verfahren, sechs OLS-Fits je Experimentlauf.
Die ursprünglichen Testfälle bleiben von Entwicklung und Entscheidung ausgeschlossen.
Der neue Lab-Loader verwendet gespeicherte Aggregate mit Hash- und Konsistenzprüfung.

## Erneut ausgeführte Prüfungen

- 8 Tests aus test_cycle2.py bestanden, einschließlich Zukunftsinvarianz,
  Wochenzuordnung, Foldtraining und Kennzahlenkontrolle.
- 7 Tests aus test_data_preparation_regression.py bestanden.
- 58 Dashboardtests aus test_dashboard*.py bestanden. Fit-Sperren für
  LinearRegression, KMeans und StandardScaler waren aktiv. Alte Lab-Ansichten,
  User View, Freigaben und neue Zyklus-2-Seite werden geprüft.
- Vollständiger Experimentlauf reproduziert die gespeicherten Dateien bytegleich.
- Zusätzlich src/cycle2_verify.py ausgeführt: schreibfreie Reproduktion aller
  zehn Experimentartefakte. Manifestvergleich erlaubt ausschließlich einen anderen
  aktuellen HEAD, weil der ursprüngliche Basiscommit historische Provenienz ist;
  Codehash, Software, Quellhashes und alle Ausgabehashes bleiben strikt gleich.
- Hashvergleich aller im Laufmanifest verzeichneten Experimentartefakte bestanden.
- git diff --check ohne Befund.

Reproduktion nach dem Commit:

```bash
python -m unittest discover -s tests -p 'test_cycle2.py' -v
python -m unittest discover -s tests -p 'test_data_preparation_regression.py' -v
python -m unittest discover -s tests -p 'test_dashboard*.py' -v
python src/cycle2_verify.py
```

Voraussetzung: vorhandene Modellierungs-/Dashboard-Abhängigkeiten. Der ursprüngliche
Schreiblauf verweigert nach einem neuen HEAD ein abweichendes Laufmanifest; deshalb
für spätere Prüfung den expliziten schreibfreien Verifikationsaufruf verwenden.

## Ergebnis und Grenzen

Gepoolter MAE: Persistenz 1,729167, bisherige Regression 1,522613,
Erweiterung 1,523105. Die Erweiterung gewinnt in zwei Folds, erfüllt aber die
UND-Regel wegen höherem Gesamt-MAE nicht. Merkmal verworfen; bestehendes Modell
bleibt erhalten. Kein neuer unabhängiger Testnachweis, keine Signifikanzbehauptung.
Kein Merge vorgesehen.
