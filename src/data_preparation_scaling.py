"""AP 4.4: StandardScaler und feste Sportmixgewichtung; kein K-Means-Fit.

Aufruf: python src/data_preparation_scaling.py
Abhängigkeiten: numpy, scikit-learn; Versionen werden in den Parametern gespeichert.
"""
import csv
import io
import json
import platform
import sys
from pathlib import Path

import numpy as np
import sklearn
from sklearn.preprocessing import StandardScaler

from data_preparation_selection import QualityError, read_csv, require, sha256
from data_preparation_kmeans import FEATURE_COLUMNS, MODEL_FEATURES

ROOT = Path(__file__).resolve().parents[1]
INPUT_HASH = 'bb6b0c4e9307ab286f9f6e76d04b9b1446a9ab322e31784c8883a6a596ca7a28'
OUTPUT_COLUMNS = ['user_id'] + MODEL_FEATURES
TOL = 1e-10
WEIGHT = 1 / np.sqrt(8)


def assert_close(actual, expected, label):
    require(np.allclose(actual, expected, atol=TOL, rtol=TOL), label)


def transform_saved(rows, params):
    """Neue berechtigte Profile mit gespeicherten Parametern transformieren, ohne Fit.

    Die Positivliste bestimmt unabhängig von der Reihenfolge eingehender Felder X.
    Inaktive Nutzer mit undefinierten Sportanteilen vorher separat ausweisen.
    """
    require(params['feature_order'] == MODEL_FEATURES, 'Parameter-Merkmalsreihenfolge abweichend')
    x = np.array([[float(row[name]) for name in params['feature_order']] for row in rows])
    require(x.ndim == 2 and x.shape[1] == 9 and np.isfinite(x).all(), 'Ungültige neue Profile')
    means = np.array([params['features'][name]['mean'] for name in MODEL_FEATURES])
    scales = np.array([params['features'][name]['scale'] for name in MODEL_FEATURES])
    factors = np.array([params['features'][name]['weight'] for name in MODEL_FEATURES])
    require(np.isfinite(scales).all() and (scales > 0).all(), 'Ungültige Skalenparameter')
    result = ((x - means) / scales) * factors
    require(np.isfinite(result).all(), 'Nicht endliche Transformation')
    return result


def fit_scale(x):
    """Schritte 4–6: Fit nur auf berechtigten Profilen, danach Sportmix gewichten."""
    require(x.ndim == 2 and x.shape[1] == 9 and len(x) > 0 and np.isfinite(x).all(),
            'Ungültige Fitmatrix')
    scaler = StandardScaler(with_mean=True, with_std=True)
    scaler.fit(x)
    z = scaler.transform(x)
    factors = np.array([1.0] + [float(WEIGHT)] * 8)
    weighted = z * factors
    return scaler, z, weighted


def validate(x, scaler, z, weighted):
    """Schritt 7: Populationseigenschaften und Inversentransformation prüfen."""
    require(np.isfinite(z).all() and np.isfinite(weighted).all(), 'NaN/Inf nach Skalierung')
    assert_close(z.mean(axis=0), np.zeros(9), 'Standardisierte Mittelwerte nicht 0')
    assert_close(weighted.mean(axis=0), np.zeros(9), 'Gewichtete Mittelwerte nicht 0')
    constant = np.ptp(x, axis=0) == 0
    # StandardScaler setzt auch numerisch ununterscheidbare Konstanten auf scale_=1.
    eps = np.finfo(np.float64).eps
    near_constant = scaler.var_ <= len(x) * eps * scaler.var_ + (len(x) * scaler.mean_ * eps) ** 2
    ordinary = ~near_constant
    assert_close(z.var(axis=0)[ordinary], np.ones(ordinary.sum()), 'Varianz vor Gewichtung falsch')
    target = np.array([1.0] + [1/8] * 8)
    assert_close(weighted.var(axis=0)[ordinary], target[ordinary], 'Varianz nach Gewichtung falsch')
    if constant.any():
        require((scaler.scale_[constant] == 1).all(), 'Konstante nicht mit Skala 1 behandelt')
        assert_close(z[:, constant], 0, 'Konstante nicht numerisch 0')
    assert_close(scaler.inverse_transform(weighted / np.array([1.0] + [float(WEIGHT)]*8)),
                 x, 'Inverse Transformation fehlerhaft')
    return constant, near_constant


def main():
    # 1. Eingaben laden, aktive V2 und bisherige Ergebnisse unverändert prüfen.
    manifest = json.loads((ROOT / 'documentation/active_data_version.json').read_text())
    require(manifest['active_version'] == 'V2', 'Keine aktive V2')
    hashes = dict(manifest['sha256'])
    hashes['data/processed/kmeans_user_features.csv'] = INPUT_HASH
    for name, expected in hashes.items():
        require(sha256(ROOT / name) == expected, f'Eingabehash abweichend: {name}')
    rows = read_csv(ROOT / 'data/processed/kmeans_user_features.csv', FEATURE_COLUMNS)
    users = [row['user_id'] for row in rows]
    # 2. Qualität prüfen: exakt vollständige V2-Nutzerliste, alle Werte endlich.
    source_users = read_csv(ROOT / 'data/raw/users_simulated.csv',
                            ['user_id','interest_sport','interest_outdoor','interest_wellness','interest_leisure'])
    require(len(rows) == len(set(users)) == 100 and users == sorted(r['user_id'] for r in source_users),
            'Nutzerliste nicht vollständig/eindeutig/sortiert')
    require(all(all(row[c].strip() for c in FEATURE_COLUMNS) for row in rows), 'Fehlende Werte')
    # 3. Ausschließlich neun explizite Eingänge auswählen; Interpretation/ID ausgeschlossen.
    x = np.array([[float(row[name]) for name in MODEL_FEATURES] for row in rows], dtype=np.float64)
    require(x.shape == (100,9) and np.isfinite(x).all() and (x >= 0).all(), 'Ungültige Eingänge')
    require((x[:,0] > 0).all(), 'Vollständig inaktive Nutzer separat behandeln')
    require((x[:,1:] <= 1).all(), 'Ungültige Sportanteile')
    assert_close(x[:,1:].sum(axis=1), np.ones(100), 'Anteilssummen falsch')
    scaler, z, weighted = fit_scale(x)
    constant, near_constant = validate(x, scaler, z, weighted)
    params = {
        'active_version': 'V2', 'method': 'sklearn.preprocessing.StandardScaler',
        'with_mean': True, 'with_std': True, 'ddof': 0, 'n_users': len(rows),
        'n_samples_seen': int(scaler.n_samples_seen_), 'fit_user_ids': users,
        'fit_scope': 'Deskriptives unüberwachtes Profiling aller 100 aktiven V2-Nutzer; kein Regressionssplit',
        'feature_order': MODEL_FEATURES, 'sport_weight_factor': float(WEIGHT),
        'source_commit': 'ed52949cb8b688bc64c0793be0e407950314769e',
        'implementation_status': 'AP-4-Skripte uncommitted',
        'input_sha256': hashes,
        'software': {'python': platform.python_version(), 'numpy': np.__version__, 'scikit_learn': sklearn.__version__},
        'constant_handling': 'StandardScaler: Populationsvarianz ddof=0; bei Varianz 0 oder numerisch ununterscheidbar konstant scale_=1; keine Division durch 0. Konstante Fitwerte sind nach Zentrierung numerisch 0. Neue abweichende Werte werden mit derselben Skala 1 transformiert.',
        'near_constant_rule': 'var <= n*eps*var + (n*mean*eps)^2; eps=float64 machine epsilon',
        'future_profiles': 'Nur berechtigte aktive Profile in feature_order; transform_saved ohne Refit. Undefinierte Sportanteile separat behandeln; keine Nullimputation.',
        'weighting_assumption': 'Fachliche Startannahme; bei neun variierenden Merkmalen beide Blockvarianz-Summen 1. Keine optimierte Gewichtung.',
        'validation_tolerance': {'atol': TOL, 'rtol': TOL},
        'features': {name: {'mean': float(scaler.mean_[i]), 'variance': float(scaler.var_[i]),
                            'std_ddof0': float(np.sqrt(scaler.var_[i])), 'scale': float(scaler.scale_[i]),
                            'weight': 1.0 if i==0 else float(WEIGHT),
                            'constant': bool(constant[i]), 'numerically_constant': bool(near_constant[i])}
                     for i,name in enumerate(MODEL_FEATURES)},
    }
    assert_close(transform_saved(rows, params), weighted, 'Parameter reproduzieren Ergebnis nicht')
    # 8. Beide Ausgaben vorab auf Konflikte prüfen, danach kontrolliert speichern.
    buffer = io.StringIO(newline='')
    writer = csv.writer(buffer, lineterminator='\n')
    writer.writerow(OUTPUT_COLUMNS)
    writer.writerows([uid, *values.tolist()] for uid,values in zip(users, weighted))
    csv_bytes = buffer.getvalue().encode('utf-8')
    import hashlib
    params['output_csv_sha256'] = hashlib.sha256(csv_bytes).hexdigest()
    outputs = {ROOT/'data/processed/kmeans_user_features_scaled.csv': csv_bytes,
               ROOT/'outputs/models/kmeans_scaling_params.json':
               (json.dumps(params, ensure_ascii=False, sort_keys=True, indent=2, allow_nan=False)+'\n').encode('utf-8')}
    for path,payload in outputs.items():
        require(not path.exists() or path.read_bytes() == payload, f'Bestehende Ausgabe abweichend: {path}')
    for path,payload in outputs.items():
        if not path.exists():
            path.parent.mkdir(parents=True, exist_ok=True)
            with path.open('xb') as stream:
                stream.write(payload)
    exported = read_csv(ROOT/'data/processed/kmeans_user_features_scaled.csv', OUTPUT_COLUMNS)
    require([r['user_id'] for r in exported] == users and len(exported)==100, 'Exportnutzer abweichend')
    actual = np.array([[float(r[c]) for c in MODEL_FEATURES] for r in exported])
    require(np.array_equal(actual, weighted), 'CSV-Rücklesen nicht identisch')
    saved = json.loads((ROOT/'outputs/models/kmeans_scaling_params.json').read_text())
    assert_close(transform_saved(rows, saved), actual, 'Gespeicherte Parameter reproduzieren CSV nicht')
    for name,expected in hashes.items():
        require(sha256(ROOT/name)==expected, f'Eingabe verändert: {name}')
    print(json.dumps({'status':'bestanden','rows':100,'columns':10,
        'constant_features':[n for i,n in enumerate(MODEL_FEATURES) if constant[i]],
        'numerically_constant_features':[n for i,n in enumerate(MODEL_FEATURES) if near_constant[i]],
        'max_abs_mean_standardized':float(np.abs(z.mean(axis=0)).max()),
        'variance_before_weighting':z.var(axis=0).tolist(),
        'variance_after_weighting':weighted.var(axis=0).tolist(),
        'block_variance_sums':[float(weighted.var(axis=0)[0]),float(weighted.var(axis=0)[1:].sum())],
        'input_hashes_unchanged':True,'output_sha256':{str(p.relative_to(ROOT)):sha256(p) for p in outputs}},indent=2))


if __name__ == '__main__':
    try:
        main()
    except (QualityError, ValueError, ArithmeticError, OSError, KeyError) as exc:
        print(f'ABBRUCH: {exc}\nKeine automatische Korrektur. Befund und Eingaben prüfen.',file=sys.stderr)
        sys.exit(1)
