"""AP 4.5: vergangenheitsbezogene Regressionsmerkmale und beobachtetes Folgeziel.

Aufruf: python src/data_preparation_regression.py (nur Standardbibliothek).
Keine neue Wochenaggregation, keine Aufteilung, kein Training und keine Prognosen.
"""
import csv
import io
import json
import math
import sys
from collections import defaultdict
from datetime import date, timedelta
from decimal import Decimal
from pathlib import Path

from data_preparation_selection import QualityError, read_csv, require, sha256
from data_preparation_weekly import OUTPUT_COLUMNS as WEEKLY_COLUMNS

ROOT = Path(__file__).resolve().parents[1]
START = date(2026, 1, 5)
WEEKS = 26
INPUT_HASH = 'c34a7bd16d1cdc3e91388cc35b8c784afde0b53c1dbfdd24de97148350359b74'
MODEL_FEATURES = ['activities_current_week', 'avg_activities_last_4_weeks']
TARGET = 'activities_next_week'
METADATA = ['user_id', 'week_index', 'week_start', 'week_end']
OUTPUT_COLUMNS = METADATA + MODEL_FEATURES + [TARGET]
TOL = 1e-10


def check_weekly(rows, users):
    """Schritt 2: fehlende/ungültige Wochen ablehnen, niemals auffüllen."""
    require(len(users) == 100 and len(set(users)) == 100, 'Nutzerliste nicht vollständig/eindeutig')
    require(len(rows) == 2600, 'Wochenraster muss 2.600 Zeilen enthalten')
    known = set(users)
    keys = set()
    groups = defaultdict(list)
    for line, row in enumerate(rows, 2):
        label = f'Wochenzeile {line}'
        require(list(row) == WEEKLY_COLUMNS and all(isinstance(v, str) and v.strip() for v in row.values()),
                f'{label}: Schema oder Pflichtwert ungültig')
        uid = row['user_id']
        require(uid in known, f'{label}: unbekannter Nutzer')
        require(row['week_index'].isdigit(), f'{label}: ungültiger Wochenindex')
        index = int(row['week_index'])
        key = uid, index
        require(key not in keys and 1 <= index <= WEEKS, f'{label}: doppelte/ungültige Woche')
        keys.add(key)
        begin, end = date.fromisoformat(row['week_start']), date.fromisoformat(row['week_end'])
        require(begin.isoformat() == row['week_start'] and end.isoformat() == row['week_end'],
                f'{label}: Datum nicht strikt ISO')
        require(begin == START + timedelta(weeks=index - 1) and end == begin + timedelta(days=6),
                f'{label}: falsches Montag-Sonntag-Intervall')
        require(row['activities_count'].isdigit(), f'{label}: Aktivitätszahl nicht ganzzahlig/nicht negativ')
        count = int(row['activities_count'])
        minutes = Decimal(row['total_duration_min'])
        require(count <= 10 and minutes.is_finite() and minutes >= 0, f'{label}: ungültige V2-Zahlen')
        require((count == 0 and minutes == 0) or (count > 0 and minutes > 0),
                f'{label}: Aktivitätszahl/Minuten inkonsistent')
        groups[uid].append(row)
    expected = {(uid, index) for uid in users for index in range(1, WEEKS + 1)}
    require(keys == expected, 'Fehlende Nutzerwochen; keine künstliche Historie erlaubt')
    return groups


def construct_features(rows, users):
    """Schritte 2–6: gruppiert sortieren, trailing Fenster und Folgeziel bilden."""
    groups = check_weekly(rows, users)
    output = []
    for uid in sorted(users):
        # 3. Chronologische Ordnung innerhalb jedes Nutzers, ohne Nutzergrenzübertritt.
        weeks = sorted(groups[uid], key=lambda row: int(row['week_index']))
        counts = [int(row['activities_count']) for row in weeks]
        for position, week in enumerate(weeks):
            # 4. Nur vier vollständig beobachtete Wochen einschließlich t, echte 0 behalten.
            average = sum(counts[position-3:position+1]) / 4 if position >= 3 else None
            # 5. Gruppenbezogene Verschiebung um eine Woche, keine unbeobachtete Zukunft = 0.
            target = counts[position+1] if position+1 < len(counts) else None
            # 6. Erste drei und letzte Eingabewoche lediglich vom Export ausnehmen.
            if average is None or target is None:
                continue
            output.append(dict(zip(OUTPUT_COLUMNS, [uid, int(week['week_index']),
                          week['week_start'], week['week_end'], counts[position], average, target])))
    return output


def validate(rows, weekly, users):
    """Schritt 7: unabhängige Prüfung anhand von Datumsadressen statt Listenfenstern."""
    require(len(rows) == 2200, 'Ergebnis muss 2.200 Zeilen haben')
    expected = [(uid, index) for uid in sorted(users) for index in range(4, 26)]
    keys = [(row['user_id'], row['week_index']) for row in rows]
    require(keys == expected and len(set(keys)) == 2200, 'Nutzer/Zeiten unvollständig, doppelt oder unsortiert')
    source = {(r['user_id'], r['week_start']): r for r in weekly}
    require(len(source) == 2600, 'Wochenquelle nicht eindeutig/vollständig')
    for row in rows:
        uid, index = row['user_id'], row['week_index']
        require(list(row) == OUTPUT_COLUMNS and all(value is not None for value in row.values()),
                f'{uid}/{index}: Schema/Fehlwert')
        begin = date.fromisoformat(row['week_start'])
        require(begin == START + timedelta(weeks=index - 1) and
                row['week_end'] == (begin + timedelta(days=6)).isoformat(), 'Ausgabekalender falsch')
        history = [source[(uid, (begin - timedelta(weeks=lag)).isoformat())] for lag in range(4)]
        next_week = source[(uid, (begin + timedelta(weeks=1)).isoformat())]
        for name in MODEL_FEATURES + [TARGET]:
            value = row[name]
            require(isinstance(value, (int, float)) and not isinstance(value, bool) and
                    math.isfinite(value) and value >= 0, f'{uid}/{index}: ungültiger Wert {name}')
        require(type(row['activities_current_week']) is int and type(row[TARGET]) is int,
                'Aktivitätszahl/Ziel muss Integer sein')
        require(row['activities_current_week'] == int(history[0]['activities_count']), 'Aktuelle Woche falsch')
        reference = sum(Decimal(h['activities_count']) for h in history) / Decimal(4)
        require(math.isclose(row['avg_activities_last_4_weeks'], float(reference), abs_tol=TOL, rel_tol=TOL),
                f'{uid}/{index}: Vierwochenmittel falsch oder Zukunft enthalten')
        require(row[TARGET] == int(next_week['activities_count']), f'{uid}/{index}: Folgeziel falsch')
        require(all(h['user_id'] == uid and h['week_end'] <= row['week_end'] for h in history),
                'Nutzervermischung/Zukunft im Fenster')
        require(next_week['user_id'] == uid and int(next_week['week_index']) == index+1 and
                date.fromisoformat(next_week['week_start']) > date.fromisoformat(row['week_end']),
                'Zielwoche nicht korrekt zeitlich nach Eingabe')


def main():
    # 1. Bestehende Wochen laden, aktive V2 und Quellhash vor jeder Verarbeitung prüfen.
    manifest = json.loads((ROOT/'documentation/active_data_version.json').read_text())
    require(manifest['active_version'] == 'V2', 'Keine aktive V2')
    hashes = dict(manifest['sha256'])
    hashes['data/processed/user_weekly_activities.csv'] = INPUT_HASH
    for name, expected in hashes.items():
        require(sha256(ROOT/name) == expected, f'Eingabehash abweichend: {name}')
    weekly = read_csv(ROOT/'data/processed/user_weekly_activities.csv', WEEKLY_COLUMNS)
    users = [r['user_id'] for r in read_csv(ROOT/'data/raw/users_simulated.csv',
             ['user_id','interest_sport','interest_outdoor','interest_wellness','interest_leisure'])]
    check_weekly(weekly, users)
    require(sum(int(r['activities_count']) for r in weekly) == 6465 and
            sum(Decimal(r['total_duration_min']) for r in weekly) == Decimal('422829.9') and
            sum(int(r['activities_count']) == 0 for r in weekly) == 558, 'V2-Summen abweichend')
    rows = construct_features(weekly, users)
    validate(rows, weekly, users)
    # 8. Export erst nach Validierung; niemals bestehende abweichende Dateien ersetzen.
    buffer = io.StringIO(newline='')
    writer = csv.DictWriter(buffer, fieldnames=OUTPUT_COLUMNS, lineterminator='\n')
    writer.writeheader()
    writer.writerows(rows)
    payload = buffer.getvalue().encode('utf-8')
    output = ROOT/'data/processed/regression_weekly_features.csv'
    if output.exists():
        require(output.read_bytes() == payload, 'Vorhandene Ausgabe abweichend; nicht überschrieben')
    else:
        with output.open('xb') as stream:
            stream.write(payload)
    loaded = read_csv(output, OUTPUT_COLUMNS)
    converted = [{name: int(value) if name in ['week_index','activities_current_week',TARGET] else
                  float(value) if name == 'avg_activities_last_4_weeks' else value
                  for name,value in row.items()} for row in loaded]
    require(converted == rows, 'Export-Rücklesen nicht identisch')
    validate(converted, weekly, users)
    for name, expected in hashes.items():
        require(sha256(ROOT/name) == expected, f'Eingabe verändert: {name}')
    print(json.dumps({'status':'bestanden', 'version':'V2', 'rows':len(rows), 'columns':OUTPUT_COLUMNS,
         'users':len(users), 'rows_per_user':22, 'input_week_range':[4,25], 'target_week_range':[5,26],
         'excluded_early_rows':300, 'excluded_last_rows':100, 'source_zero_weeks':558,
         'model_rows_with_current_zero':sum(r['activities_current_week']==0 for r in rows),
         'model_rows_with_zero_target':sum(r[TARGET]==0 for r in rows),
         'model_rows_with_zero_in_history':sum(any(int(w['activities_count'])==0 for w in weekly
            if w['user_id']==r['user_id'] and r['week_index']-3 <= int(w['week_index']) <= r['week_index']) for r in rows),
         'input_hashes_unchanged':True, 'train_test_split_created':False,
         'output_sha256':sha256(output)}, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    try:
        main()
    except (QualityError, ValueError, ArithmeticError, OSError, KeyError) as exc:
        print(f'ABBRUCH: {exc}\nKeine automatische Auffüllung. Quelle und Befund prüfen.', file=sys.stderr)
        sys.exit(1)
