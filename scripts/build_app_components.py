from pathlib import Path

# 1. app/components/ui_helpers.py
ui_helpers_code = """import streamlit as st

def apply_custom_css():
    st.markdown('''
    <style>
    /* Metric Card Styling */
    .metric-card {
        background: linear-gradient(135deg, #1e293b 0%, #0f172a 100%);
        border: 1px solid #334155;
        border-radius: 12px;
        padding: 18px 20px;
        margin-bottom: 15px;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.2);
    }
    .metric-label {
        font-size: 0.85rem;
        color: #94a3b8;
        text-transform: uppercase;
        letter-spacing: 0.05em;
        font-weight: 600;
        margin-bottom: 4px;
    }
    .metric-value {
        font-size: 1.85rem;
        font-weight: 700;
        color: #38bdf8;
    }
    .metric-sub {
        font-size: 0.8rem;
        color: #64748b;
        margin-top: 4px;
    }

    /* Status Badges */
    .badge-matched {
        background-color: #065f46;
        color: #6ee7b7;
        padding: 4px 10px;
        border-radius: 9999px;
        font-size: 0.75rem;
        font-weight: 600;
        display: inline-block;
    }
    .badge-partial {
        background-color: #854d0e;
        color: #fde047;
        padding: 4px 10px;
        border-radius: 9999px;
        font-size: 0.75rem;
        font-weight: 600;
        display: inline-block;
    }
    .badge-missing {
        background-color: #991b1b;
        color: #fca5a5;
        padding: 4px 10px;
        border-radius: 9999px;
        font-size: 0.75rem;
        font-weight: 600;
        display: inline-block;
    }
    .badge-high {
        background-color: #7f1d1d;
        color: #f87171;
        padding: 3px 8px;
        border-radius: 6px;
        font-size: 0.75rem;
        font-weight: bold;
    }
    .badge-medium {
        background-color: #78350f;
        color: #fbbf24;
        padding: 3px 8px;
        border-radius: 6px;
        font-size: 0.75rem;
        font-weight: bold;
    }
    .badge-low {
        background-color: #1e3a8a;
        color: #93c5fd;
        padding: 3px 8px;
        border-radius: 6px;
        font-size: 0.75rem;
        font-weight: bold;
    }

    /* Card Box */
    .feature-card {
        background-color: #1e293b;
        border: 1px solid #334155;
        border-radius: 10px;
        padding: 16px;
        margin-bottom: 12px;
    }
    </style>
    ''', unsafe_allow_html=True)

def render_metric_card(label: str, value: str, subtext: str = ""):
    html = f'''
    <div class="metric-card">
        <div class="metric-label">{label}</div>
        <div class="metric-value">{value}</div>
        {f'<div class="metric-sub">{subtext}</div>' if subtext else ''}
    </div>
    '''
    st.markdown(html, unsafe_allow_html=True)
"""
Path('app/components/ui_helpers.py').write_text(ui_helpers_code, encoding='utf-8')

# 2. app/components/charts.py
charts_code = """import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
from typing import List, Dict, Any

def create_radar_chart(categories: List[str], candidate_scores: List[float], role_benchmark: List[float], title: str = "Competency Radar"):
    fig = go.Figure()

    fig.add_trace(go.Scatterpolar(
        r=candidate_scores + [candidate_scores[0]],
        theta=categories + [categories[0]],
        fill='toself',
        fillcolor='rgba(56, 189, 248, 0.3)',
        line=dict(color='#38bdf8', width=2),
        name='Candidate Profile'
    ))

    fig.add_trace(go.Scatterpolar(
        r=role_benchmark + [role_benchmark[0]],
        theta=categories + [categories[0]],
        fill='toself',
        fillcolor='rgba(234, 179, 8, 0.15)',
        line=dict(color='#eab308', width=2, dash='dash'),
        name='Role Benchmark'
    ))

    fig.update_layout(
        title=dict(text=title, font=dict(size=16, color='#f8fafc')),
        polar=dict(
            radialaxis=dict(visible=True, range=[0, 1.0], color='#94a3b8'),
            angularaxis=dict(color='#e2e8f0')
        ),
        showlegend=True,
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        margin=dict(l=40, r=40, t=50, b=40),
        legend=dict(font=dict(color='#e2e8f0'))
    )
    return fig

def create_role_ranking_bar(roles_df: pd.DataFrame):
    top_df = roles_df.head(8).sort_values(by='suitability_score', ascending=True)
    
    fig = go.Figure(go.Bar(
        x=top_df['suitability_score'],
        y=top_df['role'],
        orientation='h',
        marker=dict(
            color=top_df['suitability_score'],
            colorscale='Tealgrn',
            showscale=False
        ),
        text=[f"{s:.1f}%" for s in top_df['suitability_score']],
        textposition='outside',
        textfont=dict(color='#f8fafc', size=12)
    ))
    
    fig.update_layout(
        title=dict(text="Top Career Role Suitability Matches", font=dict(size=16, color='#f8fafc')),
        xaxis=dict(title="Suitability Match (%)", range=[0, 105], color='#94a3b8'),
        yaxis=dict(color='#e2e8f0'),
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        margin=dict(l=20, r=40, t=40, b=30)
    )
    return fig

def create_waterfall_chart(drivers: List[Dict[str, Any]], title: str = "Suitability Score Impact Drivers"):
    features = [d['feature'] for d in drivers]
    contributions = [d['contribution'] for d in drivers]
    colors = ['#10b981' if c >= 0 else '#ef4444' for c in contributions]
    
    fig = go.Figure(go.Bar(
        x=contributions,
        y=features,
        orientation='h',
        marker=dict(color=colors),
        text=[f"{c:+.2f}" for c in contributions],
        textposition='outside',
        textfont=dict(color='#f8fafc')
    ))
    
    fig.update_layout(
        title=dict(text=title, font=dict(size=16, color='#f8fafc')),
        xaxis=dict(title="Relative Feature Impact (+ Boost / - Penalty)", color='#94a3b8'),
        yaxis=dict(color='#e2e8f0', autorange="reversed"),
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        margin=dict(l=20, r=50, t=40, b=30)
    )
    return fig

def create_market_demand_chart(df_demand: pd.DataFrame, top_n: int = 12):
    sub = df_demand.head(top_n).sort_values(by='demand_count', ascending=True)
    
    fig = px.bar(
        sub,
        x='demand_count',
        y='skill_name',
        color='category',
        orientation='h',
        title=f"Top {top_n} Most Demanded Skills in Job Market",
        labels={'demand_count': 'Job Postings Count', 'skill_name': 'Skill', 'category': 'Domain'}
    )
    fig.update_layout(
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font=dict(color='#e2e8f0'),
        margin=dict(l=20, r=20, t=40, b=30)
    )
    return fig
"""
Path('app/components/charts.py').write_text(charts_code, encoding='utf-8')
print('UI helpers and charts components created!')
