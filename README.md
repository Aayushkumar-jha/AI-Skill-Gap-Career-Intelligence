# AI Skill Gap & Career Intelligence System


---

## Why This Project?

Rapid technological shifts and changing industry demands make it difficult for job seekers and professionals to identify which skills are becoming obsolete and which are critical for career growth. Traditional career guidance often relies on static advice rather than data-backed analysis. This project was developed to bridge the gap between individual career aspirations and actual market demand by transforming raw job market data into actionable, personalized career intelligence.

---

## What This Project Solves

* **Skill Misalignment:** Identifies exact gaps between a user's current skill set and target industry requirements.
* **Lack of Transparency:** Provides clear, explainable insights into why specific skills or roles are recommended, avoiding "black-box" decision-making.
* **Uncertain Career Mobility:** Enables users to simulate hypothetical skill acquisitions and visually assess their potential career progression before investing time in learning.
* **Fragmented Learning:** Recommends targeted learning resources mapped directly to identified skill deficiencies.

---

## Approach

The system follows a multi-stage data processing and intelligence pipeline:

1. **Data Ingestion & Preprocessing:** Cleans and standardizes raw job market datasets, extracting skill keywords and constructing a structured skill taxonomy.
2. **Profile & Gap Analysis:** Compares user-provided skill profiles against target role requirements using dataset-backed taxonomy mapping to highlight missing core and emerging competencies.
3. **Simulation & Explainability Engine:** Runs dynamic scenario simulations ("What-If" analysis) to show how acquiring new skills impacts role compatibility, supported by model explainability metrics.
4. **Interactive Visualization:** Presents actionable insights, market trends, and tailored roadmaps via a multi-page interactive web dashboard.

---

## Tools and Techniques

* **Language & Frameworks:** Python, Streamlit
* **Data Processing & Analytics:** Pandas, NumPy
* **Data Visualization:** Plotly
* **Database & Storage:** SQLite (`career_intelligence.db`)
* **Development & Testing:** `pytest`, Modular Component Architecture

---

## Overview / Insights

The application is structured into a multi-page interface:

* **Profile Setup (`1_Profile.py`):** Captures user expertise, domain, and target roles.
* **Career Analysis (`2_Career_Analysis.py`):** Evaluates overall profile compatibility with selected job roles.
* **Skill Gap Analysis (`3_Skill_Gap.py`):** Pinpoints critical, secondary, and emerging skill shortages.
* **Market Trends (`4_Market_Trends.py`):** Visualizes hiring trends, skill demand, and market shifts.
* **Learning Path (`5_Learning_Path.py`):** Recommends curated learning resources mapped to specific gaps.
* **What-If Simulator (`6_What_If_Simulator.py`):** Simulates career trajectory improvements upon acquiring new skills.
* **Explainability (`7_Explainability.py`):** Offers clear rationale and transparency for system recommendations.

---

## Skills Demonstrated

* **Full-Stack Data Application Development:** Building modular multi-page applications using Streamlit and Python.
* **Data Engineering & Taxonomy Design:** Cleaning raw job datasets and designing structured relational database schemas (`SQLite`).
* **Interactive Data Visualization:** Developing dynamic charts and dashboard components using Plotly.
* **Explainable AI (XAI) Concepts:** Designing transparent recommendation logic and interactive decision-simulation tools.
* **Software Architecture:** Organizing clean directory structures, modular codebases, and component-based UI setups.

---

## How to Use This Project

### 1. Prerequisites

Ensure you have Python 3.10 or higher installed.

### 2. Environment Setup

Clone the repository and set up a virtual environment:

```bash
git clone <repository-url>
cd "Ai skill gap project"

python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

```

### 3. Install Dependencies

```bash
pip install streamlit pandas plotly pytest

```

### 4. Run the Application

Launch the Streamlit web dashboard:

```bash
streamlit run app/Home.py

```

---

## Future Scope

* **Real-time Job Scraper Integration:** Connect live API pipelines (e.g., LinkedIn, Indeed) to auto-update market trends dynamically.
* **Advanced NLP Skill Extraction:** Integrate Transformer-based Named Entity Recognition (NER) models to extract implicit skills directly from uploaded PDF resumes.
* **Gamified Learning Roadmaps:** Add interactive progress tracking and milestone badges for completing recommended learning paths.
* **Collaborative Filtering:** Incorporate peer-matching algorithms to connect users with mentors who have successfully navigated similar career transitions.

---

## Author

**Aspiring Data Scientist| Open to Internships,Oportunities**
