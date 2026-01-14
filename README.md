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

---

## 📘 Way of Work (Methodology)

This project also serves as a **template methodology** for developing AI skill packages for any open source project.

👉 **[Read the Way of Work document](WAY_OF_WORK.md)** to learn our 7-phase methodology:

1. **Deep Research** - Comprehensive exploration of the target technology
2. **Preliminary Research Document** - Consolidate findings into a reference
3. **Requirements Definition** - Define what the skills must achieve
4. **Detailed Masterplan** - Create phased execution plan with prompts
5. **Topic-Specific Research** - Deep-dive per skill topic
6. **Skill Creation** - Transform research into deterministic skills
7. **Validation & Version Control** - Quality assurance and GitHub sync

This methodology can be applied to create skill packages for any framework or technology.

---

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

---

## 📁 Repository Structure

```
├── WAY_OF_WORK.md            # Methodology guide (start here!)
├── README.md
├── SKILL.md
├── docs/
│   ├── masterplan/           # Project masterplan and amendments
│   ├── research/             # Research documents per topic
│   └── reference/            # Quick reference documentation
├── skills/
│   ├── syntax/               # Syntax skills (.skill packages)
│   ├── implementation/       # Implementation skills (planned)
│   ├── error-handling/       # Error handling skills (planned)
│   └── agents/               # Intelligent agents (planned)
└── memory/                   # Project memory exports
```

---

## 🚀 Getting Started

### For Claude.ai Users

1. Download the relevant skill files from the `skills/` directory
2. Upload them to your Claude.ai project as project knowledge
3. The skills will automatically guide Claude in generating ERPNext code

### For Developers Creating Their Own Skill Package

1. Read the [Way of Work](WAY_OF_WORK.md) methodology
2. Study how we structured our research documents in `docs/research/`
3. Use our masterplan as a template for your own project
4. Follow the 7-phase methodology for your target technology

---

## 📖 Documentation

### Methodology & Planning

| Document | Description |
|----------|-------------|
| [`WAY_OF_WORK.md`](WAY_OF_WORK.md) | **Start here!** Complete methodology guide |
| [`docs/masterplan/erpnext-skills-masterplan-v2.md`](docs/masterplan/erpnext-skills-masterplan-v2.md) | Detailed project masterplan |
| [`docs/masterplan/erpnext-vooronderzoek.md`](docs/masterplan/erpnext-vooronderzoek.md) | Preliminary research document |

### Research Documents

Comprehensive research documents are available in `docs/research/`:

- Client Scripts, Server Scripts, Document Controllers
- Document Hooks, Whitelisted Methods, Jinja Templates
- Scheduler/Background Jobs, Custom App Structure & Data Management

---

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

Key differences documented in our skills:
- Scheduler tick interval: 4 minutes (v14) → 60 seconds (v15)
- `job_name` parameter deprecated in favor of `job_id`
- New hooks: `before_discard`, `on_discard` (v15+)
- `on_change` hook triggers after every modification including `db_set()`

---

## 🤝 Contributing

Contributions are welcome! Please ensure:

1. All code examples are tested on both ERPNext v14 and v15
2. Documentation includes both Dutch and English versions
3. Skills follow the Anthropic skill-creator conventions
4. Follow the [Way of Work](WAY_OF_WORK.md) methodology
5. Changes are verified against official Frappe documentation

---

## 📜 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## 🙏 Acknowledgments

- [Frappe Framework](https://frappeframework.com) - The foundation of ERPNext
- [ERPNext](https://erpnext.com) - Open source ERP
- [Anthropic](https://anthropic.com) - Claude AI and skill-creator framework
- [OpenAEC Foundation](https://github.com/OpenAEC-Foundation) - Project maintainers

---

**Note**: This project demonstrates a reusable methodology for creating AI skill packages. The [Way of Work](WAY_OF_WORK.md) can be applied to any open source project where you want to enable Claude to generate correct code.
