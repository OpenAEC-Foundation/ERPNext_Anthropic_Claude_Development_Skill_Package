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
| Error Handling Skills | 2 | 5 | 7 |
| Agents | 0 | 2 | 2 |
| **TOTAAL Skills** | **21** | **7** | **28** |

**Voortgang**: █████████████████░░░ ~75%

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

1. **Fase 5.2**: erpnext-errors-serverscripts
2. **Fase 5.3-5.7**: Remaining error handling skills
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
├── errors/           # 2/7 skills 🔄
│   ├── erpnext-errors-clientscripts/ ✅
│   └── erpnext-errors-serverscripts/ ✅
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

### 🔄 Fase 5: Error Handling Skills (2/7 - IN PROGRESS)

| Stap | Skill | Status |
|------|-------|:------:|
| 5.1 | erpnext-errors-clientscripts | ✅ |
| 5.2 | erpnext-errors-serverscripts | ✅ |
| 5.3 | erpnext-errors-controllers | ⏳ |
| 5.4 | erpnext-errors-hooks | ⏳ |
| 5.5 | erpnext-errors-database | ⏳ |
| 5.6 | erpnext-errors-permissions | ⏳ |
| 5.7 | erpnext-errors-api | ⏳ |

### ⏳ Fase 6: Agents (0/2 - GEPLAND)
### ⏳ Fase 7: Finalisatie (GEPLAND)

---

## Changelog

### 2026-01-18 (sessie 18 cont.) - FASE 5.2 COMPLEET

**Voltooid:**
- erpnext-errors-serverscripts skill compleet met:
  - SKILL.md: Sandbox limitations voor error handling, decision tree, error methods reference (throw/msgprint/log_error), transaction behavior, 6 core patterns
  - references/patterns.md: 10 complete error handling patterns (comprehensive validation, safe DB operations, API full error handling, scheduler batch processing, cross-document validation, conditional processing, permission query, dependent field calculation, linked document creation, idempotent scheduler)
  - references/examples.md: 5 complete production-ready examples (Sales Order validation, REST API with full error handling, scheduler with comprehensive error handling, permission query with fallbacks, document event with external integration)
  - references/anti-patterns.md: 17 common server script error handling mistakes

**Key patterns documented:**
- Sandbox restrictions (no try/except, no raise, no imports)
- frappe.throw() vs frappe.msgprint() vs frappe.log_error()
- API error responses with correct HTTP status codes
- Scheduler error isolation and batch processing
- Transaction rollback behavior
- Safe database operations with existence checks

**Nieuwe voortgang**: ~75% (was 71%)

### 2026-01-18 (sessie 18 cont.) - FASE 5.1 COMPLEET

**Voltooid:**
- erpnext-errors-clientscripts skill compleet met:
  - SKILL.md: Main decision tree (error type selection), error feedback methods (throw vs msgprint vs show_alert), 6 core error handling patterns
  - references/patterns.md: 10 complete error handling patterns (form validation, async retry, batch operations, confirmation dialogs, network detection, dependent validation, loading states, global error handler, parallel validation, error boundaries)
  - references/examples.md: 5 complete production-ready examples (Sales Order with full validation, async validation, wizard-style form, real-time stock check with debouncing, external API integration)
  - references/anti-patterns.md: 13 common error handling mistakes to avoid

**Key patterns documented:**
- frappe.throw() vs frappe.msgprint() vs frappe.show_alert()
- Async/await error handling with try/catch
- Collecting multiple validation errors
- Server call error handling (callback + error patterns)
- Graceful degradation for non-critical features
- Debugging techniques

**Nieuwe voortgang**: ~71% (was 68%)

### 2026-01-18 (sessie 18) - FASE 4 COMPLEET! 🎉

**Voltooid:**
- erpnext-impl-customapp skill compleet met:
  - SKILL.md: Main decision trees (app necessity, extension strategy, patch vs fixture, module organization)
  - references/decision-tree.md: 7 complete decision flowcharts
  - references/workflows.md: 8 step-by-step implementation workflows
  - references/examples.md: 5 complete production-ready examples
  - references/anti-patterns.md: 10 categories of common mistakes

**Milestone bereikt**: Alle 8 Implementation Skills zijn nu voltooid!

**Nieuwe voortgang**: ~68% (was ~64%)

### 2026-01-18 (sessie 17 cont.) - FASE 4.7 COMPLEET

**Voltooid:**
- erpnext-impl-scheduler skill compleet met:
  - SKILL.md: Main decision trees, scheduler vs enqueue selection, queue selection
  - references/decision-tree.md: Complete flowcharts for task type, queue, deduplication, error handling
  - references/workflows.md: 8 step-by-step implementation workflows
  - references/examples.md: 5 complete production-ready examples
  - references/anti-patterns.md: 14 common scheduler mistakes to avoid
- V14/V15/V16 version differences documented (tick interval, job_id vs job_name)

**Nieuwe voortgang**: ~64% (was ~61%)

### 2026-01-18 (sessie 17) - FASE 4.6 COMPLEET

**Voltooid:**
- erpnext-impl-jinja skill compleet

### Eerdere sessies
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
