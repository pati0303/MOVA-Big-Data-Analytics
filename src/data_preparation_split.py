"""AP 4.6: unveränderte V2-Regressionszeilen chronologisch aufteilen.

Aufruf: python src/data_preparation_split.py; nur Standardbibliothek.
Kein Training, keine Prognosen und keine Evaluation.
"""
import csv
import hashlib
import io
import json
import math
import platform
import sys
from collections import Counter
from datetime import date, timedelta
from pathlib import Path

from data_preparation_selection import QualityError, read_csv, require, sha256
from data_preparation_regression import (
    OUTPUT_COLUMNS, MODEL_FEATURES, TARGET, METADATA, START,
    check_weekly, validate as validate_regression,
)
from data_preparation_weekly import OUTPUT_COLUMNS as WEEKLY_COLUMNS

ROOT = Path(__file__).resolve().parents[1]
INPUT_PATH = 'data/processed/regression_weekly_features.csv'
INPUT_HASH = '4fc681eaa1a042a1b44cf6bc742a27f3277eafb7a9c54f5ff78736d998b70914'
WEEKLY_HASH = 'c34a7bd16d1cdc3e91388cc35b8c784afde0b53c1dbfdd24de97148350359b74'
TRAIN_WEEKS = tuple(range(4, 22))
TEST_WEEKS = tuple(range(22, 26))


def key(row):
    return row['user_id'], int(row['week_index'])


def check_source(rows, users):
    """Schritt 2: Schema, Typen und alle erwarteten Zeitpunkte prüfen."""
    require(len(users) == len(set(users)) == 100, 'Nutzerliste unvollständig/doppelt')
    require(len(rows) == 2200, 'Ausgangstabelle muss 2.200 Zeilen enthalten')
    converted = []
    for row in sorted(rows, key=key):
        require(list(row) == OUTPUT_COLUMNS and all(isinstance(v, str) and v.strip() for v in row.values()),
                'Schema oder Pflichtwerte ungültig')
        for name in ['week_index','activities_current_week',TARGET]:
            require(row[name].isdigit(), f'{name}: nicht negative Ganzzahl erforderlich')
        average = float(row['avg_activities_last_4_weeks'])
        require(math.isfinite(average) and 0 <= average <= 10, 'Ungültiger Vierwochenmittelwert')
        index = int(row['week_index'])
        require(4 <= index <= 25, 'Eingabewoche außerhalb 4–25')
        begin = START + timedelta(weeks=index - 1)
        require(row['week_start'] == begin.isoformat() and
                row['week_end'] == (begin+timedelta(days=6)).isoformat(), 'Falsche Kalenderzuordnung')
        require(int(row['activities_current_week']) <= 10 and int(row[TARGET]) <= 10,
                'Aktivitätszahl außerhalb V2-Vertrag')
        converted.append({name: int(value) if name in ['week_index','activities_current_week',TARGET] else
                          average if name == 'avg_activities_last_4_weeks' else value
                          for name,value in row.items()})
    expected = [(uid,index) for uid in sorted(users) for index in range(4,26)]
    require([key(r) for r in sorted(rows,key=key)] == expected,
            'Unbekannte/fehlende/doppelte Nutzer-Wochen-Schlüssel')
    return converted


def validate_split(source, train, test, users):
    """Schritt 6: harte Wochenregeln, Vollständigkeit und alle Originalwerte prüfen."""
    require(len(train) == 1800 and len(test) == 400, 'Falsche Trainings-/Testgröße')
    for label,rows,weeks,per_user in [('Training',train,TRAIN_WEEKS,18),('Test',test,TEST_WEEKS,4)]:
        expected = [(uid,index) for uid in sorted(users) for index in weeks]
        require([key(r) for r in rows] == expected, f'{label}: Schlüssel, Wochen oder Sortierung falsch')
        require(Counter(r['user_id'] for r in rows) == Counter({uid:per_user for uid in users}),
                f'{label}: falsche Nutzerverteilung')
    train_keys = {key(r) for r in train}
    test_keys = {key(r) for r in test}
    require(train_keys.isdisjoint(test_keys), 'Nutzer-Wochen-Überlappung')
    train_targets = {int(r['week_index'])+1 for r in train}
    test_targets = {int(r['week_index'])+1 for r in test}
    require(train_targets == set(range(5,23)) and test_targets == set(range(23,27)) and
            max(train_targets) < min(test_targets), 'Zielwochen nicht korrekt zeitlich getrennt')
    # Dictionary-/Wertvergleich bewahrt auch ursprüngliche Zahlendarstellungen.
    require(sorted(train+test,key=key) == sorted(source,key=key),
            'Split verändert/verliert Quellzeilen oder Merkmalswerte')
    last_train_target_end = max(date.fromisoformat(r['week_end'])+timedelta(days=7) for r in train)
    first_test_target_start = min(date.fromisoformat(r['week_start'])+timedelta(days=7) for r in test)
    require(last_train_target_end < first_test_target_start, 'Kalender-Zielzeiträume überlappen')


def split_rows(rows, users, train_weeks=TRAIN_WEEKS, test_weeks=TEST_WEEKS):
    """Schritte 3–5: Auswahl nur anhand week_index, niemals zufällig."""
    check_source(rows, users)
    require(tuple(train_weeks) == TRAIN_WEEKS and tuple(test_weeks) == TEST_WEEKS,
            'Falsch konfigurierte Wochenaufteilung; freigegeben ist 4–21 / 22–25')
    ordered = sorted(rows,key=key)
    train = [row.copy() for row in ordered if int(row['week_index']) in train_weeks]
    test = [row.copy() for row in ordered if int(row['week_index']) in test_weeks]
    validate_split(rows, train, test, users)
    return train, test


def csv_payload(rows):
    buffer = io.StringIO(newline='')
    writer = csv.DictWriter(buffer, fieldnames=OUTPUT_COLUMNS, lineterminator='\n')
    writer.writeheader()
    writer.writerows(rows)
    return buffer.getvalue().encode('utf-8')


def main():
    # 1. Vorhandene Quellen laden und V2-Integrität prüfen; nichts neu aggregieren.
    active = json.loads((ROOT/'documentation/active_data_version.json').read_text())
    require(active['active_version'] == 'V2', 'Keine aktive V2')
    hashes = dict(active['sha256'])
    hashes.update({INPUT_PATH:INPUT_HASH, 'data/processed/user_weekly_activities.csv':WEEKLY_HASH})
    for name,expected in hashes.items():
        require(sha256(ROOT/name) == expected, f'Eingabehash abweichend: {name}')
    source = read_csv(ROOT/INPUT_PATH, OUTPUT_COLUMNS)
    users = [r['user_id'] for r in read_csv(ROOT/'data/raw/users_simulated.csv',
             ['user_id','interest_sport','interest_outdoor','interest_wellness','interest_leisure'])]
    weekly = read_csv(ROOT/'data/processed/user_weekly_activities.csv', WEEKLY_COLUMNS)
    check_weekly(weekly, users)
    # Vorhandene X/y gegen Originalwochen validieren, keine Merkmale neu exportieren.
    validate_regression(check_source(source, users), weekly, users)
    train, test = split_rows(source, users)
    payloads = {'data/processed/regression_train.csv':csv_payload(train),
                'data/processed/regression_test.csv':csv_payload(test)}
    manifest = {
        'active_version':'V2', 'input_file':INPUT_PATH, 'input_sha256':INPUT_HASH,
        'source_commit':'ed52949cb8b688bc64c0793be0e407950314769e',
        'implementation_status':'AP-4-Änderungen uncommitted', 'python_version':platform.python_version(),
        'split_rule':'Ausschließlich week_index: Training 4–21, Test 22–25; identisch für alle Nutzer; kein Zufall',
        'split_column':'week_index', 'train_input_weeks':list(TRAIN_WEEKS),
        'test_input_weeks':list(TEST_WEEKS), 'train_target_weeks':list(range(5,23)),
        'test_target_weeks':list(range(23,27)), 'train_rows':len(train), 'test_rows':len(test),
        'total_rows':len(source), 'n_users':len(users), 'train_rows_per_user':18,'test_rows_per_user':4,
        'train_target_date_range':['2026-02-02','2026-06-07'],
        'test_target_date_range':['2026-06-08','2026-07-05'],
        'columns':OUTPUT_COLUMNS, 'model_input_features':MODEL_FEATURES, 'target':TARGET,
        'excluded_metadata':METADATA, 'target_excluded_from_inputs':True,
        'rolling_forecast_protocol':'Rollierende Einwochenprognosen nach Abschluss von t. Beobachtete frühere Testwochen dürfen spätere Eingänge bilden. Das spätere Modell bleibt in der Testphase unverändert; kein Nachtrainieren auf Testzielen. Keine gleichzeitige Vierwochenprognose.',
        'history_overlap':'Überlappende historische Eingabewochen zulässig; zukünftige Ziele in früheren X unzulässig.',
        'validation':'Alle 2.200 X/y-Zeilen gegen Wochenquelle geprüft; disjunkte Schlüssel/Zielwochen, vollständige unveränderte Rekonstruktion',
        'input_integrity_sha256':hashes,
        'output_sha256':{name:hashlib.sha256(payload).hexdigest() for name,payload in payloads.items()},
    }
    payloads['documentation/regression_split_manifest.json'] = (json.dumps(manifest,ensure_ascii=False,
                                 indent=2,sort_keys=True,allow_nan=False)+'\n').encode('utf-8')
    # 7. Alle Konflikte zuerst prüfen, keine bestehenden abweichenden Dateien ersetzen.
    for name,payload in payloads.items():
        path = ROOT/name
        require(not path.exists() or path.read_bytes() == payload, f'Bestehende Ausgabe abweichend: {name}')
    for name,payload in payloads.items():
        path = ROOT/name
        if not path.exists():
            with path.open('xb') as stream:
                stream.write(payload)
    loaded_train = read_csv(ROOT/'data/processed/regression_train.csv', OUTPUT_COLUMNS)
    loaded_test = read_csv(ROOT/'data/processed/regression_test.csv', OUTPUT_COLUMNS)
    validate_split(source, loaded_train, loaded_test, users)
    require(json.loads((ROOT/'documentation/regression_split_manifest.json').read_text()) == manifest,
            'Manifest-Rücklesen abweichend')
    for name,expected in hashes.items():
        require(sha256(ROOT/name) == expected, f'Eingabe verändert: {name}')
    print(json.dumps({'status':'bestanden','train_rows':len(train),'test_rows':len(test),
         'users_in_each_split':len(users),'train_input_weeks':[4,21],'test_input_weeks':[22,25],
         'train_target_weeks':[5,22],'test_target_weeks':[23,26],
         'exact_source_reconstruction':True,'input_hashes_unchanged':True,
         'outputs_sha256':{name:sha256(ROOT/name) for name in payloads}},ensure_ascii=False,indent=2))


if __name__ == '__main__':
    try:
        main()
    except (QualityError, ValueError, ArithmeticError, OSError, KeyError) as exc:
        print(f'ABBRUCH: {exc}\nKeine automatische Korrektur. Befund und Quelle prüfen.',file=sys.stderr)
        sys.exit(1)
