"""AP 4.2: geprüfte V2-Aktivitäten in ein vollständiges Wochenraster integrieren.

Aufruf: python src/data_preparation_weekly.py; nur Standardbibliothek.
Keine Generatoren, Merkmalsfenster, Skalierung oder Modelle.
"""
import csv
import io
import json
import re
import sys
from collections import defaultdict
from datetime import date, timedelta
from decimal import Decimal
from pathlib import Path

from data_preparation_selection import COLUMNS, LIMITS, QualityError, number, read_csv, require, sha256

ROOT = Path(__file__).resolve().parents[1]
START = date(2026, 1, 5)
END = date(2026, 7, 5)
OUTPUT_COLUMNS = ['user_id', 'week_index', 'week_start', 'week_end',
                  'activities_count', 'total_duration_min']
SELECTED_HASH = '1dc3617cc2f9640bede26cae532bf2231fa3d7a7b3e97adc42d4d830a7f81fa1'


def monday(day):
    """Montag der einschließenden Woche, auch für Sonntage korrekt."""
    return day - timedelta(days=day.weekday())


def construct(activities, users):
    """Schritte 2–7: zuerst jede Eingabe prüfen, dann aggregieren und integrieren."""
    require(len(users) == 100 and len(set(users)) == 100, 'Nutzerliste nicht eindeutig/vollständig')
    require(all(re.fullmatch(r'U[0-9]{3}', uid) for uid in users), 'Ungültige Nutzerkennung')
    known = set(users)
    ids = set()
    parsed = []
    # 2. Pflichtwerte und Datum prüfen; unbekannte Daten niemals zu Null machen.
    for line, row in enumerate(activities, 2):
        label = f'Aktivitätszeile {line}'
        require(set(row) == set(COLUMNS) and all(isinstance(row[c], str) and row[c].strip()
                                               for c in COLUMNS), f'{label}: Pflichtwert/Schema')
        require(re.fullmatch(r'A[0-9]{6}', row['activity_id']) is not None, f'{label}: ID-Format')
        require(row['activity_id'] not in ids, f'{label}: doppelte Aktivitäts-ID')
        ids.add(row['activity_id'])
        require(row['user_id'] in known, f'{label}: unbekannter Nutzer')
        require(row['sport_type'] in LIMITS, f'{label}: unbekannte Sportart')
        day = date.fromisoformat(row['date'])
        require(day.isoformat() == row['date'] and START <= day <= END, f'{label}: Datum/Zeitraum')
        duration = number(row['duration_min'], label + ' Dauer')
        low, high, _, _ = LIMITS[row['sport_type']]
        require(low <= duration <= high, f'{label}: Dauer außerhalb Sportgrenzen')
        parsed.append((row['user_id'], day, duration))

    # 3. Montag und relativen Wochenindex ableiten; Einschluss jeder Aktivität prüfen.
    assigned = []
    for uid, day, duration in parsed:
        start = monday(day)
        index = (start - START).days // 7 + 1
        end = start + timedelta(days=6)
        require(start.weekday() == 0 and end.weekday() == 6 and start <= day <= end,
                'Fehlerhafte Kalenderzuordnung')
        require(1 <= index <= 26 and start == START + timedelta(weeks=index - 1),
                'Wochenindex außerhalb Kalender')
        assigned.append((uid, index, duration))

    # 4. Nur aufgezeichnete Aktivitäten zählen, Originalminuten exakt addieren.
    aggregate = defaultdict(lambda: [0, Decimal('0')])
    for uid, index, duration in assigned:
        aggregate[uid, index][0] += 1
        aggregate[uid, index][1] += duration

    # 5–7. Vollständige Nutzerliste × Kalender; nur fehlende Gruppen mit Null ergänzen.
    result = []
    for uid in sorted(users):
        for index in range(1, 27):
            start = START + timedelta(weeks=index - 1)
            count, duration = aggregate.get((uid, index), (0, Decimal('0')))
            result.append(dict(zip(OUTPUT_COLUMNS, [uid, str(index), start.isoformat(),
                          (start + timedelta(days=6)).isoformat(), str(count), str(duration)])))
    return result, len(aggregate)


def validate(rows, activities, users, control):
    """Schritt 8: vollständiger Kalender, unabhängige Kontrolle und Summenerhalt."""
    keys = [(r['user_id'], int(r['week_index'])) for r in rows]
    expected = [(uid, i) for uid in sorted(users) for i in range(1, 27)]
    require(len(rows) == 2600 and keys == expected and len(set(keys)) == 2600,
            'Raster, Sortierung oder eindeutige Schlüssel fehlerhaft')
    counts = {}
    zero = 0
    for row in rows:
        require(list(row) == OUTPUT_COLUMNS, 'Ausgabeschema falsch')
        start, end = date.fromisoformat(row['week_start']), date.fromisoformat(row['week_end'])
        require(start == START + timedelta(weeks=int(row['week_index']) - 1), 'Wochenbeginn falsch')
        require(end == start + timedelta(days=6) and START <= start <= end <= END,
                'Woche umfasst nicht sieben Kalendertage')
        require(row['activities_count'].isdigit(), 'Aktivitätszahl nicht ganzzahlig/nicht negativ')
        count = int(row['activities_count'])
        duration = number(row['total_duration_min'], 'Wochenminuten')
        require(count <= 10, 'V2-Wochenzahl über dokumentiertem Maximum')
        if count == 0:
            zero += 1
            require(duration == 0, 'Nullwoche mit Minuten')
        else:
            require(duration > 0, 'Aktive Woche ohne Minuten')
        counts[row['user_id'], row['week_start']] = count
    reference = {}
    for row in control:
        key = row['user_id'], row['week_start']
        require(key not in reference and row['activity_count'].isdigit(), 'Wochenkontrolle ungültig')
        reference[key] = int(row['activity_count'])
    require(reference == counts, 'Abweichende Schlüssel/Zählungen gegenüber Wochenkontrolle')
    require(zero == 558, f'Nullwochen abweichend: {zero}')
    require(sum(counts.values()) == len(activities) == 6465, 'Aktivitätensumme abweichend')
    minutes = sum(Decimal(r['total_duration_min']) for r in rows)
    require(minutes == sum(Decimal(r['duration_min']) for r in activities) == Decimal('422829.9'),
            'Trainingsminutensumme abweichend')
    # Unabhängige zweite Zuordnung: Intervallfilter statt Montag-/Indexberechnung.
    grouped = defaultdict(list)
    for activity in activities:
        grouped[activity['user_id']].append(activity)
    for row in rows:
        matches = [a for a in grouped[row['user_id']] if row['week_start'] <= a['date'] <= row['week_end']]
        require(len(matches) == int(row['activities_count']) and
                sum((Decimal(a['duration_min']) for a in matches), Decimal('0')) ==
                Decimal(row['total_duration_min']), 'Einzelaktivitäten falsch zugeordnet')


def main():
    # 1. Daten laden: aktive V2 und AP-4.1-Ausgabe vor Verarbeitung verifizieren.
    manifest = json.loads((ROOT / 'documentation/active_data_version.json').read_text())
    require(manifest['active_version'] == 'V2', 'Keine aktive V2')
    paths = dict(manifest['sha256'])
    paths['data/processed/activities_selected.csv'] = SELECTED_HASH
    for name, expected in paths.items():
        require(sha256(ROOT / name) == expected, f'Eingabehash abweichend: {name}')
    activities = read_csv(ROOT / 'data/processed/activities_selected.csv', COLUMNS)
    users = read_csv(ROOT / 'data/raw/users_simulated.csv',
                     ['user_id', 'interest_sport', 'interest_outdoor', 'interest_wellness', 'interest_leisure'])
    control = read_csv(ROOT / 'outputs/tables/simulation_weekly_check.csv',
                       ['user_id', 'week_start', 'activity_count'])
    user_ids = [r['user_id'] for r in users]
    rows, active_groups = construct(activities, user_ids)
    validate(rows, activities, user_ids, control)

    # Erst nach allen Prüfungen exportieren; abweichende Dateien niemals ersetzen.
    buffer = io.StringIO(newline='')
    writer = csv.DictWriter(buffer, fieldnames=OUTPUT_COLUMNS, lineterminator='\n')
    writer.writeheader()
    writer.writerows(rows)
    payload = buffer.getvalue().encode('utf-8')
    output = ROOT / 'data/processed/user_weekly_activities.csv'
    if output.exists():
        require(output.read_bytes() == payload, 'Bestehende Ausgabe abweichend; nicht überschrieben')
    else:
        with output.open('xb') as stream:
            stream.write(payload)
    exported = read_csv(output, OUTPUT_COLUMNS)
    require(exported == rows, 'Export-Rücklesen abweichend')
    validate(exported, activities, user_ids, control)
    for name, expected in paths.items():
        require(sha256(ROOT / name) == expected, f'Eingabe nach Lauf verändert: {name}')
    print(json.dumps({'status': 'bestanden', 'version': 'V2', 'rows': len(rows),
                      'columns': OUTPUT_COLUMNS, 'users': len(user_ids), 'weeks_per_user': 26,
                      'active_user_weeks_before': active_groups, 'zero_weeks_added': 2600-active_groups,
                      'total_activities': sum(int(r['activities_count']) for r in rows),
                      'total_duration_min': str(sum(Decimal(r['total_duration_min']) for r in rows)),
                      'control_keys_matched': len(control), 'input_hashes_unchanged': True,
                      'output_sha256': sha256(output)}, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    try:
        main()
    except (QualityError, ValueError, OSError, KeyError) as exc:
        print(f'ABBRUCH: {exc}\nKeine automatische Korrektur. Quelle prüfen und Befund dokumentieren.',
              file=sys.stderr)
        sys.exit(1)
