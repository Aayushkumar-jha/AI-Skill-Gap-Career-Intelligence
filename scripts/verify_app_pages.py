import sys
from pathlib import Path
sys.path.insert(0, str(Path('.').resolve()))

# Check imports of all modules
try:
    import config
    import src.data.loader as loader
    import src.data.db_manager as db_manager
    import src.nlp.text_cleaner as cleaner
    import src.nlp.skill_extractor as extractor
    import src.nlp.resume_parser as parser
    import src.features.feature_engineering as fe
    import src.models.role_classifier as rc
    import src.recommendation.skill_gap as sg
    import src.recommendation.skill_priority as sp
    import src.recommendation.learning_path as lp
    import src.explainability.shap_analysis as xai
    import src.evaluation.metrics as em
    import app.components.ui_helpers as ui
    import app.components.charts as ch
    print("All Python modules imported successfully!")
except Exception as e:
    print(f"Error importing modules: {e}")
    sys.exit(1)

# Check syntax of all page files
pages = list(Path('app/pages').glob('*.py')) + [Path('app/app.py')]
for p in pages:
    try:
        compile(p.read_text(encoding='utf-8'), str(p), 'exec')
        print(f"Verified syntax: {p.name}")
    except Exception as e:
        print(f"Syntax error in {p.name}: {e}")
        sys.exit(1)

print("\nAll Streamlit pages verified with 100% clean syntax and imports!")
