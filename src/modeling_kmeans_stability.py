"""AP 5.2: Initialisierungsstabilität und vorläufige aggregierte Profile.

python src/modeling_kmeans_stability.py
Nutzerlabels und Modelle werden ausschließlich im Arbeitsspeicher gehalten.
"""
import csv
import io
import json
from itertools import combinations
import warnings
import numpy as np
import pandas as pd
from sklearn.metrics import adjusted_rand_score, silhouette_score
from sklearn.cluster import KMeans
from threadpoolctl import threadpool_limits
import modeling_kmeans_k_selection as base

ROOT = base.ROOT
CANDIDATES = (2, 3, 6, 8)
SEEDS = tuple(range(19)) + (42,)
SPORTS = base.FEATURES[1:]
PROFILE_FEATURES = [base.FEATURES[0], 'avg_duration_per_week', 'sport_diversity'] + SPORTS


def frame_bytes(frame):
    return frame.to_csv(index=False, lineterminator='\n', float_format='%.17g').encode('utf-8')


def ari_summary(labels, seeds=SEEDS):
    """Alle ungeordneten Paare ohne Selbstvergleiche; 190 Paare bei 20 Seeds."""
    base.require(len(seeds) == len(set(seeds)) == 20 and 42 in seeds, '20 eindeutige Seeds inkl. 42 erforderlich')
    base.require(set(labels) == set(seeds), 'Seed-Zuordnungen unvollständig')
    for values in labels.values():
        base.require(np.asarray(values).shape == (100,), '100 Zuordnungen erforderlich')
    pairs = np.array([adjusted_rand_score(labels[a], labels[b])
                      for a,b in combinations(seeds, 2)])
    reference = np.array([adjusted_rand_score(labels[42], labels[s]) for s in seeds if s != 42])
    base.require(len(pairs) == 190 and len(reference) == 19, 'ARI-Paaranzahl falsch')
    base.require(np.isfinite(pairs).all() and ((pairs >= -1)&(pairs <= 1)).all(), 'ARI ungültig')
    # Kanonische Partition: Zuordnungen nach erstem Auftreten umbenennen.
    partitions = set()
    for values in labels.values():
        mapping = {}
        partitions.add(tuple(mapping.setdefault(int(v), len(mapping)) for v in values))
    return dict(ari_pairwise_mean=float(pairs.mean()), ari_pairwise_min=float(pairs.min()),
        ari_pairwise_max=float(pairs.max()), n_pairs=len(pairs),
        ari_vs_42_mean=float(reference.mean()), ari_vs_42_min=float(reference.min()),
        ari_vs_42_max=float(reference.max()), n_unique_partitions=len(partitions)), pairs


def evaluate(x, seeds=SEEDS):
    x = np.array(x, dtype=float, copy=True)
    base.require(x.shape == (100,9) and np.isfinite(x).all(), 'Ungültige Modellmatrix')
    base.require(len(seeds) == len(set(seeds)) == 20 and 42 in seeds and
                 all(type(s) is int and 0 <= s <= 2**32-1 for s in seeds), 'Ungültige Seeds')
    rows, summaries, references, pairs_by_k = [], [], {}, {}
    with threadpool_limits(limits=1):
        for k in CANDIDATES:
            labels = {}
            k_rows = []
            for seed in seeds:
                parameters = {**base.PARAMETERS, 'random_state':seed}
                with warnings.catch_warnings(record=True) as caught:
                    warnings.simplefilter('always')
                    model = KMeans(n_clusters=k, **parameters).fit(x)
                assignments = model.labels_.copy()
                unique, counts = np.unique(assignments, return_counts=True)
                base.require(len(unique) == k and len(assignments) == counts.sum() == 100,
                             'Clusteranzahl/Zuordnungen ungültig')
                score = float(silhouette_score(x, assignments, metric='euclidean'))
                base.require(np.isfinite(score) and -1 <= score <= 1 and
                             np.isfinite(model.inertia_) and model.inertia_ >= 0, 'Kennzahlen ungültig')
                row = dict(k=k, seed=seed, inertia=float(model.inertia_), silhouette_score=score,
                    n_iterations=int(model.n_iter_), n_clusters=len(unique),
                    min_cluster_size=int(counts.min()), max_cluster_size=int(counts.max()),
                    cluster_sizes=json.dumps(dict(zip(map(str,unique),map(int,counts))), sort_keys=True),
                    warnings='; '.join(str(w.message) for w in caught))
                rows.append(row); k_rows.append(row); labels[seed] = assignments
            references[k] = labels[42].copy()
            for row in k_rows:
                row['ari_vs_seed_42'] = float(adjusted_rand_score(labels[42], labels[row['seed']]))
            ari, pairs_by_k[k] = ari_summary(labels, seeds)
            sil = np.array([r['silhouette_score'] for r in k_rows])
            inertia = np.array([r['inertia'] for r in k_rows])
            summaries.append(dict(k=k, n_seeds=len(seeds), **ari,
                silhouette_mean=float(sil.mean()), silhouette_std=float(sil.std(ddof=0)),
                silhouette_min=float(sil.min()), silhouette_max=float(sil.max()),
                inertia_mean=float(inertia.mean()), inertia_min=float(inertia.min()),
                inertia_max=float(inertia.max()),
                min_observed_cluster_size=min(r['min_cluster_size'] for r in k_rows)))
    return pd.DataFrame(rows), pd.DataFrame(summaries), references, pairs_by_k


def candidate_profiles(scaled, raw, references):
    base.validate_frame(scaled)
    base.require(list(raw.columns) == ['user_id']+base.FEATURES+['avg_duration_per_week','sport_diversity'],
                 'Unskaliertes Schema abweichend')
    base.require(len(raw) == 100 and raw.user_id.notna().all() and raw.user_id.is_unique and
                 set(raw.user_id) == set(scaled.user_id), 'Nutzerverknüpfung nicht eindeutig/vollständig')
    base.require(np.isfinite(raw[PROFILE_FEATURES].to_numpy(dtype=float)).all(), 'Profilwerte ungültig')
    rows = []
    for k in (2,3):
        labels = np.asarray(references[k])
        base.require(labels.shape == (100,) and set(labels) == set(range(k)), 'Referenzlabels ungültig')
        assignments = pd.DataFrame({'user_id':scaled.user_id.to_numpy(), 'candidate_cluster':labels})
        joined = assignments.merge(raw, on='user_id', how='inner', validate='one_to_one')
        base.require(len(joined) == 100, 'Nutzer bei Join verloren')
        for cluster, group in joined.groupby('candidate_cluster', sort=True):
            means = group[PROFILE_FEATURES].mean()
            top = sorted(SPORTS, key=lambda sport:(-means[sport],sport))[:3]
            rows.append(dict(k=k, seed=42, candidate_cluster=int(cluster), n_users=len(group),
                **{f:float(means[f]) for f in PROFILE_FEATURES},
                top_3_sports=' / '.join(s.removeprefix('share_') for s in top),
                profile_status='vorläufiges Kandidatenprofil'))
    return pd.DataFrame(rows)


def render_figures(comparison, profiles, pairs):
    plt = base.plt
    with plt.rc_context({'font.family':'DejaVu Sans', 'font.size':10}):
        fig, ax = plt.subplots(figsize=(8.5,5), layout='constrained')
        positions=np.arange(1,5)
        for pos,k in zip(positions,CANDIDATES):
            values=pairs[k]
            ax.scatter(np.full(len(values),pos), values, s=13, alpha=.15, color='#176b87')
        ax.boxplot([pairs[k] for k in CANDIDATES], positions=positions, widths=.35,
                   showmeans=True, meanprops={'marker':'D','markerfacecolor':'#cc6600','markeredgecolor':'#cc6600'})
        ax.set(xticks=positions, xticklabels=[str(k) for k in CANDIDATES], xlabel='Anzahl Cluster k',
            ylabel='Adjusted Rand Index', ylim=(-.03,1.04), title='MOVA · Stabilität gegenüber Initialisierungen')
        ax.grid(axis='y',alpha=.25)
        fig.suptitle('20 Seeds je k · 190 paarweise ARI-Werte · Rauten: Mittelwerte',fontsize=10)
        save(fig,'kmeans_stability.png')
        fig, axes=plt.subplots(2,4,figsize=(15,7),layout='constrained',
                              gridspec_kw={'width_ratios':[1,1,1,2.4]})
        for i,k in enumerate((2,3)):
            group=profiles[profiles.k==k]
            names=[f'C{int(c)}' for c in group.candidate_cluster]
            for j,(field,title) in enumerate([
                ('avg_activities_per_week','Aktivitäten / Woche'),
                ('avg_duration_per_week','Minuten / Woche'),
                ('sport_diversity','Sportartenvielfalt')]):
                ax=axes[i,j];values=group[field].to_numpy()
                ax.bar(names,values,color='#176b87')
                ax.set(title=f'k={k} · {title}',ylim=(0,{'avg_activities_per_week':6,'avg_duration_per_week':350,'sport_diversity':8}[field]))
                for pos,value in enumerate(values):ax.text(pos,value,f'{value:.2f}',ha='center',va='bottom',fontsize=9)
            ax=axes[i,3];values=group[SPORTS].to_numpy()*100
            im=ax.imshow(values,aspect='auto',cmap='Blues',vmin=0,vmax=40)
            ax.set(yticks=range(k),yticklabels=[f'{name} (n={int(n)})' for name,n in zip(names,group.n_users)],
                   xticks=range(8),xticklabels=[s.removeprefix('share_') for s in SPORTS],
                   title=f'k={k} · mittlere Sportanteile (%)')
            ax.tick_params(axis='x',rotation=45)
            for a in range(k):
                for b in range(8):ax.text(b,a,f'{values[a,b]:.1f}',ha='center',va='center',fontsize=8,
                                         color='white' if values[a,b]>23 else 'black')
        fig.colorbar(im,ax=axes[:,3],label='Mittlerer Nutzeranteil (%)',shrink=.7)
        fig.suptitle('MOVA · Vorläufige Kandidatenprofile · Seed 42 · C-IDs ohne endgültige Bezeichnungen')
        save(fig,'kmeans_candidate_profiles.png')


def save(fig, name):
    buffer=io.BytesIO()
    fig.savefig(buffer,format='png',dpi=180,metadata={'Software':'MOVA AP 5.2'})
    base.plt.close(fig)
    base.write_identical_or_new(ROOT/'outputs/figures'/name,buffer.getvalue())


def main():
    paths=[p for folder in ['data','src','tests','documentation','outputs']
           for p in (ROOT/folder).rglob('*') if p.is_file() and '__pycache__' not in p.parts]
    before={p:base.digest(p) for p in paths}
    scaled=pd.read_csv(ROOT/'data/processed/kmeans_user_features_scaled.csv')
    x=base.load_input()
    runs,comparison,references,pairs=evaluate(x)
    # Seed 42 muss die tatsächlich vorhandenen AP-5.1-Kennzahlen reproduzieren.
    previous=pd.read_csv(ROOT/'outputs/tables/kmeans_k_selection.csv').set_index('k')
    for _,row in runs[runs.seed==42].iterrows():
        for key in ['inertia','silhouette_score','n_iterations','min_cluster_size','max_cluster_size']:
            base.require(np.isclose(row[key],previous.loc[row.k,key],atol=1e-12,rtol=1e-12),
                         f'AP-5.1-Referenz abweichend: {row.k}, {key}')
    raw=pd.read_csv(ROOT/'data/processed/kmeans_user_features.csv')
    profiles=candidate_profiles(scaled,raw,references)
    for name,frame in [('kmeans_stability_results.csv',runs),('kmeans_candidate_comparison.csv',comparison),
                       ('kmeans_candidate_profiles.csv',profiles)]:
        base.write_identical_or_new(ROOT/'outputs/tables'/name,frame_bytes(frame))
    render_figures(comparison,profiles,pairs)
    base.require(all(base.digest(p)==sha for p,sha in before.items()),'Vorhandene Datei verändert')
    print(comparison.to_string(index=False))
    print(profiles.to_string(index=False))


if __name__=='__main__':
    main()
