# MOVA – AP 2.4: robuste Rückfälle und Feature-Abschluss

Stand: 06.11.2026. Branch: `feature/ml-recommendations`.

## Fehlerkorrekturen

`src/recommendation_engine.py:recommend_user()` übernimmt nur Clusterkennungen
`'0'` und `'1'` mit exakt passendem vorhandenem Label. Fehlende, unbekannte oder
ungültig typisierte Kennungen sowie fehlende/widersprüchliche Labels bleiben
`cluster_id=None`, `segment_label=None`, `segment_status=missing_or_ineligible`.
Es werden keine Modellwerte ergänzt. Die Variantenwahl entspricht dann der
Kontrolle ohne K-Means; eine gültige Regression bleibt unabhängig davon aktiv.

`predict_activity()` fängt `EOFError` und `AttributeError` unmittelbar um
`joblib.load()` ab. Der Fehlerstatus lautet `model_unavailable_or_invalid`;
`prediction_error_type` dokumentiert ausschließlich den Ausnahmetyp. Die Prognose
bleibt `None`, ihre Quelle `not_computed`. Keine Ersatzprognose und kein
Regressionseinfluss; Interessen, Sportpassung und gültiges K-Means bleiben aktiv.
Die User View zeigt die fehlende Prognose, behält aber ihre Empfehlungen.

## Ergänzte Tests

Vier zusätzliche Testmethoden in `tests/test_ml_recommendations.py`:

- Ungültige Clusterkontexte: fehlende/ unbekannte IDs, fehlende/null Labels,
  ungültige ID-Typen und widersprüchliche Labels; Referenzwahl und weiter aktive Regression.
- `EOFError` beim Modellladen über den echten Dashboard-Service: kein Kontextverlust,
  keine Prognose, keine Regressionswirkung, K-Means bleibt aktiv.
- Derselbe Nachweis für `AttributeError`.
- User View für beide Ladefehler: keine App-Fehler, fünf Empfehlungen,
  Prognose nicht verfügbar und keine behauptete Regressionswirkung.

Vollständiger Testlauf ohne Training: **209 Tests, 187 bestanden, 22 gezielt
übersprungen, keine Fehler**. Die übersprungenen Tests würden Modelle neu
trainieren. KMeans.fit, LinearRegression.fit und StandardScaler.fit sind im
Testläufer gesperrt. Die Testumgebung entspricht der im AP-2.2-Bericht beschriebenen
isolierten UI-Installation; keine Projekt-Dependencies wurden ersetzt.

## Reproduzierbarkeit und Bestandsschutz

Die Auswertung wurde über `ml_recommendation_evaluation.compare()` im Speicher
neu berechnet, ohne bestehende Ergebnisexporte zu überschreiben. Alle 100
Nutzerprofile und alle vier Empfehlungsvarianten stimmen vollständig mit
`outputs/ml_recommendations_v1/comparison.json` überein:

| Einfluss | Geänderte Top 5 gegenüber gruppierter Kontrolle / 100 |
|---|---:|
| Nur K-Means | 63 |
| Nur Regression | 9 |
| Beide | 63 |

Alle 156 geschützten Dateien aus
`documentation/ml_recommendations_preservation_v1.json` sind bytegleich.
Trainingsdaten, Nutzerinteressen, Modelle, Modellmetriken und beide bisherigen
CRISP-DM-Zyklen bleiben unverändert. Auch comparison.json und top5.csv wurden
nicht neu geschrieben. Das neue ML-Auswertungsmanifest enthält den aktualisierten
Engine-Quellhash und den vorherigen Hash zur Nachvollziehbarkeit der Korrektur.
Der ursprüngliche AP-2.2-Testnachweis bleibt historisch erhalten; der aktuelle
Nachweis steht in `outputs/ml_recommendations_v1/ap24_validation.json`.

Die neuen CSV-Quellen und CSV-Auswertung erhalten explizite `-text`-Regeln in
`.gitattributes`, damit Git ihre im Manifest geprüften Bytes nicht normalisiert.
Die Git-Filterprüfung bestätigt die bytegleiche Behandlung. Bestehende Dateien
werden von diesen neuen, eng begrenzten Regeln nicht erfasst.

## Abschluss

Die Integration und die beiden gefundenen Fehlerpfade sind technisch geprüft.
Keine neuen Nutzer, Angebote oder Präsentationsfunktionen wurden ergänzt.
Die fachlichen Einschränkungen aus AP 2.2 bleiben bestehen: Demonstrationsannahmen,
sportartenübergreifende unsichere Prognose und kein empirischer Nachweis einer
verbesserten Empfehlungsqualität. Die alten CRISP-DM-Logs bleiben unverändert.

Der Abschlusscommit soll die vollständige bisher uncommittete ML-Integration,
Korrekturen, Tests, Katalogmetadaten, neue separate Auswertungen und Dokumentation
enthalten. Temporäre Testlogs und isolierte Dependencies liegen außerhalb des
Repositories. Ein Merge oder Push gehört nicht zu diesem Arbeitspaket.
