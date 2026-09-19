import numpy as np
import pandas as pd
from typing import Dict, List, Tuple
import config
from src.data.loader import load_skills, load_job_skills, load_jobs

class FeatureEngineer:
    def __init__(self):
        self.df_skills = load_skills()
        self.skill_names = self.df_skills['skill_name'].tolist()
        self.categories = config.SKILL_CATEGORIES
        self.roles = config.TARGET_ROLES
        
        # Precompute category to skills dict for O(1) lookups
        self.cat_to_skills = {c: [] for c in self.categories}
        for cat, group in self.df_skills.groupby('category'):
            if cat in self.cat_to_skills:
                self.cat_to_skills[cat] = group['skill_name'].tolist()
                
        self._build_role_archetypes()

    def _build_role_archetypes(self):
        df_js = load_job_skills()
        df_jobs = load_jobs()
        merged = df_js.merge(df_jobs[['job_id', 'role_category']], on='job_id')
        merged = merged.merge(self.df_skills[['skill_id', 'skill_name']], on='skill_id')
        
        # Single vectorized groupby
        mean_weights = merged.groupby(['role_category', 'skill_name'])['importance'].mean().reset_index()
        
        self.role_skill_weights = {r: {} for r in self.roles}
        for _, row in mean_weights.iterrows():
            r = row['role_category']
            if r in self.role_skill_weights:
                self.role_skill_weights[r][row['skill_name']] = float(row['importance'])
                
        self.role_total_weights = {
            r: sum(self.role_skill_weights[r].values()) or 1.0 for r in self.roles
        }

    def candidate_to_feature_vector(self, candidate_skills: Dict[str, float], exp_years: float, edu_level: str) -> np.ndarray:
        edu_map = {"Bachelor's": 0.5, "Master's": 0.8, "PhD": 1.0}
        edu_val = edu_map.get(edu_level, 0.5)
        exp_val = min(1.0, float(exp_years) / 15.0)

        # Category scores
        cat_scores = []
        for cat in self.categories:
            skills_in_cat = self.cat_to_skills.get(cat, [])
            if not skills_in_cat:
                cat_scores.append(0.0)
                continue
            cat_profs = [candidate_skills.get(s, 0.0) for s in skills_in_cat]
            top_3 = sorted(cat_profs, reverse=True)[:3]
            cat_scores.append(float(np.mean(top_3)))

        # Role scores
        role_scores = []
        for role in self.roles:
            weights = self.role_skill_weights.get(role, {})
            total_w = self.role_total_weights.get(role, 1.0)
            w_sum = sum(candidate_skills[s] * w for s, w in weights.items() if s in candidate_skills)
            role_scores.append(float(w_sum / total_w))

        skill_count_norm = min(1.0, len(candidate_skills) / 30.0)
        avg_prof = float(np.mean(list(candidate_skills.values()))) if candidate_skills else 0.0

        features = [exp_val, edu_val, skill_count_norm, avg_prof] + cat_scores + role_scores
        return np.array(features, dtype=np.float32)

    def get_feature_names(self) -> List[str]:
        base = ['Experience_Norm', 'Education_Weight', 'Skills_Count_Norm', 'Avg_Proficiency']
        cats = [f'Cat_{c.replace(" ", "_").replace("&", "and")}' for c in self.categories]
        roles = [f'RoleFit_{r.replace(" ", "_")}' for r in self.roles]
        return base + cats + roles
