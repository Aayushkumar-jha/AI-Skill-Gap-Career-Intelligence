import sys
from pathlib import Path
root_dir = Path(__file__).resolve().parent.parent
app_dir = Path(__file__).resolve().parent
if str(root_dir) not in sys.path:
    sys.path.insert(0, str(root_dir))
if str(app_dir) not in sys.path:
    sys.path.insert(0, str(app_dir))

import streamlit as st
import json
import config
from components.ui_helpers import apply_custom_css, render_metric_card
from src.nlp.resume_parser import ResumeParser
from src.nlp.skill_extractor import SkillExtractor
from src.data.loader import load_skills
from src.data.db_manager import DatabaseManager

st.set_page_config(page_title="Candidate Profile | AI Skill-Gap", page_icon="👤", layout="wide")
apply_custom_css()

st.title("👤 Candidate Skill Profiler & Resume Intelligence")
st.markdown("Extract structured skills, auto-detect candidate details, parse experience, and estimate proficiency levels.")
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
        st.session_state.uploaded_file_info = {
            "filename": "priya_patel_ds_resume.pdf",
            "file_size_kb": 128.4,
            "file_type": "PDF Document",
            "unit_count": 2,
            "unit_label": "Pages",
            "word_count": 340,
            "char_count": 2180
        }
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
        st.session_state.uploaded_file_info = {
            "filename": "rahul_verma_data_analyst.docx",
            "file_size_kb": 95.2,
            "file_type": "Microsoft Word (.docx)",
            "unit_count": 18,
            "unit_label": "Paragraphs",
            "word_count": 480,
            "char_count": 3120
        }
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
        st.session_state.uploaded_file_info = {
            "filename": "ananya_sen_mlops_cv.pdf",
            "file_size_kb": 184.0,
            "file_type": "PDF Document",
            "unit_count": 2,
            "unit_label": "Pages",
            "word_count": 520,
            "char_count": 3450
        }
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
        with st.spinner("Analyzing document structure, extracting candidate info, and identifying competencies..."):
            if uploaded_file.name.endswith(".pdf"):
                raw_text = ResumeParser.extract_text_from_pdf(file_bytes)
            else:
                raw_text = ResumeParser.extract_text_from_docx(file_bytes)
                
            extracted_skills = extractor.extract_skills_with_proficiency(raw_text)
            detected_name = ResumeParser.extract_candidate_name(raw_text, uploaded_file.name)
            detected_exp = ResumeParser.extract_experience_years(raw_text)
            detected_edu = ResumeParser.extract_education(raw_text)
            file_meta = ResumeParser.get_file_metadata(file_bytes, uploaded_file.name, raw_text)
            
            # Automatically update candidate profile
            st.session_state.candidate_name = detected_name
            st.session_state.experience_years = detected_exp
            st.session_state.education_level = detected_edu
            st.session_state.uploaded_file_info = file_meta
            
            if extracted_skills:
                st.session_state.candidate_skills = extracted_skills
                st.success(f"✓ Parsed resume for **{detected_name}**! Extracted {len(extracted_skills)} technical skills.")
            else:
                st.warning(f"Extracted info for **{detected_name}**, but no standardized technical skills were detected.")

with text_tab:
    pasted_text = st.text_area("Paste candidate resume text or skill summary:", height=150)
    if st.button("Extract Info & Skills from Text"):
        if pasted_text.strip():
            extracted = extractor.extract_skills_with_proficiency(pasted_text)
            detected_name = ResumeParser.extract_candidate_name(pasted_text, "pasted_text.txt")
            st.session_state.candidate_name = detected_name
            st.session_state.candidate_skills = extracted
            st.session_state.experience_years = ResumeParser.extract_experience_years(pasted_text)
            st.session_state.education_level = ResumeParser.extract_education(pasted_text)
            st.session_state.uploaded_file_info = {
                "filename": "Pasted Resume Text",
                "file_size_kb": round(len(pasted_text.encode('utf-8')) / 1024.0, 1),
                "file_type": "Direct Text Input",
                "unit_count": len(pasted_text.splitlines()),
                "unit_label": "Lines",
                "word_count": len(pasted_text.split()),
                "char_count": len(pasted_text)
            }
            st.success(f"Extracted profile for **{detected_name}** ({len(extracted)} skills)!")
            st.rerun()

# Display Uploaded File & Candidate Meta Info Card if available
if "uploaded_file_info" in st.session_state and st.session_state.uploaded_file_info:
    f_info = st.session_state.uploaded_file_info
    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown(f'''
    <div style="background: linear-gradient(135deg, #1e293b 0%, #0f172a 100%); border: 1px solid #38bdf8; border-radius: 12px; padding: 18px 24px; margin-bottom: 20px;">
        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 10px;">
            <span style="font-size: 1.1rem; font-weight: 700; color: #38bdf8;">📁 Uploaded File & Candidate Details</span>
            <span class="badge-matched">✓ Parsed Successfully</span>
        </div>
        <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(180px, 1fr)); gap: 12px; margin-top: 10px; color: #e2e8f0; font-size: 0.9rem;">
            <div><strong>👤 Candidate Name:</strong> <span style="color: #6ee7b7; font-weight: 600;">{st.session_state.candidate_name}</span></div>
            <div><strong>📄 File Name:</strong> {f_info.get('filename', 'N/A')}</div>
            <div><strong>📋 Format:</strong> {f_info.get('file_type', 'N/A')}</div>
            <div><strong>⚖️ Size:</strong> {f_info.get('file_size_kb', 0)} KB</div>
            <div><strong>📑 Document Length:</strong> {f_info.get('unit_count', 0)} {f_info.get('unit_label', 'Units')}</div>
            <div><strong>📝 Words / Characters:</strong> {f_info.get('word_count', 0):,} words ({f_info.get('char_count', 0):,} chars)</div>
        </div>
    </div>
    ''', unsafe_allow_html=True)

st.divider()

# Profile Attributes Editor
st.subheader("⚙️ Candidate Profile Details")
c_name, c_exp, c_edu = st.columns(3)
with c_name:
    cand_name = st.text_input("Candidate Name (Auto-updated from Resume)", value=st.session_state.get("candidate_name", "Alex Sharma"))
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
st.info("Adjust the quantitative proficiency slider for each skill (0.10 = Beginner, 0.60 = Working Competency, 1.00 = Expert):")

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
