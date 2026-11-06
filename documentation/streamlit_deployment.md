# MOVA – AP 2.6: bestehende Streamlit-App aktualisieren

Bestehende URL: https://mova-big-data-analytics.streamlit.app/

## Befund und Korrektur

Die User View ruft `dashboard.services.user_context()` auf. Dessen Engine-Aufruf
verwendet den erweiterten 38er-Katalog einschließlich `data/catalog/`.
Die Angebotsbegründungen werden direkt in den Angebotskarten angezeigt. Der
Expander „So entsteht der Ausblick“ erläutert zusätzlich die Prognoseberechnung;
er ist zum Lesen der Modellbeiträge an den Angeboten nicht erforderlich.

Ein echter Deploymentfehler wurde ausgehend von Commit
`2141d9480343e68e83405b385127dd3b85b791b2` reproduziert:
Ein frischer lokaler Clone mit `--depth 1` enthält nicht die historischen
Git-Objekte, die `verify_tracked_bytes()` bisher mit `git show a8f97ad…` benötigte.
Dadurch brach der Empfehlungskontext mit `CalledProcessError` ab. Auch Analytics
Lab und die technische Statusprüfung benötigten alte Git-Objekte.

Die betroffenen Prüfungen verwenden jetzt die bereits versionierten SHA-256-Werte
in `documentation/ml_recommendations_preservation_v1.json`. Dateiänderungen
werden weiterhin abgelehnt; vollständige Git-Historie ist zur App-Laufzeit nicht
mehr erforderlich. Ranking, Modelle, Daten und gespeicherte Auswertungen wurden
nicht verändert. Pfade bleiben über `__file__` am Repository verankert.

Zusätzlich delegiert die Community-Cloud-Einstiegsdatei `requirements.txt` jetzt
an die vorhandene `requirements-dashboard.txt` mit festen Versionen. Diese lädt
wiederum die unveränderten Modellanforderungen. Bisher installierte die
Einstiegsdatei ungepinnte Pakete; abweichende Modellbibliotheken konnten damit
nicht ausgeschlossen werden. Das ist ein behobenes Deploymentrisiko, kein
Nachweis der auf der veröffentlichten Instanz tatsächlich installierten Pakete.

## Nachweise

- 212 Tests, 190 bestanden, 22 Trainingstests gezielt übersprungen, keine Fehler.
- Getestete direkte Versionen: Python 3.12, Streamlit 1.66.1, Plotly 6.4.0,
  pandas 2.2.3, scikit-learn 1.8.0.
- Drei neue Tests: Quellarchiv ohne Git und abweichendes Arbeitsverzeichnis;
  Analytics-Prüfung ohne Git einschließlich Manipulationsablehnung;
  tatsächliche User View mit gesperrtem historischem Git-Zugriff.
- U070 erhält O032, O034, O035, O006 und O004. O032 erklärt K-Means,
  O034 die Regression. Keine sichere Teilnahme oder Leistungsfähigkeit wird behauptet.
- Der vorhandene Vierfachvergleich wird weiterhin gegen aktuelle Outputs aller
  100 Nutzer geprüft. Seine historische Quellcodeprovenienz bleibt an den
  AP-2.4-Commit gebunden; alte Auswertungsdateien wurden nicht überschrieben.
- Alle 156 geschützten Bestandsdateien bleiben bytegleich. Kein Training.

## Was in Streamlit Community Cloud zu prüfen ist

1. Die **bestehende** App verwalten; Repository
   `pati0303/MOVA-Big-Data-Analytics`, Branch `main`, Einstieg `app.py` prüfen.
   Eine eventuell früher verwendete Dashboard- oder Feature-Branch-Zuordnung
   muss auf `main` zeigen. Die URL muss nicht neu erstellt werden.
2. Python **3.12** als Laufzeit prüfen. Die Versionsvorgaben stammen aus dieser
   Umgebung. Eine abweichende Python-Version gegebenenfalls entsprechend umstellen.
3. Nach dem Korrektur-Push den Build/Neustart abwarten und die Logs prüfen:
   Wird der neue main-Commit ausgecheckt? Werden `requirements.txt` und darüber
   `requirements-dashboard.txt` verarbeitet? Kein Fehler beim Import oder Laden
   der Daten/Modelle? Falls kein automatischer Neustart erfolgt, „Reboot app“ verwenden.
4. Seite neu laden, **USER VIEW** wählen, danach **U070** auswählen.
5. **Erst nach der Nutzerauswahl beide Schalter aktivieren:**
   „Simulierte Interessenfreigabe“ und „Simulierte Garmin-Freigabe“.
   Jeder Nutzerwechsel setzt beide Schalter absichtlich zurück.
6. Unter „Neue Möglichkeiten entdecken“ O032/O034/O035 und die vollständigen
   Begründungen direkt in den Karten prüfen. Nur die Interessenfreigabe genügt
   nicht für aktivitätsbezogene ML-Varianten.

Die veröffentlichte Instanz konnte aus der Arbeitsumgebung nicht geöffnet werden:
Der ausgehende Netzwerkproxy lehnt die Streamlit-Domain mit HTTP 403 beim
CONNECT-Aufbau ab. Diese Antwort kommt vom Proxy, nicht von der MOVA-App.
Es besteht auch kein Zugriff auf das Community-Cloud-Verwaltungsportal oder
seine Buildlogs. Deshalb sind tatsächliche Branch-Zuordnung, laufender Commit,
installierte Pakete und erfolgreicher Neustart dort noch vom Betreiber zu prüfen.
Die lokale Deploymenttauglichkeit ist nachgewiesen; die erfolgreiche Aktualisierung
der konkreten veröffentlichten Instanz wird damit nicht behauptet.
