# HANDOFF — Frappe Claude Skill Package

> Snelle overdracht voor nieuwe sessies. Lees dit VOOR je begint.

## Status

- **Package versie**: v3.0.0 (61 skills, feature-complete)
- **Repo**: `OpenAEC-Foundation/Frappe_Claude_Skill_Package`
- **CLAUDE.md**: Upgraded naar v2 template (alle protocols P-000a t/m P-010)
- **CI/CD**: quality.yml workflow toegevoegd

## Wat is er (v2.0)

| Categorie | Aantal | Skills |
|-----------|:------:|--------|
| syntax/ | 13 | clientscripts, serverscripts, controllers, hooks, hooks-events, whitelisted, jinja, scheduler, customapp, doctypes, reports, **print**, **query-builder** |
| core/ | 11 | database, permissions, api, workflow, notifications, files, cache, **translation**, **utils**, **logging**, **search** |
| impl/ | 14 | clientscripts, serverscripts, controllers, hooks, whitelisted, jinja, scheduler, customapp, reports, workflow, website, ui-components, integrations, **workspace** |
| errors/ | 7 | clientscripts, serverscripts, controllers, hooks, database, permissions, api |
| ops/ | 8 | bench, deployment, backup, performance, upgrades, cloud, app-lifecycle, frontend-build |
| agents/ | 5 | interpreter, validator, debugger, migrator, architect |
| testing/ | 2 | unit, cicd |
| **Totaal** | **61** | |

## Skill Naming

Alle skills volgen het patroon `frappe-{laag}-{onderwerp}`:
- `frappe-syntax-*` — Code syntax referentie
- `frappe-core-*` — Cross-cutting concerns
- `frappe-impl-*` — Implementatie workflows
- `frappe-errors-*` — Error handling
- `frappe-ops-*` — Operations & deployment
- `frappe-agent-*` — Intelligente agents
- `frappe-testing-*` — Quality & CI/CD

## Governance Files

| Bestand | Status |
|---------|--------|
| CLAUDE.md | Volledig (P-000a t/m P-010) |
| ROADMAP.md | V3.0 100% compleet |
| WAY_OF_WORK.md | 7-fase methodologie |
| DECISIONS.md | D-001 t/m D-020 |
| LESSONS.md | 22 lessen gedocumenteerd |
| SOURCES.md | Verified Frappe doc URLs |
| REQUIREMENTS.md | Quality criteria |
| CHANGELOG.md | Keep a Changelog format |
| INDEX.md | 61 skills catalogus |
| README.md | GitHub landing page (v3.0) |
| HANDOFF.md | Dit bestand |

## V3.0 Upgrade — Compleet

V3.0 bracht de dekking van ~85% naar ~95% met 7 nieuwe skills + 12 uitbreidingen. Released 2026-03-21.

**Gap Analysis**: `docs/masterplan/frappe-skill-package-gap-analysis-v3.md`

### Nieuwe skills (7)
| Prio | Skill | Waarom |
|:----:|-------|--------|
| P0 | `frappe-core-translation` | Ieder meertalig project, string extractie regels |
| P0 | `frappe-core-utils` | 40+ utils die Claude constant heruitvindt |
| P1 | `frappe-syntax-print` | Print Formats, Print Designer [v15+], Letter Head |
| P1 | `frappe-syntax-query-builder` | frappe.qb is eigen paradigma, te groot voor sub-sectie |
| P1 | `frappe-impl-workspace` | Iedere app levert een workspace |
| P2 | `frappe-core-logging` | Productie logging patterns |
| P2 | `frappe-core-search` | FullTextSearch API |

### Uitbreidingen (12 bestaande skills)
Zie gap analysis v3 document voor details per skill.

## Volgende Sessie

1. Lees ROADMAP.md -> V3.0 sectie
2. Lees `docs/masterplan/frappe-skill-package-gap-analysis-v3.md`
3. Start V3.1 (research) of V3.2 (direct P0 skills maken)
4. Research-first: WebFetch Frappe docs voor translation en utils
