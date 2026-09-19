import shutil
from pathlib import Path

root = Path('.').resolve()
app_dir = root / 'app'
components_src = app_dir / 'components'
components_dst = root / 'components'

# Copy components to root as well so both import paths work seamlessly
if not components_dst.exists():
    shutil.copytree(components_src, components_dst)
    print("Copied components to root directory.")

# Update all python files in app and app/pages
py_files = [app_dir / 'app.py'] + list((app_dir / 'pages').glob('*.py'))

for py_file in py_files:
    content = py_file.read_text(encoding='utf-8')
    
    # Ensure sys.path includes both root and app_dir
    header = """import sys
from pathlib import Path
root_dir = Path(__file__).resolve().parent.parent
app_dir = Path(__file__).resolve().parent
if str(root_dir) not in sys.path:
    sys.path.insert(0, str(root_dir))
if str(app_dir) not in sys.path:
    sys.path.insert(0, str(app_dir))
"""
    # Replace the existing sys.path header
    if "root_dir = Path(__file__).resolve()" in content:
        # replace from 'import sys' up to 'sys.path.insert(0, str(root_dir))'
        lines = content.splitlines()
        new_lines = []
        skip = False
        inserted = False
        for line in lines:
            if line.startswith("import sys") and not inserted:
                new_lines.append(header)
                skip = True
                inserted = True
                continue
            if skip:
                if "import streamlit as st" in line:
                    skip = False
                    new_lines.append(line)
                continue
            new_lines.append(line)
        content = "\n".join(new_lines)
    
    # Replace app.components imports with resilient try-except or direct components import
    content = content.replace("from app.components.ui_helpers import", "from components.ui_helpers import")
    content = content.replace("from app.components.charts import", "from components.charts import")
    
    py_file.write_text(content, encoding='utf-8')
    print(f"Updated imports in {py_file.name}")

print("All app files updated successfully!")
