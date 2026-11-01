"""Shared MOVA presentation components. All HTML values are escaped."""
from html import escape
import streamlit as st


def card(eyebrow, title, body, *, status='AP 7.3 · vorgesehen', icon='↗'):
    st.markdown(f'''<article class="mova-card">
      <div class="mova-eyebrow">{escape(icon)} &nbsp; {escape(eyebrow)}</div>
      <h3>{escape(title)}</h3><p>{escape(body)}</p>
      <div class="mova-card-status">{escape(status)}</div>
    </article>''', unsafe_allow_html=True)


def section_title(number, title, description):
    st.markdown(f'<div class="mova-section"><span>{escape(number)}</span>'
                f'<div><h2>{escape(title)}</h2><p>{escape(description)}</p></div></div>',
                unsafe_allow_html=True)


def experiment(title, question, data, steps, insight):
    """Reusable scientific experiment frame; deliberately no fabricated output."""
    section_title('LAB', title, question)
    left, right = st.columns([1.7, 1], gap='large')
    with left:
        card('EXPERIMENT', 'Hier wird die Analyse interaktiv.',
             'Beispiele, Diagramme und Berechnungsschritte werden in AP 7.4 angebunden.',
             status='Konzept vorbereitet · noch keine Berechnung', icon='◈')
        with st.expander('Geplanter Rechenweg', expanded=True):
            for i, step in enumerate(steps, 1):
                st.write(f'{i:02d} · {step}')
    with right:
        card('LEITGEDANKE', 'Was du hier untersuchen wirst', insight,
             status='Wissenschaftlicher Fokus', icon='◎')
    with st.expander('Vorgesehene Datenquellen'):
        for path in data:
            st.code(path, language=None)
