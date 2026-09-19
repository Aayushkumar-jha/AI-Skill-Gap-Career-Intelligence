import sqlite3
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
