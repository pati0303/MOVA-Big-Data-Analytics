"""AP 5.5: ausschließlich gespeichertes Modell verwenden, kein Training/Baseline."""
import io
import json
import os
from pathlib import Path
import joblib
import numpy as np
import pandas as pd
from sklearn.metrics import mean_absolute_error, root_mean_squared_error
from threadpoolctl import threadpool_limits
import modeling_regression_train as contract

ROOT=contract.ROOT
FEATURES=contract.FEATURES
TEST='data/processed/regression_test.csv'
os.environ.setdefault('MPLCONFIGDIR',str(ROOT/'work/matplotlib'))
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
require=contract.require


def load_model(root=ROOT):
    meta=json.loads((root/contract.METADATA).read_text())
    require(contract.sha256(root/contract.MODEL)==meta['model_sha256'],'Modellhash abweichend')
    require(meta['data_version']=='V2' and meta['feature_order']==meta['feature_names']==FEATURES and
            meta['target']==contract.TARGET,'Metadatenrollen abweichend')
    require(meta['parameters']==contract.PARAMETERS,'Parametervertrag abweichend')
    # Ausschließlich vertrauenswürdiges lokal erzeugtes Projektartefakt.
    model=joblib.load(root/contract.MODEL)
    require(model.get_params()==meta['parameters'] and list(model.feature_names_in_)==FEATURES,
            'Modell und Metadaten inkonsistent')
    np.testing.assert_array_equal(model.coef_,[meta['coefficients'][f] for f in FEATURES])
    require(model.intercept_==meta['intercept'],'Intercept abweichend')
    table=pd.read_csv(root/'outputs/tables/regression_linear_coefficients.csv',float_precision='round_trip')
    require(table.term.tolist()==['intercept']+FEATURES,'Koeffiziententabelle falsch')
    np.testing.assert_array_equal(table.coefficient,np.r_[model.intercept_,model.coef_])
    return model,meta


def validate_test(frame):
    require(list(frame.columns)==contract.COLUMNS,'Testschema unzulässig')
    require(len(frame)==400 and not frame.isna().any().any(),'Testgröße/Fehlwerte falsch')
    require(frame.user_id.nunique()==100 and not frame.duplicated(['user_id','week_index']).any(),
            'Nutzer/Schlüssel falsch')
    require(all(len(g)==4 and set(g.week_index)=={22,23,24,25} for _,g in frame.groupby('user_id')),
            'Testwochen falsch')
    values=frame[FEATURES+[contract.TARGET]].to_numpy(dtype=float)
    require(np.isfinite(values).all() and (values>=0).all(),'Ungültige Testwerte')
    require((values[:,[0,2]]%1==0).all(),'Counts nicht ganzzahlig')
    start=pd.to_datetime(frame.week_start,format='%Y-%m-%d',errors='raise')
    end=pd.to_datetime(frame.week_end,format='%Y-%m-%d',errors='raise')
    expected=pd.Timestamp('2026-01-05')+pd.to_timedelta((frame.week_index-1)*7,unit='D')
    require((start==expected).all() and ((end-start).dt.days==6).all(),'Testkalender falsch')
    return frame.sort_values(['user_id','week_index']).reset_index(drop=True)


def select_features(frame,features=FEATURES):
    require(list(features)==FEATURES,'Unerlaubte Modelleingänge oder Reihenfolge')
    x=frame[features].astype('float64').copy()
    require(x.shape==(400,2) and np.isfinite(x.to_numpy()).all(),'Ungültige X-Matrix')
    return x


def check_history(frame,weekly):
    require(not weekly.duplicated(['user_id','week_index']).any(),'Doppelte Wochenquelle')
    counts=weekly.set_index(['user_id','week_index']).activities_count
    for row in frame.itertuples():
        history=[counts.loc[(row.user_id,t)] for t in range(row.week_index-3,row.week_index+1)]
        require(row.activities_current_week==history[-1] and
                row.avg_activities_last_4_weeks==sum(history)/4 and
                row.activities_next_week==counts.loc[(row.user_id,row.week_index+1)],
                'Vergangenheitsfenster oder Folgeziel abweichend')


def predict_table(model,frame):
    x=select_features(frame)
    with threadpool_limits(limits=1):predicted=model.predict(x)
    require(predicted.shape==(400,) and np.isfinite(predicted).all(),'Ungültige Prognosen')
    table=frame.rename(columns={contract.TARGET:'actual_activities_next_week'}).copy()
    table['predicted_activities_next_week']=predicted
    table['prediction_error']=predicted-table.actual_activities_next_week
    table['absolute_error']=table.prediction_error.abs()
    return table


def metrics(table):
    actual=table.actual_activities_next_week.to_numpy(dtype=float)
    predicted=table.predicted_activities_next_week.to_numpy(dtype=float)
    error=predicted-actual;absolute=np.abs(error)
    require(np.isfinite(actual).all() and np.isfinite(predicted).all(),'Nicht endliche Kennzahlenbasis')
    return dict(n_observations=len(table),actual_mean=float(actual.mean()),predicted_mean=float(predicted.mean()),
        mae=float(mean_absolute_error(actual,predicted)),rmse=float(root_mean_squared_error(actual,predicted)),
        mean_signed_error=float(error.mean()),negative_predictions=int((predicted<0).sum()),
        negative_prediction_share=float((predicted<0).mean()),predicted_min=float(predicted.min()),
        predicted_max=float(predicted.max()),actual_min=float(actual.min()),actual_max=float(actual.max()),
        absolute_error_quantiles={str(q):float(np.quantile(absolute,q,method='linear'))
                                  for q in [0,.25,.5,.75,.9,.95,.99,1]},
        errors_above_3=int((absolute>3).sum()),errors_above_5=int((absolute>5).sum()))


def evaluate(root=ROOT):
    model,meta=load_model(root)
    original_coef=model.coef_.copy();original_intercept=model.intercept_
    manifest=json.loads((root/'documentation/regression_split_manifest.json').read_text())
    active=json.loads((root/'documentation/active_data_version.json').read_text())
    require(manifest['active_version']==active['active_version']=='V2','Datenversion falsch')
    require(contract.sha256(root/TEST)==manifest['output_sha256'][TEST],'Testhash abweichend')
    require(contract.sha256(root/contract.TRAIN)==meta['training_sha256'] and
            contract.sha256(root/'documentation/regression_split_manifest.json')==meta['split_manifest_sha256'],
            'Trainingsprovenienz abweichend')
    require(manifest['train_target_weeks']==list(range(5,23)) and
            manifest['test_target_weeks']==[23,24,25,26] and meta['train_target_weeks']==[5,22],
            'Zeitliche Zielgrenzen abweichend')
    frame=validate_test(pd.read_csv(root/TEST))
    path='data/processed/user_weekly_activities.csv'
    require(contract.sha256(root/path)==manifest['input_integrity_sha256'][path],'Wochenquellenhash falsch')
    check_history(frame,pd.read_csv(root/path))
    table=predict_table(model,frame)
    total=metrics(table)
    weeks=[]
    for week,group in table.groupby('week_index',sort=True):
        m=metrics(group)
        require(len(group)==100,'Wochenumfang falsch')
        weeks.append(dict(target_week=int(week)+1,target_week_start=str(
            (pd.Timestamp(group.week_start.iloc[0])+pd.Timedelta(days=7)).date()),
            n_observations=len(group),actual_mean=m['actual_mean'],predicted_mean=m['predicted_mean'],
            mae=m['mae'],rmse=m['rmse']))
    by_week=pd.DataFrame(weeks)
    require(np.isclose(np.average(by_week.mae,weights=by_week.n_observations),total['mae']) and
            np.isclose(np.sqrt(np.average(by_week.rmse**2,weights=by_week.n_observations)),total['rmse']),
            'Wochen-/Gesamtergebnisse inkonsistent')
    groups={}
    for name,mask in [('actual_zero',table.actual_activities_next_week==0),
                      ('actual_positive',table.actual_activities_next_week>0)]:
        subset=table[mask]
        groups[name]=dict(n_observations=len(subset),mae=metrics(subset)['mae'] if len(subset) else None)
    np.testing.assert_array_equal(model.coef_,original_coef)
    require(model.intercept_==original_intercept,'Modell verändert')
    result=dict(data_version='V2',test_file=TEST,test_sha256=contract.sha256(root/TEST),
        model_file=contract.MODEL,model_sha256=meta['model_sha256'],
        model_metadata_sha256=contract.sha256(root/contract.METADATA),
        n_users=int(frame.user_id.nunique()),test_target_weeks=[23,24,25,26],
        feature_names=FEATURES,target=contract.TARGET,unit='Aktivitäten pro Nutzerwoche',
        error_definition='prediction minus actual',prediction_postprocessing='none',
        evaluation_design='Rollierende Einwochenprognosen, unverändertes Modell',
        baseline_evaluated=False,**total,zero_week_groups=groups)
    return table,by_week,result


def render_figures(table,weeks):
    with plt.rc_context({'font.family':'DejaVu Sans','font.size':11}):
        fig,ax=plt.subplots(figsize=(9,4.8),layout='constrained')
        dates=pd.to_datetime(weeks.target_week_start)
        ax.plot(dates,weeks.actual_mean,'o-',label='Tatsächlich',color='#176b87')
        ax.plot(dates,weeks.predicted_mean,'s--',label='Prognose',color='#c56a22')
        ax.set(xticks=dates,xticklabels=[f'Woche {w}\n{d:%d.%m.%Y}' for w,d in zip(weeks.target_week,dates)],
            ylabel='Aktivitäten pro Nutzerwoche',xlabel='Zielwoche · Datum des Wochenbeginns',
            title='MOVA · Mittelwerte über jeweils 100 Nutzer (V2)')
        ax.set_ylim(bottom=0);ax.grid(alpha=.2);ax.legend()
        save_figure(fig,'regression_actual_vs_predicted.png')
        fig,ax=plt.subplots(figsize=(8,4.8),layout='constrained')
        ax.hist(table.absolute_error,bins=np.arange(0,np.ceil(table.absolute_error.max())+.5,.5),
                color='#176b87',edgecolor='white')
        ax.set(xlabel='Absoluter Prognosefehler (Aktivitäten pro Nutzerwoche)',ylabel='Anzahl Testbeobachtungen',
            title='MOVA · Absolute Fehler über 400 Testbeobachtungen (V2)')
        ax.grid(axis='y',alpha=.2)
        save_figure(fig,'regression_error_distribution.png')


def save_figure(fig,name):
    buffer=io.BytesIO();fig.savefig(buffer,format='png',dpi=180,metadata={'Software':'MOVA AP 5.5'})
    plt.close(fig);contract.write_new_or_identical(ROOT/'outputs/figures'/name,buffer.getvalue())


def main():
    paths=[p for d in ['data','src','tests','documentation','outputs'] for p in (ROOT/d).rglob('*')
           if p.is_file() and '__pycache__' not in p.parts]
    before={p:contract.sha256(p) for p in paths}
    table,weeks,result=evaluate()
    for name,frame in [('regression_test_predictions.csv',table),('regression_test_metrics_by_week.csv',weeks)]:
        contract.write_new_or_identical(ROOT/'outputs/tables'/name,
            frame.to_csv(index=False,lineterminator='\n',float_format='%.17g').encode())
    contract.write_new_or_identical(ROOT/'outputs/tables/regression_test_metrics.json',
        (json.dumps(result,ensure_ascii=False,sort_keys=True,indent=2)+'\n').encode())
    render_figures(table,weeks)
    require(all(contract.sha256(p)==sha for p,sha in before.items()),'Bestehende Datei verändert')
    print(json.dumps(result,ensure_ascii=False,sort_keys=True,indent=2))
    print(weeks.to_string(index=False))


if __name__=='__main__':main()
