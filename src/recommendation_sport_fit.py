"""Retrospective sport-fit metric from four frozen CSVs; standard library only.

No engine imports, model inference/training, new recommendations or source writes.
The stored lists are measured; independent ordering checks only validate them.
Run: python src/recommendation_sport_fit.py
"""
import csv
from datetime import date
from decimal import Decimal
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SOURCES = (
    'outputs/tables/recommendation_before_after_users.csv',
    'data/processed/kmeans_user_features.csv',
    'data/raw/offers_simulated.csv',
    'documentation/offer_sport_tags_approved.csv',
)
HASHES = (
    '47725202a467eeff3120ac98799bffd7d92d4c27e1f1675e34ea6f0eac1df3d2',
    'bb6b0c4e9307ab286f9f6e76d04b9b1446a9ab322e31784c8883a6a596ca7a28',
    '83748cb66918c08e3061889834e24452d0dc9feb6581690c4959cb3ba3775fa6',
    'a637ec2ff2cfb4fd7b3cfef1a441c144917560cf03bee2ea0cea79675989cfc9',
)
SPORTS = ('Running', 'Cycling', 'Strength', 'Swimming', 'Walking', 'Hiking', 'Tennis', 'Padel')
CATEGORIES = {'Sport', 'Outdoor', 'Wellness', 'Freizeit'}
COLUMNS = (
    ['user_id','categories','eligible_offers','count_before','count_after','top5_before','top5_after',
     'tier_a_before','tier_a_after','ordered_list_changed','composition_changed',
     'shared_offer_position_changed','common_offers','change_group'],
    ['user_id','avg_activities_per_week'] + ['share_'+s.lower() for s in SPORTS] + ['avg_duration_per_week','sport_diversity'],
    ['offer_id','category','title','price_eur','discount_pct'],
    ['offer_id','title','sport_tags','review_status','reviewed_by','reviewed_at'],
)
OUTPUT = 'outputs/tables/recommendation_sport_fit_retrospective.json'


def require(condition, message):
    if not condition:
        raise ValueError(message)


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load(root=ROOT):
    tables = []
    for name, expected, columns in zip(SOURCES, HASHES, COLUMNS):
        path = root/name
        require(digest(path) == expected, 'Source hash mismatch: '+name)
        with path.open(encoding='utf-8', newline='') as stream:
            reader = csv.DictReader(stream)
            require(reader.fieldnames == columns, 'CSV schema mismatch: '+name)
            rows = list(reader)
        require(all(list(r) == columns and all(v is not None for v in r.values()) for r in rows), 'Malformed CSV')
        tables.append(rows)
    return tables


def unique(rows, key):
    require(all(r.get(key) for r in rows), 'Missing key: '+key)
    result = {r[key]:r for r in rows}
    require(len(result) == len(rows), 'Duplicate key: '+key)
    return result


def array(value):
    result = json.loads(value)
    require(type(result) is list and all(type(v) is str for v in result), 'Expected JSON string array')
    require(len(set(result)) == len(result), 'Duplicate array member')
    return result


def percentage(numerator, denominator):
    return float(Decimal(numerator)/Decimal(denominator)*100) if denominator else None


def match_score(tags, shares):
    """One slot has one maximum score even when several tags match."""
    return max((shares[s] for s in tags if shares[s]>0), default=Decimal(0))


def calculate(users, profiles, offers, tags):
    """A slot matches iff any FINAL confirmed tag has positive historical share.

    The same tag map and profile are used for BOTH saved variants. A slot counts
    once even if multiple tags match. Category eligibility is checked separately.
    Empty lists contribute zero slots, zero matches, and no user coverage.
    """
    user_map, profile_map = unique(users,'user_id'), unique(profiles,'user_id')
    catalog = unique(offers,'offer_id')
    require(len(users)==len(profiles)==100 and len(offers)==30 and len(tags)==8, 'Frozen V2 sizes differ')
    require(set(user_map)==set(profile_map), 'Different user populations')
    require(all(o['category'] in CATEGORIES for o in offers), 'Unknown catalog category')
    unique(tags,'offer_id')
    mapping = {}
    for r in tags:
        require(r['review_status']=='manually_confirmed', 'Unconfirmed tag')
        oid = r['offer_id']
        require(oid in catalog and r['title']==catalog[oid]['title'], 'Tag/catalog mismatch')
        require(bool(r['reviewed_by'].strip()), 'Missing reviewer')
        date.fromisoformat(r['reviewed_at'])
        sports = r['sport_tags'].split('|')
        require(bool(sports) and len(sports)==len(set(sports)) and set(sports)<=set(SPORTS), 'Invalid sport tags')
        mapping[oid] = sports
    totals = {v:dict(users=100,slots=0,matching_slots=0,users_with_match=0,users_without_recommendations=0,
                     category_violations=0) for v in ('before','after')}
    paired = []
    for uid in sorted(user_map):
        r, p = user_map[uid], profile_map[uid]
        shares = {s:Decimal(p['share_'+s.lower()]) for s in SPORTS}
        require(all(v.is_finite() and 0<=v<=1 for v in shares.values()), 'Invalid share')
        require(abs(sum(shares.values())-1)<=Decimal('1e-10'), 'Shares do not sum to one')
        frequency = Decimal(p['avg_activities_per_week'])
        require(frequency.is_finite() and frequency>0, 'Unavailable historical sport profile')
        categories = array(r['categories'])
        require(set(categories)<=CATEGORIES, 'Unknown positive category')
        eligible = [o for o in offers if o['category'] in categories]
        require(len(eligible)==int(r['eligible_offers']), 'Candidate count differs')
        def score(oid):
            return match_score(mapping.get(oid,[]),shares)
        per_user = dict(user_id=uid)
        lists = {}
        for variant in ('before','after'):
            ids = array(r['top5_'+variant]); lists[variant]=ids
            require(len(ids)==int(r['count_'+variant])==min(5,len(eligible)), 'Saved list length differs')
            require(set(ids)<=set(catalog), 'Unknown saved offer')
            violations = sum(catalog[oid]['category'] not in categories for oid in ids)
            require(violations==0, 'Positive interest category violation')
            # Validate identity/order, do not replace stored lists with new lists.
            key = (lambda o:o['offer_id']) if variant=='before' else (
                lambda o:(0 if score(o['offer_id'])>0 else 1, -score(o['offer_id']), o['offer_id']))
            reference = [o['offer_id'] for o in sorted(eligible,key=key)[:5]]
            require(ids==reference, 'Saved list differs from documented ordering')
            matches = sum(score(oid)>0 for oid in ids)
            require(int(r['tier_a_'+variant])==(0 if variant=='before' else matches), 'Saved tier count differs')
            t=totals[variant]
            t['slots']+=len(ids); t['matching_slots']+=matches
            t['users_with_match']+=int(matches>0)
            t['users_without_recommendations']+=int(not ids)
            t['category_violations']+=violations
            per_user[variant+'_matching_slots']=matches
        require(len(lists['before'])==len(lists['after']), 'Different per-user denominators')
        per_user['delta_matching_slots']=per_user['after_matching_slots']-per_user['before_matching_slots']
        paired.append(per_user)
    for t in totals.values():
        t['matching_slot_pct']=percentage(t['matching_slots'],t['slots'])
        t['users_with_match_pct_all_users']=percentage(t['users_with_match'],t['users'])
    a,b=totals['before'],totals['after']
    require(a['slots']==b['slots']==475, 'Frozen slot counts differ')
    delta=b['matching_slots']-a['matching_slots']
    return dict(variants=totals, delta_matching_slots=delta,
        delta_percentage_points=percentage(delta,a['slots']), paired_user_matches=paired,
        criterion=dict(definition='Retrospective technical criterion: higher matching-slot share with unchanged positive-category constraints and per-user list lengths',
                       formulated_post_hoc=True,prospective_success_threshold=None,
                       met=delta>0 and a['slots']==b['slots'] and a['category_violations']==b['category_violations']==0))


def evaluate(root=ROOT):
    result=calculate(*load(root))
    return dict(analysis='retrospective_rule_based_sport_fit', data_version='synthetic V2',
        source_sha256=dict(zip(SOURCES,HASHES)),
        script_sha256=digest(Path(__file__)),
        observation_period_end='2026-07-05',
        tag_mapping='Final manually confirmed mapping applied retrospectively to both saved variants; not claimed available at the historical observation cutoff',
        definition='A recommendation slot matches iff at least one final confirmed offer tag has historical sport share > 0 for that user. Count each slot once. Require positive interest category separately.',
        interpretation='Technical rule fit only; no real user survey, relevance labels, purchase probabilities or economic impact measured',
        temporal_scope='Profiles describe completed synthetic weeks through 2026-07-05; no later activity, target labels, model inference or future outcomes used',
        population='All 100 users in stored comparison, including five empty-list users; categories taken from that same stored comparison',
        calculation='JSON-decode stored ordered lists; validate keys, profiles, tags, candidates, lengths and documented ordering; count matches with one shared mapping; divide matching slots by all slots',
        reproduction='python src/recommendation_sport_fit.py', **result)


def payload(result):
    return (json.dumps(result,ensure_ascii=False,sort_keys=True,indent=2,allow_nan=False)+'\n').encode()


def write_result(path, data):
    if path.exists():
        require(path.read_bytes()==data, 'Refuse to overwrite differing result')
    else:
        path.parent.mkdir(parents=True,exist_ok=True)
        with path.open('xb') as stream:stream.write(data)


def main():
    result=evaluate()
    write_result(ROOT/OUTPUT,payload(result))
    for name,h in zip(SOURCES,HASHES):require(digest(ROOT/name)==h,'Source changed')
    print(json.dumps({k:result[k] for k in ['variants','delta_matching_slots','delta_percentage_points','criterion']},ensure_ascii=False,indent=2))


if __name__=='__main__':main()
