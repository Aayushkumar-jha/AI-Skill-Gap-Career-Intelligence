# AI Skill-Gap & Career Intelligence Engine
> **An ML-Driven Career Decision-Support & Employability Acceleration Platform**  
> *Developed for Smart India Hackathon (SIH) & B.Tech Capstone Project Excellence*

[![Python](https://img.shields.io/badge/Python-3.10%2B-blue.svg)](https://www.python.org/)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.30%2B-FF4B4B.svg)](https://streamlit.io/)
[![Scikit-Learn](https://img.shields.io/badge/Scikit--Learn-1.3%2B-F7931E.svg)](https://scikit-learn.org/)
[![Database](https://img.shields.io/badge/SQLite-Indexed-003B57.svg)](https://www.sqlite.org/)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

---

## 📌 Executive Summary
Technology stacks and hiring bars shift at an unprecedented pace. Candidates and fresh graduates frequently struggle to answer three critical questions:
1. *Which career role truly aligns with my current skills?*
2. *What is my quantitative skill deficiency against industry benchmarks?*
3. *Which missing skill must I prioritize learning first to maximize my hiring potential?*

The **AI Skill-Gap & Career Intelligence Engine** solves this problem using an end-to-end Data Science and Machine Learning methodology. Unlike generic job boards that rely on superficial keyword matching or black-box LLMs, this system processes **12,000+ job market postings**, extracts skills with **quantitative proficiency scoring (0.1–1.0)**, classifies role suitability with **98.9% test accuracy**, computes **market-weighted skill gap priorities**, sequences **prerequisite-aware DAG roadmaps**, provides **Explainable AI (SHAP)** score attribution, and features a signature **What-If Career Simulator**.

---

## 🌟 Key Features

| Feature | Description |
| :--- | :--- |
| **Resume Intelligence** | Multi-format resume extraction (PDF, Word DOCX, text) capturing experience duration, education, and technical skills. |
| **Contextual Proficiency Scoring** | Evaluates skills on a continuous 0.1 to 1.0 confidence scale based on frequency, seniority markers, and project context. |
| **Supervised Role Classification** | 120-tree Random Forest ensemble predicting suitability across 12 tech roles with 98.89% holdout accuracy. |
| **Multi-Factor Skill Priority Engine** | Ranks missing competencies using: $\text{Priority} = 0.35 \cdot \text{Demand} + 0.30 \cdot \text{Importance} + 0.20 \cdot \text{Deficiency} + 0.15 \cdot \text{PrereqReadiness}$. |
| **Prerequisite-Aware DAG Roadmap** | Topological graph sort preventing advanced topics from being scheduled before foundational prerequisites. |
| **What-If Career Simulator** | Interactive sandbox allowing candidates to simulate the employability gains of acquiring hypothetical skills before learning them. |
| **Explainable AI (XAI)** | Transparent attribution highlighting positive drivers boosting match scores and missing gap penalties pulling scores down. |
| **Market Intelligence Dashboard** | Visual analytics on 12,000+ postings: salary boxplots (LPA), top hiring tech firms, and regional demand maps. |

---

## 🏗️ System Architecture

```
                               ┌───────────────────────────┐
                               │  Candidate Resume / Text  │
                               └─────────────┬─────────────┘
                                             │
                                             ▼
                               ┌───────────────────────────┐
                               │   NLP Extraction Layer    │
                               │  (Aliases, N-grams, Prof) │
                               └─────────────┬─────────────┘
                                             │
                     ┌───────────────────────┴───────────────────────┐
                     ▼                                               ▼
         ┌───────────────────────┐                       ┌───────────────────────┐
         │  Job Market Knowledge │                       │    Skill Taxonomy     │
         │ (12k Jobs, SQLite DB) │                       │  (75 Skills, DAG Map) │
         └───────────┬───────────┘                       └───────────┬───────────┘
                     │                                               │
                     └───────────────────────┬───────────────────────┘
                                             │
                                             ▼
                               ┌───────────────────────────┐
                               │    Feature Engineering    │
                               │   (Coverage, Exp, Cat)    │
                               └─────────────┬─────────────┘
                                             │
                ┌────────────────────────────┼────────────────────────────┐
                ▼                            ▼                            ▼
   ┌──────────────────────────┐ ┌──────────────────────────┐ ┌──────────────────────────┐
   │  ML Role Classification  │ │   Skill-Gap & Priority   │ │   What-If Career Sim   │
   │  (Random Forest 98.9%)   │ │    Multi-Factor Engine   │ │   (Hypothetical Delta) │
   └────────────┬─────────────┘ └────────────┬─────────────┘ └────────────┬─────────────┘
                │                            │                            │
                ▼                            ▼                            ▼
   ┌──────────────────────────┐ ┌──────────────────────────┐ ┌──────────────────────────┐
   │   Explainable AI (XAI)   │ │  Topological Learning    │ │   Dynamic Comparative  │
   │   (Positive / Negative)  │ │      Roadmap DAG         │ │    Score Trajectory    │
   └────────────┬─────────────┘ └────────────┬─────────────┘ └────────────┬─────────────┘
                │                            │                            │
                └────────────────────────────┼────────────────────────────┘
                                             │
                                             ▼
                               ┌───────────────────────────┐
                               │ 8-Page Streamlit Web App  │
                               └───────────────────────────┘
```

---

## 📂 Project Directory Structure

```text
Ai skill gap project/
├── config.py                       # Central configurations, role lists, weights
├── requirements.txt                # Python package dependencies
├── README.md                       # Comprehensive documentation
├── LICENSE                         # MIT License
├── data/
│   ├── raw/                        # skills.csv, job_postings.csv, learning_resources.csv
│   └── processed/                  # cleaned_jobs.csv, job_skills.csv, skill_taxonomy.csv
├── database/
│   └── career_intelligence.db      # 25MB SQLite relational database with indexes
├── src/
│   ├── data/                       # loader.py, db_manager.py
│   ├── nlp/                        # text_cleaner.py, resume_parser.py, skill_extractor.py
│   ├── features/                   # feature_engineering.py
│   ├── models/                     # role_classifier.py
│   ├── recommendation/             # skill_gap.py, skill_priority.py, learning_path.py
│   ├── explainability/             # shap_analysis.py
│   └── evaluation/                 # metrics.py
├── models/
│   ├── role_model.pkl              # Serialized 120-tree Random Forest weights
│   ├── scaler.pkl                  # Fitted StandardScaler
│   └── model_metadata.json         # Training metrics and feature column names
├── app/
│   ├── app.py                      # Streamlit entry point
│   ├── components/                 # charts.py, ui_helpers.py
│   └── pages/
│       ├── 1_Profile.py            # Resume parser & skill proficiency editor
│       ├── 2_Career_Analysis.py    # Role suitability predictions & radar charts
│       ├── 3_Skill_Gap.py          # Matched, partial, missing priority matrix
│       ├── 4_Market_Trends.py      # Demand frequency & salary LPA distributions
│       ├── 5_Learning_Path.py      # Topological DAG personalized roadmap
│       ├── 6_What_If_Simulator.py  # Interactive hypothetical skill sandbox
│       ├── 7_Explainability.py     # Explainable AI (XAI) feature impact drivers
│       └── 8_Model_Evaluation.py   # Confusion matrices & benchmark reports
├── notebooks/
│   ├── 01_data_cleaning_eda.ipynb  # Phase 3 EDA & cleaning
│   ├── 02_nlp_skill_extraction.ipynb# Phase 4 NLP pipeline demonstration
│   └── 03_model_training_evaluation.ipynb # Phase 8 & 11 ML & XAI
├── tests/
│   ├── test_nlp.py                 # Resume parsing and alias tests
│   ├── test_models.py              # Feature vectors and inference tests
│   └── test_recommendation.py      # Gap ranking and DAG roadmap tests
└── scripts/
    ├── generate_full_market_and_resources.py # Dataset synthesis
    └── train_pipeline.py           # Model training and artifact serialization
```

---

## 🚀 Quick Start Guide

### 1. Prerequisites & Installation
Ensure Python 3.10+ is installed on your system. Clone or open the project folder and install dependencies:
```bash
pip install -r requirements.txt
```

### 2. Run Automated Test Suite
Verify that all 9 unit and integration tests pass cleanly:
```bash
pytest tests/
```

### 3. Launch the Interactive Streamlit Web Application
Run the multi-page dashboard:
```bash
streamlit run app/app.py
```
Open your browser at `http://localhost:8501`.

---

## 🎯 Target Roles Covered
The engine is calibrated across 12 high-demand industry profiles:
1. **Data Scientist**
2. **Machine Learning Engineer**
3. **Data Analyst**
4. **Data Engineer**
5. **BI Developer**
6. **MLOps Engineer**
7. **AI Research Scientist**
8. **Backend Software Engineer**
9. **NLP Engineer**
10. **Computer Vision Engineer**
11. **Cloud Data Architect**
12. **Business Analyst**

---

## 📄 Resume Positioning & B.Tech Capstone Summary
**Project Title**: *AI Skill-Gap & Career Intelligence Engine*  
**Description**: *Designed and engineered an explainable ML-based career intelligence platform that analyzes 12,000+ job postings and candidate resumes to predict career role suitability, quantify skill deficiencies, prioritize high-impact gaps using market demand, and generate prerequisite-aware personalized learning pathways using NLP, Random Forest (98.9% accuracy), and SHAP-based explainability.*
