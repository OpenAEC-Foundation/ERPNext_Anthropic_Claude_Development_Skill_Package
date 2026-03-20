---
name: frappe-agent-validator
description: >
  Use when reviewing or validating ERPNext/Frappe code against best practices
  and common pitfalls. Checks generated code before deployment, validates
  code quality, and catches errors. Keywords: review code, check script,
  validate deployment, find bugs, check errors, code quality.
license: MIT
compatibility: "Claude Code, Claude.ai Projects, Claude API. Frappe v14-v16."
metadata:
  author: OpenAEC-Foundation
  version: "2.0"
---

# ERPNext Code Validator Agent

This agent validates ERPNext/Frappe code against established patterns, common pitfalls, and version compatibility requirements.

**Purpose**: Catch errors BEFORE deployment, not after

## When to Use This Agent

```
┌─────────────────────────────────────────────────────────────────────┐
│ CODE VALIDATION TRIGGERS                                            │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│ ► Code has been generated and needs review                          │
│   "Check this Server Script before I save it"                       │
│   └── USE THIS AGENT                                                │
│                                                                     │
│ ► Code is causing errors                                            │
│   "Why isn't this working?"                                         │
│   └── USE THIS AGENT                                                │
│                                                                     │
│ ► Pre-deployment validation                                         │
│   "Is this production-ready?"                                       │
│   └── USE THIS AGENT                                                │
│                                                                     │
│ ► Code review for best practices                                    │
│   "Can this be improved?"                                           │
│   └── USE THIS AGENT                                                │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
```

## Validation Workflow

```
┌─────────────────────────────────────────────────────────────────────┐
│                    CODE VALIDATOR WORKFLOW                          │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│  STEP 1: IDENTIFY CODE TYPE                                         │
│  ══════════════════════════                                         │
│  • Client Script (JavaScript)                                       │
│  • Server Script (Python sandbox)                                   │
│  • Controller (Python full)                                         │
│  • hooks.py configuration                                           │
│  • Jinja template                                                   │
│  • Whitelisted method                                               │
│                                                                     │
│  STEP 2: RUN TYPE-SPECIFIC CHECKS                                   │
│  ═════════════════════════════════                                  │
│  • Apply checklist for identified code type                         │
│  • Check syntax patterns                                            │
│  • Verify API usage                                                 │
│                                                                     │
│  STEP 3: CHECK UNIVERSAL RULES                                      │
│  ══════════════════════════════                                     │
│  • Error handling present                                           │
│  • User feedback appropriate                                        │
│  • Security considerations                                          │
│  • Performance implications                                         │
│                                                                     │
│  STEP 4: VERIFY VERSION COMPATIBILITY                               │
│  ════════════════════════════════════                               │
│  • v14/v15/v16 specific features                                    │
│  • Deprecated patterns                                              │
│  • Version-specific behaviors                                       │
│                                                                     │
│  STEP 5: GENERATE VALIDATION REPORT                                 │
│  ══════════════════════════════════                                 │
│  • Critical errors (must fix)                                       │
│  • Warnings (should fix)                                            │
│  • Suggestions (nice to have)                                       │
│  • Corrected code (if errors found)                                 │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
```

→ See [references/workflow.md](references/workflow.md) for detailed validation steps.

## Critical Checks by Code Type

### Server Script Checks

```
┌─────────────────────────────────────────────────────────────────────┐
│ ⚠️  SERVER SCRIPT CRITICAL CHECKS                                  │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│ [FATAL] Import statements                                           │
│ ═══════════════════════════                                         │
│ ❌ import json                    → Use frappe.parse_json()         │
│ ❌ from frappe.utils import X     → Use frappe.utils.X()            │
│ ❌ import requests                → IMPOSSIBLE in Server Script     │
│                                                                     │
│ [FATAL] Undefined variables                                         │
│ ════════════════════════════                                        │
│ ❌ self.field                     → Use doc.field                   │
│ ❌ document.field                 → Use doc.field                   │
│                                                                     │
│ [FATAL] Wrong event handling                                        │
│ ═══════════════════════════════                                     │
│ ❌ try/except for validation      → Just frappe.throw()             │
│                                                                     │
│ [ERROR] Event name mismatch                                         │
│ ═══════════════════════════                                         │
│ ❌ Event "Before Save" code in "After Save" script                  │
│                                                                     │
│ [WARNING] Missing validation                                        │
│ ═══════════════════════════════                                     │
│ ⚠️  No null/empty checks before operations                          │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
```

### Client Script Checks

```
┌─────────────────────────────────────────────────────────────────────┐
│ CLIENT SCRIPT CRITICAL CHECKS                                       │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│ [FATAL] Wrong API usage                                             │
│ ═════════════════════════                                           │
│ ❌ frappe.db.get_value()          → Server-side only!               │
│ ❌ frappe.get_doc()               → Server-side only!               │
│ ✓  frappe.call() for server data                                    │
│                                                                     │
│ [FATAL] Missing async handling                                      │
│ ══════════════════════════════                                      │
│ ❌ let result = frappe.call()     → Returns undefined               │
│ ✓  frappe.call({callback: fn})   → Use callback                     │
│ ✓  await frappe.call({async:false}) → Or async/await               │
│                                                                     │
│ [ERROR] Field refresh issues                                        │
│ ════════════════════════════                                        │
│ ❌ frm.set_value() without refresh                                  │
│ ✓  frm.set_value() then frm.refresh_field()                        │
│                                                                     │
│ [WARNING] Form state checks                                         │
│ ═══════════════════════════                                         │
│ ⚠️  Not checking frm.doc.__islocal for new docs                     │
│ ⚠️  Not checking frm.doc.docstatus for submitted docs               │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
```

### Controller Checks

```
┌─────────────────────────────────────────────────────────────────────┐
│ CONTROLLER CRITICAL CHECKS                                          │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│ [FATAL] Wrong lifecycle usage                                       │
│ ═════════════════════════════                                       │
│ ❌ Modifying self.field in on_update → Changes NOT saved!           │
│ ✓  Use frappe.db.set_value() in on_update                          │
│                                                                     │
│ [FATAL] Missing super() call                                        │
│ ════════════════════════════                                        │
│ ❌ def validate(self): pass        → Breaks parent validation       │
│ ✓  def validate(self): super().validate()                          │
│                                                                     │
│ [ERROR] Transaction assumptions                                     │
│ ═══════════════════════════════                                     │
│ ❌ Assuming rollback on error in on_update                          │
│    (only validate and before_* roll back on error)                 │
│                                                                     │
│ [ERROR] Circular save                                               │
│ ══════════════════════                                              │
│ ❌ self.save() inside lifecycle hooks                               │
│ ❌ doc.save() for same document in hooks                            │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
```

→ See [references/checklists.md](references/checklists.md) for complete checklists.

## Validation Report Format

```markdown
## Code Validation Report

### Code Type: [Server Script / Client Script / Controller / etc.]
### Target DocType: [DocType name]
### Event/Trigger: [Event name]

---

### 🔴 CRITICAL ERRORS (Must Fix)

| Line | Issue | Fix |
|------|-------|-----|
| 3 | Import statement in Server Script | Use frappe.utils.X() directly |

### 🟡 WARNINGS (Should Fix)

| Line | Issue | Recommendation |
|------|-------|----------------|
| 12 | No null check before .lower() | Add: if value: value.lower() |

### 🔵 SUGGESTIONS (Nice to Have)

| Line | Suggestion |
|------|------------|
| 8 | Consider using frappe.db.get_value for single field |

---

### Corrected Code

```python
# [Corrected version with all critical errors fixed]
```

### Version Compatibility

| Version | Status |
|---------|--------|
| v14 | ✅ Compatible |
| v15 | ✅ Compatible |
| v16 | ✅ Compatible |
```

## Universal Validation Rules

These apply to ALL code types:

### Security Checks

| Check | Severity | Description |
|-------|----------|-------------|
| SQL Injection | CRITICAL | Raw user input in SQL queries |
| Permission bypass | CRITICAL | Missing permission checks before operations |
| XSS vulnerability | HIGH | Unescaped user input in HTML |
| Sensitive data exposure | HIGH | Logging passwords/tokens |

### Error Handling Checks

| Check | Severity | Description |
|-------|----------|-------------|
| Silent failures | HIGH | Catching exceptions without handling |
| Missing user feedback | MEDIUM | Errors not communicated to user |
| Generic error messages | LOW | "An error occurred" without details |

### Performance Checks

| Check | Severity | Description |
|-------|----------|-------------|
| Query in loop | HIGH | frappe.db.* inside for loop |
| Unbounded query | MEDIUM | SELECT without LIMIT |
| Unnecessary get_doc | LOW | get_doc when get_value suffices |

→ See [references/examples.md](references/examples.md) for validation examples.

## Version-Specific Validations

### v16 Features (Fail on v14/v15)

```python
# These ONLY work on v16+
extend_doctype_class = {}  # hooks.py - v16 only
naming_rule = "UUID"       # DocType - v16 only
pdf_renderer = "chrome"    # Print Format - v16 only
```

### Deprecated Patterns (Warn)

```python
# DEPRECATED - still works but should update
frappe.bean()              # Use frappe.get_doc()
frappe.msgprint(raise_exception=True)  # Use frappe.throw()
job_name parameter         # Use job_id (v15+)
```

### Version-Specific Behaviors

| Behavior | v14 | v15/v16 |
|----------|-----|---------|
| Scheduler tick | 240s | 60s |
| Background job dedup | job_name | job_id |

## Quick Validation Commands

### Server Script Quick Check
1. ❌ Any `import` statements? → FATAL
2. ❌ Any `self.` references? → FATAL (use `doc.`)
3. ❌ Any `try/except`? → WARNING (usually wrong)
4. ✅ Uses `frappe.throw()` for validation errors? → GOOD
5. ✅ Uses `doc.field` for document access? → GOOD

### Client Script Quick Check
1. ❌ Any `frappe.db.*` calls? → FATAL (server-side only)
2. ❌ Any `frappe.get_doc()` calls? → FATAL (server-side only)
3. ❌ `frappe.call()` without callback? → FATAL (async issue)
4. ✅ Uses `frm.doc.field` for field access? → GOOD
5. ✅ Uses `frm.refresh_field()` after changes? → GOOD

### Controller Quick Check
1. ❌ Modifying `self.*` in `on_update`? → ERROR (won't save)
2. ❌ Missing `super().method()` calls? → WARNING
3. ❌ `self.save()` in lifecycle hook? → FATAL (circular)
4. ✅ Imports at top of file? → GOOD (controllers allow imports)
5. ✅ Error handling with try/except? → GOOD (controllers allow this)

## Integration with Other Skills

This validator uses knowledge from:

| Skill | What It Provides |
|-------|------------------|
| `frappe-syntax-*` | Correct syntax patterns |
| `frappe-impl-*` | Correct implementation patterns |
| `frappe-errors-*` | Error handling patterns |
| `frappe-core-database` | Query patterns and pitfalls |
| `frappe-core-permissions` | Permission check patterns |
| `frappe-core-api` | API response patterns |

## Validation Depth Levels

| Level | Checks | Use When |
|-------|--------|----------|
| Quick | Fatal errors only | Initial scan |
| Standard | + Warnings | Pre-deployment |
| Deep | + Suggestions + Optimization | Production review |

Default: **Standard** level for most validations.
