"""Kontrollierte CRISP-DM-Iteration: V1 unverändert, Kontrolllauf und V2 separat.
Aufruf: python src/simulation_preference_comparison.py
Keine ML-Modelle; vorhandene Ergebnisse werden nicht überschrieben.
"""
import csv
import hashlib
import io
import json
import math
import os
import random
from collections import Counter
from datetime import timedelta
from pathlib import Path
import sys

import importlib.util

_snapshot_script = Path(__file__).resolve().parents[1] / "outputs/simulation_comparison/v1_snapshot/src/data_generation.py"
_spec = importlib.util.spec_from_file_location("mova_historical_v1", _snapshot_script)
original = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(original)
from data_generation import (SEED, N_USERS, N_WEEKS, START, END, SPORTS, PROFILES,
                             TRENDS, ACTIVITY_FIELDS, USER_FIELDS, OFFER_FIELDS,
                             clip, poisson)

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'outputs/simulation_comparison'
SNAPSHOT = OUT / 'v1_snapshot'
os.environ.setdefault('MPLCONFIGDIR', str(ROOT / 'work/__pycache__/matplotlib-cache'))
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from simulation_v2 import generate


def preserve_write(path, content):
    """Neue Datei schreiben; bei Wiederholung nur identische Inhalte akzeptieren."""
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.exists():
        if path.read_bytes() != content:
            raise FileExistsError(f'Abbruch: bestehende Datei würde verändert: {path}')
    else:
        with path.open('xb') as handle:
            handle.write(content)


def write_csv(path, rows, fields):
    buffer = io.StringIO(newline='')
    writer = csv.DictWriter(buffer, fieldnames=fields)
    writer.writeheader()
    writer.writerows(rows)
    preserve_write(path, buffer.getvalue().encode('utf-8'))


def metrics(activities, weekly):
    a = pd.DataFrame(activities)
    w = pd.DataFrame(weekly)
    counts = pd.crosstab(a.user_id, a.sport_type).reindex(columns=list(SPORTS), fill_value=0)
    diversity = counts.gt(0).sum(axis=1)
    top2 = counts.apply(lambda row: row.nlargest(2).sum() / row.sum() * 100, axis=1)
    user = pd.DataFrame({'Sportartenanzahl': diversity, 'Top2_Prozent': top2})
    summary = {f'Nutzer_{k}_Sportarten': int(diversity.eq(k).sum()) for k in range(1, 9)}
    summary.update({'Mittlere_Sportartenanzahl': diversity.mean(), 'Top2_Mittel_%': top2.mean(), 'Top2_Median_%': top2.median(), 'Top2_Min_%': top2.min(), 'Top2_Max_%': top2.max(), 'Aktivitaeten': len(a), 'Aktivitaeten_pro_Nutzer_Woche': len(a)/2600, 'Nullwochen': int(w.activity_count.astype(int).eq(0).sum()), 'Nullwochen_%': w.activity_count.astype(int).eq(0).mean()*100, 'Max_Aktivitaeten_pro_Woche': w.activity_count.astype(int).max()})
    sport = a.sport_type.value_counts().reindex(list(SPORTS), fill_value=0).rename('Anzahl').to_frame()
    sport['Anteil_%'] = sport.Anzahl / len(a)*100
    return summary, user, sport


def md(frame):
    f = frame.reset_index()
    def fmt(v):
        return f'{v:.3f}' if isinstance(v,(float,np.floating)) else str(v)
    return '\n'.join(['| '+' | '.join(map(str,f.columns))+' |', '| '+' | '.join(['---']*len(f.columns))+' |'] + ['| '+' | '.join(fmt(v) for v in row)+' |' for row in f.itertuples(index=False,name=None)])


def csv_bytes(frame):
    return frame.to_csv().encode('utf-8')


def figure(name):
    buf = io.BytesIO()
    plt.tight_layout()
    plt.savefig(buf, format='png', dpi=200, facecolor='white')
    plt.close()
    preserve_write(OUT/'figures'/name, buf.getvalue())


def verify_baseline():
    manifest = json.loads((SNAPSHOT/'SHA256.json').read_text())
    for name, digest in manifest.items():
        assert hashlib.sha256((SNAPSHOT/name).read_bytes()).hexdigest() == digest, name
        current = (ROOT/name).read_bytes()
        if name in {'src/data_generation.py', 'src/simulation_quality_analysis.py', 'documentation/simulation_config.md', 'documentation/decisions.md', '.gitignore', 'data/raw/activities_simulated.csv', 'data/raw/users_simulated.csv', 'data/raw/offers_simulated.csv', 'outputs/tables/simulation_weekly_check.csv'}:
            continue  # Autorisierte Aktivierung V2; Snapshot oben stets streng geprüft.
        if name == 'documentation/crisp_dm_log.md':
            assert current.startswith((SNAPSHOT/name).read_bytes()), name
        else:
            assert hashlib.sha256(current).hexdigest() == digest, name
    return len(manifest)


def main():
    protected_count = verify_baseline()
    original_root = original.ROOT
    original.validate()  # V1 erneut technisch prüfen; keine Generierung.
    v1a = original.read_csv('data/raw/activities_simulated.csv')
    v1w = original.read_csv('outputs/tables/simulation_weekly_check.csv')
    outputs = {}
    for label, exponent in [('control_exponent_1_0', 1.0), ('v2_exponent_1_3', 1.3)]:
        users, activities, weekly, assigned = generate(exponent)
        repeat = generate(exponent)
        assert (users, activities, weekly, assigned) == repeat, 'Nicht reproduzierbar'
        destination = OUT/label
        write_csv(destination/'data/raw/users_simulated.csv', users, USER_FIELDS)
        write_csv(destination/'data/raw/activities_simulated.csv', activities, ACTIVITY_FIELDS)
        # Angebote unverändert übernehmen; keine fachliche Anpassung nötig.
        preserve_write(destination/'data/raw/offers_simulated.csv', (ROOT/'data/raw/offers_simulated.csv').read_bytes())
        write_csv(destination/'outputs/tables/simulation_weekly_check.csv', weekly, ['user_id','week_start','activity_count'])
        try:
            original.ROOT = destination
            original.validate()
        finally:
            original.ROOT = original_root
        outputs[label] = (users, activities, weekly, assigned)
    c = outputs['control_exponent_1_0']
    v = outputs['v2_exponent_1_3']
    assert c[0] == v[0] and c[2:] == v[2:], 'Nutzer/Wochen/Trendzuweisungen müssen gepaart sein'
    keys = ['activity_id','user_id','date']
    assert [[row[k] for k in keys] for row in c[1]] == [[row[k] for k in keys] for row in v[1]]
    summary, per_user, sports = {}, {}, {}
    for label,a,w in [('V1_original',v1a,v1w), ('Kontrolle_1.0',c[1],c[2]), ('V2_1.3',v[1],v[2])]:
        summary[label],per_user[label],sports[label]=metrics(a,w)
    results = pd.DataFrame(summary)
    delta = per_user['V2_1.3'] - per_user['Kontrolle_1.0']
    combined_sports = pd.concat(sports,axis=1)
    preserve_write(OUT/'comparison_metrics.csv', csv_bytes(results))
    preserve_write(OUT/'sport_distribution_comparison.csv',csv_bytes(combined_sports))
    preserve_write(OUT/'user_metrics_comparison.csv',csv_bytes(pd.concat(per_user,axis=1)))
    preserve_write(OUT/'paired_user_changes.csv',csv_bytes(delta))
    plt.rcParams.update({'font.size':11, 'axes.spines.top':False, 'axes.spines.right':False})
    fig,axes=plt.subplots(1,2,figsize=(13,5))
    colors=['#747d87','#3893a0','#c15c34']
    for i,label in enumerate(summary):
        axes[0].bar(np.arange(1,9)+(i-1)*.25,[summary[label][f'Nutzer_{k}_Sportarten'] for k in range(1,9)],width=.25,label=label,color=colors[i])
        values=per_user[label].Top2_Prozent.sort_values().to_numpy()
        axes[1].plot(values,np.arange(1,101),label=label,color=colors[i],linewidth=2)
    axes[0].set(xlabel='Unterschiedliche Sportarten je Nutzer',ylabel='Nutzer (Anzahl)',xticks=range(1,9),title='Sportartenvielfalt')
    axes[1].set(xlabel='Anteil der zwei häufigsten Sportarten (%)',ylabel='Nutzer mit höchstens diesem Anteil (%)',title='Verteilung der Top-2-Anteile')
    axes[0].legend(fontsize=9); axes[1].legend(fontsize=9)
    fig.suptitle('MOVA: V1, technische Kontrolle und V2 · je 100 synthetische Nutzer')
    figure('diversity_and_top2_comparison.png')
    fig,axes=plt.subplots(1,2,figsize=(14,6))
    for i,label in enumerate(summary):
        axes[0].bar(np.arange(8)+(i-1)*.25,sports[label]['Anteil_%'],width=.25,label=label,color=colors[i])
        frame = pd.DataFrame(v1w if label=='V1_original' else c[2] if label=='Kontrolle_1.0' else v[2])
        series=frame.assign(activity_count=frame.activity_count.astype(int)).groupby('week_start').activity_count.mean()
        axes[1].plot(range(26),series,label=label,color=colors[i],linestyle='--' if label=='Kontrolle_1.0' else '-',linewidth=2)
    axes[0].set_xticks(range(8),list(SPORTS),rotation=45,ha='right')
    axes[0].set(ylabel='Anteil aller Aktivitäten (%)',title='Sportartenverteilung')
    axes[1].set(xlabel='ISO-Kalenderwoche 2026',ylabel='Aktivitäten je Nutzer und Woche',title='Kontrolle und V2 haben identische Wochenzahlen')
    axes[1].set_xticks(range(0,26,4),[f'KW {k+2:02d}' for k in range(0,26,4)])
    axes[0].legend(fontsize=9);axes[1].legend(fontsize=9)
    fig.suptitle('MOVA: Sportanteile und unveränderte Frequenzlogik')
    figure('sports_and_weekly_comparison.png')
    s1,sc,s2=summary.values()
    report=f'''# MOVA – Kontrollierte Präferenziteration V1 / V2

## Ziel und Baseline

Zielgruppe: aktive Smartwatch-Nutzer mit unterschiedlichen sportlichen Schwerpunkten; breite und konzentrierte Repertoires sollen nebeneinander möglich bleiben. Keine Zielquote für Sportartenvielfalt und keine vorgegebenen Cluster.

Die historische V1 wurde unverändert unter `v1_snapshot/` gesichert, einschließlich Generator, Konfiguration, vorhandenen Qualitätsberichten und Abbildungen. SHA256.json enthält die Prüfsummen von {protected_count} gesicherten Dateien. Ursprüngliche Parameter: 100 Nutzer, 26 Wochen vom 05.01.–05.07.2026, Seed 42, sieben interne Profile, individuelle Gewichte = Profilgewicht × Lognormal(0; 0,7), Exponent implizit 1,0. Grundraten 0,4–2 bzw. 1,3–5, vier Trendmechanismen, Poisson-Zählung, AR(1)-Rauschen, Pausenstart 4,5 %, Wochenobergrenze 10. Vollständige Parameter stehen im gesicherten Generator und simulation_config.md.

## Kontrolliertes Design

Die einzige fachliche Änderung: `weights = [weight ** exponent for weight in weights]` nach der individuellen Gewichterzeugung. Exponent V2 = 1,3. Die gewichtete Auswahl normalisiert implizit durch die Gewichtssumme. Alle Gewichte bleiben positiv; keine Sportart wird ausgeschlossen. Trends und Häufigkeitsparameter bleiben unverändert.

Zusätzliche technische Änderung: getrennte Random-Instanzen. Master-Seed bleibt 42. Abgeleitete Seeds: Häufigkeit/Trend/Pausen 42, Profile 43, Präferenzfaktoren 44, Sportartenwahl 45, Dauer 46, Distanz 47, Interessen 48, Wochentage 49. Profil- und Präferenzzuweisungen bleiben pro Nutzer in Kontrolle und V2 gleich. Dauer und Distanz werden getrennt, weil nur Distanzsportarten entsprechende Ziehungen auslösen. Identische numerische Seeds in separaten ursprünglichen Angebots- und Profilgeneratoren stellen keine fachliche Verbindung her; Angebote werden unverändert kopiert.

**Die historische V1 ist nicht mit dem umgestellten Zufallsstrom identisch.** Deshalb gibt es drei Spalten: V1 original, technische Kontrolle mit Exponent 1,0 und getrennten Zufallsquellen, V2 mit Exponent 1,3 und denselben getrennten Quellen. V1→V2 beschreibt den Gesamtwechsel; nur Kontrolle→V2 isoliert hier den Exponenteneffekt. Der Kontrolllauf ist keine dritte fachliche Anpassungsvariante.

Die Sportartenwahl verwendet bei Kontrolle und V2 dieselben Zufallszahlen; durch geänderte Intervallgrenzen können dennoch einzelne Aktivitäten in beide Richtungen wechseln. Daher sind beobachtete Nutzerkennzahlen nicht zwingend für jeden Nutzer monoton. Zweimalige Generierung jeder Variante im Speicher wurde auf vollständige Gleichheit geprüft. Neue Dateien werden nur angelegt; bei Wiederholung werden ausschließlich identische Inhalte akzeptiert.

## Tatsächlich berechnete Ergebnisse

{md(results)}

Top-2-Anteil: Summe der zwei häufigsten Sportarten eines Nutzers geteilt durch seine gesamte Aktivitätszahl. Mittelwerte gewichten Nutzer gleich. Nullwochen werden im vollständigen 100×26-Raster berücksichtigt. Alle Sportartenanzahlen von 1 bis 8 werden ausgewiesen, damit neu auftretende kleinere Repertoires nicht fehlen.

### Sportartenverteilung

{md(combined_sports)}

Häufigste Sportart V2: {sports['V2_1.3']['Anteil_%'].idxmax()} ({sports['V2_1.3']['Anteil_%'].max():.2f} %); seltenste: {sports['V2_1.3'].Anzahl.idxmin()} ({sports['V2_1.3'].Anzahl.min()} Aktivitäten, {sports['V2_1.3']['Anteil_%'].min():.2f} %). Kein globaler Mehrheitsanteil; alle acht Sportarten bleiben tatsächlich vertreten.

### Nachgewiesener Exponenteneffekt im gepaarten Vergleich

- Nutzer mit acht Sportarten: {sc['Nutzer_8_Sportarten']} → {s2['Nutzer_8_Sportarten']}.
- Mittlere Sportartenanzahl: {sc['Mittlere_Sportartenanzahl']:.3f} → {s2['Mittlere_Sportartenanzahl']:.3f}.
- Mittlerer Top-2-Anteil: {sc['Top2_Mittel_%']:.3f} % → {s2['Top2_Mittel_%']:.3f} %; Differenz {s2['Top2_Mittel_%']-sc['Top2_Mittel_%']:.3f} Prozentpunkte.
- Individueller Top-2-Anteil: {int(delta.Top2_Prozent.gt(1e-10).sum())} höher, {int(delta.Top2_Prozent.lt(-1e-10).sum())} niedriger, {int(delta.Top2_Prozent.abs().le(1e-10).sum())} gleich.
- Individuelle Sportartenanzahl: {int(delta.Sportartenanzahl.gt(0).sum())} höher, {int(delta.Sportartenanzahl.lt(0).sum())} niedriger, {int(delta.Sportartenanzahl.eq(0).sum())} gleich.
- Nutzerinteressen, sämtliche 2.600 Wochenzählungen, Trendzuweisungen sowie IDs/Nutzer/Datum jeder Aktivität sind zwischen Kontrolle und V2 exakt identisch geprüft. Der Exponent verändert hier keine Aktivitätshäufigkeit.

## Plausibilität, Nebenwirkungen und Grenzen

Die sieben Profilvorlagen und individuellen lognormalen Abweichungen bleiben erhalten. Unterschiedliche beobachtete Sportanteile bestehen weiterhin; keine Nutzerprofile werden als Modelllabels gespeichert. Häufigkeiten und Trends sind bewusst unverändert modelliert. Die Verstärkung bildet klarere persönliche Schwerpunkte ab, erhält aber seltene Sportarten und Überschneidungen.

Eine stärkere Konzentration ist eine fachlich motivierte Annahme, kein empirischer Realismusnachweis. Der niedrigere Anteil von Nutzern mit acht Sportarten darf nicht allein als Qualitätsmaß dienen. Seltene Sportarten können Anteile verlieren. Mehr Konzentration kann künstlich klarere Gruppen begünstigen; späteres K-Means darf nicht als Bestätigung der Generatorannahme interpretiert werden. Unverändert positive Gewichte erlauben langfristig weiterhin große Repertoires.

Dauern und Distanzen ändern sich mit dem Sportartenmix trotz unveränderter Parameter; aggregierte Trainingsminuten können daher abweichen. Der technische Wechsel der Zufallsquellen verändert gegenüber historischer V1 zusätzlich Nutzerzuweisungen, Zeitreihen und Gesamtzahlen. Diese Unterschiede werden nicht als Wirkung des Exponenten ausgegeben. Ein Seed und 100 Nutzer zeigen nur diesen konkreten Simulationsfall; keine statistische oder empirische Validierung und keine Garantie für andere Seeds.

## Technische Qualität und Integrität

V1, Kontrolle und V2 bestehen die vorhandenen technischen CSV-Prüfungen: 100 eindeutige Nutzer, 26 Wochen, 2.600 vollständige Nutzerwochen, Abgleich der Aktivitäten, IDs, Referenzen, Datumswerte, acht Sportarten, sportartspezifische Dauer-/Distanzgrenzen, nicht anwendbare Distanzen, Interessen und 30 fiktive Angebote. V1-Snapshot und Originaldateien sind per SHA-256 unverändert geprüft. Nur das CRISP-DM-Protokoll darf um den tatsächlichen Iterationseintrag ergänzt werden; sein ursprünglicher Inhalt bleibt erhalten.

## Empfehlung und weitere Verwendung

**B – V2 übernehmen**, als fachlich bevorzugte Version für die nächste Datenaufbereitung nach Prüfung dieses Vergleichs. Der gepaarte Vergleich zeigt die gewünschte moderate Verstärkung persönlicher Schwerpunkte bei identischen Häufigkeiten und erhaltenen Auswahlmöglichkeiten. Es gibt keinen Nachweis einer besseren ML-Leistung.

V2 bleibt vorerst unter `v2_exponent_1_3/`; die historischen Standarddateien und der ursprüngliche Generator werden nicht ersetzt. Bei der späteren AP-4-Umsetzung muss die verwendete Datenversion ausdrücklich ausgewählt werden. Nullwochen erhalten, nicht anwendbare Distanzen bewusst behandeln, aggregierte Merkmale skalieren und mögliche Redundanzen prüfen. Kein Modell wurde trainiert, kein Commit oder Pull Request erstellt.

## Ausführung und Artefakte

`python src/simulation_preference_comparison.py` aus dem Worktree. Python {sys.version.split()[0]}, pandas {pd.__version__}, NumPy {np.__version__}, Matplotlib {matplotlib.__version__}. Neue CSVs liegen jeweils in den Variantenverzeichnissen. Vergleichsdateien: comparison_metrics.csv, sport_distribution_comparison.csv, user_metrics_comparison.csv, paired_user_changes.csv. Grafiken: figures/diversity_and_top2_comparison.png und figures/sports_and_weekly_comparison.png. Die Top-2-Kurve ist eine kumulierte Verteilung: Sie zeigt den Anteil der Nutzer bis zum jeweiligen Top-2-Wert; eine Verschiebung nach rechts bedeutet stärkere Konzentration.
'''
    preserve_write(OUT/'comparison_report.md',report.encode('utf-8'))
    verify_baseline()
    print(results.to_string())
    print('\nAlle Qualitäts-, Paarungs-, Wiederholungs- und Integritätsprüfungen bestanden.')


if __name__ == '__main__':
    main()
