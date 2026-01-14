# ERPNext Skills

This directory contains all skill packages for the ERPNext/Frappe development skill package.

## Directory Structure

```
skills/
├── README.md          (this file)
├── syntax/            Packaged .skill files (ready to use)
└── source/            Unpacked source files (for browsing)
```

## Quick Start

### Using Packaged Skills (.skill files)

1. Go to [`syntax/`](syntax/)
2. Download the `.skill` file you need (e.g., `erpnext-syntax-clientscripts-EN.skill`)
3. Upload to your Claude.ai project as project knowledge

### Browsing Skill Contents

Want to see what's inside a skill before downloading?

👉 Go to [`source/`](source/) to browse all SKILL.md files and reference documentation directly on GitHub.

## Available Skills

| Skill | Description | Package (NL) | Package (EN) |
|-------|-------------|--------------|--------------|
| **Client Scripts** | JavaScript for form interactions | [NL](syntax/erpnext-syntax-clientscripts-NL.skill) | [EN](syntax/erpnext-syntax-clientscripts-EN.skill) |
| **Server Scripts** | Python sandbox scripts | [NL](syntax/erpnext-syntax-serverscripts-NL.skill) | [EN](syntax/erpnext-syntax-serverscripts-EN.skill) |
| **Controllers** | Document Controllers (Python) | [NL](syntax/erpnext-syntax-controllers-NL.skill) | [EN](syntax/erpnext-syntax-controllers-EN.skill) |
| **Hooks** | hooks.py configuration | [NL](syntax/erpnext-syntax-hooks-NL.skill) | [EN](syntax/erpnext-syntax-hooks-EN.skill) |
| **Whitelisted** | API endpoint methods | [NL](syntax/erpnext-syntax-whitelisted-NL.skill) | [EN](syntax/erpnext-syntax-whitelisted-EN.skill) |

## Coming Soon

- `erpnext-syntax-jinja` - Jinja Templates
- `erpnext-syntax-scheduler` - Background Jobs
- `erpnext-syntax-customapp` - Custom App Development

## Skill Package Format

Each `.skill` file is a ZIP archive containing:

```
skill-name/
├── SKILL.md           Main skill file (<500 lines)
└── references/        Detailed documentation
    ├── methods.md
    ├── events.md
    ├── examples.md
    └── anti-patterns.md
```

## Version Compatibility

- ✅ ERPNext v14
- ✅ ERPNext v15
- 🔄 ERPNext v16 (review in progress)
