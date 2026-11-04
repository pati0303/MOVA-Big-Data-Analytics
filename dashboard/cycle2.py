"""Read-only cycle-2 presentation using saved, hash-verified aggregate artifacts."""
from io import BytesIO
import hashlib
import json
from pathlib import Path
import numpy as np
import pandas as pd
import plotly.graph_objects as go
import streamlit as st
from dashboard.data_access import DataAccessError, PROJECT_ROOT
from dashboard.design import COLORS

TITLE = 'CRISP-DM – Zweiter Modellierungszyklus'
LABELS = {'persistence':'Persistence', 'linear_2':'Regression · 2 Merkmale', 'linear_3':'Regression · 3 Merkmale'}


def load_cycle2(root=PROJECT_ROOT):
    """No experiment imports, model loading, fitting, exports or legacy test access."""
    try:
        root=Path(root)
        manifest=json.loads((root/'outputs/cycle2/run_manifest.json').read_text())
        def verified(name):
            path='outputs/cycle2/'+name
            payload=(root/path).read_bytes()
            if hashlib.sha256(payload).hexdigest()!=manifest['artifact_sha256'][path]:
                raise ValueError('Prüfsumme abweichend: '+name)
            return payload
        result={key:pd.read_csv(BytesIO(verified(name)),float_precision='round_trip') for key,name in
                [('summary','comparison.csv'),('fold_metrics','metrics_by_fold.csv'),('groups','zero_week_analysis.csv')]}
        result['decision']=json.loads(verified('decision.json'))
        result['validation']=json.loads(verified('validation_manifest.json'))
        s=result['summary'];f=result['fold_metrics'];g=result['groups']
        for frame in [s,f,g]:
            if not {'model','n','mae','rmse','mean_signed_error'}.issubset(frame.columns):raise ValueError('Schema')
            if set(frame.model)!=set(LABELS) or frame.isna().any().any():raise ValueError('Verfahren oder Fehlwerte')
            if not np.isfinite(frame[['n','mae','rmse','mean_signed_error']].to_numpy(dtype=float)).all():raise ValueError('Nicht endliche Werte')
            if (frame[['mae','rmse']]<0).any().any():raise ValueError('Negative Fehlermaße')
        if len(s)!=3 or not (s.n==1200).all():raise ValueError('Vergleichsumfang')
        if len(f)!=9 or f.duplicated(['fold','model']).any() or set(f.fold)!={1,2,3} or not (f.n==400).all():raise ValueError('Foldumfang')
        expected=[([4,9],[10,13]),([4,13],[14,17]),([4,17],[18,21])]
        folds=result['validation']['folds']
        if len(folds)!=3 or [(x['train_input_weeks'],x['validation_input_weeks']) for x in folds]!=expected:raise ValueError('Foldzeiten')
        if result['validation']['legacy_test_used'] is not False:raise ValueError('Testgrenze')
        for model in LABELS:
            subset=f[f.model==model];row=s[s.model==model].iloc[0]
            if not np.isclose(subset.mae.mean(),row.mae,atol=1e-12):raise ValueError('MAE-Aggregation')
            if not np.isclose(np.sqrt((subset.rmse**2).mean()),row.rmse,atol=1e-12):raise ValueError('RMSE-Aggregation')
            targets=g[(g.model==model)&(g.grouping=='actual_target')]
            historical=g[(g.model==model)&(g.grouping=='zero_weeks_last_4_weeks')]
            if set(targets.group)!={'actual_zero','actual_positive'} or targets.n.sum()!=1200:raise ValueError('Zielgruppen')
            if set(historical.group)!={'0','1','2','3','4'} or historical.n.sum()!=1200:raise ValueError('Historische Gruppen')
        mae=s.set_index('model').mae
        fm=f.pivot(index='fold',columns='model',values='mae')
        wins=int((fm.linear_3<fm.linear_2).sum())
        adopted=bool(mae.linear_3<mae.linear_2 and wins>=2)
        d=result['decision']
        if d['adopt_extended']!=adopted or d['winning_folds']!=wins or d['selected_structure']!=('linear_3' if adopted else 'linear_2'):raise ValueError('Entscheidung widersprüchlich')
        return result
    except (OSError,ValueError,KeyError,TypeError,AttributeError) as exc:
        raise DataAccessError('Zyklus-2-Ergebnisse fehlen oder sind inkonsistent. Gespeicherten Ergebnisbestand prüfen.') from exc


def render_cycle2(d,state):
    from dashboard.analytics_view import chart,metrics,sources
    r=load_cycle2(d.root)
    s=r['summary'].set_index('model');folds=r['fold_metrics'];groups=r['groups']
    st.caption('ZYKLUS 1 → ZYKLUS 2 · GESPEICHERTE VALIDIERUNGSERGEBNISSE · KEIN NEUTRAINING')
    st.info('Zyklus 1: Schwächen bei zukünftigen Nullwochen → Hypothese: Historische Nullwochen könnten zusätzliche Prognoseinformation liefern.')
    st.markdown('**Erkenntnis → neue Hypothese → neues Merkmal → erneute Modellierung → Evaluation → Entscheidung**')
    st.markdown('### Feature Engineering · vier abgeschlossene Wochen')
    left,right=st.columns(2)
    with left:
        st.markdown('**Bisherige Merkmale**\n\n- Aktivitäten der aktuellen Woche\n- Durchschnittliche Aktivitäten der letzten vier Wochen')
    with right:
        st.markdown('**Zusätzlich untersucht**\n\n- Anzahl der Nullwochen in den letzten vier Wochen\n- Fenster: **t−3 bis t**, Werte **0 bis 4**')
    st.caption('Anschauliches Rechenbeispiel, keine Messreihe: [0, 0, 4, 4] und [1, 1, 2, 4] haben beide aktuell 4 Aktivitäten und Mittelwert 2 – aber 2 bzw. 0 Nullwochen.')
    st.markdown('### Modellvergleich · gepoolter MAE')
    metrics([(LABELS[m],number(s.loc[m,'mae'])) for m in LABELS])
    fig=go.Figure(go.Bar(x=[LABELS[m] for m in LABELS],y=[s.loc[m,'mae'] for m in LABELS],
        marker_color=[COLORS['orange'],COLORS['accent'],COLORS['blue']],
        text=[number(s.loc[m,'mae']) for m in LABELS],textposition='outside',cliponaxis=False,
        hovertemplate='%{x}<br>MAE %{y:.6f}<extra></extra>'))
    fig.update_yaxes(title='MAE · Aktivitäten pro Nutzerwoche',range=[0,float(s.mae.max())*1.23]);chart(fig,'cycle2_pooled',340)
    st.caption('1.200 identische Validierungsfälle je Verfahren · kleiner ist besser · Prognosen ohne Rundung oder Begrenzung')
    st.markdown('### Chronologische Validierung · Vergangenheit vor Zukunft')
    fig=go.Figure()
    for label,field,color in [('Training','train_input_weeks',COLORS['accent']),('Validierung','validation_input_weeks',COLORS['blue'])]:
        for i,fold in enumerate(r['validation']['folds']):
            a,b=fold[field]
            fig.add_trace(go.Bar(y=[f"Fold {fold['fold']}"],x=[b-a+1],base=[a-.5],orientation='h',name=label,
                legendgroup=label,showlegend=i==0,marker_color=color,text=[f'{label} t={a}–{b}'],textposition='inside',
                hovertemplate=f'{label}: Eingabewochen {a}–{b}<extra></extra>'))
    fig.update_layout(barmode='overlay');fig.update_xaxes(title='Relative Projektwoche · Ziel jeweils t+1',dtick=1,range=[3,22]);chart(fig,'cycle2_timeline',260)
    fig=go.Figure()
    for model,color in [('linear_2',COLORS['accent']),('linear_3',COLORS['blue'])]:
        subset=folds[folds.model==model].sort_values('fold')
        fig.add_trace(go.Bar(x=['Fold '+str(v) for v in subset.fold],y=subset.mae,name=LABELS[model],marker_color=color,
            text=[number(v) for v in subset.mae],textposition='outside',cliponaxis=False))
    fig.update_layout(barmode='group');fig.update_yaxes(title='MAE · Aktivitäten pro Nutzerwoche',range=[0,float(folds.mae.max())*1.2]);chart(fig,'cycle2_folds',330)
    st.caption('Beide Regressionen je Fold neu geschätzt; innerhalb des Validierungsblocks unverändert. Nur bereits abgeschlossene Wochen fließen in die Prognose ein.')
    st.info('Die ursprünglichen 400 Testfälle bleiben von Entwicklung und Modellentscheidung ausgeschlossen. Die Hypothese entstand nach Zyklus 1: Diese interne Validierung ist keine unabhängige Testbestätigung.')
    st.markdown('### Evaluation · zukünftige Nullwochen')
    targets=groups[(groups.grouping=='actual_target')&(groups.group=='actual_zero')].set_index('model')
    metrics([('Tatsächliche Nullziele',str(int(targets.loc['linear_2','n']))),('MAE · 2 Merkmale',number(targets.loc['linear_2','mae'])),('MAE · 3 Merkmale',number(targets.loc['linear_3','mae']))])
    st.warning('Keine Verbesserung bei zukünftigen Nullwochen. Ob eine Zielwoche null Aktivitäten enthält, ist bei der Prognose unbekannt – diese Gruppe dient nur der nachträglichen Diagnose.')
    with st.expander('Alle Kennzahlen und historische Nullwochen'):
        display=r['summary'].copy();display['model']=display.model.map(LABELS)
        st.dataframe(display.rename(columns={'model':'Verfahren','n':'Fälle','mae':'MAE','rmse':'RMSE','mean_signed_error':'Mittlerer Fehler','negative_predictions':'Negative Prognosen'}),hide_index=True,width='stretch')
        display=groups.copy();display['model']=display.model.map(LABELS)
        st.dataframe(display.rename(columns={'model':'Verfahren','grouping':'Gruppierung','group':'Gruppe','n':'Fälle','mae':'MAE','rmse':'RMSE'}),hide_index=True,width='stretch')
    st.markdown('### Zusätzliches Merkmal verworfen.' if not r['decision']['adopt_extended'] else '### Zusätzliches Merkmal übernommen.')
    delta=float(s.loc['linear_3','mae']-s.loc['linear_2','mae'])
    if not r['decision']['adopt_extended']:
        st.success(f'Entscheidung: Das ursprüngliche Modell bleibt bestehen. Gepoolter MAE der Erweiterung: {delta:+.6f} gegenüber dem bisherigen Ansatz.')
    st.markdown(f"- Niedrigerer gepoolter MAE: **{'erfüllt' if delta<0 else 'nicht erfüllt'}**\n- Niedrigerer MAE in mindestens zwei Folds: **{r['decision']['winning_folds']} von 3**\n- Übernahme verlangt **beide** Bedingungen.")
    st.markdown('### Sechs CRISP-DM-Phasen · zweiter Zyklus')
    phases=[('Business Understanding','Nullwochen-Schwäche → Hypothese und Erfolgskriterium festgelegt.'),
        ('Data Understanding','Historische Nullwochen und vollständiges Wochenraster geprüft.'),
        ('Data Preparation','Nullwochen in t−3 bis t gezählt; Zeitzuordnung und Leakage geprüft.'),
        ('Modeling','Zwei Regressionen in drei Zeitfolds geschätzt; Persistenz verglichen.'),
        ('Evaluation','1.200 Fälle bewertet; vorab festgelegte Übernahmeregel nicht erfüllt.'),
        ('Deployment','Forschungsstand dokumentiert; bisheriges Modell erhalten; Ergebnisse hier sichtbar.')]
    for row in (phases[:3],phases[3:]):
        for col,(phase,text) in zip(st.columns(3),row):
            with col:
                with st.container(border=True):st.markdown('**'+phase+'**');st.write(text)
    st.caption('Grenzen: synthetische Daten, bekannte Nutzer, abhängige Wochenfenster. Kein Nachweis realer Übertragbarkeit und kein Signifikanznachweis.')
    sources('outputs/cycle2/comparison.csv','outputs/cycle2/metrics_by_fold.csv','outputs/cycle2/zero_week_analysis.csv','outputs/cycle2/decision.json','documentation/cycle2/report.md')


def number(value):
    return f'{float(value):.6f}'.replace('.',',')
