import sys
from pathlib import Path
root_dir = Path(__file__).resolve().parent.parent
app_dir = Path(__file__).resolve().parent
if str(root_dir) not in sys.path:
    sys.path.insert(0, str(root_dir))
if str(app_dir) not in sys.path:
    sys.path.insert(0, str(app_dir))

import streamlit as st
import pandas as pd
import plotly.express as px
import config
from components.ui_helpers import apply_custom_css, render_metric_card
from components.charts import create_market_demand_chart
from src.data.loader import load_jobs, get_market_skill_demand

st.set_page_config(page_title="Market Trends | AI Skill-Gap", page_icon="📈", layout="wide")
apply_custom_css()

st.title("📈 Job-Market Intelligence & Demand Analytics")
st.markdown("Real-time market insights derived from 12,000+ indexed tech job postings.")
st.divider()

df_jobs = load_jobs()
df_demand = get_market_skill_demand()

# Filters
c_role, c_tier, c_loc = st.columns(3)
with c_role:
    roles_list = ["All Roles"] + config.TARGET_ROLES
    sel_role = st.selectbox("Filter by Role Category", roles_list)
with c_tier:
    tiers_list = ["All Tiers", "Entry Level", "Mid Level", "Senior Level", "Lead / Architect"]
    sel_tier = st.selectbox("Filter by Experience Tier", tiers_list)
with c_loc:
    locs_list = ["All Locations"] + sorted(df_jobs['location'].unique().tolist())
    sel_loc = st.selectbox("Filter by Location", locs_list)

filtered_jobs = df_jobs.copy()
if sel_role != "All Roles":
    filtered_jobs = filtered_jobs[filtered_jobs['role_category'] == sel_role]
if sel_tier != "All Tiers":
    filtered_jobs = filtered_jobs[filtered_jobs['experience_tier'] == sel_tier]
if sel_loc != "All Locations":
    filtered_jobs = filtered_jobs[filtered_jobs['location'] == sel_loc]

# KPI Summary
k1, k2, k3, k4 = st.columns(4)
with k1:
    render_metric_card("Active Postings", f"{len(filtered_jobs):,}", "In selected filter")
with k2:
    avg_sal = filtered_jobs['salary_lpa'].mean() if len(filtered_jobs) > 0 else 0
    render_metric_card("Avg Package", f"₹ {avg_sal:.1f} LPA", "Base salary compensation")
with k3:
    render_metric_card("Max Package", f"₹ {filtered_jobs['salary_lpa'].max():.1f} LPA" if len(filtered_jobs) > 0 else "N/A", "Top compensation tier")
with k4:
    avg_exp = filtered_jobs['min_experience_years'].mean() if len(filtered_jobs) > 0 else 0
    render_metric_card("Avg Experience", f"{avg_exp:.1f} Yrs", "Industry requirement")

st.markdown("<br>", unsafe_allow_html=True)

# Charts Row 1
c_chart1, c_chart2 = st.columns([3, 2])

with c_chart1:
    st.plotly_chart(create_market_demand_chart(df_demand, top_n=14), use_container_width=True)

with c_chart2:
    # Salary distribution by Role
    fig_sal = px.box(
        df_jobs,
        x='role_category',
        y='salary_lpa',
        color='experience_tier',
        title="Salary Distribution Across Tech Roles (₹ LPA)",
        labels={'salary_lpa': 'Salary (LPA)', 'role_category': 'Role'}
    )
    fig_sal.update_layout(
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font=dict(color='#e2e8f0'),
        xaxis=dict(tickangle=45),
        margin=dict(l=20, r=20, t=40, b=80)
    )
    st.plotly_chart(fig_sal, use_container_width=True)

# Charts Row 2: Top Hiring Companies and Locations
c_comp, c_city = st.columns(2)

with c_comp:
    top_companies = filtered_jobs['company'].value_counts().head(10).reset_index()
    top_companies.columns = ['Company', 'Job Postings']
    fig_comp = px.bar(
        top_companies,
        x='Job Postings',
        y='Company',
        orientation='h',
        title="Top Hiring Tech Companies",
        color='Job Postings',
        color_continuous_scale='Viridis'
    )
    fig_comp.update_layout(
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font=dict(color='#e2e8f0'),
        margin=dict(l=20, r=20, t=40, b=30)
    )
    st.plotly_chart(fig_comp, use_container_width=True)

with c_city:
    top_locs = filtered_jobs['location'].value_counts().head(10).reset_index()
    top_locs.columns = ['Location', 'Job Postings']
    fig_loc = px.pie(
        top_locs,
        names='Location',
        values='Job Postings',
        title="Hiring Volume by Geographic Hub",
        hole=0.4
    )
    fig_loc.update_layout(
        paper_bgcolor='rgba(0,0,0,0)',
        font=dict(color='#e2e8f0'),
        margin=dict(l=20, r=20, t=40, b=30)
    )
    st.plotly_chart(fig_loc, use_container_width=True)