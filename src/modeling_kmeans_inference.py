"""Schlanker AP-5.3a-Vertragskern: gespeicherte Transformation und predict, kein Fit.

Historiennachweise sind vorgelagerte bestätigte Angaben, kein automatischer Garmin-Audit.
"""
import json
import joblib
import numpy as np
import pandas as pd
from threadpoolctl import threadpool_limits
import modeling_kmeans_k_selection as base

FEATURES=base.FEATURES
ROOT=base.ROOT


def load_artifacts(root=ROOT):
    """Nur vertrauenswürdige lokale Projektartefakte; Hash ist kein Herkunftsbeweis."""
    meta=json.loads((root/'outputs/models/kmeans_final_metadata.json').read_text())
    params=json.loads((root/'outputs/models/kmeans_scaling_params.json').read_text())
    base.require(meta['data_version']==params['active_version']=='V2','Version widersprüchlich')
    base.require(meta['feature_order']==meta['feature_names']==params['feature_order']==FEATURES,
                 'Feature-Reihenfolge widersprüchlich')
    base.require(base.digest(root/'outputs/models/kmeans_final.joblib')==meta['model_sha256'],'Modellhash falsch')
    for path,sha in meta['source_sha256'].items():
        base.require(base.digest(root/path)==sha,f'Quellhash falsch: {path}')
    for i,f in enumerate(FEATURES):
        p=params['features'][f]
        base.require(np.isfinite([p['mean'],p['scale'],p['weight']]).all() and p['scale']>0,
                     'Skalierungsparameter ungültig')
        base.require(np.isclose(p['weight'],1 if i==0 else 1/np.sqrt(8),atol=1e-15,rtol=0),
                     'Gewichtung abweichend')
    model=joblib.load(root/'outputs/models/kmeans_final.joblib')
    base.require(model.get_params()==meta['parameters'] and model.n_clusters==2 and
                 model.n_features_in_==9 and list(model.feature_names_in_)==FEATURES,'Modellvertrag abweichend')
    base.require(np.allclose(model.cluster_centers_,meta['cluster_centers'],atol=1e-12,rtol=1e-12),
                 'Zentren widersprüchlich')
    mapping=meta['cluster_id_to_segment']
    base.require(set(mapping)=={'0','1'} and set(mapping.values())==
                 {'Geringere Trainingshäufigkeit','Höhere Trainingshäufigkeit'},'Segmentzuordnung ungültig')
    basis=meta['labeling_basis'];ordered=sorted(basis,key=lambda c:basis[c])
    base.require(basis[ordered[0]]<basis[ordered[1]] and mapping[ordered[0]]=='Geringere Trainingshäufigkeit',
                 'Segmentrangfolge widersprüchlich')
    return model,params,meta


def transform_saved(features,params):
    """Nur rohe gültige Aktivprofile; bereits skalierte Werte niemals hier übergeben."""
    base.require(list(features.columns)==FEATURES,'Exakte Feature-Reihenfolge erforderlich')
    base.require(all(pd.api.types.is_numeric_dtype(features[f]) and
                     not pd.api.types.is_bool_dtype(features[f]) for f in FEATURES),'Numerische Merkmale erforderlich')
    x=features.to_numpy(dtype=float)
    base.require(np.isfinite(x).all() and (x[:,0]>0).all(),'Ungültige aktive Merkmale')
    base.require(((x[:,1:]>=0)&(x[:,1:]<=1)).all() and
                 np.allclose(x[:,1:].sum(axis=1),1,atol=1e-10,rtol=0),'Ungültige Sportanteile')
    values=np.column_stack([(x[:,i]-params['features'][f]['mean'])/
        params['features'][f]['scale']*params['features'][f]['weight'] for i,f in enumerate(FEATURES)])
    base.require(np.isfinite(values).all(),'Transformation nicht endlich')
    return pd.DataFrame(values,columns=FEATURES,index=features.index)


def assign_profile(features,*,complete_weeks,records_complete,records_reliable,known_sports,artifacts):
    """Ein voraggregiertes Nutzerprofil; fehlende Nachweise werden nicht positiv angenommen.

    Statusausgabe enthält bei Ablehnung immer cluster_id=None und segment_label=None.
    """
    def rejected(status):return dict(status=status,cluster_id=None,segment_label=None)
    if type(complete_weeks) is not int or complete_weeks!=26:
        return rejected('insufficient_history')
    if records_complete is not True or records_reliable is not True:
        return rejected('incomplete_or_unverified_records')
    if known_sports is not True:return rejected('unknown_or_unverified_sports')
    if list(features)!=FEATURES:return rejected('invalid_features')
    try:
        frequency=features[FEATURES[0]]
        if isinstance(frequency,(bool,str)) or not np.isfinite(frequency) or frequency<0:
            return rejected('invalid_features')
        if frequency==0:
            if all(pd.isna(features[f]) for f in FEATURES[1:]):return rejected('inactive')
            return rejected('invalid_features')
        model,params,meta=artifacts
        transformed=transform_saved(pd.DataFrame([features]),params)
    except (TypeError,ValueError,OverflowError):
        return rejected('invalid_features')
    with threadpool_limits(limits=1):cluster=int(model.predict(transformed)[0])
    return dict(status='assigned',cluster_id=cluster,segment_label=meta['cluster_id_to_segment'][str(cluster)])


def audit_existing(root=ROOT):
    model,params,meta=load_artifacts(root)
    raw=pd.read_csv(root/'data/processed/kmeans_user_features.csv')
    scaled=pd.read_csv(root/'data/processed/kmeans_user_features_scaled.csv')
    saved=pd.read_csv(root/'data/processed/user_clusters.csv')
    base.validate_frame(scaled)
    base.require(raw.user_id.is_unique and saved.user_id.is_unique and len(raw)==len(saved)==100,
                 'Nutzerzahl/Eindeutigkeit falsch')
    base.require(raw.user_id.tolist()==scaled.user_id.tolist() and set(saved.user_id)==set(raw.user_id),
                 'Nutzerverknüpfung falsch')
    transformed=transform_saved(raw[FEATURES],params)
    base.require(np.allclose(transformed,scaled[FEATURES],atol=1e-10,rtol=1e-10),
                 'Gespeicherte Transformation abweichend')
    with threadpool_limits(limits=1):labels=model.predict(transformed)
    predicted=pd.DataFrame({'user_id':raw.user_id,'cluster_id':labels.astype('int64')})
    predicted['segment_label']=[meta['cluster_id_to_segment'][str(int(c))] for c in labels]
    pd.testing.assert_frame_equal(predicted.sort_values('user_id').reset_index(drop=True),
                                  saved.sort_values('user_id').reset_index(drop=True))
    counts={str(int(c)):int(n) for c,n in predicted.cluster_id.value_counts().items()}
    base.require(counts==meta['cluster_sizes'],'Clustergrößen widersprüchlich')
    means=raw.assign(cluster_id=labels).groupby('cluster_id')[FEATURES[0]].mean()
    base.require(all(np.isclose(means[int(c)],v,atol=1e-12) for c,v in meta['labeling_basis'].items()),
                 'Benennungsbasis widersprüchlich')
    return dict(status='bestanden',users=len(saved),clusters=counts,refit=False,
                transformed_matches_saved=True,assignments_match=True)


if __name__=='__main__':print(json.dumps(audit_existing(),ensure_ascii=False,indent=2,sort_keys=True))
