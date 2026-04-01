<p align="center">
  <img src="docs/social-preview.png" alt="61 Deterministic Claude AI Skills for Frappe Framework" width="100%">
</p>

<p align="center">
  <a href="#-installation"><img src="https://img.shields.io/badge/Claude_Code-Ready-27ca40?style=for-the-badge" alt="Claude Code Ready"></a>
  <a href="#-version-compatibility"><img src="https://img.shields.io/badge/Frappe-v14_|_v15_|_v16-0089FF?style=for-the-badge" alt="Frappe Versions"></a>
  <a href="https://agentskills.org"><img src="https://img.shields.io/badge/Agent_Skills-Standard-DA7756?style=for-the-badge" alt="Agent Skills Standard"></a>
  <a href="LICENSE.md"><img src="https://img.shields.io/badge/License-MIT-lightgrey?style=for-the-badge" alt="MIT License"></a>
  <a href="#-skill-categories"><img src="https://img.shields.io/badge/v3.2-61_skills-blueviolet?style=for-the-badge" alt="v3.2 — 61 Skills"></a>
</p>

<p align="center">
  <strong>61 deterministic skills</strong> enabling Claude AI to generate flawless Frappe/ERPNext code.<br>
  Covers ~95% of the Frappe Framework surface area across 7 categories.<br>
  Built on the <a href="https://agentskills.org">Agent Skills</a> open standard.
</p>


---

## 🎯 Why This Exists

Claude is powerful, but without domain-specific guidance it generates Frappe/ERPNext code that *looks* correct but **fails in production**.

**The #1 cause of AI-generated Frappe failures:**

```python
# ❌ WRONG - This fails silently in Server Scripts
from frappe.utils import nowdate
today = nowdate()

# ✅ CORRECT - Server Scripts block all imports
today = frappe.utils.nowdate()
```

This package encodes **61 hard-won lessons** like this into deterministic skills that Claude follows automatically.

---

## 📦 Skill Categories

| Category | Count | What's Covered |
|:---------|:-----:|:---------------|
| **Syntax** | 13 | Client scripts, server scripts, controllers, hooks, Jinja, scheduler, custom apps, print formats, query builder |
| **Core** | 11 | Database, permissions, REST API, caching, files, notifications, workflow, translation/i18n, utilities, logging, search |
| **Implementation** | 14 | Development workflows, migrations, fixtures, integrations, reports, UI components, website, workspaces |
| **Error Handling** | 7 | Production-ready error patterns and debugging |
| **Operations** | 9 | Deployment, bench management, backup/restore, monitoring, performance tuning, upgrades |
| **Agents** | 5 | Code interpretation, validation, migration planning, architecture, debugging |
| **Testing** | 2 | Unit testing patterns, CI/CD workflows |

**Total: 61 skills covering ~95% of the Frappe Framework surface area** (up from 53 skills / ~85% in v2.0).

---

## 🚀 Installation

### Claude Code (Recommended)

```bash
# Clone the repository
git clone https://github.com/OpenAEC-Foundation/Frappe_Claude_Skill_Package.git

# Copy all 61 skills to your Claude Code skills directory
cp -r Frappe_Claude_Skill_Package/skills/source/* ~/.claude/skills/
```

### Claude.ai Web/Desktop

1. Download skill folders from [`skills/source/`](skills/source/)
2. ZIP each folder individually
3. Upload via **Settings → Capabilities → Skills**

### Claude.ai Projects

1. Create a new project
2. Upload `SKILL.md` files to the **Knowledge** section

---

## 🔄 Version Compatibility

All 61 skills document version-specific behavior for Frappe Framework v14 through v16.

| Feature | v14 | v15 | v16 |
|:--------|:---:|:---:|:---:|
| Type annotations | ❌ | ✅ | ✅ |
| UUID autoname | ❌ | ✅ | ✅ |
| Data masking | ❌ | ❌ | ✅ |
| Scheduler improvements | ❌ | ✅ | ✅ |
| Virtual DocTypes | ❌ | ✅ | ✅ |

---

## 📚 Documentation

| Document | Description |
|:---------|:------------|
| **[INDEX.md](INDEX.md)** | Complete skill catalog with descriptions and dependency graph |
| **[USAGE.md](USAGE.md)** | Platform-specific installation guides |
| **[WAY_OF_WORK.md](WAY_OF_WORK.md)** | 7-phase development methodology |
| **[LESSONS.md](LESSONS.md)** | Technical discoveries and gotchas |
| **[CHANGELOG.md](CHANGELOG.md)** | Version history |

---

## 🤝 Contributing

This package also serves as a **template** for building Claude skill packages in other technology domains.

See [`WAY_OF_WORK.md`](WAY_OF_WORK.md) for the methodology we used to build these skills.

**Found an issue?** [Open an issue](https://github.com/OpenAEC-Foundation/Frappe_Claude_Skill_Package/issues/new)
**Want to contribute?** PRs welcome!

---

## Companion Skills: Cross-Technology Integration

This package covers ERPNext and Frappe as individual technologies. When you need to **bridge** ERPNext with BIM/IFC tools, install the companion cross-technology package:

> **[Cross-Tech AEC Integration Skills](https://github.com/OpenAEC-Foundation/Cross-Tech-AEC-Claude-Skill-Package)** — 15 skills for technology boundaries

Relevant cross-tech skills for ERPNext users:

| Skill | Boundary | What it adds |
|-------|----------|-------------|
| `crosstech-impl-ifc-erpnext-costing` | IFC ↔ ERPNext | Extract IFC quantities → ERPNext BOMs, cost estimation pipeline |
| `crosstech-impl-n8n-aec-pipeline` | n8n ↔ ERPNext API | Automate IFC→ERPNext workflows with n8n |
| `crosstech-impl-docker-aec-stack` | Docker ↔ ERPNext | Containerized AEC stack with ERPNext integration |
| `crosstech-core-ifc-schema-bridge` | IFC ↔ All formats | IFC quantity sets, property sets, schema mapping |

---

## 📄 License

MIT — See [LICENSE.md](LICENSE.md) for details.

---

<p align="center">
  <sub>Built with ❤️ by <a href="https://github.com/OpenAEC-Foundation">OpenAEC Foundation</a></sub><br>
  <sub>Open standards for AEC technology</sub>
</p>

<p align="center">
  <a href="https://github.com/OpenAEC-Foundation/Frappe_Claude_Skill_Package/stargazers">⭐ Star this repo if it helps you!</a>
</p>
