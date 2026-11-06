# MOVA V3 – Integration mit vollständiger V2-Oberfläche

Branch: `feature/mova-v3-integration`. Grundlage: main `9ec32dcbd683004cd640605a4c49db3cf007d3fe`.
Verbindliche V2-Referenz: `feature/final-lab-log`, Commit `53595cbace3a5002a9401ba84d9512c1368127c5`.

## Vergleich der tatsächlichen Oberfläche

Alle 15 Dateien aus app.py, dashboard/ und .streamlit/ wurden anhand ihres
Inhalts geprüft. Zehn bleiben bytegleich mit V2. CSS, Farbwerte, Abstände,
Kartenvorlagen, Diagramme, Navigation und bestehende interaktive Ansichten sind
vollständig vorhanden. Es wurde kein älteres Gestaltungssystem eingesetzt.
Die Bezeichnung V2 im bestehenden Kopftext bezeichnet weiterhin die unveränderte
synthetische Datengrundlage; MOVA V3 ist der neue Integrationsstand der Anwendung.

| Bestandteil | MOVA V2 | MOVA V3 | Ergebnis |
|---|---|---|---|
| Theme, Farben, CSS, Design-Tokens | Dunkles MOVA-Design | Dieselben Dateien und Werte | unverändert |
| Kopfbereich, Navigation, Nutzerwahl | User View / Analytics Lab | Gleiche Anordnung, Labels und Optionen | unverändert |
| Simulierte Freigaben | Zwei Schalter, Reset bei Nutzerwechsel | Dieselbe Zugriffs- und Resetlogik | unverändert |
| User-View-Kennzahlen | Aktivitäten, Wochenmittel, Minuten | Identische Werte und Darstellung | unverändert |
| User-View-Diagramme | Verlauf und Sportverteilung | Identische Plotly-Spezifikationen | unverändert |
| Analytics Lab | Acht Seiten einschließlich Zyklus 2 | Alle acht Seiten, gleiche Widgets und Diagramme | unverändert |
| Analytics-Erklärungen | Verbesserungen aus 53595cb | Erhalten, zusätzlich Abgrenzung historischer Auswertung / aktueller ML-Regeln | bewusst erweitert |
| Angebotskarten | Interessens-/Sportbegründungen | Gleiche HTML-Struktur und CSS; zusätzliche echte ML-Begründungen | bewusst erweitert |
| Auswahl von Angebotsvarianten | Interessen und Sportanteile | Zusätzlich Cluster und kurzfristige Prognose | bewusst erweitert |
| Technischer Status / Dateiprüfung | Historische Git-Objekte erforderlich | Versionierte Prüfsummen ohne alte Git-Historie | bewusst erweitert |
| Mobile Darstellung | Responsive V2-Darstellung | Gleiche Breiten, kein horizontaler Überlauf bei 390 px | unverändert |

Gegenüber V2 unterscheiden sich ausschließlich diese fünf Oberflächendateien:

- `app.py`: korrekter technischer Dateistatus statt Git-Historienstatus; kein Layoutwechsel.
- `dashboard/user_view.py`: zusätzliche ML-Begründungen und passende Erläuterungen in bestehenden Karten.
- `dashboard/analytics_view.py`: bestehende V2-Texte plus aktuelle ML-/Historienabgrenzung.
- `dashboard/data_access.py`: unveränderte Datenaggregation, portable Prüfsummenprüfung.
- `dashboard/analytics_data.py`: gleiche Analytics-Daten und Darstellungen, portable Prüfsummenprüfung.

Bytegleich sind `.streamlit/config.toml`, `dashboard/__init__.py`, `charts.py`,
`components.py`, `cycle2.py`, `design.py`, `services.py`, `state.py`, `styles.css`
und `views.py` (jeweils unter dashboard/, sofern nicht anders angegeben).

## Inhaltliche Konfliktauflösung

Der Merge ergab Konflikte in `dashboard/analytics_view.py` und
`tests/test_dashboard_explanations.py`. Jede Konfliktstelle wurde einzeln geprüft:
Die gemeinsamen V2-Erklärungen bleiben vollständig; die fachlich überholte
Aussage „K-Means und Regression bestimmen die Angebotsreihenfolge nicht direkt“
wird durch die präzise Trennung zwischen altem AP-6-Vergleich und aktueller
ML-Variantenwahl ersetzt. Der zugehörige Test prüft diese aktuelle Aussage.
Es wurde keine pauschale Branch-Version für den gesamten Merge übernommen.

Die ML-Engine, Modelle und das Regelwerk von main bleiben unverändert.
Alle 22 zusätzlichen Lab-Branch-Artefakte wurden bytegleich übernommen:
Word-Fassungen, Lab-Log-Markdowns, Audit, zehn Abbildungsdateien sowie
retrospektive Auswertung, Skript und zwölf Tests. Historische Dokumente wurden
nicht redaktionell überschrieben. Bereits vorhandene SVG-Leerzeichen bleiben
zur Bytegleichheit erhalten; sie sind keine neue Codeabweichung.

## Nachweise

- Gesamte Testsuite ohne Modelltraining: **226 Tests; 204 bestanden, 22 Trainingstests
  gezielt übersprungen, keine Fehler**.
- Zwei neue Referenztests sichern die Design-Dateigrenzen und alle 22 importierten
  Lab-Artefakte anhand der verbindlichen V2-Prüfsummen ab.
- Getrennte AppTest-Prozesse für V2 und V3: User View plus alle acht Analytics-Seiten;
  Navigation, Widget-Labels/-Optionen, Modellkennzahlen und alle 16 Plotly-Spezifikationen
  stimmen überein. Die erwarteten zusätzlichen Erklärungstexte werden separat geprüft.
- Chromium-Prüfung für beide Versionen bei 1440 × 1000 und 390 × 844 Pixeln:
  Diagramme tatsächlich gerendert; Nutzerwahl und beide Freigabeschalter bedient;
  fünf Angebotskarten vorhanden; K-Means-/Regressionsbegründungen sichtbar.
- Desktop-Karten: gleiche Hintergrund-/Text-/Rahmenfarben, 16 px Radius, 24 px Innenabstand,
  624 px Breite. Mobil: 358 px Kartenbreite; Hauptbereich 390 px breit und 390 px scrollWidth.
  Längere Erklärungstexte erhöhen erwartungsgemäß die Kartenhöhe, ohne das Design zu ersetzen.
- U070: **O032, O034, O035, O006, O004**. O032 erklärt den K-Means-Beitrag,
  O034 den Regressionsbeitrag. Historischer Prognosezeitraum bleibt 06.–12.07.2026.
- Vergleich aller 100 Nutzer im Speicher: vollständige Übereinstimmung mit bisherigen
  ML-Ergebnissen, Modellwirkung weiterhin **63/9/63**. Keine alten Ergebnisdateien überschrieben.
- Alle **156 geschützten Bestandsdateien** sind unverändert. Kein Training und keine neuen Angebote/Nutzer.

Maschinenlesbare Nachweise: `mova_v3_reference.json` und `mova_v3_validation.json`.
Screenshots der beiden Versionen liegen unter `screenshots/mova_v3/`:

- [V2 Desktop](screenshots/mova_v3/v2_u070.png) / [V3 Desktop](screenshots/mova_v3/v3_u070.png)
- [V2 Mobil](screenshots/mova_v3/v2_mobile.png) / [V3 Mobil](screenshots/mova_v3/v3_mobile.png)
- [V3 Angebotskarte mit ML-Begründung](screenshots/mova_v3/v3_offer.png)

## Freigabestatus

Gemessen an der vorgegebenen V2-Branch-Referenz wurden keine gestalterischen oder
funktionalen Rückschritte gefunden. Die Integrationsversion ist zur finalen
Freigabe vorbereitet. Die Prüfung erfolgte lokal mit dem vollständigen Repository;
eine Aktualisierung der veröffentlichten App gehört nicht zu diesem Schritt.
`main` bleibt auf `9ec32dc`, der bestehende Deployment-Branch und die veröffentlichte
App bleiben ebenfalls unverändert. Es erfolgt ausschließlich ein Commit auf
`feature/mova-v3-integration`, kein Merge in main und kein Push.
