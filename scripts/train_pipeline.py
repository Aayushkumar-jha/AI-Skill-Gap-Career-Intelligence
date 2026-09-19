import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import random
import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import classification_report, accuracy_score
import config
from src.data.loader import load_skills, load_jobs, load_job_skills
from src.features.feature_engineering import FeatureEngineer
from src.models.role_classifier import RoleClassifier

random.seed(config.RANDOM_STATE)
np.random.seed(config.RANDOM_STATE)

print("Initializing Feature Engineer...")
fe = FeatureEngineer()
roles = config.TARGET_ROLES
df_skills = load_skills()
skill_names = df_skills['skill_name'].tolist()

print("Generating synthetic candidate feature dataset for 12 roles...")
X_samples = []
y_labels = []

from scripts.generate_full_market_and_resources import ROLE_CORE_SKILLS

for role in roles:
    spec = ROLE_CORE_SKILLS[role]
    must_skills = spec['must']
    should_skills = spec['should']
    nice_skills = spec['nice']
    
    for _ in range(300):
        exp_tier = random.choices(['Entry Level', 'Mid Level', 'Senior Level'], weights=[0.4, 0.4, 0.2])[0]
        if exp_tier == 'Entry Level':
            exp = round(random.uniform(0.5, 2.0), 1)
            edu = random.choice(["Bachelor's", "Master's"])
            must_ratio = random.uniform(0.70, 0.95)
            should_ratio = random.uniform(0.40, 0.70)
            nice_ratio = random.uniform(0.10, 0.40)
            base_prof = (0.50, 0.80)
        elif exp_tier == 'Mid Level':
            exp = round(random.uniform(2.5, 5.5), 1)
            edu = random.choices(["Bachelor's", "Master's", "PhD"], weights=[0.6, 0.35, 0.05])[0]
            must_ratio = random.uniform(0.85, 1.0)
            should_ratio = random.uniform(0.60, 0.90)
            nice_ratio = random.uniform(0.30, 0.60)
            base_prof = (0.65, 0.92)
        else:
            exp = round(random.uniform(6.0, 12.0), 1)
            edu = random.choices(["Master's", "PhD", "Bachelor's"], weights=[0.5, 0.25, 0.25])[0]
            must_ratio = 1.0
            should_ratio = random.uniform(0.75, 1.0)
            nice_ratio = random.uniform(0.50, 0.85)
            base_prof = (0.75, 1.0)

        cand_skills = {}
        k_must = max(1, int(len(must_skills) * must_ratio))
        for s in random.sample(must_skills, k=k_must):
            cand_skills[s] = round(random.uniform(base_prof[0], base_prof[1]), 2)
            
        k_should = max(1, int(len(should_skills) * should_ratio))
        for s in random.sample(should_skills, k=k_should):
            cand_skills[s] = round(random.uniform(base_prof[0] - 0.1, base_prof[1]), 2)
            
        k_nice = max(0, int(len(nice_skills) * nice_ratio))
        if k_nice > 0:
            for s in random.sample(nice_skills, k=k_nice):
                cand_skills[s] = round(random.uniform(0.40, base_prof[1]), 2)
                
        if random.random() < 0.3:
            random_s = random.choice(skill_names)
            if random_s not in cand_skills:
                cand_skills[random_s] = round(random.uniform(0.30, 0.70), 2)
                
        feat_vec = fe.candidate_to_feature_vector(cand_skills, exp, edu)
        X_samples.append(feat_vec)
        y_labels.append(role)

X_arr = np.array(X_samples)
feature_names = fe.get_feature_names()

print(f"Constructed feature matrix of shape {X_arr.shape} with {len(feature_names)} features.")

print("Training RoleClassifier model...")
clf = RoleClassifier()
metrics = clf.train(X_arr, y_labels, feature_names=feature_names)
print(f"Model Training Complete! Train Accuracy: {metrics['train_acc']:.4f}, Test Accuracy: {metrics['test_acc']:.4f}")

# Sanity check inference
test_cand = {
    'Python': 0.9, 'SQL': 0.85, 'Pandas & NumPy': 0.9, 'Scikit-Learn': 0.85,
    'Exploratory Data Analysis': 0.8, 'Supervised Learning': 0.85
}
test_vec = fe.candidate_to_feature_vector(test_cand, 2.0, "Bachelor's")
pred_df = clf.predict_roles(test_vec)
print("\nTop 3 predicted roles for sample Data Science candidate:")
print(pred_df.head(3).to_string(index=False))
