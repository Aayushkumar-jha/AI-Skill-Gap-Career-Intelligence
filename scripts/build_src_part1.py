from pathlib import Path

# 1. src/data/loader.py
loader_code = """import os
import sqlite3
import pandas as pd
from pathlib import Path
import config

def get_db_connection():
    return sqlite3.connect(config.DB_PATH)

def load_skills():
    if config.DB_PATH.exists():
        conn = get_db_connection()
        df = pd.read_sql_query("SELECT * FROM skills", conn)
        conn.close()
        return df
    return pd.read_csv(config.RAW_DATA_DIR / 'skills.csv')

def load_jobs(limit=None):
    conn = get_db_connection()
    query = "SELECT * FROM jobs"
    if limit:
        query += f" LIMIT {int(limit)}"
    df = pd.read_sql_query(query, conn)
    conn.close()
    return df

def load_job_skills():
    conn = get_db_connection()
    df = pd.read_sql_query("SELECT * FROM job_skills", conn)
    conn.close()
    return df

def load_learning_resources(skill_name=None):
    conn = get_db_connection()
    if skill_name:
        df = pd.read_sql_query(
            "SELECT * FROM learning_resources WHERE skill_name = ?", conn, params=(skill_name,)
        )
    else:
        df = pd.read_sql_query("SELECT * FROM learning_resources", conn)
    conn.close()
    return df

def get_market_skill_demand():
    conn = get_db_connection()
    query = '''
    SELECT s.skill_name, s.category, COUNT(js.job_id) as demand_count,
           ROUND(AVG(js.importance), 2) as avg_importance
    FROM job_skills js
    JOIN skills s ON js.skill_id = s.skill_id
    GROUP BY s.skill_name, s.category
    ORDER BY demand_count DESC
    '''
    df = pd.read_sql_query(query, conn)
    conn.close()
    max_demand = df['demand_count'].max() if len(df) > 0 else 1
    df['normalized_demand'] = (df['demand_count'] / max_demand).round(4)
    return df
"""
Path('src/data/loader.py').write_text(loader_code, encoding='utf-8')

# 2. src/data/db_manager.py
db_manager_code = """import sqlite3
import pandas as pd
from pathlib import Path
import config

class DatabaseManager:
    def __init__(self, db_path=config.DB_PATH):
        self.db_path = db_path
        self._init_tables()

    def get_connection(self):
        return sqlite3.connect(self.db_path)

    def _init_tables(self):
        conn = self.get_connection()
        cur = conn.cursor()
        cur.execute('''
        CREATE TABLE IF NOT EXISTS candidate_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
            candidate_name TEXT,
            experience_years REAL,
            education_level TEXT,
            extracted_skills_json TEXT,
            top_recommended_role TEXT,
            top_suitability_score REAL
        )
        ''')
        conn.commit()
        conn.close()

    def save_candidate_profile(self, name, exp_years, edu_level, skills_json, top_role, top_score):
        conn = self.get_connection()
        cur = conn.cursor()
        cur.execute('''
        INSERT INTO candidate_history 
        (candidate_name, experience_years, education_level, extracted_skills_json, top_recommended_role, top_suitability_score)
        VALUES (?, ?, ?, ?, ?, ?)
        ''', (name, exp_years, edu_level, skills_json, top_role, top_score))
        conn.commit()
        conn.close()

    def get_candidate_history(self):
        conn = self.get_connection()
        df = pd.read_sql_query("SELECT * FROM candidate_history ORDER BY id DESC LIMIT 20", conn)
        conn.close()
        return df
"""
Path('src/data/db_manager.py').write_text(db_manager_code, encoding='utf-8')

# 3. src/nlp/text_cleaner.py
cleaner_code = """import re
import string

def clean_text(text: str) -> str:
    if not isinstance(text, str):
        return ""
    text = text.replace('\\r', ' ').replace('\\n', ' ')
    text = re.sub(r'\\s+', ' ', text)
    text = text.strip()
    return text

def normalize_skill_name(skill: str) -> str:
    s = skill.strip().lower()
    s = re.sub(r'[^a-zA-Z0-9+#./-]', ' ', s)
    s = re.sub(r'\\s+', ' ', s).strip()
    return s
"""
Path('src/nlp/text_cleaner.py').write_text(cleaner_code, encoding='utf-8')

# 4. src/nlp/resume_parser.py
resume_parser_code = """import re
import io
import zipfile
import xml.etree.ElementTree as ET
from pypdf import PdfReader
from src.nlp.text_cleaner import clean_text

class ResumeParser:
    @staticmethod
    def extract_text_from_pdf(file_bytes) -> str:
        try:
            reader = PdfReader(io.BytesIO(file_bytes))
            text = []
            for page in reader.pages:
                t = page.extract_text()
                if t:
                    text.append(t)
            return clean_text(" ".join(text))
        except Exception as e:
            return f"Error parsing PDF: {str(e)}"

    @staticmethod
    def extract_text_from_docx(file_bytes) -> str:
        try:
            with zipfile.ZipFile(io.BytesIO(file_bytes)) as z:
                tree = ET.fromstring(z.read('word/document.xml'))
                paragraphs = []
                for p in tree.iter('{http://schemas.openxmlformats.org/wordprocessingml/2006/main}p'):
                    texts = [t.text for t in p.iter('{http://schemas.openxmlformats.org/wordprocessingml/2006/main}t') if t.text]
                    if texts:
                        paragraphs.append(''.join(texts))
                return clean_text(" ".join(paragraphs))
        except Exception as e:
            return f"Error parsing DOCX: {str(e)}"

    @staticmethod
    def extract_experience_years(text: str) -> float:
        # Look for explicit years of experience: e.g. "3+ years", "4 years of experience", "2.5 yrs"
        exp_patterns = [
            r'(\\b\\d+(?:\\.\\d+)?)\\s*\\+?\\s*(?:years?|yrs?)(?:\\s+of)?\\s+experience',
            r'experience\\s*:\\s*(\\b\\d+(?:\\.\\d+)?)\\s*\\+?\\s*(?:years?|yrs?)',
            r'(\\b\\d+(?:\\.\\d+)?)\\s*\\+?\\s*years?\\s+(?:in|of|as)'
        ]
        for pattern in exp_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            if matches:
                try:
                    vals = [float(m) for m in matches if float(m) <= 40]
                    if vals:
                        return max(vals)
                except ValueError:
                    pass
        # Fallback heuristic: count year ranges e.g. 2021-2024
        range_matches = re.findall(r'(20\\d{2})\\s*[-–—to]+\\s*(20\\d{2}|present)', text, re.IGNORECASE)
        if range_matches:
            total_yrs = 0
            for start, end in range_matches:
                s = int(start)
                e = 2026 if 'present' in end.lower() else int(end)
                if 0 <= (e - s) <= 25:
                    total_yrs = max(total_yrs, e - s)
            if total_yrs > 0:
                return float(total_yrs)
        return 1.0 # Default entry level

    @staticmethod
    def extract_education(text: str) -> str:
        text_lower = text.lower()
        if any(kw in text_lower for kw in ['ph.d', 'phd', 'doctor of philosophy']):
            return 'PhD'
        elif any(kw in text_lower for kw in ['m.tech', 'm.s.', 'master of technology', 'master of science', 'mca', 'm.sc', 'mba']):
            return "Master's"
        elif any(kw in text_lower for kw in ['b.tech', 'b.e.', 'bachelor of technology', 'bachelor of engineering', 'bca', 'b.sc', 'bachelor']):
            return "Bachelor's"
        return "Bachelor's"
"""
Path('src/nlp/resume_parser.py').write_text(resume_parser_code, encoding='utf-8')

# 5. src/nlp/skill_extractor.py
skill_extractor_code = """import re
import pandas as pd
from typing import Dict, List, Tuple
from src.data.loader import load_skills

# Comprehensive canonical alias map
SKILL_ALIASES = {
    'Python': ['python', 'python3', 'py', 'pythonic'],
    'R': ['r programming', 'r-lang', 'r language'],
    'SQL': ['sql', 'structured query language', 'ansi sql', 't-sql', 'pl/sql'],
    'Java': ['java', 'java8', 'java11', 'core java'],
    'C++': ['c++', 'cpp', 'c plus plus'],
    'Scala': ['scala'],
    'Bash/Shell Scripting': ['bash', 'shell script', 'shell scripting', 'sh', 'zsh'],
    'JavaScript': ['javascript', 'js', 'es6'],
    'TypeScript': ['typescript', 'ts'],
    'Go': ['golang', 'go language'],
    'Linear Algebra': ['linear algebra', 'matrices', 'eigenvalues', 'matrix operations'],
    'Multivariate Calculus': ['calculus', 'multivariable calculus', 'gradients', 'derivatives'],
    'Probability & Statistics': ['statistics', 'probability', 'inferential statistics', 'probabilistic modeling'],
    'Hypothesis Testing & A/B Testing': ['a/b testing', 'ab testing', 'hypothesis testing', 'p-value', 't-test', 'chi-square'],
    'Bayesian Inference': ['bayesian', 'bayes', 'mcmc', 'pymc'],
    'Exploratory Data Analysis': ['eda', 'exploratory data analysis', 'data profiling', 'data wrangling'],
    'Pandas & NumPy': ['pandas', 'numpy', 'scipy stack'],
    'Scikit-Learn': ['scikit-learn', 'sklearn', 'scikit learn'],
    'Supervised Learning': ['supervised learning', 'linear regression', 'logistic regression', 'decision trees', 'random forest'],
    'Unsupervised Learning': ['unsupervised learning', 'k-means', 'clustering', 'pca', 't-sne', 'dimensionality reduction'],
    'Feature Engineering': ['feature engineering', 'feature extraction', 'feature selection', 'data preprocessing'],
    'XGBoost & LightGBM': ['xgboost', 'lightgbm', 'catboost', 'gradient boosting'],
    'Model Evaluation & Cross-Validation': ['cross validation', 'k-fold', 'roc-auc', 'confusion matrix', 'f1-score'],
    'Time Series Forecasting': ['time series', 'arima', 'prophet', 'sarima', 'lstm time series'],
    'Neural Networks Fundamentals': ['neural networks', 'ann', 'backpropagation', 'deep learning basics'],
    'PyTorch': ['pytorch', 'torch'],
    'TensorFlow & Keras': ['tensorflow', 'tf', 'keras', 'tf.keras'],
    'Convolutional Neural Networks (CNN)': ['cnn', 'convolutional neural network', 'resnet', 'yolo'],
    'Computer Vision (OpenCV)': ['computer vision', 'opencv', 'image processing', 'cv2', 'object detection'],
    'Recurrent Neural Networks (RNN/LSTM)': ['rnn', 'lstm', 'gru', 'recurrent neural networks'],
    'Transformers & Attention Mechanisms': ['transformers', 'attention mechanism', 'bert', 'roberta', 't5'],
    'Hugging Face Ecosystem': ['hugging face', 'huggingface', 'diffusers', 'tokenizers'],
    'Large Language Models (LLMs)': ['llm', 'llms', 'large language models', 'gpt-4', 'llama', 'mistral', 'claude'],
    'Retrieval-Augmented Generation (RAG)': ['rag', 'retrieval augmented generation', 'langchain', 'llamaindex'],
    'Prompt Engineering & Fine-Tuning': ['prompt engineering', 'lora', 'qlora', 'peft', 'instruction tuning'],
    'Natural Language Processing (NLP)': ['nlp', 'natural language processing', 'spacy', 'nltk', 'text mining', 'named entity recognition'],
    'Data Warehousing & Modeling': ['data warehouse', 'data warehousing', 'star schema', 'snowflake schema', 'dimensional modeling'],
    'ETL / ELT Pipelines': ['etl', 'elt', 'data pipeline', 'data pipelines', 'data ingestion'],
    'Apache Spark / PySpark': ['spark', 'pyspark', 'apache spark'],
    'Apache Kafka': ['kafka', 'apache kafka', 'event streaming', 'pub/sub'],
    'Apache Airflow': ['airflow', 'apache airflow', 'dag', 'dags', 'workflow orchestration'],
    'Snowflake': ['snowflake', 'snowflake data cloud'],
    'Databricks': ['databricks', 'delta lake'],
    'DBT (Data Build Tool)': ['dbt', 'data build tool'],
    'Hadoop & HDFS': ['hadoop', 'hdfs', 'mapreduce'],
    'PostgreSQL / MySQL': ['postgresql', 'postgres', 'mysql'],
    'NoSQL & MongoDB': ['mongodb', 'nosql', 'documentdb'],
    'Redis & Caching': ['redis', 'caching', 'memcached'],
    'Vector Databases (Chroma/Pinecone/Milvus)': ['pinecone', 'chromadb', 'milvus', 'weaviate', 'vector db', 'faiss'],
    'Database Indexing & Query Tuning': ['query optimization', 'database indexing', 'execution plan', 'query tuning'],
    'Linux & Bash': ['linux', 'ubuntu', 'bash', 'unix'],
    'Docker & Containerization': ['docker', 'containerization', 'dockerfile', 'docker compose'],
    'Kubernetes': ['kubernetes', 'k8s', 'helm', 'kubectl'],
    'AWS (S3, EC2, Lambda, SageMaker)': ['aws', 'amazon web services', 's3', 'ec2', 'sagemaker', 'lambda'],
    'Azure (ADF, Databricks, Azure ML)': ['azure', 'azure ml', 'azure data factory'],
    'Google Cloud Platform (GCP & BigQuery)': ['gcp', 'google cloud', 'bigquery', 'vertex ai'],
    'CI/CD Pipelines (GitHub Actions)': ['ci/cd', 'cicd', 'github actions', 'jenkins', 'gitlab ci'],
    'MLflow & Experiment Tracking': ['mlflow', 'experiment tracking', 'model registry', 'wandb', 'weights & biases'],
    'DVC (Data Version Control)': ['dvc', 'data version control'],
    'Model Serving & FastAPI': ['fastapi', 'flask', 'model serving', 'rest api deployment', 'torchserve'],
    'Power BI & DAX': ['power bi', 'powerbi', 'dax', 'power query'],
    'Tableau': ['tableau', 'tableau desktop'],
    'Plotly & Dash / Streamlit': ['streamlit', 'plotly', 'dash'],
    'Matplotlib & Seaborn': ['matplotlib', 'seaborn', 'data visualization'],
    'Advanced Excel & VBA': ['excel', 'vba', 'pivot tables', 'vlookup', 'advanced excel'],
    'Data Storytelling & KPI Dashboards': ['kpi', 'dashboards', 'data storytelling', 'executive reporting'],
    'Data Structures & Algorithms': ['dsa', 'data structures', 'algorithms', 'leetcode'],
    'Git & GitHub': ['git', 'github', 'version control'],
    'System Design & Distributed Systems': ['system design', 'distributed systems', 'microservices', 'high availability'],
    'RESTful API Design': ['rest api', 'restful', 'api design', 'json api'],
    'Problem Solving & Critical Thinking': ['problem solving', 'analytical skills', 'critical thinking'],
    'Stakeholder Communication': ['stakeholder management', 'client communication', 'presentation skills'],
    'Agile & Scrum Methodologies': ['agile', 'scrum', 'jira', 'sprint planning'],
    'Business Acumen & Domain Knowledge': ['business acumen', 'business domain', 'roi analysis'],
    'Research Paper Implementation': ['research paper', 'arxiv', 'literature review', 'novel architecture']
}

class SkillExtractor:
    def __init__(self):
        self.df_skills = load_skills()
        self.skill_names = self.df_skills['skill_name'].tolist()

    def extract_skills_with_proficiency(self, text: str) -> Dict[str, float]:
        text_clean = text.lower()
        extracted = {}

        for skill_name, aliases in SKILL_ALIASES.items():
            found_count = 0
            has_lead_context = False

            for alias in aliases:
                # Regex boundary match
                pattern = r'(?<![a-zA-Z0-9])' + re.escape(alias) + r'(?![a-zA-Z0-9])'
                matches = re.findall(pattern, text_clean)
                if matches:
                    found_count += len(matches)
                    
                    # Context checks around the skill
                    sub_context_pattern = r'(?:advanced|expert|proficient|experienced|lead|senior|built|architected|deployed)\\s+[^.\\n]*?' + re.escape(alias)
                    if re.search(sub_context_pattern, text_clean):
                        has_lead_context = True

            if found_count > 0:
                # Proficiency heuristic: 0.1 to 1.0
                # Baseline 0.50
                score = 0.50
                # Mention frequency bonus (up to +0.25)
                score += min(0.25, (found_count - 1) * 0.08)
                # Strong context bonus
                if has_lead_context:
                    score += 0.20
                extracted[skill_name] = round(min(1.0, score), 2)

        return extracted
"""
Path('src/nlp/skill_extractor.py').write_text(skill_extractor_code, encoding='utf-8')
print('Data and NLP modules created successfully!')
