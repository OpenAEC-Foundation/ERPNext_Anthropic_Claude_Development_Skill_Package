# Skills Source Files

This directory contains the **unpacked** versions of all skill packages for easy browsing on GitHub.

## Directory Structure

```
source/
├── erpnext-syntax-clientscripts/
│   ├── NL/
│   │   ├── SKILL.md
│   │   └── references/
│   └── EN/
│       ├── SKILL.md
│       └── references/
├── erpnext-syntax-serverscripts/
│   ├── NL/ ...
│   └── EN/ ...
├── erpnext-syntax-controllers/
│   ├── NL/ ...
│   └── EN/ ...
├── erpnext-syntax-hooks/
│   ├── NL/ ...
│   └── EN/ ...
└── erpnext-syntax-whitelisted/
    ├── NL/ ...
    └── EN/ ...
```

## Quick Links

### Client Scripts
- [SKILL.md (NL)](erpnext-syntax-clientscripts/NL/SKILL.md)
- [SKILL.md (EN)](erpnext-syntax-clientscripts/EN/SKILL.md)

### Server Scripts
- [SKILL.md (NL)](erpnext-syntax-serverscripts/NL/SKILL.md)
- [SKILL.md (EN)](erpnext-syntax-serverscripts/EN/SKILL.md)

### Document Controllers
- [SKILL.md (NL)](erpnext-syntax-controllers/NL/SKILL.md)
- [SKILL.md (EN)](erpnext-syntax-controllers/EN/SKILL.md)

### Hooks.py Configuration
- [SKILL.md (NL)](erpnext-syntax-hooks/NL/SKILL.md)
- [SKILL.md (EN)](erpnext-syntax-hooks/EN/SKILL.md)

### Whitelisted API Methods
- [SKILL.md (NL)](erpnext-syntax-whitelisted/NL/SKILL.md)
- [SKILL.md (EN)](erpnext-syntax-whitelisted/EN/SKILL.md)

## Using Skills

### Option 1: Download .skill Package
Go to [skills/syntax/](../syntax/) and download the `.skill` file you need. Upload it to your Claude.ai project.

### Option 2: Copy Source Files
Copy the entire skill folder (e.g., `erpnext-syntax-clientscripts/EN/`) to your project.

## File Contents

Each skill contains:

| File | Purpose |
|------|---------|
| `SKILL.md` | Main skill file with quick reference, decision trees, and essential patterns |
| `references/*.md` | Detailed documentation (methods, events, examples, anti-patterns) |

## Version Compatibility

All skills are compatible with:
- ✅ ERPNext v14
- ✅ ERPNext v15
- 🔄 ERPNext v16 (review pending)
