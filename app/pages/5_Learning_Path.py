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
from src.recommendation.skill_gap import SkillGapEngine
from src.recommendation.skill_priority import SkillPriorityEngine
from src.recommendation.learning_path import LearningPathEngine

st.set_page_config(page_title="Learning Roadmap | AI Skill-Gap", page_icon="🗺️", layout="wide")
apply_custom_css()

st.title("🗺️ Prerequisite-Aware Personalized Learning Roadmap")
st.markdown("Topological DAG-sequenced curriculum ensuring foundational mastery before advanced specializations.")
st.divider()

cand_skills = st.session_state.get("candidate_skills", {})
target_role = st.session_state.get("target_role", "Data Scientist")

gap_engine = SkillGapEngine()
priority_engine = SkillPriorityEngine()
lp_engine = LearningPathEngine()

analysis = gap_engine.analyze_gaps(cand_skills, target_role)
prioritized_gaps = priority_engine.prioritize_gaps(analysis, cand_skills)
roadmap = lp_engine.build_personalized_roadmap(prioritized_gaps, cand_skills)

total_weeks = sum(item['duration_weeks'] for item in roadmap) if roadmap else 0

# Summary Metrics
c1, c2, c3, c4 = st.columns(4)
with c1:
    render_metric_card("Target Role", target_role, "Target career objective")
with c2:
    render_metric_card("Roadmap Modules", str(len(roadmap)), "Sequenced learning milestones")
with c3:
    render_metric_card("Estimated Timeline", f"{total_weeks} Weeks", "At 10-15 hrs/week study")
with c4:
    render_metric_card("Curated Resources", str(sum(len(r['resources']) for r in roadmap)), "Free & verified learning guides")

st.markdown("<br>", unsafe_allow_html=True)

# Phase-Wise Roadmap Display
if not roadmap:
    st.success("🎉 Outstanding! You already possess all recommended competencies for this target role!")
else:
    # Group by phase
    phases = {}
    for item in roadmap:
        p = item['phase']
        if p not in phases:
            phases[p] = []
        phases[p].append(item)
        
    for phase_name, items in phases.items():
        st.subheader(f"📌 {phase_name}")
        for step in items:
            with st.expander(f"**Step {step['order']}: {step['skill_name']}** (Weeks {step['start_week']}–{step['end_week']} | {step['difficulty']})", expanded=True):
                st.markdown(f"**Skill Category Focus**: {step['skill_name']} | **Difficulty Level**: `{step['difficulty']}`")
                st.markdown("##### 📚 Recommended Verified Learning Resources:")
                
                if step['resources']:
                    for res in step['resources']:
                        r_c1, r_c2 = st.columns([3, 1])
                        with r_c1:
                            st.markdown(f"- **[{res['title']}]({res['url']})**")
                            st.caption(f"Platform: *{res['platform']}* | Format: *{res['resource_type']}* | Est. Duration: *{res['duration_hours']} hours*")
                        with r_c2:
                            st.link_button("Access Resource ↗", res['url'])
                else:
                    st.info("Interactive projects and documentation available in resource library.")
        st.markdown("<br>", unsafe_allow_html=True)

st.divider()
if st.button("🔮 Test Impact of These Skills in the What-If Career Simulator", type="primary", use_container_width=True):
    st.switch_page("pages/6_What_If_Simulator.py")