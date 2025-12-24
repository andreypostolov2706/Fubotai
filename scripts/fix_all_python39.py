"""
Fix ALL Python 3.9 compatibility issues in the entire project
Adds 'from __future__ import annotations' to files that need it
"""
import os
import re
from pathlib import Path

def needs_future_import(content: str) -> bool:
    """Check if file uses Python 3.10+ type syntax"""
    patterns = [
        r'\blist\[',           # list[...]
        r'\bdict\[',           # dict[...]
        r'\btuple\[',          # tuple[...]
        r'\bset\[',            # set[...]
        r'\w+\s*\|\s*\w+',     # str | None, int | str, etc.
    ]
    
    for pattern in patterns:
        if re.search(pattern, content):
            return True
    return False

def has_future_import(content: str) -> bool:
    """Check if file already has future annotations import"""
    return 'from __future__ import annotations' in content

def add_future_import(content: str) -> str:
    """Add future annotations import at the top of the file"""
    lines = content.split('\n')
    
    # Find the position to insert (after docstring, before other imports)
    insert_pos = 0
    in_docstring = False
    docstring_char = None
    
    for i, line in enumerate(lines):
        stripped = line.strip()
        
        # Handle docstrings
        if not in_docstring:
            if stripped.startswith('"""') or stripped.startswith("'''"):
                docstring_char = stripped[:3]
                if stripped.count(docstring_char) >= 2:
                    # Single-line docstring
                    insert_pos = i + 1
                else:
                    in_docstring = True
            elif stripped and not stripped.startswith('#'):
                # First non-comment, non-docstring line
                insert_pos = i
                break
        else:
            if docstring_char in line:
                in_docstring = False
                insert_pos = i + 1
    
    # Insert the import
    lines.insert(insert_pos, 'from __future__ import annotations')
    lines.insert(insert_pos + 1, '')
    
    return '\n'.join(lines)

def fix_file(filepath: Path) -> bool:
    """Fix a single file. Returns True if modified."""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        
        if not needs_future_import(content):
            return False
        
        if has_future_import(content):
            return False
        
        new_content = add_future_import(content)
        
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(new_content)
        
        print(f"✅ Fixed: {filepath}")
        return True
    except Exception as e:
        print(f"❌ Error processing {filepath}: {e}")
        return False

def main():
    project_root = Path(__file__).parent.parent
    
    # Scan all Python files in core/ and services/
    directories = ['core', 'services']
    fixed_count = 0
    
    for directory in directories:
        dir_path = project_root / directory
        if not dir_path.exists():
            continue
        
        for py_file in dir_path.rglob('*.py'):
            # Skip __pycache__ and other generated files
            if '__pycache__' in str(py_file):
                continue
            
            if fix_file(py_file):
                fixed_count += 1
    
    print(f"\n✅ Fixed {fixed_count} files!")
    print("Now run: supervisorctl restart fubotai")

if __name__ == '__main__':
    main()
