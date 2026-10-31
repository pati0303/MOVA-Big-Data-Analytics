"""AP 4.7: unabhängiges Audit echter V2-Dateien und vier Forschungsabbildungen.

Aufruf: python src/data_preparation_audit.py
Importiert keine Transformationsskripte und verwendet keine früheren Prüfberichte.
"""
import hashlib
import json
import math
import os
import platform
import sys
from datetime import date, timedelta
from decimal import Decimal
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
os.environ.setdefault('MPLCONFIGDIR', str(ROOT/'work/matplotlib'))
os.environ.setdefault('XDG_CACHE_HOME', str(ROOT/'work/cache'))
Path(os.environ['XDG_CACHE_HOME']).mkdir(parents=True,exist_ok=True)
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch
import numpy as np
import pandas as pd

SPORTS = ['Running','Cycling','Strength','Swimming','Walking','Hiking','Tennis','Padel']
FEATURES = ['avg_activities_per_week'] + ['share_'+s.lower() for s in SPORTS]
USER_COLUMNS = ['user_id']+FEATURES+['avg_duration_per_week','sport_diversity']
WEEK_COLUMNS = ['user_id','week_index','week_start','week_end','activities_count','total_duration_min']
REG_COLUMNS = ['user_id','week_index','week_start','week_end','activities_current_week',
               'avg_activities_last_4_weeks','activities_next_week']
ACT_COLUMNS = ['activity_id','user_id','date','sport_type','duration_min']
CSV_PATHS = {
    'raw':'data/raw/activities_simulated.csv','users':'data/raw/users_simulated.csv',
    'selected':'data/processed/activities_selected.csv',
    'weekly':'data/processed/user_weekly_activities.csv',
    'kmeans':'data/processed/kmeans_user_features.csv',
    'scaled':'data/processed/kmeans_user_features_scaled.csv',
    'regression':'data/processed/regression_weekly_features.csv',
    'train':'data/processed/regression_train.csv','test':'data/processed/regression_test.csv',
    'control':'outputs/tables/simulation_weekly_check.csv',
}
JSON_PATHS = {'active':'documentation/active_data_version.json',
              'params':'outputs/models/kmeans_scaling_params.json',
              'split':'documentation/regression_split_manifest.json'}
TOL = 1e-10
START = date(2026,1,5)


class AuditError(ValueError):
    pass


def need(condition, message):
    if not condition:
        raise AuditError(message)


def close(actual, expected, message):
    need(np.allclose(np.asarray(actual,dtype=float),np.asarray(expected,dtype=float),
                     atol=TOL,rtol=TOL),message)


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load_data(root=ROOT):
    data = {name:pd.read_csv(root/path,dtype=str,keep_default_na=False) for name,path in CSV_PATHS.items()}
    metadata = {name:json.loads((root/path).read_text(encoding='utf-8')) for name,path in JSON_PATHS.items()}
    return data,metadata


def sorted_frame(frame, keys):
    return frame.sort_values(keys).reset_index(drop=True)


def same_frame(actual, expected, keys, message):
    need(sorted_frame(actual,keys).equals(sorted_frame(expected,keys)),message)


def decimal_sum(values):
    return sum((Decimal(v) for v in values),Decimal(0))


def audit_content(d, meta):
    """Inhaltsaudit; Tests können isolierte Speicherkopien übergeben."""
    checks = []
    def passed(label, detail):
        checks.append((label,detail))
    active = meta['active']
    need(active['active_version']=='V2' and (active['users'],active['weeks'],active['activities'],
         active['zero_user_weeks'])==(100,26,6465,558),'V2-Datenvertrag abweichend')
    counts = {'raw':6465,'users':100,'selected':6465,'weekly':2600,'kmeans':100,
              'scaled':100,'regression':2200,'train':1800,'test':400,'control':2600}
    schemas = {'raw':ACT_COLUMNS+['distance_km'],
               'users':['user_id','interest_sport','interest_outdoor','interest_wellness','interest_leisure'],
               'selected':ACT_COLUMNS,'weekly':WEEK_COLUMNS,'kmeans':USER_COLUMNS,
               'scaled':['user_id']+FEATURES,'regression':REG_COLUMNS,'train':REG_COLUMNS,
               'test':REG_COLUMNS,'control':['user_id','week_start','activity_count']}
    for name,expected in counts.items():
        need(len(d[name])==expected,f'{name}: falsche Zeilenanzahl {len(d[name])}, erwartet {expected}')
        need(list(d[name])==schemas[name],f'{name}: unzulässiges/fehlendes Merkmal oder falsche Spaltenfolge')
    users = sorted(d['users']['user_id'])
    need(len(set(users))==100 and all(pd.Series(users).str.fullmatch(r'U\d{3}')),'Nutzer-IDs ungültig')
    key_columns = {'raw':['activity_id'],'selected':['activity_id'],'users':['user_id'],
                   'weekly':['user_id','week_index'],'kmeans':['user_id'],'scaled':['user_id'],
                   'regression':['user_id','week_index'],'train':['user_id','week_index'],
                   'test':['user_id','week_index'],'control':['user_id','week_start']}
    for name,keys in key_columns.items():
        need(not d[name].duplicated(keys).any(),f'{name}: doppelte Schlüssel')
        need(not d[name][keys].eq('').any().any(),f'{name}: leere Schlüssel')
        need(set(d[name]['user_id'])==set(users),f'{name}: Nutzerliste unvollständig/unbekannt')
    passed('Schemas, Zeilenzahlen, Schlüssel und Nutzerlisten','Alle zehn CSVs vollständig; skalierter Export exakt ID + neun Eingänge')
    raw=d['raw'];selected=d['selected']
    same_frame(selected,raw[ACT_COLUMNS],['activity_id'],'Aktivitäten/Auswahlwerte verändert')
    need(not raw[ACT_COLUMNS].eq('').any().any(),'Fehlende Pflichtwerte in Rohaktivitäten')
    need(raw['activity_id'].str.fullmatch(r'A\d{6}').all(),'Ungültige Aktivitätskennung')
    need(set(raw['sport_type'])==set(SPORTS),'Sportarten abweichend')
    dates=pd.to_datetime(raw['date'],format='%Y-%m-%d',errors='raise')
    need((dates.dt.strftime('%Y-%m-%d')==raw['date']).all(),'Datum nicht strikt ISO')
    need(dates.between('2026-01-05','2026-07-05').all(),'Datum außerhalb V2-Zeitraum')
    duration=raw['duration_min'].map(Decimal)
    need(all(v.is_finite() and v>=0 for v in duration),'Ungültige Dauer')
    limits={'Running':(10,150,5,16),'Cycling':(15,240,8,35),'Strength':(15,120,None,None),
            'Swimming':(10,100,.8,3.5),'Walking':(10,180,2.5,6.5),
            'Hiking':(30,360,1.5,6),'Tennis':(20,180,None,None),'Padel':(20,150,None,None)}
    structural=0
    for sport,minute,distance in zip(raw['sport_type'],duration,raw['distance_km']):
        lo,hi,vlo,vhi=limits[sport]
        need(lo<=minute<=hi,'Dauer außerhalb dokumentierter Sportgrenzen')
        if vlo is None:
            need(distance=='','Unerwartete Distanz bei nicht anwendbarer Sportart');structural+=1
        else:
            distance=Decimal(distance)
            need(distance.is_finite() and distance>=0,'Ungültige Distanz')
            lower=(minute-Decimal('.05'))/60*Decimal(str(vlo))-Decimal('.005')
            upper=(minute+Decimal('.05'))/60*Decimal(str(vhi))+Decimal('.005')
            need(lower<=distance<=upper,'Unplausible Distanz/Geschwindigkeit')
    need(all(d['users'][c].isin(['True','False']).all() for c in list(d['users'])[1:]),'Ungültige Interessenwerte')
    need(decimal_sum(raw['duration_min'])==decimal_sum(selected['duration_min'])==Decimal('422829.9'),
         'Roh-/Auswahlminutensumme abweichend')
    passed('Aktivitätsauswahl und Rohqualität',f'Alle 6.465 Aktivitätszeilen und fünf Werte exakt erhalten; {structural} strukturell nicht anwendbare Distanzen')

    # Unabhängige Wochenrekonstruktion direkt aus Rohaktivitäten, nicht aus Prüfberichten.
    work=raw.assign(week_start=(dates-pd.to_timedelta(dates.dt.weekday,unit='D')).dt.strftime('%Y-%m-%d'),
                    minutes=duration)
    aggregation=work.groupby(['user_id','week_start']).agg(count=('activity_id','size'),minutes=('minutes','sum'))
    week=d['weekly'];week_lookup={}
    expected_keys={(uid,index) for uid in users for index in range(1,27)}
    actual_keys={(r.user_id,int(r.week_index)) for r in week.itertuples()}
    need(actual_keys==expected_keys,'Unvollständiges Wochenraster')
    need(list(zip(week['user_id'],week['week_index'].astype(int)))==sorted(actual_keys),'Wochen nicht sortiert')
    zero=0
    for r in week.itertuples():
        index=int(r.week_index);begin=START+timedelta(weeks=index-1)
        need(r.week_start==begin.isoformat() and r.week_end==(begin+timedelta(days=6)).isoformat(),
             'Falscher Wochenkalender/week_end')
        need(r.activities_count.isdigit(),'Wochenaktivitäten nicht nicht-negative Integer')
        actual_count=int(r.activities_count);actual_minutes=Decimal(r.total_duration_min)
        reference=aggregation.loc[(r.user_id,r.week_start)] if (r.user_id,r.week_start) in aggregation.index else None
        expected_count=0 if reference is None else int(reference['count'])
        expected_minutes=Decimal(0) if reference is None else reference['minutes']
        need(actual_count==expected_count and actual_minutes==expected_minutes,'Wochenwerte weichen von Rohaktivitäten ab')
        if actual_count==0:
            zero+=1;need(actual_minutes==0,'Nullwoche mit Minuten')
        week_lookup[r.user_id,index]=(actual_count,r.week_start,r.week_end)
    need(zero==558 and len(aggregation)==2042,'Nullwochen/aktive Gruppen abweichend')
    need(sum(int(v) for v in week['activities_count'])==6465 and
         decimal_sum(week['total_duration_min'])==Decimal('422829.9'),'Wochensummen abweichend')
    control={(r.user_id,r.week_start):int(r.activity_count) for r in d['control'].itertuples()}
    need(control=={(uid,val[1]):val[0] for (uid,i),val in week_lookup.items()},'Unabhängige Wochenkontrolle abweichend')
    passed('Wochenraster und Rohdatenrekonstruktion','2.600 eindeutige Nutzerwochen; 2.042 aktive Gruppen + 558 echte Nullen; jede Count-/Minutensumme stimmt')

    # Nutzermerkmale mit eigener Groupby-/Crosstab-Referenz.
    totals=raw.groupby('user_id').agg(count=('activity_id','size'))
    minute_totals=work.groupby('user_id')['minutes'].sum()
    sports=pd.crosstab(raw['user_id'],raw['sport_type']).reindex(index=users,columns=SPORTS,fill_value=0)
    reference=np.column_stack([totals.loc[users,'count'].to_numpy()/26,
                               sports.to_numpy()/totals.loc[users,'count'].to_numpy()[:,None]])
    unscaled=sorted_frame(d['kmeans'],['user_id'])
    need(unscaled['user_id'].tolist()==d['kmeans']['user_id'].tolist(),'Nutzerprofile nicht sortiert')
    x=unscaled[FEATURES].astype(float).to_numpy()
    need(np.isfinite(x).all() and (x>=0).all(),'Ungültige unskalierte Eingänge')
    close(x,reference,'Falsche K-Means-Eingangsmerkmale')
    close(x[:,1:].sum(axis=1),1,'Anteilssummen nicht 1')
    need((x[:,1:]<=1).all(),'Anteile außerhalb [0,1]')
    expected_diversity=(sports>0).sum(axis=1).to_numpy()
    need(np.array_equal(unscaled['sport_diversity'].astype(int),expected_diversity),'Sportvielfalt falsch')
    close(unscaled['avg_duration_per_week'].astype(float),[float(minute_totals[uid]/26) for uid in users],
          'Wochenminuten pro Nutzer falsch')
    close(math.fsum(x[:,0]*26),6465,'Nutzeraktivitätensumme falsch')
    close(math.fsum(unscaled['avg_duration_per_week'].astype(float)*26),422829.9,'Nutzerminuten verloren')
    for uid in users:
        need(sum(week_lookup[uid,i][0] for i in range(1,27))==int(totals.loc[uid,'count']),
             'Nutzer-/Wochensummen abweichend')
    passed('Nutzeraggregate und neun K-Means-Merkmale','100 vollständige Profile; alle Sportanteile und zwei Interpretationsmerkmale unabhängig rekonstruiert')

    params=meta['params']
    need(params['active_version']=='V2' and params['feature_order']==FEATURES and params['n_users']==100 and
         params['method']=='sklearn.preprocessing.StandardScaler' and params['ddof']==0 and
         params['with_mean'] is True and params['with_std'] is True,'Skalierungsmetadaten falsch')
    means=x.mean(axis=0);variances=x.var(axis=0);std=np.sqrt(variances)
    pmean=np.array([params['features'][f]['mean'] for f in FEATURES])
    pscale=np.array([params['features'][f]['scale'] for f in FEATURES])
    pvar=np.array([params['features'][f]['variance'] for f in FEATURES])
    pstd=np.array([params['features'][f]['std_ddof0'] for f in FEATURES])
    weights=np.array([params['features'][f]['weight'] for f in FEATURES])
    close(pmean,means,'Gespeicherte Mittelwerte falsch');close(pvar,variances,'Gespeicherte Varianzen falsch')
    close(pstd,std,'Gespeicherte Standardabweichungen falsch');close(pscale,std,'V2-scale_ falsch')
    close(weights,[1]+[1/np.sqrt(8)]*8,'Sportgewicht falsch')
    close(params['sport_weight_factor'],1/np.sqrt(8),'Globales Sportgewicht falsch')
    need((variances>0).all() and np.isfinite(pscale).all() and (pscale>0).all(),'V2-Varianz/Skalen ungültig')
    need(params['fit_user_ids']==users and params['n_samples_seen']==100,'Falsche Skalierungs-Fitpopulation')
    need(all(not params['features'][f]['constant'] and not params['features'][f]['numerically_constant'] for f in FEATURES),
         'V2-Konstantenstatus falsch')
    scaled=sorted_frame(d['scaled'],['user_id'])
    need(scaled['user_id'].tolist()==d['scaled']['user_id'].tolist(),'Skalierte Nutzer nicht sortiert')
    y=scaled[FEATURES].astype(float).to_numpy()
    need(np.isfinite(y).all(),'Nicht endliche skalierte Eingänge')
    z=(x-pmean)/pscale
    close(y,z*weights,'JSON-Parameter reproduzieren skalierte Werte nicht')
    close(y,(x-means)/std*weights,'Unabhängige Standardisierung abweichend')
    close(z.mean(axis=0),0,'z-Mittelwerte falsch');close(z.var(axis=0),1,'z-Varianzen falsch')
    close(y.mean(axis=0),0,'Gewichtete Mittelwerte falsch');close(y.var(axis=0),[1]+[1/8]*8,'Gewichtete Varianzen falsch')
    close((y/weights)*pscale+pmean,x,'Inverse Skalierung falsch')
    passed('Standardisierung und Gewichtung','Alle Parameter unabhängig nachgerechnet; JSON reproduziert 100×9 Werte; Blockvarianzsummen jeweils ≈1')

    # Regression wird ausschließlich aus adressierten Wochen nachgerechnet.
    reg=d['regression']
    expected_reg={(uid,i) for uid in users for i in range(4,26)}
    need({(r.user_id,int(r.week_index)) for r in reg.itertuples()}==expected_reg,'Regressionsraster falsch')
    need(list(zip(reg['user_id'],reg['week_index'].astype(int)))==sorted(expected_reg),'Regression nicht sortiert')
    zero_current=zero_target=zero_history=0
    for r in reg.itertuples():
        index=int(r.week_index);history=[week_lookup[r.user_id,i][0] for i in range(index-3,index+1)]
        current=week_lookup[r.user_id,index];target=week_lookup[r.user_id,index+1]
        need(r.activities_current_week.isdigit() and r.activities_next_week.isdigit(),'Ungültige Integer-Counts/Ziele')
        need(r.week_start==current[1] and r.week_end==current[2],'Regressionskalender falsch')
        need(int(r.activities_current_week)==current[0] and int(r.activities_next_week)==target[0],
             'Falsche aktuelle Woche oder Folgeziel/Nutzervermischung')
        avg=float(r.avg_activities_last_4_weeks)
        need(math.isfinite(avg) and avg>=0,'Ungültiges Regressionsmerkmal')
        close(avg,sum(history)/4,'Falsches Fenster/Zukunftsinformation')
        need(date.fromisoformat(target[1])>date.fromisoformat(r.week_end),'Zielzeitpunkt nicht nach Eingabe')
        zero_current+=current[0]==0;zero_target+=target[0]==0;zero_history+=0 in history
    passed('Regression und Zeitverfügbarkeit','Alle 2.200 Zeilen: X nur t−3…t, y t+1 desselben Nutzers; keine künstliche Historie')
    for name,weeks,per_user in [('train',range(4,22),18),('test',range(22,26),4)]:
        frame=d[name]
        need({(r.user_id,int(r.week_index)) for r in frame.itertuples()}=={(uid,i) for uid in users for i in weeks},
             f'{name}: falsche Wochengrenzen')
        need((frame.groupby('user_id').size()==per_user).all(),f'{name}: falsche Nutzerverteilung')
        need(list(zip(frame['user_id'],frame['week_index'].astype(int)))==sorted((uid,i) for uid in users for i in weeks),
             f'{name}: falsche Sortierung')
    train_keys={(r.user_id,int(r.week_index)) for r in d['train'].itertuples()}
    test_keys={(r.user_id,int(r.week_index)) for r in d['test'].itertuples()}
    need(train_keys.isdisjoint(test_keys),'Train/Test-Schlüssel überlappen')
    same_frame(pd.concat([d['train'],d['test']],ignore_index=True),reg,['user_id','week_index'],
               'Split verändert/verliert Ausgangswerte')
    train_targets={i+1 for uid,i in train_keys};test_targets={i+1 for uid,i in test_keys}
    need(max(train_targets)==22 and min(test_targets)==23 and train_targets.isdisjoint(test_targets),
         'Prognose-Zielwochen nicht getrennt')
    split=meta['split']
    need(split['active_version']=='V2' and split['split_column']=='week_index' and
         split['train_input_weeks']==list(range(4,22)) and split['test_input_weeks']==list(range(22,26)) and
         split['train_target_weeks']==list(range(5,23)) and split['test_target_weeks']==list(range(23,27)) and
         split['train_rows']==1800 and split['test_rows']==400 and split['n_users']==100 and
         split['model_input_features']==REG_COLUMNS[4:6] and split['target']==REG_COLUMNS[6] and
         split['excluded_metadata']==REG_COLUMNS[:4] and split['columns']==REG_COLUMNS and
         split['total_rows']==2200 and split['train_rows_per_user']==18 and split['test_rows_per_user']==4 and
         split['train_target_date_range']==['2026-02-02','2026-06-07'] and
         split['test_target_date_range']==['2026-06-08','2026-07-05'],'Split-Manifest inhaltlich falsch')
    passed('Train/Test und Manifest','1.800/400 unveränderte Zeilen; 18/4 pro Nutzer; disjunkte Zielwochen 5–22 / 23–26')
    pooled=6465/2600;without=6465/2042
    metrics={'raw_activities':len(raw),'selected_activities':len(selected),'users':len(users),
             'weekly_rows':len(week),'active_weeks':len(aggregation),'zero_weeks':zero,
             'kmeans_rows':len(unscaled),'scaled_rows':len(scaled),'regression_rows':len(reg),
             'train_rows':len(d['train']),'test_rows':len(d['test']),'total_minutes':str(decimal_sum(raw['duration_min'])),
             'mean_with_zero_weeks':pooled,'mean_without_zero_weeks':without,
             'overestimation_pct':(without/pooled-1)*100,'zero_week_pct':zero/2600*100,
             'regression_current_zeros':zero_current,'regression_target_zeros':zero_target,
             'regression_zero_history_rows':zero_history,'weight':float(1/np.sqrt(8)),
             'max_abs_scaled_mean':float(np.abs(y.mean(axis=0)).max()),
             'block_variance_sums':[float(y.var(axis=0)[0]),float(y.var(axis=0)[1:].sum())]}
    return checks,metrics,{'x':x,'z':z,'y':y}


def verify_hashes(root, meta):
    paths=set(CSV_PATHS.values())|set(JSON_PATHS.values())|{'data/raw/offers_simulated.csv'}
    actual={name:digest(root/name) for name in sorted(paths)}
    need(set(meta['active']['sha256'])=={'data/raw/activities_simulated.csv','data/raw/users_simulated.csv',
         'data/raw/offers_simulated.csv','outputs/tables/simulation_weekly_check.csv'},'Unerwartete Manifest-Hashquellen')
    groups=[meta['active']['sha256'],meta['params']['input_sha256'],meta['split']['input_integrity_sha256'],
            meta['split']['output_sha256'],{meta['split']['input_file']:meta['split']['input_sha256']},
            {'data/processed/kmeans_user_features_scaled.csv':meta['params']['output_csv_sha256']}]
    for hashes in groups:
        for name,expected in hashes.items():
            need(name in actual and actual[name]==expected,f'SHA-256 abweichend: {name}')
    return actual


def save_figure(fig,path):
    fig.savefig(path,dpi=180,facecolor='white',metadata={'Software':'MOVA AP 4.7 independent audit'})
    plt.close(fig)


def make_figures(metrics, arrays, folder):
    """Vier klar beschriftete Diagramme ausschließlich aus auditierten Daten."""
    folder.mkdir(parents=True,exist_ok=True)
    plt.rcParams.update({'font.family':'DejaVu Sans','font.size':11,'axes.spines.top':False,
                         'axes.spines.right':False,'axes.titleweight':'bold','figure.dpi':100})
    blue='#245B83';green='#217D73';orange='#CE8B36';grey='#6B7280'
    # 1. Tatsächliche Quellen: Sportmix stammt aus Einzelaktivitäten, Wochen dienen dem Summenabgleich.
    fig,ax=plt.subplots(figsize=(15,8));ax.set(xlim=(0,15),ylim=(0,8));ax.axis('off')
    fig.suptitle('MOVA · Umgesetzte Data Preparation (V2)',fontsize=21,x=.07,ha='left',y=.97)
    def box(x,y,w,h,title,detail,color):
        ax.add_patch(FancyBboxPatch((x,y),w,h,boxstyle='round,pad=0.10,rounding_size=.12',
                                   facecolor=color,edgecolor='none',alpha=.12))
        ax.text(x+w/2,y+h*.68,title,ha='center',va='center',weight='bold',color=color,fontsize=10.5)
        ax.text(x+w/2,y+h*.29,detail,ha='center',va='center',fontsize=9,linespacing=1.5)
    def arrow(a,b,dashed=False):
        ax.add_patch(FancyArrowPatch(a,b,arrowstyle='-|>',mutation_scale=16,color=grey,
                                    linewidth=1.5,linestyle='--' if dashed else '-'))
    box(.2,5.3,3,1.2,'Rohaktivitäten','6.465 Aktivitätszeilen · 6 Spalten',blue)
    box(4.2,5.3,3.4,1.2,'Data Selection','6.465 Aktivitätszeilen · 5 Spalten',blue)
    box(.2,2.8,3,1.2,'Vollständige Nutzerliste','100 Nutzer · unverändert',green)
    box(4.2,2.8,3.4,1.2,'Wochenaggregation + Raster','2.600 Nutzerwochen\ninklusive 558 Nullwochen',green)
    box(9,5.3,2.5,1.2,'Nutzermerkmale','100 Nutzerprofile\n9 Eingänge + 2 Interpretation',green)
    box(12.2,5.3,2.5,1.2,'Standardisierung','100 Nutzerprofile\n9 skalierte/gewichtete Eingänge',green)
    box(9,2.8,2.5,1.2,'Regressionsmerkmale','2.200 Beobachtungen\n2 Eingänge + beobachtetes Ziel',blue)
    box(12.2,2.8,2.5,1.2,'Chronologischer Split','1.800 Training\n400 Testbeobachtungen',blue)
    arrow((3.3,5.9),(4.1,5.9));arrow((7.7,5.9),(8.9,5.9));arrow((11.6,5.9),(12.1,5.9))
    arrow((5.9,5.2),(5.9,4.1));arrow((3.3,3.4),(4.1,3.4))
    arrow((7.7,3.4),(8.9,3.4));arrow((11.6,3.4),(12.1,3.4))
    arrow((2.5,4.1),(9.1,5.2),True)
    arrow((7.7,4),(9.7,5.2),True)
    ax.text(8.2,4.45,'Nutzersummen\nabgleichen',ha='center',fontsize=9,color=grey)
    ax.text(.2,1.5,'Lesart: Pfeile zeigen Verarbeitung und Quellen; gestrichelt: Nutzerintegration / Kontrollabgleich.',color=grey)
    ax.text(.2,1.0,'Zeileneinheiten unterscheiden sich: Aktivitäten ≠ Nutzerwochen ≠ Profile ≠ Regressionsbeobachtungen.',color=grey)
    ax.text(.2,.5,'Keine Modelle, Clusterlabels, Prognosen oder Gütemaße erzeugt.',color=grey)
    save_figure(fig,folder/'data_preparation_pipeline.png')

    # 2. Gleiche Einheit auf beiden Vergleichsachsen: Aktivitäten pro Nutzerwoche.
    fig,axes=plt.subplots(1,2,figsize=(13,5.7),gridspec_kw={'width_ratios':[1.25,1]})
    fig.suptitle('Nullwochen bewahren die vollständige Beobachtungszeit',fontsize=17,y=.96)
    ax=axes[0];ax.barh(['Vollständiges Raster'],[metrics['active_weeks']],color=blue,label='2.042 aktive Nutzerwochen')
    ax.barh(['Vollständiges Raster'],[metrics['zero_weeks']],left=[metrics['active_weeks']],color=orange,label='558 ergänzte Nullwochen')
    ax.text(1021,0,'2.042',ha='center',va='center',color='white',weight='bold')
    ax.text(2321,0,'558',ha='center',va='center',color='white',weight='bold')
    ax.set_yticks([]);ax.set_xlim(0,2800);ax.set_xlabel('Nutzerwochen (insgesamt 2.600)');ax.set_ylim(-.7,.7)
    ax.legend(loc='lower left',bbox_to_anchor=(0,1.02),frameon=False,fontsize=10)
    ax=axes[1];values=[metrics['mean_with_zero_weeks'],metrics['mean_without_zero_weeks']]
    bars=ax.bar(['Mit Nullwochen\n6.465 / 2.600','Nur aktive Wochen\n6.465 / 2.042'],values,color=[green,orange],width=.6)
    ax.set_ylabel('Aktivitäten je Nutzerwoche (gepoolter Mittelwert)');ax.set_ylim(0,3.9)
    for bar,value in zip(bars,values):ax.text(bar.get_x()+bar.get_width()/2,value+.06,f'{value:.4f}',ha='center',weight='bold')
    ax.text(.5,3.65,f'Ohne Nullwochen: +{metrics["overestimation_pct"]:.2f} %',ha='center',color='#9B5B15',weight='bold')
    fig.text(.05,.035,'Nullwochen ergänzen die vollständige Zeitreihe. Der aktive-Wochen-Mittelwert überschätzt die Häufigkeit über alle 26 Wochen.',fontsize=10)
    fig.subplots_adjust(left=.07,right=.97,bottom=.20,top=.77,wspace=.38)
    save_figure(fig,folder/'data_preparation_zero_weeks.png')

    # 3. Separate Achsen pro Maßstab; gleiche Nutzer, keine vermeintliche Prozentdarstellung von z.
    fig,axes=plt.subplots(2,3,figsize=(14,8))
    fig.suptitle('Standardisierung und Sportmixgewichtung · tatsächliche 100 V2-Nutzer',fontsize=17,y=.98)
    titles=['Ursprünglicher Wert','StandardScaler · z','Nach Bereichsgewichtung']
    for row,index in enumerate([0,1]):
        for col,matrix in enumerate([arrays['x'],arrays['z'],arrays['y']]):
            ax=axes[row,col];ax.hist(matrix[:,index],bins=15,color=[blue,green,orange][col],edgecolor='white')
            ax.set_title(titles[col],fontsize=12);ax.set_ylabel('Anzahl Nutzer')
            label=('Aktivitäten / Woche' if index==0 else 'Running-Anteil (0–1)') if col==0 else 'Standardisierter Wert z'
            if col==2:label='z (Häufigkeit unverändert)' if index==0 else 'z / √8 (Running)'
            ax.set_xlabel(label)
            if col>0:ax.axvline(0,color=grey,lw=1,ls='--')
            ax.text(.98,.94,'Häufigkeit' if row==0 else 'Running-Anteil',transform=ax.transAxes,ha='right',va='top',fontsize=10)
    fig.text(.06,.035,'Jedes Panel hat eine eigene x-Skala. Negative standardisierte Werte sind erwartbar: Rohwert unter dem jeweiligen Mittelwert.',fontsize=10)
    fig.subplots_adjust(left=.06,right=.98,bottom=.13,top=.89,wspace=.30,hspace=.50)
    save_figure(fig,folder/'data_preparation_scaling.png')

    # 4. Eingaben und Ziele als unterschiedliche Zeilen mit explizitem Wochenraster.
    fig,ax=plt.subplots(figsize=(15,6.8));fig.suptitle('Regression · chronologisches Testdesign',fontsize=19,y=.96)
    lanes=[('Training: Eingaben · 1.800 Zeilen',4,21,blue),('Training: Ziele',5,22,blue),
           ('Test: Eingaben · 400 Zeilen',22,25,orange),('Test: Ziele',23,26,orange)]
    for y,(label,lo,hi,color) in enumerate(lanes):
        ax.barh(y,26,left=.5,color='#EEF1F4',height=.6)
        ax.barh(y,hi-lo+1,left=lo-.5,color=color,height=.6)
        ax.text((lo+hi)/2,y,f'Wochen {lo}–{hi}',ha='center',va='center',color='white',weight='bold')
    ax.set_yticks(range(4),[lane[0] for lane in lanes]);ax.invert_yaxis()
    ax.set_xticks(range(1,27));ax.set_xlim(.5,26.5);ax.set_xlabel('Relative Beobachtungswoche · 1 = 05.01.–11.01.2026; 26 = 29.06.–05.07.2026')
    ax.axvline(22.5,color=grey,ls='--',lw=1)
    fig.text(.07,.22,'Wochen 1–3: notwendige vergangene Historie; frühestens in Woche 4 ist das Vierwochenfenster vollständig.',fontsize=11)
    fig.text(.07,.17,'Woche 26: nur als Ziel nutzbar; für eine Eingabe in Woche 26 fehlt das beobachtete Ziel aus Woche 27.',fontsize=11)
    fig.text(.07,.11,'Geplante Evaluation: rollierende Einwochenprognose; Modell während der Testphase unverändert.',fontsize=11,weight='bold')
    fig.text(.07,.06,'Abgeschlossene frühere Testwochen dürfen spätere Eingaben bilden. Hier wurden noch keine Modelle oder Prognosen erzeugt.',fontsize=10)
    fig.subplots_adjust(left=.24,right=.97,bottom=.36,top=.86)
    save_figure(fig,folder/'data_preparation_train_test_split.png')


def report_text(checks, metrics, hashes):
    lines=['# MOVA – unabhängiges Data-Preparation-Audit (AP 4.7)','',
           'Stand: 31.10.2026. Aktive synthetische V2. CRISP-DM 3.5 Format Data / Qualitätssicherung.',
           'Basiscommit: `ed52949cb8b688bc64c0793be0e407950314769e`, Branch `ap4-data-preparation`; AP-4-Arbeit weiterhin uncommitted.',
           '', '## Ziel und unabhängige Methode','',
           'Alle tatsächlichen CSV-/JSON-Artefakte erneut einlesen. Keine früheren Prüfberichte als Beweis und keine Imports aus Transformationsskripten. '
           'Wochenwerte direkt aus Rohaktivitäten rekonstruieren, Nutzer-/Sportaggregate mit Groupby/Crosstab unabhängig nachrechnen, '
           'Skalierungsparameter gegen Populationsstatistiken vergleichen, Regressionsfenster per Nutzer/Wochenadresse nachprüfen. '
           'Keine bestehenden Daten oder Transformationsskripte ändern. Kritische Fehler stoppen vor Visualisierung und Berichterstellung.',
           '', '## Tatsächlich geprüfte Dateien und SHA-256','', '| Datei | SHA-256 |','| --- | --- |']
    lines += [f'| `{name}` | `{value}` |' for name,value in hashes.items()]
    lines += ['', 'Alle vier aktiven V2-Manifest-Prüfsummen und dokumentierten Eingangs-/Ausgabehashes in Skalierungsparametern und Split-Manifest stimmen. '
              'Alle aufgelisteten Dateien vor/nach Audit auf bytegleiche Integrität geprüft. Angebote werden ausschließlich per Hash geprüft, nicht in Modellierungsdaten integriert.',
              '', '## Tatsächliche Qualitätsprüfungen','', '| Prüfung | Ergebnis |','| --- | --- |']
    lines += [f'| {label} | BESTANDEN: {detail} |' for label,detail in checks]
    lines += ['', '## Neu berechnete Kennzahlen','', '| Kennzahl | Tatsächlicher Wert |','| --- | --- |']
    lines += [f'| {name} | {value} |' for name,value in metrics.items()]
    lines += ['', '## Vergleich mit und ohne Nullwochen','',
              f'Gepoolte Trainingshäufigkeit über das vollständige Raster: 6.465 / 2.600 = **{metrics["mean_with_zero_weeks"]:.8f} Aktivitäten je Nutzerwoche**. '
              f'Nach Weglassen der 558 Nullwochen: 6.465 / 2.042 = **{metrics["mean_without_zero_weeks"]:.8f}**. '
              f'Relative Überschätzung gegenüber der vollständigen Beobachtungszeit: **{metrics["overestimation_pct"]:.4f} %** '
              '((Mittel ohne Nullen / Mittel mit Nullen − 1) × 100).',
              '', 'Das sind gepoolte Nutzerwochenmittel, keine mittlere Trainingsdauer und keine durchschnittliche Aktivitätszahl ausschließlich aktiver Nutzer. '
              'Im vollständigen Raster haben alle Nutzer denselben Nenner 26; deshalb entspricht dieser Mittelwert dort auch dem Mittel ihrer individuellen Wochenhäufigkeiten. '
              'Ohne Nullwochen ist die Gewichtung je Nutzer unterschiedlich. Der aktive-Wochen-Mittelwert beschreibt eine andere bedingte Größe und überschätzt '
              'bei Verwendung als Häufigkeit über den gesamten Zeitraum systematisch den hier tatsächlich beobachteten Wert.',
              '', '## Vier Abbildungen','',
              '1. [Datenfluss](../figures/data_preparation_pipeline.png): echte Verarbeitung und verschiedene Zeileneinheiten. '
              'Nutzer-Sportmix kommt aus Einzelaktivitäten, Nutzerliste führt die Integration an; Wochenwerte liefern den Summenabgleich. Boxgrößen kodieren keine Stichprobengröße.',
              '2. [Nullwochen](../figures/data_preparation_zero_weeks.png): 2.042 aktive + 558 Nullwochen und der exakt berechnete Nenner-Effekt.',
              '3. [Standardisierung](../figures/data_preparation_scaling.png): dieselben 100 Nutzer, Häufigkeit und Running-Anteil jeweils roh, z-standardisiert und nach Gewichtung. '
              'Panels mit eigenen x-Skalen; negative z-Werte sind erwartbar. Jeder Sportanteil wird zusätzlich durch √8 geteilt.',
              '4. [Chronologischer Split](../figures/data_preparation_train_test_split.png): getrennte Eingabe-/Zielwochen. '
              'Wochen 1–3 liefern Historie; Woche 26 hat kein beobachtetes Folgeziel. '
              'Rollierende Einwochenprognosen mit später unverändertem Modell; keine tatsächliche Modellbewertung in diesem Audit.',
              '', '## Reproduktion und Software','',
              '`python src/data_preparation_audit.py`; Python '+platform.python_version()+', pandas '+pd.__version__+', NumPy '+np.__version__+', Matplotlib '+matplotlib.__version__+'. '
              'Numerische Vergleiche atol=rtol=1e−10; Minuten mit Decimal. Matplotlib Agg, feste Farben/Größen/Schrift und konstante PNG-Metadaten, kein Laufzeitstempel. '
              'Ein zweiter Lauf prüft identische Report-/PNG-Bytes; vorhandene fremde/abweichende Audit-Ausgaben werden nicht überschrieben. '
              'Reproduzierbarkeit gilt für diese Software-/Schriftumgebung; andere Rendering-Versionen können Pixelunterschiede erzeugen.',
              '', '## Technische Audit-Tests','',
              '`python -m unittest discover -s tests -v`: acht Audit-Tests plus 14 bestehende Zeit-/Splittests bestanden. '
              'Audit-Tests prüfen unveränderte V2, manipulierte Wochensummen, entfernte Nullwochen, falsche Train/Test-Grenzen '
              'bei unveränderten Zeilenzahlen, unzulässige Interpretationsspalten im skalierten Export, Zukunft im Mittelwert, '
              'falsche Gewichtungsparameter und falsche Manifest-Zielgrenzen. Änderungen ausschließlich an Speicherkopien; '
              'nicht nur Hashprüfungen, sondern Inhaltskontrollen lösen bei Manipulation aus.',
              '', '## Auffälligkeiten, Annahmen und Grenzen','',
              'Keine Qualitätsabweichung festgestellt. 558 Nullwochen sind echte fehlende Aktivitätsgruppen im bestätigten Raster, keine Imputation fehlerhafter Pflichtwerte. '
              'Skalierte share-Werte sind keine Wahrscheinlichkeiten; negative Werte zulässig. '
              'Neun positive V2-Merkmalsvarianzen führen nach Gewichtung zu Blockvarianzsummen ≈1; diese gleiche Streuungsgewichtung ist eine fachliche Startannahme, '
              'keine empirisch optimierte Clustergewichtung und kein Beleg einer Clusterstruktur.',
              '', '100 synthetische Nutzer und nur 26 Wochen; wiederholte Nutzer und überlappende Fenster erzeugen Abhängigkeiten. '
              'Keine Aussage zur Generalisierbarkeit auf echte Garmin-Nutzer. Testzielzeiträume sind getrennt, historische Eingabewochen dürfen sich überlappen. '
              'Neue frühere Testbeobachtungen dürfen erst nach ihrem Abschluss in spätere Eingaben gelangen; kein späteres Nachtrainieren auf Testzielen. '
              'Roh-, Auswahl-, Wochen- und Nutzeraggregate bewahren die Gesamtminuten. Regressionszeilen sind dagegen überlappende Fenster '
              'mit Rand-Ausschlüssen: ihre Counts oder Mittelwerte dürfen nicht als neue Aktivitäts-Gesamtsumme interpretiert werden.',
              '', '## Fazit','',
              '**Die vorliegenden Datensätze sind intern konsistent und für die geplante nachfolgende Modellierung vorbereitet. '
              'Ein bestandener Datenqualitätscheck ist kein Nachweis guter Modellgüte.** '
              'Keine Modelle, Labels, Prognosen oder Gütemaße erzeugt; keine neue CRISP-DM-Iteration ohne tatsächlichen Anlass.']
    return '\n'.join(lines)+'\n'


def main():
    data,meta=load_data()
    hashes=verify_hashes(ROOT,meta)
    checks,metrics,arrays=audit_content(data,meta)
    # Nur neue eigene Audit-Ausgaben; fremde bestehende Reports niemals überschreiben.
    staging=ROOT/'work/ap47_render';staging.mkdir(parents=True,exist_ok=True)
    make_figures(metrics,arrays,staging)
    report=report_text(checks,metrics,hashes).encode('utf-8')
    outputs={ROOT/'outputs/tables/data_preparation_audit_report.md':report}
    outputs.update({ROOT/'outputs/figures'/p.name:p.read_bytes() for p in sorted(staging.glob('data_preparation_*.png'))})
    for path,payload in outputs.items():
        need(not path.exists() or path.read_bytes()==payload,f'Bestehende Audit-Ausgabe abweichend, nicht überschrieben: {path}')
    for path,payload in outputs.items():
        if not path.exists():
            path.parent.mkdir(parents=True,exist_ok=True)
            with path.open('xb') as stream:stream.write(payload)
    need(hashes==verify_hashes(ROOT,meta),'Eingabedateien während Audit verändert')
    print(json.dumps({'status':'bestanden','independent_check_groups':len(checks),'metrics':metrics,
                     'outputs_sha256':{str(p.relative_to(ROOT)):digest(p) for p in outputs},
                     'input_hashes_unchanged':True},ensure_ascii=False,indent=2))


if __name__=='__main__':
    try:
        main()
    except (AuditError,ValueError,ArithmeticError,OSError,KeyError,TypeError) as exc:
        print(f'AUDIT ABBRUCH: {exc}\nKeine Datenkorrektur oder Änderung vorhandener Transformationen.',file=sys.stderr)
        sys.exit(1)
