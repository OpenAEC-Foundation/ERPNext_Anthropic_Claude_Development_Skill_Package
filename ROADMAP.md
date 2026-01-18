# ROADMAP - ERPNext Skills Package

> **Laatste update**: 2026-01-18  
> **Huidige fase**: Fase 4 Implementation Skills  
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

## Volgende Stappen

1. **Fase 4.3**: erpnext-impl-controllers
2. **Fase 4.4**: erpnext-impl-hooks
3. **Fase 4.5-4.8**: Overige implementation skills

---

## Changelog

### 2026-01-18 (sessie 11) - FASE 4.2 VOLTOOID

**Nieuwe skill gemaakt:**
- `erpnext-impl-serverscripts` - Complete implementation skill voor Server Scripts

**Structuur:**
- SKILL.md (369 regels) - Hoofd workflow document
- references/decision-tree.md - Complete beslisboom
- references/workflows.md - 7 categorieën implementatie patronen
- references/examples.md - 10 complete voorbeelden

**Inhoud:**
- Server Script vs Controller beslisboom
- 4 script types: Document Event, API, Scheduler, Permission Query
- Event name mapping (UI vs internal hooks)
- 6 core workflows in SKILL.md
- 7 workflow categorieën in references
- Client + Server integration patronen
- Implementation checklist

**Voortgang**: 43% → 46%

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

### 2026-01-17 (sessie 10 - vervolg) - CLEANUP VOLTOOID

**Verwijderd:**
- Alle NL versies en folders (~100 bestanden)
- Alle oude EN/CORE en NL/CORE folders
- Alle oude .skill packages met taal suffix
- Alle ghost folders met reference files
- README.md bestanden uit skills/

**Opgeschoond:**
- LESSONS_LEARNED.md: 1500+ → 329 regels (correcte nummering)

**Finale structuur:**
```
skills/source/
├── syntax/   8 skills ✅
├── core/     3 skills ✅
└── impl/     2 skills ✅
```

### Eerdere sessies
- Sessie 9: Fase 4.1 compleet
- Sessie 1-8: Research, Syntax, Core skills

---

## Legenda

| Symbool | Betekenis |
|:-------:|-----------:|
| ✅ | Voltooid |
| 🔄 | In progress |
| ⏳ | Gepland |
