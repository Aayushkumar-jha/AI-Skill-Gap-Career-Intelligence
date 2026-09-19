import sys
from pathlib import Path
root_dir = Path(__file__).resolve().parent.parent
app_dir = Path(__file__).resolve().parent
if str(root_dir) not in sys.path:
    sys.path.insert(0, str(root_dir))
if str(app_dir) not in sys.path:
    sys.path.insert(0, str(app_dir))

import streamlit as st
import numpy as np
import pandas as pd
import config
from components.ui_helpers import apply_custom_css, render_metric_card
from components.charts import create_radar_chart, create_role_ranking_bar
from src.features.feature_engineering import FeatureEngineer
from src.models.role_classifier import RoleClassifier

st.set_page_config(page_title="Career Analysis | AI Skill-Gap", page_icon="📊", layout="wide")
apply_custom_css()

st.title("📊 Career Role Suitability & Ranking")
st.markdown("Supervised Machine Learning prediction of role readiness across 12 tech domains.")
st.divider()

cand_skills = st.session_state.get("candidate_skills", {})
exp_years = st.session_state.get("experience_years", 2.0)
edu_level = st.session_state.get("education_level", "Bachelor's")

if not cand_skills:
    st.warning("No candidate skills found! Please set up your profile first.")
    if st.button("Go to Profile Setup"):
        st.switch_page("pages/1_Profile.py")
    st.stop()

# Feature Vector & Model Prediction
fe = FeatureEngineer()
clf = RoleClassifier()

feat_vec = fe.candidate_to_feature_vector(cand_skills, exp_years, edu_level)
predictions_df = clf.predict_roles(feat_vec)

top_role = predictions_df.iloc[0]['role']
top_score = predictions_df.iloc[0]['suitability_score']
st.session_state.top_role = top_role

# Top Metrics
m1, m2, m3, m4 = st.columns(4)
with m1:
    render_metric_card("Top Match Role", top_role, "Highest ML affinity")
with m2:
    render_metric_card("Suitability Score", f"{top_score:.1f}%", "Calibrated model confidence")
with m3:
    render_metric_card("Candidate Skills", str(len(cand_skills)), "Skills in active profile")
with m4:
    render_metric_card("Experience Level", f"{exp_years} Yrs", f"Education: {edu_level}")

st.markdown("<br>", unsafe_allow_html=True)

# Visualizations Row
col_bar, col_radar = st.columns([3, 2])

with col_bar:
    st.plotly_chart(create_role_ranking_bar(predictions_df), use_container_width=True)

with col_radar:
    # Compute radar competency
    categories = config.SKILL_CATEGORIES[:8] # First 8 core domains
    cand_cat_scores = []
    benchmark_scores = [0.85, 0.80, 0.75, 0.70, 0.75, 0.65, 0.70, 0.65] # Benchmark
    for cat in categories:
        skills_in_c = fe.cat_to_skills.get(cat, [])
        profs = [cand_skills.get(s, 0.0) for s in skills_in_c]
        cand_cat_scores.append(round(float(np.mean(sorted(profs, reverse=True)[:2])) if profs else 0.0, 2))
        
    radar_fig = create_radar_chart(categories, cand_cat_scores, benchmark_scores, f"Competency vs {top_role} Archetype")
    st.plotly_chart(radar_fig, use_container_width=True)

st.divider()

# Target Role Selector for Downstream Analysis
st.subheader("🎯 Select Target Role for Skill-Gap Analysis")
target_role = st.selectbox(
    "Choose which career role you want to analyze and optimize for:",
    predictions_df['role'].tolist(),
    index=0
)
st.session_state.target_role = target_role

# Role summary card
role_row = predictions_df[predictions_df['role'] == target_role].iloc[0]
st.info(f"Target Role selected: **{target_role}** | Current Readiness Score: **{role_row['suitability_score']:.1f}%** (Rank #{role_row['rank']})")

if st.button("🔍 Deep Dive into Skill-Gap Analysis for " + target_role, type="primary", use_container_width=True):
    st.switch_page("pages/3_Skill_Gap.py")