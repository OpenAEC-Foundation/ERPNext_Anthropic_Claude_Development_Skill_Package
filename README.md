<p align="center">
  <img src="docs/social-preview.png" alt="53 Deterministic Claude AI Skills for Frappe Framework" width="100%">
</p>

<p align="center">
  <a href="#-installation"><img src="https://img.shields.io/badge/Claude_Code-Ready-27ca40?style=for-the-badge" alt="Claude Code Ready"></a>
  <a href="#-version-compatibility"><img src="https://img.shields.io/badge/Frappe-v14_|_v15_|_v16-0089FF?style=for-the-badge" alt="Frappe Versions"></a>
  <a href="https://agentskills.org"><img src="https://img.shields.io/badge/Agent_Skills-Standard-DA7756?style=for-the-badge" alt="Agent Skills Standard"></a>
  <a href="LICENSE.md"><img src="https://img.shields.io/badge/License-MIT-lightgrey?style=for-the-badge" alt="MIT License"></a>
  <a href="#-skill-categories"><img src="https://img.shields.io/badge/v2.0-53_skills-blueviolet?style=for-the-badge" alt="v2.0 — 53 Skills"></a>
</p>

<p align="center">
  <strong>53 deterministic skills</strong> enabling Claude AI to generate flawless Frappe/ERPNext code.<br>
  Covers ~85% of the Frappe Framework surface area across 7 categories.<br>
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

This package encodes **53 hard-won lessons** like this into deterministic skills that Claude follows automatically.

---

## 📦 Skill Categories

| Category | Count | What's Covered |
|:---------|:-----:|:---------------|
| **Syntax** | 11 | Client scripts, server scripts, controllers, hooks, whitelisting, Jinja templating, scheduler events, custom apps, form manipulation, workspace configuration, print formats |
| **Core** | 7 | Database operations, permissions system, REST API patterns, DocType architecture, naming rules, caching, background jobs |
| **Implementation** | 13 | Step-by-step development workflows for common tasks, migrations, fixtures, data import/export, custom fields, report builder, dashboard creation |
| **Error Handling** | 7 | Production-ready error patterns and debugging |
| **Operations** | 8 | Deployment, bench management, site configuration, backup/restore, monitoring, multi-tenancy, update procedures, performance tuning |
| **Agents** | 5 | Code interpretation, validation, migration planning, test generation, review automation |
| **Testing** | 2 | Unit testing patterns, integration test workflows |

**Total: 53 skills covering ~85% of the Frappe Framework surface area** (up from 28 skills / ~16% in v1.x).

---

## 🚀 Installation

### Claude Code (Recommended)

```bash
# Clone the repository
git clone https://github.com/OpenAEC-Foundation/ERPNext_Anthropic_Claude_Development_Skill_Package.git

# Copy all 53 skills to your Claude Code skills directory
cp -r ERPNext_Anthropic_Claude_Development_Skill_Package/skills/source/* ~/.claude/skills/
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

All 53 skills document version-specific behavior for Frappe Framework v14 through v16.

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

**Found an issue?** [Open an issue](https://github.com/OpenAEC-Foundation/ERPNext_Anthropic_Claude_Development_Skill_Package/issues/new)
**Want to contribute?** PRs welcome!

---

## 📄 License

MIT — See [LICENSE.md](LICENSE.md) for details.

---

<p align="center">
  <sub>Built with ❤️ by <a href="https://github.com/OpenAEC-Foundation">OpenAEC Foundation</a></sub><br>
  <sub>Open standards for AEC technology</sub>
</p>

<p align="center">
  <a href="https://github.com/OpenAEC-Foundation/ERPNext_Anthropic_Claude_Development_Skill_Package/stargazers">⭐ Star this repo if it helps you!</a>
</p>
