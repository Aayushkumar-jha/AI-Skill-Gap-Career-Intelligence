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
from components.ui_helpers import apply_custom_css, render_metric_card
from components.charts import create_waterfall_chart
from src.features.feature_engineering import FeatureEngineer
from src.models.role_classifier import RoleClassifier
from src.explainability.shap_analysis import ExplainabilityEngine

st.set_page_config(page_title="Explainable AI | AI Skill-Gap", page_icon="🧠", layout="wide")
apply_custom_css()

st.title("🧠 Explainable AI (XAI) & SHAP Attribution")
st.markdown("Demystifying model predictions: Understanding positive boost drivers and missing skill penalties.")
st.divider()

cand_skills = st.session_state.get("candidate_skills", {})
exp_years = st.session_state.get("experience_years", 2.0)
edu_level = st.session_state.get("education_level", "Bachelor's")
target_role = st.session_state.get("target_role", "Data Scientist")

fe = FeatureEngineer()
clf = RoleClassifier()
explainer = ExplainabilityEngine(clf, fe.get_feature_names())

feat_vec = fe.candidate_to_feature_vector(cand_skills, exp_years, edu_level)
explanation = explainer.explain_candidate_prediction(feat_vec, target_role)

# Metrics
c1, c2, c3 = st.columns(3)
with c1:
    render_metric_card("Analyzed Role", target_role, "Target explanation profile")
with c2:
    render_metric_card("Top Positive Driver", explanation['positive_drivers'][0]['feature'] if explanation['positive_drivers'] else "N/A", "Strongest positive contribution")
with c3:
    render_metric_card("Top Gap Penalty", explanation['negative_penalties'][0]['feature'] if explanation['negative_penalties'] else "None", "Strongest negative drag")

st.markdown("<br>", unsafe_allow_html=True)

# Waterfall Chart
st.subheader(f"📈 Feature Contribution Waterfall for {target_role}")
top_drivers = explanation['positive_drivers'][:5] + explanation['negative_penalties'][:5]
st.plotly_chart(create_waterfall_chart(top_drivers, f"Key Drivers Behind {target_role} Suitability"), use_container_width=True)

st.markdown("<br>", unsafe_allow_html=True)

# Detailed Breakdown
col_pos, col_neg = st.columns(2)

with col_pos:
    st.subheader("✅ Positive Drivers (+ Score Boost)")
    st.markdown("Competencies and profile factors that significantly qualified the candidate:")
    for pos in explanation['positive_drivers']:
        st.markdown(f"- **{pos['feature']}**: `+{pos['contribution']:.3f}` contribution")

with col_neg:
    st.subheader("❌ Missing Gap Penalties (- Score Drag)")
    st.markdown("Critical absent skills or deficit factors that dampened suitability:")
    for neg in explanation['negative_penalties']:
        st.markdown(f"- **{neg['feature']}**: `{neg['contribution']:.3f}` penalty")

st.divider()
st.info("💡 **Explainability Note**: Unlike uninterpretable black-box algorithms, our system attributes exact quantitative Shapley weights to every skill and background vector, ensuring transparent career decision-support.")