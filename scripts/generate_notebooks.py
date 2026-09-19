import json
from pathlib import Path

def make_notebook(cells):
    return {
        "cells": cells,
        "metadata": {
            "language_info": {"name": "python"},
            "orig_nbformat": 4
        },
        "nbformat": 4,
        "nbformat_minor": 2
    }

def md_cell(source):
    return {
        "cell_type": "markdown",
        "metadata": {},
        "source": source if isinstance(source, list) else [source]
    }

def code_cell(source):
    return {
        "cell_type": "code",
        "execution_count": None,
        "metadata": {},
        "outputs": [],
        "source": source if isinstance(source, list) else [source]
    }

# 1. 01_data_cleaning_eda.ipynb
nb1_cells = [
    md_cell("# Phase 3: Data Cleaning & Exploratory Data Analysis (EDA)\n## AI Skill-Gap & Career Intelligence Engine\n\nThis notebook demonstrates data acquisition, cleaning, deduplication, and market demand analytics across 12,000+ job postings."),
    code_cell("import sqlite3\nimport pandas as pd\nimport numpy as np\nimport matplotlib.pyplot as plt\nimport seaborn as sns\nimport config\n\nconn = sqlite3.connect(config.DB_PATH)\ndf_jobs = pd.read_sql_query('SELECT * FROM jobs', conn)\ndf_skills = pd.read_sql_query('SELECT * FROM skills', conn)\nconn.close()\n\nprint(f'Loaded {len(df_jobs)} jobs and {len(df_skills)} standardized skills.')\ndf_jobs.head(3)"),
    md_cell("### 1. Missing Value and Cleanliness Audit"),
    code_cell("print('Missing values in Job Postings:')\nprint(df_jobs.isnull().sum())\n\nprint('\\nJob Distribution across 12 Target Roles:')\nprint(df_jobs['role_category'].value_counts())"),
    md_cell("### 2. Salary Distribution Across Roles & Experience Tiers"),
    code_cell("plt.figure(figsize=(12, 6))\nsns.boxplot(data=df_jobs, x='role_category', y='salary_lpa', hue='experience_tier')\nplt.xticks(rotation=45, ha='right')\nplt.title('Industry Compensation Distribution (LPA) by Role & Seniority')\nplt.ylabel('Salary (INR LPA)')\nplt.tight_layout()\nplt.show()"),
    md_cell("### 3. Top Most Demanded Skills in Job Market"),
    code_cell("from src.data.loader import get_market_skill_demand\ndf_demand = get_market_skill_demand()\n\nplt.figure(figsize=(10, 6))\nsns.barplot(data=df_demand.head(15), y='skill_name', x='demand_count', palette='viridis')\nplt.title('Top 15 Most Demanded Technical Skills Across All 12 Roles')\nplt.xlabel('Number of Job Postings Requiring Skill')\nplt.ylabel('Skill Name')\nplt.show()")
]
Path('notebooks/01_data_cleaning_eda.ipynb').write_text(json.dumps(make_notebook(nb1_cells), indent=2), encoding='utf-8')

# 2. 02_nlp_skill_extraction.ipynb
nb2_cells = [
    md_cell("# Phase 4: NLP Skill Extraction & Candidate Profiling\n## AI Skill-Gap & Career Intelligence Engine\n\nDemonstration of multi-tier NLP parsing: canonical alias matching, regex boundary chunking, and contextual proficiency estimation."),
    code_cell("from src.nlp.skill_extractor import SkillExtractor\nfrom src.nlp.resume_parser import ResumeParser\n\nextractor = SkillExtractor()\n\nsample_resume = '''\nSenior Machine Learning Engineer with 4 years experience.\nExpert in Python, PyTorch, Scikit-Learn, and Docker.\nBuilt and deployed LLM solutions using Transformers, LangChain (RAG), and FastAPI.\nExperienced in SQL and PostgreSQL query tuning.\n'''\n\nextracted_skills = extractor.extract_skills_with_proficiency(sample_resume)\nexp_years = ResumeParser.extract_experience_years(sample_resume)\nedu = ResumeParser.extract_education(sample_resume)\n\nprint(f'Detected Experience: {exp_years} Years')\nprint(f'Detected Education: {edu}')\nprint(f'Extracted {len(extracted_skills)} Skills with Proficiency Confidence:')\nfor s, p in sorted(extracted_skills.items(), key=lambda x: x[1], reverse=True):\n    print(f'  - {s:35s}: {p:.2f}')")
]
Path('notebooks/02_nlp_skill_extraction.ipynb').write_text(json.dumps(make_notebook(nb2_cells), indent=2), encoding='utf-8')

# 3. 03_model_training_evaluation.ipynb
nb3_cells = [
    md_cell("# Phase 8 & 11: Role Classification, Explainability & What-If Simulation\n## AI Skill-Gap & Career Intelligence Engine\n\nCovers feature vector transformation, Random Forest model inference, explainable AI (XAI) feature attribution, and What-If simulation."),
    code_cell("from src.features.feature_engineering import FeatureEngineer\nfrom src.models.role_classifier import RoleClassifier\nfrom src.explainability.shap_analysis import ExplainabilityEngine\n\nfe = FeatureEngineer()\nclf = RoleClassifier()\nexplainer = ExplainabilityEngine(clf, fe.get_feature_names())\n\ncand_skills = {\n    'Python': 0.90, 'SQL': 0.85, 'Pandas & NumPy': 0.85, 'Scikit-Learn': 0.80,\n    'Exploratory Data Analysis': 0.80, 'Probability & Statistics': 0.75\n}\n\nfeat_vec = fe.candidate_to_feature_vector(cand_skills, 2.0, \"Bachelor's\")\npred_df = clf.predict_roles(feat_vec)\nprint('Role Suitability Predictions:')\nprint(pred_df.head(5).to_string(index=False))"),
    md_cell("### SHAP Feature Attribution (Explainable AI)"),
    code_cell("explanation = explainer.explain_candidate_prediction(feat_vec, 'Data Scientist')\nprint('\\nTop Positive Factors Boosting Score:')\nfor pos in explanation['positive_drivers']:\n    print(f\"  + {pos['feature']}: {pos['contribution']:+.3f}\")\n\nprint('\\nTop Missing Gap Penalties:')\nfor neg in explanation['negative_penalties']:\n    print(f\"  - {neg['feature']}: {neg['contribution']:+.3f}\")")
]
Path('notebooks/03_model_training_evaluation.ipynb').write_text(json.dumps(make_notebook(nb3_cells), indent=2), encoding='utf-8')

print("3 Jupyter Notebooks generated in notebooks/ directory!")
