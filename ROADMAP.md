# ROADMAP - ERPNext Skills Package

> **📍 Dit is de SINGLE SOURCE OF TRUTH voor project status en voortgang.**  
> Claude Project Instructies verwijzen hiernaar - geen dubbele tracking.

> **Laatste update**: 2026-01-18  
> **Huidige fase**: Fase 6 Agents  
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
| Agents | 0 | 2 | 2 |
| **TOTAAL Skills** | **26** | **2** | **28** |

**Voortgang**: ████████████████████ ~93%

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

1. **Fase 6**: Agents (2 agents - code-generator, code-reviewer)
2. **Fase 7**: Finalisatie en packaging

🎉 **FASE 5 ERROR HANDLING COMPLEET!**

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
├── errors/           # 7/7 skills ✅
│   ├── erpnext-errors-clientscripts/ ✅
│   ├── erpnext-errors-serverscripts/ ✅
│   ├── erpnext-errors-controllers/ ✅
│   ├── erpnext-errors-hooks/ ✅
│   ├── erpnext-errors-database/ ✅
│   ├── erpnext-errors-permissions/ ✅
│   └── erpnext-errors-api/ ✅
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

### ⏳ Fase 6: Agents (0/2 - GEPLAND)
### ⏳ Fase 7: Finalisatie (GEPLAND)

---

## Changelog

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

**Nieuwe voortgang**: ~93% (was ~89%)
**Nog te doen**: Fase 6 (2 Agents) + Fase 7 (Finalisatie)

### 2026-01-18 (sessie 18 cont.) - FASE 5.6 COMPLEET

**Voltooid:**
- erpnext-errors-permissions skill compleet met:
  - SKILL.md: Decision tree by context, permission hook patterns, API permission handling
  - references/patterns.md: 6 complete patterns (has_permission, permission_query_conditions, API endpoint, controller, graceful degradation, security audit)
  - references/examples.md: 3 complete examples (hooks.py config, API endpoints, client-side)
  - references/anti-patterns.md: 15 common permission error handling mistakes

**Key patterns documented:**
- has_permission hooks should NEVER throw (return False to deny)
- permission_query_conditions should NEVER throw (return restrictive SQL)
- Always use frappe.db.escape() in SQL conditions
- Use frappe.get_list() not frappe.get_all() for user-facing queries
- Log denied access for security audit
- Handle None values safely in permission hooks

**Nieuwe voortgang**: ~89% (was ~86%)

### 2026-01-18 (sessie 18 cont.) - FASE 5.5 COMPLEET

**Voltooid:**
- erpnext-errors-database skill compleet met:
  - SKILL.md: Exception types reference, decision tree by operation, transaction handling
  - references/patterns.md: 7 complete error handling patterns (DocumentManager class, batch operations, safe queries, query builder, transactions with savepoints, existence checks, connection retry)
  - references/examples.md: 5 complete production-ready examples (customer CRUD API, data import, report queries, background job, controller with DB ops)
  - references/anti-patterns.md: 15 common database error handling mistakes

**Key exceptions documented:**
- DoesNotExistError - document not found
- DuplicateEntryError - unique constraint violation  
- LinkExistsError - cannot delete linked document
- TimestampMismatchError - concurrent edit detected
- InternalError - database-level errors (deadlock, connection)

**Nieuwe voortgang**: ~86% (was ~82%)

### 2026-01-18 (sessie 18 cont.) - FASE 5.4 COMPLEET

**Voltooid:**
- erpnext-errors-hooks skill compleet met:
  - SKILL.md: Decision tree per hook type, transaction behavior, error method reference
  - references/patterns.md: 7 complete error handling patterns (doc_events multi-operation, scheduler with tracking, permission query, has_permission, override class, extend_bootinfo, wildcard handler)
  - references/examples.md: 5 complete production-ready examples (hooks.py config, sales invoice events, scheduler task, permission hooks, boot extension)
  - references/anti-patterns.md: 15 common hooks error handling mistakes

**Key differences documented:**
- permission_query_conditions and has_permission should NEVER throw
- extend_bootinfo errors break entire page load
- Scheduler tasks have NO user feedback - logging is critical
- Wildcard (*) handlers must never break other apps' saves
- Multiple apps can register handlers - order matters

**Nieuwe voortgang**: ~82% (was ~79%)

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
