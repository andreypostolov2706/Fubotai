"""
Fix Python 3.9 compatibility - add future annotations to files using | union syntax
"""
import os
import re
from pathlib import Path

def needs_future_import(content: str) -> bool:
    """Check if file uses | union syntax"""
    # Match patterns like: str | None, int | str, etc.
    pattern = r'\b\w+\s*\|\s*\w+'
    return bool(re.search(pattern, content))

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
            print(f"✅ Already fixed: {filepath}")
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
    
    # Files identified by grep
    files_to_fix = [
        'core/platform/telegram/media_sender.py',
        'core/payments/providers/platega.py',
        'core/platform/telegram/handlers/service.py',
        'core/platform/telegram/middlewares.py',
        'core/platform/telegram/utils.py',
    ]
    
    fixed_count = 0
    for file_path in files_to_fix:
        full_path = project_root / file_path
        if full_path.exists():
            if fix_file(full_path):
                fixed_count += 1
        else:
            print(f"⏭️  File not found: {full_path}")
    
    print(f"\n✅ Fixed {fixed_count} files!")

if __name__ == '__main__':
    main()
