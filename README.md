# ERPNext Anthropic Claude Development Skill Package

> **A comprehensive skills package enabling Claude AI to generate flawless ERPNext/Frappe code**

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![ERPNext](https://img.shields.io/badge/ERPNext-v14%20%7C%20v15%20%7C%20v16-blue)](https://erpnext.com)
[![Frappe](https://img.shields.io/badge/Frappe-Framework-green)](https://frappeframework.com)
[![Agent Skills](https://img.shields.io/badge/Agent%20Skills-Compliant-orange)](https://agentskills.io)
[![Skills](https://img.shields.io/badge/Skills-28-purple)](INDEX.md)

## 🎯 Project Overview

This project contains a collection of **28 deterministic skills and agents** that enable Claude AI instances to generate accurate, production-ready ERPNext/Frappe code. The skills package follows the [Agent Skills](https://agentskills.io) open standard and provides comprehensive coverage of all major ERPNext/Frappe development mechanisms.

### Key Features

- ✅ **28 Skills & Agents** - Complete coverage of ERPNext development
- 🎯 **Deterministic Output** - Produces consistent, verified code patterns
- 📚 **Research-Backed** - Every skill built from verified Frappe documentation
- 🔄 **Version-Aware** - Explicit compatibility for v14, v15, and v16
- 🛡️ **Error Handling** - Production-ready error handling patterns
- 🤖 **Agent-Assisted** - Code interpretation and validation agents

---

## 📦 Quick Start

### Option 1: Claude Code (Recommended)

```bash
# Clone repository
git clone https://github.com/OpenAEC-Foundation/ERPNext_Anthropic_Claude_Development_Skill_Package.git

# Copy to personal skills directory
cp -r ERPNext_Anthropic_Claude_Development_Skill_Package/skills/source/* ~/.claude/skills/
```

### Option 2: Claude.ai Web / Desktop

1. Download skill folders from `skills/source/`
2. ZIP each skill folder
3. Upload via **Settings > Capabilities > Skills**

### Option 3: Claude.ai Project

1. Create a new Project in Claude.ai
2. Upload relevant `SKILL.md` files to Project Knowledge
3. Start chatting about ERPNext development

👉 **See [USAGE.md](USAGE.md) for detailed platform-specific guides**

| Platform | Guide |
|----------|-------|
| Claude Code | [docs/usage/claude-code.md](docs/usage/claude-code.md) |
| Claude.ai Web | [docs/usage/claude-web.md](docs/usage/claude-web.md) |
| Claude Desktop | [docs/usage/claude-desktop.md](docs/usage/claude-desktop.md) |

> ⚠️ **Note**: Claude Mobile does not support custom skills.

---

## 📚 What's Included

| Category | Skills | Description |
|----------|:------:|-------------|
| [Syntax](skills/source/syntax/) | 8 | Language patterns and API syntax |
| [Core](skills/source/core/) | 3 | Database, Permissions, API fundamentals |
| [Implementation](skills/source/impl/) | 8 | Step-by-step development workflows |
| [Error Handling](skills/source/errors/) | 7 | Robust error handling patterns |
| [Agents](skills/source/agents/) | 2 | Code interpretation & validation |
| **Total** | **28** | |

👉 **See [INDEX.md](INDEX.md) for complete skill descriptions**

---

## 🎓 Skills Overview

### Syntax Skills (8)
Define HOW to write ERPNext code:

| Skill | Description |
|-------|-------------|
| `erpnext-syntax-clientscripts` | Client-side JavaScript patterns |
| `erpnext-syntax-serverscripts` | Server Script sandbox rules |
| `erpnext-syntax-controllers` | Document controller methods |
| `erpnext-syntax-hooks` | hooks.py configuration |
| `erpnext-syntax-whitelisted` | @frappe.whitelist() patterns |
| `erpnext-syntax-jinja` | Jinja templating for print formats |
| `erpnext-syntax-scheduler` | Background job configuration |
| `erpnext-syntax-customapp` | Custom app structure |

### Core Skills (3)
Cross-cutting framework knowledge:

| Skill | Description |
|-------|-------------|
| `erpnext-database` | frappe.db API and ORM patterns |
| `erpnext-permissions` | Permission system + Data Masking (v16) |
| `erpnext-api-patterns` | REST, RPC, and webhook patterns |

### Implementation Skills (8)
Step-by-step development workflows for each area.

### Error Handling Skills (7)
Production-ready error handling for every context.

### Agent Skills (2)

| Agent | Description |
|-------|-------------|
| `erpnext-code-interpreter` | Translates requirements to technical specs |
| `erpnext-code-validator` | Validates code against all skill patterns |

---

## 🔑 Critical Knowledge

### Server Script Sandbox

**⚠️ The #1 cause of AI-generated ERPNext code failures:**

```python
# ❌ WRONG - All imports are blocked in Server Scripts
from frappe.utils import nowdate
import json

# ✅ CORRECT - Use frappe namespace directly
date = frappe.utils.nowdate()
data = frappe.parse_json(json_string)
```

All skills in this package are designed with this limitation in mind.

### Version-Specific Features

| Feature | v14 | v15 | v16 |
|---------|:---:|:---:|:---:|
| Basic Server Scripts | ✅ | ✅ | ✅ |
| Type Annotations | ❌ | ✅ | ✅ |
| UUID autoname | ❌ | ❌ | ✅ |
| Data Masking | ❌ | ❌ | ✅ |
| 60s Scheduler Tick | ❌ | ❌ | ✅ |
| Chrome PDF Rendering | ❌ | ❌ | ✅ |

---

## 🏗️ Project Structure

```
ERPNext_Anthropic_Claude_Development_Skill_Package/
├── skills/source/
│   ├── syntax/     # 8 syntax skills
│   ├── core/       # 3 core skills
│   ├── impl/       # 8 implementation skills
│   ├── errors/     # 7 error handling skills
│   └── agents/     # 2 agent skills
├── docs/
│   ├── research/   # 13 research documents
│   ├── usage/      # Platform-specific guides
│   └── masterplan/ # Project planning
├── tools/          # Validation scripts
├── INDEX.md        # Complete skill index
├── USAGE.md        # Installation guides
├── ROADMAP.md      # Project history
└── LESSONS_LEARNED.md
```

---

## 📖 Documentation

| Document | Purpose |
|----------|---------|
| [INDEX.md](INDEX.md) | Complete skill overview & selection guide |
| [USAGE.md](USAGE.md) | Platform-specific installation guides |
| [DEPENDENCIES.md](docs/DEPENDENCIES.md) | Skill dependency matrix |
| [ROADMAP.md](ROADMAP.md) | Project status & changelog |
| [LESSONS_LEARNED.md](LESSONS_LEARNED.md) | Technical discoveries |
| [WAY_OF_WORK.md](WAY_OF_WORK.md) | Development methodology |

---

## 🎓 Using as a Template

This project serves as a **template for developing Claude skill packages** for any technology.

### Key Resources
- [WAY_OF_WORK.md](WAY_OF_WORK.md) - Complete 7-phase methodology
- [LESSONS_LEARNED.md](LESSONS_LEARNED.md) - What we learned
- [Agent Skills Spec](https://agentskills.io) - Official standard

### Top Lessons

1. **Test Anthropic tooling FIRST** - Ensures structure compatibility
2. **English-only skills** - Claude reads English, responds in any language
3. **SKILL.md in folder ROOT** - Required by standard
4. **Research first, code second** - Deterministic outputs require deep understanding
5. **Push after EVERY phase** - Claude's filesystem resets between sessions

---

## 🤝 Contributing

This project is developed by the **OpenAEC Foundation**.

- 🐛 **Issues**: [GitHub Issues](https://github.com/OpenAEC-Foundation/ERPNext_Anthropic_Claude_Development_Skill_Package/issues)
- 💡 **Feature Requests**: Open an issue with the `enhancement` label
- 🔀 **Pull Requests**: Welcome for bug fixes and improvements

---

## 📄 License

MIT License - See [LICENSE](LICENSE) for details.

---

## 🙏 Acknowledgments

- [Anthropic](https://anthropic.com) - Claude AI and Agent Skills standard
- [Frappe](https://frappe.io) - Frappe Framework and ERPNext
- [Agent Skills](https://agentskills.io) - Open standard specification

---

*ERPNext Skills Package v1.1 | Built with Claude AI | OpenAEC Foundation*
