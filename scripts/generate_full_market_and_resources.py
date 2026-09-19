import os
import random
import sqlite3
import pandas as pd
import numpy as np
from pathlib import Path
from datetime import datetime, timedelta

random.seed(42)
np.random.seed(42)

base_dir = Path('.')
data_raw = base_dir / 'data' / 'raw'
data_proc = base_dir / 'data' / 'processed'
db_dir = base_dir / 'database'
db_path = db_dir / 'career_intelligence.db'

for d in [data_raw, data_proc, db_dir]:
    d.mkdir(parents=True, exist_ok=True)

df_skills = pd.read_csv(data_raw / 'skills.csv')
skills_dict = dict(zip(df_skills['skill_id'], df_skills['skill_name']))
name_to_id = dict(zip(df_skills['skill_name'], df_skills['skill_id']))

# 1. GENERATE LEARNING RESOURCES
resources = []
rid = 1

resource_templates = {
    'Python': [
        ('Python for Everybody Specialization', 'Coursera', 'Specialization', 'Beginner', 40, 'https://www.coursera.org/specializations/python', ''),
        ('Complete Python Bootcamp from Zero to Hero', 'Udemy', 'Course', 'Beginner', 22, 'https://www.udemy.com/course/complete-python-bootcamp/', ''),
        ('Official Python 3 Documentation & Tutorial', 'Official Docs', 'Documentation', 'Intermediate', 15, 'https://docs.python.org/3/tutorial/', '')
    ],
    'SQL': [
        ('SQL for Data Science', 'Coursera', 'Course', 'Beginner', 20, 'https://www.coursera.org/learn/sql-for-data-science', ''),
        ('Mode Analytics SQL Tutorial for Beginners & Advanced', 'Interactive Tutorial', 'Interactive Tutorial', 'Beginner', 12, 'https://mode.com/sql-tutorial/', ''),
        ('PostgreSQL High Performance & Indexing Guide', 'Official Docs', 'Documentation', 'Advanced', 15, 'https://www.postgresql.org/docs/', 'SQL')
    ],
    'Pandas & NumPy': [
        ('Data Analysis with Python (Pandas & NumPy)', 'freeCodeCamp', 'Course', 'Beginner', 10, 'https://freecodecamp.org', 'Python'),
        ('Python for Data Analysis by Wes McKinney', 'O Reilly Book', 'Book', 'Intermediate', 30, 'https://wesmckinney.com/book/', 'Python')
    ],
    'Scikit-Learn': [
        ('Machine Learning Specialization by Andrew Ng', 'Coursera', 'Specialization', 'Intermediate', 60, 'https://www.coursera.org/specializations/machine-learning-introduction', 'Python,Linear Algebra'),
        ('Hands-On Machine Learning with Scikit-Learn, Keras & TF (A. Geron)', 'O Reilly Book', 'Book', 'Intermediate', 45, 'https://www.oreilly.com', 'Pandas & NumPy'),
        ('Scikit-Learn Official User Guide & API Reference', 'Official Docs', 'Documentation', 'Intermediate', 20, 'https://scikit-learn.org', 'Python')
    ],
    'PyTorch': [
        ('Deep Learning with PyTorch: Zero to GANs', 'freeCodeCamp', 'Course', 'Intermediate', 18, 'https://jovian.ai', 'Python,Linear Algebra'),
        ('Deep Learning Specialization (DeepLearning.AI)', 'Coursera', 'Specialization', 'Intermediate', 75, 'https://deeplearning.ai', 'Linear Algebra,Multivariate Calculus'),
        ('Official PyTorch Tutorials & Recipes', 'Official Docs', 'Documentation', 'Intermediate', 15, 'https://pytorch.org/tutorials/', 'Python')
    ],
    'Transformers & Attention Mechanisms': [
        ('Hugging Face NLP Course (Transformers, Tokenizers, Datasets)', 'Hugging Face Ecosystem', 'Course', 'Intermediate', 30, 'https://huggingface.co/learn/nlp-course', 'PyTorch'),
        ('Stanford CS224N: Natural Language Processing with Deep Learning', 'YouTube', 'Course', 'Advanced', 40, 'https://web.stanford.edu/class/cs224n/', 'PyTorch')
    ],
    'Large Language Models (LLMs)': [
        ('Generative AI with Large Language Models (AWS & DeepLearning.AI)', 'Coursera', 'Course', 'Advanced', 25, 'https://deeplearning.ai', 'Transformers & Attention Mechanisms'),
        ('Full Stack LLM Bootcamp', 'YouTube', 'Guided Project', 'Advanced', 20, 'https://fullstackdeeplearning.com', 'Python,Transformers & Attention Mechanisms')
    ],
    'Retrieval-Augmented Generation (RAG)': [
        ('Building RAG Applications with LangChain & LlamaIndex', 'DeepLearning.AI', 'Course', 'Advanced', 12, 'https://deeplearning.ai', 'Large Language Models (LLMs)'),
        ('Pinecone Vector Mastery & RAG Architecture', 'Official Docs', 'Interactive Tutorial', 'Intermediate', 8, 'https://www.pinecone.io/learn/', 'Python')
    ],
    'Apache Spark / PySpark': [
        ('Spark and Python for Big Data with PySpark', 'Udemy', 'Course', 'Intermediate', 15, 'https://www.udemy.com', 'Python,SQL'),
        ('Learning Spark: Lightning-Fast Data Analytics (2nd Ed)', 'O Reilly Book', 'Book', 'Advanced', 25, 'https://www.oreilly.com', 'Python')
    ],
    'Apache Airflow': [
        ('Data Engineering with Apache Airflow', 'Coursera', 'Course', 'Intermediate', 16, 'https://coursera.org', 'Python,ETL / ELT Pipelines'),
        ('Official Apache Airflow Fundamentals & Operators Guide', 'Official Docs', 'Documentation', 'Intermediate', 10, 'https://airflow.apache.org', 'Python')
    ],
    'Docker & Containerization': [
        ('Docker Mastery: with Kubernetes +Swarm from a Docker Captain', 'Udemy', 'Course', 'Intermediate', 21, 'https://www.udemy.com', 'Linux & Bash'),
        ('Docker Official Get-Started Workshop', 'Official Docs', 'Interactive Tutorial', 'Beginner', 6, 'https://docs.docker.com/get-started/', '')
    ],
    'Kubernetes': [
        ('Certified Kubernetes Administrator (CKA) with Practice Tests', 'Udemy', 'Course', 'Advanced', 22, 'https://www.udemy.com', 'Docker & Containerization'),
        ('Kubernetes Up & Running (K. Hightower)', 'O Reilly Book', 'Book', 'Advanced', 18, 'https://www.oreilly.com', 'Docker & Containerization')
    ],
    'MLflow & Experiment Tracking': [
        ('MLOps Bootcamp: Hands-on MLflow, DVC, and Deployment', 'Udemy', 'Course', 'Intermediate', 14, 'https://www.udemy.com', 'Scikit-Learn,Docker & Containerization'),
        ('Official MLflow Quickstart & Registry Docs', 'Official Docs', 'Documentation', 'Intermediate', 6, 'https://mlflow.org/docs/latest/', 'Python')
    ],
    'Power BI & DAX': [
        ('Microsoft Power BI Desktop for Business Intelligence', 'Udemy', 'Course', 'Beginner', 18, 'https://www.udemy.com', 'SQL'),
        ('DAX Formulas for Power BI Tutorial (SQLBI Marco Russo)', 'YouTube', 'Tutorial', 'Intermediate', 12, 'https://www.sqlbi.com', 'Power BI & DAX')
    ],
    'Tableau': [
        ('Tableau 2024 A-Z: Hands-On Tableau Training For Data Science', 'Udemy', 'Course', 'Beginner', 9, 'https://www.udemy.com', ''),
        ('Tableau Official Visual Best Practices Guide', 'Official Docs', 'Documentation', 'Beginner', 5, 'https://www.tableau.com', '')
    ],
    'AWS (S3, EC2, Lambda, SageMaker)': [
        ('AWS Certified Machine Learning Specialty Course', 'Udemy', 'Specialization', 'Intermediate', 35, 'https://www.udemy.com', 'Python,Scikit-Learn'),
        ('AWS SageMaker Hands-On MLOps Workshop', 'Official Docs', 'Guided Project', 'Intermediate', 10, 'https://aws.amazon.com/sagemaker/', 'Python')
    ],
    'Computer Vision (OpenCV)': [
        ('PyImageSearch OpenCV, Deep Learning & Vision Course', 'Tutorial', 'Course', 'Intermediate', 25, 'https://pyimagesearch.com', 'Python,Convolutional Neural Networks (CNN)'),
        ('Mastering Computer Vision with PyTorch and OpenCV', 'Udemy', 'Course', 'Intermediate', 16, 'https://udemy.com', 'PyTorch')
    ],
    'Feature Engineering': [
        ('Feature Engineering for Machine Learning (Alice Zheng)', 'O Reilly Book', 'Book', 'Intermediate', 15, 'https://oreilly.com', 'Pandas & NumPy'),
        ('Feature Engineering & Selection (Kaggle Learn)', 'Kaggle Learn', 'Interactive Tutorial', 'Beginner', 8, 'https://www.kaggle.com/learn/feature-engineering', 'Scikit-Learn')
    ]
}

# Auto-expand for all skills
for skill_id, skill_name in skills_dict.items():
    if skill_name in resource_templates:
        for item in resource_templates[skill_name]:
            resources.append({
                'resource_id': f'RES{rid:04d}',
                'skill_id': skill_id,
                'skill_name': skill_name,
                'title': item[0],
                'platform': item[1],
                'resource_type': item[2],
                'difficulty': item[3],
                'duration_hours': item[4],
                'url': item[5],
                'prerequisite': item[6]
            })
            rid += 1
    else:
        resources.append({
            'resource_id': f'RES{rid:04d}',
            'skill_id': skill_id,
            'skill_name': skill_name,
            'title': f'{skill_name} Comprehensive Masterclass & Projects',
            'platform': 'Coursera / freeCodeCamp',
            'resource_type': 'Course',
            'difficulty': 'Intermediate',
            'duration_hours': random.choice([10, 15, 20, 25]),
            'url': f'https://www.google.com/search?q={skill_name}+course',
            'prerequisite': ''
        })
        rid += 1
        resources.append({
            'resource_id': f'RES{rid:04d}',
            'skill_id': skill_id,
            'skill_name': skill_name,
            'title': f'{skill_name} Official Documentation & Reference',
            'platform': 'Official Documentation',
            'resource_type': 'Documentation',
            'difficulty': 'Advanced',
            'duration_hours': random.choice([8, 12, 16]),
            'url': f'https://www.google.com/search?q={skill_name}+documentation',
            'prerequisite': skill_name
        })
        rid += 1

df_resources = pd.DataFrame(resources)
df_resources.to_csv(data_raw / 'learning_resources.csv', index=False)
print(f'Generated {len(df_resources)} learning resources.')

# 2. DEFINE 12 TARGET ROLES & CORE SKILL PROFILES
ROLE_CORE_SKILLS = {
    'Data Scientist': {
        'must': ['Python', 'SQL', 'Pandas & NumPy', 'Scikit-Learn', 'Exploratory Data Analysis', 'Supervised Learning', 'Probability & Statistics'],
        'should': ['Feature Engineering', 'XGBoost & LightGBM', 'Unsupervised Learning', 'Hypothesis Testing & A/B Testing', 'Matplotlib & Seaborn', 'Neural Networks Fundamentals'],
        'nice': ['PyTorch', 'AWS (S3, EC2, Lambda, SageMaker)', 'Docker & Containerization', 'MLflow & Experiment Tracking', 'Time Series Forecasting']
    },
    'Machine Learning Engineer': {
        'must': ['Python', 'Scikit-Learn', 'PyTorch', 'Docker & Containerization', 'Data Structures & Algorithms', 'Supervised Learning', 'Model Evaluation & Cross-Validation'],
        'should': ['Neural Networks Fundamentals', 'XGBoost & LightGBM', 'Model Serving & FastAPI', 'MLflow & Experiment Tracking', 'Linux & Bash', 'Git & GitHub'],
        'nice': ['Kubernetes', 'AWS (S3, EC2, Lambda, SageMaker)', 'Transformers & Attention Mechanisms', 'Large Language Models (LLMs)', 'CI/CD Pipelines (GitHub Actions)']
    },
    'Data Analyst': {
        'must': ['SQL', 'Python', 'Pandas & NumPy', 'Exploratory Data Analysis', 'Power BI & DAX', 'Advanced Excel & VBA'],
        'should': ['Tableau', 'Probability & Statistics', 'Hypothesis Testing & A/B Testing', 'Data Storytelling & KPI Dashboards', 'Matplotlib & Seaborn'],
        'nice': ['Scikit-Learn', 'PostgreSQL / MySQL', 'Stakeholder Communication', 'Business Acumen & Domain Knowledge']
    },
    'Data Engineer': {
        'must': ['SQL', 'Python', 'ETL / ELT Pipelines', 'Data Warehousing & Modeling', 'PostgreSQL / MySQL', 'Apache Spark / PySpark'],
        'should': ['Apache Airflow', 'Snowflake', 'Databricks', 'Linux & Bash', 'Docker & Containerization', 'Git & GitHub'],
        'nice': ['Apache Kafka', 'DBT (Data Build Tool)', 'AWS (S3, EC2, Lambda, SageMaker)', 'NoSQL & MongoDB', 'Database Indexing & Query Tuning']
    },
    'BI Developer': {
        'must': ['Power BI & DAX', 'SQL', 'Data Warehousing & Modeling', 'Data Storytelling & KPI Dashboards', 'Advanced Excel & VBA'],
        'should': ['Tableau', 'PostgreSQL / MySQL', 'ETL / ELT Pipelines', 'Stakeholder Communication', 'Business Acumen & Domain Knowledge'],
        'nice': ['Python', 'Snowflake', 'DBT (Data Build Tool)', 'Plotly & Dash / Streamlit']
    },
    'MLOps Engineer': {
        'must': ['Python', 'Docker & Containerization', 'Kubernetes', 'CI/CD Pipelines (GitHub Actions)', 'Linux & Bash', 'MLflow & Experiment Tracking'],
        'should': ['AWS (S3, EC2, Lambda, SageMaker)', 'Model Serving & FastAPI', 'Git & GitHub', 'DVC (Data Version Control)', 'PyTorch', 'Scikit-Learn'],
        'nice': ['Apache Airflow', 'Apache Kafka', 'System Design & Distributed Systems', 'Database Indexing & Query Tuning']
    },
    'AI Research Scientist': {
        'must': ['Python', 'PyTorch', 'Linear Algebra', 'Multivariate Calculus', 'Probability & Statistics', 'Neural Networks Fundamentals', 'Research Paper Implementation'],
        'should': ['Transformers & Attention Mechanisms', 'Large Language Models (LLMs)', 'Convolutional Neural Networks (CNN)', 'Recurrent Neural Networks (RNN/LSTM)', 'Scikit-Learn'],
        'nice': ['Hugging Face Ecosystem', 'Computer Vision (OpenCV)', 'Natural Language Processing (NLP)', 'C++']
    },
    'Backend Software Engineer': {
        'must': ['Python', 'SQL', 'PostgreSQL / MySQL', 'Data Structures & Algorithms', 'RESTful API Design', 'Git & GitHub'],
        'should': ['Model Serving & FastAPI', 'Docker & Containerization', 'Linux & Bash', 'Redis & Caching', 'System Design & Distributed Systems'],
        'nice': ['CI/CD Pipelines (GitHub Actions)', 'Kubernetes', 'AWS (S3, EC2, Lambda, SageMaker)', 'NoSQL & MongoDB', 'Java']
    },
    'NLP Engineer': {
        'must': ['Python', 'Natural Language Processing (NLP)', 'PyTorch', 'Transformers & Attention Mechanisms', 'Hugging Face Ecosystem', 'Scikit-Learn'],
        'should': ['Large Language Models (LLMs)', 'Retrieval-Augmented Generation (RAG)', 'Vector Databases (Chroma/Pinecone/Milvus)', 'Prompt Engineering & Fine-Tuning'],
        'nice': ['Model Serving & FastAPI', 'Docker & Containerization', 'Exploratory Data Analysis', 'MLflow & Experiment Tracking']
    },
    'Computer Vision Engineer': {
        'must': ['Python', 'Computer Vision (OpenCV)', 'PyTorch', 'Convolutional Neural Networks (CNN)', 'Neural Networks Fundamentals', 'Linear Algebra'],
        'should': ['C++', 'TensorFlow & Keras', 'Model Serving & FastAPI', 'Docker & Containerization', 'Scikit-Learn'],
        'nice': ['AWS (S3, EC2, Lambda, SageMaker)', 'Linux & Bash', 'Transformers & Attention Mechanisms']
    },
    'Cloud Data Architect': {
        'must': ['Data Warehousing & Modeling', 'SQL', 'AWS (S3, EC2, Lambda, SageMaker)', 'Snowflake', 'System Design & Distributed Systems', 'ETL / ELT Pipelines'],
        'should': ['Azure (ADF, Databricks, Azure ML)', 'Google Cloud Platform (GCP & BigQuery)', 'Databricks', 'Apache Spark / PySpark', 'Database Indexing & Query Tuning'],
        'nice': ['Kubernetes', 'Docker & Containerization', 'Apache Kafka', 'DBT (Data Build Tool)', 'Stakeholder Communication']
    },
    'Business Analyst': {
        'must': ['SQL', 'Advanced Excel & VBA', 'Data Storytelling & KPI Dashboards', 'Stakeholder Communication', 'Business Acumen & Domain Knowledge', 'Problem Solving & Critical Thinking'],
        'should': ['Power BI & DAX', 'Tableau', 'Exploratory Data Analysis', 'Agile & Scrum Methodologies', 'Hypothesis Testing & A/B Testing'],
        'nice': ['Python', 'Pandas & NumPy', 'Data Warehousing & Modeling']
    }
}

COMPANIES = [
    'Google', 'Microsoft', 'Amazon Web Services', 'Meta AI', 'Apple', 'NVIDIA', 'Netflix',
    'Uber', 'Snowflake', 'Databricks', 'Flipkart', 'Swiggy', 'Razorpay', 'Zomato',
    'JPMorgan Chase', 'Goldman Sachs', 'Morgan Stanley', 'McKinsey & Company', 'Boston Consulting Group',
    'Walmart Global Tech', 'Adobe', 'Salesforce', 'Intel Labs', 'TCS Innovation Lab', 'Infosys Cobalt',
    'PhonePe', 'Cisco Systems', 'Stripe', 'Atlassian', 'ServiceNow', 'Datadog'
]

LOCATIONS = [
    'Bangalore, India', 'Hyderabad, India', 'Pune, India', 'Gurgaon / Delhi NCR, India',
    'Mumbai, India', 'Remote (India)', 'Remote (Global)', 'San Francisco, CA, USA',
    'Seattle, WA, USA', 'New York, NY, USA', 'London, UK', 'Singapore'
]

EXP_TIERS = [
    ('Entry Level', 0, 2, (6.0, 16.0)),
    ('Mid Level', 2, 5, (14.0, 28.0)),
    ('Senior Level', 5, 8, (26.0, 50.0)),
    ('Lead / Architect', 8, 14, (45.0, 85.0))
]

TOTAL_JOBS = 12000
jobs = []
job_skills = []
start_date = datetime(2025, 1, 1)

print('Generating 12,000 job postings across 12 roles...')
for i in range(1, TOTAL_JOBS + 1):
    job_id = f'JOB{i:06d}'
    role = random.choice(list(ROLE_CORE_SKILLS.keys()))
    tier, min_e, max_e, sal_range = random.choices(
        EXP_TIERS, weights=[0.30, 0.40, 0.22, 0.08], k=1
    )[0]
    
    exp_years = round(random.uniform(min_e, max_e), 1)
    salary = round(random.uniform(sal_range[0], sal_range[1]), 2)
    company = random.choice(COMPANIES)
    location = random.choice(LOCATIONS)
    posting_date = (start_date + timedelta(days=random.randint(0, 580))).strftime('%Y-%m-%d')
    emp_type = random.choices(['Full-time', 'Contract', 'Hybrid Full-time'], weights=[0.8, 0.05, 0.15], k=1)[0]
    
    role_spec = ROLE_CORE_SKILLS[role]
    selected_must = random.sample(role_spec['must'], k=random.randint(max(1, len(role_spec['must']) - 1), len(role_spec['must'])))
    k_should = min(len(role_spec['should']), random.randint(2, len(role_spec['should'])))
    selected_should = random.sample(role_spec['should'], k=k_should)
    k_nice = min(len(role_spec['nice']), random.randint(1, len(role_spec['nice'])))
    selected_nice = random.sample(role_spec['nice'], k=k_nice)
    
    cross = []
    if random.random() < 0.2:
        other_skills = [s for s in skills_dict.values() if s not in selected_must + selected_should + selected_nice]
        cross = random.sample(other_skills, k=1)
        
    all_job_skills = selected_must + selected_should + selected_nice + cross
    skills_str = '; '.join(all_job_skills)
    
    desc = f'We are looking for a talented {tier} {role} to join our team at {company} ({location}). ' \
           f'The ideal candidate will have {exp_years}+ years of proven industry experience and strong proficiency in {skills_str}. ' \
           f'Key duties involve architecting scalable systems, driving analytical and ML initiatives, and collaborating across cross-functional teams.'
           
    jobs.append({
        'job_id': job_id,
        'job_title': f'{tier} {role}',
        'role_category': role,
        'company': company,
        'location': location,
        'experience_tier': tier,
        'min_experience_years': exp_years,
        'salary_lpa': salary,
        'employment_type': emp_type,
        'posting_date': posting_date,
        'required_skills': skills_str,
        'description': desc
    })
    
    for s_name in selected_must:
        if s_name in name_to_id:
            job_skills.append({'job_id': job_id, 'skill_id': name_to_id[s_name], 'importance': 1.0, 'importance_label': 'Must-Have'})
    for s_name in selected_should:
        if s_name in name_to_id:
            job_skills.append({'job_id': job_id, 'skill_id': name_to_id[s_name], 'importance': 0.65, 'importance_label': 'Good-to-Have'})
    for s_name in selected_nice + cross:
        if s_name in name_to_id:
            job_skills.append({'job_id': job_id, 'skill_id': name_to_id[s_name], 'importance': 0.35, 'importance_label': 'Optional'})

df_jobs = pd.DataFrame(jobs)
df_job_skills = pd.DataFrame(job_skills)

df_jobs.to_csv(data_raw / 'job_postings.csv', index=False)
df_jobs.to_csv(data_proc / 'cleaned_jobs.csv', index=False)
df_job_skills.to_csv(data_proc / 'job_skills.csv', index=False)
print(f'Successfully generated {len(df_jobs)} jobs and {len(df_job_skills)} job-skill mappings.')

# 3. POPULATE SQLITE DATABASE
print('Populating SQLite Database at', db_path)
conn = sqlite3.connect(db_path)

df_jobs.to_sql('jobs', conn, if_exists='replace', index=False)
df_skills.to_sql('skills', conn, if_exists='replace', index=False)
df_job_skills.to_sql('job_skills', conn, if_exists='replace', index=False)
df_resources.to_sql('learning_resources', conn, if_exists='replace', index=False)

cur = conn.cursor()
cur.execute('CREATE INDEX IF NOT EXISTS idx_jobs_role ON jobs (role_category)')
cur.execute('CREATE INDEX IF NOT EXISTS idx_jobs_tier ON jobs (experience_tier)')
cur.execute('CREATE INDEX IF NOT EXISTS idx_skills_name ON skills (skill_name)')
cur.execute('CREATE INDEX IF NOT EXISTS idx_job_skills_job ON job_skills (job_id)')
cur.execute('CREATE INDEX IF NOT EXISTS idx_job_skills_skill ON job_skills (skill_id)')
cur.execute('CREATE INDEX IF NOT EXISTS idx_res_skill ON learning_resources (skill_name)')
conn.commit()
conn.close()
print('Database indexing and population complete!')
