# ERPNext Skills Project - Memory & Context Export

> Export date: January 2025
> Project: ERPNext Anthropic Claude Development Skill Package

## Project Purpose & Context

This project is dedicated to building a comprehensive **ERPNext/Frappe Skills Package** - a collection of 56 deterministic skills and agents that enable Claude AI instances to generate flawless ERPNext/Frappe code.

### Core Principles

1. **Bilingual Documentation**: All content in Dutch (NL) and English (EN)
2. **Version Explicit**: Clear compatibility for ERPNext v14 and v15
3. **Research-First**: Verify against official documentation before coding
4. **One-Shot Execution**: No proof-of-concepts, direct production quality
5. **Deterministic Output**: Only verified facts, exact syntax

## Project Structure

The project follows a 7-phase masterplan:

| Phase | Focus | Status |
|-------|-------|--------|
| 1 | Foundational Research | ✅ Complete |
| 2 | Syntax Skills | 🔄 In Progress |
| 3 | Core Skills | Planned |
| 4 | Implementation Skills | Planned |
| 5 | Error Handling Skills | Planned |
| 6 | Intelligent Agents | Planned |
| 7 | Final Packaging | Planned |

## Key Technical Discoveries

### Frappe Server Script Sandbox Limitations

**Critical**: All import statements are blocked in Server Scripts for security. Use Frappe's pre-loaded namespace instead:

```python
# ❌ WRONG
from frappe.utils import nowdate

# ✅ CORRECT  
date = frappe.utils.nowdate()
```

### Version Differences (v14 vs v15)

- Scheduler tick: 4 min (v14) → 60 sec (v15)
- `job_name` deprecated → use `job_id`
- New hooks in v15: `before_discard`, `on_discard`
- `on_change` triggers after every modification including `db_set()`

### hooks.py Resolution

- "Last writer wins" principle for conflicting hooks
- `scheduler_events` changes require `bench migrate`

## Phase Split Criteria

Phases should be split when:
- More than 700 research lines
- More than 5 reference files required
- More than 8-10 sections in skill

## Research Sources (Priority Order)

1. Official Frappe documentation (docs.frappe.io)
2. GitHub source code (github.com/frappe/frappe)
3. Community input (2023+ only)

## Completed Research Documents

- Client Scripts
- Server Scripts
- Document Controllers
- Document Hooks
- Whitelisted Methods
- Jinja Templates
- Scheduler/Background Jobs
- Custom App Structure
- Custom App Data Management

## Skills Completed

- erpnext-syntax-clientscripts (NL + EN)
- erpnext-syntax-serverscripts (NL + EN)

## Communication Preferences

- **Language**: Dutch for communication, English for code comments
- **Format**: Skills must stay under 500 lines
- **Validation**: YAML frontmatter compliance required

---

*This document serves as a memory export for project continuity across Claude sessions.*
