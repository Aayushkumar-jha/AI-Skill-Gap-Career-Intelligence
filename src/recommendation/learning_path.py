import pandas as pd
from typing import Dict, List, Any
from src.data.loader import load_skills, load_learning_resources

class LearningPathEngine:
    def __init__(self):
        self.df_skills = load_skills()
        self.df_resources = load_learning_resources()
        self.prereq_map = dict(zip(self.df_skills['skill_name'], self.df_skills['prerequisites'].fillna('')))
        self.diff_map = dict(zip(self.df_skills['skill_name'], self.df_skills['difficulty']))

    def build_personalized_roadmap(self, prioritized_skills: List[Dict[str, Any]], candidate_skills: Dict[str, float]) -> List[Dict[str, Any]]:
        # Topological Ordering
        target_skills = [s['skill_name'] for s in prioritized_skills]
        visited = set()
        ordered_skills = []

        def visit(skill):
            if skill in visited:
                return
            visited.add(skill)
            prereqs_raw = self.prereq_map.get(skill, '')
            if prereqs_raw and prereqs_raw != 'None':
                for p in prereqs_raw.split(','):
                    p_clean = p.strip()
                    if p_clean and candidate_skills.get(p_clean, 0.0) < 0.5:
                        visit(p_clean)
            ordered_skills.append(skill)

        for s in target_skills:
            visit(s)

        roadmap = []
        current_week = 1
        
        # Partition into phases
        n = len(ordered_skills)
        for idx, skill in enumerate(ordered_skills):
            diff = self.diff_map.get(skill, 'Intermediate')
            
            if idx < max(2, int(n * 0.35)):
                phase = "Phase 1: Foundational Prerequisites"
                duration_wks = 2
            elif idx < max(4, int(n * 0.75)):
                phase = "Phase 2: Core Competencies"
                duration_wks = 3
            else:
                phase = "Phase 3: Advanced & Capstone Integration"
                duration_wks = 4

            # Fetch top learning resources
            res = self.df_resources[self.df_resources['skill_name'] == skill].head(2).to_dict(orient='records')
            
            roadmap.append({
                'order': idx + 1,
                'skill_name': skill,
                'phase': phase,
                'difficulty': diff,
                'start_week': current_week,
                'end_week': current_week + duration_wks - 1,
                'duration_weeks': duration_wks,
                'resources': res
            })
            current_week += duration_wks

        return roadmap
