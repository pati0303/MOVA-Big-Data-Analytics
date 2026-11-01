"""Read-only project access. No implicit loading of personal activity data."""
import csv
import hashlib
import json
from pathlib import Path
import subprocess

PROJECT_ROOT = Path(__file__).resolve().parents[1]
ENGINE_BASE = 'a8f97ad75c378329a614a322bd541f372de0b072'


class DataAccessError(RuntimeError):
    """A source or installation issue safe to explain in the UI."""


def load_user_ids(root=PROJECT_ROOT):
    root = Path(root)
    try:
        path = root / 'data/raw/users_simulated.csv'
        manifest = json.loads((root / 'documentation/active_data_version.json').read_text())
        if manifest['active_version'] != 'V2':
            raise ValueError('Aktive Datenversion ist nicht V2.')
        expected = manifest['sha256']['data/raw/users_simulated.csv']
        if hashlib.sha256(path.read_bytes()).hexdigest() != expected:
            raise ValueError('Prüfsumme der Nutzerdatei stimmt nicht mit V2 überein.')
        with path.open(encoding='utf-8', newline='') as stream:
            reader = csv.DictReader(stream)
            required = ['user_id', 'interest_sport', 'interest_outdoor',
                        'interest_wellness', 'interest_leisure']
            if reader.fieldnames != required:
                raise ValueError('Unerwartete Spalten in der Nutzerdatei.')
            rows = list(reader)
        ids = [row['user_id'] for row in rows]
        if len(ids) != 100 or len(set(ids)) != 100 or set(ids) != {f'U{i:03}' for i in range(1, 101)}:
            raise ValueError('Erwartet werden 100 eindeutige V2-Nutzerkennungen.')
        if any(row[key] not in ('True', 'False') for row in rows for key in required[1:]):
            raise ValueError('Ungültige Interessenwerte in der Nutzerdatei.')
        return sorted(ids)
    except (OSError, ValueError, KeyError, TypeError, csv.Error) as exc:
        raise DataAccessError(f'Nutzerquelle nicht verfügbar oder ungültig: {exc}') from exc


def check_engine_basis(root=PROJECT_ROOT):
    """Check local Git objects needed by the existing loader; no remote access."""
    root = Path(root)
    paths = ('data/processed/user_weekly_activities.csv',
             'data/processed/kmeans_user_features.csv', 'data/processed/user_clusters.csv')
    try:
        for path in paths:
            subprocess.run(['git', '-C', str(root), 'cat-file', '-e', f'{ENGINE_BASE}:{path}'],
                           check=True, capture_output=True, timeout=10)
        return True
    except (OSError, subprocess.SubprocessError):
        return False


def load_activity_summary(user_id, *, garmin_permission, verify_source, root=PROJECT_ROOT):
    """Read verified 26-week observations for one permitted user, without caching.

    verify_source is the existing engine's verify_tracked_bytes function. This
    adapter only aggregates observations; it builds no model or ranking features.
    """
    if type(garmin_permission) is not bool:
        raise ValueError('Garmin-Freigabe muss ein bool-Wert sein.')
    if not garmin_permission:
        return None  # Before any file read or verification.
    from collections import Counter
    from datetime import date, timedelta
    from decimal import Decimal
    root = Path(root)
    try:
        paths = ('data/raw/activities_simulated.csv', 'data/processed/user_weekly_activities.csv')
        for path in paths:
            verify_source(root, path)
        def read(path, columns):
            with (root / path).open(encoding='utf-8', newline='') as stream:
                reader = csv.DictReader(stream)
                if reader.fieldnames != columns:
                    raise ValueError(f'Unerwartete Spalten: {path}')
                return [row for row in reader if row['user_id'] == user_id]
        raw = read(paths[0], ['activity_id', 'user_id', 'date', 'sport_type', 'duration_min', 'distance_km'])
        weeks = read(paths[1], ['user_id', 'week_index', 'week_start', 'week_end', 'activities_count', 'total_duration_min'])
        weeks.sort(key=lambda row: int(row['week_index']))
        if len(weeks) != 26 or [int(row['week_index']) for row in weeks] != list(range(1, 27)):
            raise ValueError('Die vollständige Reihe mit 26 Wochen fehlt.')
        start = date(2026, 1, 5)
        normalized = []
        for index, row in enumerate(weeks):
            monday = start + timedelta(weeks=index)
            if row['week_start'] != monday.isoformat() or row['week_end'] != (monday + timedelta(days=6)).isoformat():
                raise ValueError('Wochenintervalle stimmen nicht mit dem Beobachtungszeitraum überein.')
            count, minutes = int(row['activities_count']), Decimal(row['total_duration_min'])
            if count < 0 or not minutes.is_finite() or minutes < 0 or (count == 0 and minutes != 0):
                raise ValueError('Ungültige Wochenwerte.')
            normalized.append(dict(week_index=index+1, week_start=row['week_start'],
                                   week_end=row['week_end'], activities_count=count,
                                   total_duration_min=float(minutes)))
        sports = Counter(row['sport_type'] for row in raw)
        total = sum(row['activities_count'] for row in normalized)
        minutes = sum(Decimal(row['total_duration_min']) for row in weeks)
        if len(raw) != total or sum(Decimal(row['duration_min']) for row in raw) != minutes:
            raise ValueError('Wochen- und Aktivitätssummen stimmen nicht überein.')
        active = sum(row['activities_count'] > 0 for row in normalized)
        top = [sport for sport in sorted(sports) if sports[sport] == max(sports.values())] if sports else []
        return dict(user_id=user_id, weeks=normalized, total_activities=total,
                    avg_activities_per_week=total / 26, avg_minutes_per_week=float(minutes / 26),
                    active_weeks=active, zero_weeks=26-active, top_sports=top,
                    sport_counts=dict(sorted(sports.items())), total_minutes=float(minutes),
                    period_start='2026-01-05', period_end='2026-07-05')
    except Exception as exc:
        raise DataAccessError('Aktivitätsdaten fehlen, sind unvollständig oder konnten nicht verifiziert werden.') from exc
