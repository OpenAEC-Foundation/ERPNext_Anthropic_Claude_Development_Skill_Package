# ROADMAP - ERPNext Skills Package

> **📍 Dit is de SINGLE SOURCE OF TRUTH voor project status en voortgang.**  
> Claude Project Instructies verwijzen hiernaar - geen dubbele tracking.

> **Laatste update**: 2026-01-18  
> **Huidige fase**: Fase 7 Finalisatie  
> **Masterplan**: [erpnext-skills-masterplan-v3.md](docs/masterplan/erpnext-skills-masterplan-v3.md)  
> **Structuur**: Engels-only, Anthropic-conform, V14/V15/V16 compatible

---

## Quick Status

| Categorie | Voltooid | Te Maken | Totaal |
|-----------|:--------:|:--------:|:------:|
| Research | 13 | 0 | 13 |
| Syntax Skills | 8 | 0 | 8 |
| Core Skills | 3 | 0 | 3 |
| Implementation Skills | 8 | 0 | 8 |
| Error Handling Skills | 7 | 0 | 7 |
| Agents | 2 | 0 | 2 |
| **TOTAAL Skills** | **28** | **0** | **28** |

**Voortgang**: ████████████████████ **100%** 🎉

---

## V16 Compatibility Status

| Aspect | Status | Notes |
|--------|:------:|-------|
| `extend_doctype_class` hook | ✅ | Gedocumenteerd in impl-hooks |
| Data masking | ✅ | Gedocumenteerd in erpnext-permissions |
| UUID naming | ✅ | Gedocumenteerd in syntax-controllers |
| Chrome PDF rendering | ✅ | Gedocumenteerd in impl-jinja |
| Scheduler tick interval | ✅ | Gedocumenteerd in impl-scheduler |

**V16 Compatibility Review: COMPLEET ✅**

---

## Volgende Stappen

1. **Fase 7**: Finalisatie en packaging
   - ~~V16 Compatibility Review van alle skills~~ ✅
   - Dependencies matrix
   - Final packaging (28 .skill files)
   - INDEX.md en INSTALL.md
   - Archive oude amendments

🎉 **ALLE 28 SKILLS EN AGENTS COMPLEET!**
🎉 **V16 COMPATIBILITY REVIEW COMPLEET!**

---

## Directory Structuur (Compleet)

```
skills/source/
├── syntax/           # 8 skills ✅
│   ├── erpnext-syntax-clientscripts/
│   ├── erpnext-syntax-serverscripts/
│   ├── erpnext-syntax-controllers/
│   ├── erpnext-syntax-hooks/
│   ├── erpnext-syntax-whitelisted/
│   ├── erpnext-syntax-jinja/
│   ├── erpnext-syntax-scheduler/
│   └── erpnext-syntax-customapp/
│
├── core/             # 3 skills ✅
│   ├── erpnext-database/
│   ├── erpnext-permissions/
│   └── erpnext-api-patterns/
│
├── impl/             # 8 skills ✅
│   ├── erpnext-impl-clientscripts/
│   ├── erpnext-impl-serverscripts/
│   ├── erpnext-impl-controllers/
│   ├── erpnext-impl-hooks/
│   ├── erpnext-impl-whitelisted/
│   ├── erpnext-impl-jinja/
│   ├── erpnext-impl-scheduler/
│   └── erpnext-impl-customapp/
│
├── errors/           # 7 skills ✅
│   ├── erpnext-errors-clientscripts/
│   ├── erpnext-errors-serverscripts/
│   ├── erpnext-errors-controllers/
│   ├── erpnext-errors-hooks/
│   ├── erpnext-errors-database/
│   ├── erpnext-errors-permissions/
│   └── erpnext-errors-api/
│
└── agents/           # 2 agents ✅
    ├── erpnext-code-interpreter/
    └── erpnext-code-validator/
```

---

## Fase Overzicht

### ✅ Research (13/13 - COMPLEET)
Alle research documenten in `docs/research/`.

### ✅ Fase 2: Syntax Skills (8/8 - COMPLEET)
Alle 8 syntax skills gemigreerd naar `skills/source/syntax/`.

### ✅ Fase 3: Core Skills (3/3 - COMPLEET)
Alle 3 core skills gemigreerd naar `skills/source/core/`.

### ✅ Fase 4: Implementation Skills (8/8 - COMPLEET)
Alle 8 implementation skills in `skills/source/impl/`.

### ✅ Fase 5: Error Handling Skills (7/7 - COMPLEET)

| Stap | Skill | Status |
|------|-------|:------:|
| 5.1 | erpnext-errors-clientscripts | ✅ |
| 5.2 | erpnext-errors-serverscripts | ✅ |
| 5.3 | erpnext-errors-controllers | ✅ |
| 5.4 | erpnext-errors-hooks | ✅ |
| 5.5 | erpnext-errors-database | ✅ |
| 5.6 | erpnext-errors-permissions | ✅ |
| 5.7 | erpnext-errors-api | ✅ |

### ✅ Fase 6: Agents (2/2 - COMPLEET)

| Stap | Agent | Status | Beschrijving |
|------|-------|:------:|--------------|
| 6.1 | erpnext-code-interpreter | ✅ | Vage requirements → technische specs |
| 6.2 | erpnext-code-validator | ✅ | Code validatie tegen alle skills |

### 🔄 Fase 7: Finalisatie (IN PROGRESS)

| Stap | Taak | Status |
|------|------|:------:|
| 7.1 | V16 Compatibility Review | ✅ |
| 7.2 | Dependencies Matrix | ⏳ |
| 7.3 | INDEX.md & INSTALL.md | ⏳ |
| 7.4 | Final Packaging (.skill files) | ⏳ |
| 7.5 | Cleanup & Archive | ⏳ |

---

## Changelog

### 2026-01-18 (sessie 20) - FASE 7.1 V16 COMPATIBILITY REVIEW COMPLEET ✅

**Voltooid:**

**7.1 V16 Compatibility Review:**
- Updated `erpnext-permissions` skill (v1.0.0 → v1.1.0):
  - Added comprehensive Data Masking section
  - Documented `mask` permission type
  - Added supported field types for masking
  - Added critical warning for custom SQL queries
  - Updated decision tree with Data Masking option
  - Added v16 to Version Differences table

- Updated `erpnext-syntax-controllers` skill:
  - Added UUID naming documentation
  - Documented `autoname = "UUID"` option
  - Added UUID vs traditional naming decision tree
  - Updated Version Differences table with v16 features
  - Added UUID in Link fields (native format) note

**V16 Compatibility Status: ALL ITEMS COMPLETE**
| Item | Skill | Status |
|------|-------|--------|
| extend_doctype_class | impl-hooks | ✅ |
| Data masking | erpnext-permissions | ✅ |
| UUID naming | syntax-controllers | ✅ |
| Chrome PDF | impl-jinja | ✅ |
| Scheduler tick | impl-scheduler | ✅ |

**Also created**: GitHub Issue #9 for Agent Skills standard review (agentskills.io)

---

### 2026-01-18 (sessie 19) - FASE 6 COMPLEET! 🎉🎉

**Voltooid:**

**6.1 erpnext-code-interpreter agent:**
- SKILL.md (313 regels): Interpretation workflow, mechanism selection matrix, clarifying questions framework, specification template, skill dependencies map, common pattern recognition
- references/workflow.md: 5-step interpretation process met gedetailleerde decision trees
- references/examples.md: 6 complete interpretation examples (auto-calculate, notification, external integration, permission filtering, workflow, scheduled task)
- references/checklists.md: Pre-interpretation checklist, step-by-step checklists, output quality checklist, common pitfalls, quick reference

**6.2 erpnext-code-validator agent:**
- SKILL.md (332 regels): Validation workflow, critical checks per code type (Server Script, Client Script, Controller), validation report format, universal rules, version-specific validations
- references/workflow.md: 5-step validation process, type-specific checks, severity classification
- references/checklists.md: Complete validation checklists voor Server Script, Client Script, Controller, hooks.py, Jinja, Whitelisted Methods, universal security
- references/examples.md: 6 validation examples met corrected code (import error, async issue, on_update modification, SQL injection, version issue, clean code)

**🎉🎉 ALLE 28 SKILLS EN AGENTS VOLTOOID! 🎉🎉**

**Milestone bereikt**: 100% van skills/agents compleet
- 8 Syntax Skills
- 3 Core Skills
- 8 Implementation Skills
- 7 Error Handling Skills
- 2 Agents

**Volgende**: Fase 7 - Finalisatie en packaging

### 2026-01-18 (sessie 18 cont.) - FASE 5 COMPLEET! 🎉

**Voltooid:**
- erpnext-errors-api skill compleet met:
  - SKILL.md: HTTP status codes, whitelisted method patterns, client-side handling, webhook errors
  - references/patterns.md: 5 complete patterns (whitelisted method, response wrapper, client handler class, external API client, webhook handler)
  - references/examples.md: 3 complete examples (API module, client-side, external integration)
  - references/anti-patterns.md: 15 common API error handling mistakes

**🎉 FASE 5 ERROR HANDLING SKILLS VOLLEDIG AFGEROND!**

Alle 7 error handling skills compleet:
1. ✅ errors-clientscripts
2. ✅ errors-serverscripts
3. ✅ errors-controllers
4. ✅ errors-hooks
5. ✅ errors-database
6. ✅ errors-permissions
7. ✅ errors-api

### 2026-01-18 (sessie 18 cont.) - FASE 5.6 COMPLEET

**Voltooid:**
- erpnext-errors-permissions skill compleet met:
  - SKILL.md: Decision tree by context, permission hook patterns, API permission handling
  - references/patterns.md: 6 complete patterns (has_permission, permission_query_conditions, API endpoint, controller, graceful degradation, security audit)
  - references/examples.md: 3 complete examples (hooks.py config, API endpoints, client-side)
  - references/anti-patterns.md: 15 common permission error handling mistakes

### 2026-01-18 (sessie 18 cont.) - FASE 5.5 COMPLEET

**Voltooid:**
- erpnext-errors-database skill compleet met:
  - SKILL.md: Exception types reference, decision tree by operation, transaction handling
  - references/patterns.md: 7 complete error handling patterns
  - references/examples.md: 5 complete production-ready examples
  - references/anti-patterns.md: 15 common database error handling mistakes

### 2026-01-18 (sessie 18 cont.) - FASE 5.4 COMPLEET

**Voltooid:**
- erpnext-errors-hooks skill compleet

### 2026-01-18 (sessie 18 cont.) - FASE 5.3 COMPLEET

**Voltooid:**
- erpnext-errors-controllers skill compleet

### 2026-01-18 (sessie 18 cont.) - FASE 5.1 & 5.2 COMPLEET

**Voltooid:**
- erpnext-errors-clientscripts skill compleet
- erpnext-errors-serverscripts skill compleet

### 2026-01-18 (sessie 18) - FASE 4 COMPLEET! 🎉

**Voltooid:**
- erpnext-impl-customapp skill compleet

**Milestone bereikt**: Alle 8 Implementation Skills zijn nu voltooid!

### Eerdere sessies
- Sessie 17: Fase 4.6, 4.7 compleet
- Sessie 16: Fase 4.5 compleet
- Sessie 15: Fase 4.4 compleet
- Sessie 14: Fase 4.3 compleet
- Sessie 13: Masterplan v3 consolidatie
- Sessie 12: Documentatie sync
- Sessie 11: Fase 4.2 compleet
- Sessie 10: Grote herstructurering (Engels-only)
- Sessie 9: Fase 4.1 compleet
- Sessie 1-8: Research, Syntax, Core skills

---

## Legenda

| Symbool | Betekenis |
|:-------:|----------:|
| ✅ | Voltooid |
| 🔄 | In progress |
| ⏳ | Gepland |
