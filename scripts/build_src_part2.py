from pathlib import Path

# 1. src/features/feature_engineering.py
feat_code = """import numpy as np
import pandas as pd
from typing import Dict, List, Tuple
import config
from src.data.loader import load_skills, load_job_skills

class FeatureEngineer:
    def __init__(self):
        self.df_skills = load_skills()
        self.skill_names = self.df_skills['skill_name'].tolist()
        self.categories = config.SKILL_CATEGORIES
        self.roles = config.TARGET_ROLES
        self._build_role_archetypes()

    def _build_role_archetypes(self):
        df_js = load_job_skills()
        df_merged = df_js.merge(self.df_skills, on='skill_id')
        
        # Calculate base skill importance per role category from jobs
        from src.data.loader import load_jobs
        df_jobs = load_jobs()
        merged = df_js.merge(df_jobs[['job_id', 'role_category']], on='job_id')
        merged = merged.merge(self.df_skills[['skill_id', 'skill_name', 'category']], on='skill_id')
        
        self.role_skill_weights = {}
        for role in self.roles:
            role_df = merged[merged['role_category'] == role]
            counts = role_df.groupby('skill_name')['importance'].mean().to_dict()
            self.role_skill_weights[role] = counts

    def candidate_to_feature_vector(self, candidate_skills: Dict[str, float], exp_years: float, edu_level: str) -> np.ndarray:
        # Education weight
        edu_map = {"Bachelor's": 0.5, "Master's": 0.8, "PhD": 1.0}
        edu_val = edu_map.get(edu_level, 0.5)

        # 1. Base experience normalized (0 to 15 years -> 0.0 to 1.0)
        exp_val = min(1.0, float(exp_years) / 15.0)

        # 2. Category average proficiencies (11 values)
        cat_scores = []
        for cat in self.categories:
            skills_in_cat = self.df_skills[self.df_skills['category'] == cat]['skill_name'].tolist()
            if not skills_in_cat:
                cat_scores.append(0.0)
                continue
            cat_profs = [candidate_skills.get(s, 0.0) for s in skills_in_cat]
            # Average of top 3 skills in category
            top_3 = sorted(cat_profs, reverse=True)[:3]
            cat_scores.append(float(np.mean(top_3)))

        # 3. Role-specific weighted coverage scores (12 values)
        role_scores = []
        for role in self.roles:
            weights = self.role_skill_weights.get(role, {})
            if not weights:
                role_scores.append(0.0)
                continue
            total_weight = sum(weights.values())
            weighted_sum = sum(candidate_skills.get(s, 0.0) * w for s, w in weights.items())
            coverage = (weighted_sum / total_weight) if total_weight > 0 else 0.0
            role_scores.append(float(coverage))

        # 4. Total skills count & global proficiency
        skill_count_norm = min(1.0, len(candidate_skills) / 30.0)
        avg_prof = float(np.mean(list(candidate_skills.values()))) if candidate_skills else 0.0

        features = [exp_val, edu_val, skill_count_norm, avg_prof] + cat_scores + role_scores
        return np.array(features, dtype=np.float32)

    def get_feature_names(self) -> List[str]:
        base = ['Experience_Norm', 'Education_Weight', 'Skills_Count_Norm', 'Avg_Proficiency']
        cats = [f'Cat_{c.replace(" ", "_").replace("&", "and")}' for c in self.categories]
        roles = [f'RoleFit_{r.replace(" ", "_")}' for r in self.roles]
        return base + cats + roles
"""
Path('src/features/feature_engineering.py').write_text(feat_code, encoding='utf-8')

# 2. src/models/role_classifier.py
role_classifier_code = """import os
import pickle
import numpy as np
import pandas as pd
from pathlib import Path
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split, cross_val_score
import config

class RoleClassifier:
    def __init__(self):
        self.model_path = config.MODELS_DIR / 'role_model.pkl'
        self.scaler_path = config.MODELS_DIR / 'scaler.pkl'
        self.metadata_path = config.MODELS_DIR / 'model_metadata.json'
        self.model = None
        self.scaler = None
        self.feature_names = None
        self.load_or_initialize()

    def load_or_initialize(self):
        if self.model_path.exists() and self.scaler_path.exists():
            with open(self.model_path, 'rb') as f:
                self.model = pickle.load(f)
            with open(self.scaler_path, 'rb') as f:
                self.scaler = pickle.load(f)
            if self.metadata_path.exists():
                import json
                with open(self.metadata_path, 'r') as f:
                    meta = json.load(f)
                    self.feature_names = meta.get('feature_names', [])
        else:
            self.model = RandomForestClassifier(n_estimators=120, max_depth=14, random_state=config.RANDOM_STATE)
            self.scaler = StandardScaler()

    def train(self, X: np.ndarray, y: List[str], feature_names: List[str] = None):
        self.feature_names = feature_names or []
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=config.RANDOM_STATE, stratify=y)
        
        X_train_scaled = self.scaler.fit_transform(X_train)
        X_test_scaled = self.scaler.transform(X_test)
        
        self.model.fit(X_train_scaled, y_train)
        train_acc = self.model.score(X_train_scaled, y_train)
        test_acc = self.model.score(X_test_scaled, y_test)
        
        # Save artifacts
        with open(self.model_path, 'wb') as f:
            pickle.dump(self.model, f)
        with open(self.scaler_path, 'wb') as f:
            pickle.dump(self.scaler, f)
            
        import json
        with open(self.metadata_path, 'w') as f:
            json.dump({
                'feature_names': self.feature_names,
                'train_accuracy': round(float(train_acc), 4),
                'test_accuracy': round(float(test_acc), 4),
                'classes': list(self.model.classes_)
            }, f, indent=2)
            
        return {'train_acc': train_acc, 'test_acc': test_acc}

    def predict_roles(self, feature_vector: np.ndarray) -> pd.DataFrame:
        if self.model is None or self.scaler is None:
            self.load_or_initialize()
            
        feat_2d = feature_vector.reshape(1, -1)
        feat_scaled = self.scaler.transform(feat_2d)
        
        probabilities = self.model.predict_proba(feat_scaled)[0]
        classes = self.model.classes_
        
        results = []
        for role, prob in zip(classes, probabilities):
            # Scale probability to an intuitive Career Suitability Score (35% to 98%)
            suitability = round(float(prob) * 100, 1)
            results.append({
                'role': role,
                'suitability_score': suitability,
                'raw_prob': round(float(prob), 4)
            })
            
        df = pd.DataFrame(results).sort_values(by='suitability_score', ascending=False).reset_index(drop=True)
        df['rank'] = df.index + 1
        return df
"""
Path('src/models/role_classifier.py').write_text(role_classifier_code, encoding='utf-8')

# 3. src/recommendation/skill_gap.py
skill_gap_code = """import pandas as pd
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
"""
Path('src/recommendation/skill_gap.py').write_text(skill_gap_code, encoding='utf-8')

# 4. src/recommendation/skill_priority.py
skill_priority_code = """import pandas as pd
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
"""
Path('src/recommendation/skill_priority.py').write_text(skill_priority_code, encoding='utf-8')

# 5. src/recommendation/learning_path.py
learning_path_code = """import pandas as pd
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
"""
Path('src/recommendation/learning_path.py').write_text(learning_path_code, encoding='utf-8')

# 6. src/explainability/shap_analysis.py
shap_code = """import numpy as np
import pandas as pd
from typing import Dict, List, Any

class ExplainabilityEngine:
    def __init__(self, classifier, feature_names: List[str]):
        self.classifier = classifier
        self.feature_names = feature_names

    def explain_candidate_prediction(self, feature_vector: np.ndarray, target_role: str) -> Dict[str, Any]:
        feat_scaled = self.classifier.scaler.transform(feature_vector.reshape(1, -1))[0]
        
        # Determine base weights from model tree importances or linear coefficients
        if hasattr(self.classifier.model, 'feature_importances_'):
            importances = self.classifier.model.feature_importances_
        else:
            importances = np.ones(len(self.feature_names)) / len(self.feature_names)
            
        contributions = feat_scaled * importances
        
        factors = []
        for name, val, cont in zip(self.feature_names, feature_vector, contributions):
            # Clean human readable name
            clean_name = name.replace('RoleFit_', 'Role Fit: ').replace('Cat_', 'Domain: ').replace('_', ' ')
            is_pos = cont >= 0
            factors.append({
                'feature': clean_name,
                'raw_value': round(float(val), 2),
                'contribution': round(float(cont), 3),
                'direction': 'Positive Driver' if is_pos else 'Missing Gap Penalty'
            })
            
        df_factors = pd.DataFrame(factors)
        pos_drivers = df_factors[df_factors['contribution'] > 0].sort_values(by='contribution', ascending=False).head(6).to_dict(orient='records')
        neg_drivers = df_factors[df_factors['contribution'] <= 0].sort_values(by='contribution').head(6).to_dict(orient='records')
        
        return {
            'target_role': target_role,
            'positive_drivers': pos_drivers,
            'negative_penalties': neg_drivers,
            'all_factors': factors
        }
"""
Path('src/explainability/shap_analysis.py').write_text(shap_code, encoding='utf-8')

# 7. src/evaluation/metrics.py
eval_code = """import numpy as np
import pandas as pd
from sklearn.metrics import classification_report, confusion_matrix, accuracy_score, f1_score

def evaluate_classifier(model, X_test, y_test):
    y_pred = model.predict(X_test)
    acc = accuracy_score(y_test, y_pred)
    macro_f1 = f1_score(y_test, y_pred, average='macro')
    weighted_f1 = f1_score(y_test, y_pred, average='weighted')
    report = classification_report(y_test, y_pred, output_dict=True)
    cm = confusion_matrix(y_test, y_pred)
    
    return {
        'accuracy': round(acc, 4),
        'macro_f1': round(macro_f1, 4),
        'weighted_f1': round(weighted_f1, 4),
        'report': report,
        'confusion_matrix': cm.tolist()
    }
"""
Path('src/evaluation/metrics.py').write_text(eval_code, encoding='utf-8')
print('Part 2 core modules created successfully!')
