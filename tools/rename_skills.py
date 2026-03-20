#!/usr/bin/env python3
"""V2.0 Rename Script: erpnext-* -> frappe-* skill migration.

This script:
1. Renames all 28 skill directories using git mv
2. Updates name: fields in SKILL.md frontmatter
3. Updates all cross-references across all .md files
4. Updates license from LGPL-3.0 to MIT
5. Reports what was changed
"""

import os
import re
import subprocess
import sys

# Project root
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SKILLS_DIR = os.path.join(ROOT, "skills", "source")

# Complete rename mapping (old_name -> new_name)
RENAME_MAP = {
    # Syntax (8 skills)
    "frappe-syntax-clientscripts": "frappe-syntax-clientscripts",
    "frappe-syntax-serverscripts": "frappe-syntax-serverscripts",
    "frappe-syntax-controllers": "frappe-syntax-controllers",
    "frappe-syntax-hooks": "frappe-syntax-hooks",
    "frappe-syntax-whitelisted": "frappe-syntax-whitelisted",
    "frappe-syntax-jinja": "frappe-syntax-jinja",
    "frappe-syntax-scheduler": "frappe-syntax-scheduler",
    "frappe-syntax-customapp": "frappe-syntax-customapp",
    # Core (3 skills)
    "frappe-core-database": "frappe-core-database",
    "frappe-core-permissions": "frappe-core-permissions",
    "frappe-core-api": "frappe-core-api",
    # Implementation (8 skills)
    "frappe-impl-clientscripts": "frappe-impl-clientscripts",
    "frappe-impl-serverscripts": "frappe-impl-serverscripts",
    "frappe-impl-controllers": "frappe-impl-controllers",
    "frappe-impl-hooks": "frappe-impl-hooks",
    "frappe-impl-whitelisted": "frappe-impl-whitelisted",
    "frappe-impl-jinja": "frappe-impl-jinja",
    "frappe-impl-scheduler": "frappe-impl-scheduler",
    "frappe-impl-customapp": "frappe-impl-customapp",
    # Errors (7 skills)
    "frappe-errors-clientscripts": "frappe-errors-clientscripts",
    "frappe-errors-serverscripts": "frappe-errors-serverscripts",
    "frappe-errors-controllers": "frappe-errors-controllers",
    "frappe-errors-hooks": "frappe-errors-hooks",
    "frappe-errors-database": "frappe-errors-database",
    "frappe-errors-permissions": "frappe-errors-permissions",
    "frappe-errors-api": "frappe-errors-api",
    # Agents (2 skills)
    "frappe-agent-interpreter": "frappe-agent-interpreter",
    "frappe-agent-validator": "frappe-agent-validator",
}

# Category mapping (old_dir_name -> category_folder)
CATEGORY_MAP = {
    "frappe-syntax-clientscripts": "syntax",
    "frappe-syntax-serverscripts": "syntax",
    "frappe-syntax-controllers": "syntax",
    "frappe-syntax-hooks": "syntax",
    "frappe-syntax-whitelisted": "syntax",
    "frappe-syntax-jinja": "syntax",
    "frappe-syntax-scheduler": "syntax",
    "frappe-syntax-customapp": "syntax",
    "frappe-core-database": "core",
    "frappe-core-permissions": "core",
    "frappe-core-api": "core",
    "frappe-impl-clientscripts": "impl",
    "frappe-impl-serverscripts": "impl",
    "frappe-impl-controllers": "impl",
    "frappe-impl-hooks": "impl",
    "frappe-impl-whitelisted": "impl",
    "frappe-impl-jinja": "impl",
    "frappe-impl-scheduler": "impl",
    "frappe-impl-customapp": "impl",
    "frappe-errors-clientscripts": "errors",
    "frappe-errors-serverscripts": "errors",
    "frappe-errors-controllers": "errors",
    "frappe-errors-hooks": "errors",
    "frappe-errors-database": "errors",
    "frappe-errors-permissions": "errors",
    "frappe-errors-api": "errors",
    "frappe-agent-interpreter": "agents",
    "frappe-agent-validator": "agents",
}


def git_mv(old_path, new_path):
    """Rename using git mv."""
    result = subprocess.run(
        ["git", "mv", old_path, new_path],
        cwd=ROOT,
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        print(f"  ERROR: git mv failed: {result.stderr.strip()}")
        return False
    return True


def find_all_md_files(directory):
    """Find all .md files recursively."""
    md_files = []
    for dirpath, dirnames, filenames in os.walk(directory):
        # Skip .git directory
        if ".git" in dirpath:
            continue
        for filename in filenames:
            if filename.endswith(".md"):
                md_files.append(os.path.join(dirpath, filename))
    return md_files


def replace_in_file(filepath, replacements):
    """Apply multiple string replacements in a file. Returns count of changes."""
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            content = f.read()
    except (UnicodeDecodeError, FileNotFoundError):
        return 0

    original = content
    for old, new in replacements:
        content = content.replace(old, new)

    if content != original:
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(content)
        changes = sum(1 for old, new in replacements if old in original)
        return changes
    return 0


def main():
    print("=" * 60)
    print("V2.0 Skill Rename: erpnext-* -> frappe-*")
    print("=" * 60)

    # Step 1: Rename directories
    print("\n--- Step 1: Renaming directories ---")
    renamed = 0
    for old_name, new_name in RENAME_MAP.items():
        category = CATEGORY_MAP[old_name]
        old_path = os.path.join("skills", "source", category, old_name)
        new_path = os.path.join("skills", "source", category, new_name)

        old_full = os.path.join(ROOT, old_path)
        if not os.path.exists(old_full):
            print(f"  SKIP: {old_path} (not found)")
            continue

        if git_mv(old_path, new_path):
            print(f"  OK: {old_name} -> {new_name}")
            renamed += 1

    print(f"\n  Renamed {renamed}/{len(RENAME_MAP)} directories")

    # Step 2: Build replacement pairs for content updates
    print("\n--- Step 2: Updating cross-references in all .md files ---")

    # Sort by length (longest first) to avoid partial replacements
    replacements = sorted(
        [(old, new) for old, new in RENAME_MAP.items()],
        key=lambda x: len(x[0]),
        reverse=True,
    )

    # Also add license replacement
    license_replacements = [
        ("license: MIT", "license: MIT"),
        ('license: MIT', "license: MIT"),
        ("license: MIT-or-later", "license: MIT"),
    ]

    all_replacements = replacements + license_replacements

    # Find all .md files in the project
    md_files = find_all_md_files(ROOT)
    files_changed = 0

    for filepath in md_files:
        changes = replace_in_file(filepath, all_replacements)
        if changes > 0:
            relpath = os.path.relpath(filepath, ROOT)
            print(f"  Updated: {relpath} ({changes} replacements)")
            files_changed += 1

    print(f"\n  Updated {files_changed} files")

    # Step 3: Also update .py and .yml files
    print("\n--- Step 3: Updating .py and .yml files ---")
    for dirpath, dirnames, filenames in os.walk(ROOT):
        if ".git" in dirpath:
            continue
        for filename in filenames:
            if filename.endswith((".py", ".yml", ".yaml")):
                filepath = os.path.join(dirpath, filename)
                changes = replace_in_file(filepath, all_replacements)
                if changes > 0:
                    relpath = os.path.relpath(filepath, ROOT)
                    print(f"  Updated: {relpath} ({changes} replacements)")
                    files_changed += 1

    # Step 4: Summary
    print("\n" + "=" * 60)
    print("SUMMARY")
    print("=" * 60)
    print(f"  Directories renamed: {renamed}")
    print(f"  Files updated: {files_changed}")
    print(f"  Replacements applied: {len(RENAME_MAP)} name mappings + license fixes")
    print("\nNext steps:")
    print("  1. Review changes with: git diff --stat")
    print("  2. Verify with: git status")
    print("  3. Commit with: git commit -m 'chore: rename erpnext-* -> frappe-* (v2.0)'")


if __name__ == "__main__":
    main()
