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
import numpy as np
import plotly.graph_objects as go
import config
from components.ui_helpers import apply_custom_css, render_metric_card
from src.features.feature_engineering import FeatureEngineer
from src.models.role_classifier import RoleClassifier
from src.data.loader import load_skills

st.set_page_config(page_title="What-If Simulator | AI Skill-Gap", page_icon="🔮", layout="wide")
apply_custom_css()

st.title("🔮 What-If Career Simulator")
st.markdown("Hypothetically acquire new industry skills and simulate your employability & readiness gains.")
st.divider()

cand_skills = dict(st.session_state.get("candidate_skills", {}))
exp_years = st.session_state.get("experience_years", 2.0)
edu_level = st.session_state.get("education_level", "Bachelor's")
target_role = st.session_state.get("target_role", "Data Scientist")

fe = FeatureEngineer()
clf = RoleClassifier()
all_skills = load_skills()['skill_name'].unique().tolist()
available_hypo = [s for s in all_skills if s not in cand_skills]

# Baseline Prediction
base_vec = fe.candidate_to_feature_vector(cand_skills, exp_years, edu_level)
base_preds = clf.predict_roles(base_vec)
base_dict = dict(zip(base_preds['role'], base_preds['suitability_score']))
base_rank_dict = dict(zip(base_preds['role'], base_preds['rank']))

st.subheader("🧪 Simulation Playground")
st.markdown("Select hypothetical skills you plan to master over the next 3–6 months:")

sim_col1, sim_col2 = st.columns([3, 1])
with sim_col1:
    selected_hypo = st.multiselect(
        "Choose hypothetical skills to acquire:",
        available_hypo,
        default=available_hypo[:2] if len(available_hypo) >= 2 else available_hypo
    )
with sim_col2:
    hypo_prof = st.slider("Target Proficiency Level", 0.5, 1.0, 0.85, 0.05)

# Simulate Feature Vector
sim_skills = dict(cand_skills)
for s in selected_hypo:
    sim_skills[s] = hypo_prof

sim_vec = fe.candidate_to_feature_vector(sim_skills, exp_years, edu_level)
sim_preds = clf.predict_roles(sim_vec)
sim_dict = dict(zip(sim_preds['role'], sim_preds['suitability_score']))
sim_rank_dict = dict(zip(sim_preds['role'], sim_preds['rank']))

# Delta Metrics for Target Role
target_base_score = base_dict.get(target_role, 0.0)
target_sim_score = sim_dict.get(target_role, 0.0)
delta_score = target_sim_score - target_base_score
target_base_rank = base_rank_dict.get(target_role, 12)
target_sim_rank = sim_rank_dict.get(target_role, 12)

st.markdown("<br>", unsafe_allow_html=True)

# Comparison Cards
c1, c2, c3, c4 = st.columns(4)
with c1:
    render_metric_card("Current Score", f"{target_base_score:.1f}%", f"Rank #{target_base_rank} for {target_role}")
with c2:
    render_metric_card("Simulated Score", f"{target_sim_score:.1f}%", f"Rank #{target_sim_rank} for {target_role}")
with c3:
    sign = "+" if delta_score >= 0 else ""
    render_metric_card("Readiness Boost", f"{sign}{delta_score:.1f}%", "Employability jump")
with c4:
    est_effort = len(selected_hypo) * 4 # ~4 weeks per skill
    render_metric_card("Learning Investment", f"~{est_effort} Weeks", "Estimated study effort")

st.markdown("<br>", unsafe_allow_html=True)

# Comparative Bar Chart
st.subheader("📊 Before vs. After Suitability Comparison (Top 8 Roles)")

top_roles = base_preds.head(8)['role'].tolist()
scores_before = [base_dict[r] for r in top_roles]
scores_after = [sim_dict[r] for r in top_roles]

fig = go.Figure()
fig.add_trace(go.Bar(
    x=top_roles,
    y=scores_before,
    name='Current Readiness',
    marker_color='#64748b'
))
fig.add_trace(go.Bar(
    x=top_roles,
    y=scores_after,
    name='Simulated Readiness (With Added Skills)',
    marker_color='#10b981'
))

fig.update_layout(
    barmode='group',
    title=dict(text="Impact of Hypothetical Skills on Role Readiness", font=dict(size=16, color='#f8fafc')),
    yaxis=dict(title="Suitability Score (%)", range=[0, 105], color='#94a3b8'),
    xaxis=dict(color='#e2e8f0', tickangle=25),
    paper_bgcolor='rgba(0,0,0,0)',
    plot_bgcolor='rgba(0,0,0,0)',
    legend=dict(font=dict(color='#e2e8f0')),
    margin=dict(l=20, r=20, t=40, b=60)
)
st.plotly_chart(fig, use_container_width=True)

st.divider()
st.subheader("📋 Comprehensive Simulation Breakdown")
comp_df = pd.DataFrame([{
    'Role': r,
    'Current Score (%)': f"{base_dict[r]:.1f}%",
    'Simulated Score (%)': f"{sim_dict[r]:.1f}%",
    'Delta (%)': f"{sim_dict[r] - base_dict[r]:+.1f}%",
    'Current Rank': f"#{base_rank_dict[r]}",
    'Simulated Rank': f"#{sim_rank_dict[r]}"
} for r in config.TARGET_ROLES])
st.dataframe(comp_df, use_container_width=True, hide_index=True)