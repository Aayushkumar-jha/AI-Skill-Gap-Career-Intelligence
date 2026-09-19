import sys
from pathlib import Path

# 1. app/pages/1_Profile.py
page1_code = """import sys
from pathlib import Path
root_dir = Path(__file__).resolve().parent.parent.parent
if str(root_dir) not in sys.path:
    sys.path.insert(0, str(root_dir))

import streamlit as st
import json
import config
from app.components.ui_helpers import apply_custom_css, render_metric_card
from src.nlp.resume_parser import ResumeParser
from src.nlp.skill_extractor import SkillExtractor
from src.data.loader import load_skills
from src.data.db_manager import DatabaseManager

st.set_page_config(page_title="Candidate Profile | AI Skill-Gap", page_icon="👤", layout="wide")
apply_custom_css()

st.title("👤 Candidate Skill Profiler & Resume Intelligence")
st.markdown("Extract structured skills, parse experience, and estimate proficiency levels.")
st.divider()

extractor = SkillExtractor()
all_skills_df = load_skills()
all_skill_names = sorted(all_skills_df['skill_name'].unique().tolist())

# Sample Profile presets
st.subheader("📋 Quick Profile Presets")
preset_cols = st.columns(3)

with preset_cols[0]:
    if st.button("🎓 Preset: Data Science Fresher", use_container_width=True):
        st.session_state.candidate_name = "Priya Patel (Fresher)"
        st.session_state.experience_years = 1.0
        st.session_state.education_level = "Bachelor's"
        st.session_state.candidate_skills = {
            "Python": 0.85, "SQL": 0.75, "Pandas & NumPy": 0.80, "Scikit-Learn": 0.70,
            "Exploratory Data Analysis": 0.75, "Probability & Statistics": 0.70, "Git & GitHub": 0.70
        }
        st.rerun()

with preset_cols[1]:
    if st.button("💼 Preset: Mid-Level Data Analyst", use_container_width=True):
        st.session_state.candidate_name = "Rahul Verma (Analyst)"
        st.session_state.experience_years = 3.5
        st.session_state.education_level = "Bachelor's"
        st.session_state.candidate_skills = {
            "SQL": 0.90, "Power BI & DAX": 0.85, "Advanced Excel & VBA": 0.85,
            "Exploratory Data Analysis": 0.80, "Python": 0.70, "Tableau": 0.75,
            "Data Storytelling & KPI Dashboards": 0.80, "Stakeholder Communication": 0.80
        }
        st.rerun()

with preset_cols[2]:
    if st.button("⚙️ Preset: Backend to MLOps Engineer", use_container_width=True):
        st.session_state.candidate_name = "Ananya Sen (DevOps/Backend)"
        st.session_state.experience_years = 4.0
        st.session_state.education_level = "Master's"
        st.session_state.candidate_skills = {
            "Python": 0.85, "Docker & Containerization": 0.85, "Linux & Bash": 0.85,
            "Git & GitHub": 0.90, "RESTful API Design": 0.80, "Kubernetes": 0.70,
            "CI/CD Pipelines (GitHub Actions)": 0.75, "PostgreSQL / MySQL": 0.80
        }
        st.rerun()

st.markdown("<br>", unsafe_allow_html=True)

# Resume Upload & Parser Section
st.subheader("📄 Upload Resume or Paste Profile")
upload_tab, text_tab = st.tabs(["📤 Upload Resume (PDF / Word DOCX)", "✍️ Paste Resume Text"])

with upload_tab:
    uploaded_file = st.file_uploader("Upload candidate resume (PDF or DOCX)", type=["pdf", "docx"])
    if uploaded_file is not None:
        file_bytes = uploaded_file.read()
        with st.spinner("Extracting text and identifying technical competencies..."):
            if uploaded_file.name.endswith(".pdf"):
                raw_text = ResumeParser.extract_text_from_pdf(file_bytes)
            else:
                raw_text = ResumeParser.extract_text_from_docx(file_bytes)
                
            extracted_skills = extractor.extract_skills_with_proficiency(raw_text)
            detected_exp = ResumeParser.extract_experience_years(raw_text)
            detected_edu = ResumeParser.extract_education(raw_text)
            
            st.session_state.experience_years = detected_exp
            st.session_state.education_level = detected_edu
            if extracted_skills:
                st.session_state.candidate_skills = extracted_skills
                st.success(f"Successfully extracted {len(extracted_skills)} technical skills with proficiency estimates!")
            else:
                st.warning("No canonical skills detected. You can add them manually below.")

with text_tab:
    pasted_text = st.text_area("Paste candidate resume text or skill summary:", height=150)
    if st.button("Extract Skills from Text"):
        if pasted_text.strip():
            extracted = extractor.extract_skills_with_proficiency(pasted_text)
            st.session_state.candidate_skills = extracted
            st.session_state.experience_years = ResumeParser.extract_experience_years(pasted_text)
            st.session_state.education_level = ResumeParser.extract_education(pasted_text)
            st.success(f"Extracted {len(extracted)} skills!")
            st.rerun()

st.divider()

# Profile Attributes Editor
st.subheader("⚙️ Candidate Profile Details")
c_name, c_exp, c_edu = st.columns(3)
with c_name:
    cand_name = st.text_input("Candidate Name", value=st.session_state.get("candidate_name", "Alex Sharma"))
    st.session_state.candidate_name = cand_name
with c_exp:
    cand_exp = st.slider("Years of Industry Experience", 0.0, 15.0, float(st.session_state.get("experience_years", 2.0)), 0.5)
    st.session_state.experience_years = cand_exp
with c_edu:
    edu_options = ["Bachelor's", "Master's", "PhD"]
    cur_edu = st.session_state.get("education_level", "Bachelor's")
    idx_edu = edu_options.index(cur_edu) if cur_edu in edu_options else 0
    cand_edu = st.selectbox("Highest Education Level", edu_options, index=idx_edu)
    st.session_state.education_level = cand_edu

st.markdown("<br>", unsafe_allow_html=True)

# Skills & Proficiency Editor
st.subheader(f"🛠️ Active Skill Profile ({len(st.session_state.candidate_skills)} Skills)")
st.info("Adjust the quantitative proficiency slider for each skill (0.1 = Beginner, 0.6 = Working Competency, 1.0 = Expert):")

skills_to_delete = []
curr_skills = dict(st.session_state.candidate_skills)

# Display skills in a 2-column grid
cols = st.columns(2)
for idx, (skill_name, prof) in enumerate(curr_skills.items()):
    col = cols[idx % 2]
    with col:
        sc1, sc2 = st.columns([4, 1])
        with sc1:
            new_val = st.slider(f"**{skill_name}**", 0.1, 1.0, float(prof), 0.05, key=f"prof_{skill_name}")
            st.session_state.candidate_skills[skill_name] = new_val
        with sc2:
            st.markdown("<div style='height: 28px;'></div>", unsafe_allow_html=True)
            if st.button("🗑️", key=f"del_{skill_name}", help=f"Remove {skill_name}"):
                skills_to_delete.append(skill_name)

if skills_to_delete:
    for s in skills_to_delete:
        st.session_state.candidate_skills.pop(s, None)
    st.rerun()

st.markdown("<br>", unsafe_allow_html=True)

# Add New Skill
st.subheader("➕ Add Additional Skill")
add_c1, add_c2 = st.columns([3, 1])
with add_c1:
    remaining_skills = [s for s in all_skill_names if s not in st.session_state.candidate_skills]
    skill_to_add = st.selectbox("Select Skill from Standardized Taxonomy", remaining_skills)
with add_c2:
    st.markdown("<div style='height: 28px;'></div>", unsafe_allow_html=True)
    if st.button("Add Skill to Profile", use_container_width=True):
        if skill_to_add:
            st.session_state.candidate_skills[skill_to_add] = 0.70
            st.rerun()

st.divider()

# Save & Proceed Button
if st.button("🚀 Proceed to Career Role Suitability Matcher", type="primary", use_container_width=True):
    # Save to SQLite history
    db = DatabaseManager()
    db.save_candidate_profile(
        st.session_state.candidate_name,
        st.session_state.experience_years,
        st.session_state.education_level,
        json.dumps(st.session_state.candidate_skills),
        "Pending Evaluation",
        0.0
    )
    st.switch_page("pages/2_Career_Analysis.py")
"""
Path('app/pages/1_Profile.py').write_text(page1_code, encoding='utf-8')

# 2. app/pages/2_Career_Analysis.py
page2_code = """import sys
from pathlib import Path
root_dir = Path(__file__).resolve().parent.parent.parent
if str(root_dir) not in sys.path:
    sys.path.insert(0, str(root_dir))

import streamlit as st
import numpy as np
import pandas as pd
import config
from app.components.ui_helpers import apply_custom_css, render_metric_card
from app.components.charts import create_radar_chart, create_role_ranking_bar
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
"""
Path('app/pages/2_Career_Analysis.py').write_text(page2_code, encoding='utf-8')

# 3. app/pages/3_Skill_Gap.py
page3_code = """import sys
from pathlib import Path
root_dir = Path(__file__).resolve().parent.parent.parent
if str(root_dir) not in sys.path:
    sys.path.insert(0, str(root_dir))

import streamlit as st
import pandas as pd
import config
from app.components.ui_helpers import apply_custom_css, render_metric_card
from src.recommendation.skill_gap import SkillGapEngine
from src.recommendation.skill_priority import SkillPriorityEngine

st.set_page_config(page_title="Skill-Gap Analysis | AI Skill-Gap", page_icon="🔍", layout="wide")
apply_custom_css()

st.title("🔍 Skill-Gap & Multi-Factor Priority Matrix")
st.markdown("Quantify missing competencies and prioritize skill acquisitions based on industry market demand.")
st.divider()

cand_skills = st.session_state.get("candidate_skills", {})
target_role = st.session_state.get("target_role", "Data Scientist")

gap_engine = SkillGapEngine()
priority_engine = SkillPriorityEngine()

analysis = gap_engine.analyze_gaps(cand_skills, target_role)
prioritized_gaps = priority_engine.prioritize_gaps(analysis, cand_skills)
st.session_state.prioritized_gaps = prioritized_gaps

# Top KPI metrics
k1, k2, k3, k4 = st.columns(4)
with k1:
    render_metric_card("Role Match Rate", f"{analysis['match_rate']:.1f}%", f"Target: {target_role}")
with k2:
    render_metric_card("Matched Skills", str(analysis['matched_count']), "Competencies met")
with k3:
    render_metric_card("Partial Skills", str(analysis['partial_count']), "Below required threshold")
with k4:
    render_metric_card("Critical Gaps", str(analysis['missing_count']), "Missing skills to acquire")

st.markdown("<br>", unsafe_allow_html=True)

# Categorized Breakdown
st.subheader("🏷️ Competency Overview")
tab_all, tab_matched, tab_partial, tab_missing = st.tabs([
    f"Priority Matrix ({len(prioritized_gaps)} Gaps)",
    f"✅ Matched ({analysis['matched_count']})",
    f"⚠️ Partial ({analysis['partial_count']})",
    f"❌ Missing ({analysis['missing_count']})"
])

with tab_all:
    st.markdown('''
    **Priority Score Formula**:
    $$Priority = 0.35 \\cdot MarketDemand + 0.30 \\cdot RoleImportance + 0.20 \\cdot Deficiency + 0.15 \\cdot PrereqReadiness$$
    ''')
    
    # Priority Filter
    f_tier = st.multiselect("Filter by Priority Tier", ["High", "Medium", "Low"], default=["High", "Medium", "Low"])
    
    filtered_gaps = [g for g in prioritized_gaps if g['priority_tier'] in f_tier]
    
    if filtered_gaps:
        df_table = pd.DataFrame([{
            'Priority Tier': g['priority_tier'],
            'Priority Score': f"{g['priority_score']:.1f}",
            'Skill Name': g['skill_name'],
            'Domain Category': g['category'],
            'Market Demand': f"{g['demand_pct']}%",
            'Your Proficiency': f"{g['candidate_proficiency']:.2f}",
            'Required Proficiency': f"{g['required_proficiency']:.2f}",
            'Gap': f"{g['gap']:.2f}",
            'Prerequisites': g['prerequisites'] or "None"
        } for g in filtered_gaps])
        st.dataframe(df_table, use_container_width=True, hide_index=True)
    else:
        st.info("No gaps in selected filter.")

with tab_matched:
    if analysis['matched']:
        for m in analysis['matched']:
            st.markdown(f"<span class='badge-matched'>✓ {m['skill_name']}</span> (Proficiency: {m['candidate_proficiency']:.2f} / {m['required_proficiency']:.2f} | Category: {m['category']})", unsafe_allow_html=True)
            st.write("")
    else:
        st.write("No fully matched skills yet.")

with tab_partial:
    if analysis['partial']:
        for p in analysis['partial']:
            st.markdown(f"<span class='badge-partial'>▲ {p['skill_name']}</span> (Current: {p['candidate_proficiency']:.2f} ➔ Target: {p['required_proficiency']:.2f} | Gap: {p['gap']:.2f})", unsafe_allow_html=True)
            st.write("")
    else:
        st.write("No partial skills.")

with tab_missing:
    if analysis['missing']:
        for mis in analysis['missing']:
            st.markdown(f"<span class='badge-missing'>✕ {mis['skill_name']}</span> (Target: {mis['required_proficiency']:.2f} | Market Demand: {mis['demand_pct']}%)", unsafe_allow_html=True)
            st.write("")
    else:
        st.write("No missing skills for this role!")

st.divider()

if st.button("🗺️ Generate Personalized Learning Roadmap for " + target_role, type="primary", use_container_width=True):
    st.switch_page("pages/5_Learning_Path.py")
"""
Path('app/pages/3_Skill_Gap.py').write_text(page3_code, encoding='utf-8')

# 4. app/pages/4_Market_Trends.py
page4_code = """import sys
from pathlib import Path
root_dir = Path(__file__).resolve().parent.parent.parent
if str(root_dir) not in sys.path:
    sys.path.insert(0, str(root_dir))

import streamlit as st
import pandas as pd
import plotly.express as px
import config
from app.components.ui_helpers import apply_custom_css, render_metric_card
from app.components.charts import create_market_demand_chart
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
"""
Path('app/pages/4_Market_Trends.py').write_text(page4_code, encoding='utf-8')
print('Pages 1-4 created successfully!')
