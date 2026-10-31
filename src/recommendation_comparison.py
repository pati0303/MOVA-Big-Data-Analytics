"""AP 6.3c: controlled tag-only comparison using existing engine matching.

No model inference or training; the two calls share exactly the same validated
user context and catalog. The approval file is never modified.
"""
import csv
from collections import Counter
import hashlib
import json
import os
from pathlib import Path
import recommendation_engine as engine

ROOT = engine.ROOT
EXPECTED_TAGS = {'O001': ('Running',), 'O003': ('Swimming',), 'O004': ('Tennis',),
                 'O005': ('Padel',), 'O006': ('Cycling',), 'O007': ('Strength',),
                 'O009': ('Hiking',), 'O010': ('Hiking',)}
GROUPS = ('unchanged', 'reordered_only', 'composition_changed')
INPUTS = ['data/raw/users_simulated.csv', 'data/raw/offers_simulated.csv',
          'data/raw/activities_simulated.csv', 'data/processed/kmeans_user_features.csv',
          'data/processed/user_weekly_activities.csv', 'data/processed/user_clusters.csv',
          'documentation/active_data_version.json', 'documentation/offer_sport_tags_approved.csv',
          'outputs/models/kmeans_scaling_params.json', 'src/recommendation_engine.py',
          'src/recommendation_comparison.py']


def digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def classify(before, after):
    if before == after:
        return 'unchanged'
    return 'reordered_only' if set(before) == set(after) else 'composition_changed'


def pct(numerator, denominator):
    return 100 * numerator / denominator if denominator else None


def compare(data):
    if len(data.users) != 100 or len(data.offers) != 30:
        raise ValueError('Expected 100 V2 users and 30 offers')
    if data.approved_tags != EXPECTED_TAGS:
        raise ValueError('Expected exactly the eight approved tag assignments')
    engine.index_unique(data.offers, 'offer_id')
    permissions = engine.permission_flags(True, True)
    results, raw = [], {}
    counts = {offer['offer_id']: dict(offer_id=offer['offer_id'], title=offer['title'],
              category=offer['category'], approved_sport_tags='|'.join(data.approved_tags.get(offer['offer_id'], ())),
              slots_before=0, slots_after=0, tier_a_after=0, entered=0, exited=0,
              retained_same_position=0, retained_changed_position=0) for offer in data.offers}
    category_users = {cat: set() for cat in engine.INTERESTS.values()}
    sport_slots = Counter()
    for uid in sorted(data.users):
        user = engine.select_user(data, uid)
        categories = engine.interest_categories(user)
        shares, status = engine.sport_profile(data, uid, engine.PROFILE_END)
        if status != 'available':
            raise ValueError(f'Invalid V2 profile: {uid}: {status}')
        # The only differing argument is the tag mapping. No second ranking logic.
        before = engine.recommendations(uid, data.offers, categories, {}, shares)
        after = engine.recommendations(uid, data.offers, categories, data.approved_tags, shares)
        ids0, ids1 = [[r['offer_id'] for r in frame] for frame in (before, after)]
        for frame, ids in [(before, ids0), (after, ids1)]:
            if len(ids) > 5 or len(ids) != len(set(ids)):
                raise ValueError('Invalid top-five output')
            if any(r['category'] not in categories for r in frame):
                raise ValueError('Category boundary violated')
        if any(r['ranking_tier'] != 'B' for r in before):
            raise ValueError('Unexpected tier A before approval')
        group = classify(ids0, ids1)
        results.append(dict(user_id=uid, categories=sorted(categories),
            eligible_offers=len(engine.filter_offers(data.offers, categories)),
            count_before=len(before), count_after=len(after), top5_before=ids0, top5_after=ids1,
            tier_a_before=0, tier_a_after=sum(r['ranking_tier']=='A' for r in after),
            ordered_list_changed=ids0!=ids1, composition_changed=set(ids0)!=set(ids1),
            shared_offer_position_changed=any(ids0.index(oid)!=ids1.index(oid) for oid in set(ids0)&set(ids1)),
            common_offers=len(set(ids0)&set(ids1)), change_group=group))
        raw[uid] = dict(categories=sorted(categories), sport_shares=shares, before=before, after=after)
        p0 = {oid: i for i, oid in enumerate(ids0)}
        p1 = {oid: i for i, oid in enumerate(ids1)}
        for oid in set(ids0)|set(ids1):
            c = counts[oid]
            c['slots_before'] += oid in p0
            c['slots_after'] += oid in p1
            c['entered'] += oid not in p0 and oid in p1
            c['exited'] += oid in p0 and oid not in p1
            if oid in p0 and oid in p1:
                c['retained_same_position'] += p0[oid] == p1[oid]
                c['retained_changed_position'] += p0[oid] != p1[oid]
            if p0.get(oid) != p1.get(oid):
                category_users[c['category']].add(uid)
        for rec in after:
            if rec['ranking_tier'] == 'A':
                oid = rec['offer_id']
                counts[oid]['tier_a_after'] += 1
                # Actual approved catalog has one tag per offer; one attribution per slot.
                sport_slots[data.approved_tags[oid][0]] += 1
    offers = []
    for oid in sorted(counts):
        row = counts[oid]
        row['slot_delta'] = row['slots_after'] - row['slots_before']
        offers.append(row)
    groups = Counter(r['change_group'] for r in results)
    slots0, slots1 = [sum(r[key] for r in results) for key in ['count_before','count_after']]
    tier_a = sum(r['tier_a_after'] for r in results)
    changed = len(results)-groups['unchanged']
    summary = dict(users=100, offers=30, as_of=engine.PROFILE_END.isoformat(),
        variants={'A_before': {'approved_tags': {}, 'permissions_simulated': permissions},
                  'B_after': {'approved_tags': data.approved_tags, 'permissions_simulated': permissions}},
        change_groups={g:groups[g] for g in GROUPS}, users_changed=changed,
        users_changed_pct=pct(changed,100), slots_before=slots0, slots_after=slots1,
        tier_a_before=0, tier_b_before=slots0, tier_a_after=tier_a, tier_b_after=slots1-tier_a,
        tier_a_after_pct=pct(tier_a,slots1), users_with_tier_a=sum(r['tier_a_after']>0 for r in results),
        mean_common_offers=sum(r['common_offers'] for r in results)/100,
        users_no_positive_interests=sum(not r['categories'] for r in results),
        users_fewer_than_five_eligible=sum(r['eligible_offers']<5 for r in results),
        users_positive_interests_fewer_than_five_eligible=sum(0<r['eligible_offers']<5 for r in results),
        tier_a_slots_by_sport=dict(sorted(sport_slots.items())),
        category_analysis={cat:dict(slots_before=sum(o['slots_before'] for o in offers if o['category']==cat),
            slots_after=sum(o['slots_after'] for o in offers if o['category']==cat),
            users_with_entry_exit_or_position_change=len(category_users[cat])) for cat in sorted(category_users)},
        metric_definitions={'users_changed_pct_denominator':100, 'tier_a_after_pct_denominator':slots1,
            'mean_common_offers_denominator':100,
            'ordered_list_changed':'Lists differ; includes composition changes.',
            'shared_offer_position_changed':'At least one retained offer changes position; also possible with composition change.',
            'sport_attribution':'One confirmed tag per actual offer; no duplicated slot counts.',
            'fewer_than_five':'Includes zero eligible offers; positive-interest subset reported separately.'})
    examples = []
    for group in GROUPS:
        available=[r for r in results if r['change_group']==group]
        if available:
            row=next((r for r in available if r['count_after']>0), available[0])
            examples.append(dict(user_id=row['user_id'],change_group=group,**raw[row['user_id']]))
    for row in results:
        if len(examples)>=3:break
        if row['user_id'] not in {r['user_id'] for r in examples}:
            examples.append(dict(user_id=row['user_id'],change_group=row['change_group'],**raw[row['user_id']]))
    summary['examples']=examples
    assert sum(summary['change_groups'].values())==100
    return results, offers, summary


def write_csv(path, rows):
    with path.open('w',encoding='utf-8',newline='') as stream:
        writer=csv.DictWriter(stream,fieldnames=list(rows[0]),lineterminator='\n')
        writer.writeheader()
        for row in rows:
            writer.writerow({k:json.dumps(v,ensure_ascii=False,separators=(',',':'))
                             if isinstance(v,(list,dict)) else v for k,v in row.items()})


def plots(summary, root):
    os.environ.setdefault('MPLCONFIGDIR', str(root/'work/matplotlib'))
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    with plt.rc_context({'font.family':'DejaVu Sans','font.size':11}):
        fig,ax=plt.subplots(figsize=(9,5.2),layout='constrained')
        values=[summary['change_groups'][g] for g in GROUPS]
        bars=ax.bar(['Unveränderte\nListe','Nur Reihenfolge\nverändert','Zusammensetzung\nverändert'],values,
                    color=['#65758b','#45a6a3','#215e96'])
        ax.bar_label(bars,padding=4);ax.set_ylim(0,max(values)+12)
        ax.set_ylabel('Anzahl Nutzer (N = 100)');ax.set_title('Wirkung der acht bestätigten Sporttags auf die Top 5')
        fig.savefig(root/'outputs/figures/recommendation_before_after_users.png',dpi=160,metadata={'Software':'MOVA AP 6.3c'})
        plt.close(fig)
        fig,ax=plt.subplots(figsize=(9,5.2),layout='constrained')
        a=[summary['tier_a_before'],summary['tier_a_after']]
        b=[summary['tier_b_before'],summary['tier_b_after']]
        ba=ax.bar(['Vorher: keine Tags','Nachher: acht Tags'],a,color='#215e96',label='Stufe A: bestätigter Sportbezug + beobachtete Sportart')
        bb=ax.bar(['Vorher: keine Tags','Nachher: acht Tags'],b,bottom=a,color='#b8c7d8',label='Stufe B: übrige zulässige Angebote')
        ax.bar_label(ba,label_type='center',labels=[str(v) if v else '' for v in a])
        ax.bar_label(bb,label_type='center');ax.set_ylabel('Ausgegebene Empfehlungsslots\n(100 Nutzer, maximal 5 je Nutzer)')
        ax.set_ylim(0,max(summary['slots_before'],summary['slots_after'])*1.23)
        ax.set_title('Verteilung der Stufen vor und nach der Tagfreigabe')
        ax.legend(loc='upper center',bbox_to_anchor=(.5,-.08),fontsize=9)
        fig.savefig(root/'outputs/figures/recommendation_before_after_tiers.png',dpi=160,metadata={'Software':'MOVA AP 6.3c'})
        plt.close(fig)


def main(root=ROOT):
    root=Path(root)
    checksums={p:digest(root/p) for p in INPUTS}
    users,offers,summary=compare(engine.load_data(root,include_activity=True))
    summary['input_sha256']=checksums
    summary['models_used_for_ranking']=False
    summary['model_inference_performed']=False
    summary['model_artifact_sha256']={p:digest(root/p) for p in
        ['outputs/models/kmeans_final.joblib','outputs/models/regression_linear.joblib']}
    for folder in ['outputs/tables','outputs/figures']:(root/folder).mkdir(parents=True,exist_ok=True)
    write_csv(root/'outputs/tables/recommendation_before_after_users.csv',users)
    write_csv(root/'outputs/tables/recommendation_before_after_offers.csv',offers)
    (root/'outputs/tables/recommendation_before_after_summary.json').write_text(
        json.dumps(summary,ensure_ascii=False,indent=2,sort_keys=True,allow_nan=False)+'\n',encoding='utf-8')
    plots(summary,root)
    assert checksums=={p:digest(root/p) for p in INPUTS}, 'Inputs changed during comparison'
    return summary


if __name__=='__main__':
    s=main()
    print(json.dumps({k:v for k,v in s.items() if k not in ['examples','input_sha256','variants']},ensure_ascii=False,indent=2))
