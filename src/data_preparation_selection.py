"""AP 4.1: aktive V2 prüfen und fünf Aktivitätsspalten verlustfrei auswählen.

Aufruf: python src/data_preparation_selection.py (keine externen Pakete).
Keine Reparaturen, Aggregationen oder Modellmerkmale. Fehler stoppen den Export.
"""
import csv
import hashlib
import io
import json
import re
import sys
from collections import Counter
from datetime import date
from decimal import Decimal, InvalidOperation
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
COLUMNS = ['activity_id', 'user_id', 'date', 'sport_type', 'duration_min']
# Fachliche Grenzen: documentation/simulation_config.md, aktive V2.
LIMITS = {
    'Running': (10, 150, 5, 16), 'Cycling': (15, 240, 8, 35),
    'Strength': (15, 120, None, None), 'Swimming': (10, 100, .8, 3.5),
    'Walking': (10, 180, 2.5, 6.5), 'Hiking': (30, 360, 1.5, 6),
    'Tennis': (20, 180, None, None), 'Padel': (20, 150, None, None),
}


class QualityError(ValueError):
    """Kritischer Befund; Eingaben bleiben unverändert."""


def require(condition, message):
    if not condition:
        raise QualityError(message)


def sha256(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def read_csv(path, columns):
    with path.open(encoding='utf-8', newline='') as stream:
        reader = csv.DictReader(stream)
        require(reader.fieldnames == columns, f'{path.name}: unerwartetes Schema')
        rows = list(reader)
    require(all(None not in row and None not in row.values() for row in rows),
            f'{path.name}: fehlerhafte CSV-Zeilenbreite')
    return rows


def number(value, label):
    require(bool(re.fullmatch(r'[0-9]+(?:\.[0-9]+)?', value)),
            f'{label}: ungültige, negative oder nicht endliche Zahl {value!r}')
    try:
        result = Decimal(value)
    except InvalidOperation as exc:
        raise QualityError(f'{label}: ungültige Zahl') from exc
    require(result.is_finite(), f'{label}: nicht endlich')
    return result


def main():
    # 1. Daten laden: ausschließlich aktive Pfade, zuerst Integrität prüfen.
    manifest = json.loads((ROOT / 'documentation/active_data_version.json').read_text())
    require(manifest['active_version'] == 'V2', 'Aktive Version ist nicht V2')
    require((manifest['users'], manifest['activities'], manifest['weeks'],
             manifest['zero_user_weeks']) == (100, 6465, 26, 558), 'V2-Vertrag abweichend')
    expected_paths = {'data/raw/activities_simulated.csv', 'data/raw/users_simulated.csv',
                      'data/raw/offers_simulated.csv', 'outputs/tables/simulation_weekly_check.csv'}
    require(set(manifest['sha256']) == expected_paths, 'Unerwartete Integritätsquellen')
    for name, expected in manifest['sha256'].items():
        require(sha256(ROOT / name) == expected, f'SHA-256 abweichend: {name}')
    activities = read_csv(ROOT / 'data/raw/activities_simulated.csv', COLUMNS + ['distance_km'])
    users = read_csv(ROOT / 'data/raw/users_simulated.csv',
                     ['user_id', 'interest_sport', 'interest_outdoor', 'interest_wellness', 'interest_leisure'])

    # 2. Datenqualität prüfen: sammeln statt still korrigieren oder entfernen.
    errors = []
    user_ids = [row['user_id'] for row in users]
    require(len(users) == 100 and len(set(user_ids)) == 100, 'Nutzeranzahl/IDs fehlerhaft')
    require(all(re.fullmatch(r'U[0-9]{3}', uid) for uid in user_ids), 'Ungültige Nutzerkennung')
    require(all(row[col] in ('True', 'False') for row in users for col in row if col != 'user_id'),
            'Ungültiger Boolean in Nutzerdatei')
    known_users = set(user_ids)
    seen = set()
    observed_sports = set()
    structural_missing = Counter()
    observed_dates = set()
    for line, row in enumerate(activities, start=2):
        try:
            label = f'CSV-Zeile {line}, {row["activity_id"]}'
            require(all(row[col].strip() for col in COLUMNS), f'{label}: fehlender Pflichtwert')
            require(bool(re.fullmatch(r'A[0-9]{6}', row['activity_id'])), f'{label}: ID-Format')
            require(row['activity_id'] not in seen, f'{label}: doppelte Aktivitäts-ID')
            seen.add(row['activity_id'])
            require(row['user_id'] in known_users, f'{label}: unbekannter Nutzer')
            sport = row['sport_type']
            require(sport in LIMITS, f'{label}: ungültige Sportart')
            observed_sports.add(sport)
            day = date.fromisoformat(row['date'])
            require(day.isoformat() == row['date'], f'{label}: kein striktes ISO-Datum')
            require(date(2026, 1, 5) <= day <= date(2026, 7, 5), f'{label}: außerhalb Zeitraum')
            observed_dates.add(day)
            minutes = number(row['duration_min'], label + ' Dauer')
            low, high, speed_low, speed_high = LIMITS[sport]
            require(low <= minutes <= high, f'{label}: Dauer außerhalb Sportgrenzen')
            if speed_low is None:
                require(row['distance_km'] == '', f'{label}: Distanz unerwartet anwendbar')
                structural_missing[sport] += 1
            else:
                distance = number(row['distance_km'], label + ' Distanz')
                # Originaldauer vor Rundung kann um 0,05 min abweichen;
                # Distanzrundung erlaubt zusätzlich 0,005 km Abweichung.
                lower = (minutes - Decimal('.05')) / 60 * Decimal(str(speed_low)) - Decimal('.005')
                upper = (minutes + Decimal('.05')) / 60 * Decimal(str(speed_high)) + Decimal('.005')
                require(lower <= distance <= upper, f'{label}: unplausible Distanz/Geschwindigkeit')
        except (QualityError, ValueError) as exc:
            errors.append(f'CSV-Zeile {line}: {exc}')
    require(not errors, '\n'.join(errors))
    require(len(activities) == 6465, 'Aktivitätsanzahl abweichend')
    require(observed_sports == set(LIMITS), 'Nicht alle acht Sportarten vorhanden')
    require(min(observed_dates) == date(2026, 1, 5) and max(observed_dates) == date(2026, 7, 5),
            'Beobachtungsgrenzen abweichend')

    # 3. Variablen auswählen: Originalreihenfolge und originale Wertdarstellung erhalten.
    selected = [{col: row[col] for col in COLUMNS} for row in activities]
    buffer = io.StringIO(newline='')
    writer = csv.DictWriter(buffer, fieldnames=COLUMNS, lineterminator='\n')
    writer.writeheader()
    writer.writerows(selected)
    payload = buffer.getvalue().encode('utf-8')

    # 4. Export: abweichende bestehende Dateien niemals überschreiben.
    output = ROOT / 'data/processed/activities_selected.csv'
    if output.exists():
        require(output.read_bytes() == payload, 'Vorhandene Ausgabe weicht ab; nicht überschrieben')
    else:
        output.parent.mkdir(parents=True, exist_ok=True)
        with output.open('xb') as stream:
            stream.write(payload)

    # 5. Verarbeitung validieren: jeder einzelne Wert, Schlüssel und exakte Summe.
    exported = read_csv(output, COLUMNS)
    require(exported == selected, 'Export weicht von ausgewählten Rohwerten ab')
    require(len(exported) == 6465 and len({r['activity_id'] for r in exported}) == 6465,
            'Zeilen/Schlüssel verloren')
    require({r['user_id'] for r in exported} <= known_users, 'Nutzerzuordnung verloren')
    source_sum = sum(Decimal(r['duration_min']) for r in activities)
    require(source_sum == sum(Decimal(r['duration_min']) for r in exported), 'Minutensumme verändert')
    for name, expected in manifest['sha256'].items():
        require(sha256(ROOT / name) == expected, f'Eingabe nach Lauf verändert: {name}')
    print(json.dumps({'status': 'bestanden', 'version': 'V2', 'rows': len(exported),
                      'columns': COLUMNS, 'unique_activity_ids': len(seen),
                      'known_users': len(known_users), 'sport_types': len(observed_sports),
                      'duration_sum_min': str(source_sum),
                      'structural_missing_distance': dict(sorted(structural_missing.items())),
                      'quality_errors': 0, 'selected_values_unchanged': True,
                      'all_four_input_hashes_unchanged': True, 'output_sha256': sha256(output)},
                     ensure_ascii=False, indent=2))


if __name__ == '__main__':
    try:
        main()
    except (QualityError, OSError, KeyError, ValueError) as exc:
        print(f'ABBRUCH: {exc}\nKeine automatische Korrektur. Ursache anhand der '
              'gemeldeten Quelle prüfen, fachlich begründete Korrektur separat dokumentieren.', file=sys.stderr)
        sys.exit(1)
