"""Plotly views of observed data only; no model, matching or inferred values."""
from datetime import date
import plotly.graph_objects as go
from dashboard.design import plotly_layout, COLORS

SPORT_LABELS = {'Running':'Laufen', 'Cycling':'Radfahren', 'Strength':'Krafttraining',
                'Swimming':'Schwimmen', 'Walking':'Gehen', 'Hiking':'Wandern',
                'Tennis':'Tennis', 'Padel':'Padel'}


def weekly_chart(activity, unit):
    minutes = unit == 'Trainingsminuten'
    values = [row['total_duration_min' if minutes else 'activities_count'] for row in activity['weeks']]
    label = 'Trainingsminuten' if minutes else 'Aktivitäten'
    fig = go.Figure(go.Bar(
        x=[date.fromisoformat(row['week_start']) for row in activity['weeks']], y=values,
        marker_color=COLORS['accent'], marker_line_width=0, name=label, showlegend=False,
        customdata=[[date.fromisoformat(row['week_start']).strftime('%d.%m.'),
                     date.fromisoformat(row['week_end']).strftime('%d.%m.%Y'),row['week_index']] for row in activity['weeks']],
        hovertemplate='Woche %{customdata[2]} · %{customdata[0]}–%{customdata[1]}<br>'+label+': %{y}<extra></extra>'))
    # Zero-valued bars have no height: explicit baseline markers retain their visibility.
    zeros = [i for i, row in enumerate(activity['weeks']) if row['activities_count'] == 0]
    if zeros:
        fig.add_trace(go.Scatter(x=[date.fromisoformat(activity['weeks'][i]['week_start']) for i in zeros],
                                y=[0]*len(zeros), mode='markers', marker=dict(color=COLORS['blue'],size=8,symbol='diamond'),
                                name='Woche ohne Aktivität', hovertemplate='Woche ab %{x|%d.%m.%Y}<br>0 Aktivitäten · 0 Minuten<extra></extra>'))
    fig.update_layout(**plotly_layout(), height=300, showlegend=bool(zeros), bargap=.32,
                      legend=dict(orientation='h',y=1.12,x=0), hovermode='closest')
    fig.update_xaxes(title='Wochenbeginn · 05.01.–05.07.2026', tickformat='%d.%m.', showgrid=False)
    fig.update_yaxes(title=label, rangemode='tozero', gridcolor='#30483B', dtick=None if minutes else 1)
    return fig


def sports_chart(activity):
    counts = activity['sport_counts']
    sports = sorted(counts, key=lambda sport: (-counts[sport], sport))
    total = activity['total_activities']
    fig = go.Figure(go.Bar(
        x=[counts[sport] for sport in sports], y=[SPORT_LABELS.get(sport,sport) for sport in sports], orientation='h',
        marker_color=COLORS['blue'], text=[str(counts[sport]) for sport in sports], textposition='outside',
        customdata=[[counts[sport]/total*100] for sport in sports],
        hovertemplate='%{y}<br>%{x} Aktivitäten · %{customdata[0]:.1f} %<extra></extra>'))
    fig.update_layout(**plotly_layout(), height=340, showlegend=False)
    fig.update_yaxes(autorange='reversed',showgrid=False)
    fig.update_xaxes(title='Anzahl beobachteter Aktivitäten',rangemode='tozero',gridcolor='#30483B')
    return fig
