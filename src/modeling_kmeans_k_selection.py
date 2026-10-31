"""AP 5.1: explorative k-Auswahl; keine persistierten Modelle oder Nutzerlabels.

Aufruf: python src/modeling_kmeans_k_selection.py
Nur die bereits standardisierten und gewichteten AP-4-Werte gehen in KMeans ein.
"""
import csv
import hashlib
import io
import json
import os
from pathlib import Path
import platform
import warnings

ROOT = Path(__file__).resolve().parents[1]
os.environ.setdefault('MPLCONFIGDIR', str(ROOT / 'work/matplotlib'))
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import sklearn
from sklearn.cluster import KMeans
from sklearn.metrics import silhouette_score
from threadpoolctl import threadpool_limits

FEATURES = ['avg_activities_per_week'] + ['share_' + s for s in
    ['running', 'cycling', 'strength', 'swimming', 'walking', 'hiking', 'tennis', 'padel']]
PARAMETERS = dict(init='k-means++', random_state=42, n_init=20, max_iter=300,
                  algorithm='lloyd', tol=1e-4)
COLUMNS = ['k', 'inertia', 'silhouette_score', 'n_iterations',
           'min_cluster_size', 'max_cluster_size']
TOLERANCE = 1e-10
SMALL_CLUSTER = 5  # Explorative fachliche Warnschwelle: weniger als 5 von 100 Nutzern.


def require(condition, message):
    if not condition:
        raise ValueError(message)


def digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def validate_frame(frame):
    require(list(frame.columns) == ['user_id'] + FEATURES, 'Unerlaubtes Eingabeschema')
    require(len(frame) == 100, 'Genau 100 Nutzer erforderlich')
    ids = frame['user_id']
    require(ids.notna().all() and ids.astype(str).str.strip().ne('').all()
            and ids.is_unique, 'Fehlende oder doppelte Nutzer')
    x = frame[FEATURES].to_numpy(dtype=np.float64, copy=True)
    require(x.shape == (100, 9) and np.isfinite(x).all(), 'Ungültige Eingabewerte')
    return x


def load_input(root=ROOT):
    params = json.loads((root/'outputs/models/kmeans_scaling_params.json').read_text())
    manifest = json.loads((root/'documentation/active_data_version.json').read_text())
    require(params['active_version'] == manifest['active_version'] == 'V2', 'V2 erforderlich')
    require(params['feature_order'] == FEATURES, 'Merkmalsreihenfolge abweichend')
    refs = {**manifest['sha256'], **params['input_sha256'],
            'data/processed/kmeans_user_features_scaled.csv': params['output_csv_sha256']}
    for path, expected in refs.items():
        require(digest(root/path) == expected, f'Quellhash abweichend: {path}')
    frame = pd.read_csv(root/'data/processed/kmeans_user_features_scaled.csv')
    x = validate_frame(frame)
    raw = pd.read_csv(root/'data/processed/kmeans_user_features.csv')
    require(raw['user_id'].tolist() == frame['user_id'].tolist() == params['fit_user_ids'],
            'Nutzerzuordnung abweichend')
    # Nur Kontrollrechnung mit gespeicherten Parametern; kein Fit, keine Änderung an X.
    expected = np.column_stack([(raw[f].to_numpy()-params['features'][f]['mean']) /
        params['features'][f]['scale'] * params['features'][f]['weight'] for f in FEATURES])
    require(np.allclose(x, expected, atol=1e-10, rtol=1e-10), 'AP-4-Transformation abweichend')
    return x


def evaluate(x, ks=range(1, 9)):
    x = np.array(x, dtype=np.float64, copy=True)
    require(x.shape == (100, 9) and np.isfinite(x).all(), 'Ungültige Modellmatrix')
    ks = list(ks)
    require(bool(ks) and ks == sorted(set(ks)) and
            all(type(k) is int and 1 <= k <= 8 for k in ks), 'Ungültige k-Werte')
    rows, details = [], []
    previous = None
    with threadpool_limits(limits=1):
        for k in ks:
            with warnings.catch_warnings(record=True) as caught:
                warnings.simplefilter('always')
                model = KMeans(n_clusters=k, **PARAMETERS).fit(x)
            labels = model.labels_
            unique, counts = np.unique(labels, return_counts=True)
            require(len(labels) == 100 and int(counts.sum()) == 100, 'Zuordnungszahl falsch')
            require(np.isfinite(model.inertia_) and model.inertia_ >= 0, 'Inertia ungültig')
            score = float(silhouette_score(x, labels, metric='euclidean')) if 1 < len(unique) < 100 else None
            require(score is None or -1 <= score <= 1, 'Silhouette ungültig')
            notes = [str(w.message) for w in caught]
            if len(unique) != k:
                notes.append('Anzahl entstandener Cluster weicht von k ab')
            if k > 1 and counts.min() < SMALL_CLUSTER:
                notes.append('Sehr kleiner Cluster (<5 Nutzer)')
            if model.n_iter_ >= PARAMETERS['max_iter']:
                notes.append('Iterationsgrenze erreicht; Konvergenz prüfen')
            if previous is not None and model.inertia_ > previous + TOLERANCE:
                notes.append('Inertia-Anstieg: lokale Optimierung trotz 20 Starts; keine Werte korrigiert')
            previous = model.inertia_
            rows.append(dict(k=k, inertia=float(model.inertia_), silhouette_score=score,
                n_iterations=int(model.n_iter_), min_cluster_size=int(counts.min()) if k > 1 else None,
                max_cluster_size=int(counts.max()) if k > 1 else None))
            details.append(dict(k=k, n_clusters=len(unique), sizes=dict(zip(map(int,unique),map(int,counts))),
                                notes=notes))
    return rows, details


def csv_bytes(rows):
    buffer = io.StringIO(newline='')
    writer = csv.DictWriter(buffer, fieldnames=COLUMNS, lineterminator='\n')
    writer.writeheader()
    writer.writerows(rows)
    return buffer.getvalue().encode('utf-8')


def write_identical_or_new(path, payload):
    if path.exists():
        require(path.read_bytes() == payload, f'Bestehende Ausgabe abweichend: {path}')
    else:
        path.parent.mkdir(parents=True, exist_ok=True)
        with path.open('xb') as stream:
            stream.write(payload)


def figures(rows):
    for name, key, title, ylabel in [
        ('kmeans_elbow.png', 'inertia', 'MOVA · Elbow-Analyse', 'Inertia'),
        ('kmeans_silhouette.png', 'silhouette_score', 'MOVA · Silhouette-Analyse', 'Silhouette-Score')]:
        selected = [r for r in rows if r[key] is not None]
        with plt.rc_context({'font.family':'DejaVu Sans', 'font.size':11}):
            fig, ax = plt.subplots(figsize=(8, 4.8), layout='constrained')
            ax.plot([r['k'] for r in selected], [r[key] for r in selected],
                    marker='o', color='#176b87', linewidth=2)
            ax.set(title=title, xlabel='Anzahl Cluster k', ylabel=ylabel,
                   xticks=[r['k'] for r in selected])
            ax.grid(alpha=.25)
            ax.spines[['top','right']].set_visible(False)
            fig.suptitle('V2 · 100 Nutzer · neun vorbereitete Eingangsmerkmale', fontsize=10)
            buffer = io.BytesIO()
            fig.savefig(buffer, format='png', dpi=180, metadata={'Software':'MOVA AP 5.1'})
            plt.close(fig)
            write_identical_or_new(ROOT/'outputs/figures'/name, buffer.getvalue())


def main():
    # Alle vorhandenen versionierten Daten/Skripte und Dokumentationen bleiben unverändert.
    paths = [p for folder in ['data','src','documentation','outputs/models']
             for p in (ROOT/folder).rglob('*') if p.is_file() and '__pycache__' not in p.parts]
    before = {p:digest(p) for p in paths}
    x = load_input()
    rows, details = evaluate(x)
    write_identical_or_new(ROOT/'outputs/tables/kmeans_k_selection.csv', csv_bytes(rows))
    figures(rows)
    require(all(digest(p) == sha for p,sha in before.items()), 'Vorhandene Datei verändert')
    print(json.dumps(dict(software=dict(python=platform.python_version(), sklearn=sklearn.__version__,
        numpy=np.__version__, pandas=pd.__version__, matplotlib=matplotlib.__version__),
        parameters=PARAMETERS, threads=1, rows=rows, details=details), indent=2, ensure_ascii=False))


if __name__ == '__main__':
    main()
