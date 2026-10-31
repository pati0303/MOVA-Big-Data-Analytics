"""AP 5.4: eine globale OLS-Regression nur auf regression_train.csv.

Keine Testvorhersagen, Gütebewertung, Skalierung oder Hyperparameterwahl.
"""
import hashlib
import io
import json
from pathlib import Path
import platform
import joblib
import numpy as np
import pandas as pd
import sklearn
from sklearn.linear_model import LinearRegression
from threadpoolctl import threadpool_limits

ROOT=Path(__file__).resolve().parents[1]
FEATURES=['activities_current_week','avg_activities_last_4_weeks']
TARGET='activities_next_week'
COLUMNS=['user_id','week_index','week_start','week_end']+FEATURES+[TARGET]
TRAIN='data/processed/regression_train.csv'
MODEL='outputs/models/regression_linear.joblib'
METADATA='outputs/models/regression_linear_metadata.json'
COEFFICIENTS='outputs/tables/regression_linear_coefficients.csv'
PARAMETERS=dict(fit_intercept=True,copy_X=True,tol=1e-6,n_jobs=None,positive=False)


def require(condition,message):
    if not condition:raise ValueError(message)


def sha256(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def validate_train(frame):
    require(list(frame.columns)==COLUMNS,'Unzulässiges Trainingsschema')
    require(len(frame)==1800 and not frame.isna().any().any(),'Zeilenzahl oder fehlende Werte')
    require(frame.user_id.nunique()==100 and frame.user_id.astype(str).str.fullmatch(r'U\d{3}').all(),
            'Nutzer ungültig')
    require(not frame.duplicated(['user_id','week_index']).any(),'Doppelte Nutzerwoche')
    require(all(len(g)==18 and set(g.week_index)==set(range(4,22)) for _,g in frame.groupby('user_id')),
            'Trainingswochen unvollständig oder außerhalb 4–21')
    values=frame[FEATURES+[TARGET]].to_numpy(dtype=float)
    require(np.isfinite(values).all() and (values>=0).all(),'Nicht endliche oder negative Werte')
    require(np.equal(values[:,[0,2]]%1,0).all(),'Counts nicht ganzzahlig')
    require(np.equal(values[:,1]*4%1,0).all(),'Vierwochenmittel nicht in Viertelschritten')
    start=pd.to_datetime(frame.week_start,format='%Y-%m-%d',errors='raise')
    end=pd.to_datetime(frame.week_end,format='%Y-%m-%d',errors='raise')
    expected=pd.Timestamp('2026-01-05')+pd.to_timedelta((frame.week_index-1)*7,unit='D')
    require((start==expected).all() and ((end-start).dt.days==6).all(),'Kalenderzuordnung ungültig')
    x=frame[FEATURES].astype('float64').copy()
    y=frame[TARGET].astype('float64').copy()
    require(np.linalg.matrix_rank(np.column_stack([np.ones(len(x)),x]))==3,'Designmatrix rangdefizient')
    return x,y


def load_training(root=ROOT):
    manifest=json.loads((root/'documentation/regression_split_manifest.json').read_text())
    active=json.loads((root/'documentation/active_data_version.json').read_text())
    require(manifest['active_version']==active['active_version']=='V2','Keine aktive V2')
    require(manifest['model_input_features']==FEATURES and manifest['target']==TARGET,'Modellrollen abweichend')
    require(manifest['train_input_weeks']==list(range(4,22)) and
            manifest['train_target_weeks']==list(range(5,23)),'Splitvertrag abweichend')
    require(sha256(root/TRAIN)==manifest['output_sha256'][TRAIN],'Trainingshash abweichend')
    frame=pd.read_csv(root/TRAIN)
    x,y=validate_train(frame)
    return frame,x,y,manifest


def train(x,y):
    require(list(x.columns)==FEATURES and len(x)==len(y)==1800 and y.name==TARGET,'Trainingsrollen falsch')
    with threadpool_limits(limits=1):model=LinearRegression(**PARAMETERS).fit(x,y)
    require(model.get_params()==PARAMETERS,'Modellparameter abweichend')
    require(list(model.feature_names_in_)==FEATURES and model.n_features_in_==2,'Feature-Vertrag falsch')
    require(np.isfinite(model.coef_).all() and np.isfinite(model.intercept_),'Ungültige Modellparameter')
    # Unabhängige Lösung der OLS-Normalaufgabe mittels numpy.linalg.lstsq, nur Training.
    design=np.column_stack([np.ones(len(x)),x.to_numpy()])
    expected=np.linalg.lstsq(design,y.to_numpy(),rcond=None)[0]
    require(np.allclose(np.r_[model.intercept_,model.coef_],expected,atol=1e-12,rtol=1e-12),
            'Unabhängige OLS-Kontrolle abweichend')
    return model


def write_new_or_identical(path,payload):
    if path.exists():require(path.read_bytes()==payload,f'Abweichende Ausgabe nicht überschrieben: {path}')
    else:
        path.parent.mkdir(parents=True,exist_ok=True)
        with path.open('xb') as f:f.write(payload)


def main():
    paths=[p for d in ['data','src','tests','documentation','outputs'] for p in (ROOT/d).rglob('*')
           if p.is_file() and '__pycache__' not in p.parts]
    before={p:sha256(p) for p in paths}
    frame,x,y,manifest=load_training()
    model=train(x,y)
    buffer=io.BytesIO();joblib.dump(model,buffer,compress=3);payload=buffer.getvalue()
    meta=dict(data_version='V2',training_file=TRAIN,training_sha256=sha256(ROOT/TRAIN),
        split_manifest_sha256=sha256(ROOT/'documentation/regression_split_manifest.json'),
        n_training_rows=len(frame),n_users=int(frame.user_id.nunique()),
        train_input_weeks=[4,21],train_target_weeks=[5,22],
        train_target_date_range=manifest['train_target_date_range'],
        feature_names=FEATURES,feature_order=FEATURES,target=TARGET,excluded_metadata=COLUMNS[:4],
        algorithm='sklearn.linear_model.LinearRegression',
        parameters=model.get_params(),intercept=float(model.intercept_),
        coefficients=dict(zip(FEATURES,map(float,model.coef_))),rank=int(model.rank_),
        singular_values=model.singular_.tolist(),scaling='none',model_file=MODEL,
        model_sha256=hashlib.sha256(payload).hexdigest(),
        software=dict(python=platform.python_version(),scikit_learn=sklearn.__version__,
                      numpy=np.__version__,pandas=pd.__version__,joblib=joblib.__version__),
        scope='Globales Modell für nächste Wochenaktivitätszahl über alle Sportarten; synthetische V2',
        test_data_used_for_training=False,test_evaluation_performed=False,
        evaluation_stage='AP 5.5: rollierende Einwochenprognose mit unverändertem Modell',
        numerical_threads=1)
    write_new_or_identical(ROOT/MODEL,payload)
    write_new_or_identical(ROOT/METADATA,(json.dumps(meta,ensure_ascii=False,sort_keys=True,indent=2)+'\n').encode())
    table=pd.DataFrame({'term':['intercept']+FEATURES,
                        'coefficient':np.r_[model.intercept_,model.coef_]})
    write_new_or_identical(ROOT/COEFFICIENTS,table.to_csv(index=False,lineterminator='\n',float_format='%.17g').encode())
    # Ausschließlich das in diesem Projekt erzeugte vertrauenswürdige Artefakt laden.
    loaded=joblib.load(ROOT/MODEL)
    require(loaded.get_params()==model.get_params(),'Reload-Parameter abweichend')
    np.testing.assert_array_equal(loaded.coef_,model.coef_)
    require(loaded.intercept_==model.intercept_,'Reload-Intercept abweichend')
    saved_meta=json.loads((ROOT/METADATA).read_text())
    require(saved_meta==meta,'Gespeicherte Metadaten abweichend')
    require(list(loaded.feature_names_in_)==saved_meta['feature_order'],'Reload-Reihenfolge abweichend')
    with threadpool_limits(limits=1):
        np.testing.assert_array_equal(loaded.predict(x),model.predict(x))
    # Ausschließlich Trainingsvorhersagen zur technischen Persistenzprüfung, kein Gütemaß.
    require(all(sha256(p)==sha for p,sha in before.items()),'Bestehende Datei verändert')
    print(json.dumps(meta,ensure_ascii=False,sort_keys=True,indent=2))


if __name__=='__main__':main()
