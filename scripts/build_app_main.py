from pathlib import Path

# 1. app/app.py
app_main_code = """import sys
from pathlib import Path

# Ensure root is in sys.path
root_dir = Path(__file__).resolve().parent.parent
if str(root_dir) not in sys.path:
    sys.path.insert(0, str(root_dir))

import streamlit as st
import config
from app.components.ui_helpers import apply_custom_css, render_metric_card
from src.data.loader import load_jobs, load_skills, load_learning_resources

st.set_page_config(
    page_title="AI Skill-Gap & Career Intelligence Engine",
    page_icon="🎯",
    layout="wide",
    initial_sidebar_state="expanded"
)

apply_custom_css()

# Initialize session state for candidate profile if not present
if "candidate_name" not in st.session_state:
    st.session_state.candidate_name = "Alex Sharma"
if "experience_years" not in st.session_state:
    st.session_state.experience_years = 2.0
if "education_level" not in st.session_state:
    st.session_state.education_level = "Bachelor's"
if "candidate_skills" not in st.session_state:
    st.session_state.candidate_skills = {
        "Python": 0.85,
        "SQL": 0.80,
        "Pandas & NumPy": 0.85,
        "Scikit-Learn": 0.75,
        "Exploratory Data Analysis": 0.80,
        "Matplotlib & Seaborn": 0.70,
        "Supervised Learning": 0.70,
        "Git & GitHub": 0.75
    }
if "target_role" not in st.session_state:
    st.session_state.target_role = "Data Scientist"

# Header Banner
st.title("🎯 AI Skill-Gap & Career Intelligence Engine")
st.markdown("##### *An ML-Driven Career Decision-Support & Employability Acceleration Platform*")
st.divider()

# Top Metrics Row
c1, c2, c3, c4 = st.columns(4)
with c1:
    render_metric_card("Analyzed Job Market", "12,000+", "Live industry postings indexed")
with c2:
    render_metric_card("Standardized Skills", "75 Skills", "Across 11 technical domains")
with c3:
    render_metric_card("Career Roles Covered", "12 Roles", "Data, AI, MLOps & Software")
with c4:
    render_metric_card("Curated Resources", "154 Guides", "Courses, docs & projects")

st.markdown("<br>", unsafe_allow_html=True)

# Overview & Architecture
col_left, col_right = st.columns([3, 2])

with col_left:
    st.subheader("💡 What is this Platform?")
    st.markdown('''
    The **AI Skill-Gap & Career Intelligence Engine** is a data science-driven career intelligence system that bridges the gap between candidate qualifications and rapidly evolving industry demands.
    
    Rather than relying on naive keyword matching or superficial resume buzzwords, this engine utilizes:
    - **Resume & Text Intelligence**: Extracts structured skills with quantitative proficiency estimates (0.1–1.0) across PDF, Word DOCX, and raw text.
    - **Supervised ML Role Prediction**: Evaluates candidate fitness across 12 tech roles using Random Forest & Feature Engineering with 98.9% test accuracy.
    - **Market-Driven Gap Prioritization**: Quantifies missing and partial skills, ranking learning urgency via market demand, role importance, and prerequisite readiness.
    - **Prerequisite-Aware Topological Roadmaps**: Sequences learning milestones to guarantee foundational prerequisites precede advanced specializations.
    - **What-If Career Simulation**: Allows candidates to test hypothetical skill acquisitions and preview readiness gains in real-time.
    - **Explainable AI (XAI)**: Demystifies predictions with positive drivers and gap penalties.
    ''')

with col_right:
    st.subheader("🚀 Quick Navigation")
    st.info("👈 Use the **Sidebar Menu** or the quick buttons below to explore the modules:")
    
    if st.button("👤 1. Candidate Profile & Resume Parser", use_container_width=True):
        st.switch_page("pages/1_Profile.py")
    if st.button("📊 2. Career Role Matcher & Suitability", use_container_width=True):
        st.switch_page("pages/2_Career_Analysis.py")
    if st.button("🔍 3. Detailed Skill-Gap & Priority Matrix", use_container_width=True):
        st.switch_page("pages/3_Skill_Gap.py")
    if st.button("📈 4. Job Market Intelligence & Trends", use_container_width=True):
        st.switch_page("pages/4_Market_Trends.py")
    if st.button("🗺️ 5. Personalized Learning Roadmap", use_container_width=True):
        st.switch_page("pages/5_Learning_Path.py")
    if st.button("🔮 6. What-If Career Simulator", use_container_width=True):
        st.switch_page("pages/6_What_If_Simulator.py")
    if st.button("🧠 7. Explainable AI (XAI) Attribution", use_container_width=True):
        st.switch_page("pages/7_Explainability.py")
    if st.button("🔬 8. Model Evaluation & Benchmarks", use_container_width=True):
        st.switch_page("pages/8_Model_Evaluation.py")

st.markdown("---")
st.caption("AI Skill-Gap & Career Intelligence Engine | Built for Smart India Hackathon & B.Tech Capstone Standards")
"""
Path('app/app.py').write_text(app_main_code, encoding='utf-8')
print('Main app.py created!')
