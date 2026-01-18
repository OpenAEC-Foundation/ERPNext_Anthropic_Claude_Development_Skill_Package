# ROADMAP - ERPNext Skills Package

> **📍 Dit is de SINGLE SOURCE OF TRUTH voor project status en voortgang.**  
> Claude Project Instructies verwijzen hiernaar - geen dubbele tracking.

> **Laatste update**: 2026-01-18  
> **Huidige fase**: Fase 4.3 Implementation Skills  
> **Structuur**: Engels-only, Anthropic-conform

---

## Quick Status

| Categorie | Voltooid | Te Maken | Totaal |
|-----------|:--------:|:--------:|:------:|
| Research | 13 | 0 | 13 |
| Syntax Skills | 8 | 0 | 8 |
| Core Skills | 3 | 0 | 3 |
| Implementation Skills | 2 | 6 | 8 |
| Error Handling Skills | 0 | 7 | 7 |
| Agents | 0 | 2 | 2 |
| **TOTAAL Skills** | **13** | **15** | **28** |

**Voortgang**: █████████░░░░░░░░░░░ ~46%

---

## Volgende Stappen

1. **Fase 4.3**: erpnext-impl-controllers
2. **Fase 4.4**: erpnext-impl-hooks
3. **Fase 4.5-4.8**: Overige implementation skills

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
├── impl/             # 2/8 skills 🔄
│   ├── erpnext-impl-clientscripts/ ✅
│   └── erpnext-impl-serverscripts/ ✅
│
├── errors/           # 0/7 skills ⏳
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

### 🔄 Fase 4: Implementation Skills (2/8 - IN PROGRESS)

| Stap | Skill | Status |
|------|-------|:------:|
| 4.1 | erpnext-impl-clientscripts | ✅ |
| 4.2 | erpnext-impl-serverscripts | ✅ |
| 4.3 | erpnext-impl-controllers | ⏳ |
| 4.4 | erpnext-impl-hooks | ⏳ |
| 4.5 | erpnext-impl-whitelisted | ⏳ |
| 4.6 | erpnext-impl-jinja | ⏳ |
| 4.7 | erpnext-impl-scheduler | ⏳ |
| 4.8 | erpnext-impl-customapp | ⏳ |

### ⏳ Fase 5: Error Handling Skills (0/7 - GEPLAND)
### ⏳ Fase 6: Agents (0/2 - GEPLAND)
### ⏳ Fase 7: Finalisatie (GEPLAND)

---

## Changelog

### 2026-01-18 (sessie 12) - DOCUMENTATIE SYNC & CLEANUP

**Documentatie bijgewerkt:**
- WAY_OF_WORK.md: Session Recovery Protocol + Project Status Tracking sectie
- LESSONS_LEARNED.md: Sectie 9 (Session Recovery) + Sectie 10 (Single Source of Truth)
- README.md: Status tabel bijgewerkt naar 46% (13/28 skills)
- ROADMAP.md: Header "Single Source of Truth" + verplichte update na elke fase

**Claude Project Instructies refactor:**
- Status tracking VERWIJDERD uit instructies (was verouderd)
- Verwijzing naar ROADMAP.md als enige bron voor status
- ROADMAP update nu expliciet VERPLICHT na elke fase
- Session Recovery Protocol trigger toegevoegd

**Issues opgeschoond:**
- Issue #1 gesloten (duplicate van #4 - V16 compat)
- Issue #2 gesloten (duplicate van #5 - Claude Code format)
- Issue #7 gesloten (Session Recovery - geïmplementeerd)
- Issue #8 bijna klaar (wacht op handmatige instructies update)

**Key insight:**
> "Nooit status tracking op meerdere plekken. ROADMAP.md is single source of truth."

### 2026-01-18 (sessie 11) - FASE 4.2 COMPLEET

**Voltooid:**
- erpnext-impl-serverscripts skill compleet met:
  - SKILL.md: Main decision trees en workflows
  - references/decision-tree.md: Complete script type selection
  - references/workflows.md: Extended implementation patterns
  - references/examples.md: 12+ complete working examples
  - references/anti-patterns.md: Common mistakes and solutions

**Nieuwe voortgang**: ~46% (was ~43%)

### 2026-01-17 (sessie 10) - GROTE HERSTRUCTURERING

**Strategische Beslissingen:**
- **ENGELS-ONLY**: Nederlandse skills geschrapt (56 → 28 skills)
- **ANTHROPIC-CONFORM**: SKILL.md direct in folder root

**Migratie Uitgevoerd:**
- 12 EN skills gemigreerd naar nieuwe `skills/source/[categorie]/` structuur
- Oude NL/EN subfolder structuur vervangen

**Documentatie:**
- LESSONS_LEARNED.md: Secties 12-14 toegevoegd
- Amendment 6: Engels-only + definitieve structuur
- ROADMAP: Volledig herschreven

### Eerdere sessies
- Sessie 9: Fase 4.1 compleet
- Sessie 1-8: Research, Syntax, Core skills

---

## Legenda

| Symbool | Betekenis |
|:-------:|----------:|
| ✅ | Voltooid |
| 🔄 | In progress |
| ⏳ | Gepland |
