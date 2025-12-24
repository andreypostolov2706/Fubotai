"""
Fix Python 3.9 compatibility by adding 'from __future__ import annotations'
to all files that use list[...] or dict[...] syntax
"""
import os
import re
from pathlib import Path

# Files to fix based on grep results
FILES_TO_FIX = [
    "core/plugins/base_service.py",
    "core/settings/manager.py",
    "core/payments/providers/cryptobot.py",
    "core/payments/providers/manager.py",
    "core/plugins/registry.py",
    "services/ai_avatar/service.py",
    "services/gpt_image/service.py",
    "services/kling/service.py",
    "services/nano_banano/service.py",
    "core/database/models/partner.py",
    "core/database/models/user.py",
    "core/locales/__init__.py",
    "core/payments/providers/base.py",
    "core/payments/rates.py",
    "core/plugins/core_api.py",
    "services/flux2_flex/service.py",
    "services/gpt_image/api/fal_client.py",
    "services/kling/api/fal_client.py",
    "services/sora/service.py",
    "services/veo/service.py",
    "core/config.py",
    "core/database/models/payment.py",
    "core/payments/converter.py",
    "core/payments/providers/platega.py",
    "core/payments/service.py",
    "core/platform/telegram/keyboards/main_menu.py",
    "core/platform/telegram/utils.py",
    "core/referral/commission.py",
    "services/nano_banano/api/fal_client.py",
]

FUTURE_IMPORT = "from __future__ import annotations\n"


def fix_file(file_path: Path) -> bool:
    """Add future annotations import if needed"""
    
    if not file_path.exists():
        print(f"⚠️  File not found: {file_path}")
        return False
    
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Check if already has the import
    if "from __future__ import annotations" in content:
        print(f"✅ Already fixed: {file_path}")
        return False
    
    # Check if file uses list[...] or dict[...] syntax
    if not (re.search(r'list\[', content) or re.search(r'dict\[', content)):
        print(f"⏭️  No changes needed: {file_path}")
        return False
    
    # Find the position to insert the import
    lines = content.split('\n')
    
    # Find first non-comment, non-empty line after docstring
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
                    continue
                else:
                    in_docstring = True
                    continue
        else:
            if docstring_char in stripped:
                in_docstring = False
                insert_pos = i + 1
                continue
        
        # Skip empty lines and comments after docstring
        if not in_docstring and stripped and not stripped.startswith('#'):
            insert_pos = i
            break
    
    # Insert the import
    lines.insert(insert_pos, FUTURE_IMPORT)
    
    # Write back
    new_content = '\n'.join(lines)
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(new_content)
    
    print(f"✅ Fixed: {file_path}")
    return True


def main():
    """Fix all files"""
    project_root = Path(__file__).parent.parent
    
    print("🔧 Fixing Python 3.9 compatibility...\n")
    
    fixed_count = 0
    for file_rel_path in FILES_TO_FIX:
        file_path = project_root / file_rel_path
        if fix_file(file_path):
            fixed_count += 1
    
    print(f"\n✅ Fixed {fixed_count} files!")


if __name__ == "__main__":
    main()
