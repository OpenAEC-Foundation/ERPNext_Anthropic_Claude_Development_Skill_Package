#!/usr/bin/env python3
"""
Quick validation script for Anthropic skill format.
Based on documented requirements from LESSONS_LEARNED.md §6.3
"""

import os
import sys
import re
import yaml

def validate_skill(skill_path):
    """Validate a skill folder against Anthropic requirements."""
    errors = []
    warnings = []
    
    skill_path = os.path.abspath(skill_path)
    skill_name = os.path.basename(skill_path)
    
    # Check 1: SKILL.md exists in root
    skill_md_path = os.path.join(skill_path, "SKILL.md")
    if not os.path.exists(skill_md_path):
        errors.append("SKILL.md not found in skill root folder")
        return errors, warnings
    
    # Read SKILL.md
    with open(skill_md_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Check 2: Line count < 500
    lines = content.split('\n')
    if len(lines) > 500:
        errors.append(f"SKILL.md has {len(lines)} lines (max 500)")
    
    # Check 3: YAML frontmatter exists and is valid
    if not content.startswith('---'):
        errors.append("SKILL.md must start with YAML frontmatter (---)")
        return errors, warnings
    
    # Extract frontmatter
    parts = content.split('---', 2)
    if len(parts) < 3:
        errors.append("Invalid YAML frontmatter format")
        return errors, warnings
    
    try:
        frontmatter = yaml.safe_load(parts[1])
    except yaml.YAMLError as e:
        errors.append(f"Invalid YAML in frontmatter: {e}")
        return errors, warnings
    
    # Check 4: name field
    if 'name' not in frontmatter:
        errors.append("Missing required 'name' field in frontmatter")
    else:
        name = frontmatter['name']
        if len(name) > 64:
            errors.append(f"name '{name}' exceeds 64 characters ({len(name)})")
        if not re.match(r'^[a-z0-9-]+$', name):
            errors.append(f"name '{name}' must be kebab-case (a-z, 0-9, - only)")
    
    # Check 5: description field
    if 'description' not in frontmatter:
        errors.append("Missing required 'description' field in frontmatter")
    else:
        desc = str(frontmatter['description'])
        if len(desc) > 1024:
            errors.append(f"description exceeds 1024 characters ({len(desc)})")
        if '<' in desc or '>' in desc:
            warnings.append("description contains < or > which may cause issues")
    
    # Check 6: No forbidden files
    forbidden_files = ['README.md', 'CHANGELOG.md']
    for ff in forbidden_files:
        if os.path.exists(os.path.join(skill_path, ff)):
            warnings.append(f"Found {ff} in skill folder (not recommended)")
    
    # Check 7: references/ folder structure
    refs_path = os.path.join(skill_path, "references")
    if os.path.exists(refs_path):
        if not os.path.isdir(refs_path):
            errors.append("'references' should be a directory, not a file")
    
    return errors, warnings

def main():
    if len(sys.argv) < 2:
        print("Usage: python quick_validate.py <skill_folder>")
        sys.exit(1)
    
    skill_path = sys.argv[1]
    
    if not os.path.isdir(skill_path):
        print(f"Error: {skill_path} is not a directory")
        sys.exit(1)
    
    print(f"Validating: {skill_path}")
    print("-" * 50)
    
    errors, warnings = validate_skill(skill_path)
    
    if warnings:
        print("\n⚠️  WARNINGS:")
        for w in warnings:
            print(f"   - {w}")
    
    if errors:
        print("\n❌ ERRORS:")
        for e in errors:
            print(f"   - {e}")
        print(f"\nValidation FAILED with {len(errors)} error(s)")
        sys.exit(1)
    else:
        print("\n✅ Skill is valid!")
        sys.exit(0)

if __name__ == "__main__":
    main()
