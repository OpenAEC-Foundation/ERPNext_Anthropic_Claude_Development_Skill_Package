#!/usr/bin/env python3
"""
Package a skill folder into a .skill file (tar.gz archive).
Based on Anthropic skill packaging conventions.
"""

import os
import sys
import tarfile
import tempfile
import shutil

def package_skill(skill_path, output_dir):
    """Package a skill folder into a .skill file."""
    skill_path = os.path.abspath(skill_path)
    skill_name = os.path.basename(skill_path)
    output_dir = os.path.abspath(output_dir)
    
    # Verify SKILL.md exists
    skill_md = os.path.join(skill_path, "SKILL.md")
    if not os.path.exists(skill_md):
        raise FileNotFoundError(f"SKILL.md not found in {skill_path}")
    
    # Create output directory if needed
    os.makedirs(output_dir, exist_ok=True)
    
    # Output file
    output_file = os.path.join(output_dir, f"{skill_name}.skill")
    
    # Create tar.gz archive
    with tarfile.open(output_file, "w:gz") as tar:
        # Add SKILL.md
        tar.add(skill_md, arcname="SKILL.md")
        
        # Add references/ if exists
        refs_dir = os.path.join(skill_path, "references")
        if os.path.isdir(refs_dir):
            for root, dirs, files in os.walk(refs_dir):
                for file in files:
                    file_path = os.path.join(root, file)
                    arcname = os.path.relpath(file_path, skill_path)
                    tar.add(file_path, arcname=arcname)
    
    return output_file

def main():
    if len(sys.argv) < 3:
        print("Usage: python package_skill.py <skill_folder> <output_dir>")
        sys.exit(1)
    
    skill_path = sys.argv[1]
    output_dir = sys.argv[2]
    
    if not os.path.isdir(skill_path):
        print(f"Error: {skill_path} is not a directory")
        sys.exit(1)
    
    try:
        output_file = package_skill(skill_path, output_dir)
        print(f"✅ Packaged: {output_file}")
        
        # Show file size
        size = os.path.getsize(output_file)
        print(f"   Size: {size:,} bytes")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
