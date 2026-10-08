# AI Skill-Gap & Career Intelligence Engine

An AI-powered career intelligence platform that analyzes a candidate's skills and compares them with job-role requirements to identify suitable career paths, skill gaps, and personalized learning recommendations.

## 🚀 Project Overview

The **AI Skill-Gap & Career Intelligence Engine** helps students and job seekers understand their current career readiness and determine which skills they need to develop for their target role.

The system analyzes candidate profiles, extracts skills from resumes, predicts suitable career roles, identifies missing or underdeveloped skills, prioritizes those skills based on job-market demand, and generates a personalized learning path.

## ✨ Key Features

- **Resume Skill Extraction**  
  Extracts technical skills and candidate information from PDF/DOCX resumes.

- **Career Role Prediction**  
  Predicts and ranks suitable career roles using a Machine Learning model.

- **Skill-Gap Analysis**  
  Compares candidate skills with the required skills for a selected career role.

- **Skill Prioritization**  
  Ranks missing skills based on market demand, role importance, skill deficiency, and prerequisites.

- **Personalized Learning Path**  
  Generates a structured learning roadmap based on skill prerequisites and difficulty.

- **Job Market Analytics**  
  Provides insights into job roles, skill demand, salary ranges, experience requirements, and hiring trends.

- **What-If Career Simulator**  
  Allows users to add hypothetical skills and analyze how those skills could improve their career suitability.

- **Explainable AI**  
  Shows the major factors contributing to the predicted career-role suitability.

## 🔄 System Workflow

```text
Candidate Resume / Profile
          ↓
Resume Parsing & Skill Extraction
          ↓
Candidate Skill Profile
          ↓
Feature Engineering
          ↓
Career Role Prediction
          ↓
Skill-Gap Analysis
          ↓
Skill Priority Ranking
          ↓
Personalized Learning Path
          ↓
What-If Simulation & Explainability
```

## 🧠 Machine Learning

The project uses a **Random Forest Classifier** to predict candidate suitability across multiple technology roles.

Supported roles include:

- Data Scientist
- Machine Learning Engineer
- Data Analyst
- Data Engineer
- BI Developer
- MLOps Engineer
- AI Research Scientist
- Backend Software Engineer
- NLP Engineer
- Computer Vision Engineer
- Cloud Data Architect
- Business Analyst

The model uses candidate experience, education, skill proficiency, skill categories, and role-specific skill compatibility as features.

## 📊 Skill-Gap Analysis

For a selected target role, the system categorizes skills into:

| Category | Description |
|---|---|
| ✅ Matched | Required skill is sufficiently developed |
| ⚠️ Partial | Candidate has the skill but needs improvement |
| ❌ Missing | Required skill is not present |

The system then calculates a priority score for each skill to determine what the candidate should learn first.

## 🗺️ Personalized Learning Path

The learning engine creates a structured roadmap using:

- Skill prerequisites
- Skill difficulty
- Candidate's existing skills
- Skill priority
- Recommended learning resources

Example:

```text
Python
   ↓
Machine Learning
   ↓
Deep Learning
   ↓
Transformers
   ↓
LLMs
   ↓
RAG
```

## 📈 Job Market Analytics

The platform analyzes job-market data to provide:

- Job demand by role
- Skill demand
- Salary analysis
- Experience requirements
- Company distribution
- Location-based job trends

## 🔮 What-If Career Simulator

Users can select skills they plan to learn and simulate their future career profile.

```text
Current Skills
      ↓
Add Hypothetical Skills
      ↓
Recalculate Profile
      ↓
Compare Career Suitability
```

This helps users understand which skills can have the greatest impact on their target career.

## 🛠️ Tech Stack

- **Python**
- **Pandas**
- **NumPy**
- **Scikit-Learn**
- **NLP / Regex**
- **SQLite**
- **Plotly**
- **Streamlit**
- **Pytest**
- **Jupyter Notebook**

## 📁 Project Structure

```text
Ai Skill Gap Project/
│
├── app/
│   ├── app.py
│   ├── Home.py
│   └── pages/
│
├── data/
│   ├── raw/
│   └── processed/
│
├── database/
│
├── models/
│
├── src/
│   ├── data/
│   ├── nlp/
│   ├── features/
│   ├── models/
│   ├── recommendation/
│   └── explainability/
│
├── notebooks/
├── scripts/
├── tests/
├── config.py
├── requirements.txt
└── README.md
```

## ▶️ Run the Project

Install the required dependencies:

```bash
pip install -r requirements.txt
```

Run the Streamlit application:

```bash
streamlit run app/app.py
```

The application provides an interactive interface for **career analysis, skill-gap identification, market analytics, learning-path generation, What-If simulation, and explainable predictions**.

## Author

**Aspiring Data Scientist| Open to Internships,Opportunities**
