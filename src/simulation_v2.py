"""Getrennte Zufallsquellen der geprüften V2; keine Änderung ihrer Logik.
Exponent 1,0 dient ausschließlich dem historischen Kontrollvergleich.
"""
import math
import random
from collections import Counter
from datetime import timedelta
from data_generation import (SEED, N_USERS, N_WEEKS, START, END, SPORTS, PROFILES,
                             TRENDS, ACTIVITY_FIELDS, USER_FIELDS, clip, poisson)

def generate(exponent):
    # Master-Seed 42; feste abgeleitete Seeds je Zweck.
    rng = random.Random(SEED)  # Frequenz, Trendparameter, Pausen, Wochenrauschen
    profile_rng = random.Random(SEED + 1)
    preference_rng = random.Random(SEED + 2)
    sport_rng = random.Random(SEED + 3)
    duration_rng = random.Random(SEED + 4)
    distance_rng = random.Random(SEED + 5)
    interest_rng = random.Random(SEED + 6)
    day_rng = random.Random(SEED + 7)
    users, activities, weekly = [], [], []
    assigned = Counter()
    for number in range(1, N_USERS + 1):
        uid = f'U{number:03d}'
        profile = profile_rng.choice(list(PROFILES))
        trend = rng.choice(TRENDS)
        assigned[trend] += 1
        # Interessen sind unabhängig von Profil und Verlauf.
        users.append(dict(zip(USER_FIELDS, [uid] + [interest_rng.random() < p for p in (0.65, 0.5, 0.4, 0.6)])))
        weights = [w * preference_rng.lognormvariate(0, 0.7) for w in PROFILES[profile]]
        weights = [weight ** exponent for weight in weights]
        base = rng.uniform(0.4, 2) if profile == 'Gelegenheitsaktiv' else rng.uniform(1.3, 5)
        duration_factor = duration_rng.uniform(0.75, 1.3)
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
                day = day_rng.choices(range(7), weights=[(1.3 if d >= 5 else 1) if days[d] < 2 else 0 for d in range(7)])[0]
                days[day] += 1
                sport = sport_rng.choices(list(SPORTS), weights=weights)[0]
                median, lower, upper, speed, sd, slow, fast = SPORTS[sport]
                duration = round(clip(duration_rng.lognormvariate(math.log(median * duration_factor), 0.3), lower, upper), 1)
                distance = '' if speed is None else round(duration / 60 * clip(distance_rng.gauss(speed, sd), slow, fast), 2)
                activities.append(dict(zip(ACTIVITY_FIELDS, ['', uid, (monday + timedelta(days=day)).isoformat(), sport, duration, distance])))
    activities.sort(key=lambda row: (row['date'], row['user_id']))
    for i, row in enumerate(activities, 1):
        row['activity_id'] = f'A{i:06d}'
    return users, activities, weekly, assigned

