# ERPNext Anthropic Claude Development Skill Package

> **A comprehensive skills package enabling Claude AI to generate flawless ERPNext/Frappe code**

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![ERPNext](https://img.shields.io/badge/ERPNext-v14%20%7C%20v15-blue)](https://erpnext.com)
[![Frappe](https://img.shields.io/badge/Frappe-Framework-green)](https://frappeframework.com)

## 🎯 Project Overview

This project contains a collection of **28 deterministic skills and agents** that enable Claude AI instances to generate accurate, production-ready ERPNext/Frappe code. The skills package follows Anthropic's official skill-creator conventions and provides comprehensive coverage of all major ERPNext/Frappe development mechanisms.

### Key Features

- **Anthropic-Conformant**: Follows official skill-creator structure and tooling
- **Version-Specific**: Explicit compatibility documentation for ERPNext v14 and v15
- **Deterministic Output**: Skills produce consistent, verified code patterns
- **One-Shot Execution**: Designed for direct, production-quality code generation
- **Research-First**: Every skill backed by verified research documentation

---

## 🎓 Template Methodology

**This project serves as a template for developing Claude skill packages for ANY open source project.**

### What You Can Learn Here

1. **How to structure Claude skills** following Anthropic's conventions
2. **Research-first methodology** for creating deterministic AI outputs
3. **Phase-based development** with clear checkpoints and validation
4. **Lessons learned** from real-world skill development

### Key Documents

| Document | Purpose |
|----------|---------|
| [WAY_OF_WORK.md](WAY_OF_WORK.md) | Complete 7-phase methodology |
| [LESSONS_LEARNED.md](LESSONS_LEARNED.md) | Technical & process insights |
| [ROADMAP.md](ROADMAP.md) | Project status & planning |
| [docs/masterplan/](docs/masterplan/) | Original vision + amendments |

### The Methodology in Brief

```
Phase 1: Deep Research → Understand the technology deeply
Phase 2: Preliminary Research → Document findings
Phase 3: Requirements → Define skill scope
Phase 4: Masterplan → Create execution plan
Phase 5: Topic Research → Deep-dive per skill
Phase 6: Skill Creation → Transform research into skills
Phase 7: Validation → Test with Anthropic tooling
```

---

## 📚 Covered Topics

The skills package covers all major ERPNext/Frappe development areas:

| Category | Skills | Status |
|----------|:------:|:------:|
| **Syntax Skills** | 8 | ✅ Complete |
| **Core Skills** | 3 | ✅ Complete |
| **Implementation Skills** | 8 | 🔄 In Progress |
| **Error Handling Skills** | 7 | ⏳ Planned |
| **Agents** | 2 | ⏳ Planned |

### Syntax Skills (How to write code)
- Client Scripts, Server Scripts, Document Controllers
- hooks.py, Whitelisted Methods, Jinja Templates
- Scheduler/Background Jobs, Custom App Structure

### Core Skills (Framework fundamentals)
- Database Operations, Permissions, API Patterns

### Implementation Skills (Complete workflows)
- Decision trees for choosing the right approach
- End-to-end implementation patterns

---

## 🏗️ Project Structure

```
ERPNext_Anthropic_Claude_Development_Skill_Package/
│
├── skills/
│   └── source/
│       ├── syntax/           # 8 syntax skills
│       │   ├── erpnext-syntax-clientscripts/
│       │   │   ├── SKILL.md  # Main skill file
│       │   │   └── references/
│       │   └── ...
│       ├── core/             # 3 core skills
│       └── impl/             # Implementation skills
│
├── docs/
│   ├── masterplan/           # Project planning
│   └── research/             # 13 research documents
│
├── WAY_OF_WORK.md            # Template methodology
├── LESSONS_LEARNED.md        # Project insights
└── ROADMAP.md                # Current status
```

---

## 🔑 Critical Technical Discovery

**Server Scripts run in a RestrictedPython sandbox where ALL imports are blocked:**

```python
# ❌ WRONG - Will fail in Server Scripts
from frappe.utils import nowdate, getdate
import json

# ✅ CORRECT - Use frappe namespace directly
date = frappe.utils.nowdate()
data = frappe.parse_json(json_string)
```

This single discovery prevents the most common AI-generated ERPNext code failures.

---

## 📖 Using This as a Template

Want to create a skill package for another technology? Follow these steps:

1. **Clone this repository** as a starting point
2. **Read [WAY_OF_WORK.md](WAY_OF_WORK.md)** for the complete methodology
3. **Study [LESSONS_LEARNED.md](LESSONS_LEARNED.md)** to avoid our mistakes
4. **Follow the Anthropic skill-creator conventions** (SKILL.md in folder root!)
5. **Research first, code second** - deterministic outputs require deep understanding

### Key Lessons for Your Project

| Lesson | Why It Matters |
|--------|----------------|
| Test Anthropic tooling FIRST | Ensures your structure is compatible |
| English-only skills | Claude reads English, responds in any language |
| SKILL.md in folder ROOT | Required by `package_skill.py` |
| Research documents per topic | Foundation for deterministic content |
| Push after EVERY phase | Claude's filesystem resets between sessions |

---

## 🤝 Contributing

This project is developed by the OpenAEC Foundation. Contributions welcome!

---

## 📄 License

MIT License - See [LICENSE](LICENSE) for details.

---

*Developed with Claude AI using the methodology documented in this repository.*
