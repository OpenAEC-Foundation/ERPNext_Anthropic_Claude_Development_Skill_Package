# 📊 ERPNext Skills Package - Roadmap & Status

> **Laatste update**: 2026-01-17  
> **Huidige fase**: Fase 4 - Implementation Skills (in progress)

---

## Quick Status

| Categorie | Voltooid | In Progress | Gepland | Totaal |
|-----------|:--------:|:-----------:|:-------:|:------:|
| Research | 13 | 0 | 0 | 13 |
| Syntax Skills | 8 | 0 | 0 | 8 |
| Core Skills | 3 | 0 | 0 | 3 |
| Implementation Skills | 1 | 0 | 7 | 8 |
| Error Handling Skills | 0 | 0 | 7 | 7 |
| Agents | 0 | 0 | 2 | 2 |
| **Totaal** | **25** | **0** | **16** | **41** |

**Voortgang**: ████████████████░░░░ ~61%

---

## Fase Overzicht

### ✅ Fase 1: Foundational Research & Initial Skills (COMPLEET)
*Alle stappen voltooid - zie vorige ROADMAP versies voor details*

### ✅ Fase 2: Syntax Skills (COMPLEET - 8/8)
*Alle stappen voltooid - zie vorige ROADMAP versies voor details*

### ✅ Fase 3: Core Skills (COMPLEET - 3/3)
*Alle stappen voltooid - zie vorige ROADMAP versies voor details*

---

### 🔄 Fase 4: Implementation Skills (In Progress - 1/8)

Elke impl-skill vereist upload van corresponderende syntax skill.

| Stap | Skill | Status | Output |
|------|-------|:------:|--------|
| 4.1 | erpnext-impl-clientscripts | ✅ | NL + EN + 3 refs |
| 4.2 | erpnext-impl-serverscripts | ⏳ | - |
| 4.3 | erpnext-impl-controllers | ⏳ | - |
| 4.4 | erpnext-impl-hooks | ⏳ | - |
| 4.5 | erpnext-impl-whitelisted | ⏳ | - |
| 4.6 | erpnext-impl-jinja | ⏳ | - |
| 4.7 | erpnext-impl-scheduler | ⏳ | - |
| 4.8 | erpnext-impl-customapp | ⏳ | - |

---

### ⏳ Fase 5: Error Handling Skills (Gepland)

| Stap | Skill | Status |
|------|-------|:------:|
| 5.1 | erpnext-errors-clientscripts | ⏳ |
| 5.2 | erpnext-errors-serverscripts | ⏳ |
| 5.3 | erpnext-errors-controllers | ⏳ |
| 5.4 | erpnext-errors-hooks | ⏳ |
| 5.5 | erpnext-errors-whitelisted | ⏳ |
| 5.6 | erpnext-errors-jinja | ⏳ |
| 5.7 | erpnext-errors-scheduler | ⏳ |

---

### ⏳ Fase 6: Intelligent Agents (Gepland)

| Stap | Agent | Functie | Uploads Vereist |
|------|-------|---------|-----------------| 
| 6.1 | erpnext-interpreter | Vage input → technische specs | 8 syntax skills |
| 6.2 | erpnext-validator | Code verificatie tegen skills | 23 skills |

---

### ⏳ Fase 7: Finalisatie (Gepland)

| Stap | Taak | Status |
|------|------|:------:|
| 7.1 | Dependencies documenteren | ⏳ |
| 7.2 | Final packaging | ⏳ |
| 7.3 | README finaliseren | ⏳ |

---

## Voltooide Skills Overzicht

| Skill | NL | EN | Reference Files |
|-------|:--:|:--:|-----------------|
| erpnext-syntax-clientscripts | ✅ | ✅ | events, methods, examples, anti-patterns |
| erpnext-syntax-serverscripts | ✅ | ✅ | events, methods, examples, anti-patterns |
| erpnext-syntax-controllers | ✅ | ✅ | lifecycle, methods, flags, examples, anti-patterns |
| erpnext-syntax-hooks | ✅ | ✅ | doc-events, scheduler, bootinfo, overrides, permissions, fixtures |
| erpnext-syntax-whitelisted | ✅ | ✅ | decorator, parameters, responses, client-calls |
| erpnext-syntax-jinja | ✅ | ✅ | context, methods, filters, examples, anti-patterns |
| erpnext-syntax-scheduler | ✅ | ✅ | scheduler, enqueue, queues, examples, anti-patterns |
| erpnext-syntax-customapp | ✅ | ✅ | structure, pyproject, modules, patches, fixtures, examples, anti-patterns |
| erpnext-database | ✅ | ✅ | methods, queries, caching, examples, anti-patterns |
| erpnext-permissions | ✅ | ✅ | types, api, hooks, examples, anti-patterns |
| erpnext-api-patterns | ✅ | ✅ | authentication, resource, method, rest, rpc, webhooks, examples, anti-patterns |
| **erpnext-impl-clientscripts** | ✅ | ✅ | **decision-tree, workflows, examples** |

---

## Belangrijke Ontdekkingen

Gedocumenteerd in `LESSONS_LEARNED.md`:

1. **Server Scripts Sandbox**: Alle imports geblokkeerd - gebruik `frappe.utils.*` namespace
2. **hooks.py Resolution**: "Last writer wins" principe
3. **Scheduler**: v15 tick interval 60s (was 4 min in v14)
4. **on_change hook**: Triggert na ELKE modificatie inclusief `db_set`
5. **Wijzigingen na on_update**: Worden NIET automatisch opgeslagen
6. **Report Print Formats**: Gebruiken JavaScript templating, NIET Jinja
7. **pyproject.toml**: Frappe gebruikt flit_core, `__version__` in `__init__.py` is VERPLICHT
8. **Patches INI secties**: `[pre_model_sync]` voor oude velden, `[post_model_sync]` voor nieuwe
9. **db_set**: Bypassed alle ORM validaties - gebruik met voorzichtigheid
10. **Transaction hooks**: Beschikbaar vanaf v15 voor commit/rollback callbacks

---

## Volgende Stappen

1. **Fase 4.2**: erpnext-impl-serverscripts (vereist upload syntax-serverscripts)
2. **Fase 4.3-4.8**: Remaining implementation skills

---

## Legenda

| Symbool | Betekenis |
|:-------:|-----------|
| ✅ | Voltooid |
| 🔄 | In progress |
| ⏳ | Gepland |
| ❌ | Geblokkeerd |

---

## Changelog

### 2026-01-17 (sessie 10) - MID-PROJECT REVIEW & ANTHROPIC TOOLING ANALYSE
- **MID-PROJECT REVIEW UITGEVOERD** @ 61% voortgang
- **KRITIEKE ONTDEKKING**: Skill structuur niet compatibel met Anthropic tooling!
  - `quick_validate.py` verwacht SKILL.md in folder ROOT
  - NL/EN subfolders werken NIET met officiële tooling
  - Nieuwe structuur: aparte folders met `-nl`/`-en` suffix
- Amendment 5 v2: Anthropic-conforme directory structuur gedefinieerd
- Amendment 5 v2: Verplichte validatie met quick_validate.py toegevoegd
- LESSONS_LEARNED.md uitgebreid met secties 8-13:
  - Sectie 8-11: Project structuur en AI workflow lessen
  - Sectie 12: Anthropic Tooling Compatibiliteit (kritiek!)
  - Sectie 13: Uitgebreide Top 15 lessen
- **VOLGENDE**: Migratie naar Anthropic-conforme structuur (56 aparte skill folders)

### 2026-01-17 (sessie 9)
- **Fase 4.1 COMPLEET**: erpnext-impl-clientscripts skill
- NL + EN versies met 3 reference files elk:
  - decision-tree.md (event selection guide)
  - workflows.md (7 implementation patterns)
  - examples.md (10 complete examples)
- **START FASE 4**: Implementation Skills
- Voortgang: 58% → 61%

### 2026-01-17 (sessie 8)
- AUDIT & FIX: Alle missende .skill packages gecreëerd
- ALLE 11 SKILLS NU VOLLEDIG PACKAGED (22 .skill files)

### 2026-01-17 (sessie 7)
- Fase 3.3: Reference files vervolledigd
- **FASE 3 DEFINITIEF COMPLEET**

### 2026-01-17 (sessie 6)
- Fase 3.3 voltooid: erpnext-api-patterns skill
- **FASE 3 COMPLEET**

### 2026-01-17 (sessie 5)
- Fase 3.1 + 3.2 voltooid

### 2026-01-17 (sessie 4)
- **FASE 2 COMPLEET** - Alle 8 syntax skills voltooid

---

*Document gegenereerd als onderdeel van ERPNext Skills Package*
