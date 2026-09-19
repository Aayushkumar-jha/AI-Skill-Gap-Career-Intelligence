import sys
from pathlib import Path
root_dir = Path(__file__).resolve().parent.parent
app_dir = Path(__file__).resolve().parent
if str(root_dir) not in sys.path:
    sys.path.insert(0, str(root_dir))
if str(app_dir) not in sys.path:
    sys.path.insert(0, str(app_dir))

import streamlit as st
import config
from components.ui_helpers import apply_custom_css, render_metric_card
from src.data.loader import load_jobs, load_skills, load_learning_resources

st.set_page_config(
    page_title="Home | AI Skill-Gap & Career Intelligence Engine",
    page_icon="🏠",
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

# Overview & Core Intelligence Pillars (Full Width - Quick Navigation Removed)
st.subheader("💡 What is this Platform?")
st.markdown('''
The **AI Skill-Gap & Career Intelligence Engine** is a data science-driven career intelligence system designed to help students, job seekers, and placement cells understand employability, identify suitable job roles, quantify skill gaps, and generate personalized, prerequisite-aware learning pathways.

Rather than relying on naive keyword matching or superficial resume buzzwords, this engine utilizes:
''')

col1, col2 = st.columns(2)

with col1:
    st.markdown('''
    - 📄 **Resume & Text Intelligence**: Extracts structured skills with quantitative proficiency estimates (`0.10`–`1.00`) across PDF, Word DOCX, and raw text formats.
    - 🤖 **Supervised ML Role Prediction**: Evaluates candidate fitness across 12 tech roles using Random Forest & Feature Engineering with **98.89% test accuracy**.
    - ⚖️ **Market-Driven Gap Prioritization**: Quantifies missing and partial skills, ranking learning urgency via mathematical weighting:
      $$\\text{Priority} = 0.35 \\cdot \\text{Demand} + 0.30 \\cdot \\text{Importance} + 0.20 \\cdot \\text{Deficiency} + 0.15 \\cdot \\text{PrereqReadiness}$$
    ''')

with col2:
    st.markdown('''
    - 🗺️ **Prerequisite-Aware DAG Roadmaps**: Sequences learning milestones via topological graph traversal ensuring foundational prerequisites precede advanced specializations.
    - 🔮 **What-If Career Simulation**: Allows candidates to test hypothetical skill acquisitions and preview readiness gains in real-time.
    - 🧠 **Explainable AI (XAI)**: Demystifies predictions by breaking down positive qualification drivers vs. missing skill penalties via interactive waterfall charts.
    ''')

st.markdown("<br>", unsafe_allow_html=True)

st.markdown("---")
