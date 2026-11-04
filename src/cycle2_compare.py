"""Frozen cycle-2 experiment. Run: python src/cycle2_compare.py.

Only training CSV and weekly history are read; no legacy test/model/results access.
Outputs are exclusively in cycle2 directories. Existing differing files are refused.
"""
import csv
import hashlib
import io
import json
import platform
import subprocess
from pathlib import Path

import numpy as np
import pandas as pd
import sklearn
from sklearn.linear_model import LinearRegression
from threadpoolctl import threadpool_limits

ROOT = Path(__file__).resolve().parents[1]
BASE = ['activities_current_week', 'avg_activities_last_4_weeks']
EXTRA = 'zero_weeks_last_4_weeks'
TARGET = 'activities_next_week'
FOLDS = [(1, 9, 10, 13), (2, 13, 14, 17), (3, 17, 18, 21)]
PARAMETERS = dict(fit_intercept=True, copy_X=True, tol=1e-6, n_jobs=None, positive=False)
SOURCES = {
    'data/processed/regression_train.csv': 'e984a547de12aca7d53ce908dd5051992bbd21aa83895a67bcd6fc0b541fb0b8',
    'data/processed/user_weekly_activities.csv': 'c34a7bd16d1cdc3e91388cc35b8c784afde0b53c1dbfdd24de97148350359b74',
}


def require(ok, message):
    if not ok:
        raise ValueError(message)


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def construct(train, history):
    """History contains only weeks 1..22; feature calculation accesses t-3..t."""
    train = train.copy().sort_values(['user_id', 'week_index']).reset_index(drop=True)
    require(list(train.columns) == ['user_id', 'week_index', 'week_start', 'week_end'] + BASE + [TARGET], 'Training schema')
    users = sorted(train.user_id.unique())
    require(len(users) == 100 and len(train) == 1800, 'Training size')
    require(not train.duplicated(['user_id', 'week_index']).any(), 'Duplicate training key')
    require(all(set(g.week_index) == set(range(4, 22)) for _, g in train.groupby('user_id')), 'Training weeks')
    require(not history.duplicated(['user_id', 'week_index']).any(), 'Duplicate history key')
    require(set(zip(history.user_id, history.week_index)) == {(u, t) for u in users for t in range(1, 23)}, 'History must be complete weeks 1..22')
    for frame in (train, history):
        start = pd.to_datetime(frame.week_start, format='%Y-%m-%d', errors='raise')
        end = pd.to_datetime(frame.week_end, format='%Y-%m-%d', errors='raise')
        expected = pd.Timestamp('2026-01-05') + pd.to_timedelta((frame.week_index - 1) * 7, unit='D')
        require((start == expected).all() and ((end-start).dt.days == 6).all(), 'Calendar mismatch')
    values = history.activities_count.to_numpy(dtype=float)
    require(np.isfinite(values).all() and (values >= 0).all() and (values <= 10).all() and (values % 1 == 0).all(), 'Invalid historical counts')
    require(np.isfinite(train[BASE + [TARGET]].to_numpy(dtype=float)).all(), 'Invalid training values')
    lookup = history.set_index(['user_id', 'week_index']).activities_count
    zeros = []
    for r in train.itertuples():
        window = [lookup.loc[(r.user_id, t)] for t in range(r.week_index-3, r.week_index+1)]
        require(r.activities_current_week == window[-1] and r.avg_activities_last_4_weeks == sum(window)/4, 'Legacy inputs differ')
        require(getattr(r, TARGET) == lookup.loc[(r.user_id, r.week_index+1)], 'Target mismatch')
        zeros.append(sum(v == 0 for v in window))
    train[EXTRA] = np.asarray(zeros, dtype=int)
    return train


def load(root=ROOT):
    for name, expected in SOURCES.items():
        require(digest(root/name) == expected, 'Source hash mismatch: ' + name)
    train = pd.read_csv(root/'data/processed/regression_train.csv')
    # The shared historical file also contains legacy test weeks. Discard them at
    # the input boundary, before any statistics, joins, features or fitting.
    with (root/'data/processed/user_weekly_activities.csv').open(newline='') as stream:
        rows = [r for r in csv.DictReader(stream) if int(r['week_index']) <= 22]
    history = pd.DataFrame(rows)
    for col in ['week_index', 'activities_count']:
        history[col] = pd.to_numeric(history[col], errors='raise')
    return construct(train, history)


def split(frame, spec):
    fold, last, first, end = spec
    training = frame[frame.week_index.between(4, last)].copy()
    validation = frame[frame.week_index.between(first, end)].copy()
    require(len(training) == (last-3)*100 and len(validation) == 400, 'Fold size')
    require(training.week_index.max()+1 <= validation.week_index.min(), 'Unavailable training label')
    require(set(training.user_id) == set(validation.user_id), 'Different users')
    return training, validation


def metrics(group):
    error = group.prediction.to_numpy() - group.actual.to_numpy()
    return dict(n=len(group), mae=float(np.abs(error).mean()), rmse=float(np.sqrt(np.mean(error**2))),
                mean_signed_error=float(error.mean()), negative_predictions=int((group.prediction < 0).sum()))


def evaluate(frame):
    predictions, models, folds = [], [], []
    for spec in FOLDS:
        fold, last, first, end = spec
        training, validation = split(frame, spec)
        folds.append(dict(fold=fold, train_input_weeks=[4,last], train_target_weeks=[5,last+1],
                          validation_input_weeks=[first,end], validation_target_weeks=[first+1,end+1],
                          train_rows=len(training), validation_rows=len(validation)))
        for name, features in [('persistence', None), ('linear_2', BASE), ('linear_3', BASE+[EXTRA])]:
            if features is None:
                predicted = validation.activities_current_week.to_numpy(dtype=float)
            else:
                x = training[features].astype(float)
                design = np.column_stack([np.ones(len(x)), x])
                require(np.linalg.matrix_rank(design) == len(features)+1, 'Rank deficient design')
                with threadpool_limits(limits=1):
                    model = LinearRegression(**PARAMETERS).fit(x, training[TARGET].astype(float))
                    predicted = model.predict(validation[features].astype(float))
                expected = np.linalg.lstsq(design, training[TARGET].to_numpy(dtype=float), rcond=None)[0]
                require(np.allclose(np.r_[model.intercept_, model.coef_], expected, rtol=1e-10, atol=1e-10), 'OLS solver mismatch')
                models.append(dict(fold=fold, model=name, features=features, parameters=PARAMETERS,
                                   intercept=float(model.intercept_), coefficients=model.coef_.tolist(),
                                   design_rank=int(np.linalg.matrix_rank(design)),
                                   design_condition_number=float(np.linalg.cond(design)),
                                   feature_correlations=x.corr().to_dict()))
            require(np.isfinite(predicted).all(), 'Nonfinite predictions')
            table = validation[['user_id','week_index','week_start','week_end',EXTRA]].copy()
            table['target_week'] = table.week_index+1
            table['actual'] = validation[TARGET]
            table['fold'], table['model'], table['prediction'] = fold, name, predicted
            table['error'] = table.prediction-table.actual
            table['absolute_error'] = abs(table.error)
            predictions.append(table)
    predictions = pd.concat(predictions, ignore_index=True)
    require(len(predictions) == 3600, 'Expected 1200 cases per procedure')
    summary = pd.DataFrame([dict(model=name, **metrics(g)) for name,g in predictions.groupby('model', sort=True)])
    by_fold = pd.DataFrame([dict(fold=int(fold), model=name, **metrics(g)) for (fold,name),g in predictions.groupby(['fold','model'],sort=True)])
    groups = []
    for name,g in predictions.groupby('model',sort=True):
        for label,mask in [('actual_zero',g.actual == 0), ('actual_positive',g.actual > 0)]:
            if mask.any(): groups.append(dict(model=name, grouping='actual_target', group=label, **metrics(g[mask])))
        for z,subset in g.groupby(EXTRA,sort=True):
            groups.append(dict(model=name, grouping=EXTRA, group=str(int(z)), **metrics(subset)))
    wide = predictions.pivot(index=['user_id','week_index'], columns='model', values='absolute_error')
    paired = wide.reset_index()
    paired['improvement_linear3_vs_linear2'] = paired.linear_2-paired.linear_3
    pooled = summary.set_index('model').mae
    fold_mae = by_fold.pivot(index='fold',columns='model',values='mae')
    wins = int((fold_mae.linear_3 < fold_mae.linear_2).sum())
    adopted = bool(pooled.linear_3 < pooled.linear_2 and wins >= 2)
    decision = dict(rule='Adopt linear_3 iff pooled MAE is strictly lower than linear_2 and MAE is strictly lower in at least 2/3 folds',
                    pooled_mae_improvement=float(pooled.linear_2-pooled.linear_3), winning_folds=wins,
                    adopt_extended=adopted, selected_structure='linear_3' if adopted else 'linear_2',
                    interpretation='Internal temporal validation of a post-hoc hypothesis; no independent test confirmation',
                    final_full_training_fit_performed=False)
    weekly = pd.DataFrame([dict(target_week=int(w), model=name, **metrics(g)) for (w,name),g in predictions.groupby(['target_week','model'],sort=True)])
    return predictions, summary, by_fold, pd.DataFrame(groups), paired, weekly, models, folds, decision


def json_bytes(value):
    return (json.dumps(value, ensure_ascii=False, sort_keys=True, indent=2, allow_nan=False)+'\n').encode()


def persist(root, payloads):
    # Preflight all paths before writing any artifact.
    for name, payload in payloads.items():
        path = root/name
        require('cycle2' in path.parts, 'Output outside cycle2')
        require(not path.exists() or path.read_bytes() == payload, 'Refuse differing output: '+name)
    for name,payload in payloads.items():
        path = root/name
        if not path.exists():
            path.parent.mkdir(parents=True,exist_ok=True)
            with path.open('xb') as stream: stream.write(payload)


def main(root=ROOT):
    frame = load(root)
    predictions, summary, folds_table, groups, paired, weekly, models, folds, decision = evaluate(frame)
    payloads = {}
    tables = {'data/processed/cycle2/regression_development.csv':frame,
              'outputs/cycle2/validation_predictions.csv':predictions,
              'outputs/cycle2/comparison.csv':summary,
              'outputs/cycle2/metrics_by_fold.csv':folds_table,
              'outputs/cycle2/zero_week_analysis.csv':groups,
              'outputs/cycle2/paired_errors.csv':paired,
              'outputs/cycle2/metrics_by_week.csv':weekly}
    for name,table in tables.items():
        payloads[name] = table.to_csv(index=False,lineterminator='\n',float_format='%.17g').encode()
    payloads['outputs/cycle2/models/fold_parameters.json'] = json_bytes(models)
    payloads['outputs/cycle2/validation_manifest.json'] = json_bytes(dict(folds=folds, history_window='t-3..t',
        target='t+1', frozen_model_within_validation_block=True, legacy_test_used=False, postprocessing='none'))
    payloads['outputs/cycle2/decision.json'] = json_bytes(decision)
    manifest = dict(source_sha256=SOURCES, code_sha256={str(Path(__file__).relative_to(ROOT)):digest(Path(__file__))},
        source_base_commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=root,text=True).strip(),
        software=dict(python=platform.python_version(),numpy=np.__version__,pandas=pd.__version__,sklearn=sklearn.__version__),
        numerical_threads=1, artifact_sha256={p:hashlib.sha256(v).hexdigest() for p,v in payloads.items()})
    payloads['outputs/cycle2/run_manifest.json'] = json_bytes(manifest)
    persist(root,payloads)
    for name,expected in SOURCES.items(): require(digest(root/name) == expected, 'Input changed')
    print(summary.to_string(index=False))
    print(folds_table.to_string(index=False))
    print(json.dumps(decision,ensure_ascii=False,indent=2))


if __name__ == '__main__':
    main()
