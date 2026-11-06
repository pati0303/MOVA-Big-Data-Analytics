"""Local MOVA shell. Start from repository root: streamlit run app.py."""
import streamlit as st
from dashboard.data_access import DataAccessError, load_user_ids, check_engine_basis
from dashboard.design import apply_design
from dashboard.state import MODES, SECTIONS, initialize, user_changed, permissions_changed
from dashboard.views import user_view, analytics_view

st.set_page_config(page_title='MOVA · Move beyond.', page_icon='↗', layout='wide')
apply_design()
try:
    user_ids = load_user_ids()
except DataAccessError as exc:
    st.error(str(exc))
    st.info('Bitte die unveränderte V2-Nutzerdatei und documentation/active_data_version.json im Projektbestand prüfen.')
    st.stop()
initialize(st.session_state, user_ids)

brand, navigation, user = st.columns([1.1, 1.8, 1.1], vertical_alignment='center')
with brand:
    st.markdown('<div class="mova-brand"><div class="mova-mark">↗</div><div><div class="mova-wordmark">MOVA</div><div class="mova-claim">Move beyond.</div></div></div>', unsafe_allow_html=True)
with navigation:
    st.segmented_control('Ansicht', MODES, key='mode', required=True, width='stretch')
with user:
    st.selectbox('Synthetischer Nutzer', user_ids, key='selected_user_id',
                 on_change=user_changed, args=(st.session_state,))
st.caption('SYNTHETISCHE V2-DEMO · Historischer Demo-Stichtag 05.07.2026 · Keine echten Garmin-Daten')

with st.container(border=True):
    label, interests, garmin = st.columns([1.35,1,1], vertical_alignment='center')
    with label:
        st.markdown('**Simulierte Freigaben**')
        # Synthetic scope is already visible above; keep the grant row compact.
    with interests:
        st.toggle('Simulierte Interessenfreigabe', key='interests_permission',
                  on_change=permissions_changed, args=(st.session_state,),
                  help='Erlaubt positive Interessenkategorien und personalisierte Angebote. Bei Nutzerwechsel zurückgesetzt.')
    with garmin:
        st.toggle('Simulierte Garmin-Freigabe', key='garmin_permission',
                  on_change=permissions_changed, args=(st.session_state,),
                  help='Erlaubt persönlichen Aktivitäts-, Segment- und Prognosekontext. Bei Nutzerwechsel zurückgesetzt.')

if st.session_state['mode'] == 'ANALYTICS LAB':
    with st.sidebar:
        st.markdown('### Analytics Lab')
        st.caption('ACHT PERSPEKTIVEN · EIN DATENSATZ')
        st.session_state['lab_widget'] = st.session_state['lab_section']
        st.radio('Forschungsbereich', SECTIONS, key='lab_widget',
                 on_change=lambda: st.session_state.update(lab_section=st.session_state['lab_widget']))
        st.caption('Interaktive Einblicke in unsere Daten, Modelle und beide CRISP-DM-Zyklen.')
    analytics_view(st.session_state)
else:
    user_view(st.session_state)

with st.expander('Projektstatus und technische Voraussetzungen'):
    st.write('AP 7.5a: User View und Analytics Lab für die lokale Demonstration geprüft. Nur synthetische Projektdaten.')
    if check_engine_basis():
        st.success('Geprüfte Quelldateien für den Engine-Loader verfügbar.')
    else:
        st.warning('Quelldateien für den Engine-Loader fehlen oder sind verändert. '
                   'Bitte den vollständigen unveränderten Projektbestand bereitstellen.')
    st.caption('Nur das gespeicherte Regressionsmodell wird bei Garmin-Freigabe verwendet, ohne Training. Keine persönlichen Resultate werden gecacht.')
st.markdown('<div class="mova-footer">MOVA — Move beyond. &nbsp; / &nbsp; Hochschulprojekt Big Data Analytics · Synthetischer Demonstrator</div>', unsafe_allow_html=True)
