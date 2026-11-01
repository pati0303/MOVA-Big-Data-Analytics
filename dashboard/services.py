"""Thin permission-bound integration adapter; no model or ranking implementation."""
from datetime import date
import importlib
import sys

from dashboard.data_access import DataAccessError, PROJECT_ROOT

DEMO_DATE = date(2026, 7, 5)


def recommendation_context(user_id, *, interests_permission, garmin_permission, root=PROJECT_ROOT):
    """Delegate all permissions, model context and ranking to the existing engine.

    No cache or retained previous response. Called by the permission-gated User View.
    """
    if type(interests_permission) is not bool or type(garmin_permission) is not bool:
        raise ValueError('Simulierte Freigaben müssen explizite bool-Werte sein.')
    source = str(PROJECT_ROOT / 'src')
    if source not in sys.path:
        sys.path.insert(0, source)
    try:
        engine = importlib.import_module('recommendation_engine')
        return engine.run(user_id, interests_permission=interests_permission,
                          garmin_permission=garmin_permission, as_of=DEMO_DATE, root=root)
    except Exception as exc:  # UI boundary: never reuse a stale response on infrastructure failure.
        raise DataAccessError('Der Projektkontext konnte nicht geladen werden. '
                              'Bitte Quelldateien, Git-Basis und Modellumgebung prüfen.') from exc


def user_context(user_id, *, interests_permission, garmin_permission, root=PROJECT_ROOT):
    """Fresh request-scoped context. Permissions never come from a stored profile."""
    from dashboard.data_access import load_activity_summary
    result = recommendation_context(user_id, interests_permission=interests_permission,
                                    garmin_permission=garmin_permission, root=root)
    if result.get('user_id') != user_id:
        raise DataAccessError('Der geladene Nutzerkontext stimmt nicht mit der Auswahl überein.')
    activity, activity_error = None, None
    if garmin_permission:
        try:
            engine = importlib.import_module('recommendation_engine')
            activity = load_activity_summary(user_id, garmin_permission=True,
                                            verify_source=engine.verify_tracked_bytes, root=root)
        except DataAccessError as exc:
            activity_error = str(exc)
    return dict(engine=result, activity=activity, activity_error=activity_error)
