"""Session transitions independent of Streamlit, with explicit permission reset."""
MODES = ('USER VIEW', 'ANALYTICS LAB')
SECTIONS = ('Data Understanding', 'Data Preparation', 'K-Means', 'Regression',
            'Evaluation', 'Empfehlungssystem', 'CRISP-DM')
PERSONAL_KEYS = ('personal_result', 'personal_activity', 'personal_error')


def clear_personal(state):
    for key in PERSONAL_KEYS:
        state.pop(key, None)


def initialize(state, user_ids):
    if not user_ids:
        raise ValueError('Keine Nutzer verfügbar.')
    if state.get('selected_user_id') not in user_ids:
        state['selected_user_id'] = user_ids[0]
        state['interests_permission'] = False
        state['garmin_permission'] = False
        clear_personal(state)
    defaults = {'mode': MODES[0], 'lab_section': SECTIONS[0],
                'interests_permission': False, 'garmin_permission': False}
    for key, value in defaults.items():
        state.setdefault(key, value)
    if state['mode'] not in MODES:
        state['mode'] = MODES[0]
    if state['lab_section'] not in SECTIONS:
        state['lab_section'] = SECTIONS[0]


def user_changed(state):
    # Called by the persistent user widget before the next script execution.
    state['interests_permission'] = False
    state['garmin_permission'] = False
    clear_personal(state)


def permissions_changed(state):
    # Fail closed for both grants and revocations; recompute later via the engine.
    clear_personal(state)


def capabilities(state):
    return {'activity': state.get('garmin_permission') is True,
            'offers': state.get('interests_permission') is True}
