# MOVA – CRISP-DM-Grafiken

## Erzeugte Abbildungen

1. `01_crisp_dm_gesamtprozess.svg` / `.png`: beide vollständigen Zyklen, Dateniteration innerhalb von Zyklus 1 und Übergang aus der Nullzielschwäche zur zweiten Modellierung.
2. `02_crisp_dm_zyklus_1.svg` / `.png`: sechs Phasen und 24 Arbeitsschritte des ersten Zyklus; Inhalte nach der im Chat bereitgestellten ausgefüllten MOVA-Grafik.
3. `03_crisp_dm_zyklus_2.svg` / `.png`: sechs Phasen und 24 Arbeitsschritte des zweiten Zyklus; vollständige verbindliche Zuordnung aus der Nutzerfreigabe.

Die Detailgrafiken übernehmen die Struktur der bereitgestellten Originalvorlage von Prof. Schieder: sechs nebeneinanderliegende Spalten, vertikale Trennlinien, weiße rechteckige Phasenköpfe mit dunklem versetztem Schatten und darunter die Arbeitsschritte in ursprünglicher Reihenfolge. Die Vorlage wurde aus der im Chat übergebenen Rasterabbildung nachgesetzt, nicht als originale Vektordatei übernommen. Die farbige MOVA-Kartenanordnung wurde nicht als Detailgestaltung verwendet. Die Gesamtübersicht ist eine eigenständige Prozessdarstellung.

## Bearbeitung und Reproduktion

- SVG-Dateien enthalten editierbare Textobjekte, keine in Pfade umgewandelten Buchstaben.
- `crisp_dm_content.json`: bearbeitbare Texte, Phasen und Schrittüberschriften.
- `generate_crisp_dm.py`: bearbeitbare Layoutquelle, benötigt Python, Matplotlib und Pillow. Keine Importe von Modellierungs- oder Dashboardcode.
- Aufruf vom Repository-Stamm: `python documentation/figures/generate_crisp_dm.py`.
- PNG-Auflösungen: Gesamtübersicht 4050 × 2565 Pixel; Detailgrafiken je 4950 × 2850 Pixel. SVG kann verlustfrei vergrößert werden.
- Empfohlene Schrift: DejaVu Sans. Bei anderer Schriftinstallation kann ein SVG-Editor Ersatzschriften verwenden und dadurch Umbrüche verschieben; die PNGs behalten die geprüfte Darstellung.

## Prüfbericht

- Je Detailgrafik sechs Phasen und exakt 24 vollständige Arbeitsschritte.
- Alle 24 englischen Schrittüberschriften und alle 24 deutschen Beschreibungen je Detailgrafik im erzeugten SVG geprüft; Zeilenumbrüche werden bei der Textprüfung normalisiert.
- Textrechtecke im Renderer automatisch paarweise auf Überschneidung und Überschreitung der Zeichenfläche geprüft: keine Befunde.
- Spaltenbreiten und untere Textgrenzen geprüft; Details in `layout_checks.json`.
- PNG-Dateien dekodiert und auf gültige Bildstruktur geprüft; visuelle Kontrolle der Gesamtübersicht und beider Detailgrafiken durchgeführt.
- Zwei vollständige Zyklen von der frühen Dateniteration abgegrenzt. Änderungen an Häufigkeiten zwischen V1 und V2 werden nicht als Wirkung des Präferenzexponenten dargestellt; dessen Effekt wird im gepaarten Kontrollvergleich angegeben.
- Testleistung aus Zyklus 1 und interne Validierung aus Zyklus 2 ausdrücklich getrennt. Übernahmeregel korrekt als UND-Verknüpfung dargestellt; Erweiterung verworfen.
- Zyklus-1-Abschlussangaben einschließlich 157 trainingsfreier Tests sind als historischer AP-1–8-Stand gekennzeichnet; keine neuen Testergebnisse behauptet.
- Ausschließlich neue Grafik-/Quelldateien in diesem Verzeichnis erstellt. Keine Modellläufe, Datenänderungen, Dashboardänderungen, Git-Operationen oder PR-Erstellung.

## Offener Quellenpunkt

Die genaue bibliografische Angabe der Lehrvorlage (Foliensatz, Jahr, Folien-/Seitenzahl) wurde nicht mitgeliefert. Für das finale wissenschaftliche Lab-Log sollte diese Quellenangabe ergänzt werden. Die Zuschreibung „Prof. Schieder“ folgt der Nutzerangabe; eine pixelgenaue Übereinstimmung mit einer nicht vorliegenden Originaldatei wird nicht behauptet.
