"""AP 5.6: gespeicherte Prognosen gegen Persistenz, kein Modellaufruf/Training."""
import json
import numpy as np
import pandas as pd
from sklearn.metrics import mean_absolute_error,root_mean_squared_error
import modeling_regression_evaluate as prior

ROOT=prior.ROOT
require=prior.require
SOURCES=['data/processed/regression_test.csv','outputs/tables/regression_test_predictions.csv',
         'outputs/tables/regression_test_metrics.json','documentation/regression_split_manifest.json']


def align(test,predictions):
    test=prior.validate_test(test)
    require(len(predictions)==400 and not predictions.duplicated(['user_id','week_index']).any(),
            'Prognoseschlüssel fehlen/doppelt')
    joined=test.merge(predictions,on=['user_id','week_index'],how='outer',validate='one_to_one',
                      suffixes=('_test','_saved'),indicator=True)
    require(len(joined)==400 and (joined['_merge']=='both').all(),'Keine vollständige 1:1-Zuordnung')
    for f in ['week_start','week_end']+prior.FEATURES:
        require(np.array_equal(joined[f+'_test'],joined[f+'_saved']),f'Abweichender Eingang: {f}')
    require(np.array_equal(joined.activities_next_week,joined.actual_activities_next_week),'Abweichende Ziele')
    predicted=joined.predicted_activities_next_week.to_numpy()
    require(np.isfinite(predicted).all(),'Ungültige Regressionsprognosen')
    err=predicted-joined.activities_next_week.to_numpy()
    require(np.allclose(err,joined.prediction_error,atol=1e-14,rtol=1e-14) and
            np.allclose(abs(err),joined.absolute_error,atol=1e-14,rtol=1e-14),'Gespeicherte Fehler inkonsistent')
    table=pd.DataFrame(dict(user_id=joined.user_id,week_index=joined.week_index,
        week_start=joined.week_start_test,week_end=joined.week_end_test,
        activities_current_week=joined.activities_current_week_test,
        actual_activities_next_week=joined.activities_next_week,
        regression_prediction=predicted,baseline_prediction=joined.activities_current_week_test))
    table['regression_absolute_error']=abs(table.regression_prediction-table.actual_activities_next_week)
    table['baseline_absolute_error']=abs(table.baseline_prediction-table.actual_activities_next_week)
    table['absolute_error_difference']=table.baseline_absolute_error-table.regression_absolute_error
    return table.sort_values(['user_id','week_index']).reset_index(drop=True)


def improvement(baseline_mae,regression_mae):
    difference=float(baseline_mae-regression_mae)
    return dict(absolute_mae_improvement=difference,
        relative_mae_improvement_pct=float(difference/baseline_mae*100) if baseline_mae!=0 else None)


def summarize(table):
    result=dict(n_observations=len(table))
    actual=table.actual_activities_next_week
    for method in ['regression','baseline']:
        predicted=table[method+'_prediction'];errors=predicted-actual
        result[method]=dict(mae=float(mean_absolute_error(actual,predicted)),
            rmse=float(root_mean_squared_error(actual,predicted)),mean_signed_error=float(errors.mean()),
            absolute_error_min=float(abs(errors).min()),absolute_error_max=float(abs(errors).max()))
    result.update(improvement(result['baseline']['mae'],result['regression']['mae']))
    return result


def compare(root=ROOT):
    manifest=json.loads((root/SOURCES[3]).read_text())
    metrics=json.loads((root/SOURCES[2]).read_text())
    require(manifest['active_version']==metrics['data_version']=='V2','Keine V2')
    require(prior.contract.sha256(root/SOURCES[0])==manifest['output_sha256'][SOURCES[0]]==metrics['test_sha256'],
            'Testhash abweichend')
    test=pd.read_csv(root/SOURCES[0],float_precision='round_trip')
    predictions=pd.read_csv(root/SOURCES[1],float_precision='round_trip')
    table=align(test,predictions);total=summarize(table)
    for key in ['mae','rmse','mean_signed_error']:
        require(np.isclose(total['regression'][key],metrics[key],atol=1e-12,rtol=1e-12),'AP-5.5-Kennzahl abweichend')
    weeks=[dict(target_week=int(week)+1,**summarize(group)) for week,group in table.groupby('week_index',sort=True)]
    require([g['n_observations'] for g in weeks]==[100]*4,'Wochenumfänge falsch')
    groups={name:summarize(table[mask]) for name,mask in [
        ('actual_zero',table.actual_activities_next_week==0),('actual_positive',table.actual_activities_next_week>0)]}
    require(groups['actual_zero']['n_observations']==92 and groups['actual_positive']['n_observations']==308,
            'Null-/Nichtnullzahlen abweichend')
    diff=table.absolute_error_difference
    # Exakter Vergleich unveränderter Gleitkommawerte, keine nachträgliche Gleichheitstoleranz.
    outcomes={name:dict(count=int(mask.sum()),share=float(mask.mean())) for name,mask in [
        ('regression_better',diff>0),('baseline_better',diff<0),('equal',diff==0)]}
    require(sum(g['count'] for g in outcomes.values())==400,'Fallzahlen falsch')
    require(np.isclose(diff.mean(),total['absolute_mae_improvement'],atol=1e-12),'Differenzmittel inkonsistent')
    for method in ['regression','baseline']:
        require(np.isclose(sum(g[method]['mae']*g['n_observations'] for g in weeks)/400,total[method]['mae']),
                'Wochenaggregation inkonsistent')
    result=dict(data_version='V2',n_users=int(table.user_id.nunique()),
        baseline_definition='predicted_baseline_next_week = activities_current_week; kein Training',
        unit='Aktivitäten pro Nutzerwoche',difference_definition='baseline absolute error minus regression absolute error',
        equality_rule='Exakte Gleichheit der unveränderten absoluten Fehler',**total,
        mean_absolute_error_difference=float(diff.mean()),by_target_week=weeks,by_actual_group=groups,
        individual_outcomes=outcomes,source_sha256={p:prior.contract.sha256(root/p) for p in SOURCES})
    return table,result


def figures(result):
    plt=prior.plt
    with plt.rc_context({'font.family':'DejaVu Sans','font.size':11}):
        fig,ax=plt.subplots(figsize=(7,4.5),layout='constrained')
        values=[result['regression']['mae'],result['baseline']['mae']]
        bars=ax.bar(['Lineare Regression','Persistenz-Baseline'],values,color=['#176b87','#c56a22'])
        ax.bar_label(bars,fmt='%.4f',padding=3)
        ax.set(ylabel='MAE (Aktivitäten pro Nutzerwoche)',ylim=(0,max(values)*1.2),
               title='MOVA · Vergleich auf denselben 400 V2-Testbeobachtungen')
        prior.save_figure(fig,'regression_baseline_comparison.png')
        fig,ax=plt.subplots(figsize=(8,4.8),layout='constrained')
        weeks=result['by_target_week'];positions=np.arange(4)
        for i,(name,label,color) in enumerate([('regression','Lineare Regression','#176b87'),
                                              ('baseline','Persistenz-Baseline','#c56a22')]):
            values=[g[name]['mae'] for g in weeks]
            bars=ax.bar(positions+(i-.5)*.36,values,width=.36,label=label,color=color)
            ax.bar_label(bars,fmt='%.3f',padding=3,fontsize=9)
        ax.set(xticks=positions,xticklabels=[f"Zielwoche {g['target_week']}" for g in weeks],
               ylabel='MAE (Aktivitäten pro Nutzerwoche)',ylim=(0,2.5),
               title='MOVA · Jeweils dieselben 100 Nutzer pro Testwoche')
        ax.legend();prior.save_figure(fig,'regression_baseline_by_week.png')


def main():
    paths=[p for d in ['data','src','tests','documentation','outputs'] for p in (ROOT/d).rglob('*')
           if p.is_file() and '__pycache__' not in p.parts]
    before={p:prior.contract.sha256(p) for p in paths}
    table,result=compare()
    prior.contract.write_new_or_identical(ROOT/'outputs/tables/regression_baseline_comparison.csv',
        table.to_csv(index=False,lineterminator='\n',float_format='%.17g').encode())
    prior.contract.write_new_or_identical(ROOT/'outputs/tables/regression_baseline_metrics.json',
        (json.dumps(result,ensure_ascii=False,sort_keys=True,indent=2)+'\n').encode())
    figures(result)
    require(all(prior.contract.sha256(p)==sha for p,sha in before.items()),'Bestehende Datei verändert')
    print(json.dumps(result,ensure_ascii=False,sort_keys=True,indent=2))


if __name__=='__main__':main()
