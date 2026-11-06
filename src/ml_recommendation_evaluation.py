"""Read-only four-way ablation; write only new AP-2.2 recommendation artifacts.

Run: python src/ml_recommendation_evaluation.py
Never trains models or changes historical evaluation outputs.
"""
import csv
import hashlib
import json
from pathlib import Path
import recommendation_engine as e

MODES = {'no_ml': (False, False), 'kmeans_only': (True, False),
         'regression_only': (False, True), 'both': (True, True)}


def compare(data):
    records = []
    original = e.load_data(include_activity=True)
    for uid in sorted(data.users):
        # One actual inference per user, reused unchanged for every ablation.
        actual = e.recommend_user(data, uid, interests_permission=True, garmin_permission=True)
        profile = actual['profile']
        categories = set(actual['interest_categories'])
        shares = profile['sport_shares']
        variants = {}
        for mode, (km, reg) in MODES.items():
            variants[mode] = e.recommendations(uid, data.offers, categories, data.approved_tags, shares,
                catalog_metadata=data.catalog_metadata, profile=profile,
                use_kmeans=km, use_regression=reg)
        legacy = e.recommendations(uid, original.offers, categories, original.approved_tags, shares)
        expanded_raw = e.recommendations(uid, data.offers, categories, data.approved_tags, shares)
        records.append(dict(user_id=uid, profile=profile, interest_categories=sorted(categories),
            original_30_top5=[o['offer_id'] for o in legacy],
            expanded_38_ungrouped_top5=[o['offer_id'] for o in expanded_raw], variants=variants))
    ids = lambda row, mode: [o['offer_id'] for o in row['variants'][mode]]
    summary = dict(users=len(records), offers=len(data.offers), as_of=e.PROFILE_END.isoformat(),
        baseline='no_ml uses the same 38 offers and one variant per group, with both ML signals disabled. '
                 'Original 30-offer and expanded ungrouped lists are separate references to expose catalog/grouping effects.',
        changed_top5_vs_no_ml={mode: sum(ids(row, mode) != ids(row, 'no_ml') for row in records)
                              for mode in MODES},
        limitation='Ranking changes demonstrate rule effects, not improved satisfaction, purchase probability or recommendation quality.')
    return records, summary


def main():
    data = e.load_data(include_activity=True, include_catalog_extension=True)
    records, summary = compare(data)
    output = e.ROOT / 'outputs/ml_recommendations_v1'
    output.mkdir(exist_ok=True)
    (output / 'comparison.json').write_text(json.dumps(dict(summary=summary, users=records),
        ensure_ascii=False, indent=2, allow_nan=False)+'\n', encoding='utf-8')
    with (output / 'top5.csv').open('w', newline='', encoding='utf-8') as stream:
        writer = csv.DictWriter(stream, fieldnames=['user_id', 'mode', 'ranking_position', 'offer_id',
            'offer_group', 'kmeans_influence', 'regression_influence', 'match_reason'])
        writer.writeheader()
        for user in records:
            for mode, offers in user['variants'].items():
                for offer in offers:
                    writer.writerow(dict(user_id=user['user_id'], mode=mode,
                        **{key: offer[key] for key in writer.fieldnames if key not in ('user_id', 'mode')}))
    paths = ['src/recommendation_engine.py', 'src/ml_recommendation_rules.py',
             'src/ml_recommendation_evaluation.py', 'data/catalog/offers_extension_v1.csv',
             'data/catalog/recommendation_metadata_v1.json', 'documentation/offer_sport_tags_approved.csv',
             'data/raw/users_simulated.csv', 'data/raw/activities_simulated.csv',
             'data/raw/offers_simulated.csv', 'data/processed/kmeans_user_features.csv',
             'data/processed/user_weekly_activities.csv', 'data/processed/user_clusters.csv',
             'outputs/models/regression_linear.joblib', 'outputs/models/regression_linear_metadata.json',
             'outputs/models/kmeans_final.joblib', 'outputs/models/kmeans_final_metadata.json']
    manifest = dict(policy_version=data.catalog_metadata['policy_version'], training_performed=False,
        source_sha256={p: hashlib.sha256((e.ROOT/p).read_bytes()).hexdigest() for p in paths},
        artifact_sha256={p.name: hashlib.sha256(p.read_bytes()).hexdigest() for p in
                         [output/'comparison.json', output/'top5.csv']})
    (output/'manifest.json').write_text(json.dumps(manifest, indent=2)+'\n')
    print(json.dumps(summary, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()
