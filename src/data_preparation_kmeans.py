"""AP 4.3: unskalierte Nutzermerkmale aus aktiver V2, keine Modellierung.

Aufruf: python src/data_preparation_kmeans.py (nur Standardbibliothek).
"""
import csv
import io
import json
import math
import sys
from collections import Counter, defaultdict
from decimal import Decimal
from pathlib import Path

from data_preparation_selection import COLUMNS, QualityError, read_csv, require, sha256
from data_preparation_weekly import OUTPUT_COLUMNS, SELECTED_HASH, validate as validate_weekly

ROOT = Path(__file__).resolve().parents[1]
SPORTS = ['Running', 'Cycling', 'Strength', 'Swimming', 'Walking', 'Hiking', 'Tennis', 'Padel']
SHARES = ['share_' + sport.lower() for sport in SPORTS]
MODEL_FEATURES = ['avg_activities_per_week'] + SHARES
INTERPRETATION_FEATURES = ['avg_duration_per_week', 'sport_diversity']
FEATURE_COLUMNS = ['user_id'] + MODEL_FEATURES + INTERPRETATION_FEATURES
WEEKS = 26
ABS_TOL = 1e-9
REL_TOL = 1e-12
WEEKLY_HASH = 'c34a7bd16d1cdc3e91388cc35b8c784afde0b53c1dbfdd24de97148350359b74'


def close(actual, expected, label):
    require(math.isclose(float(actual), float(expected), rel_tol=REL_TOL, abs_tol=ABS_TOL), label)


def construct_features(activities, users):
    """Schritte 2–6; vollständige Nutzerliste führt die Integration an."""
    require(len(users) == len(set(users)), 'Doppelte Nutzer in Nutzerliste')
    known = set(users)
    ids = set()
    for row in activities:
        require(row['user_id'] in known, 'Unbekannter Nutzer')
        require(row['sport_type'] in SPORTS, 'Unbekannte Sportart')
        require(row['activity_id'] and row['activity_id'] not in ids, 'Fehlende/doppelte Aktivitäts-ID')
        ids.add(row['activity_id'])
        value = Decimal(row['duration_min'])
        require(value.is_finite() and value >= 0, 'Ungültige Trainingsdauer')

    # 2. Aktivitäten zählen: keine Beschränkung auf aktive Wochen.
    counts = Counter(row['user_id'] for row in activities)
    # 3. Minuten je Nutzer exakt summieren, erst Wochenmittel als Float darstellen.
    minutes = defaultdict(lambda: Decimal('0'))
    for row in activities:
        minutes[row['user_id']] += Decimal(row['duration_min'])
    # 4. Sportcounts liefern Anteile; fehlender Sport bei aktivem Nutzer = echte 0.
    sport_counts = Counter((row['user_id'], row['sport_type']) for row in activities)
    result = []
    inactive = []
    for uid in sorted(users):
        count = counts[uid]
        mix = [sport_counts[uid, sport] / count if count else None for sport in SPORTS]
        # 5. Zahl tatsächlich beobachteter Sportarten, kein geschätztes Repertoire.
        diversity = sum(sport_counts[uid, sport] > 0 for sport in SPORTS)
        # 6. Links-Integration: auch vollständig inaktive Nutzer bleiben enthalten.
        row = dict(zip(FEATURE_COLUMNS, [uid, count / WEEKS, *mix,
                         float(minutes[uid] / WEEKS), diversity]))
        result.append(row)
        if count == 0:
            inactive.append({'user_id': uid, 'eligibility_status': 'inactive_no_sport_mix'})
    return result, inactive


def validate_features(rows, activities, users, weekly):
    """Schritt 7: Werte gegen Einzelaktivitäten und bestehende Wochen prüfen."""
    require(len(rows) == len(users) and [r['user_id'] for r in rows] == sorted(users),
            'Nutzer unvollständig, doppelt oder unsortiert')
    grouped = defaultdict(list)
    for activity in activities:
        grouped[activity['user_id']].append(activity)
    weekly_counts = Counter()
    weekly_minutes = defaultdict(lambda: Decimal('0'))
    weekly_indices = defaultdict(set)
    seen = set()
    for row in weekly:
        uid, index = row['user_id'], int(row['week_index'])
        require(uid in users and (uid, index) not in seen and 1 <= index <= WEEKS,
                'Ungültiger Nutzer-Wochen-Schlüssel')
        seen.add((uid, index))
        weekly_indices[uid].add(index)
        require(row['activities_count'].isdigit(), 'Ungültiger Wochencount')
        duration = Decimal(row['total_duration_min'])
        require(duration.is_finite() and duration >= 0, 'Ungültige Wochenminuten')
        weekly_counts[uid] += int(row['activities_count'])
        weekly_minutes[uid] += duration
    require(len(weekly) == len(users) * WEEKS and
            all(weekly_indices[uid] == set(range(1, WEEKS + 1)) for uid in users),
            'Wochen nicht vollständig')
    for row in rows:
        require(list(row) == FEATURE_COLUMNS, 'Falsches Merkmalsschema')
        uid = row['user_id']
        source = grouped[uid]
        count = len(source)
        minutes = sum((Decimal(a['duration_min']) for a in source), Decimal('0'))
        require(count == weekly_counts[uid] and minutes == weekly_minutes[uid],
                f'{uid}: Einzelaktivitäten und Wochen weichen ab')
        for name in ['avg_activities_per_week', *INTERPRETATION_FEATURES]:
            value = row[name]
            require(math.isfinite(value) and value >= 0, f'{uid}: ungültiges Merkmal {name}')
        close(row['avg_activities_per_week'] * WEEKS, count, f'{uid}: Aktivitätsrekonstruktion')
        close(row['avg_duration_per_week'] * WEEKS, minutes, f'{uid}: Minutenrekonstruktion')
        expected_diversity = len({a['sport_type'] for a in source})
        require(isinstance(row['sport_diversity'], int) and
                row['sport_diversity'] == expected_diversity, f'{uid}: Sportvielfalt falsch')
        if not count:
            require(all(row[col] is None for col in SHARES), f'{uid}: künstlicher Sportmix')
            require(row['avg_activities_per_week'] == row['avg_duration_per_week'] ==
                    row['sport_diversity'] == 0, f'{uid}: Inaktivitätsregel verletzt')
            continue
        require(1 <= row['sport_diversity'] <= 8, f'{uid}: ungültige Sportvielfalt')
        require(all(row[c] is not None and math.isfinite(row[c]) and 0 <= row[c] <= 1
                    for c in SHARES), f'{uid}: ungültiger Anteil')
        close(math.fsum(row[c] for c in SHARES), 1, f'{uid}: Anteilssumme')
        for sport, col in zip(SPORTS, SHARES):
            close(row[col], sum(a['sport_type'] == sport for a in source) / count,
                  f'{uid}: Sportanteil falsch')
    close(math.fsum(r['avg_activities_per_week'] * WEEKS for r in rows),
          len(activities), 'Gesamtaktivitäten nicht erhalten')
    close(math.fsum(r['avg_duration_per_week'] * WEEKS for r in rows),
          sum(Decimal(a['duration_min']) for a in activities), 'Gesamtminuten nicht erhalten')


def main():
    # 1. Daten laden und prüfen; keine bestehende Datei neu erzeugen.
    manifest = json.loads((ROOT / 'documentation/active_data_version.json').read_text())
    require(manifest['active_version'] == 'V2' and manifest['weeks'] == WEEKS, 'Kein gültiger V2-Vertrag')
    hashes = dict(manifest['sha256'])
    hashes.update({'data/processed/activities_selected.csv': SELECTED_HASH,
                   'data/processed/user_weekly_activities.csv': WEEKLY_HASH})
    for name, expected in hashes.items():
        require(sha256(ROOT / name) == expected, f'Eingabehash abweichend: {name}')
    activities = read_csv(ROOT / 'data/processed/activities_selected.csv', COLUMNS)
    users = read_csv(ROOT / 'data/raw/users_simulated.csv',
                    ['user_id', 'interest_sport', 'interest_outdoor', 'interest_wellness', 'interest_leisure'])
    user_ids = [row['user_id'] for row in users]
    weekly = read_csv(ROOT / 'data/processed/user_weekly_activities.csv', OUTPUT_COLUMNS)
    control = read_csv(ROOT / 'outputs/tables/simulation_weekly_check.csv',
                       ['user_id', 'week_start', 'activity_count'])
    # Vorhandene Wochen nur validieren, keine Wochenaggregation neu exportieren.
    validate_weekly(weekly, activities, user_ids, control)
    require(len(users) == len(set(user_ids)) == 100 and len(activities) == 6465,
            'V2-Nutzer-/Aktivitätsanzahl abweichend')
    require(sum(Decimal(a['duration_min']) for a in activities) == Decimal('422829.9'),
            'V2-Minuten abweichend')
    rows, inactive = construct_features(activities, user_ids)
    validate_features(rows, activities, user_ids, weekly)
    require(not inactive and all(value is not None for row in rows for value in row.values()),
            'Aktuelle V2 unerwartet inaktiv/fehlend')

    # 8. Deterministischer Export; Interpretationsspalten sind nicht Teil von MODEL_FEATURES.
    buffer = io.StringIO(newline='')
    writer = csv.DictWriter(buffer, fieldnames=FEATURE_COLUMNS, lineterminator='\n')
    writer.writeheader()
    writer.writerows(rows)  # None wäre ein leeres CSV-Feld, niemals ein künstlicher Nullmix.
    payload = buffer.getvalue().encode('utf-8')
    output = ROOT / 'data/processed/kmeans_user_features.csv'
    if output.exists():
        require(output.read_bytes() == payload, 'Vorhandene Ausgabe abweichend; nicht überschrieben')
    else:
        with output.open('xb') as stream:
            stream.write(payload)
    loaded = read_csv(output, FEATURE_COLUMNS)
    converted = []
    for row in loaded:
        converted.append({col: row[col] if col == 'user_id' else
                          int(row[col]) if col == 'sport_diversity' else
                          None if row[col] == '' else float(row[col]) for col in FEATURE_COLUMNS})
    require(converted == rows, 'Export-Rücklesen abweichend')
    validate_features(converted, activities, user_ids, weekly)
    for name, expected in hashes.items():
        require(sha256(ROOT / name) == expected, f'Eingabe verändert: {name}')
    print(json.dumps({'status': 'bestanden', 'rows': len(rows), 'columns': FEATURE_COLUMNS,
                      'model_features_unscaled': MODEL_FEATURES,
                      'interpretation_only': INTERPRETATION_FEATURES,
                      'eligible_users': len(rows) - len(inactive), 'inactive_users': inactive,
                      'weekly_users_matched': len(user_ids), 'activities_total': len(activities),
                      'duration_total_min': str(sum(Decimal(a['duration_min']) for a in activities)),
                      'diversity_min': min(r['sport_diversity'] for r in rows),
                      'diversity_max': max(r['sport_diversity'] for r in rows),
                      'abs_tolerance': ABS_TOL, 'rel_tolerance': REL_TOL,
                      'input_hashes_unchanged': True, 'output_sha256': sha256(output)},
                     ensure_ascii=False, indent=2))


if __name__ == '__main__':
    try:
        main()
    except (QualityError, ValueError, ArithmeticError, OSError, KeyError) as exc:
        print(f'ABBRUCH: {exc}\nKeine automatische Korrektur. Quelle und Befund prüfen.', file=sys.stderr)
        sys.exit(1)
