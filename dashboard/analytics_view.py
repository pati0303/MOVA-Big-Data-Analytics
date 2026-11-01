"""Seven interactive research pages, with aggregated and permission-gated paths."""
from html import escape
import math
import pandas as pd
import plotly.graph_objects as go
import streamlit as st
from dashboard.analytics_data import ResearchData, PermissionRequired, K_VALUES, RAW, WEEKS, FEATURES, SCALED
from dashboard.data_access import DataAccessError
from dashboard.design import plotly_layout, COLORS
from dashboard.user_view import number
from dashboard.state import capabilities


def chart(fig, key, height=300):
    fig.update_layout(**plotly_layout(),height=height,legend=dict(orientation='h',y=1.18,x=0))
    st.plotly_chart(fig,width='stretch',key=key,config={'displayModeBar':False})


def metrics(items):
    for col,(label,value) in zip(st.columns(len(items)),items):
        with col:st.metric(label,value)


def takeaway(text):
    st.success('Erkenntnis · '+text)


def sources(*paths):
    with st.expander('Quellen und Berechnung'):
        for path in paths:st.code(path,language=None)
        st.caption('Geprüfter gespeicherter V2-Projektbestand. Keine Trainings- oder Exportskripte werden gestartet.')


def personal_gate(state, offers=False):
    if not capabilities(state)['activity']:
        st.info('Individuelle Analyse gesperrt: Aktiviere die simulierte Garmin-Freigabe für den ausgewählten Nutzer. Aggregierte Ergebnisse bleiben verfügbar.')
        return False
    if offers and not capabilities(state)['offers']:
        st.info('Individuelle Angebote gesperrt: Zusätzlich ist die simulierte Interessenfreigabe erforderlich.')
        return False
    return True


def understanding(d,state):
    st.caption('Fragestellung · Wie unterscheiden sich Sportarten und Datenmerkmale in den synthetischen Beobachtungen?')
    initial=d.understanding()
    sports=st.selectbox('Sportart',['Alle Sportarten',*initial['sports']],key='lab_sport')
    data=d.understanding(None if sports=='Alle Sportarten' else sports)
    metrics([('Nutzer',str(data['users'])),('Wochen','26'),('Aktivitäten',number(data['activities'])),('Sportarten',str(len(data['sports']))),('Nutzerwochen',number(data['weekly_rows']))])
    st.markdown(f"**Auswahl: {number(data['selected_count'])} Aktivitäten · {number(data['share']*100,2)} % aller 6.465 Aktivitäten.**")
    fig=go.Figure(go.Bar(x=data['series']['Wochenbeginn'],y=data['series']['Aktivitäten'],marker_color=COLORS['accent'],
                        hovertemplate='Wochenbeginn %{x|%d.%m.%Y}<br>%{y} Aktivitäten<extra></extra>'))
    fig.update_xaxes(title='Wochenbeginn',tickformat='%d.%m.');fig.update_yaxes(title='Aktivitäten aller Nutzer',rangemode='tozero')
    chart(fig,'understanding_series')
    field=st.selectbox('Datenmerkmal',['duration_min','distance_km','sport_type','date'],key='lab_field')
    meanings={'duration_min':'Dauer einer Aktivität in Minuten; sportabhängig.',
              'distance_km':'Sportabhängige Distanz; bei Krafttraining, Tennis und Padel strukturell nicht anwendbar.',
              'sport_type':'Kategorialer Name der tatsächlich ausgeübten Sportart.',
              'date':'Beobachtetes Datum; für Zeitzuordnung in Montag–Sonntag-Wochen genutzt.'}
    values=data['selected'][field]
    st.write(meanings[field])
    st.caption(f'pandas-Datentyp: {values.dtype} · CSV-Speichertyp: Text · Fehlend in Auswahl: {values.isna().sum()} / {len(values)}')
    if field in ('duration_min','distance_km'):
        valid=values.dropna()
        if len(valid):
            metrics([('Gültige Werte',number(len(valid))),('Mittelwert',number(valid.mean(),2)),('Median',number(valid.median(),2))])
            fig=go.Figure(go.Histogram(x=valid,nbinsx=24,marker_color=COLORS['blue']))
            fig.update_xaxes(title=field);fig.update_yaxes(title='Aktivitäten');chart(fig,'understanding_field')
        else:st.info('In dieser Auswahl sind keine anwendbaren Werte vorhanden. Es werden keine Nullen eingesetzt.')
    elif field=='sport_type':
        counts=values.value_counts().rename_axis('Sportart').reset_index(name='Aktivitäten')
        st.dataframe(counts,hide_index=True,width='stretch')
    else:
        st.write('Zeitraum der Auswahl:',values.min().strftime('%d.%m.%Y') if len(values) else 'leer','bis',values.max().strftime('%d.%m.%Y') if len(values) else 'leer')
    takeaway('Der Sportfilter ändert die betrachtete Teilmenge. Fehlende strukturelle Distanzen sind keine 0-km-Aktivitäten; beobachtetes Verhalten ist keine Präferenz.')
    sources(RAW,'documentation/data_dictionary.md')


PIPELINE=['Rohaktivitäten','Auswahl / Prüfung','Wochenaggregation','K-Means-Features','K-Means-Skalierung','Regressionsfeatures','Modellinputs / Split']


def preparation(d,state):
    experiment=st.segmented_control('Experiment',['Pipeline','Nullwochen','Skalierung','Zeitlicher Split'],default='Nullwochen',required=True,key='prep_experiment',label_visibility='collapsed')
    if experiment=='Pipeline':
        st.caption('Fragestellung · Wie werden aus einzelnen Aktivitäten zwei verschiedene Modellinputs?')
        step=st.select_slider('Verarbeitungsschritt',options=PIPELINE,value=PIPELINE[0],key='pipeline_step')
        item=d.pipeline(step)
        metrics([('Eingabe',f"{number(item['input_shape'][0])} × {item['input_shape'][1]}"),('Ausgabe',f"{number(item['output_shape'][0])} × {item['output_shape'][1]}")])
        st.write('**Transformation:** '+item['why'])
        st.code(item['input']+'\n↓\n'+item['output'],language=None)
        st.dataframe(item['schema'],hide_index=True,width='stretch')
        st.info('Zwei getrennte Pfade: Aktivitäten → Nutzerfeatures → gewichtete K-Means-Matrix; Wochenraster → Regressionsfenster → chronologischer Split. Regression verwendet keine K-Means-Skalierung.')
        takeaway('Die Zeileneinheit wechselt von Aktivität zu Nutzerwoche, Nutzerprofil oder Prognosebeispiel. Validierung bedeutet hier keine erfundene Löschung von Ausreißern.')
    elif experiment=='Nullwochen':
        st.caption('Fragestellung · Was passiert mit der Häufigkeit, wenn Wochen ohne Aktivität fehlen?')
        variant=st.radio('Wochenbasis',['Mit Nullwochen','Ohne Nullwochen'],horizontal=True,key='zero_variant',label_visibility='collapsed')
        include=variant=='Mit Nullwochen';r=d.zero_weeks(include)
        metrics([('Nutzerwochen',number(r['n'])),('Nullwochen in Auswahl',number(r['zero_n'])),('Aktivitäten / Woche',number(r['mean'],4)),('Auslassungseffekt',number(r['relative_pct'],2)+' %')])
        fig=go.Figure(go.Bar(x=r['distribution'].activities_count,y=r['distribution'].Nutzerwochen,
                            marker_color=COLORS['accent'] if include else COLORS['orange'],hovertemplate='%{x} Aktivitäten<br>%{y} Nutzerwochen<extra></extra>'))
        fig.update_xaxes(title='Aktivitäten pro Nutzerwoche',dtick=1);fig.update_yaxes(title='Anzahl Nutzerwochen');chart(fig,'zero_hist')
        denominator=r['n'];numerator=r['total']
        st.latex(r'\bar{x}=\frac{'+str(numerator)+'}{'+str(denominator)+r'}='+f"{r['mean']:.6f}")
        st.write('Mit vollständigem Raster: **'+number(r['all_mean'],4)+'**. Nur aktive Wochen: **'+number(r['active_mean'],4)+'**. '
                 'Relative Differenz: (ohne / mit − 1) × 100 = **'+number(r['relative_pct'],2)+' %**.')
        takeaway('Alle 2.600 Wochen beschreiben den gesamten Beobachtungszeitraum.' if include else 'Ohne 558 Nullwochen bleibt die Aktivitätssumme gleich, der Nenner sinkt auf 2.042. Der höhere Wert beschreibt nur aktive Wochen.')
        st.warning('Das ist Auslassungsverzerrung bei Verwendung als Gesamthäufigkeit, kein Nachweis verbesserter Modellgüte. Ohne Nullwochen werden Nutzer zudem unterschiedlich gewichtet.')
    elif experiment=='Skalierung':
        st.caption('Fragestellung · Wie entsteht aus einem beobachteten Nutzerfeature der tatsächliche Modellwert?')
        if personal_gate(state):
            params=d.metadata('outputs/models/kmeans_scaling_params.json')
            feature=st.selectbox('Modellfeature',params['feature_order'],key='scale_feature')
            step=st.slider('Rechenschritt',1,4,3,key='scale_step')
            r=d.scaling(state['selected_user_id'],feature,garmin_permission=True)
            st.caption(f"Tatsächliches Beispiel: {state['selected_user_id']} · Schritt {step}/4")
            if step==1:
                st.dataframe(r['raw_activities'],hide_index=True,width='stretch')
                st.write(f"{len(r['raw_activities'])} beobachtete Aktivitäten → Häufigkeit / 26; Sportanteile / Gesamtaktivitäten.")
            elif step==2:
                st.dataframe(r['features'],hide_index=True,width='stretch')
                st.caption('avg_duration_per_week und sport_diversity sind Interpretationsmerkmale, keine Modelleingänge.')
            elif step==3:
                values={'Ursprünglicher Wert x':r['x'],'Gespeicherter Mittelwert μ':r['mean'],'Gespeicherte Skala σ':r['scale'],
                        'Standardisiert z = (x − μ) / σ':r['z'],'Gewicht w':r['weight'],'Modellwert z × w':r['weighted']}
                st.dataframe(pd.DataFrame({'Zwischenwert':list(values),'Wert':list(values.values())}),hide_index=True,width='stretch')
                st.latex(r'z_j=(x_j-\mu_j)/\mathrm{scale}_j,\quad x^{Modell}_j=z_j\cdot w_j')
            else:
                row=r['scaled'].iloc[0]
                fig=go.Figure(go.Bar(x=row.index,y=row.values,marker_color=COLORS['accent']))
                fig.update_yaxes(title='Standardisierter, gewichteter Modellwert');chart(fig,'scaled_features')
                st.dataframe(r['scaled'],hide_index=True,width='stretch')
            takeaway('Standardisierung verwendet gespeicherte Populationsparameter (ddof=0). Häufigkeit hat Gewicht 1, jede der acht Sportkoordinaten 1/√8. Kein Refit.')
        else:
            p=d.metadata('outputs/models/kmeans_scaling_params.json')
            st.dataframe(pd.DataFrame([{'Feature':f,'Mittelwert':v['mean'],'scale_':v['scale'],'Gewicht':v['weight']} for f,v in p['features'].items()]),hide_index=True,width='stretch')
        st.caption('Gleiche Blockvarianzsummen sind eine transparente Startannahme, keine empirisch optimierte Gewichtung. Acht Sportanteile enthalten nur sieben unabhängige Freiheitsgrade.')
    else:
        split_view(d,state)
    sources(WEEKS,FEATURES,SCALED,'outputs/models/kmeans_scaling_params.json','documentation/regression_split_manifest.json')


def split_view(d,state):
    st.caption('Fragestellung · Welche Daten sind beim Prognosezeitpunkt bereits bekannt?')
    r=d.split();m=r['manifest']
    metrics([('Beispiele',number(r['all_rows'])),('Training',number(r['train_rows'])),('Test',number(r['test_rows']))])
    week=st.slider('Eingabewoche t',4,25,22,key='split_week')
    phase='Training' if week<=21 else 'Test'
    fig=go.Figure()
    for label,weeks,color,y in [('Trainingsziele',list(range(5,23)),COLORS['accent'],2),('Testziele',list(range(23,27)),COLORS['orange'],2),
                                 ('Bekannte Historie',list(range(week-3,week+1)),COLORS['blue'],1),('Ziel t+1',[week+1],COLORS['orange'],0)]:
        fig.add_trace(go.Scatter(x=weeks,y=[y]*len(weeks),mode='markers',name=label,marker=dict(color=color,size=14),hovertemplate=label+' · Projektwoche %{x}<extra></extra>'))
    fig.update_yaxes(tickvals=[0,1,2],ticktext=['Ziel des Beispiels','Vier historische Wochen','Chronologischer Split']);fig.update_xaxes(title='Relative Projektwoche (keine ISO-Kalenderwoche)',dtick=2,range=[.5,27])
    chart(fig,'split_timeline')
    st.write(f'**{phase}:** Eingaben aus Wochen {week-3}–{week}; vorhergesagte Folgewoche {week+1}. '
             'Die Zielaktivität ist kein Eingangsfeature. Wochen 1–3 besitzen noch keine Vierwochenhistorie; Woche 26 hat kein beobachtetes Folgeziel.')
    st.caption('Trainingsziele: '+ ' bis '.join(m['train_target_date_range'])+' · Testziele: '+' bis '.join(m['test_target_date_range']))
    if personal_gate(state):
        frame=d.table('data/processed/regression_weekly_features.csv')
        row=frame[(frame.user_id==state['selected_user_id'])&(frame.week_index==week)]
        st.dataframe(row.drop(columns='user_id'),hide_index=True,width='stretch')
    takeaway('Der Split folgt den Zielzeiträumen. Frühere abgeschlossene Testwochen dürfen spätere Eingänge bilden; das Modell bleibt unverändert. Keine gleichzeitige Vierwochenprognose.')


def kmeans(d,state):
    st.caption('Fragestellung · Welche gespeicherten Ergebnisse sprechen für zwei Segmente?')
    controls=st.columns([1.2,1])
    with controls[0]:
        k=st.selectbox('Gespeicherte Clusterzahl k',K_VALUES,key='cluster_k')
    with controls[1]:
        measure=st.radio('Vergleichsmetrik',['Silhouette','Inertia'],horizontal=True,key='k_measure')
    r=d.kmeans(k);selected=r['selected'];stable=r['stability']
    metrics([('Silhouette · Seed 42',number(selected.silhouette_score,6)),('Inertia · Seed 42',number(selected.inertia,4)),('ARI · 20 Seeds',number(stable.ari_pairwise_mean,4))])
    col='silhouette_score' if measure=='Silhouette' else 'inertia'
    fig=go.Figure(go.Bar(x=r['scores'].k.astype(str),y=r['scores'][col],marker_color=[COLORS['accent'] if value==k else COLORS['blue'] for value in r['scores'].k],hovertemplate='k=%{x}<br>%{y:.6f}<extra></extra>'))
    fig.update_xaxes(title='Gespeicherte Clusterzahl');fig.update_yaxes(title=measure);chart(fig,'k_scores')
    st.caption(f"20-Seed-Mittel: Silhouette {number(stable.silhouette_mean,6)} · Inertia {number(stable.inertia_mean,4)}. Einzellauf und Seedmittel sind unterschiedliche Kennzahlen. Keine neue Anpassung beim Wechsel.")
    st.caption(f"k={k} erreicht Silhouette {number(selected.silhouette_score,4)}; der gespeicherte k=2-Lauf erreicht {number(float(r['scores'].loc[r['scores'].k==2,'silhouette_score'].iloc[0]),4)}. Höhere Werte bedeuten hier bessere Trennung. Sinkende Inertia allein begründet kein größeres k.")
    if k in (6,8):st.info('Für diese Clusterzahl fehlen gespeicherte Profile und Nutzerzuordnungen. Angezeigt werden ausschließlich vorhandene Evaluation und Stabilität.')
    elif k==3:
        with st.expander('Vorläufige Kandidatenprofile k=3 · Seed 42'):
            p=d.table('outputs/tables/kmeans_candidate_profiles.csv');st.dataframe(p[p.k==3].drop(columns=['seed','k']),hide_index=True,width='stretch')
    with st.expander('Neun Modelleingänge und ihre Gewichtung'):
        params=d.metadata('outputs/models/kmeans_scaling_params.json')
        st.dataframe(pd.DataFrame([{'Feature':f,'Gewicht nach Standardisierung':params['features'][f]['weight']} for f in params['feature_order']]),hide_index=True,width='stretch')
        st.caption('StandardScaler mit ddof=0; danach Häufigkeit ×1, acht Sportkoordinaten je ×1/√8. Keine erneute Gewichtungsoptimierung.')
    st.markdown('### Finale Segmente · k = 2')
    profiles=r['profiles'];metrics([('Geringere Häufigkeit',str(int(profiles.iloc[0].n_users))+' Nutzer'),('Höhere Häufigkeit',str(int(profiles.iloc[1].n_users))+' Nutzer'),('Finale Silhouette',number(r['metadata']['silhouette_score'],6))])
    feature=st.selectbox('Profilmerkmal',['avg_activities_per_week',*[f for f in profiles.columns if f.startswith('share_')],'avg_duration_per_week','sport_diversity'],key='cluster_feature')
    is_input=feature not in ('avg_duration_per_week','sport_diversity')
    st.caption('Modelleingang (hier unskaliert dargestellt)' if is_input else 'Nur Interpretation · nicht im Clustering verwendet')
    fig=go.Figure(go.Bar(x=profiles.segment_label,y=profiles[feature],marker_color=[COLORS['accent'],COLORS['blue']],hovertemplate='%{x}<br>%{y:.6f}<extra></extra>'))
    fig.update_yaxes(title=feature);chart(fig,'cluster_profiles')
    if personal_gate(state):
        user=d.cluster_for_user(state['selected_user_id'],garmin_permission=True)
        st.write(f"Gespeicherter Kontext {state['selected_user_id']}: **{user['segment_label']}**, Cluster-ID {user['cluster_id']}.")
    takeaway('Die Trennung ist moderat (Silhouette ≈ 0,303). Sie beschreibt relative Trainingshäufigkeit, keine Fitness oder Gesundheit. Neun gewichtete Eingänge; kein Wirkungs- oder Generalisierungsnachweis.')
    sources('outputs/tables/kmeans_k_selection.csv','outputs/tables/kmeans_candidate_comparison.csv','outputs/tables/kmeans_final_cluster_profiles.csv','outputs/models/kmeans_final_metadata.json')


def regression(d,state):
    m=d.regression_metadata();f=m['feature_order'];coef=m['coefficients']
    st.caption('Fragestellung · Wie entsteht eine gespeicherte Einwochenprognose und wo liegt ihr Fehler?')
    st.code(f"ŷ(t+1) = {m['intercept']!r} + {coef[f[0]]!r} × Aktivitäten(t) + {coef[f[1]]!r} × Mittel(t−3…t)",language=None)
    st.caption('Ziel: Aktivitätszahl der Folgewoche. Zwei Eingangsfeatures, keine Skalierung. Koeffizienten beschreiben partielle Änderungen bei konstantem anderem Eingang, keine kausalen Wirkungen. Die aktuelle Woche ist im Vierwochenmittel enthalten.')
    week=st.selectbox('Test-Zielwoche',[23,24,25,26],key='reg_week')
    aggregate=d.evaluation(week)
    with st.expander('Projektüberblick · 100 Testfälle der ausgewählten Zielwoche',expanded=not capabilities(state)['activity']):
        vals=aggregate['by_week'].iloc[0]
        fig=go.Figure(go.Bar(x=['Ist · Mittel','Regression · Mittel','Baseline · Mittel'],y=[vals.actual_activities_next_week,vals.regression_prediction,vals.baseline_prediction],marker_color=[COLORS['blue'],COLORS['accent'],COLORS['orange']]))
        fig.update_yaxes(title='Aktivitäten pro Nutzer · Mittelwert');chart(fig,'reg_aggregate',240)
        st.caption('Aggregierte Mittelwerte verdecken individuelle Fehler; MAE misst die mittleren absoluten Einzelfehler.')
    st.markdown('### Tatsächlicher Testfall · '+state['selected_user_id'])
    if personal_gate(state):
        case=d.regression_case(state['selected_user_id'],week-1,garmin_permission=True);p=case['prediction'];b=case['baseline']
        step=st.slider('Berechnungsschritt',1,4,3,key='reg_step')
        metrics([('Istwert',number(b['actual_activities_next_week'])),('Regression',number(b['regression_prediction'],4)),('Baseline',number(b['baseline_prediction'],4))])
        metrics([('Absoluter Fehler · Regression',number(b['regression_absolute_error'],4)),('Absoluter Fehler · Baseline',number(b['baseline_absolute_error'],4))])
        if step==1:
            st.dataframe(case['history'],hide_index=True,width='stretch')
            st.write('Die vier vollständig abgeschlossenen Wochen bilden t−3…t; die Zielwoche ist nicht enthalten.')
        elif step==2:
            metrics([('Aktivitäten(t)',number(p[f[0]],0)),('Vierwochenmittel',number(p[f[1]],4))])
            st.write(f"Eingabewoche {week-1} endet {p['week_end']}; erst danach wird Zielwoche {week} vorhergesagt.")
        elif step==3:
            st.dataframe(pd.DataFrame({'Term':['Intercept',f[0],f[1]],'Koeffizient':[m['intercept'],coef[f[0]],coef[f[1]]],
                                      'Eingang':[1,p[f[0]],p[f[1]]],'Beitrag':case['contributions']}),hide_index=True,width='stretch')
            st.write('Summe der Beiträge:',sum(case['contributions']),'· gespeicherte Prognose:',p['predicted_activities_next_week'])
        else:
            st.caption('Fehler = Prognose − Ist; absoluter Fehler = Betrag. Keine Prognosen nachträglich runden oder kappen.')
        fig=go.Figure()
        cases=case['user_cases']
        for column,label,color in [('actual_activities_next_week','Ist',COLORS['blue']),('regression_prediction','Regression',COLORS['accent']),('baseline_prediction','Baseline',COLORS['orange'])]:
            fig.add_trace(go.Scatter(x=cases.week_index+1,y=cases[column],name=label,mode='lines+markers',line=dict(color=color)))
        fig.add_vline(x=week,line_dash='dot');fig.update_xaxes(title='Test-Zielwoche',dtick=1);fig.update_yaxes(title='Aktivitäten');chart(fig,'reg_personal')
        takeaway('Persistence übernimmt die aktuelle Aktivitätszahl unverändert. Die Regression glättet über zwei Eingänge, kann aber im einzelnen Fall deutlich abweichen.')
    st.warning('Historische Testziele: 08.06.–05.07.2026. Die User-View-Demo für 06.–12.07.2026 ist eine andere, unbeobachtete Zielwoche und wird hier nicht evaluiert.')
    sources('outputs/tables/regression_test_predictions.csv','outputs/tables/regression_baseline_comparison.csv','outputs/models/regression_linear_metadata.json')


def evaluation(d,state):
    st.caption('Fragestellung · Ist der Gesamtvorteil der Regression in jeder Zielgruppe vorhanden?')
    week=st.selectbox('Evaluationszeitraum',['Alle Testwochen',23,24,25,26],key='eval_week')
    group=st.radio('Diagnosegruppe',['Alle Testfälle','Zielwoche = 0','Zielwoche > 0'],horizontal=True,key='eval_group')
    r=d.evaluation(None if week=='Alle Testwochen' else week,group)
    metrics([('Testfälle',number(r['n'])),('MAE · Regression',number(r['regression_mae'],6)),('MAE · Baseline',number(r['baseline_mae'],6)),('Relative Verbesserung',number(r['improvement_pct'],2)+' %' if r['improvement_pct'] is not None else 'nicht definiert')])
    metric=st.segmented_control('Fehlermaß',['MAE','RMSE'],default='MAE',required=True,key='eval_metric')
    field=metric.lower()
    fig=go.Figure(go.Bar(x=['Regression','Persistence-Baseline'],y=[r['regression_'+field],r['baseline_'+field]],marker_color=[COLORS['accent'],COLORS['orange']]))
    fig.update_yaxes(title=metric+' · Aktivitäten je Nutzerwoche',rangemode='tozero');chart(fig,'eval_compare')
    st.write('MAE = Mittel der absoluten Einzelfehler. RMSE = Wurzel des mittleren quadrierten Fehlers; große Fehler wirken stärker. '
             'Relative Verbesserung = (MAE Baseline − MAE Regression) / MAE Baseline × 100.')
    st.dataframe(r['by_week'].rename(columns={'actual_activities_next_week':'Ist-Mittel','regression_prediction':'Prognose-Mittel','baseline_prediction':'Baseline-Mittel','regression_absolute_error':'MAE Regression','baseline_absolute_error':'MAE Baseline'}),hide_index=True,width='stretch')
    if group=='Zielwoche = 0':
        takeaway('Bei später beobachteten Nullzielwochen ist die Regression in dieser Evaluation schlechter als die Baseline. Die positive Grundprognose führt hier zu Überschätzung.')
    else:takeaway('Der Gesamtvorteil bedeutet weder einen Vorteil für jeden Nutzer noch für jede Teilgruppe. Filter ersetzen nicht die Gesamtmetrik.')
    st.warning('Post-hoc-Diagnose: Ob die zukünftige Zielwoche null Aktivitäten hat, ist am Prognosezeitpunkt unbekannt. Diese Gruppeninformation darf keine nachträgliche Modellauswahl steuern — das wäre Data Leakage.')
    with st.expander('Methodische Grenzen',expanded=True):
        st.write('Synthetische Daten, wiederholte bekannte Nutzer und überlappende Historien; begrenzte Übertragbarkeit auf echte Garmin-Nutzer. Moderate Clustertrennung und individuelle Prognosefehler. Keine Kausal-, Gesundheits- oder Umsatzwirkung belegt.')
    sources('outputs/tables/regression_baseline_comparison.csv','outputs/tables/regression_baseline_metrics.json','outputs/tables/regression_test_metrics.json')


def recommendations(d,state):
    st.caption('Fragestellung · Wie verändern bestätigte Sporttags die Top-5-Zusammensetzung?')
    r=d.recommendation_totals()
    with st.expander('Gesamtergebnis · Empfehlungsslots und Rangstufen',expanded=not (capabilities(state)['activity'] and capabilities(state)['offers'])):
        metrics([('Untersuchte Nutzer',str(r['users'])),('Unveränderte Listen',str(r['change_groups']['unchanged'])),('Andere Zusammensetzung',str(r['change_groups']['composition_changed'])),('A-Slots nachher',str(r['tier_a_after']))])
        fig=go.Figure()
        fig.add_trace(go.Bar(x=['Ohne Tags','Mit acht Tags'],y=[0,r['tier_a_after']],name='Stufe A',marker_color=COLORS['accent']))
        fig.add_trace(go.Bar(x=['Ohne Tags','Mit acht Tags'],y=[r['slots_before'],r['tier_b_after']],name='Stufe B',marker_color=COLORS['blue']))
        fig.update_layout(barmode='stack');fig.update_yaxes(title='Empfehlungsslots · keine Nutzerzahl');chart(fig,'recommendation_totals',260)
        st.write(f"Je Variante **{r['slots_before']} Slots**. Nachher **{r['tier_a_after']}/{r['slots_after']} = {number(r['tier_a_after_pct'],2)} %** Stufe A. "
                 f"**{r['users_with_tier_a']} Nutzer** haben mindestens ein A-Angebot. **{r['change_groups']['reordered_only']} reine Umordnungen** wurden beobachtet.")
    st.markdown('### Individueller Vergleich · '+state['selected_user_id'])
    if personal_gate(state,offers=True):
        c=d.recommendation_case(state['selected_user_id'],garmin_permission=True,interests_permission=True)
        before={o['offer_id']:o for o in c['before']};after={o['offer_id']:o for o in c['after']}
        for col,items,label in zip(st.columns(2),[c['before'],c['after']],['Ohne bestätigte Tags','Mit acht bestätigten Tags']):
            with col:
                st.markdown('#### '+label)
                if not items:st.info('Keine positiven Kategorien: keine personalisierten Angebote.')
                rows=[]
                for offer in items:
                    oid=offer['offer_id']
                    if oid in before and oid in after:
                        change='Behalten · gleiche Position' if before[oid]['ranking_position']==after[oid]['ranking_position'] else 'Behalten · Position geändert'
                        if before[oid]['ranking_tier']!=after[oid]['ranking_tier']:change+=' · Stufe B→A'
                    else:change='Neu in Top 5' if oid in after else 'Verlässt Top 5'
                    rows.append(f'<div class="mova-compare-row"><span class="mova-compare-rank">{offer["ranking_position"]}</span>'
                                f'<div><div class="mova-compare-title">{escape(offer["offer_title"])}</div>'
                                f'<div class="mova-compare-detail">{escape(oid)} · {escape(change)}</div></div>'
                                f'<span class="mova-compare-tier">{escape(offer["ranking_tier"])}</span></div>')
                if rows:st.markdown('<div class="mova-compare-list">'+''.join(rows)+'</div>',unsafe_allow_html=True)
                with st.expander('Begründungen · '+label):
                    for offer in items:
                        st.write(offer['offer_id']+' · '+offer['match_reason'])
        st.caption('Kontrollierter historischer Versuch am 05.07.2026: beide simulierten Freigaben aktiv, identische Kategorien und Sportanteile. Nur die Tagmenge unterscheidet sich. Engine-Replay im Speicher gegen gespeicherte IDs geprüft; keine Modellinferenz und keine Änderung der Tagdatei.')
    takeaway('64 veränderte Zusammensetzungen zeigen Regelwirkung, keine nachgewiesene höhere Empfehlungsqualität. 81 Nutzer mit A-Angebot sind nicht 81 veränderte Listen.')
    sources('outputs/tables/recommendation_before_after_users.csv','outputs/tables/recommendation_before_after_summary.json','src/recommendation_engine.py')


PHASES={
 'Business Understanding':('Geschäftsfrage und Demo-Scope','Synthetischer Personal-Advisor-Demonstrator für Sport, Outdoor, Wellness und Freizeit. Keine realen Umsatz- oder Eignungsnachweise.',['README.md','documentation/decisions.md']),
 'Data Understanding':('Daten verstehen und Qualität prüfen','Sportverteilungen, Nutzerwochen und ungewöhnlich breite Sportrepertoires untersucht; Anlass zur dokumentierten Iteration identifiziert.',['documentation/data_dictionary.md','outputs/tables/simulation_quality_report.md']),
 'Data Preparation':('Beobachtungen in prüfbare Features überführen','V2 angenommen, Rohfelder ausgewählt, Nullwochenraster, neun K-Means-Eingänge und zeitliche Regressionsfenster erzeugt und auditiert.',['documentation/data_preparation_execution.md','outputs/tables/data_preparation_audit_report.md']),
 'Modeling':('K-Means und lineare Regression entwickeln','k-Varianten und Stabilität untersucht, k=2 finalisiert, globale lineare Regression mit zwei Eingängen auf Trainingszeitraum angepasst. Hier ausschließlich gespeicherte Ergebnisse.',['documentation/kmeans_modeling_execution.md','documentation/regression_modeling_execution.md']),
 'Evaluation':('Modelle und Regeln kritisch bewerten','400 chronologische Testfälle gegen Persistence-Baseline; Nullzielwochen kritisch untersucht; AP 6 evaluiert ausschließlich Regelwirkung.',['documentation/modeling_evaluation.md','documentation/recommendation_execution.md']),
 'Deployment':('Lokale Demonstration bereitstellen','User View und Analytics Lab lokal in Streamlit integriert. Kein produktiver Garmin-Dienst und keine Veröffentlichung der App; Gesamtabnahme AP 7.5a durchgeführt; GitHub-Sicherung AP 7.5b noch ausstehend.',['documentation/dashboard_execution.md','app.py'])}


def crisp(d,state):
    st.caption('Fragestellung · Welche Entscheidungen, Nachweise und Rücksprünge prägen den Projektverlauf?')
    phase=st.selectbox('CRISP-DM-Phase',list(PHASES),key='crisp_phase')
    fig=go.Figure(go.Scatter(x=[0]*6,y=list(range(6)),mode='lines+markers+text',
                            text=[f'{i+1} · {p}' for i,p in enumerate(PHASES)],textposition='middle right',
                            marker=dict(size=16,color=[COLORS['accent'] if p==phase else COLORS['blue'] for p in PHASES]),
                            line=dict(color='#30483B'),hovertext=list(PHASES),hoverinfo='text'))
    fig.update_xaxes(visible=False,range=[-.12,1]);fig.update_yaxes(visible=False,range=[5.5,-.5]);chart(fig,'crisp_phases',280)
    goal,text,paths=PHASES[phase];st.markdown('### '+goal);st.write(text)
    for path in paths:st.code(path,language=None)
    st.markdown('### Tatsächliche Iteration · MOVA-ITER-001')
    st.write('Data Understanding → Construct Data → erneute Qualitätsprüfung: Die breite Sportartenvielfalt war auffällig. Der Präferenzexponent wurde von 1,0 auf 1,3 erhöht, um individuelle Schwerpunkte zu verstärken. Das ist eine fachliche Änderung, keine bloße Fehlerkorrektur.')
    metric=st.selectbox('Iterationskennzahl',['Top2_Mittel_%','Mittlere_Sportartenanzahl','Nutzer_8_Sportarten','Aktivitaeten','Nullwochen'],key='iteration_metric')
    df=d.iteration(metric)
    fig=go.Figure(go.Bar(x=df.Variante,y=df.Wert,marker_color=[COLORS['blue'],COLORS['orange'],COLORS['accent']]))
    fig.update_yaxes(title=metric);chart(fig,'iteration_compare')
    st.dataframe(df,hide_index=True,width='stretch')
    takeaway('Der gepaarte Kontrolle→V2-Vergleich isoliert den Exponenteneffekt: Top-2-Anteil +6,507 Prozentpunkte, acht Sportarten 58→40. Häufigkeitsunterschiede V1→V2 stammen auch aus umgestellten Zufallsströmen und sind kein belegter Exponenteneffekt.')
    st.info('Technische Git-Probleme, Bugfixes und wiederholte Prüfungen sind keine fachlichen CRISP-DM-Iterationen. Eine verbesserte Simulation ist noch kein Nachweis besserer ML-Modelle oder realer Datenqualität.')
    sources('documentation/crisp_dm_log.md','outputs/simulation_comparison/comparison_metrics.csv','outputs/simulation_comparison/comparison_report.md')


PAGES={'Data Understanding':understanding,'Data Preparation':preparation,'K-Means':kmeans,'Regression':regression,
       'Evaluation':evaluation,'Empfehlungssystem':recommendations,'CRISP-DM':crisp}


def analytics_view(state):
    section=state['lab_section']
    st.markdown(f'<div class="mova-welcome"><div><div class="mova-kicker">MOVA ANALYTICS LAB</div>'
                f'<h1>{escape(section)}</h1></div><p>Geprüfte V2-Ergebnisse · kein Neutraining<br>Aggregierte Forschung und freigegebene Einzelfälle</p></div>',unsafe_allow_html=True)
    try:
        PAGES[section](ResearchData(),state)
    except DataAccessError as exc:
        st.error(str(exc))
        st.caption('Keine Ersatzdaten und kein Ergebnis aus einer vorherigen Auswahl. Bitte den unveränderten lokalen Projektbestand prüfen.')
