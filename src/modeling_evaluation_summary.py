"""AP 5.7: Zusammenfassung vorhandener Ergebnisse, keinerlei Modellaufrufe."""
import json
import numpy as np
import pandas as pd
import modeling_regression_baseline as baseline

ROOT=baseline.ROOT
require=baseline.require
SOURCES=['documentation/kmeans_modeling_execution.md','documentation/kmeans_inference_contract.md',
 'documentation/regression_modeling_execution.md','outputs/models/kmeans_final_metadata.json',
 'outputs/models/regression_linear_metadata.json','outputs/tables/kmeans_k_selection.csv',
 'outputs/tables/kmeans_candidate_comparison.csv','outputs/tables/kmeans_final_cluster_profiles.csv',
 'outputs/tables/regression_test_metrics.json','outputs/tables/regression_baseline_metrics.json',
 'outputs/tables/regression_baseline_comparison.csv','documentation/crisp_dm_log.md','documentation/decisions.md']


def close(a,b,message):require(np.isclose(a,b,atol=1e-12,rtol=1e-12),message)


def validate_sources(k,selection,stability,profiles,r,b,table):
    require(k['data_version']==r['data_version']==b['data_version']=='V2','Datenversion falsch')
    require(k['n_clusters']==2 and k['n_users']==100,'K-Means-Umfang falsch')
    row=selection.set_index('k').loc[2];stable=stability.set_index('k').loc[2]
    close(k['inertia'],row.inertia,'Inertia widersprüchlich')
    close(k['silhouette_score'],row.silhouette_score,'Silhouette widersprüchlich')
    close(k['silhouette_score'],stable.silhouette_mean,'Stabilität/Silhouette widersprüchlich')
    require(stable.n_seeds==20 and stable.n_pairs==190 and stable.n_unique_partitions==1 and
            stable.ari_pairwise_mean==stable.ari_pairwise_min==stable.ari_pairwise_max==1,'ARI widersprüchlich')
    require(len(profiles)==2 and sorted(profiles.n_users.tolist())==[43,57],'Profile/Größen falsch')
    for p in profiles.itertuples():
        require(k['cluster_sizes'][str(p.cluster_id)]==p.n_users and
                k['cluster_id_to_segment'][str(p.cluster_id)]==p.segment_label,'Profilmapping widersprüchlich')
        close(k['labeling_basis'][str(p.cluster_id)],p.avg_activities_per_week,'Profilhäufigkeit widersprüchlich')
    require(len(table)==400 and table.user_id.nunique()==100 and
            not table.duplicated(['user_id','week_index']).any() and
            all(set(g.week_index)=={22,23,24,25} for _,g in table.groupby('user_id')),'Testumfang falsch')
    independent=baseline.summarize(table)
    for method in ['regression','baseline']:
        for key in ['mae','rmse','mean_signed_error','absolute_error_min','absolute_error_max']:
            close(independent[method][key],b[method][key],'Baselinezusammenfassung widersprüchlich')
    for key in ['mae','rmse','mean_signed_error']:
        close(r[key],b['regression'][key],'AP-5.5/5.6 widersprüchlich')
    close(independent['relative_mae_improvement_pct'],b['relative_mae_improvement_pct'],'Verbesserung falsch')
    for name,mask in [('actual_zero',table.actual_activities_next_week==0),
                       ('actual_positive',table.actual_activities_next_week>0)]:
        group=baseline.summarize(table[mask]);saved=b['by_actual_group'][name]
        require(group['n_observations']==saved['n_observations'],'Zielgruppenfälle falsch')
        for method in ['regression','baseline']:
            close(group[method]['mae'],saved[method]['mae'],'Zielgruppen-MAE falsch')
    for saved in b['by_target_week']:
        group=baseline.summarize(table[table.week_index==saved['target_week']-1])
        require(group['n_observations']==saved['n_observations']==100,'Wochenfälle falsch')
        for method in ['regression','baseline']:close(group[method]['mae'],saved[method]['mae'],'Wochen-MAE falsch')


def summarize(root=ROOT):
    read=lambda path:json.loads((root/path).read_text())
    k=read('outputs/models/kmeans_final_metadata.json')
    regression=read('outputs/models/regression_linear_metadata.json')
    r=read('outputs/tables/regression_test_metrics.json');b=read('outputs/tables/regression_baseline_metrics.json')
    selection=pd.read_csv(root/'outputs/tables/kmeans_k_selection.csv',float_precision='round_trip')
    stability=pd.read_csv(root/'outputs/tables/kmeans_candidate_comparison.csv',float_precision='round_trip')
    profiles=pd.read_csv(root/'outputs/tables/kmeans_final_cluster_profiles.csv',float_precision='round_trip')
    table=pd.read_csv(root/'outputs/tables/regression_baseline_comparison.csv',float_precision='round_trip')
    validate_sources(k,selection,stability,profiles,r,b,table)
    for meta,path in [(k,'outputs/models/kmeans_final.joblib'),(regression,'outputs/models/regression_linear.joblib')]:
        require(baseline.prior.contract.sha256(root/path)==meta['model_sha256'],'Modellartefakthash falsch')
    require(regression['model_sha256']==r['model_sha256'] and regression['n_training_rows']==1800,
            'Regressionsprovenienz widersprüchlich')
    for path,sha in b['source_sha256'].items():
        require(baseline.prior.contract.sha256(root/path)==sha,'Evaluationsquellhash falsch')
    diagnostics={name:baseline.summarize(table[mask]) for name,mask in [
        ('current_week_zero',table.activities_current_week==0),
        ('current_week_positive',table.activities_current_week>0)]}
    limits=['Nur synthetische V2, keine reale Garmin-Validierung',
        'Regression: vier Testwochen derselben 100 Nutzer, abhängige Beobachtungen',
        'K-Means: interne Bewertung auf Fitdaten, keine neue Stichprobe',
        'ARI misst nur Initialisierungsstabilität bei unveränderten Daten',
        'Regression schwächer nach MAE bei tatsächlichen Nullzielen; große Einzelfehler',
        'Kein Empfehlungs- oder finanzieller Nutzen nachgewiesen']
    return dict(data_version='V2',n_users=100,
        kmeans=dict(n_clusters=2,n_users=100,inertia=k['inertia'],silhouette_score=k['silhouette_score'],
            cluster_sizes=k['cluster_sizes'],segments=k['cluster_id_to_segment'],
            ari_pairwise_mean=1.,ari_pairwise_min=1.,ari_pairwise_max=1.,n_seeds=20,n_pairs=190,
            profiles=profiles.to_dict(orient='records'),suitability='Für erste grobe Segmentierung im synthetischen Prototyp geeignet'),
        regression=dict(n_training_observations=1800,n_test_observations=400,**r,
            suitability='Nur eingeschränkt für synthetischen Prototyp geeignet; unverbindliche Niveauprognose'),
        baseline_comparison=b,current_week_diagnostics=diagnostics,
        diagnostic_scope='Post-hoc-Diagnose anhand bekannter Eingänge; keine Auswahl oder Nachbearbeitung einer Prognose',
        limitations=limits,real_user_production_validated=False,
        ap6_recommendation='Bedingte Freigabe zur regelbasierten Prototyp-Konzeption; keine produktive Freigabe',
        actual_iteration='AP 2: Data Understanding zurück zu Construct Data, Präferenzexponent 1,3 und erneute Qualitätsprüfung; V2 angenommen',
        future_iterations_status='Nur Vorschläge, nicht umgesetzt',
        source_sha256={path:baseline.prior.contract.sha256(root/path) for path in SOURCES})


def main():
    result=summarize()
    baseline.prior.contract.write_new_or_identical(ROOT/'outputs/tables/modeling_evaluation_summary.json',
        (json.dumps(result,ensure_ascii=False,sort_keys=True,indent=2)+'\n').encode())
    print(json.dumps(result['current_week_diagnostics'],ensure_ascii=False,indent=2))


if __name__=='__main__':main()
