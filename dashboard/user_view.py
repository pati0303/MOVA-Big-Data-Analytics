"""Personal MOVA view. Every render uses a fresh permission-bound context."""
from html import escape
from math import isfinite
import streamlit as st
from dashboard.components import card, section_title
from dashboard.data_access import DataAccessError
from dashboard.services import user_context
from dashboard.charts import weekly_chart, sports_chart, SPORT_LABELS
from dashboard.state import capabilities

STATUS = {
 'permission_denied':'Die simulierte Garmin-Freigabe fehlt.',
 'missing_or_ineligible':'Es liegt kein gültiges gespeichertes Segment vor.',
 'missing_profile':'Das beobachtete Aktivitätsprofil ist nicht verfügbar.',
 'invalid_profile':'Das Aktivitätsprofil konnte nicht bestätigt werden.',
 'inactive':'Für dieses Profil liegt keine beobachtete Aktivität vor.',
 'unverified_activity_data':'Die Aktivitätsquellen konnten nicht verifiziert werden.',
 'profile_not_yet_available':'Das vollständige Beobachtungsprofil liegt zu diesem Stichtag noch nicht vor.',
 'insufficient_history':'Es fehlen vier vollständige historische Wochen.',
 'invalid_history':'Die vier historischen Eingabewochen sind nicht vollständig gültig.',
 'model_training_after_cutoff':'Das gespeicherte Modell ist für diesen früheren Stichtag nicht zulässig.',
 'model_unavailable_or_invalid':'Das gespeicherte Prognosemodell ist nicht verfügbar oder nicht gültig.',
 'interests_permission_denied':'Die simulierte Interessenfreigabe fehlt.',
 'invalid_or_missing_interests':'Die Interessenkategorien fehlen oder sind ungültig.',
 'no_positive_interests':'Für diesen synthetischen Nutzer ist keine positive Interessenkategorie gespeichert.'}


def number(value, places=0):
    return f'{value:,.{places}f}'.replace(',', 'X').replace('.', ',').replace('X', '.')


def unavailable(status):
    return STATUS.get(status, 'Dieser Kontext ist derzeit nicht verfügbar.')


def metric_card(label, value, detail):
    st.markdown(f'<article class="mova-stat"><div class="mova-eyebrow">{escape(label)}</div>'
                f'<div class="mova-stat-value">{escape(value)}</div><p>{escape(detail)}</p></article>', unsafe_allow_html=True)


def offers_view(result, allowed):
    section_title('03', 'Neue Möglichkeiten entdecken', 'Fiktive Angebote · Rangfolge und Begründungen aus der bestehenden MOVA-Engine.')
    if not allowed:
        st.info('Angebotsbereich gesperrt: Die simulierte Interessenfreigabe ist ausgeschaltet.')
        return
    if result is None:
        st.warning('Der Angebotskontext konnte nicht geladen werden.')
        return
    categories = result.get('interest_categories', [])
    if categories:
        st.caption('Positiv ausgewählte Interessenkategorien: ' + ' · '.join(categories))
    offers = result['recommendations']
    if not offers:
        st.info(unavailable(result['personalization_status']))
        return
    st.caption('A: bestätigter Sportbezug und beobachtete Aktivität. B: zulässiges Kategorieangebot. '
               'Die Rangstufe ist keine Bewertung deiner Fitness oder der Angebotsqualität. '
               'Je Vergleichsgruppe erscheint höchstens eine Variante. Preise und Rabatte der neuen '
               'Angebote O031–O038 sind frei erfundene Demonstrationswerte.')
    # Render in original ranking order. No sorting, matching or additional offers.
    for start in range(0, len(offers), 2):
        for col, offer in zip(st.columns(2, gap='medium'), offers[start:start+2]):
            with col:
                title = escape(offer['offer_title'])
                st.markdown(f'''<article class="mova-offer">
                  <div class="mova-offer-top"><span class="mova-eyebrow">{escape(offer['category'])} · {escape(offer['offer_id'])}</span>
                  <span class="mova-tier">Stufe {escape(offer['ranking_tier'])} · Platz {offer['ranking_position']}</span></div>
                  <h3>{title}</h3><div class="mova-price">{number(offer['price_eur'],2)} €
                  <span>{offer['discount_pct']} % Rabatt laut Katalog</span></div>
                  <p>{escape(offer['match_reason'])}</p>
                  <div class="mova-card-status">Fiktives Angebot · Katalogpreis und Rabatt separat angegeben</div>
                  </article>''', unsafe_allow_html=True)


def user_view(state):
    uid = state['selected_user_id']
    access = capabilities(state)
    st.markdown(f'<div class="mova-welcome"><div><div class="mova-kicker">DEIN MOVA · {escape(uid)}</div>'
                '<h1>Deine Bewegung im Blick.</h1></div>'
                '<p>05.01.–05.07.2026 · 26 beobachtete Wochen<br>Synthetische Daten · Move beyond.</p></div>', unsafe_allow_html=True)
    context, result = None, None
    if access['activity'] or access['offers']:
        try:
            context = user_context(uid, interests_permission=access['offers'], garmin_permission=access['activity'])
            result = context['engine']
        except DataAccessError as exc:
            st.error(str(exc))
    if not access['activity']:
        st.info('Aktivitätsbereiche gesperrt: Die simulierte Garmin-Freigabe ist ausgeschaltet.')
    elif context is not None:
        activity = context['activity']
        if activity is None:
            st.warning(context['activity_error'] or 'Aktivitätsdaten sind nicht verfügbar.')
        else:
            metrics = [('AKTIVITÄTEN GESAMT',number(activity['total_activities']),'Beobachtet in 26 Wochen'),
                       ('AKTIVITÄTEN / WOCHE',number(activity['avg_activities_per_week'],2),'Alle 26 Wochen, einschließlich Pausen'),
                       ('MINUTEN / WOCHE',number(activity['avg_minutes_per_week'],1),'Durchschnitt über den gesamten Zeitraum')]
            for col, args in zip(st.columns(3,gap='medium'),metrics):
                with col: metric_card(*args)
            st.caption(f"{activity['active_weeks']} aktive Wochen · {activity['zero_weeks']} Nullwochen · "
                       f"Häufigste beobachtete Sportart{'en' if len(activity['top_sports'])>1 else ''}: "
                       + ', '.join(SPORT_LABELS.get(s,s) for s in activity['top_sports']))
            trend, mix = st.columns([1.65,1],gap='medium')
            with trend:
                st.markdown('### Dein Trainingsverlauf')
                unit = st.segmented_control('Darstellung', ['Aktivitäten','Trainingsminuten'],
                                            default='Aktivitäten',key='training_unit',required=True)
                st.plotly_chart(weekly_chart(activity,unit),width='stretch',key='weekly_chart',config={'displayModeBar':False})
                st.caption('Blaue Rauten markieren Wochen ohne Aktivität. Alle 26 Wochen bleiben enthalten.')
            with mix:
                st.markdown('### Deine Sportarten')
                st.caption('Beobachtetes Verhalten, keine Aussage über persönliche Vorlieben.')
                st.plotly_chart(sports_chart(activity),width='stretch',key='sports_chart',config={'displayModeBar':False})
            with st.expander('Die 26 Wochen im Detail'):
                import pandas as pd
                table = pd.DataFrame(activity['weeks']).rename(columns={'week_index':'Woche','week_start':'Von',
                          'week_end':'Bis','activities_count':'Aktivitäten','total_duration_min':'Minuten'})
                st.dataframe(table,hide_index=True,width='stretch')
        section_title('02','Dein Muster und der Blick nach vorn','Aus synthetischen Beobachtungen · keine Fitness- oder Gesundheitsbewertung.')
        profile = result['profile']
        segment, prediction = st.columns(2,gap='medium')
        with segment:
            if profile['segment_status']=='available' and profile['segment_label'] is not None:
                card('DEIN AKTIVITÄTSMUSTER',profile['segment_label'],
                     'Dein Aktivitätsprofil zeigt diese relative Trainingshäufigkeit innerhalb der synthetischen Nutzergruppe. '
                     'Das ist keine Bewertung deiner Fitness, Gesundheit oder Erfahrung.',
                     status='Gespeichertes Segment · Beobachtungen bis 05.07.2026',icon='◈')
            else:
                card('DEIN AKTIVITÄTSMUSTER','Segment nicht verfügbar',unavailable(profile['segment_status']),status='Keine Ersatzzuordnung',icon='◈')
        with prediction:
            value=profile.get('regression_prediction')
            if profile['prediction_status']=='available' and isinstance(value,(int,float)) and isfinite(value):
                card('AUSBLICK · 06.–12.07.2026',f'{number(value,2)} geschätzte Aktivitäten',
                     'Die Schätzung nutzt die letzte abgeschlossene Woche und den Durchschnitt der letzten vier Wochen. '
                     'Sie ist unverbindlich; individuelle Fehler sind möglich. Für die Zielwoche liegen keine Istwerte vor.',
                     status='Historischer Demo-Stichtag 05.07.2026 · gespeichertes Modell',icon='↗')
            else:
                card('AUSBLICK · 06.–12.07.2026','Prognose nicht verfügbar',unavailable(profile['prediction_status']),status='Kein Ersatzwert',icon='↗')
        with st.expander('So entsteht der Ausblick'):
            if profile['prediction_status']=='available':
                features=profile['input_features']
                st.write(f"Aktivitäten in der letzten Woche: {number(features['activities_current_week'])}. "
                         f"Vierwochenmittel einschließlich dieser Woche: {number(features['avg_activities_last_4_weeks'],2)}.")
                st.caption(f"Historie: 08.06.–05.07.2026 · Eingabewoche endet {profile['input_week_end']} · "
                           f"Ziel: {profile['target_week_start']} bis {profile['target_week_end']}.")
                st.write('Ungerundete Modellschätzung:',profile['regression_prediction'])
                st.caption('Nur zur Anzeige gerundet; keine Kappung, kein neues Training und kein erfundenes Prognoseintervall. '
                           'Segment und Schätzung wählen ausschließlich fachlich zugeordnete Angebotsvarianten; die Begründung steht am jeweiligen Angebot.')
            else:
                st.write(unavailable(profile['prediction_status']))
    offers_view(result,access['offers'])
