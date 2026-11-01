"""Central offline design tokens for native widgets, MOVA cards and Plotly."""
from pathlib import Path
import streamlit as st

COLORS = {'background': '#0B1110', 'surface': '#14201C', 'text': '#F2F7F4',
          'muted': '#B4C6BC', 'accent': '#7DE2A6', 'blue': '#76B7E5', 'orange': '#F1B675'}


def apply_design():
    css = Path(__file__).with_name('styles.css').read_text(encoding='utf-8')
    st.markdown(f'<style>{css}</style>', unsafe_allow_html=True)


def plotly_layout():
    """Shared chart styling for later real-data charts; no example data."""
    return dict(template='plotly_dark', paper_bgcolor=COLORS['surface'],
                plot_bgcolor=COLORS['surface'], font=dict(color=COLORS['text'], size=16),
                colorway=[COLORS['accent'], COLORS['blue'], COLORS['orange']],
                margin=dict(l=30, r=20, t=45, b=35))
