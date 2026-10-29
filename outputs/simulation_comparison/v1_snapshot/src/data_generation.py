"""AP 2.3: reproduzierbare, rein synthetische Smartwatch-Daten (Python >= 3.10)."""
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
    rng = random.Random(SEED)
    users, activities, weekly = [], [], []
    assigned = Counter()
    for number in range(1, N_USERS + 1):
        uid = f'U{number:03d}'
        profile = rng.choice(list(PROFILES))
        trend = rng.choice(TRENDS)
        assigned[trend] += 1
        # Interessen sind unabhängig von Profil und Verlauf.
        users.append(dict(zip(USER_FIELDS, [uid] + [rng.random() < p for p in (0.65, 0.5, 0.4, 0.6)])))
        weights = [w * rng.lognormvariate(0, 0.7) for w in PROFILES[profile]]
        base = rng.uniform(0.4, 2) if profile == 'Gelegenheitsaktiv' else rng.uniform(1.3, 5)
        duration_factor = rng.uniform(0.75, 1.3)
        amplitude, phase = rng.uniform(0.2, 0.55), rng.uniform(0, 2 * math.pi)
        period, state, pause_left = rng.uniform(6, 12), 0.0, 0
        for week in range(N_WEEKS):
            progress = week / (N_WEEKS - 1)
            factor = {'steigend': 1 - amplitude + 2 * amplitude * progress,
                      'sinkend': 1 + amplitude - 2 * amplitude * progress,
                      'konstant': 1.0,
                      'schwankend': 1 + amplitude * math.sin(2 * math.pi * week / period + phase)}[trend]
            # AR(1): Belastungsschwankungen wirken in benachbarte Wochen nach.
            state = clip(0.65 * state + rng.gauss(0, 0.2), -0.7, 0.7)
            if pause_left == 0 and rng.random() < 0.045:
                pause_left = rng.choice([1, 1, 2, 3])
            paused = pause_left > 0
            count = 0 if paused else min(10, poisson(rng, clip(base * factor * math.exp(state), 0.1, 8)))
            pause_left = max(0, pause_left - 1)
            monday = START + timedelta(weeks=week)
            weekly.append({'user_id': uid, 'week_start': monday.isoformat(), 'activity_count': count})
            # Höchstens zwei Aufzeichnungen pro Tag, Wochenenden etwas wahrscheinlicher.
            days = [0] * 7
            for _ in range(count):
                day = rng.choices(range(7), weights=[(1.3 if d >= 5 else 1) if days[d] < 2 else 0 for d in range(7)])[0]
                days[day] += 1
                sport = rng.choices(list(SPORTS), weights=weights)[0]
                median, lower, upper, speed, sd, slow, fast = SPORTS[sport]
                duration = round(clip(rng.lognormvariate(math.log(median * duration_factor), 0.3), lower, upper), 1)
                distance = '' if speed is None else round(duration / 60 * clip(rng.gauss(speed, sd), slow, fast), 2)
                activities.append(dict(zip(ACTIVITY_FIELDS, ['', uid, (monday + timedelta(days=day)).isoformat(), sport, duration, distance])))
    activities.sort(key=lambda row: (row['date'], row['user_id']))
    for i, row in enumerate(activities, 1):
        row['activity_id'] = f'A{i:06d}'
    return users, activities, weekly, assigned


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
    users, acts, offers, weekly = validate()
    frequencies = [int(w['activity_count']) for w in weekly]
    sports = Counter(a['sport_type'] for a in acts)
    observed = Counter()
    for u in users:
        series = [int(w['activity_count']) for w in weekly if w['user_id'] == u['user_id']]
        delta = sum(series[-6:]) / 6 - sum(series[:6]) / 6
        observed['steigend' if delta > 0.5 else 'sinkend' if delta < -0.5 else 'ähnliches Anfangs-/Endniveau'] += 1
    text = '\n'.join([
        '# MOVA – Ergebnis der ersten Simulation', '',
        'Erste synthetische Datensimulation – noch keine vollständige Data Preparation oder Modellierung durchgeführt.', '',
        f'Zeitraum: {START} bis {END}; 26 vollständige Wochen (ISO-KW 02–27). Seed: {SEED}.',
        f'Python-Standardbibliothek; Ausführung: `python src/data_generation.py` vom Repository-Verzeichnis.', '',
        f'- Nutzer: {len(users)}', f'- Aktivitäten: {len(acts)}', f'- Angebote: {len(offers)} (alle fiktiv)',
        f'- Nutzerwochen: {len(weekly)}',
        f'- Aktivitäten je Nutzer/Woche einschließlich Nullwochen: {len(acts) / len(weekly):.3f}',
        f'- Minimum / Maximum je Nutzerwoche: {min(frequencies)} / {max(frequencies)}',
        f'- Nutzerwochen ohne Aktivität: {frequencies.count(0)} ({frequencies.count(0) / len(weekly):.1%})', '',
        '## Sportarten', '', '| Sportart | Aktivitäten | Anteil |', '|---|---:|---:|',
        *[f'| {s} | {sports[s]} | {sports[s] / len(acts):.1%} |' for s in SPORTS], '',
        '## Aktivitätsverläufe', '',
        'Intern zugewiesene Generierungsmechanismen (keine gemessenen oder gespeicherten Nutzerlabels):',
        *[f'- {t}: {assigned[t]}' for t in TRENDS], '',
        'Tatsächlich beobachteter deskriptiver Vergleich: Mittelwert der letzten sechs minus der ersten sechs Wochen; Schwelle ±0,5 Aktivitäten/Woche. Dies identifiziert insbesondere keine schwankenden Verläufe und ist keine Regression.',
        *[f'- {t}: {observed[t]}' for t in ['steigend', 'sinkend', 'ähnliches Anfangs-/Endniveau']], '',
        '## Technische Datenqualität', '',
        'BESTANDEN: 100 eindeutige Nutzer, vollständiger Zeitraum, 2.600 eindeutige Nutzerwochen inklusive Nullen, Abgleich aller Wochenzählungen mit den Aktivitäten, eindeutige Aktivitäts-IDs, bekannte Nutzer, acht erlaubte und vorhandene Sportarten, gültige ISO-Daten, Pflichtfelder, endliche und sportartspezifisch begrenzte Dauern und Distanzen, gezielt leere Distanzen, boolesche Interessen, 30 eindeutige fiktive Angebote mit gültigen Kategorien/Preisen/Rabatten.', '',
        '## Einordnung und nächster Prüfschritt', '',
        'Nullwochen und Unterschiede zwischen vorgegebenen und beobachteten Trends sind beabsichtigt: Pausen und Zählrauschen überlagern die Grundentwicklung. Die Tabellen enthalten ausschließlich simulierte Beobachtungen; keine empirischen Befunde.', '',
        'Die Obergrenze von zehn Aktivitäten pro Woche und abgeschnittene Dauern können Randhäufungen verursachen. Sportarten, Häufigkeiten, Nullwochen und auffällige Randwerte sollten fachlich mit den Projektzielen abgeglichen werden. Geschwindigkeiten sind Annahmen, keine Leistungsdiagnostik. Wetter, Feiertage, Saison, Verletzungen und Messfehler fehlen. Interessen sind bewusst unabhängig; reale Zusammenhänge werden nicht behauptet.', '',
        'CRISP-DM: Beitrag zu 2.1 Collect Initial Data / 3.3 Construct Data. Tatsächlich durchgeführt: Generierung und technische Kontrolle. Kein fachlicher Review, keine vollständige Data Preparation, keine Modellierung und kein abgeschlossener iterativer CRISP-DM-Rücksprung. Ein Rücksprung wird erst nach tatsächlicher Prüfung und Anpassung dokumentiert.', '',
    ])
    (ROOT / 'outputs/tables/simulation_report.md').write_text(text, encoding='utf-8')
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
