# MOVA – Ergebnis der ersten Simulation

Erste synthetische Datensimulation – noch keine vollständige Data Preparation oder Modellierung durchgeführt.

Zeitraum: 2026-01-05 bis 2026-07-05; 26 vollständige Wochen (ISO-KW 02–27). Seed: 42.
Python-Standardbibliothek; Ausführung: `python src/data_generation.py` vom Repository-Verzeichnis.

- Nutzer: 100
- Aktivitäten: 6665
- Angebote: 30 (alle fiktiv)
- Nutzerwochen: 2600
- Aktivitäten je Nutzer/Woche einschließlich Nullwochen: 2.563
- Minimum / Maximum je Nutzerwoche: 0 / 10
- Nutzerwochen ohne Aktivität: 545 (21.0%)

## Sportarten

| Sportart | Aktivitäten | Anteil |
|---|---:|---:|
| Running | 974 | 14.6% |
| Cycling | 1207 | 18.1% |
| Strength | 873 | 13.1% |
| Swimming | 584 | 8.8% |
| Walking | 1109 | 16.6% |
| Hiking | 863 | 12.9% |
| Tennis | 525 | 7.9% |
| Padel | 530 | 8.0% |

## Aktivitätsverläufe

Intern zugewiesene Generierungsmechanismen (keine gemessenen oder gespeicherten Nutzerlabels):
- steigend: 21
- konstant: 22
- sinkend: 18
- schwankend: 39

Tatsächlich beobachteter deskriptiver Vergleich: Mittelwert der letzten sechs minus der ersten sechs Wochen; Schwelle ±0,5 Aktivitäten/Woche. Dies identifiziert insbesondere keine schwankenden Verläufe und ist keine Regression.
- steigend: 35
- sinkend: 41
- ähnliches Anfangs-/Endniveau: 24

## Technische Datenqualität

BESTANDEN: 100 eindeutige Nutzer, vollständiger Zeitraum, 2.600 eindeutige Nutzerwochen inklusive Nullen, Abgleich aller Wochenzählungen mit den Aktivitäten, eindeutige Aktivitäts-IDs, bekannte Nutzer, acht erlaubte und vorhandene Sportarten, gültige ISO-Daten, Pflichtfelder, endliche und sportartspezifisch begrenzte Dauern und Distanzen, gezielt leere Distanzen, boolesche Interessen, 30 eindeutige fiktive Angebote mit gültigen Kategorien/Preisen/Rabatten.

## Einordnung und nächster Prüfschritt

Nullwochen und Unterschiede zwischen vorgegebenen und beobachteten Trends sind beabsichtigt: Pausen und Zählrauschen überlagern die Grundentwicklung. Die Tabellen enthalten ausschließlich simulierte Beobachtungen; keine empirischen Befunde.

Die Obergrenze von zehn Aktivitäten pro Woche und abgeschnittene Dauern können Randhäufungen verursachen. Sportarten, Häufigkeiten, Nullwochen und auffällige Randwerte sollten fachlich mit den Projektzielen abgeglichen werden. Geschwindigkeiten sind Annahmen, keine Leistungsdiagnostik. Wetter, Feiertage, Saison, Verletzungen und Messfehler fehlen. Interessen sind bewusst unabhängig; reale Zusammenhänge werden nicht behauptet.

CRISP-DM: Beitrag zu 2.1 Collect Initial Data / 3.3 Construct Data. Tatsächlich durchgeführt: Generierung und technische Kontrolle. Kein fachlicher Review, keine vollständige Data Preparation, keine Modellierung und kein abgeschlossener iterativer CRISP-DM-Rücksprung. Ein Rücksprung wird erst nach tatsächlicher Prüfung und Anpassung dokumentiert.
