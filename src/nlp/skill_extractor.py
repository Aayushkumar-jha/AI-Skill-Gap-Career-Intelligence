import re
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
                    sub_context_pattern = r'(?:advanced|expert|proficient|experienced|lead|senior|built|architected|deployed)\s+[^.\n]*?' + re.escape(alias)
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
