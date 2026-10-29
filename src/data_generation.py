"""Aktive MOVA-Datenversion V2: reproduzierbare synthetische Daten (Python >= 3.10)."""
import csv
import math
import random
from collections import Counter
from datetime import date, timedelta
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SEED, N_USERS, N_WEEKS = 42, 100, 26
START, END = date(2026, 1, 5), date(2026, 7, 5)
# Dauer: Median, Minimum, Maximum; Geschwindigkeit: Mittel, SD, Minimum, Maximum.
SPORTS = {
    'Running': (40, 10, 150, 9, 1.8, 5, 16),
    'Cycling': (65, 15, 240, 20, 4, 8, 35),
    'Strength': (50, 15, 120, None, None, None, None),
    'Swimming': (35, 10, 100, 2, 0.4, 0.8, 3.5),
    'Walking': (45, 10, 180, 4.5, 0.7, 2.5, 6.5),
    'Hiking': (120, 30, 360, 3.8, 0.8, 1.5, 6),
    'Tennis': (65, 20, 180, None, None, None, None),
    'Padel': (65, 20, 150, None, None, None, None),
}
PROFILES = {
    'Laufaffin': [7, 2, 3, 1, 3, 2, 1, 1],
    'Radaffin': [2, 7, 2, 1, 2, 3, 1, 1],
    'Kraftorientiert': [2, 1, 7, 1, 3, 1, 2, 2],
    'Schwimmorientiert': [2, 2, 2, 7, 2, 1, 1, 1],
    'Outdoororientiert': [3, 4, 1, 1, 5, 7, 1, 1],
    'Multisport': [3, 3, 3, 3, 3, 2, 3, 3],
    'Gelegenheitsaktiv': [2, 2, 1, 1, 6, 3, 2, 2],
}
TRENDS = ['steigend', 'konstant', 'sinkend', 'schwankend']
ACTIVITY_FIELDS = ['activity_id', 'user_id', 'date', 'sport_type', 'duration_min', 'distance_km']
USER_FIELDS = ['user_id', 'interest_sport', 'interest_outdoor', 'interest_wellness', 'interest_leisure']
OFFER_FIELDS = ['offer_id', 'category', 'title', 'price_eur', 'discount_pct']


def clip(value, low, high):
    return max(low, min(high, value))


def poisson(rng, rate):
    """Poisson-Zählverteilung nach Knuth; kleine Wochenraten benötigen kein Paket."""
    threshold, product, count = math.exp(-rate), 1.0, 0
    while product > threshold:
        product *= rng.random()
        count += 1
    return count - 1


def generate():
    """Aktive Datenversion V2: Seed 42, getrennte Quellen, Exponent 1,3."""
    from simulation_v2 import generate as generate_version
    return generate_version(exponent=1.3)


OFFER_CATALOG = {
    'Sport': [('Laufschuhe', 110), ('Fitnesskurs', 25), ('Schwimmkurs', 85), ('Tennistraining', 45), ('Padelturnier', 30), ('Fahrradhelm', 75), ('Hantelset', 65), ('Sportfestival', 22)],
    'Outdoor': [('Wanderrucksack', 90), ('Wanderführung', 35), ('Trekkingstöcke', 55), ('Regenjacke', 120), ('Kletterkurs', 70), ('Naturwochenende', 180), ('Outdoor-Messe', 18), ('Zelt', 160)],
    'Wellness': [('Saunatag', 28), ('Massage', 65), ('Yogakurs', 20), ('Thermeneintritt', 35), ('Entspannungskurs', 45), ('Wellnesswochenende', 250), ('Meditationsworkshop', 40)],
    'Freizeit': [('Kinoticket', 13), ('Museumseintritt', 15), ('Konzert', 55), ('Kochkurs', 80), ('Stadtführung', 20), ('Brettspielabend', 10), ('Theaterticket', 38)],
}


def make_offers():
    rng = random.Random(SEED + 1)  # separater, ebenfalls fester Zufallsstrom
    rows = []
    for category, entries in OFFER_CATALOG.items():
        for title, price in entries:
            rows.append(dict(zip(OFFER_FIELDS, [f'O{len(rows) + 1:03d}', category, f'FIKTIV – {title}', f'{price:.2f}', rng.choice([5, 10, 15, 20, 25, 30]) ])))
    return rows


def write_csv(relative, rows, fields):
    path = ROOT / relative
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open('w', encoding='utf-8', newline='') as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)


def read_csv(relative):
    with (ROOT / relative).open(encoding='utf-8', newline='') as handle:
        return list(csv.DictReader(handle))


def validate():
    """Prüft die tatsächlich gespeicherten CSVs; Fehler brechen das Skript ab."""
    users = read_csv('data/raw/users_simulated.csv')
    acts = read_csv('data/raw/activities_simulated.csv')
    offers = read_csv('data/raw/offers_simulated.csv')
    weekly = read_csv('outputs/tables/simulation_weekly_check.csv')
    def require(condition, message):
        if not condition:
            raise ValueError(message)
    require(len(users) == len({u['user_id'] for u in users}) == N_USERS, 'Nutzerzahl/IDs')
    uids = {u['user_id'] for u in users}
    require(START.weekday() == 0 and END.weekday() == 6 and (END - START).days + 1 == 7 * N_WEEKS, 'Zeitraum')
    require(len(acts) == len({a['activity_id'] for a in acts}), 'Aktivitäts-IDs')
    counts = Counter()
    for a in acts:
        require(all(a[f] for f in ACTIVITY_FIELDS if f != 'distance_km'), 'Pflichtfelder')
        day = date.fromisoformat(a['date'])
        require(day.isoformat() == a['date'] and START <= day <= END, 'Datum')
        require(a['user_id'] in uids and a['sport_type'] in SPORTS, 'Nutzer/Sportart')
        _, low, high, speed, _, slow, fast = SPORTS[a['sport_type']]
        duration = float(a['duration_min'])
        require(math.isfinite(duration) and low <= duration <= high, 'Trainingsdauer')
        if speed is None:
            require(a['distance_km'] == '', 'Distanz muss leer sein')
        else:
            distance = float(a['distance_km'])
            require(math.isfinite(distance) and distance >= 0 and slow * duration / 60 - 0.0051 <= distance <= fast * duration / 60 + 0.0051, 'Distanz/Geschwindigkeit')
        counts[(a['user_id'], (day - timedelta(days=day.weekday())).isoformat())] += 1
    expected = {(uid, (START + timedelta(weeks=w)).isoformat()) for uid in uids for w in range(N_WEEKS)}
    require(len(weekly) == 2600 and {(w['user_id'], w['week_start']) for w in weekly} == expected, 'Nutzer-Wochen-Raster')
    for w in weekly:
        require(int(w['activity_count']) == counts[(w['user_id'], w['week_start'])], 'Wochenzählung')
    require({a['user_id'] for a in acts} == uids, 'Aktive Nutzer im Gesamtzeitraum')
    require({a['sport_type'] for a in acts} == set(SPORTS), 'Sportartenabdeckung')
    for u in users:
        require(all(u[f] in ('True', 'False') for f in USER_FIELDS[1:]), 'Boolesche Interessen')
    require(len(offers) == len({o['offer_id'] for o in offers}) == 30, 'Angebotszahl/IDs')
    for o in offers:
        require(all(o.values()) and o['category'] in OFFER_CATALOG and o['title'].startswith('FIKTIV – '), 'Angebotsfelder')
        require(math.isfinite(float(o['price_eur'])) and float(o['price_eur']) > 0 and 0 <= float(o['discount_pct']) <= 100, 'Preis/Rabatt')
    return users, acts, offers, weekly


def report(assigned):
    """Aktueller V2-Bericht; historische V1-Berichte bleiben unverändert."""
    users, acts, offers, weekly = validate()
    counts = [int(w['activity_count']) for w in weekly]
    if (len(users), len(acts), len(offers), len(weekly), counts.count(0)) != (100, 6465, 30, 2600, 558):
        raise ValueError('Aktive V2 entspricht nicht der freigegebenen Baseline')
    text = '\n'.join([
        '# MOVA – Aktive Simulation V2', '',
        'Verbindliche Datengrundlage nach abgeschlossener erster CRISP-DM-Iteration.',
        'Noch keine vollständige Data Preparation oder Modellierung durchgeführt.',
        'Seed 42; getrennte Zufallsquellen 42–49; Exponent 1,3; 26 Wochen.', '',
        f'- Nutzer: {len(users)}', f'- Aktivitäten: {len(acts)}',
        f'- Fiktive Angebote: {len(offers)}', f'- Nutzerwochen: {len(weekly)}',
        f'- Nullwochen: {counts.count(0)}',
        f'- Aktivitäten/Nutzer/Woche: {len(acts)/len(weekly):.6f}',
        f'- Minimum / Maximum Aktivitäten pro Nutzerwoche: {min(counts)} / {max(counts)}',
        '- Technische Qualitätsprüfung: BESTANDEN', '',
        'Sportartenverteilung:',
        *[f'- {sport}: {sum(a["sport_type"] == sport for a in acts)}' for sport in SPORTS], '',
        'Interne Trendmechanismen, keine Modelllabels:',
        *[f'- {trend}: {assigned[trend]}' for trend in TRENDS], '',
        'Historischer V1-Bericht: simulation_report.md; historischer Qualitätsbericht: simulation_quality_report.md.',
        'Vergleich und Einschränkungen: outputs/simulation_comparison/comparison_report.md.', '',
    ])
    (ROOT / 'outputs/tables/simulation_report_v2.md').write_text(text, encoding='utf-8')
    print(text)


def main():
    users, acts, weekly, assigned = generate()
    write_csv('data/raw/users_simulated.csv', users, USER_FIELDS)
    write_csv('data/raw/activities_simulated.csv', acts, ACTIVITY_FIELDS)
    write_csv('data/raw/offers_simulated.csv', make_offers(), OFFER_FIELDS)
    write_csv('outputs/tables/simulation_weekly_check.csv', weekly, ['user_id', 'week_start', 'activity_count'])
    report(assigned)


if __name__ == '__main__':
    main()
