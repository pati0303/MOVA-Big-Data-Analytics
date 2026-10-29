# Projektentscheidungen

Hier werden künftig tatsächlich getroffene Entscheidungen mit Begründung und Auswirkungen dokumentiert.

## Vorlage für einen Eintrag

- Datum:
- CRISP-DM-Phase:
- Fragestellung / Kontext:
- Betrachtete Alternativen:
- Entscheidung und Begründung:
- Auswirkungen auf Daten, Modellierung oder Reproduzierbarkeit:
- Verweise auf zugehörige Dateien / Prüfungen:

Noch keine fachlichen oder methodischen Entscheidungen eingetragen.


## Entscheidung MOVA-DATA-002 – V2 als aktive Datengrundlage

- Datum: 29.10.2026.
- CRISP-DM: Abschluss der ersten Construct-Data-/Qualitätsprüfungsiteration, Grundlage der folgenden Aufbereitung.
- Entscheidung des Projektteams: V2 mit Präferenzexponent 1,3 verbindlich übernehmen. Historische V1 vollständig erhalten.
- Begründung: Mittel des Top-2-Anteils 64,12 % gegenüber V1 59,41 %, 40 statt 59 Nutzer mit acht Sportarten. Alle Sportarten und Überschneidungen bleiben vorhanden.
- Kausale Einordnung: Getrennte Kontrolle mit Exponent 1,0 liefert 57,61 % Top-2 und 58 Nutzer mit acht Sportarten. Kontrolle und V2 haben identische Wochenzählungen. Unterschiede 6.665→6.465 Aktivitäten und 545→558 Nullwochen gegenüber V1 stammen aus dem technischen Wechsel der Zufallsquellen, nicht aus geänderten Häufigkeitsparametern.
- Alternativen: V1 beibehalten oder weitere Anpassungen. Die moderate V2 erfüllt das vereinbarte Demonstrationsziel ohne zusätzliche fachliche Regeln.
- Umsetzung: aktive Dateien unter data/raw, passende vollständige Wochenkontrolle unter outputs/tables; V1 vor der Ersetzung anhand des Snapshot-Manifests und direkter SHA-256-Vergleiche geprüft. V2 ebenfalls gegen die zuvor generierten Vergleichsdateien geprüft. Standardaufruf src/data_generation.py generiert künftig V2, keine V1.
- Historie: vollständiger V1-Snapshot und vorhandene historische Berichte bleiben unverändert. Die frühere Aussage „Noch keine ... Entscheidungen eingetragen“ beschreibt den damaligen Vorlagenstand.
- Einschränkungen: synthetische, nicht empirisch validierte Daten; kein Nachweis besserer Cluster- oder Prognosequalität. Seltenere Sportarten verlieren teilweise Anteile, Dauern ändern sich mit dem Mix, Saison und Messfehler fehlen. AP 4 muss Nullwochen und nicht anwendbare Distanzen korrekt behandeln.
- Git-Umfang: aktive V2-Rohdaten, V1-Archiv, benötigte Skripte/Konfigurationen, zugehörige Wochenkontrolle und relevante historische/vergleichende Kennzahlen sowie Grafiken. Zusätzliche V2-/Kontroll-Rohdatenkopien bleiben lokal, werden aber ignoriert und bei Bedarf reproduziert.
- Nachweise: simulation_config.md, active_data_version.json, ../outputs/tables/simulation_report_v2.md sowie ../outputs/simulation_comparison/comparison_report.md.
