# Frappe Skill Package — Technische Specificatie v2.0

> **Repo**: `OpenAEC-Foundation/ERPNext_Anthropic_Claude_Development_Skill_Package`
> **Wordt**: `OpenAEC-Foundation/Frappe_Claude_Skill_Package` (GitHub rename, auto-redirect)
> **Datum**: 2026-03-20

---

## 1. Repo Rename

**Actie**: GitHub Settings → Rename repository

```
Oud:  OpenAEC-Foundation/ERPNext_Anthropic_Claude_Development_Skill_Package
Nieuw: OpenAEC-Foundation/Frappe_Claude_Skill_Package
```

GitHub maakt automatisch een redirect aan. Alle bestaande links, git remotes, en clones blijven werken totdat iemand expliciet de remote URL wijzigt.

**Te doen na rename:**
- README.md bijwerken (titel, badges, beschrijving)
- social-preview.png vervangen
- GitHub topics bijwerken: `frappe`, `frappe-framework`, `erpnext`, `claude`, `anthropic`, `agent-skills`, `ai-skills`
- Description: "53 deterministic Claude AI skills for Frappe Framework & ERPNext v14-v16 development and operations"

---

## 2. Het Naming Probleem

### Analyse van de huidige 28 skills

De huidige skills heten allemaal `erpnext-*`, maar ze gaan over **Frappe Framework** concepten:

| Huidig | Onderwerp | Is eigenlijk... |
|---|---|---|
| `frappe-syntax-clientscripts` | `frappe.ui.form.on()` | Frappe |
| `frappe-syntax-serverscripts` | Frappe Server Scripts | Frappe |
| `frappe-syntax-controllers` | `frappe.model.document.Document` | Frappe |
| `frappe-syntax-hooks` | Frappe hooks.py | Frappe |
| `frappe-syntax-whitelisted` | `@frappe.whitelist()` | Frappe |
| `frappe-syntax-jinja` | Frappe Jinja templating | Frappe |
| `frappe-syntax-scheduler` | Frappe scheduler_events | Frappe |
| `frappe-syntax-customapp` | `bench new-app` | Frappe |
| `frappe-core-database` | `frappe.db.*` | Frappe |
| `frappe-core-permissions` | Frappe permission system | Frappe |
| `frappe-core-api` | Frappe REST/RPC API | Frappe |
| Alle `errors-*` | Frappe error handling | Frappe |
| Alle `impl-*` | Frappe implementation | Frappe |
| `frappe-agent-interpreter` | Agent | Frappe |
| `frappe-agent-validator` | Agent | Frappe |

**Conclusie**: 28 van de 28 skills gaan over Frappe, niet specifiek ERPNext. De ERPNext-voorbeelden (Sales Invoice, Sales Order) zijn slechts illustraties — de patronen zijn universeel voor elke Frappe app.

### Voorgesteld naming schema

```
frappe-{laag}-{onderwerp}
```

Waarbij `{laag}` de skill categoriseert:

| Prefix | Domein | Scope |
|---|---|---|
| `frappe-syntax-*` | Code syntax referentie | Hoe schrijf je het |
| `frappe-impl-*` | Implementatie workflows | Hoe bouw je het |
| `frappe-errors-*` | Error handling | Hoe ga je om met fouten |
| `frappe-core-*` | Cross-cutting concerns | Database, permissions, etc. |
| `frappe-agent-*` | Intelligente agents | Code interpreter, validator |
| `frappe-ops-*` | **NIEUW**: Operations | Bench, deploy, hosting |

Dit behoudt de bestaande drieluik-structuur (syntax/impl/errors) en voegt `ops` toe.

### Rename mapping (28 bestaande skills)

| Oud | Nieuw | Wijziging |
|---|---|---|
| `frappe-syntax-clientscripts` | `frappe-syntax-clientscripts` | prefix |
| `frappe-syntax-serverscripts` | `frappe-syntax-serverscripts` | prefix |
| `frappe-syntax-controllers` | `frappe-syntax-controllers` | prefix |
| `frappe-syntax-hooks` | `frappe-syntax-hooks` | prefix |
| `frappe-syntax-whitelisted` | `frappe-syntax-whitelisted` | prefix |
| `frappe-syntax-jinja` | `frappe-syntax-jinja` | prefix |
| `frappe-syntax-scheduler` | `frappe-syntax-scheduler` | prefix |
| `frappe-syntax-customapp` | `frappe-syntax-customapp` | prefix |
| `frappe-core-database` | `frappe-core-database` | prefix + laag |
| `frappe-core-permissions` | `frappe-core-permissions` | prefix + laag |
| `frappe-core-api` | `frappe-core-api` | prefix + laag + korter |
| `frappe-impl-clientscripts` | `frappe-impl-clientscripts` | prefix |
| `frappe-impl-serverscripts` | `frappe-impl-serverscripts` | prefix |
| `frappe-impl-controllers` | `frappe-impl-controllers` | prefix |
| `frappe-impl-hooks` | `frappe-impl-hooks` | prefix |
| `frappe-impl-whitelisted` | `frappe-impl-whitelisted` | prefix |
| `frappe-impl-jinja` | `frappe-impl-jinja` | prefix |
| `frappe-impl-scheduler` | `frappe-impl-scheduler` | prefix |
| `frappe-impl-customapp` | `frappe-impl-customapp` | prefix |
| `frappe-errors-clientscripts` | `frappe-errors-clientscripts` | prefix |
| `frappe-errors-serverscripts` | `frappe-errors-serverscripts` | prefix |
| `frappe-errors-controllers` | `frappe-errors-controllers` | prefix |
| `frappe-errors-hooks` | `frappe-errors-hooks` | prefix |
| `frappe-errors-database` | `frappe-errors-database` | prefix |
| `frappe-errors-permissions` | `frappe-errors-permissions` | prefix |
| `frappe-errors-api` | `frappe-errors-api` | prefix |
| `frappe-agent-interpreter` | `frappe-agent-interpreter` | prefix + laag |
| `frappe-agent-validator` | `frappe-agent-validator` | prefix + laag |

**Impact**: Elke SKILL.md bevat interne cross-referenties ("See also: frappe-syntax-hooks"). Die moeten allemaal mee. Dit is een find-and-replace operatie over alle bestanden.

---

## 3. Directory Structuur v2.0

```
Frappe_Claude_Skill_Package/
├── README.md
├── INDEX.md                          # Master catalog (alle 53 skills)
├── INSTALL.md
├── USAGE.md
├── WAY_OF_WORK.md
├── CHANGELOG.md
├── ROADMAP.md
├── CONTRIBUTING.md
├── SECURITY.md
├── LICENSE
├── docs/
│   ├── masterplan/
│   ├── reference/
│   ├── research/
│   └── usage/
├── tools/
│   ├── package_skill.py
│   ├── quick_validate.py
│   └── rename_skills.py              # NIEUW: migratie-tool
│
└── skills/source/
    │
    ├── syntax/                        # LAAG: Hoe schrijf je het (10 skills)
    │   ├── frappe-syntax-clientscripts/       # [BESTAAND, renamed]
    │   ├── frappe-syntax-serverscripts/       # [BESTAAND, renamed]
    │   ├── frappe-syntax-controllers/         # [BESTAAND, renamed]
    │   ├── frappe-syntax-hooks/               # [BESTAAND, renamed]
    │   ├── frappe-syntax-whitelisted/         # [BESTAAND, renamed]
    │   ├── frappe-syntax-jinja/               # [BESTAAND, renamed]
    │   ├── frappe-syntax-scheduler/           # [BESTAAND, renamed]
    │   ├── frappe-syntax-customapp/           # [BESTAAND, renamed]
    │   ├── frappe-syntax-doctypes/            # NIEUW — schema design, fieldtypes, naming
    │   └── frappe-syntax-reports/             # NIEUW — Query Report, Script Report
    │
    ├── core/                          # LAAG: Cross-cutting concerns (7 skills)
    │   ├── frappe-core-database/              # [BESTAAND, renamed]
    │   ├── frappe-core-permissions/            # [BESTAAND, renamed]
    │   ├── frappe-core-api/                   # [BESTAAND, renamed van api-patterns]
    │   ├── frappe-core-workflow/              # NIEUW — workflow engine, states, transitions
    │   ├── frappe-core-notifications/         # NIEUW — notification system, email
    │   ├── frappe-core-files/                 # NIEUW — file handling, uploads, S3
    │   └── frappe-core-cache/                 # NIEUW — Redis, @redis_cache, invalidation
    │
    ├── impl/                          # LAAG: Hoe bouw je het (13 skills)
    │   ├── frappe-impl-clientscripts/         # [BESTAAND, renamed]
    │   ├── frappe-impl-serverscripts/         # [BESTAAND, renamed]
    │   ├── frappe-impl-controllers/           # [BESTAAND, renamed]
    │   ├── frappe-impl-hooks/                 # [BESTAAND, renamed]
    │   ├── frappe-impl-whitelisted/           # [BESTAAND, renamed]
    │   ├── frappe-impl-jinja/                 # [BESTAAND, renamed]
    │   ├── frappe-impl-scheduler/             # [BESTAAND, renamed]
    │   ├── frappe-impl-customapp/             # [BESTAAND, renamed]
    │   ├── frappe-impl-reports/               # NIEUW — report implementation workflows
    │   ├── frappe-impl-workflow/              # NIEUW — workflow implementation
    │   ├── frappe-impl-website/               # NIEUW — portal, web forms, themes
    │   ├── frappe-impl-ui-components/         # NIEUW — dialogs, list view, page API
    │   └── frappe-impl-integrations/          # NIEUW — OAuth, webhooks, payment, import/export
    │
    ├── errors/                        # LAAG: Error handling (7 skills, ongewijzigd)
    │   ├── frappe-errors-clientscripts/       # [BESTAAND, renamed]
    │   ├── frappe-errors-serverscripts/       # [BESTAAND, renamed]
    │   ├── frappe-errors-controllers/         # [BESTAAND, renamed]
    │   ├── frappe-errors-hooks/               # [BESTAAND, renamed]
    │   ├── frappe-errors-database/            # [BESTAAND, renamed]
    │   ├── frappe-errors-permissions/         # [BESTAAND, renamed]
    │   └── frappe-errors-api/                 # [BESTAAND, renamed]
    │
    ├── ops/                           # LAAG: Operations & Deployment (9 skills, ALLES NIEUW)
    │   ├── frappe-ops-bench/                  # bench CLI, site management, multi-tenancy
    │   ├── frappe-ops-deployment/             # production setup, nginx, supervisor, docker
    │   ├── frappe-ops-backup/                 # backup, restore, disaster recovery
    │   ├── frappe-ops-performance/            # MariaDB, Redis, Gunicorn tuning
    │   ├── frappe-ops-upgrades/               # version upgrades, migration, rollback
    │   ├── frappe-ops-cloud/                  # Frappe Cloud API, Press, provisioning
    │   ├── frappe-ops-hosting/                # Hetzner stack, DNS, SSL, monitoring
    │   ├── frappe-ops-app-lifecycle/          # app scaffolding → build → deploy → update
    │   └── frappe-ops-frontend-build/         # esbuild, assets, SCSS, bench build
    │
    ├── agents/                        # LAAG: Intelligent agents (5 skills)
    │   ├── frappe-agent-interpreter/          # [BESTAAND, renamed]
    │   ├── frappe-agent-validator/            # [BESTAAND, renamed]
    │   ├── frappe-agent-debugger/             # NIEUW — debugging workflows
    │   ├── frappe-agent-migrator/             # NIEUW — version migration assistant
    │   └── frappe-agent-architect/            # NIEUW — multi-app architecture decisions
    │
    └── testing/                       # LAAG: Quality (2 skills, ALLES NIEUW)
        ├── frappe-testing-unit/               # unit tests, integration tests, fixtures
        └── frappe-testing-cicd/               # GitHub Actions, linting, pre-commit
```

---

## 4. Volledige Skill Inventory v2.0

### Totaal: 53 skills (28 bestaand + 25 nieuw)

| # | Skill naam | Status | Laag | Beschrijving |
|---|---|---|---|---|
| 1 | `frappe-syntax-clientscripts` | RENAME | syntax | Client-side JS, form events, field manipulation |
| 2 | `frappe-syntax-serverscripts` | RENAME | syntax | Server Script sandbox, doc events, API |
| 3 | `frappe-syntax-controllers` | RENAME | syntax | Document controllers, lifecycle hooks, autoname |
| 4 | `frappe-syntax-hooks` | RENAME | syntax | hooks.py configuratie, doc_events, scheduler |
| 5 | `frappe-syntax-whitelisted` | RENAME | syntax | @frappe.whitelist(), REST endpoints |
| 6 | `frappe-syntax-jinja` | RENAME | syntax | Jinja templates, print formats, email |
| 7 | `frappe-syntax-scheduler` | RENAME | syntax | Scheduler events, background jobs, RQ |
| 8 | `frappe-syntax-customapp` | RENAME | syntax | App structure, pyproject.toml, patches |
| 9 | `frappe-syntax-doctypes` | **NIEUW** | syntax | DocType JSON design, fieldtypes, naming rules, child tables, tree, virtual, Custom Fields, Property Setters |
| 10 | `frappe-syntax-reports` | **NIEUW** | syntax | Query Report columns/execute, Script Report JS, Report Builder, chart data |
| 11 | `frappe-core-database` | RENAME | core | frappe.db.*, ORM, Query Builder, caching |
| 12 | `frappe-core-permissions` | RENAME | core | Roles, user perms, perm levels, data masking |
| 13 | `frappe-core-api` | RENAME | core | REST API, RPC, auth, webhooks |
| 14 | `frappe-core-workflow` | **NIEUW** | core | Workflow engine, states, transitions, actions, conditions, Workflow Action |
| 15 | `frappe-core-notifications` | **NIEUW** | core | Notification DocType, email send/receive, Email Account, templates, Assignment Rules, Auto Repeat, ToDo |
| 16 | `frappe-core-files` | **NIEUW** | core | File DocType, uploads, private/public, S3, file URL patterns |
| 17 | `frappe-core-cache` | **NIEUW** | core | frappe.cache(), @redis_cache, invalidation, locking |
| 18 | `frappe-impl-clientscripts` | RENAME | impl | Client Script implementation workflows |
| 19 | `frappe-impl-serverscripts` | RENAME | impl | Server Script implementation workflows |
| 20 | `frappe-impl-controllers` | RENAME | impl | Controller implementation workflows |
| 21 | `frappe-impl-hooks` | RENAME | impl | hooks.py implementation workflows |
| 22 | `frappe-impl-whitelisted` | RENAME | impl | API endpoint implementation |
| 23 | `frappe-impl-jinja` | RENAME | impl | Template implementation workflows |
| 24 | `frappe-impl-scheduler` | RENAME | impl | Scheduled task implementation |
| 25 | `frappe-impl-customapp` | RENAME | impl | Custom app building workflows |
| 26 | `frappe-impl-reports` | **NIEUW** | impl | Report building workflows, dashboard charts, number cards |
| 27 | `frappe-impl-workflow` | **NIEUW** | impl | Workflow implementation, approval chains |
| 28 | `frappe-impl-website` | **NIEUW** | impl | Portal pages, Web Forms, website settings, themes, SEO |
| 29 | `frappe-impl-ui-components` | **NIEUW** | impl | Dialog API, List View, Page API, Kanban, Calendar, realtime/socket.io |
| 30 | `frappe-impl-integrations` | **NIEUW** | impl | OAuth, Connected Apps, Webhooks DocType, Payment Gateway, Data Import/Export, Print Designer |
| 31 | `frappe-errors-clientscripts` | RENAME | errors | Client-side error handling |
| 32 | `frappe-errors-serverscripts` | RENAME | errors | Server Script error handling |
| 33 | `frappe-errors-controllers` | RENAME | errors | Controller error handling |
| 34 | `frappe-errors-hooks` | RENAME | errors | Hook error handling |
| 35 | `frappe-errors-database` | RENAME | errors | Database error handling |
| 36 | `frappe-errors-permissions` | RENAME | errors | Permission error handling |
| 37 | `frappe-errors-api` | RENAME | errors | API error handling |
| 38 | `frappe-ops-bench` | **NIEUW** | ops | bench CLI complete reference, site management, multi-tenancy, domains, bench get-app, install-app |
| 39 | `frappe-ops-deployment` | **NIEUW** | ops | Production setup, Nginx, Supervisor, Docker, SSL, security hardening, firewall |
| 40 | `frappe-ops-backup` | **NIEUW** | ops | Backup strategies, restore, encryption, S3, scheduled backups, disaster recovery |
| 41 | `frappe-ops-performance` | **NIEUW** | ops | MariaDB tuning, Redis memory, Gunicorn workers, CDN, slow query, profiling |
| 42 | `frappe-ops-upgrades` | **NIEUW** | ops | Version upgrades v14→v15→v16, migration troubleshooting, rollback, breaking changes |
| 43 | `frappe-ops-cloud` | **NIEUW** | ops | Frappe Cloud API, Press, site provisioning, bench management, app deployment |
| 44 | `frappe-ops-hosting` | **NIEUW** | ops | Hetzner stack, server provisioning, DNS, monitoring, scaling |
| 45 | `frappe-ops-app-lifecycle` | **NIEUW** | ops | App scaffolding → config → build → test → deploy → update → publish, Setup Wizard, Module Def, development mode, debugging |
| 46 | `frappe-ops-frontend-build` | **NIEUW** | ops | esbuild (v15+), build.json (v14), asset bundling, SCSS, bench build |
| 47 | `frappe-agent-interpreter` | RENAME | agents | Vague requirements → technical specs |
| 48 | `frappe-agent-validator` | RENAME | agents | Code review against all skills |
| 49 | `frappe-agent-debugger` | **NIEUW** | agents | Debugging workflows, bench console, error diagnosis, log analysis |
| 50 | `frappe-agent-migrator` | **NIEUW** | agents | Version migration assistant, breaking change detection, upgrade path planning |
| 51 | `frappe-agent-architect` | **NIEUW** | agents | Multi-app architecture, when to split, cross-app patterns, marketplace strategy |
| 52 | `frappe-testing-unit` | **NIEUW** | testing | frappe.tests, IntegrationTestCase, fixtures, bench run-tests |
| 53 | `frappe-testing-cicd` | **NIEUW** | testing | GitHub Actions, test matrix, linting, semgrep, pre-commit |

---

## 5. Rename Operatie (technisch)

### Wat er moet veranderen per skill

Elke bestaande skill heeft:

1. **Directory naam** — `frappe-syntax-clientscripts/` → `frappe-syntax-clientscripts/`
2. **SKILL.md `name:` field** — `name: frappe-syntax-clientscripts` → `name: frappe-syntax-clientscripts`
3. **SKILL.md `description:` field** — tekst bevat soms "ERPNext" waar "Frappe" correcter is
4. **Cross-references in tekst** — "See: `frappe-syntax-hooks`" → "See: `frappe-syntax-hooks`"
5. **Cross-references in "See Also"** — alle `erpnext-*` referenties
6. **Reference file cross-references** — bestanden in `references/` verwijzen ook naar andere skills

### Geautomatiseerd rename script

```bash
# Pseudocode voor tools/rename_skills.py
RENAME_MAP = {
    "frappe-syntax-clientscripts": "frappe-syntax-clientscripts",
    "frappe-syntax-serverscripts": "frappe-syntax-serverscripts",
    "frappe-syntax-controllers":   "frappe-syntax-controllers",
    "frappe-syntax-hooks":         "frappe-syntax-hooks",
    "frappe-syntax-whitelisted":   "frappe-syntax-whitelisted",
    "frappe-syntax-jinja":         "frappe-syntax-jinja",
    "frappe-syntax-scheduler":     "frappe-syntax-scheduler",
    "frappe-syntax-customapp":     "frappe-syntax-customapp",
    "frappe-core-database":             "frappe-core-database",
    "frappe-core-permissions":          "frappe-core-permissions",
    "frappe-core-api":         "frappe-core-api",
    "frappe-impl-clientscripts":   "frappe-impl-clientscripts",
    "frappe-impl-serverscripts":   "frappe-impl-serverscripts",
    "frappe-impl-controllers":     "frappe-impl-controllers",
    "frappe-impl-hooks":           "frappe-impl-hooks",
    "frappe-impl-whitelisted":     "frappe-impl-whitelisted",
    "frappe-impl-jinja":           "frappe-impl-jinja",
    "frappe-impl-scheduler":       "frappe-impl-scheduler",
    "frappe-impl-customapp":       "frappe-impl-customapp",
    "frappe-errors-clientscripts": "frappe-errors-clientscripts",
    "frappe-errors-serverscripts": "frappe-errors-serverscripts",
    "frappe-errors-controllers":   "frappe-errors-controllers",
    "frappe-errors-hooks":         "frappe-errors-hooks",
    "frappe-errors-database":      "frappe-errors-database",
    "frappe-errors-permissions":   "frappe-errors-permissions",
    "frappe-errors-api":           "frappe-errors-api",
    "frappe-agent-interpreter":     "frappe-agent-interpreter",
    "frappe-agent-validator":       "frappe-agent-validator",
}

# Per skill:
# 1. git mv old_dir/ new_dir/
# 2. sed -i over alle .md bestanden: replace old_name → new_name
# 3. Update SKILL.md name: field
# 4. Update SKILL.md description: waar nodig
```

### Bestanden buiten skills/ die mee moeten

| Bestand | Bevat skill-referenties |
|---|---|
| `INDEX.md` | Alle 28 skill namen |
| `USAGE.md` | Skill namen in voorbeelden |
| `WAY_OF_WORK.md` | Skill namen in workflow |
| `LESSONS.md` | Mogelijke referenties |
| `docs/DEPENDENCIES.md` | Dependency matrix |
| `docs/AGENT_SKILLS_REVIEW.md` | Skill namen |
| `tools/quick_validate.py` | Possible hardcoded names |

---

## 6. Directory Migratie

### Huidige structuur → Nieuwe structuur

```
HUIDIG                              NIEUW
skills/source/                      skills/source/
├── syntax/                         ├── syntax/
│   ├── erpnext-syntax-*  (8)       │   ├── frappe-syntax-*  (8 renamed)
│   └──                             │   ├── frappe-syntax-doctypes/   (NIEUW)
│                                   │   └── frappe-syntax-reports/    (NIEUW)
├── core/                           ├── core/
│   ├── frappe-core-database             │   ├── frappe-core-database     (renamed + moved)
│   ├── frappe-core-permissions          │   ├── frappe-core-permissions  (renamed + moved)
│   ├── frappe-core-api         │   ├── frappe-core-api          (renamed + moved)
│   └──                             │   ├── frappe-core-workflow/     (NIEUW)
│                                   │   ├── frappe-core-notifications/(NIEUW)
│                                   │   ├── frappe-core-files/        (NIEUW)
│                                   │   └── frappe-core-cache/        (NIEUW)
├── impl/                           ├── impl/
│   ├── erpnext-impl-*  (8)         │   ├── frappe-impl-*  (8 renamed)
│   └──                             │   ├── frappe-impl-reports/      (NIEUW)
│                                   │   ├── frappe-impl-workflow/     (NIEUW)
│                                   │   ├── frappe-impl-website/      (NIEUW)
│                                   │   ├── frappe-impl-ui-components/(NIEUW)
│                                   │   └── frappe-impl-integrations/ (NIEUW)
├── errors/                         ├── errors/
│   └── erpnext-errors-*  (7)       │   └── frappe-errors-*  (7 renamed)
├── agents/                         ├── agents/
│   ├── frappe-agent-interpreter     │   ├── frappe-agent-interpreter (renamed + moved)
│   ├── frappe-agent-validator       │   ├── frappe-agent-validator   (renamed + moved)
│   └──                             │   ├── frappe-agent-debugger/    (NIEUW)
│                                   │   ├── frappe-agent-migrator/    (NIEUW)
│                                   │   └── frappe-agent-architect/   (NIEUW)
                                    ├── ops/                          (HELE LAAG NIEUW)
                                    │   ├── frappe-ops-bench/
                                    │   ├── frappe-ops-deployment/
                                    │   ├── frappe-ops-backup/
                                    │   ├── frappe-ops-performance/
                                    │   ├── frappe-ops-upgrades/
                                    │   ├── frappe-ops-cloud/
                                    │   ├── frappe-ops-hosting/
                                    │   ├── frappe-ops-app-lifecycle/
                                    │   └── frappe-ops-frontend-build/
                                    └── testing/                      (HELE LAAG NIEUW)
                                        ├── frappe-testing-unit/
                                        └── frappe-testing-cicd/
```

### Migratie volgorde

```
Stap 1: Rename bestaande directories (git mv)
Stap 2: Verplaats core/ skills naar nieuwe locaties (database, permissions, api-patterns)
Stap 3: Verplaats agents/ skills naar nieuwe namen
Stap 4: Find-and-replace alle erpnext-* referenties in alle .md bestanden
Stap 5: Update INDEX.md, USAGE.md, WAY_OF_WORK.md, etc.
Stap 6: Maak lege SKILL.md stubs voor alle 25 nieuwe skills
Stap 7: Valideer (tools/quick_validate.py)
Stap 8: Commit als "chore: rename erpnext-* → frappe-* (v2.0 restructure)"
```

---

## 7. Skill Structuur Template

Elke nieuwe skill volgt dezelfde structuur als de bestaande:

```
frappe-{laag}-{onderwerp}/
├── SKILL.md                # Hoofdbestand (Claude leest dit)
└── references/             # Ondersteunende bestanden
    ├── examples.md         # Werkende code voorbeelden
    ├── anti-patterns.md    # Veelgemaakte fouten
    ├── decision-tree.md    # Wanneer-gebruik-je-wat (voor impl skills)
    ├── workflows.md        # Stap-voor-stap (voor impl skills)
    └── {topic}.md          # Topic-specifieke referenties
```

### SKILL.md frontmatter

```yaml
---
name: frappe-{laag}-{onderwerp}
description: >
  Use when ... Covers ... Keywords: ...
license: MIT
compatibility: "Claude Code, Claude.ai Projects, Claude API. Frappe v14-v16."
metadata:
  author: OpenAEC-Foundation
  version: "2.0"
---
```

---

## 8. Open Ontwerp-vragen

Deze moeten nog besloten worden:

| # | Vraag | Opties | Impact |
|---|---|---|---|
| 1 | **Repo naam exact** | `Frappe_Claude_Skill_Package` / `Frappe_Agent_Skills` / `Frappe_Anthropic_Claude_Development_Skill_Package` | Branding, herkenbaarheid |
| 2 | **ERPNext-specifieke skills later?** | Na deze 53 Frappe skills, komen er ook ERPNext module-specifieke skills (Accounting, HR, Manufacturing)? | Scope van het project |
| 3 | **Bestaande skills inhoudelijk updaten?** | Alleen rename, of ook de content van de 28 bestaande skills herzien/verbeteren? | Scope van v2.0 |
| 4 | **hooks.py skill splitsen?** | De huidige `syntax-hooks` dekt ~15 hooks, maar er zijn 50+. Eén uitgebreide skill of splitsen? | Skill grootte vs. overzichtelijkheid |
| 5 | **Ops skills: generiek of jullie-stack-specifiek?** | `frappe-ops-hosting` generiek of specifiek voor Hetzner? | Herbruikbaarheid vs. jullie directe nut |
