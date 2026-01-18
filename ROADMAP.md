# ROADMAP - ERPNext Skills Package

> **📍 Dit is de SINGLE SOURCE OF TRUTH voor project status en voortgang.**  
> Claude Project Instructies verwijzen hiernaar - geen dubbele tracking.

> **Laatste update**: 2026-01-18  
> **Huidige fase**: Fase 5 Error Handling Skills  
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
| Error Handling Skills | 3 | 4 | 7 |
| Agents | 0 | 2 | 2 |
| **TOTAAL Skills** | **22** | **6** | **28** |

**Voortgang**: ██████████████████░░ ~79%

---

## V16 Compatibility Status

| Aspect | Status | Notes |
|--------|:------:|-------|
| `extend_doctype_class` hook | ✅ | Gedocumenteerd in impl-hooks |
| Data masking | ⏳ | Te documenteren in permissions skill |
| UUID naming | ⏳ | Te documenteren in controllers skill |
| Chrome PDF rendering | ✅ | Gedocumenteerd in impl-jinja |
| Scheduler tick interval | ✅ | Gedocumenteerd in impl-scheduler |

---

## Volgende Stappen

1. **Fase 5.4**: erpnext-errors-hooks
2. **Fase 5.5-5.7**: Remaining error handling skills
3. **Fase 6**: Agents (2 agents)
4. **Fase 7**: Finalisatie en packaging

---

## Directory Structuur (Post-Migratie)

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
├── errors/           # 3/7 skills 🔄
│   ├── erpnext-errors-clientscripts/ ✅
│   ├── erpnext-errors-serverscripts/ ✅
│   └── erpnext-errors-controllers/ ✅
│
└── agents/           # 0/2 agents ⏳
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

### 🔄 Fase 5: Error Handling Skills (3/7 - IN PROGRESS)

| Stap | Skill | Status |
|------|-------|:------:|
| 5.1 | erpnext-errors-clientscripts | ✅ |
| 5.2 | erpnext-errors-serverscripts | ✅ |
| 5.3 | erpnext-errors-controllers | ✅ |
| 5.4 | erpnext-errors-hooks | ⏳ |
| 5.5 | erpnext-errors-database | ⏳ |
| 5.6 | erpnext-errors-permissions | ⏳ |
| 5.7 | erpnext-errors-api | ⏳ |

### ⏳ Fase 6: Agents (0/2 - GEPLAND)
### ⏳ Fase 7: Finalisatie (GEPLAND)

---

## Changelog

### 2026-01-18 (sessie 18 cont.) - FASE 5.3 COMPLEET

**Voltooid:**
- erpnext-errors-controllers skill compleet met:
  - SKILL.md: Decision tree per lifecycle hook, transaction rollback behavior, error methods reference
  - references/patterns.md: 7 complete error handling patterns (validation class, external API, batch processing, controller override, async operations, change detection, linked document updates)
  - references/examples.md: 3 complete production-ready examples (Sales Order full controller, Payment processing with API, Data migration with tracking)
  - references/anti-patterns.md: 16 common controller error handling mistakes

**Key differences from Server Scripts documented:**
- Controllers CAN use try/except (no sandbox)
- Transaction rollback varies by hook (validate vs on_update)
- Changes after on_update are NOT saved (use db_set)
- Critical validations belong in before_submit, not on_submit

**Nieuwe voortgang**: ~79% (was ~75%)

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
