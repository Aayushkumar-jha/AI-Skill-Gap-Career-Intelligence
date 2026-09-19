import pandas as pd
from typing import Dict, List, Any
from src.data.loader import load_skills, load_job_skills, load_jobs

class SkillGapEngine:
    def __init__(self):
        self.df_skills = load_skills()
        self.skill_map = dict(zip(self.df_skills['skill_id'], self.df_skills['skill_name']))
        self.cat_map = dict(zip(self.df_skills['skill_name'], self.df_skills['category']))
        self.diff_map = dict(zip(self.df_skills['skill_name'], self.df_skills['difficulty']))

    def get_role_requirements(self, target_role: str) -> pd.DataFrame:
        df_jobs = load_jobs()
        df_js = load_job_skills()
        
        role_job_ids = df_jobs[df_jobs['role_category'] == target_role]['job_id'].tolist()
        reqs = df_js[df_js['job_id'].isin(role_job_ids)]
        
        grouped = reqs.groupby('skill_id').agg(
            frequency=('job_id', 'count'),
            avg_importance=('importance', 'mean')
        ).reset_index()
        
        grouped['skill_name'] = grouped['skill_id'].map(self.skill_map)
        grouped['category'] = grouped['skill_name'].map(self.cat_map)
        grouped['difficulty'] = grouped['skill_name'].map(self.diff_map)
        
        total_jobs_in_role = max(1, len(role_job_ids))
        grouped['demand_pct'] = (grouped['frequency'] / total_jobs_in_role * 100).round(1)
        grouped['required_proficiency'] = grouped['avg_importance'].apply(lambda x: 0.85 if x >= 0.8 else (0.65 if x >= 0.5 else 0.45))
        
        return grouped.sort_values(by='frequency', ascending=False)

    def analyze_gaps(self, candidate_skills: Dict[str, float], target_role: str) -> Dict[str, Any]:
        role_reqs = self.get_role_requirements(target_role)
        
        matched = []
        partial = []
        missing = []
        
        for _, row in role_reqs.iterrows():
            s_name = row['skill_name']
            cand_prof = candidate_skills.get(s_name, 0.0)
            req_prof = row['required_proficiency']
            gap = max(0.0, req_prof - cand_prof)
            
            item = {
                'skill_name': s_name,
                'category': row['category'],
                'difficulty': row['difficulty'],
                'candidate_proficiency': cand_prof,
                'required_proficiency': req_prof,
                'gap': round(gap, 2),
                'demand_pct': row['demand_pct'],
                'avg_importance': round(row['avg_importance'], 2)
            }
            
            if cand_prof >= req_prof:
                matched.append(item)
            elif cand_prof > 0.0:
                partial.append(item)
            else:
                missing.append(item)
                
        total_reqs = len(role_reqs)
        match_rate = round((len(matched) + 0.5 * len(partial)) / total_reqs * 100, 1) if total_reqs > 0 else 0
        
        return {
            'target_role': target_role,
            'match_rate': match_rate,
            'matched_count': len(matched),
            'partial_count': len(partial),
            'missing_count': len(missing),
            'matched': matched,
            'partial': partial,
            'missing': missing
        }
