import pandas as pd
from typing import Dict, List, Any
import config
from src.data.loader import load_skills, get_market_skill_demand

class SkillPriorityEngine:
    def __init__(self):
        self.weights = config.PRIORITY_WEIGHTS
        self.df_skills = load_skills()
        self.prereq_map = dict(zip(self.df_skills['skill_name'], self.df_skills['prerequisites'].fillna('')))
        self.market_demand = get_market_skill_demand()
        self.demand_dict = dict(zip(self.market_demand['skill_name'], self.market_demand['normalized_demand']))

    def prioritize_gaps(self, gap_analysis: Dict[str, Any], candidate_skills: Dict[str, float]) -> List[Dict[str, Any]]:
        gaps_to_rank = gap_analysis['partial'] + gap_analysis['missing']
        ranked = []
        
        for item in gaps_to_rank:
            s_name = item['skill_name']
            
            # 1. Market demand score (0.0 to 1.0)
            market_score = self.demand_dict.get(s_name, item['demand_pct'] / 100.0)
            
            # 2. Role importance score (0.0 to 1.0)
            role_score = item['avg_importance']
            
            # 3. Deficiency score (gap magnitude 0.0 to 1.0)
            deficiency_score = item['gap']
            
            # 4. Prerequisite readiness (Are candidate's prereqs met?)
            prereqs_str = self.prereq_map.get(s_name, '')
            if not prereqs_str or prereqs_str == 'None':
                prereq_readiness = 1.0
            else:
                prereq_list = [p.strip() for p in prereqs_str.split(',') if p.strip()]
                met_count = sum(1 for p in prereq_list if candidate_skills.get(p, 0.0) >= 0.5)
                prereq_readiness = met_count / len(prereq_list) if prereq_list else 1.0
                
            # Weighted Priority Formula
            priority_score = (
                self.weights['market_demand'] * market_score +
                self.weights['role_importance'] * role_score +
                self.weights['deficiency'] * deficiency_score +
                self.weights['prereq_readiness'] * prereq_readiness
            )
            
            if priority_score >= 0.65:
                tier = 'High'
            elif priority_score >= 0.40:
                tier = 'Medium'
            else:
                tier = 'Low'
                
            ranked.append({
                **item,
                'priority_score': round(float(priority_score) * 100, 1),
                'priority_tier': tier,
                'prereq_readiness': round(float(prereq_readiness) * 100, 0),
                'prerequisites': prereqs_str
            })
            
        ranked.sort(key=lambda x: x['priority_score'], reverse=True)
        return ranked
