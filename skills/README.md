# ERPNext Skills Packages

This directory contains the compiled skill packages (`.skill` files) that can be uploaded to Claude.ai projects.

## Available Skills

### Syntax Skills (`skills/syntax/`)

These skills provide exact syntax references for ERPNext/Frappe development:

| Skill | NL | EN | Description |
|-------|----|----|-------------|
| **clientscripts** | ✅ | ✅ | Client-side JavaScript: form events, field manipulation, frappe.call |
| **serverscripts** | ✅ | ✅ | Server Scripts: document events, API endpoints, scheduler events |
| **hooks** | ✅ | ✅ | hooks.py configuration: doc_events, scheduler, fixtures, permissions |
| **whitelisted** | ✅ | ✅ | Whitelisted API methods: @frappe.whitelist(), permissions, responses |

### Planned Skills

| Category | Skills | Status |
|----------|--------|--------|
| **Syntax** | controllers, jinja, scheduler, customapp | 🔜 In development |
| **Implementation** | impl-clientscripts, impl-serverscripts, etc. | 📋 Planned |
| **Error Handling** | errors-clientscripts, errors-serverscripts, etc. | 📋 Planned |
| **Agents** | code-generator, debugger | 📋 Planned |

## How to Use

### In Claude.ai

1. Download the `.skill` file you need
2. Go to your Claude.ai project
3. Upload the skill file to Project Knowledge
4. Claude will automatically use the skill when generating ERPNext code

### File Format

Each `.skill` file is a ZIP archive containing:
- `SKILL.md` - Main instructions and quick reference
- `references/` - Detailed reference documentation
  - `events.md` - Event listings
  - `methods.md` - Method signatures
  - `examples.md` - Working code examples
  - `anti-patterns.md` - Common mistakes to avoid

## Language Versions

All skills are available in two languages:
- **NL** - Dutch (Nederlands)
- **EN** - English

Both versions contain identical technical content, only the explanatory text differs.

## Version Compatibility

All skills document compatibility with:
- ERPNext v14
- ERPNext v15

Version-specific differences are clearly marked in the documentation.
