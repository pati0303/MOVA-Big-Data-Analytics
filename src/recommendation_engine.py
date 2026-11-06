"""MOVA AP 6.2: deterministic synthetic demonstration; no real consent records.

Only a separate manually_confirmed tag record enables sports prioritisation.
The review proposals are deliberately never loaded by this module.
"""
from __future__ import annotations

import argparse
import csv
from dataclasses import dataclass, field
from datetime import date, timedelta
import hashlib
import json
import math
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SPORTS = ('Running', 'Cycling', 'Strength', 'Swimming', 'Walking', 'Hiking', 'Tennis', 'Padel')
INTERESTS = dict(zip(('interest_sport', 'interest_outdoor', 'interest_wellness', 'interest_leisure'),
                     ('Sport', 'Outdoor', 'Wellness', 'Freizeit')))
FEATURES = ['activities_current_week', 'avg_activities_last_4_weeks']
PROFILE_END = date(2026, 7, 5)


def read_csv(path):
    with Path(path).open(encoding='utf-8', newline='') as stream:
        return list(csv.DictReader(stream))


def index_unique(rows, key):
    result = {}
    for row in rows:
        if not row.get(key) or row[key] in result:
            raise ValueError(f'Missing or duplicate {key}')
        result[row[key]] = row
    return result


def permission_flags(interests_permission, garmin_permission):
    if type(interests_permission) is not bool or type(garmin_permission) is not bool:
        raise ValueError('Both simulated permissions must be explicit booleans')
    return {'interests_permission': interests_permission, 'garmin_permission': garmin_permission,
            'simulated': True, 'real_consent_record': False}


def interest_categories(user):
    categories = set()
    for key, category in INTERESTS.items():
        value = user.get(key)
        if type(value) is bool:
            positive = value
        elif value in ('True', 'False'):
            positive = value == 'True'
        else:
            raise ValueError(f'Missing or invalid interest: {key}')
        if positive:
            categories.add(category)
    return categories


@dataclass
class ProjectData:
    users: dict
    offers: list
    approved_tags: dict = field(default_factory=dict)
    profiles: dict = field(default_factory=dict)
    clusters: dict = field(default_factory=dict)
    weeks: list = field(default_factory=list)
    records_verified: bool = False
    known_sports: bool = False
    catalog_metadata: dict = field(default_factory=dict)
    root: Path = ROOT


def load_confirmed_tags(path, offers):
    """Approval file is a manual trust boundary, not an automatic title classifier."""
    path = Path(path)
    if not path.exists():
        return {}
    catalog = index_unique(offers, 'offer_id')
    rows = read_csv(path)
    index_unique(rows, 'offer_id')
    confirmed = {}
    for row in rows:
        if row.get('review_status') != 'manually_confirmed':
            continue
        oid = row.get('offer_id')
        tags = row.get('sport_tags', '').split('|')
        if (oid not in catalog or row.get('title') != catalog[oid]['title']
                or not row.get('reviewed_by', '').strip() or not row.get('reviewed_at', '').strip()
                or not tags or any(tag not in SPORTS for tag in tags) or len(tags) != len(set(tags))):
            raise ValueError('Invalid manual approval record')
        date.fromisoformat(row['reviewed_at'])
        confirmed[oid] = tuple(tags)
    return confirmed


def verify_tracked_bytes(root, path):
    """Compare activity inputs with trusted V2 source hashes in repository metadata."""
    digest = hashlib.sha256((root / path).read_bytes()).hexdigest()
    manifest = json.loads((root / 'documentation/active_data_version.json').read_text())
    scaling = json.loads((root / 'outputs/models/kmeans_scaling_params.json').read_text())
    # AP-4 scaling metadata contains the processed input source hashes.
    expected = manifest['sha256'].get(path) or scaling.get('source_sha256', {}).get(path)
    if expected is None:
        # Committed hashes also work in shallow clones and source archives.
        preserved = json.loads((root / 'documentation/ml_recommendations_preservation_v1.json').read_text())
        expected = preserved['sha256'].get(path)
        if expected is None:
            raise ValueError(f'No verified source hash: {path}')
    if digest != expected:
        raise ValueError(f'Unverified V2 source: {path}')


def load_data(root=ROOT, *, include_activity=False, include_catalog_extension=False):
    root = Path(root)
    if type(include_activity) is not bool or type(include_catalog_extension) is not bool:
        raise ValueError('Data loading switches must be boolean')
    users = index_unique(read_csv(root / 'data/raw/users_simulated.csv'), 'user_id')
    offers = read_csv(root / 'data/raw/offers_simulated.csv')
    index_unique(offers, 'offer_id')
    for offer in offers:
        if offer['category'] not in INTERESTS.values():
            raise ValueError('Unknown offer category')
        price, discount = float(offer['price_eur']), int(offer['discount_pct'])
        if not math.isfinite(price) or price < 0 or not 0 <= discount <= 100:
            raise ValueError('Invalid catalog price/discount')
    data = ProjectData(users, offers, load_confirmed_tags(
        root / 'documentation/offer_sport_tags_approved.csv', offers), root=root)
    if include_catalog_extension:
        from ml_recommendation_rules import extend_catalog
        data.offers, data.approved_tags, data.catalog_metadata = extend_catalog(
            root, data.offers, data.approved_tags)
    if include_activity:
        # Coverage is a documented property of hash-verified synthetic V2 only.
        try:
            for path in ['data/raw/activities_simulated.csv', 'data/processed/user_weekly_activities.csv']:
                verify_tracked_bytes(root, path)
            data.weeks = read_csv(root / 'data/processed/user_weekly_activities.csv')
            data.known_sports = all(row['sport_type'] in SPORTS for row in
                                    read_csv(root / 'data/raw/activities_simulated.csv'))
            data.records_verified = True
        except (ValueError, OSError):
            data.records_verified = False
        for attribute, path in [('profiles', 'data/processed/kmeans_user_features.csv'),
                                ('clusters', 'data/processed/user_clusters.csv')]:
            try:
                verify_tracked_bytes(root, path)
                setattr(data, attribute, index_unique(read_csv(root / path), 'user_id'))
            except (ValueError, OSError):
                setattr(data, attribute, {})
    return data


def select_user(data, user_id):
    if user_id not in data.users:
        raise ValueError(f'Unknown user: {user_id}')
    return data.users[user_id]


def sport_profile(data, user_id, as_of):
    if not data.records_verified or not data.known_sports:
        return {}, 'unverified_activity_data'
    if as_of < PROFILE_END:
        return {}, 'profile_not_yet_available'
    row = data.profiles.get(user_id)
    if row is None:
        return {}, 'missing_profile'
    try:
        frequency = float(row['avg_activities_per_week'])
        if not math.isfinite(frequency) or frequency < 0:
            raise ValueError()
        if frequency == 0:
            return {}, 'inactive'
        shares = {sport: float(row['share_' + sport.lower()]) for sport in SPORTS}
        if (any(not math.isfinite(v) or not 0 <= v <= 1 for v in shares.values())
                or not math.isclose(sum(shares.values()), 1, abs_tol=1e-10, rel_tol=0)):
            raise ValueError()
        return shares, 'available'
    except (ValueError, TypeError, KeyError):
        return {}, 'invalid_profile'


def filter_offers(offers, categories):
    return [offer for offer in offers if offer['category'] in categories]


def rank_offers(offers, approved_tags, shares):
    """Pure matching; inputs are already authorised/validated by the orchestrator."""
    ranked = []
    for offer in offers:
        matching = sorted((sport for sport in approved_tags.get(offer['offer_id'], ())
                           if shares.get(sport, 0) > 0), key=lambda s: (-shares[s], s))
        best_share = max((shares[s] for s in matching), default=0)
        ranked.append((0 if matching else 1, -best_share, offer['offer_id'], offer, matching))
    return sorted(ranked, key=lambda row: row[:3])


def match_reason(offer, matching):
    reason = f"Dieses Angebot gehört zu deiner ausgewählten Interessenkategorie {offer['category']}."
    if matching:
        reason += f" Im betrachteten Zeitraum wurden bei dir Aktivitäten der Sportart {matching[0]} aufgezeichnet; der Angebotsbezug ist manuell bestätigt."
    return reason


def recommendations(user_id, offers, categories, approved_tags, shares, *,
                    catalog_metadata=None, profile=None, use_kmeans=True, use_regression=True):
    results = []
    ranked = rank_offers(filter_offers(offers, categories), approved_tags, shares)
    decisions = {}
    if catalog_metadata:
        from ml_recommendation_rules import select_variants
        ranked, decisions = select_variants(ranked, catalog_metadata, profile or {},
                                           use_kmeans=use_kmeans, use_regression=use_regression)
    for position, (tier, _, _, offer, matching) in enumerate(ranked[:5], 1):
        results.append(dict(user_id=user_id, ranking_position=position, offer_id=offer['offer_id'],
                            offer_title=offer['title'], category=offer['category'],
                            price_eur=float(offer['price_eur']), discount_pct=int(offer['discount_pct']),
                            ranking_tier='A' if tier == 0 else 'B', match_reason=match_reason(offer, matching)))
    if catalog_metadata:
        from ml_recommendation_rules import explain
        for result in results:
            decision = decisions[result['offer_id']]
            result.update(decision)
            if result['metadata_status'] == 'demonstration_assumption':
                result['match_reason'] = result['match_reason'].replace(
                    'der Angebotsbezug ist manuell bestätigt.',
                    'die Sportzuordnung ist im fiktiven Demo-Katalog ausdrücklich festgelegt.')
            result['match_reason'] += explain(decision, profile or {})
            if result['historical_sport_share'] > 0:
                result['match_reason'] += (f" Historischer Anteil: {result['historical_sport_share']:.1%} der Aktivitäten; "
                                           "dies beschreibt beobachtetes Verhalten, keine gesicherte persönliche Relevanz.")
    return results


def predict_activity(data, user_id, *, garmin_permission, as_of):
    """Infer from the latest four consecutive completed weeks at/before as_of.

    Verification refers to documented synthetic V2, never to real Garmin coverage.
    No target labels or stored training/test feature tables are read.
    """
    result = dict(regression_prediction=None, prediction_status='permission_denied',
                  source='not_computed', input_features=None, input_week_end=None,
                  target_week_start=None, target_week_end=None,
                  limitation='Unverbindliche Schätzung; synthetisch evaluiert, individuelle Fehler möglich.')
    if garmin_permission is not True:
        return result
    if not data.records_verified or not data.known_sports:
        result['prediction_status'] = 'unverified_activity_data'
        return result
    try:
        rows = []
        for row in data.weeks:
            if row['user_id'] != user_id:
                continue
            end = date.fromisoformat(row['week_end'])
            if end <= as_of:
                rows.append((end, row))
        rows.sort(key=lambda pair: pair[0])
        if len(rows) < 4:
            result['prediction_status'] = 'insufficient_history'
            return result
        window = rows[-4:]
        counts = []
        for i, (end, row) in enumerate(window):
            start = date.fromisoformat(row['week_start'])
            value = float(row['activities_count'])
            if (end.weekday() != 6 or start != end - timedelta(days=6)
                    or not math.isfinite(value) or value < 0 or not value.is_integer()
                    or (i and end != window[i-1][0] + timedelta(days=7))):
                raise ValueError('Invalid four-week window')
            counts.append(value)
        end = window[-1][0]
        result.update(input_features=dict(zip(FEATURES, [counts[-1], sum(counts) / 4])),
                      input_week_end=end.isoformat(),
                      target_week_start=(end + timedelta(days=1)).isoformat(),
                      target_week_end=(end + timedelta(days=7)).isoformat())
    except (ValueError, KeyError, TypeError):
        result['prediction_status'] = 'invalid_history'
        return result
    try:
        import joblib
        import pandas as pd
        from threadpoolctl import threadpool_limits
        meta = json.loads((data.root / 'outputs/models/regression_linear_metadata.json').read_text())
        # The saved model was trained on targets through 2026-06-07. It must not
        # be presented as an as-of model for dates preceding its training data.
        if end < date.fromisoformat(meta['train_target_date_range'][1]):
            result['prediction_status'] = 'model_training_after_cutoff'
            return result
        model_path = data.root / 'outputs/models/regression_linear.joblib'
        if hashlib.sha256(model_path.read_bytes()).hexdigest() != meta['model_sha256']:
            raise ValueError('Model hash mismatch')
        if meta['feature_order'] != FEATURES:
            raise ValueError('Feature order mismatch')
        try:
            model = joblib.load(model_path)
        except (EOFError, AttributeError) as exc:
            result.update(prediction_status='model_unavailable_or_invalid',
                          prediction_error_type=type(exc).__name__)
            return result
        if (list(model.feature_names_in_) != FEATURES or model.get_params() != meta['parameters']
                or float(model.intercept_) != meta['intercept']
                or list(model.coef_) != [meta['coefficients'][f] for f in FEATURES]):
            raise ValueError('Model metadata mismatch')
        with threadpool_limits(limits=1):
            value = float(model.predict(pd.DataFrame([result['input_features']], columns=FEATURES))[0])
        if not math.isfinite(value):
            raise ValueError('Nonfinite prediction')
        result.update(regression_prediction=value, prediction_status='available',
                      source='new_inference_saved_regression_model')
    except (ValueError, OSError, KeyError, TypeError, ImportError):
        result['prediction_status'] = 'model_unavailable_or_invalid'
    return result


def recommend_user(data, user_id, *, interests_permission, garmin_permission, as_of=PROFILE_END,
                   use_kmeans=True, use_regression=True):
    flags = permission_flags(interests_permission, garmin_permission)
    if type(as_of) is not date:
        raise ValueError('as_of must be a date (inclusive completed-week cutoff)')
    user = select_user(data, user_id)
    profile = dict(segment_label=None, cluster_id=None, segment_status='permission_denied',
                   segment_source='not_loaded', sport_profile_status='permission_denied')
    shares = {}
    if garmin_permission:
        shares, status = sport_profile(data, user_id, as_of)
        profile['sport_profile_status'] = status
        cluster = data.clusters.get(user_id) if status == 'available' else None
        expected = {'0': 'Geringere Trainingshäufigkeit', '1': 'Höhere Trainingshäufigkeit'}
        cluster_id = cluster.get('cluster_id') if isinstance(cluster, dict) else None
        if (type(cluster_id) is str and cluster_id in expected
                and cluster.get('segment_label') == expected[cluster_id]):
            profile.update(segment_label=cluster['segment_label'], cluster_id=int(cluster_id),
                           segment_status='available', segment_source='stored_user_clusters',
                           segment_period_end=PROFILE_END.isoformat())
        else:
            profile['segment_status'] = 'missing_or_ineligible'
    # Expose the already authorised/validated profile, without recomputing features.
    profile['sport_shares'] = dict(shares)
    profile.update(predict_activity(data, user_id, garmin_permission=garmin_permission, as_of=as_of))
    output = dict(user_id=user_id, permissions_simulated=flags, as_of=as_of.isoformat(),
                  profile=profile, interest_categories=[], recommendations=[],
                  personalization_status='interests_permission_denied')
    if not interests_permission:
        return output
    try:
        categories = interest_categories(user)
    except ValueError:
        output['personalization_status'] = 'invalid_or_missing_interests'
        return output
    output['interest_categories'] = sorted(categories)
    output['personalization_status'] = 'available' if categories else 'no_positive_interests'
    output['recommendations'] = recommendations(
        user_id, data.offers, categories, data.approved_tags, shares,
        catalog_metadata=data.catalog_metadata, profile=profile,
        use_kmeans=use_kmeans, use_regression=use_regression)
    return output


def run(user_id, *, interests_permission, garmin_permission, as_of=PROFILE_END, root=ROOT):
    permission_flags(interests_permission, garmin_permission)
    return recommend_user(load_data(root, include_activity=garmin_permission, include_catalog_extension=True), user_id,
                          interests_permission=interests_permission,
                          garmin_permission=garmin_permission, as_of=as_of)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('user_id')
    parser.add_argument('--interests-permission', required=True, choices=['yes', 'no'])
    parser.add_argument('--garmin-permission', required=True, choices=['yes', 'no'])
    parser.add_argument('--as-of', type=date.fromisoformat, default=PROFILE_END)
    args = parser.parse_args()
    print(json.dumps(run(args.user_id, interests_permission=args.interests_permission == 'yes',
                         garmin_permission=args.garmin_permission == 'yes', as_of=args.as_of),
                     ensure_ascii=False, indent=2, allow_nan=False))
