# MOVA – AP 2.2: implementierte ML-Empfehlungen

Stand: 06.11.2026. Branch `feature/ml-recommendations`, Basis
`4a312743928d0d2e3adf4e2a89c245302d9672f4`. Online-Abgleich von main bestätigt.
Historischer Demo-Stichtag: 05.07.2026, Prognoseziel: 06.–12.07.2026.

## Änderungen und Katalog

Die öffentliche Engine `src/recommendation_engine.py:run()` und damit
`dashboard/services.py:recommendation_context()` verwenden die Erweiterung.
`load_data()` bleibt standardmäßig für historische Analysen beim 30er-Katalog;
`include_catalog_extension=True` lädt den 38er-Katalog und seine Metadaten.
Die bestehende Rohangebotsdatei und die bestätigte Sporttag-Datei bleiben bytegleich.

`data/catalog/offers_extension_v1.csv` ergänzt O031–O038 mit den beauftragten
fiktiven Titeln. Preise/Rabatte sind frei erfundene Demonstrationswerte:

| ID | Preis EUR | Rabatt % |
|---|---:|---:|
| O031 | 89,00 | 10 |
| O032 | 139,00 | 15 |
| O033 | 35,00 | 10 |
| O034 | 69,00 | 15 |
| O035 | 49,00 | 5 |
| O036 | 99,00 | 10 |
| O037 | 179,00 | 15 |
| O038 | 29,00 | 5 |

`data/catalog/recommendation_metadata_v1.json` enthält alle 38 IDs, Gruppen,
bestätigte bzw. ausdrücklich beauftragte Sporttags, Nutzungseignung,
Terminzahl, Regel, Prüfstatus und fachliche Begründung. Bestehende Angebote
erhalten keine neuen Sporttags. Neue Zuordnungen sind Demonstrationsannahmen.

## Tatsächlich implementierte Regeln

1. Unveränderter verbindlicher Interessenfilter und simulierte Freigabeprüfung.
2. Bestehende Sportpassung: bestätigter Tag mit Anteil >0 vor reinem Kategorienangebot;
   größter passender Anteil absteigend, ID als stabiler Gleichstandsentscheid.
3. Vergleichsgruppen belegen die erste Position ihrer Mitglieder in dieser Rangfolge.
   Innerhalb der Gruppe wird genau eine Variante gewählt; ML verschiebt keine
   unabhängigen Gruppen. Es gibt keine allgemeinen Boni oder Maluspunkte.
4. Gruppe `running_shoes`: O001 als allgemeine neutrale Referenz, O031 gelegentlich,
   O032 häufig. `hiking_sets`: O036 gelegentlich, O037 häufig.
   Gültiger Cluster 0 bevorzugt gelegentliche, Cluster 1 häufige Nutzung.
5. Gruppe `running_instruction`: O033 Einzeltermin, O034 drei Termine pro Woche.
   Zentrale Demo-Schwellen: Prognose <2 bevorzugt O033; >=3 bevorzugt O034;
   [2,3) bleibt neutral. Keine empirisch optimierten Grenzen.
6. Ohne gültiges Modelloutput oder ohne passende autorisierte Sporthistorie bleibt
   die ID-basierte Referenzvariante bestehen. Die beiden Signale wirken auf
   getrennte Gruppen; die Metadatenvalidierung verbietet gemischte ML-Regeln.
7. Die ersten fünf unterschiedlichen Gruppen liefern ihre gewählte Variante.

O009 Wanderrucksack und die neuen Sets bleiben unterschiedliche Gruppen;
Wanderführung und Tageswanderung ebenfalls. O035 Halbmarathon und O038 Tageswanderung
bleiben ML-neutral, weil allgemeine Aktivitätshäufigkeit keine Teilnahmefähigkeit belegt.
Neutrale Angebote erhalten keine eigenen ML-Abzüge. Neue Kandidaten können sie
allerdings durch reguläre Sportpassung aus den fünf verfügbaren Plätzen verdrängen.

Technik: `src/ml_recommendation_rules.py:extend_catalog()` validiert die Metadaten;
`select_variants()` wählt die Varianten; `explain()` beschreibt tatsächliche Einflüsse.
`recommendations()` liefert Gruppenkennung, Sportanteil, Referenzvariante,
Kandidaten, angewendetes Signal und getrennte Änderungsflags.
Eine bestätigte, aber unveränderte Auswahl wird nicht als verursachter Rangwechsel ausgegeben.
Der Anteil wird numerisch angezeigt; auch ein seltener Sportmatch ist kein Beleg hoher Relevanz.

## Nachweis beider Modelle und Vierfachvergleich

Alle Varianten verwenden dieselben tatsächlichen Nutzerinformationen und eine pro Nutzer
mit dem gespeicherten Modell berechnete Prognose; kein Refit, keine speziellen Nutzerregeln.
Die gemeinsame Kontrollbedingung verwendet denselben 38er-Katalog und dieselbe Gruppierung,
aber deaktiviert beide ML-Signale. So bleiben Katalog- und Diversitätseffekte kontrolliert.
Die tatsächliche ursprüngliche 30er-Liste sowie die ungruppierte 38er-Liste stehen zusätzlich
pro Nutzer in der Ergebnisdatei.

| Variante | Geänderte Top 5 gegenüber gruppierter Kontrolle / 100 Nutzer |
|---|---:|
| Ohne ML | 0 |
| Nur K-Means | 63 |
| Nur Regression | 9 |
| Beide | 63 |

Dass beide zusammen 63 statt 72 Nutzer verändern, folgt aus überlappenden Nutzergruppen.
Die Zählung ist ein Wirkungsnachweis der Regeln, kein Qualitätsnachweis.

Konkreter kontrollierter Vergleich für U070:

| Variante | Top 5 |
|---|---|
| Ohne ML | O001, O033, O035, O006, O004 |
| Nur K-Means | O032, O033, O035, O006, O004 |
| Nur Regression | O001, O034, O035, O006, O004 |
| Beide | O032, O034, O035, O006, O004 |

## Tatsächliche Live-Demo

### U070

Interessen: Outdoor, Sport. Cluster 1; tatsächliche Prognose 3.326195370018.

1. **O032 – FIKTIV – Laufschuhe für häufige Nutzung**: Dieses Angebot gehört zu deiner ausgewählten Interessenkategorie Sport. Im betrachteten Zeitraum wurden bei dir Aktivitäten der Sportart Running aufgezeichnet; die Sportzuordnung ist im fiktiven Demo-Katalog ausdrücklich festgelegt. Dein gespeichertes langfristiges Aktivitätssegment bevorzugt innerhalb dieser Angebotsgruppe die Variante für häufige Nutzung. Dies ist eine Demonstrationsannahme zur Nutzungshäufigkeit, keine Bewertung deiner Leistungsfähigkeit. Historischer Anteil: 40.2% der Aktivitäten; dies beschreibt beobachtetes Verhalten, keine gesicherte persönliche Relevanz.

2. **O034 – FIKTIV – Laufkurs – drei Termine pro Woche**: Dieses Angebot gehört zu deiner ausgewählten Interessenkategorie Sport. Im betrachteten Zeitraum wurden bei dir Aktivitäten der Sportart Running aufgezeichnet; die Sportzuordnung ist im fiktiven Demo-Katalog ausdrücklich festgelegt. Deine Prognose für 2026-07-06 bis 2026-07-12 beträgt rund 3.33 Aktivitäten insgesamt. Nach der Demonstrationsregel wird innerhalb dieser Laufkursgruppe das Format mit drei Terminen pro Woche bevorzugt. Die Gesamtprognose sagt keine drei Laufaktivitäten oder Terminverfügbarkeit voraus; sie ist keine Teilnahmevoraussetzung. Historischer Anteil: 40.2% der Aktivitäten; dies beschreibt beobachtetes Verhalten, keine gesicherte persönliche Relevanz.

3. **O035 – FIKTIV – Halbmarathon-Veranstaltung**: Dieses Angebot gehört zu deiner ausgewählten Interessenkategorie Sport. Im betrachteten Zeitraum wurden bei dir Aktivitäten der Sportart Running aufgezeichnet; die Sportzuordnung ist im fiktiven Demo-Katalog ausdrücklich festgelegt. Historischer Anteil: 40.2% der Aktivitäten; dies beschreibt beobachtetes Verhalten, keine gesicherte persönliche Relevanz.

4. **O006 – FIKTIV – Fahrradhelm**: Dieses Angebot gehört zu deiner ausgewählten Interessenkategorie Sport. Im betrachteten Zeitraum wurden bei dir Aktivitäten der Sportart Cycling aufgezeichnet; der Angebotsbezug ist manuell bestätigt. Historischer Anteil: 22.0% der Aktivitäten; dies beschreibt beobachtetes Verhalten, keine gesicherte persönliche Relevanz.

5. **O004 – FIKTIV – Tennistraining**: Dieses Angebot gehört zu deiner ausgewählten Interessenkategorie Sport. Im betrachteten Zeitraum wurden bei dir Aktivitäten der Sportart Tennis aufgezeichnet; der Angebotsbezug ist manuell bestätigt. Historischer Anteil: 4.9% der Aktivitäten; dies beschreibt beobachtetes Verhalten, keine gesicherte persönliche Relevanz.

### U044

Interessen: Outdoor, Sport, Wellness. Cluster 0; tatsächliche Prognose 1.703923897910.

1. **O009 – FIKTIV – Wanderrucksack**: Dieses Angebot gehört zu deiner ausgewählten Interessenkategorie Outdoor. Im betrachteten Zeitraum wurden bei dir Aktivitäten der Sportart Hiking aufgezeichnet; der Angebotsbezug ist manuell bestätigt. Historischer Anteil: 51.2% der Aktivitäten; dies beschreibt beobachtetes Verhalten, keine gesicherte persönliche Relevanz.

2. **O010 – FIKTIV – Wanderführung**: Dieses Angebot gehört zu deiner ausgewählten Interessenkategorie Outdoor. Im betrachteten Zeitraum wurden bei dir Aktivitäten der Sportart Hiking aufgezeichnet; der Angebotsbezug ist manuell bestätigt. Historischer Anteil: 51.2% der Aktivitäten; dies beschreibt beobachtetes Verhalten, keine gesicherte persönliche Relevanz.

3. **O036 – FIKTIV – Wanderausrüstungs-Set für gelegentliche Nutzung**: Dieses Angebot gehört zu deiner ausgewählten Interessenkategorie Outdoor. Im betrachteten Zeitraum wurden bei dir Aktivitäten der Sportart Hiking aufgezeichnet; die Sportzuordnung ist im fiktiven Demo-Katalog ausdrücklich festgelegt. Historischer Anteil: 51.2% der Aktivitäten; dies beschreibt beobachtetes Verhalten, keine gesicherte persönliche Relevanz.

4. **O038 – FIKTIV – Geführte Tageswanderung**: Dieses Angebot gehört zu deiner ausgewählten Interessenkategorie Outdoor. Im betrachteten Zeitraum wurden bei dir Aktivitäten der Sportart Hiking aufgezeichnet; die Sportzuordnung ist im fiktiven Demo-Katalog ausdrücklich festgelegt. Historischer Anteil: 51.2% der Aktivitäten; dies beschreibt beobachtetes Verhalten, keine gesicherte persönliche Relevanz.

5. **O006 – FIKTIV – Fahrradhelm**: Dieses Angebot gehört zu deiner ausgewählten Interessenkategorie Sport. Im betrachteten Zeitraum wurden bei dir Aktivitäten der Sportart Cycling aufgezeichnet; der Angebotsbezug ist manuell bestätigt. Historischer Anteil: 16.3% der Aktivitäten; dies beschreibt beobachtetes Verhalten, keine gesicherte persönliche Relevanz.

U044s Laufkursgruppe bevorzugt O033; diese Variante war bereits die neutrale
Referenz. Seine Laufschuhgruppe wählt O031 statt O001. Beide Laufgruppen erreichen
wegen des niedrigeren Laufanteils die Top 5 nicht. Die Top 5 sind für U044 in allen
vier Bedingungen gleich. Wellness ist erlaubt, wird aber nicht in die Top 5 gezwungen.

## Tests und Schutz bestehender Ergebnisse

Siehe den abschließenden Testnachweis unten. Der Testläufer verhindert KMeans.fit,
LinearRegression.fit und StandardScaler.fit. Bestehende Tests, die explizit neu
trainieren würden, werden ausgelassen; der neue AP-9-Trainingstest ist jetzt ebenfalls
im bestehenden No-Training-Läufer berücksichtigt. Tests für alte Dashboard-Listen
wurden für die aktuelle User View angepasst; der historische Vergleich wird weiter
gegen seine gespeicherten Resultate geprüft. Seine früheren Quellcodehashes werden
gegen den festen Basiscommit geprüft, anstatt neue Quellcodeänderungen zu verbieten.

`documentation/ml_recommendations_preservation_v1.json` enthält SHA-256-Werte
aller vor Beginn vorhandenen Dateien unter data/, outputs/ und documentation/.
Der neue Schutztest prüft sie unverändert. Keine Aktivitätsdaten, Nutzerinteressen,
Modelle, Modellmetriken, CRISP-DM-Ergebnisse oder Referenzauswertungen wurden geändert.

Reproduzieren mit installierten requirements:

```sh
python tests/run_without_training.py
python src/ml_recommendation_evaluation.py
```

Neue Evaluation: `outputs/ml_recommendations_v1/comparison.json`, `top5.csv`,
`manifest.json` (Quell- und Ergebnisprüfsummen). Kein bestehender Export wurde überschrieben.
Der Analytics-Lab-Bereich kennzeichnet seinen alten AP-6-Vergleich ausdrücklich.

## Grenzen und CRISP-DM-Lab-Log

Die Regression prognostiziert die Gesamtaktivität, keine drei Laufkursteilnahmen.
Termine, Sportfähigkeit, Erfahrung und Gesundheitszustand werden daraus nicht abgeleitet.
Das Regressionsmodell hat im bestehenden synthetischen Test MAE ~1,49 Aktivitäten/Woche;
Schwellenentscheidungen bleiben unsicher. Es gibt keine erfundenen Prognoseintervalle.
Gruppen und Schwellen sind fachliche Demonstrationsannahmen, nicht gelernt oder optimiert.
Die weiterhin bestehende A/B-Sportregel kann auch bei kleinen Anteilen neutrale
Wellness- oder Freizeitangebote verdrängen. Das neue System verspricht keine
nachgewiesene Verbesserung von Zufriedenheit oder Kaufwahrscheinlichkeit.

Für einen späteren Lab-Log-Eintrag: ursprüngliche Integrationslücke, getrennte Aufgaben
beider Modelle, beauftragte Katalogerweiterung, versionierte Annahmen, kontrollierte
Ablation, unveränderte Modelle/Daten und Grenzen dokumentieren. Dies ist eine Integration
in die Empfehlungsentscheidung, keine neue Modellierungsiteration und kein neuer
Nachweis der Modellgüte. Frühere CRISP-DM-Logs wurden nicht umgeschrieben.

## Geänderte und neue Projektdateien

```text
 M README.md
 M dashboard/analytics_view.py
 M dashboard/user_view.py
 M src/recommendation_engine.py
 M tests/run_without_training.py
 M tests/test_dashboard_explanations.py
 M tests/test_dashboard_user_view.py
 M tests/test_recommendation_comparison.py
 M tests/test_recommendation_engine.py
?? data/catalog/offers_extension_v1.csv
?? data/catalog/recommendation_metadata_v1.json
?? documentation/ml_recommendations_preservation_v1.json
?? outputs/ml_recommendations_v1/comparison.json
?? outputs/ml_recommendations_v1/manifest.json
?? outputs/ml_recommendations_v1/top5.csv
?? src/ml_recommendation_evaluation.py
?? src/ml_recommendation_rules.py
?? tests/test_ml_recommendations.py
```

## Abschließender Testnachweis

Vollständiger Lauf: **205 Tests, 183 bestanden, 22 gezielt übersprungen, keine Fehler**.
Die 22 ausgelassenen Tests würden Modelle trainieren und bleiben gemäß Auftrag gesperrt.
Enthalten sind elf neue AP-2.2-Tests einschließlich tatsächlicher Dashboard-Darstellung
für U070/U044 und Widerruf der Freigabe. Der vollständige Lauf verwendet Fit-Sperren.
Alle **156 geschützten Bestandsdateien** stimmen mit ihren Ausgangsprüfsummen überein.
`git diff --check` ist fehlerfrei.

Testumgebung: vorhandene pandas 2.2.3, scikit-learn 1.8.0 und joblib 1.5.3;
fehlende UI-Abhängigkeiten wurden außerhalb des Repositories isoliert ergänzt
(Streamlit 1.67.0, Plotly 7.1.0). Die isolierte Streamlit-Installation benötigte
beim Teststart `global.developmentMode=False`; die Projektkonfiguration blieb unverändert.
Es wurden keine Dependencies oder Modellartefakte im Projekt ersetzt.
