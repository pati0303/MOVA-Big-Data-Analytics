"""AP 2.4: deskriptive Analyse vorhandener Daten, ohne Generierung oder ML.
Ausführung im Repository: python src/simulation_quality_analysis.py
"""
import hashlib
import importlib.util
from pathlib import Path
import sys
import os

os.environ.setdefault("MPLCONFIGDIR", str(Path(__file__).resolve().parents[1] / "work/__pycache__/matplotlib-cache"))

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
FIG = ROOT / 'outputs/figures'
TABLE = ROOT / 'outputs/tables'
START, END = pd.Timestamp('2026-01-05'), pd.Timestamp('2026-07-05')
WEEKS = pd.date_range(START, periods=26, freq='W-MON')
SPORTS = ['Running', 'Cycling', 'Strength', 'Swimming', 'Walking', 'Hiking', 'Tennis', 'Padel']
NA_SPORTS = ['Strength', 'Tennis', 'Padel']
PROTECTED = ['src/data_generation.py', 'documentation/simulation_config.md', 'data/raw/activities_simulated.csv', 'data/raw/users_simulated.csv', 'data/raw/offers_simulated.csv', 'outputs/tables/simulation_weekly_check.csv', 'outputs/tables/simulation_report.md', '.gitignore']


def sha(name):
    return hashlib.sha256((ROOT / name).read_bytes()).hexdigest()


def table(frame):
    frame = frame.copy().reset_index()
    def cell(value):
        return f'{value:.3f}' if isinstance(value, (float, np.floating)) else str(value)
    return '\n'.join(['| ' + ' | '.join(map(str, frame.columns)) + ' |', '| ' + ' | '.join(['---'] * len(frame.columns)) + ' |'] + ['| ' + ' | '.join(cell(v) for v in row) + ' |' for row in frame.itertuples(index=False, name=None)])


def summary(frame):
    return frame.agg(['min', 'median', 'max', 'mean', 'std']).T.assign(IQR=frame.quantile(.75) - frame.quantile(.25))


def save_plot(name):
    plt.tight_layout()
    plt.savefig(FIG / name, dpi=200, facecolor='white')
    plt.close()


def main():
    before = {name: sha(name) for name in PROTECTED}
    FIG.mkdir(parents=True, exist_ok=True)
    TABLE.mkdir(parents=True, exist_ok=True)
    a = pd.read_csv(ROOT / 'data/raw/activities_simulated.csv', dtype={'activity_id': str, 'user_id': str})
    users = pd.read_csv(ROOT / 'data/raw/users_simulated.csv')
    stored = pd.read_csv(TABLE / 'simulation_weekly_check.csv')
    a['parsed_date'] = pd.to_datetime(a['date'], format='%Y-%m-%d', errors='coerce')
    a['week_start'] = a.parsed_date - pd.to_timedelta(a.parsed_date.dt.dayofweek, unit='D')
    full_index = pd.MultiIndex.from_product([users.user_id, WEEKS], names=['user_id', 'week_start'])
    counts = a.groupby(['user_id', 'week_start']).size().reindex(full_index, fill_value=0)
    minutes = a.groupby(['user_id', 'week_start']).duration_min.sum().reindex(full_index, fill_value=0)
    wide = counts.unstack('week_start')
    zero = wide.eq(0)
    sc = a.sport_type.value_counts().reindex(SPORTS, fill_value=0).rename('Anzahl').to_frame()
    sc['Anteil_%'] = sc.Anzahl / len(a) * 100
    user_sports = pd.crosstab(a.user_id, a.sport_type).reindex(index=users.user_id, columns=SPORTS, fill_value=0)
    shares = user_sports.div(user_sports.sum(axis=1), axis=0) * 100
    metrics = pd.DataFrame({'Aktivitaeten_pro_Woche': wide.mean(axis=1), 'Minuten_pro_Woche': minutes.unstack().mean(axis=1), 'Sportartenanzahl': user_sports.gt(0).sum(axis=1), 'Nullwochen': zero.sum(axis=1), 'Wochen_SD': wide.std(axis=1), 'Ende_minus_Anfang': wide.iloc[:, -6:].mean(axis=1) - wide.iloc[:, :6].mean(axis=1)})
    metrics['dominante_Sportart'] = shares.idxmax(axis=1)
    metrics['groesster_Sportanteil_%'] = shares.max(axis=1)
    # Transparente Heuristik, keine latenten Simulationslabels und kein Modell.
    metrics['deskriptiver_Verlauf'] = np.select([metrics.Ende_minus_Anfang > .5, metrics.Ende_minus_Anfang < -.5, metrics.Wochen_SD > 1.5], ['steigend', 'sinkend', 'schwankend'], default='stabil/geringe_Schwankung')
    choices = []
    for label, series in [('stärkste Zunahme', metrics.Ende_minus_Anfang.sort_values(ascending=False)), ('stärkste Abnahme', metrics.Ende_minus_Anfang.sort_values()), ('stabil, geringe Schwankung', metrics.loc[metrics.deskriptiver_Verlauf.eq('stabil/geringe_Schwankung'), 'Wochen_SD'].sort_values()), ('größte Schwankung', metrics.Wochen_SD.sort_values(ascending=False)), ('meiste Nullwochen', metrics.Nullwochen.sort_values(ascending=False))]:
        uid = next(uid for uid in series.index if uid not in [u for _, u in choices])
        choices.append((label, uid))
    runs = []
    for uid, row in zero.iterrows():
        start = None
        for i, is_zero in enumerate([*row, False]):
            if is_zero and start is None:
                start = i
            elif not is_zero and start is not None:
                runs.append({'user_id': uid, 'week_start': WEEKS[start], 'Laenge_Wochen': i-start, 'am_Rand': start == 0 or i == 26})
                start = None
    pauses = pd.DataFrame(runs)
    overview = pd.DataFrame({'Aktivitaeten': wide.sum(), 'Aktivitaeten_pro_Nutzer': wide.mean(), 'Nullwochen': zero.sum()})
    overview['ISO_KW'] = [f'{d.isocalendar().year}-KW{d.isocalendar().week:02d}' for d in overview.index]
    weekday = a.parsed_date.dt.dayofweek.value_counts().reindex(range(7), fill_value=0)
    weekday.index = ['Mo', 'Di', 'Mi', 'Do', 'Fr', 'Sa', 'So']
    sport_stats = []
    for sport in SPORTS:
        part = a[a.sport_type.eq(sport)]
        duration = part.duration_min
        distance = part.distance_km.dropna()
        limits = {'Running': (10,150), 'Cycling': (15,240), 'Strength': (15,120), 'Swimming': (10,100), 'Walking': (10,180), 'Hiking': (30,360), 'Tennis': (20,180), 'Padel': (20,150)}[sport]
        q1, q3 = duration.quantile([.25, .75])
        outliers = ((duration < q1 - 1.5*(q3-q1)) | (duration > q3 + 1.5*(q3-q1))).sum()
        dq1, dq3 = distance.quantile([.25, .75]) if len(distance) else (np.nan, np.nan)
        distance_outliers = ((distance < dq1 - 1.5*(dq3-dq1)) | (distance > dq3 + 1.5*(dq3-dq1))).sum()
        sport_stats.append({'Sport': sport, 'Dauer_min': duration.min(), 'Dauer_Median': duration.median(), 'Dauer_max': duration.max(), 'Distanz_min_km': distance.min(), 'Distanz_Median_km': distance.median(), 'Distanz_max_km': distance.max(), 'Distanz_fehlt': part.distance_km.isna().sum(), 'Dauer_unterer_Rand': duration.eq(limits[0]).sum(), 'Dauer_oberer_Rand': duration.eq(limits[1]).sum(), 'Dauer_IQR_Ausreisser': outliers, 'Distanz_IQR_Ausreisser': int(distance_outliers) if len(distance) else np.nan})
    sport_stats = pd.DataFrame(sport_stats).set_index('Sport')
    checks = {
        'Fehlende Pflichtwerte': int(a[['activity_id','user_id','date','sport_type','duration_min']].isna().sum().sum()),
        'Ungueltige Datumswerte/Format': int((a.parsed_date.isna() | a.parsed_date.dt.strftime('%Y-%m-%d').ne(a.date)).sum()),
        'Unbekannte Nutzer': int((~a.user_id.isin(users.user_id)).sum()),
        'Doppelte Aktivitaets-IDs': int(a.activity_id.duplicated().sum()),
        'Negative/nicht endliche Dauer': int((~np.isfinite(a.duration_min) | a.duration_min.lt(0)).sum()),
        'Negative/nicht endliche vorhandene Distanz': int((~np.isfinite(a.distance_km.dropna()) | a.distance_km.dropna().lt(0)).sum()),
        'Ausserhalb Zeitraum': int((~a.parsed_date.between(START,END)).sum()),
        'Unbekannte Sportart': int((~a.sport_type.isin(SPORTS)).sum()),
        'Fehlende notwendige Distanz': int((~a.sport_type.isin(NA_SPORTS) & a.distance_km.isna()).sum()),
        'Unerwartete Distanz bei nicht anwendbar': int((a.sport_type.isin(NA_SPORTS) & a.distance_km.notna()).sum()),
    }
    assert not any(checks.values()), checks
    stored['week_start'] = pd.to_datetime(stored.week_start, format='%Y-%m-%d')
    assert len(stored) == 2600 and not stored.duplicated(['user_id','week_start']).any()
    assert stored.set_index(['user_id','week_start']).activity_count.sort_index().equals(counts.sort_index())
    assert users.user_id.nunique() == len(users) == 100 and wide.shape == (100,26)
    # Bestehende technische Grenzwertkontrollen wiederverwenden, ohne main()/Generator.
    spec = importlib.util.spec_from_file_location('simulation', ROOT / 'src/data_generation.py')
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    mod.validate()
    plt.rcParams.update({'font.size': 11, 'axes.spines.top': False, 'axes.spines.right': False})
    plt.figure(figsize=(10,6))
    plt.barh(sc.index[::-1], sc.Anzahl.iloc[::-1], color='#247c91')
    for i, sport in enumerate(sc.index[::-1]):
        plt.text(sc.loc[sport,'Anzahl']+12, i, f'{sc.loc[sport,"Anzahl"]} ({sc.loc[sport,"Anteil_%"]:.1f} %) ', va='center', fontsize=10)
    plt.xlim(0, sc.Anzahl.max()*1.25)
    plt.xlabel('Aufgezeichnete Aktivitäten (Anzahl)')
    plt.title('MOVA: Verteilung der acht Sportarten\nSynthetische Daten · 05.01.–05.07.2026')
    save_plot('sport_distribution.png')
    plt.figure(figsize=(10,6))
    plt.hist(metrics.Aktivitaeten_pro_Woche, bins=np.arange(0, 7, .5), color='#247c91', edgecolor='white')
    plt.axvline(metrics.Aktivitaeten_pro_Woche.median(), color='#bd4c32', linestyle='--', label=f'Median: {metrics.Aktivitaeten_pro_Woche.median():.2f}')
    plt.xlabel('Durchschnittliche Aktivitäten pro Nutzer und Woche (inklusive Nullwochen)')
    plt.ylabel('Nutzer (Anzahl)')
    plt.title('MOVA: Unterschiede in der Aktivitätshäufigkeit\n100 synthetische Nutzer · je 26 Wochen')
    plt.legend()
    save_plot('activity_frequency_distribution.png')
    plt.figure(figsize=(12,7))
    for label, uid in choices:
        plt.plot(range(26), wide.loc[uid], marker='o', markersize=3, linewidth=1.4, label=f'{uid}: {label}')
    plt.xticks(range(0,26,2), [f'KW {w.isocalendar().week:02d}' for w in WEEKS[::2]])
    plt.ylabel('Aktivitäten pro Woche (Anzahl)')
    plt.xlabel('Kalenderwoche 2026 (Montag bis Sonntag)')
    plt.title('MOVA: Fünf beobachtete Aktivitätsverläufe\nAuswahl anhand der Zeitreihen, ohne interne Simulationslabels')
    plt.legend(loc='upper center', bbox_to_anchor=(.5,-.15), ncol=2, fontsize=10)
    plt.grid(axis='y', alpha=.2)
    save_plot('user_activity_trends.png')
    fig, axes = plt.subplots(2,1,figsize=(12,8),sharex=True)
    axes[0].plot(range(26),overview.Aktivitaeten_pro_Nutzer,marker='o',color='#247c91')
    axes[0].set_ylabel('Aktivitäten pro Nutzer/Woche')
    axes[0].set_title('MOVA: Wochenübersicht über alle 100 Nutzer\nSynthetische Daten · Nullwochen eingeschlossen')
    axes[1].bar(range(26),overview.Nullwochen,color='#bd4c32')
    axes[1].set_ylabel('Nutzer ohne Aktivität (Anzahl)')
    axes[1].set_xlabel('Kalenderwoche 2026')
    axes[1].set_xticks(range(0,26,2), [f'KW {w.isocalendar().week:02d}' for w in WEEKS[::2]])
    save_plot('weekly_activity_overview.png')
    metrics.to_csv(TABLE / 'simulation_user_quality_metrics.csv', index_label='user_id')
    shares.to_csv(TABLE / 'simulation_user_sport_shares.csv', index_label='user_id')
    overview.to_csv(TABLE / 'simulation_weekly_quality_metrics.csv', index_label='week_start')
    pauses.to_csv(TABLE / 'simulation_zero_runs.csv',index=False)
    lag = np.corrcoef(wide.iloc[:,:-1].to_numpy().ravel(),wide.iloc[:,1:].to_numpy().ravel())[0,1]
    centered = wide.sub(wide.mean(axis=1),axis=0)
    within_lag = np.corrcoef(centered.iloc[:,:-1].to_numpy().ravel(),centered.iloc[:,1:].to_numpy().ravel())[0,1]
    total_zero = int(zero.to_numpy().sum())
    boundary_days = ((a.parsed_date.dt.dayofweek >= 5).sum() / len(a))*100
    selection = metrics.loc[[u for _,u in choices], ['Aktivitaeten_pro_Woche','Wochen_SD','Ende_minus_Anfang','Nullwochen']].copy()
    selection['Auswahlgrund'] = [label for label,_ in choices]
    run_distribution = pauses.Laenge_Wochen.value_counts().sort_index().rename('Pausenanzahl').to_frame()
    zero_distribution = metrics.Nullwochen.value_counts().sort_index().rename('Nutzeranzahl').to_frame()
    report = f'''# MOVA – Fachliche Qualitätsprüfung AP 2.4

## 1. Ziel und Datenbasis

Untersucht werden fachliche Plausibilität und Eignung für spätere Arbeitspakete (CRISP-DM 2.2 Describe Data, 2.3 Explore Data, 2.4 Verify Data Quality). Es wurden keine Daten neu generiert, keine Parameter geändert, keine Cluster erzeugt und keine Modelle trainiert.

Vorhandene Daten: {len(users)} Nutzer, {len(a):,} Aktivitäten, 26 vollständige Wochen vom 05.01. bis 05.07.2026 (ISO-KW 02–27), 2.600 Nutzerwochen und 30 fiktive Angebote. Schwerpunkt dieser Prüfung sind Aktivitäten und Nutzerwochen. Die bestehende technische Prüfung umfasst auch Nutzerinteressen und Angebote. Interessen werden nicht als Clustering- oder Regressionsmerkmale ausgewertet.

## 2. Methoden und Reproduzierbarkeit

Aufruf: `python src/simulation_quality_analysis.py`. Python {sys.version.split()[0]}, pandas {pd.__version__}, NumPy {np.__version__}, Matplotlib {matplotlib.__version__}. Die Analyse verwendet keine Zufallsziehung. Alle ursprünglichen sieben Dateien sowie .gitignore werden vor und nach der Analyse über SHA-256 auf unveränderte Inhalte geprüft.

Das Nutzer-Wochen-Raster wird aus allen 100 Nutzer-IDs und 26 Montagen unabhängig rekonstruiert. Fehlende Aktivitäten werden dort als 0 berücksichtigt und mit der vorhandenen Kontrolltabelle verglichen. Nutzer-Mittelwerte werden stets durch 26 geteilt. Sportartenanteile verwenden die Gesamtzahl der Aktivitäten des jeweiligen Nutzers als Nenner.

Der Median ist der mittlere sortierte Wert. Standardabweichung (SD, Stichprobenformel mit n−1) beschreibt Streuung um den Mittelwert; IQR ist der Abstand zwischen dem 25. und 75. Perzentil und weniger empfindlich gegenüber Extremwerten. Ein IQR-Ausreißer liegt außerhalb Q1−1,5×IQR bis Q3+1,5×IQR und ist zunächst ein Prüfhinweis, kein Datenfehler.

Zeitliche Entwicklung wird durch den Mittelwert der letzten sechs minus der ersten sechs Wochen beschrieben. Über +0,5 Aktivitäten/Woche heißt deskriptiv steigend, unter −0,5 sinkend. Sonst gilt SD > 1,5 als schwankend, der Rest als stabil/geringe Schwankung. Diese heuristischen Schwellen sind nicht empirisch validiert, Kategorien sind priorisiert und werden ausschließlich als deskriptive Prüfkennzahlen gespeichert, nicht als Clusterlabels oder Modellmerkmale. Steigende Nutzer können stark schwanken. Anfangs-/Endvergleich kann zwischenzeitliche Wellen übersehen. Interne Generatorlabels werden nicht herangezogen.

## 3. Sportartenverteilung

{table(sc)}

Häufigste Sportart: {sc.Anzahl.idxmax()} ({sc['Anteil_%'].max():.2f} %); seltenste: {sc.Anzahl.idxmin()} ({sc['Anteil_%'].min():.2f} %). Verhältnis häufigste/seltenste: {sc.Anzahl.max()/sc.Anzahl.min():.2f}:1. Alle acht Sportarten sind ausreichend oft für deskriptive Vergleiche vertreten; keine dominiert die Gesamtaktivitäten mit einer Mehrheit. Die Gleichmäßigkeit ist eine Eigenschaft der Konstruktionsannahmen, kein Nachweis einer realen Population.

Grafik: `outputs/figures/sport_distribution.png`.

## 4. Unterschiede zwischen Nutzern

{table(summary(metrics[['Aktivitaeten_pro_Woche','Minuten_pro_Woche','Sportartenanzahl','Nullwochen','groesster_Sportanteil_%']]))}

Verteilung der Zahl unterschiedlicher Sportarten:

{table(metrics.Sportartenanzahl.value_counts().sort_index().rename('Nutzeranzahl').to_frame())}

Sportartenanteile innerhalb eines Nutzers, über alle Nutzer zusammengefasst (Prozent, mit Nullanteilen):

{table(summary(shares))}

Die Häufigkeit und Trainingsminuten unterscheiden sich deutlich. Breite Sportmischungen und überlappende Vorlieben verhindern jedoch die Annahme sauber getrennter Gruppen. K-Means kann später auf geeigneten aggregierten Merkmalen demonstriert werden; die Existenz sinnvoller Cluster ist damit nicht belegt. Skalierung ist nötig, weil Minuten größere Zahlenbereiche haben als Häufigkeiten oder Anteile. Anteilsmerkmale summieren sich zu 100 % und sind abhängig; Häufigkeit und Minuten können dieselbe Aktivität mehrfach gewichten. Anzahl Sportarten kann nahe acht wenig Trennkraft liefern. Feature-Auswahl, Skalierung, Clusterstabilität und fachliche Interpretation bleiben offen.

Grafik: `outputs/figures/activity_frequency_distribution.png`.

## 5. Zeitliche Entwicklungen

{table(overview)}

Wochenmittel über alle Nutzer: Minimum {overview.Aktivitaeten_pro_Nutzer.min():.2f}, Maximum {overview.Aktivitaeten_pro_Nutzer.max():.2f} Aktivitäten/Nutzer. Aggregation glättet gegenläufige individuelle Entwicklungen.

Deskriptive Verlaufskategorien gemäß der oben erklärten Heuristik:

{table(metrics.deskriptiver_Verlauf.value_counts().rename('Nutzeranzahl').to_frame())}

Fünf anhand tatsächlicher Zeitreihen ausgewählte Nutzer; je Kriterium wird der extremste noch nicht ausgewählte Nutzer gewählt:

{table(selection)}

Exakte Wochenzahlen dieser Nutzer von KW 02 bis KW 27:

''' + '\n'.join(f'- {uid} ({label}): ' + ', '.join(map(str, wide.loc[uid].tolist())) for label,uid in choices) + f'''

Wochentage (jeder Wochentag ist im Zeitraum genau 26-mal vorhanden):

{table(weekday.rename('Aktivitaeten').to_frame().assign(Anteil_Prozent=weekday/len(a)*100))}

Wochenendanteil: {boundary_days:.2f} %, gegenüber 28,57 % bei gleichmäßiger Tagesverteilung. Das passt zu den höheren Wochenendgewichten im Generator. Es ist kein gemessener realer Verhaltenseffekt.

Für eine spätere Folgewoche-Prognose sind Schwankungen, Nullen und unterschiedliche Niveaus vorhanden. Die deskriptive Pearson-Korrelation benachbarter Wochen beträgt gepoolt {lag:.3f}, nach Abzug des jeweiligen Nutzermittels {within_lag:.3f}. Eine Korrelation beschreibt gemeinsamen Verlauf, keine Prognosegüte. Die Zentrierung nutzt hier rein deskriptiv alle 26 Wochen und darf so nicht in spätere Trainings-/Testmerkmale übernommen werden. Der Unterschied beider Korrelationen zeigt den Einfluss verschiedener Grundniveaus.

Maximal 100×25 = 2.500 benachbarte Nutzer-Wochen-Paare stehen vor zusätzlichen Rückblickfenstern zur Verfügung; diese sind innerhalb von Nutzern abhängig. 26 Wochen pro Nutzer sind kurz. Lineare Regression ist als Demonstration grundsätzlich möglich, aber Zähldaten, Nullwochen und nichtlineare Schwankungen verletzen möglicherweise einfache lineare Annahmen. Zeitlich trennen, Merkmale ausschließlich aus vorher bekannten Wochen bilden und später mit einfachen Vorhersagen (Vorwoche bzw. bisheriges Mittel) vergleichen. Negative Prognosen und Residuen kritisch prüfen. Es wird keine erreichbare Güte behauptet.

Grafiken: `outputs/figures/user_activity_trends.png`, `outputs/figures/weekly_activity_overview.png`.

## 6. Nullwochen und Aktivitätspausen

{total_zero} von 2.600 Nutzerwochen ({total_zero/2600*100:.2f} %) sind null. {int(zero.any(axis=1).sum())} Nutzer haben mindestens eine Nullwoche. Verteilung je Nutzer:

{table(zero_distribution)}

Eine beobachtete Pause ist jede maximal zusammenhängende Folge von Nullwochen, unabhängig von ihrer Ursache. Die Daten erlauben keine Unterscheidung zwischen intern erzeugter Pause und zufällig null gezogenen Aktivitäten. Verteilung der {len(pauses)} beobachteten Folgen:

{table(run_distribution)}

Längste beobachtete Nullfolge: {pauses.Laenge_Wochen.max()} Wochen; Median {pauses.Laenge_Wochen.median():.1f}. {int(pauses.am_Rand.sum())} Folgen berühren den Beobachtungsrand und können außerhalb des Zeitraums länger sein. Folgen können länger als die im Generator vorgesehenen Einzelpausen sein, weil zufällige Nullwochen und weitere Pausen anschließen können.

Wöchentliche Nullnutzerzahl: {overview.Nullwochen.min()}–{overview.Nullwochen.max()}; Maximum in {', '.join(overview.loc[overview.Nullwochen.eq(overview.Nullwochen.max()),'ISO_KW'])}. Die vollständige zeitliche Verteilung steht in Abschnitt 5. Daraus allein lässt sich kein Kalender- oder Saisonproblem ableiten.

21 % Nullwochen sind für eine bewusst heterogene Demonstrationspopulation einschließlich Gelegenheitsaktiven vertretbar. Für ausschließlich regelmäßig trainierende Nutzer wäre dieser Anteil kritisch. Ohne empirischen Vergleich ist er nicht validiert. Entscheidend sind individuelle Konzentration und Pausenlängen, nicht nur der Gesamtanteil. Die Nullwochen dürfen später nicht aus der Regressionstabelle entfernt werden.

## 7. Sportartspezifische Plausibilität

Dauern in Minuten, Distanzen in Kilometern. `nan` bedeutet in der folgenden Tabelle nicht anwendbar, wenn die gesamte Sportart keine Distanzen besitzt.

{table(sport_stats)}

Bei Strength, Tennis und Padel sind insgesamt {int(a.sport_type.isin(NA_SPORTS).sum())} leere Distanzfelder fachlich beabsichtigt. Bei den fünf Distanzsportarten fehlt keine Distanz. Nicht anwendbare Werte werden weder als gemessene 0 interpretiert noch pauschal imputiert. Spätere Aggregationen müssen zwischen Sportart ohne Distanz und Nutzerwoche ohne Aktivität unterscheiden.

Die sportartspezifischen Dauer- und Geschwindigkeitsgrenzen des vorhandenen Generators wurden erneut technisch geprüft und eingehalten (einschließlich Rundungstoleranz bei Distanzen). IQR-Ausreißer sind bei rechtsschiefen Trainingsdauern erwartbar und hier kein bestätigter Fehler. Lange Ausdauereinheiten und hohe Geschwindigkeiten benötigen dennoch fachliche Einordnung. Grenzwerte sind Simulationsannahmen, keine universellen menschlichen Leistungsgrenzen. Die exakten Randhäufigkeiten sind oben ausgewiesen; Häufungen können durch Abschneiden entstehen. Wochen mit genau zehn Aktivitäten: {int(wide.eq(10).to_numpy().sum())} ({wide.eq(10).to_numpy().mean()*100:.2f} %). Der Einfluss dieser Obergrenze sollte im späteren Modellvergleich beachtet werden.

## 8. Erneute technische Datenqualität

{table(pd.Series(checks, name='Fehleranzahl').to_frame())}

BESTANDEN: 100 eindeutige Nutzer; vollständiges und eindeutiges 100×26-Raster; jede Wochenzählung stimmt mit unabhängig gezählten Einzelaktivitäten überein. Vorhandene Generatorprüfung `validate()` ebenfalls bestanden; der Generator selbst wurde nicht ausgeführt. Keine bestätigten technischen Fehler. Fachliche Modellannahmen werden dadurch nicht empirisch bestätigt.

## 9. Gesamtbewertung und nächste Schritte

**B – Grundsätzlich geeignet, aber Verbesserungen sinnvoll.** Die Daten sind technisch konsistent, enthalten Nutzerunterschiede, überlappende Sportarten und unregelmäßige Zeitreihen. Sie eignen sich für eine didaktische Pipeline. Reale Clusterstruktur, reale Prognoseleistung oder Übertragbarkeit lassen sich daraus nicht ableiten.

1. Vor einer möglichen zweiten Simulation Zielpopulation und gewünschte Häufigkeits-/Pausenbereiche fachlich festlegen. Insbesondere Nullwochenkonzentrationen und lange Nullfolgen prüfen; nicht allein auf 21 % optimieren.
2. Den hohen Sportartenmix und die Trennkraft der Sportartenanzahl prüfen. Falls fachlich nötig, später begründete und weiterhin überlappende Vorlieben anpassen; in diesem Arbeitsschritt wurde nichts verändert.
3. Randhäufungen, lange Einheiten und die Wochenobergrenze anhand der Tabellen besprechen. Alternative Verteilungen nur bei fachlichem Bedarf in einem dokumentierten Folgeschritt testen.
4. Für spätere Modelle Nullwochen erhalten, Anteile und fehlende Distanzen bewusst behandeln, Features skalieren und redundante Merkmale vermeiden. Zeitbasierte Evaluation und einfache Vergleichsvorhersagen planen.
5. Saison und Messfehler sind bislang nicht enthalten. Vor ihrer Ergänzung prüfen, ob sie dem Hochschulziel dienen; keinen empirischen Realismus behaupten.

Tatsächlich abgeschlossen ist diese deskriptive Qualitätsprüfung. Noch kein Rücksprung mit geänderten Simulationsannahmen durchgeführt; eine solche Iteration würde erst nach beschlossener Änderung und erneutem Vergleich dokumentiert. Keine vollständige Data Preparation für AP 4 und keine Modellierung erfolgt.

## 10. Artefakte und Integrität

Zusätzlich zum Bericht und den vier PNG-Grafiken entstehen `simulation_user_quality_metrics.csv`, `simulation_user_sport_shares.csv`, `simulation_weekly_quality_metrics.csv` und `simulation_zero_runs.csv` unter outputs/tables. Dies sind beschreibende Auswertungen, keine neuen simulierten Beobachtungen oder Modellmerkmale für AP 4.

SHA-256 der unveränderten Quelldateien:

''' + '\n'.join(f'- `{name}`: `{value}`' for name,value in before.items()) + '\n'
    assert before == {name: sha(name) for name in PROTECTED}, 'Quelldateien verändert'
    (TABLE / 'simulation_quality_report.md').write_text(report, encoding='utf-8')
    print(report)


if __name__ == '__main__':
    main()
