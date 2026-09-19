import plotly.express as px
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
