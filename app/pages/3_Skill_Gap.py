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
import config
from components.ui_helpers import apply_custom_css, render_metric_card
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
    st.markdown(r'''
    **Priority Score Formula**:
    $$Priority = 0.35 \cdot MarketDemand + 0.30 \cdot RoleImportance + 0.20 \cdot Deficiency + 0.15 \cdot PrereqReadiness$$
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