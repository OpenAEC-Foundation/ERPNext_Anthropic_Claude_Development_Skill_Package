# Contributing to ERPNext Claude Skills Package

Thank you for your interest in contributing! This project provides deterministic skills for Claude to generate flawless ERPNext/Frappe code.

## How to Contribute

### Reporting Issues

- **Bug reports**: Use the bug report template
- **Feature requests**: Use the feature request template
- **Questions**: Open a discussion or issue

### Submitting Changes

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/your-feature`)
3. Make your changes
4. Test your changes (see Testing below)
5. Commit with clear messages (`git commit -m "Add: description"`)
6. Push to your fork (`git push origin feature/your-feature`)
7. Open a Pull Request

## Skill Development Guidelines

### Structure

Every skill must follow this structure:

```
skill-name/
├── SKILL.md           # Main skill file (<500 lines)
└── references/
    ├── methods.md     # Detailed method documentation
    ├── examples.md    # Working code examples
    └── anti-patterns.md  # Common mistakes to avoid
```

### SKILL.md Requirements

- Must be in skill folder root (not in subdirectory)
- Maximum 500 lines
- Must include YAML frontmatter with name, description, version
- English language only
- Only verified facts from official Frappe documentation

### Content Standards

**DO:**
- Verify all code against official docs.frappe.io
- Include version-specific information (v14/v15/v16)
- Provide working examples tested in actual ERPNext
- Document anti-patterns with explanations

**DON'T:**
- Make assumptions about API behavior
- Copy from outdated community posts
- Use imports in Server Script examples (sandbox restriction)

### Critical Technical Note

Server Scripts run in a RestrictedPython sandbox. Never use imports:

```python
# ❌ WRONG - Will fail
from frappe.utils import nowdate

# ✅ CORRECT - Use namespace
date = frappe.utils.nowdate()
```

## Testing

Before submitting:

1. Validate SKILL.md format:
   ```bash
   python tools/quick_validate.py skills/source/your-skill/
   ```

2. Check line count:
   ```bash
   wc -l skills/source/your-skill/SKILL.md  # Must be <500
   ```

3. Verify all code examples work in ERPNext

## Commit Message Format

```
Type: Short description

Types:
- Add: New feature or skill
- Fix: Bug fix
- Update: Improvement to existing content
- Docs: Documentation only
- Cleanup: Code cleanup, no functional change
```

## Questions?

Open an issue or check existing documentation in the `docs/` folder.
