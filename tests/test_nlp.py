import pytest
from src.nlp.text_cleaner import clean_text, normalize_skill_name
from src.nlp.skill_extractor import SkillExtractor
from src.nlp.resume_parser import ResumeParser

def test_clean_text():
    raw = "  Hello   World!\r\nThis is a test.   "
    cleaned = clean_text(raw)
    assert cleaned == "Hello World! This is a test."

def test_normalize_skill_name():
    assert normalize_skill_name("Scikit-Learn") == "scikit-learn"
    assert normalize_skill_name("C++") == "c++"

def test_skill_extractor():
    extractor = SkillExtractor()
    sample_text = """
    Senior Data Scientist with 5 years experience in Python, SQL, and Scikit-Learn.
    Built production ML models using PyTorch, Pandas & NumPy.
    Proficient in Docker and Git.
    """
    extracted = extractor.extract_skills_with_proficiency(sample_text)
    assert "Python" in extracted
    assert "SQL" in extracted
    assert "Scikit-Learn" in extracted
    assert "PyTorch" in extracted
    assert "Docker & Containerization" in extracted
    # Check proficiency bounds
    for skill, prof in extracted.items():
        assert 0.1 <= prof <= 1.0

def test_resume_parser_heuristics():
    sample_resume = """
    John Doe
    Education: B.Tech in Computer Science
    Experience: 4.5 years of experience as Machine Learning Engineer
    """
    exp = ResumeParser.extract_experience_years(sample_resume)
    edu = ResumeParser.extract_education(sample_resume)
    name = ResumeParser.extract_candidate_name(sample_resume, "john_doe_resume.pdf")
    meta = ResumeParser.get_file_metadata(b"sample resume bytes", "john_doe_resume.pdf", sample_resume)
    
    assert exp == 4.5
    assert edu == "Bachelor's"
    assert name == "John Doe"
    assert meta["filename"] == "john_doe_resume.pdf"
    assert meta["file_type"] == "PDF Document"

