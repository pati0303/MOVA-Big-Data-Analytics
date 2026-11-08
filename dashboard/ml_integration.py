"""Read-only presentation of the saved ML ablation; no engine or model calls."""
import hashlib
import json

import plotly.graph_objects as go
import streamlit as st

from dashboard.data_access import DataAccessError, PROJECT_ROOT
from dashboard.design import COLORS

VARIANTS = ('no_ml', 'kmeans_only', 'regression_only', 'both')
LABELS = ('Nur K-Means', 'Nur Regression', 'K-Means + Regression')


def load_ablation(root=PROJECT_ROOT):
    """Verify the saved artifact and reconcile summary with all paired ID lists."""
    directory = root / 'outputs/ml_recommendations_v1'
    try:
        manifest = json.loads((directory / 'manifest.json').read_bytes())
        raw = (directory / 'comparison.json').read_bytes()
        if hashlib.sha256(raw).hexdigest() != manifest['artifact_sha256']['comparison.json']:
            raise ValueError('Prüfsumme stimmt nicht.')
        data = json.loads(raw)
        summary, users = data['summary'], data['users']
        n = summary['users']
        if type(n) is not int or n <= 0 or len(users) != n:
            raise ValueError('Nutzerzahl ist nicht eindeutig.')
        if len({u['user_id'] for u in users}) != n:
            raise ValueError('Doppelte Nutzerkennung.')
        counts = dict.fromkeys(VARIANTS, 0)
        for user in users:
            lists = {}
            for variant in VARIANTS:
                offers = user['variants'][variant]
                ids = [offer['offer_id'] for offer in offers]
                if len(ids) > 5 or len(set(ids)) != len(ids):
                    raise ValueError('Ungültige Top-5-Liste.')
                lists[variant] = ids
            for variant in VARIANTS:
                counts[variant] += lists[variant] != lists['no_ml']
        saved = summary['changed_top5_vs_no_ml']
        if (set(saved) != set(VARIANTS) or
                any(type(saved[k]) is not int or saved[k] != counts[k] for k in VARIANTS)):
            raise ValueError('Zusammenfassung weicht von den Listen ab.')
        if summary['offers'] != 38:
            raise ValueError('Unerwartete Katalogbasis.')
        return n, counts
    except (OSError, ValueError, KeyError, TypeError, AttributeError) as exc:
        raise DataAccessError('ML-Ablation nicht verfügbar: Gespeicherte Ergebnisse fehlen, '
                              'sind nicht verifiziert oder nicht eindeutig interpretierbar.') from exc


def render_ml_integration(chart):
    st.divider()
    st.markdown('### ML-Integration – K-Means und Regression')
    st.caption('Nachgelagerte CRISP-DM-Iteration · Modeling → Evaluation → Deployment')
    st.markdown('**Ausgangspunkt:** Im ersten Demonstrator waren die Modelle sichtbar, beeinflussten '
                'die Angebote aber noch nicht. **Erweiterung:** Modellinformationen wählen nun '
                'Angebotsvarianten. **Prüfung:** gespeicherter Ablationstest vor der Integration in die User View.')
    left, right = st.columns(2)
    with left:
        st.markdown('#### K-Means · Nutzungshäufigkeit')
        st.markdown('- **Cluster 0:** geringere Trainingshäufigkeit → gelegentliche Nutzung: '
                    'Laufschuhe **O031**, Wanderset **O036**.\n'
                    '- **Cluster 1:** höhere Trainingshäufigkeit → häufige Nutzung: '
                    'Laufschuhe **O032**, Wanderset **O037**.')
    with right:
        st.markdown('#### Regression · Aktivitäten der Folgewoche')
        st.markdown('- **Unter 2:** Einzeltermin **O033**.\n'
                    '- **2 bis unter 3:** Standardauswahl bleibt bestehen, im aktuellen Katalog **O033**.\n'
                    '- **Ab 3:** Laufkurs **O034**, drei Termine pro Woche.')
    st.caption('Die Regression prognostiziert alle sportlichen Aktivitäten, nicht nur Laufeinheiten. '
               'Im mittleren Bereich greift keine spezielle Regressionsvariante; die bestehende Auswahl bleibt erhalten.')
    st.info('Die Modelle wählen Varianten innerhalb einer Angebotsgruppe; die Reihenfolge der Gruppen bleibt erhalten. '
            'Zuordnungen und Schwellen sind Demonstrationsannahmen, keine erlernten Entscheidungsregeln. '
            'Voraussetzung sind gültige Modellinformationen, passende Sporthistorie und die simulierten Freigaben.')
    st.markdown('#### ML-Ablation · Vergleich mit „Ohne ML“')
    try:
        n, counts = load_ablation()
    except DataAccessError as exc:
        st.warning(str(exc))
        st.caption('Es werden keine Ersatzwerte angezeigt. Der historische Vergleich oben bleibt davon unabhängig.')
        return
    st.caption(f'Referenz: Ohne ML · dieselben {n} synthetischen Nutzerprofile und dieselben 38 Angebote, '
               'jeweils höchstens eine Variante pro Gruppe. Beide ML-Signale sind in der Referenz deaktiviert. '
               'Verglichen wird jede geordnete Top-5-Liste mit dieser Referenz.')
    values = [counts[k] for k in VARIANTS[1:]]
    fig = go.Figure(go.Bar(
        x=values, y=LABELS, orientation='h',
        marker_color=[COLORS['accent'], COLORS['blue'], COLORS['accent']],
        text=[f'{v} von {n}' for v in values], textposition='outside', cliponaxis=False,
        hovertemplate='%{y}<br>%{text} veränderte Top-5-Listen<extra></extra>'))
    fig.update_xaxes(title='Nutzer mit veränderter Top-5-Liste gegenüber Ohne ML', range=[0, n], dtick=20)
    fig.update_yaxes(autorange='reversed')
    chart(fig, 'ml_ablation', 280)
    st.success(f'Erkenntnis · K-Means verändert bei {values[0]} von {n} Nutzern die Top-5-Liste, '
               f'Regression bei {values[1]} von {n}, beide zusammen bei {values[2]} von {n}. '
               'Damit ist der Einfluss der ML-Integration auf die Empfehlungen nachgewiesen; '
               'eine Verbesserung ihrer tatsächlichen Relevanz oder Qualität ist damit nicht belegt.')
    st.caption('Getrennte Untersuchungen: Oben historischer Interessen-/Sportartenvergleich mit 30 Angeboten '
               '(64/100 andere Zusammensetzungen); hier ML-Variantenwahl mit 38 Angeboten gegenüber Ohne ML.')
    with st.expander('Quellen der ML-Integration'):
        st.code('outputs/ml_recommendations_v1/comparison.json\n'
                'outputs/ml_recommendations_v1/manifest.json\n'
                'src/ml_recommendation_rules.py · select_variants()\n'
                'src/recommendation_engine.py · recommendations()\n'
                'data/catalog/recommendation_metadata_v1.json', language=None)
        st.caption('Nur gespeicherte Ergebnisse. Prüfsumme und Zählwerte gegen die gespeicherten Listen geprüft; '
                   'kein Training, keine erneute Evaluation und kein Export.')
