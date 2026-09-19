import pytest
import numpy as np
from src.features.feature_engineering import FeatureEngineer
from src.models.role_classifier import RoleClassifier

def test_feature_engineering():
    fe = FeatureEngineer()
    candidate_skills = {
        "Python": 0.9, "SQL": 0.8, "Pandas & NumPy": 0.85,
        "Scikit-Learn": 0.8, "Supervised Learning": 0.8
    }
    vec = fe.candidate_to_feature_vector(candidate_skills, 2.5, "Master's")
    assert isinstance(vec, np.ndarray)
    assert len(vec) == 27
    assert vec[0] > 0.0 # Experience norm
    assert vec[1] == 0.8 # Master's weight

def test_role_classifier_inference():
    fe = FeatureEngineer()
    clf = RoleClassifier()
    candidate_skills = {
        "Python": 0.95, "PyTorch": 0.90, "Scikit-Learn": 0.85,
        "Docker & Containerization": 0.80, "Data Structures & Algorithms": 0.85
    }
    vec = fe.candidate_to_feature_vector(candidate_skills, 3.0, "Bachelor's")
    pred_df = clf.predict_roles(vec)
    
    assert len(pred_df) == 12
    assert "role" in pred_df.columns
    assert "suitability_score" in pred_df.columns
    assert pred_df.iloc[0]["suitability_score"] >= pred_df.iloc[1]["suitability_score"]
