# Technischer Abschluss – Aktivierung V2

Aktive Version: V2, Exponent 1,3, Master-Seed 42 und getrennte Quellen 42–49.

BESTANDEN: 100 eindeutige Nutzer; 26 Wochen; 2.600 eindeutige Nutzerwochen; 6.465 Aktivitäten; 30 fiktive Angebote; 558 Nullwochen; keine doppelten Aktivitäts-IDs, ungültigen Daten, unbekannten Nutzer oder negativen Dauern; acht Sportarten vorhanden. Die vollständige vorhandene CSV-Prüfung einschließlich sportartspezifischer Distanz-/Dauergrenzen und Wochenzählungsabgleich wurde bei beiden Generatorläufen erfolgreich ausgeführt.

Vor Ersetzung: die drei V1-Rohdatensätze und V1-Wochenkontrolle waren SHA-256-identisch mit dem gesicherten V1-Snapshot. Nach Ersetzung und zwei Standard-Generatorläufen stimmen die aktiven Daten bytegenau mit der zuvor erzeugten V2 überein.

## Prüfsummen der aktiven Dateien

- `data/raw/activities_simulated.csv`: `c3789d26f00cba3ba14952cf99909b091cb263045b8993ed366fe5aa64a4ee6b`
- `data/raw/users_simulated.csv`: `6ba9f8398707412bf922c76e352d2a6a7f86857e7a54dbbf1421555b1dbf99f9`
- `data/raw/offers_simulated.csv`: `83748cb66918c08e3061889834e24452d0dc9feb6581690c4959cb3ba3775fa6`
- `outputs/tables/simulation_weekly_check.csv`: `70c290c2913ea976fe0bb370b1debf4d78febb5896247f5e02a1f8aa0b1381b8`

Alle 31 Dateien im historischen Snapshot stimmen weiterhin mit SHA256.json überein. Historische Berichte und Vergleichsmesswerte sind unverändert. Der Vergleichsaufruf wurde nach der Aktivierung erfolgreich wiederholt und lieferte dieselben Kennzahlen und Grafiken, ohne aktive Dateien zu verändern.

AP-1-Struktur vollständig. 16 Ignore-Prüffälle bestanden: nur die drei vorgesehenen aktiven Rohdaten freigegeben, sonstige Roh-/Referenzdaten und Garmin-Dateien weiterhin geschützt; historischer V1-Snapshot versionierbar; zusätzliche lokale Kontroll-/V2-Rohdatenkopien und identische Wochenkontrollen ignoriert. Keine persönlichen Daten aufgenommen. Kein Commit, kein Pull Request, keine Modellierung.
