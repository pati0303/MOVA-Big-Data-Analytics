"""AP 5.3: finales K-Means für synthetische V2, k=2 nach Teamentscheidung.

Aufruf: python src/modeling_kmeans_final.py
Keine Skalierung: Modell erwartet bereits nach AP 4 transformierte neun Merkmale.
Joblib ausschließlich aus vertrauenswürdigen Projektquellen laden.
"""
import hashlib
import io
import json
import platform
from pathlib import Path
import joblib
import numpy as np
import pandas as pd
import sklearn
from sklearn.cluster import KMeans
from sklearn.metrics import silhouette_score
from threadpoolctl import threadpool_limits
import modeling_kmeans_k_selection as base

ROOT = base.ROOT
FEATURES = base.FEATURES
PROFILE_FEATURES = [FEATURES[0], 'avg_duration_per_week', 'sport_diversity'] + FEATURES[1:]
PARAMETERS = {**base.PARAMETERS, 'n_clusters':2}
LOWER = 'Geringere Trainingshäufigkeit'
HIGHER = 'Höhere Trainingshäufigkeit'
MODEL_PATH = 'outputs/models/kmeans_final.joblib'
METADATA_PATH = 'outputs/models/kmeans_final_metadata.json'


def csv_bytes(frame):
    return frame.to_csv(index=False, lineterminator='\n', float_format='%.17g').encode('utf-8')


def describe_clusters(scaled, raw, labels):
    """Benennung nach gemessener Häufigkeit; technische IDs sind keine Rangfolge."""
    base.validate_frame(scaled)
    base.require(list(raw.columns) == ['user_id']+FEATURES+['avg_duration_per_week','sport_diversity'],
                 'Unerlaubtes Profilschema')
    base.require(len(raw)==100 and raw.user_id.notna().all() and raw.user_id.is_unique and
                 set(raw.user_id)==set(scaled.user_id), 'Nutzerverknüpfung ungültig')
    base.require(np.isfinite(raw[PROFILE_FEATURES].to_numpy(dtype=float)).all(), 'Profilwerte ungültig')
    labels=np.asarray(labels)
    base.require(labels.shape==(100,) and np.issubdtype(labels.dtype,np.integer) and
                 set(labels)=={0,1}, 'Genau zwei vollständige Cluster erforderlich')
    assignments=pd.DataFrame({'user_id':scaled.user_id.to_numpy(),'cluster_id':labels.astype(np.int64)})
    joined=assignments.merge(raw,on='user_id',how='inner',validate='one_to_one')
    base.require(len(joined)==100,'Nutzer beim Join verloren')
    frequencies=joined.groupby('cluster_id')[FEATURES[0]].mean().sort_values()
    base.require(frequencies.iloc[0] < frequencies.iloc[1], 'Keine eindeutige Häufigkeitsrangfolge')
    mapping={int(frequencies.index[0]):LOWER,int(frequencies.index[1]):HIGHER}
    assignments['segment_label']=assignments.cluster_id.map(mapping)
    profiles=[]
    for cluster,group in joined.groupby('cluster_id',sort=True):
        means=group[PROFILE_FEATURES].mean()
        top=sorted(FEATURES[1:],key=lambda f:(-means[f],f))[:3]
        profiles.append(dict(cluster_id=int(cluster),segment_label=mapping[int(cluster)],n_users=len(group),
            **{f:float(means[f]) for f in PROFILE_FEATURES},
            top_3_sports=' / '.join(f.removeprefix('share_') for f in top)))
    return assignments, pd.DataFrame(profiles), mapping


def validate_parameters(model):
    for name,value in PARAMETERS.items():
        base.require(model.get_params()[name]==value,f'Modellparameter abweichend: {name}')
    base.require(model.n_features_in_==9 and list(model.feature_names_in_)==FEATURES,
                 'Modellmerkmale abweichend')


def train(scaled, raw, expected_x):
    x=base.validate_frame(scaled)
    base.require(np.array_equal(x,expected_x),'Trainingsmatrix nicht identisch zu AP-4-Eingabe')
    matrix=scaled[FEATURES].copy()
    with threadpool_limits(limits=1):
        model=KMeans(**PARAMETERS).fit(matrix)
        labels=model.predict(matrix)
        score=float(silhouette_score(matrix,labels,metric='euclidean'))
    validate_parameters(model)
    base.require(np.array_equal(labels,model.labels_),'Fit-/Predict-Zuordnung abweichend')
    base.require(sorted(np.bincount(labels).tolist())==[43,57], 'Clustergrößen abweichend')
    base.require(np.isfinite(model.inertia_) and model.inertia_>=0 and -1<=score<=1,'Kennzahlen ungültig')
    assignments,profiles,mapping=describe_clusters(scaled,raw,labels)
    return model,score,assignments,profiles,mapping


def metadata(model,score,profiles,mapping,payload,root=ROOT):
    inputs=['data/processed/kmeans_user_features_scaled.csv','data/processed/kmeans_user_features.csv',
            'outputs/models/kmeans_scaling_params.json']
    references=['outputs/tables/kmeans_k_selection.csv','outputs/tables/kmeans_candidate_comparison.csv',
                'outputs/tables/kmeans_candidate_profiles.csv']
    return dict(data_version='V2',input_file=inputs[0],input_sha256=base.digest(root/inputs[0]),
        source_sha256={p:base.digest(root/p) for p in inputs},
        selection_evidence_sha256={p:base.digest(root/p) for p in references},
        feature_names=FEATURES,feature_order=FEATURES,n_users=100,n_clusters=2,
        parameters=model.get_params(),software=dict(python=platform.python_version(),
            scikit_learn=sklearn.__version__,numpy=np.__version__,pandas=pd.__version__,
            joblib=joblib.__version__,matplotlib=base.matplotlib.__version__),
        n_iterations=int(model.n_iter_),cluster_centers=model.cluster_centers_.tolist(),
        cluster_center_space='AP-4-standardisierte und gewichtete Koordinaten; feature_order beachten',
        inertia=float(model.inertia_),silhouette_score=score,silhouette_metric='euclidean',
        cluster_sizes={str(int(r.cluster_id)):int(r.n_users) for r in profiles.itertuples()},
        cluster_id_to_segment={str(k):v for k,v in sorted(mapping.items())},
        labeling_rule='Nach unskalierter mittlerer avg_activities_per_week aufsteigend; Gleichstand führt zum Abbruch',
        labeling_basis={str(int(r.cluster_id)):float(r.avg_activities_per_week) for r in profiles.itertuples()},
        selection_decision='Empirisch begründete Teamentscheidung: k=2 nach AP 5.1/5.2; gültig für erste synthetische MOVA-V2',
        model_file=MODEL_PATH,model_sha256=hashlib.sha256(payload).hexdigest(),
        input_contract='Bereits gemäß gespeicherten AP-4-Parametern standardisierte und gewichtete Features; kein Refit und keine erneute Gewichtung',
        scope='Deskriptive Segmentierung von 100 synthetischen V2-Nutzern; keine belegte Generalisierbarkeit',
        segment_semantics='Relative Trainingshäufigkeit, keine Aussagen zu Fitness, Erfahrung oder Gesundheit',
        source_basis_commit='1b26533d2ceea30478577bd519244c245dd3e558',numerical_threads=1)


def verify_saved(root,scaled,expected_assignments):
    """Nur das in diesem vertrauenswürdigen Projekt erzeugte Artefakt laden.

    SHA-256 prüft Konsistenz, keine Authentizität fremder Joblib-Dateien.
    """
    meta=json.loads((root/METADATA_PATH).read_text())
    base.require(base.digest(root/MODEL_PATH)==meta['model_sha256'],'Modellhash abweichend')
    base.require(meta['feature_order']==FEATURES and meta['parameters']==KMeans(**PARAMETERS).get_params(),
                 'Metadatenparameter abweichend')
    model=joblib.load(root/MODEL_PATH)
    validate_parameters(model)
    base.require(model.get_params()==meta['parameters'],'Gespeicherte Modellparameter inkonsistent')
    np.testing.assert_array_equal(model.cluster_centers_,np.asarray(meta['cluster_centers']))
    base.require(model.inertia_==meta['inertia'] and model.n_iter_==meta['n_iterations'],
                 'Gespeicherte Modellkennzahlen inkonsistent')
    with threadpool_limits(limits=1):
        labels=model.predict(scaled[FEATURES])
    base.require(np.array_equal(labels,expected_assignments.cluster_id.to_numpy()),'Reload-Zuordnung abweichend')
    restored=[meta['cluster_id_to_segment'][str(int(c))] for c in labels]
    base.require(restored==expected_assignments.segment_label.tolist(),'Segmentzuordnung inkonsistent')
    exported=pd.read_csv(root/'data/processed/user_clusters.csv')
    pd.testing.assert_frame_equal(exported,expected_assignments)
    return model


def save_figure(fig,name):
    buffer=io.BytesIO()
    fig.savefig(buffer,format='png',dpi=180,metadata={'Software':'MOVA AP 5.3'})
    base.plt.close(fig)
    base.write_identical_or_new(ROOT/'outputs/figures'/name,buffer.getvalue())


def render_figures(profiles):
    # Darstellung in fachlicher Reihenfolge statt impliziter ID-Semantik.
    rows=profiles.set_index('segment_label').loc[[LOWER,HIGHER]]
    names=['Geringere\nTrainingshäufigkeit','Höhere\nTrainingshäufigkeit']
    colors=['#176b87','#c56a22']
    plt=base.plt
    with plt.rc_context({'font.family':'DejaVu Sans','font.size':11}):
        fig,ax=plt.subplots(figsize=(7,4.5),layout='constrained')
        ax.bar(names,rows.n_users,color=colors)
        ax.set(ylabel='Anzahl Nutzer',ylim=(0,65),title='MOVA · Nutzer je Segment (V2)')
        for i,v in enumerate(rows.n_users):ax.text(i,v,f'{v} ({v} %)',ha='center',va='bottom')
        save_figure(fig,'kmeans_final_cluster_sizes.png')
        fig,axes=plt.subplots(1,3,figsize=(12,4.5),layout='constrained')
        for ax,(field,title,limit) in zip(axes,[('avg_activities_per_week','Aktivitäten / Woche',5),
            ('avg_duration_per_week','Minuten / Woche',300),('sport_diversity','Sportartenvielfalt',8)]):
            values=rows[field]
            ax.bar(names,values,color=colors)
            ax.set(title=title,ylim=(0,limit),ylabel='Mittelwert je Nutzer')
            ax.tick_params(axis='x',labelsize=9)
            for i,v in enumerate(values):ax.text(i,v,f'{v:.2f}',ha='center',va='bottom')
        fig.suptitle('MOVA · Clusterprofile · k=2 · 100 synthetische Nutzer')
        save_figure(fig,'kmeans_final_cluster_profiles.png')
        fig,ax=plt.subplots(figsize=(10,5),layout='constrained')
        positions=np.arange(8)
        for i,(_,row) in enumerate(rows.iterrows()):
            bars=ax.bar(positions+(i-.5)*.36,row[FEATURES[1:]].to_numpy(dtype=float)*100,
                        width=.36,color=colors[i],label=row.name)
            ax.bar_label(bars,fmt='%.1f',fontsize=9,padding=2)
        ax.set(xticks=positions,xticklabels=[f.removeprefix('share_').capitalize() for f in FEATURES[1:]],
            ylabel='Mittlerer Sportanteil je Nutzer (%)',ylim=(0,27),title='MOVA · Sportmix nach Segment (V2)')
        ax.legend(loc='upper right',fontsize=9)
        ax.grid(axis='y',alpha=.2)
        save_figure(fig,'kmeans_final_sport_mix.png')


def main():
    paths=[p for folder in ['data','src','tests','documentation','outputs']
           for p in (ROOT/folder).rglob('*') if p.is_file() and '__pycache__' not in p.parts]
    before={p:base.digest(p) for p in paths}
    x=base.load_input()
    scaled=pd.read_csv(ROOT/'data/processed/kmeans_user_features_scaled.csv')
    raw=pd.read_csv(ROOT/'data/processed/kmeans_user_features.csv')
    model,score,assignments,profiles,mapping=train(scaled,raw,x)
    previous=pd.read_csv(ROOT/'outputs/tables/kmeans_k_selection.csv').set_index('k').loc[2]
    base.require(np.isclose(score,previous.silhouette_score,atol=1e-12,rtol=1e-12) and
                 np.isclose(model.inertia_,previous.inertia,atol=1e-12,rtol=1e-12), 'AP-5.1-Kennzahlen abweichend')
    candidates=pd.read_csv(ROOT/'outputs/tables/kmeans_candidate_profiles.csv')
    for row in profiles.itertuples():
        prior=candidates[(candidates.k==2)&(candidates.candidate_cluster==row.cluster_id)].iloc[0]
        for feature in PROFILE_FEATURES+['n_users']:
            base.require(np.isclose(getattr(row,feature),prior[feature],atol=1e-12,rtol=1e-12),
                         'AP-5.2-Profil abweichend')
    buffer=io.BytesIO();joblib.dump(model,buffer,compress=3);payload=buffer.getvalue()
    meta=metadata(model,score,profiles,mapping,payload)
    base.write_identical_or_new(ROOT/MODEL_PATH,payload)
    base.write_identical_or_new(ROOT/METADATA_PATH,(json.dumps(meta,ensure_ascii=False,sort_keys=True,indent=2)+'\n').encode('utf-8'))
    base.write_identical_or_new(ROOT/'data/processed/user_clusters.csv',csv_bytes(assignments))
    base.write_identical_or_new(ROOT/'outputs/tables/kmeans_final_cluster_profiles.csv',csv_bytes(profiles))
    verify_saved(ROOT,scaled,assignments)
    render_figures(profiles)
    base.require(all(base.digest(p)==sha for p,sha in before.items()),'Bestehende Datei verändert')
    print(json.dumps(dict(n_users=len(assignments),parameters=model.get_params(),
        inertia=float(model.inertia_),silhouette_score=score,n_iterations=int(model.n_iter_),
        cluster_sizes=meta['cluster_sizes'],segment_mapping=meta['cluster_id_to_segment'],
        model_sha256=meta['model_sha256'],reload_verified=True),ensure_ascii=False,indent=2,sort_keys=True))
    print(profiles.to_string(index=False))


if __name__=='__main__':main()
