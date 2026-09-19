import os
from pathlib import Path

# Base Paths
BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / 'data'
RAW_DATA_DIR = DATA_DIR / 'raw'
PROCESSED_DATA_DIR = DATA_DIR / 'processed'
DATABASE_DIR = BASE_DIR / 'database'
DB_PATH = DATABASE_DIR / 'career_intelligence.db'
MODELS_DIR = BASE_DIR / 'models'
REPORTS_DIR = BASE_DIR / 'reports'

# Ensure directories exist
for p in [RAW_DATA_DIR, PROCESSED_DATA_DIR, DATABASE_DIR, MODELS_DIR, REPORTS_DIR]:
    p.mkdir(parents=True, exist_ok=True)

# Standardized Target Roles (12 Key Industry Roles)
TARGET_ROLES = [
    'Data Scientist',
    'Machine Learning Engineer',
    'Data Analyst',
    'Data Engineer',
    'BI Developer',
    'MLOps Engineer',
    'AI Research Scientist',
    'Backend Software Engineer',
    'NLP Engineer',
    'Computer Vision Engineer',
    'Cloud Data Architect',
    'Business Analyst'
]

# Skill Categories
SKILL_CATEGORIES = [
    'Programming',
    'Data Science & ML',
    'Deep Learning & AI',
    'Data Engineering & Big Data',
    'Databases & SQL',
    'Cloud & DevOps',
    'Business Intelligence & Viz',
    'Web & API Development',
    'Mathematics & Statistics',
    'Core CS & Systems',
    'Domain & Soft Skills'
]

# Skill Priority Weights Formula:
PRIORITY_WEIGHTS = {
    'market_demand': 0.35,
    'role_importance': 0.30,
    'deficiency': 0.20,
    'prereq_readiness': 0.15
}

# Experience Benchmarks (in years)
EXPERIENCE_BENCHMARKS = {
    'Entry Level': (0, 2),
    'Mid Level': (2, 5),
    'Senior Level': (5, 10),
    'Lead / Architect': (8, 20)
}

RANDOM_STATE = 42
