import re
import io
import zipfile
import xml.etree.ElementTree as ET
from pathlib import Path
from pypdf import PdfReader
from src.nlp.text_cleaner import clean_text

class ResumeParser:
    @staticmethod
    def extract_text_from_pdf(file_bytes) -> str:
        try:
            reader = PdfReader(io.BytesIO(file_bytes))
            text = []
            for page in reader.pages:
                t = page.extract_text()
                if t:
                    text.append(t)
            return clean_text(" ".join(text))
        except Exception as e:
            return f"Error parsing PDF: {str(e)}"

    @staticmethod
    def extract_text_from_docx(file_bytes) -> str:
        try:
            with zipfile.ZipFile(io.BytesIO(file_bytes)) as z:
                tree = ET.fromstring(z.read('word/document.xml'))
                paragraphs = []
                for p in tree.iter('{http://schemas.openxmlformats.org/wordprocessingml/2006/main}p'):
                    texts = [t.text for t in p.iter('{http://schemas.openxmlformats.org/wordprocessingml/2006/main}t') if t.text]
                    if texts:
                        paragraphs.append(''.join(texts))
                return clean_text(" ".join(paragraphs))
        except Exception as e:
            return f"Error parsing DOCX: {str(e)}"

    @staticmethod
    def extract_candidate_name(text: str, filename: str = "") -> str:
        stop_headers = {
            'curriculum vitae', 'resume', 'profile', 'email', 'phone', 'contact',
            'page', 'http', 'www', 'linkedin', 'github', 'skills', 'technical skills',
            'summary', 'experience', 'education', 'projects', 'certifications', 'objective'
        }
        
        # Split text into original lines
        raw_lines = [l.strip() for l in text.splitlines() if l.strip()]
        
        # Filter lines that look like candidate names (first 5 lines)
        for line in raw_lines[:6]:
            line_lower = line.lower()
            if any(h in line_lower for h in stop_headers) or '@' in line or 'http' in line_lower:
                continue
            cleaned = re.sub(r'[^a-zA-Z\s]', ' ', line).strip()
            words = cleaned.split()
            if 2 <= len(words) <= 4:
                # Disallow common role/title words
                disallowed = {
                    'software', 'engineer', 'developer', 'data', 'scientist', 'analyst',
                    'fresher', 'experience', 'education', 'skills', 'projects', 'summary',
                    'objective', 'btech', 'mtech', 'python', 'sql', 'java', 'manager',
                    'intern', 'consultant', 'lead', 'architect', 'junior', 'senior'
                }
                if all(w.isalpha() and len(w) >= 2 and w.lower() not in disallowed for w in words):
                    return ' '.join(w.capitalize() for w in words)

        # Fallback to extracting name from filename
        if filename:
            stem = Path(filename).stem
            cleaned_stem = re.sub(r'(?i)[_\-]*(?:resume|cv|profile|latest|updated|final|\d+)[_\-]*', ' ', stem)
            cleaned_stem = re.sub(r'[^a-zA-Z\s]', ' ', cleaned_stem).strip()
            words = cleaned_stem.split()
            if 1 <= len(words) <= 4:
                return ' '.join(w.capitalize() for w in words)

        return "Candidate Profile"

    @staticmethod
    def get_file_metadata(file_bytes, filename: str, extracted_text: str) -> dict:
        size_kb = round(len(file_bytes) / 1024.0, 1)
        ext = Path(filename).suffix.lower() if filename else ""
        
        page_or_para_count = 1
        file_type = "Plain Text"
        
        if ext == ".pdf":
            file_type = "PDF Document"
            try:
                reader = PdfReader(io.BytesIO(file_bytes))
                page_or_para_count = len(reader.pages)
            except Exception:
                page_or_para_count = 1
        elif ext == ".docx":
            file_type = "Microsoft Word (.docx)"
            try:
                with zipfile.ZipFile(io.BytesIO(file_bytes)) as z:
                    tree = ET.fromstring(z.read('word/document.xml'))
                    paras = list(tree.iter('{http://schemas.openxmlformats.org/wordprocessingml/2006/main}p'))
                    page_or_para_count = len(paras)
            except Exception:
                page_or_para_count = 1

        words = len(extracted_text.split())
        chars = len(extracted_text)

        return {
            "filename": filename,
            "file_size_kb": size_kb,
            "file_type": file_type,
            "unit_count": page_or_para_count,
            "unit_label": "Pages" if ext == ".pdf" else ("Paragraphs" if ext == ".docx" else "Lines"),
            "word_count": words,
            "char_count": chars
        }

    @staticmethod
    def extract_experience_years(text: str) -> float:
        exp_patterns = [
            r'(\b\d+(?:\.\d+)?)\s*\+?\s*(?:years?|yrs?)(?:\s+of)?\s+experience',
            r'experience\s*:\s*(\b\d+(?:\.\d+)?)\s*\+?\s*(?:years?|yrs?)',
            r'(\b\d+(?:\.\d+)?)\s*\+?\s*years?\s+(?:in|of|as)'
        ]
        for pattern in exp_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            if matches:
                try:
                    vals = [float(m) for m in matches if float(m) <= 40]
                    if vals:
                        return max(vals)
                except ValueError:
                    pass
        range_matches = re.findall(r'(20\d{2})\s*[-–—to]+\s*(20\d{2}|present)', text, re.IGNORECASE)
        if range_matches:
            total_yrs = 0
            for start, end in range_matches:
                s = int(start)
                e = 2026 if 'present' in end.lower() else int(end)
                if 0 <= (e - s) <= 25:
                    total_yrs = max(total_yrs, e - s)
            if total_yrs > 0:
                return float(total_yrs)
        return 1.0

    @staticmethod
    def extract_education(text: str) -> str:
        text_lower = text.lower()
        if any(kw in text_lower for kw in ['ph.d', 'phd', 'doctor of philosophy']):
            return 'PhD'
        elif any(kw in text_lower for kw in ['m.tech', 'm.s.', 'master of technology', 'master of science', 'mca', 'm.sc', 'mba']):
            return "Master's"
        elif any(kw in text_lower for kw in ['b.tech', 'b.e.', 'bachelor of technology', 'bachelor of engineering', 'bca', 'b.sc', 'bachelor']):
            return "Bachelor's"
        return "Bachelor's"
