"""AP 2.2: reviewed demo variants, no fitting, no per-user special cases.

Groups occupy their first position in the legacy sport-ranked list. Model signals
choose a representative *inside* that position; unrelated offers get no bonus.
"""
import csv
import json
import math


def extend_catalog(root, original, approved_tags):
    path = root / 'data/catalog'
    with (path / 'offers_extension_v1.csv').open(encoding='utf-8', newline='') as stream:
        reader = csv.DictReader(stream)
        if reader.fieldnames != ['offer_id', 'category', 'title', 'price_eur', 'discount_pct']:
            raise ValueError('Invalid extension columns')
        extension = list(reader)
    policy = json.loads((path / 'recommendation_metadata_v1.json').read_text(encoding='utf-8'))
    if policy['schema_version'] != 1 or policy['policy_version'] != 'AP2.2-v1':
        raise ValueError('Unsupported catalog policy')
    thresholds = policy['thresholds']
    low, high = thresholds['single_below'], thresholds['multiple_from']
    if (type(low) not in (int, float) or type(high) not in (int, float)
            or not math.isfinite(low) or not math.isfinite(high) or not 0 <= low < high):
        raise ValueError('Invalid demonstration thresholds')
    if len(extension) != 8 or {o['offer_id'] for o in extension} != {f'O{i:03}' for i in range(31, 39)}:
        raise ValueError('Expected eight unique extension IDs')
    offers = original + extension
    ids = [o['offer_id'] for o in offers]
    metadata = policy['offers']
    if len(ids) != len(set(ids)) or set(metadata) != set(ids):
        raise ValueError('Duplicate IDs or incomplete metadata')
    tags = dict(approved_tags)
    groups = {}
    for offer in offers:
        oid = offer['offer_id']; meta = metadata[oid]
        if (offer['category'] not in ('Sport', 'Outdoor', 'Wellness', 'Freizeit')
                or not offer['title'].startswith('FIKTIV')
                or not math.isfinite(float(offer['price_eur'])) or float(offer['price_eur']) < 0
                or not 0 <= int(offer['discount_pct']) <= 100):
            raise ValueError('Invalid extension offer')
        if not meta['group'] or not meta['rationale'].strip():
            raise ValueError('Missing group or rationale')
        expected = list(approved_tags.get(oid, ())) if offer in original else [
            'Running' if offer['category'] == 'Sport' else 'Hiking']
        if meta['sport_tags'] != expected:
            raise ValueError('Unapproved sport tag')
        if meta['status'] not in ('neutral', 'demonstration_assumption'):
            raise ValueError('Unreviewed metadata')
        rule = meta['ml_rule']
        if rule not in (None, 'kmeans', 'regression'):
            raise ValueError('Unknown rule')
        if rule and (meta['status'] != 'demonstration_assumption' or not expected):
            raise ValueError('ML rule lacks documented sport assumption')
        if rule == 'kmeans':
            if meta['long_term_use'] not in ('occasional', 'frequent') or meta['weekly_sessions'] is not None:
                raise ValueError('Invalid long-term variant')
        elif rule == 'regression':
            if type(meta['weekly_sessions']) is not int or meta['weekly_sessions'] not in (1, 3) or meta['long_term_use'] is not None:
                raise ValueError('Invalid schedule variant')
        elif meta['long_term_use'] is not None or meta['weekly_sessions'] is not None:
            raise ValueError('Neutral offer has ML attributes')
        # Comparable variants must have the same category and sport basis.
        signature = (offer['category'], tuple(expected))
        group = groups.setdefault(meta['group'], {'signature': signature, 'rules': set()})
        if group['signature'] != signature:
            raise ValueError('Incomparable variants in one group')
        if rule:
            group['rules'].add(rule)
        if expected:
            tags[oid] = tuple(expected)
    if any(len(g['rules']) > 1 for g in groups.values()):
        raise ValueError('Frequency cannot be counted twice in one group')
    return offers, tags, policy


def select_variants(ranked, policy, profile, *, use_kmeans=True, use_regression=True):
    if type(use_kmeans) is not bool or type(use_regression) is not bool:
        raise ValueError('Ablation switches must be booleans')
    groups = {}
    metadata = policy['offers']
    for row in ranked:
        groups.setdefault(metadata[row[2]]['group'], []).append(row)
    selected, decisions = [], {}
    cid = profile.get('cluster_id')
    cluster_valid = (profile.get('segment_status') == 'available'
                     and type(cid) is int and cid in (0, 1))
    value = profile.get('regression_prediction')
    prediction_valid = (profile.get('prediction_status') == 'available'
                        and type(value) in (int, float) and math.isfinite(value) and value >= 0)
    for group_id, members in groups.items():
        # Legacy order supplies deterministic fallback and the group's anchor.
        baseline = members[0]
        winner = baseline
        signal = None
        # Never use activity-based rules without an authorised matching sport.
        if baseline[4]:
            if use_kmeans and cluster_valid:
                use = 'occasional' if cid == 0 else 'frequent'
                preferred = [row for row in members if metadata[row[2]]['ml_rule'] == 'kmeans'
                             and metadata[row[2]]['long_term_use'] == use]
                if preferred:
                    winner = preferred[0]; signal = 'kmeans'
            if use_regression and prediction_valid:
                thresholds = policy['thresholds']
                sessions = (1 if value < thresholds['single_below'] else
                            3 if value >= thresholds['multiple_from'] else None)
                preferred = [row for row in members if metadata[row[2]]['ml_rule'] == 'regression'
                             and metadata[row[2]]['weekly_sessions'] == sessions]
                if preferred:
                    winner = preferred[0]; signal = 'regression'
        changed = winner[2] != baseline[2]
        decisions[winner[2]] = dict(
            offer_group=group_id, historical_sport_share=-winner[1],
            matched_sports=winner[4], baseline_variant=baseline[2],
            candidate_variants=[row[2] for row in members],
            kmeans_influence=signal == 'kmeans' and changed,
            regression_influence=signal == 'regression' and changed,
            variant_signal=signal, metadata_status=metadata[winner[2]]['status'],
            policy_version=policy['policy_version'])
        selected.append(winner)
    return selected, decisions


def explain(decision, profile):
    parts = []
    if decision['kmeans_influence']:
        use = 'gelegentliche' if profile['cluster_id'] == 0 else 'häufige'
        parts.append(f'Dein gespeichertes langfristiges Aktivitätssegment bevorzugt innerhalb '
                     f'dieser Angebotsgruppe die Variante für {use} Nutzung. '
                     'Dies ist eine Demonstrationsannahme zur Nutzungshäufigkeit, keine Bewertung deiner Leistungsfähigkeit.')
    if decision['regression_influence']:
        start, end = profile.get('target_week_start'), profile.get('target_week_end')
        period = f' für {start} bis {end}' if start and end else ''
        parts.append(f"Deine Prognose{period} beträgt rund {profile['regression_prediction']:.2f} "
                     'Aktivitäten insgesamt. Nach der Demonstrationsregel wird innerhalb dieser '
                     'Laufkursgruppe das Format mit drei Terminen pro Woche bevorzugt. '
                     'Die Gesamtprognose sagt keine drei Laufaktivitäten oder Terminverfügbarkeit voraus; '
                     'sie ist keine Teilnahmevoraussetzung.')
    if decision['variant_signal'] == 'regression' and not decision['regression_influence']:
        parts.append('Die Prognoseregel bestätigt den Einzeltermin; dieser liegt auch ohne '
                     'Regression vorn. Sie verändert hier die Variantenwahl nicht.')
    return (' ' + ' '.join(parts)) if parts else ''
