# ERPNext Skills Package - Index

> Complete collection of 28 deterministic skills for generating flawless ERPNext/Frappe code.

---

## Package Overview

| Category | Skills | Description |
|----------|:------:|-------------|
| [Syntax](#syntax-skills) | 8 | Language patterns and API syntax |
| [Core](#core-skills) | 3 | Database, Permissions, API fundamentals |
| [Implementation](#implementation-skills) | 8 | Step-by-step development workflows |
| [Error Handling](#error-handling-skills) | 7 | Robust error handling patterns |
| [Agents](#agent-skills) | 2 | Intelligent code interpretation & validation |
| **Total** | **28** | |

**Compatibility**: Frappe/ERPNext v14, v15, v16

---

## Syntax Skills

Foundation skills that define HOW to write code.

| Skill | Description | Key Topics |
|-------|-------------|------------|
| `frappe-syntax-clientscripts` | Client-side JavaScript patterns | frappe.ui.form, triggers, field manipulation |
| `frappe-syntax-serverscripts` | Server Script sandbox patterns | Restricted Python, frappe namespace, doc events |
| `frappe-syntax-controllers` | Document Controller patterns | Lifecycle hooks, autoname, UUID (v16), flags |
| `frappe-syntax-hooks` | hooks.py configuration | doc_events, override_doctype_class, scheduler |
| `frappe-syntax-whitelisted` | @frappe.whitelist() methods | API endpoints, permissions, async patterns |
| `frappe-syntax-jinja` | Jinja templating patterns | Print formats, web templates, filters |
| `frappe-syntax-scheduler` | Scheduled jobs patterns | Cron syntax, background jobs, tick intervals |
| `frappe-syntax-customapp` | Custom app structure | Module creation, fixtures, patches |

---

## Core Skills

Cross-cutting concerns that apply to all development.

| Skill | Description | Key Topics |
|-------|-------------|------------|
| `frappe-core-database` | Database operations | frappe.db API, transactions, SQL patterns |
| `frappe-core-permissions` | Permission system | Roles, user permissions, data masking (v16) |
| `frappe-core-api` | API design patterns | REST, RPC, webhooks, authentication |

---

## Implementation Skills

Step-by-step workflows for common development tasks.

| Skill | Description | When to Use |
|-------|-------------|-------------|
| `frappe-impl-clientscripts` | Client Script workflows | Form customization, UX enhancement |
| `frappe-impl-serverscripts` | Server Script workflows | Quick server-side logic without custom app |
| `frappe-impl-controllers` | Controller workflows | Full DocType customization |
| `frappe-impl-hooks` | hooks.py workflows | Extending existing DocTypes |
| `frappe-impl-whitelisted` | API endpoint workflows | Building custom API endpoints |
| `frappe-impl-jinja` | Template workflows | Print formats, emails, reports |
| `frappe-impl-scheduler` | Scheduled job workflows | Background processing, automation |
| `frappe-impl-customapp` | Custom app workflows | Building complete Frappe apps |

---

## Error Handling Skills

Robust error handling patterns for production code.

| Skill | Description | Covers |
|-------|-------------|--------|
| `frappe-errors-clientscripts` | Client-side error handling | JavaScript errors, API call failures |
| `frappe-errors-serverscripts` | Server Script error handling | Sandbox limitations, exception handling |
| `frappe-errors-controllers` | Controller error handling | Validation, transaction failures |
| `frappe-errors-hooks` | hooks.py error handling | Hook failures, event handling |
| `frappe-errors-database` | Database error handling | Deadlocks, constraints, transactions |
| `frappe-errors-permissions` | Permission error handling | Access denied, graceful degradation |
| `frappe-errors-api` | API error handling | HTTP errors, response formatting |

---

## Agent Skills

Intelligent skills that orchestrate other skills.

| Skill | Description | Use Case |
|-------|-------------|----------|
| `frappe-agent-interpreter` | Requirements → Technical specs | Vague requests like "make invoice auto-calculate" |
| `frappe-agent-validator` | Code validation against all skills | Verify code before deployment |

---

## Quick Selection Guide

```
What do you need to build?
│
├─► Form behavior / UX
│   └─► syntax-clientscripts + impl-clientscripts + errors-clientscripts
│
├─► Quick server logic (no custom app)
│   └─► syntax-serverscripts + impl-serverscripts + errors-serverscripts
│
├─► Full DocType customization
│   └─► syntax-controllers + impl-controllers + errors-controllers
│       + database + permissions
│
├─► Extend existing ERPNext DocType
│   └─► syntax-hooks + impl-hooks + errors-hooks
│
├─► Build API endpoints
│   └─► syntax-whitelisted + impl-whitelisted + api-patterns + errors-api
│
├─► Print formats / Templates
│   └─► syntax-jinja + impl-jinja
│
├─► Scheduled automation
│   └─► syntax-scheduler + impl-scheduler + syntax-hooks
│
├─► Complete custom app
│   └─► syntax-customapp + impl-customapp + (all relevant skills)
│
└─► Don't know where to start?
    └─► code-interpreter (will recommend skills)
```

---

## Version-Specific Features

### v14 Only
- Basic Server Scripts
- Standard permissions

### v15+
- Type annotations
- `before_discard` / `on_discard` hooks
- `Desk User` role

### v16+
- **UUID autoname** - Globally unique document IDs
- **Data Masking** - Field-level data protection
- Chrome PDF rendering
- 60-second scheduler tick (was 4 minutes)
- `extend_doctype_class` hook

---

## Related Documentation

| Document | Description |
|----------|-------------|
| [DEPENDENCIES.md](docs/DEPENDENCIES.md) | Skill dependency matrix |
| [INSTALL.md](INSTALL.md) | Installation instructions |
| [ROADMAP.md](ROADMAP.md) | Project status and history |
| [LESSONS.md](LESSONS.md) | Technical discoveries |

---

## Contributing

This package is maintained by OpenAEC Foundation. For issues or contributions, see the GitHub repository.

---

*ERPNext Skills Package v1.0 | Last updated: 2026-01-18*
