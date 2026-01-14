# ERPNext Anthropic Claude Development Skill Package

> **A comprehensive skills package enabling Claude AI to generate flawless ERPNext/Frappe code**

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![ERPNext](https://img.shields.io/badge/ERPNext-v14%20%7C%20v15-blue)](https://erpnext.com)
[![Frappe](https://img.shields.io/badge/Frappe-Framework-green)](https://frappeframework.com)

## 🎯 Project Overview

This project contains a collection of **56 deterministic skills and agents** that enable Claude AI instances to generate accurate, production-ready ERPNext/Frappe code. The skills package follows Anthropic's official skill-creator conventions and provides comprehensive coverage of all major ERPNext/Frappe development mechanisms.

### Key Features

- **Bilingual Documentation**: All skills available in Dutch (NL) and English (EN)
- **Version-Specific**: Explicit compatibility documentation for ERPNext v14 and v15
- **Deterministic Output**: Skills produce consistent, verified code patterns
- **One-Shot Execution**: Designed for direct, production-quality code generation without iterations

## 📚 Covered Topics

The skills package covers all major ERPNext/Frappe development areas:

| Category | Topics |
|----------|--------|
| **Client-Side** | Client Scripts, Form Events, List Events, Field Manipulation |
| **Server-Side** | Server Scripts, Document Controllers, Whitelisted Methods |
| **Configuration** | hooks.py, Fixtures, Permissions, Scheduler Events |
| **Templates** | Jinja Templates, Print Formats, Web Templates |
| **Background Jobs** | Scheduler Jobs, Background Workers, Queues |
| **Custom Apps** | App Structure, Data Management, Migrations |

## 📁 Repository Structure

```
├── docs/
│   ├── masterplan/           # Project masterplan and phase documentation
│   ├── research/             # Research documents for each topic
│   └── reference/            # Quick reference documentation
├── skills/
│   ├── syntax/               # Syntax skills (correct code patterns)
│   ├── implementation/       # Implementation skills (best practices)
│   ├── error-handling/       # Error handling skills
│   └── agents/               # Intelligent agents for complex tasks
├── memory/                   # Project memory exports
└── README.md
```

## 🚀 Getting Started

### For Claude.ai Users

1. Download the relevant skill files from the `skills/` directory
2. Upload them to your Claude.ai project as project knowledge
3. The skills will automatically guide Claude in generating ERPNext code

### For Developers

1. Clone this repository
2. Review the research documents in `docs/research/` for comprehensive API documentation
3. Use the reference files in `docs/reference/` for quick lookups

## 📖 Documentation

### Core Documents

| Document | Description |
|----------|-------------|
| `erpnext-skills-masterplan-v2.md` | Complete project masterplan with all phases |
| `erpnext-vooronderzoek.md` | Initial research and findings |
| `SKILL.md` | Main skill definition following Anthropic conventions |

### Research Documents

Comprehensive research documents are available for:

- Client Scripts (`research-client-scripts.md`)
- Server Scripts (`research-server-scripts.md`)
- Document Controllers (`research-document-controllers.md`)
- Document Hooks (`research-document-hooks.md`)
- Whitelisted Methods (`research-whitelisted-methods.md`)
- Jinja Templates (`research-jinja-templates.md`)
- Scheduler/Background Jobs (`research-scheduler-background-jobs.md`)
- Custom App Structure (`research-custom-app-structure.md`)
- Custom App Data Management (`research-customapp-datamanagement.md`)

## ⚠️ Important Notes

### Frappe Server Script Sandbox Limitations

A critical discovery: Frappe Server Scripts run in a sandboxed environment where **all import statements are blocked** for security reasons. Instead, use Frappe's pre-loaded namespace:

```python
# ❌ WRONG - Will fail in Server Scripts
from frappe.utils import nowdate
date = nowdate()

# ✅ CORRECT - Use pre-loaded namespace
date = frappe.utils.nowdate()
```

### Version Differences (v14 vs v15)

Key differences between Frappe v14 and v15:
- Scheduler tick interval: 4 minutes (v14) → 60 seconds (v15)
- `job_name` parameter deprecated in favor of `job_id`
- New hooks: `before_discard`, `on_discard` (v15+)
- `on_change` hook triggers after every modification including `db_set()`

## 🤝 Contributing

Contributions are welcome! Please ensure:

1. All code examples are tested on both ERPNext v14 and v15
2. Documentation includes both Dutch and English versions
3. Skills follow the Anthropic skill-creator conventions
4. Changes are verified against official Frappe documentation

## 📜 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- [Frappe Framework](https://frappeframework.com) - The foundation of ERPNext
- [ERPNext](https://erpnext.com) - Open source ERP
- [Anthropic](https://anthropic.com) - Claude AI and skill-creator framework
- [OpenAEC Foundation](https://github.com/OpenAEC-Foundation) - Project maintainers

---

**Note**: This skills package is designed for use with Anthropic's Claude AI. The skills provide deterministic guidance for code generation and should be used in conjunction with official Frappe/ERPNext documentation.
