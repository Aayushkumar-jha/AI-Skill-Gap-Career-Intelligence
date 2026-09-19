import re
import string

def clean_text(text: str) -> str:
    if not isinstance(text, str):
        return ""
    text = text.replace('\r', ' ').replace('\n', ' ')
    text = re.sub(r'\s+', ' ', text)
    text = text.strip()
    return text

def normalize_skill_name(skill: str) -> str:
    s = skill.strip().lower()
    s = re.sub(r'[^a-zA-Z0-9+#./-]', ' ', s)
    s = re.sub(r'\s+', ' ', s).strip()
    return s
