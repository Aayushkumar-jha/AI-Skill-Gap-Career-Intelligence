import pytest
from src.recommendation.skill_gap import SkillGapEngine
from src.recommendation.skill_priority import SkillPriorityEngine
from src.recommendation.learning_path import LearningPathEngine

def test_skill_gap_analysis():
    gap_engine = SkillGapEngine()
    candidate_skills = {"Python": 0.9, "SQL": 0.85}
    analysis = gap_engine.analyze_gaps(candidate_skills, "Data Scientist")
    
    assert analysis["target_role"] == "Data Scientist"
    assert "matched" in analysis
    assert "partial" in analysis
    assert "missing" in analysis
    assert len(analysis["matched"]) >= 1

def test_skill_priority_ranking():
    gap_engine = SkillGapEngine()
    priority_engine = SkillPriorityEngine()
    candidate_skills = {"Python": 0.9, "SQL": 0.85}
    analysis = gap_engine.analyze_gaps(candidate_skills, "Data Scientist")
    ranked = priority_engine.prioritize_gaps(analysis, candidate_skills)
    
    assert len(ranked) > 0
    # Highest priority should be first
    assert ranked[0]["priority_score"] >= ranked[-1]["priority_score"]
    assert ranked[0]["priority_tier"] in ["High", "Medium", "Low"]

def test_learning_path_dag():
    gap_engine = SkillGapEngine()
    priority_engine = SkillPriorityEngine()
    lp_engine = LearningPathEngine()
    
    candidate_skills = {"Python": 0.9}
    analysis = gap_engine.analyze_gaps(candidate_skills, "Data Scientist")
    ranked = priority_engine.prioritize_gaps(analysis, candidate_skills)
    roadmap = lp_engine.build_personalized_roadmap(ranked, candidate_skills)
    
    assert len(roadmap) > 0
    assert roadmap[0]["order"] == 1
    assert "Phase" in roadmap[0]["phase"]
    assert len(roadmap[0]["resources"]) > 0
