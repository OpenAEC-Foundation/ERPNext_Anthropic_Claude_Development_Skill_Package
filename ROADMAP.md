# ROADMAP - Frappe Claude Skill Package

> **📍 Dit is de SINGLE SOURCE OF TRUTH voor project status en voortgang.**
> Claude Project Instructies verwijzen hiernaar - geen dubbele tracking.

> **Laatste update**: 2026-03-21
> **Status**: V3.0 COMPLEET — Release pending
> **V3 Gap Analysis**: [frappe-skill-package-gap-analysis-v3.md](docs/masterplan/frappe-skill-package-gap-analysis-v3.md)
> **V2 Tech Spec**: [frappe-skill-package-tech-spec-v2.md](docs/masterplan/frappe-skill-package-tech-spec-v2.md)
> **V2 Gap Analysis**: [frappe-skill-package-gap-analysis.md](docs/masterplan/frappe-skill-package-gap-analysis.md)
> **Structuur**: Engels-only, Anthropic-conform, V14/V15/V16 compatible

---

## V2.0 Upgrade — Frappe Framework Full Coverage

> **Doel**: Van 28 ERPNext-specifieke skills naar 53 Frappe Framework skills
> **Scope**: Rename + restructure + 25 nieuwe skills
> **Dekking**: ~16% → ~85% van het Frappe surface area

### V2 Status

| Categorie | Voltooid | Totaal |
|-----------|:--------:|:------:|
| Rename + frontmatter upgrade | 28 | 28 |
| Content upgrade bestaande skills | 28 | 28 |
| Nieuwe Syntax skills | 3 | 3 |
| Nieuwe Core skills | 4 | 4 |
| Nieuwe Impl skills | 5 | 5 |
| Nieuwe Ops skills | 8 | 8 |
| Nieuwe Agents | 3 | 3 |
| Nieuwe Testing skills | 2 | 2 |
| **TOTAAL v2.0** | **81** | **81** |

**V2 Progress**: ████████████████████ **100%** — Alle 53 skills compleet!

### V2 Fasen

| Fase | Beschrijving | Status |
|------|-------------|:------:|
| V2.1 | Gap analysis valideren | ✅ Compleet |
| V2.2 | Rename + frontmatter upgrade (28 skills) | ✅ Compleet |
| V2.3 | Directory herstructurering + 25 nieuwe stubs | ✅ Compleet |
| V2.4 | Content upgrade bestaande 28 skills | ✅ Compleet |
| V2.5 | Nieuwe skills vullen (25 skills, P0-P3) | ✅ Compleet |
| V2.6 | Validatie, INDEX, README | ✅ Compleet |

### V2 Prioriteiten

| Prioriteit | Skills | Status |
|:----------:|--------|:------:|
| **P0** | doctypes, reports, workflow, testing, app-lifecycle | ✅ |
| **P1** | notifications, ui-components, website, files, hooks-events | ✅ |
| **P2** | bench, deployment, backup, performance, upgrades, frontend-build | ✅ |
| **P3** | cloud, cache, integrations, architect, debugger, migrator | ✅ |

---

## V3.0 Upgrade — Full Coverage (~95%)

> **Doel**: Van 53 naar 60 skills + 12 bestaande skills verrijken
> **Scope**: 7 nieuwe skills + 12 uitbreidingen (extra reference files)
> **Dekking**: ~85% -> ~95% van het Frappe surface area
> **Gap Analysis**: [frappe-skill-package-gap-analysis-v3.md](docs/masterplan/frappe-skill-package-gap-analysis-v3.md)

### V3 Status

| Categorie | Voltooid | Totaal |
|-----------|:--------:|:------:|
| Nieuwe skills (P0: translation, utils) | 2 | 2 |
| Nieuwe skills (P1: print, query-builder, workspace) | 3 | 3 |
| Nieuwe skills (P2: logging, search) | 2 | 2 |
| Uitbreidingen bestaande skills | 12 | 12 |
| **TOTAAL v3.0** | **19** | **19** |

**V3 Progress**: ████████████████████ **100%** — Alle 61 skills compleet!

### V3 Fasen

| Fase | Beschrijving | Status |
|------|-------------|:------:|
| V3.1 | Research voor 7 nieuwe skills | ✅ Compleet |
| V3.2 | Nieuwe skills creeren (P0 -> P1 -> P2) | ✅ Compleet |
| V3.3 | 12 bestaande skills uitbreiden | ✅ Compleet |
| V3.4 | Validatie + INDEX + README | ✅ Compleet |
| V3.5 | Release v3.0.0 | ✅ Compleet |

### V3 Nieuwe Skills

| Prioriteit | Skill | Scope |
|:----------:|-------|-------|
| **P0** | `frappe-core-translation` | i18n, _(), CSV files, bench get-untranslated, RTL |
| **P0** | `frappe-core-utils` | 40+ frappe.utils.* functies referentie |
| **P1** | `frappe-syntax-print` | Print Formats, Print Designer [v15+], Letter Head, get_pdf() |
| **P1** | `frappe-syntax-query-builder` | frappe.qb dedicated referentie, joins, cross-DB |
| **P1** | `frappe-impl-workspace` | Workspace DocType, shortcuts, charts, number cards |
| **P2** | `frappe-core-logging` | frappe.logger(), structured logging, production patterns |
| **P2** | `frappe-core-search` | FullTextSearch API, global_search, Awesomebar |

### V3 Uitbreidingen Bestaande Skills

| Skill | Uitbreiding |
|-------|------------|
| frappe-impl-ui-components | Controls API, Tree View API, dropdown_button |
| frappe-impl-website | Portal Generators, Blog systeem |
| frappe-impl-jinja | Print Designer decision tree |
| frappe-core-notifications | Email Account setup, Email Queue, bulk email |
| frappe-ops-app-lifecycle | Module Def, Workspace JSON shipping |
| frappe-syntax-controllers | Document API complete reference |
| frappe-ops-bench | Custom bench commands hook |
| frappe-syntax-hooks | Request lifecycle, Router API |
| frappe-agent-debugger | VS Code DAP, bench console advanced |
| frappe-ops-upgrades | Frappe Packages |
| frappe-syntax-doctypes | Data Masking [v16+], frappe.types |
| frappe-core-database | Cross-ref naar query-builder skill |

---

## V1.x — Completed Releases

---

## Project Status

| Categorie | Voltooid | Totaal |
|-----------|:--------:|:------:|
| Research | 13 | 13 |
| Syntax Skills | 8 | 8 |
| Core Skills | 3 | 3 |
| Implementation Skills | 8 | 8 |
| Error Handling Skills | 7 | 7 |
| Agents | 2 | 2 |
| **TOTAAL Skills** | **28** | **28** |

**Skills**: ████████████████████ **100%** ✅  
**V16 Compatibility**: ████████████████████ **100%** ✅  
**Validation**: ████████████████████ **28/28 PASS** ✅  
**GitHub Community**: ██████████████████░░ **6/7** ✅

---

## Open Issues

| # | Titel | Prioriteit | Status |
|---|-------|:----------:|:------:|
| #14 | Repository topics toevoegen | 🟢 | Open (handmatig) |
| #15 | GitHub Community Standards | 🔴 | ✅ Compleet |

---

## ✅ Fase 8.8: GitHub Community Standards - COMPLEET

**Doel:** Repository klaarmaken voor public release met volledige GitHub community compliance.

### Score: 6/7 ✅

| Criterium | Status |
|-----------|:------:|
| README.md | ✅ |
| LICENSE | ✅ |
| CODE_OF_CONDUCT.md | ⏭️ Skipped |
| CONTRIBUTING.md | ✅ |
| SECURITY.md | ✅ |
| Issue Templates | ✅ |
| PR Template | ✅ |

### Substappen

| Stap | Bestand | Beschrijving | Status |
|------|---------|--------------|:------:|
| 8.8.1 | `CODE_OF_CONDUCT.md` | Contributor Covenant v2.1 | ⏭️ Skipped |
| 8.8.2 | `CONTRIBUTING.md` | Bijdrage richtlijnen | ✅ |
| 8.8.3 | `SECURITY.md` | Security vulnerability policy | ✅ |
| 8.8.4 | `CHANGELOG.md` | Versie geschiedenis (Keep a Changelog) | ✅ |
| 8.8.5 | `INSTALL.md` | Volledige installatie instructies | ✅ (exists) |
| 8.8.6 | `.github/ISSUE_TEMPLATE/bug_report.yml` | Bug report template | ✅ |
| 8.8.7 | `.github/ISSUE_TEMPLATE/feature_request.yml` | Feature request template | ✅ |
| 8.8.8 | `.github/ISSUE_TEMPLATE/config.yml` | Template configuratie | ✅ |
| 8.8.9 | `.github/PULL_REQUEST_TEMPLATE.md` | PR checklist | ✅ |

### Na Voltooiing
- [ ] Repository public maken (handmatig via GitHub UI)
- [ ] Topics toevoegen (Issue #14)
- [ ] Description toevoegen aan repo
- [ ] API tokens regenereren (security)

---

## Fase Overzicht

### ✅ Fase 1-7: v1.0 Release (Compleet)

Alle 28 skills en agents voltooid en gedocumenteerd.

### ✅ Fase 8.1-8.7: Post-release Verbeteringen (v1.1)

| Stap | Issue | Beschrijving | Status |
|------|:-----:|--------------|:------:|
| 8.1 | - | Kritische Reflectie | ✅ |
| 8.2 | #10, #4 | V16 skill updates | ✅ |
| 8.3 | - | Validatie & Testing | ✅ |
| 8.4 | #9 | Agent Skills review | ✅ |
| 8.5 | #5 | ~~Claude Code format~~ | ❌ Vervallen |
| 8.6 | #11 | How-to-use docs | ✅ |
| 8.7 | #12 | Final Polish & Release | ✅ |

### ✅ Fase 8.8: GitHub Community Standards (v1.2)

| Stap | Beschrijving | Status |
|------|--------------|:------:|
| 8.8.1 | CODE_OF_CONDUCT.md | ⏭️ Skipped |
| 8.8.2-8.8.4 | Community & Docs | ✅ |
| 8.8.5 | INSTALL.md | ✅ (exists) |
| 8.8.6-8.8.9 | Issue & PR Templates | ✅ |

**Fase 8 Voortgang**: ████████████████████ **100%** ✅

---

## Release History

### v3.0.0 (2026-03-21) - Full Coverage (~95%) ✅

- 61 skills (was 53) across 7 categories
- 7 new skills: translation, utils, print, query-builder, workspace, logging, search
- 12 existing skills extended with new reference files
- ~95% Frappe Framework surface area coverage (was ~85%)
- All 61 skills validated (under 500 lines, valid frontmatter)

### v2.0.0 (2026-03-20) - Frappe Framework Full Coverage ✅

- 53 skills (was 28) across 7 categories
- Renamed erpnext-* -> frappe-* (all 28 existing skills)
- 25 new skills: ops (8), testing (2), agents (+3), syntax (+3), core (+4), impl (+5)
- All 28 existing skills fully rewritten with fresh research
- ~85% Frappe Framework surface area coverage
- MIT license, v2.0 metadata
- Repository renamed to Frappe_Claude_Skill_Package
- Social preview banner updated

### v1.2 (2026-01-18) - GitHub Ready ✅

- ✅ GitHub Community Standards compliance (6/7)
- ✅ Issue & PR templates
- ✅ CONTRIBUTING.md
- ✅ SECURITY.md
- ✅ CHANGELOG.md

### v1.1 (2026-01-18)

- ✅ V16 compatibility for all skills
- ✅ Agent Skills standard compliance
- ✅ Platform-specific usage guides (USAGE.md)
- ✅ Complete README overhaul
- ✅ Validation: 28/28 skills pass

### v1.0 (2026-01-17)

- 🎉 Initial release
- ✅ 28 skills and agents
- ✅ V14/V15 compatibility
- ✅ Full documentation

---

## Closed Issues

| # | Titel | Resolution |
|---|-------|:----------:|
| #4 | V16 compatibility review | ✅ Compleet |
| #5 | Claude Code native format | ❌ Niet meer nodig |
| #9 | Agent Skills standaard review | ✅ Compleet |
| #10 | V16 skill updates (9 skills) | ✅ Compleet |
| #11 | How-to-use documentatie | ✅ Compleet |
| #12 | Final Polish & v1.1 Release | ✅ Compleet |
| #15 | GitHub Community Standards | ✅ Compleet |

---

## Changelog

### 2026-03-21 (sessie 26) - V3.0 COMPLEET

**V3.0 Upgrade — 53 skills -> 60 skills + 12 uitbreidingen:**
- V3.1: Research voor 7 nieuwe skills (5 agents parallel)
- V3.2: 7 nieuwe skills gecreeerd (P0: translation, utils; P1: print, query-builder, workspace; P2: logging, search)
- V3.3: 12 bestaande skills uitgebreid met nieuwe reference files (12 agents parallel)
- V3.4: Validatie (60/60 pass), INDEX.md herbouwd, README.md geupdate
- Issue #14 gesloten (topics waren al ingesteld)

**Totaal: 61 skills, ~95% Frappe surface area dekking**
- syntax: 13 skills (+2: print, query-builder)
- core: 11 skills (+4: translation, utils, logging, search)
- impl: 14 skills (+1: workspace)
- errors: 7 skills (unchanged)
- ops: 8 skills (unchanged)
- agents: 5 skills (unchanged)
- testing: 2 skills (unchanged)

---

### 2026-03-20 (sessie 25) - V2.0 COMPLEET

**V2.0 Massive Upgrade — 28 skills -> 53 skills:**
- D-016 t/m D-020: scope beslissingen vastgelegd
- Research: hooks (95 hooks, split in 2 skills), hosting (bench op Hetzner VPS)
- V2.2: 28 skills hernoemd `erpnext-*` -> `frappe-*`, frontmatter upgraded
- V2.3: 25 nieuwe skill stubs + `ops/` en `testing/` directories
- V2.4: Alle 28 bestaande skills volledig herschreven met verse research
- V2.5: Alle 25 nieuwe skills gevuld met volledige content (P0-P3)
- V2.6: INDEX.md herbouwd, README.md geupdate

**Totaal: 53 skills, ~85% Frappe surface area dekking**
- 7 categorieen: syntax (11), core (7), impl (13), errors (7), ops (8), agents (5), testing (2)
- Alle skills geverifieerd tegen officiele Frappe docs
- MIT license, v2.0 metadata, Frappe v14-v16 compatible

**Nog te doen (handmatig):**
- Repository rename naar `Frappe_Claude_Skill_Package`
- GitHub topics bijwerken
- Release tag v2.0.0

---

### 2026-01-18 (sessie 24) - Fase 8.8 COMPLEET

**GitHub Community Standards:**
- CONTRIBUTING.md toegevoegd met skill development guidelines
- SECURITY.md toegevoegd met vulnerability policy
- CHANGELOG.md toegevoegd in Keep a Changelog format
- Issue templates: bug_report.yml, feature_request.yml, config.yml
- PR template: PULL_REQUEST_TEMPLATE.md
- CODE_OF_CONDUCT.md overgeslagen (content filter issues)
- Score: 6/7 ✅

**Status:** Repository ready for public release!

---

### 2026-01-18 (sessie 23) - Fase 8.8 Planning

**GitHub Best Practices Research:**
- Gap analyse uitgevoerd tegen GitHub community standards
- Huidige score: 2/7 (alleen README + LICENSE)
- 9 bestanden geïdentificeerd die ontbreken
- Fase 8.8 plan opgesteld

**Fase 8.6-8.7 Compleet:**
- USAGE.md + platform guides
- README.md volledig herschreven
- Issue #14 aangemaakt voor topics (handmatig)

---

### 2026-01-18 (sessie 22) - Fase 8.1-8.4

**Fase 8.1-8.4:**
- V16 skill updates (9 skills)
- 28/28 skills gevalideerd
- Agent Skills standaard review compleet
- Issues #4, #9, #10 gesloten

---

### Eerdere sessies

- **Sessie 21**: Fase 8 planning, V16 audit
- **Sessie 20**: 🎉 v1.0 RELEASE
- **Sessie 19**: Fase 6 - Agents
- **Sessie 18**: Fase 5 - Error handling
- **Sessie 17**: Fase 4.6-4.7
- **Sessie 16**: Fase 4.5
- **Sessie 15**: Fase 4.4
- **Sessie 14**: Fase 4.3
- **Sessie 13**: Masterplan v3
- **Sessie 12**: Documentatie sync
- **Sessie 11**: Fase 4.2
- **Sessie 10**: Engels-only herstructurering
- **Sessie 1-9**: Research, Syntax, Core skills

---

## Next Steps

🎉 **V3.0 feature-complete! 61 skills, ~95% coverage.**

Alles compleet:
- ✅ Release tag v3.0.0
- ✅ GitHub release gepubliceerd
- ✅ Social preview banner bijgewerkt (61 skills)

---

## Future Considerations

Deze items zijn niet gepland maar kunnen in de toekomst worden overwogen:

- [ ] Plugin marketplace publicatie
- [ ] Meer agents (debugging, migration, etc.)
- [ ] Community contributions
- [ ] Video tutorials

---

## Legenda

| Symbool | Betekenis |
|:-------:|----------:|
| ✅ | Voltooid |
| 🔄 | In progress |
| ⏳ | Gepland |
| ⏭️ | Skipped |
| ❌ | Vervallen |
| 🔴 | Hoge prioriteit |
| 🟡 | Medium prioriteit |
| 🟢 | Lage prioriteit |
