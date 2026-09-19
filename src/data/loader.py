import os
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
