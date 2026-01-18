# ROADMAP - ERPNext Skills Package

> **📍 Dit is de SINGLE SOURCE OF TRUTH voor project status en voortgang.**  
> Claude Project Instructies verwijzen hiernaar - geen dubbele tracking.

> **Laatste update**: 2026-01-18  
> **Huidige fase**: Fase 4.7 Implementation Skills  
> **Masterplan**: [erpnext-skills-masterplan-v3.md](docs/masterplan/erpnext-skills-masterplan-v3.md)  
> **Structuur**: Engels-only, Anthropic-conform, V14/V15/V16 compatible

---

## Quick Status

| Categorie | Voltooid | Te Maken | Totaal |
|-----------|:--------:|:--------:|:------:|
| Research | 13 | 0 | 13 |
| Syntax Skills | 8 | 0 | 8 |
| Core Skills | 3 | 0 | 3 |
| Implementation Skills | 6 | 2 | 8 |
| Error Handling Skills | 0 | 7 | 7 |
| Agents | 0 | 2 | 2 |
| **TOTAAL Skills** | **17** | **11** | **28** |

**Voortgang**: █████████████░░░░░░░ ~61%

---

## V16 Compatibility Status

| Aspect | Status | Notes |
|--------|:------:|-------|
| `extend_doctype_class` hook | ✅ | Gedocumenteerd in impl-hooks |
| Data masking | ⏳ | Te documenteren in permissions skill |
| UUID naming | ⏳ | Te documenteren in controllers skill |
| Chrome PDF rendering | ✅ | Gedocumenteerd in impl-jinja |
| Scheduler tick interval | ✅ | Gedocumenteerd in research |

---

## Volgende Stappen

1. **Fase 4.7**: erpnext-impl-scheduler
2. **Fase 4.8**: erpnext-impl-customapp
3. **Fase 5**: Error Handling Skills
4. **V16 Review**: Alle voltooide skills reviewen op V16 compatibility

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
├── impl/             # 6/8 skills 🔄
│   ├── erpnext-impl-clientscripts/ ✅
│   ├── erpnext-impl-serverscripts/ ✅
│   ├── erpnext-impl-controllers/ ✅
│   ├── erpnext-impl-hooks/ ✅
│   ├── erpnext-impl-whitelisted/ ✅
│   └── erpnext-impl-jinja/ ✅
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

### 🔄 Fase 4: Implementation Skills (6/8 - IN PROGRESS)

| Stap | Skill | Status |
|------|-------|:------:|
| 4.1 | erpnext-impl-clientscripts | ✅ |
| 4.2 | erpnext-impl-serverscripts | ✅ |
| 4.3 | erpnext-impl-controllers | ✅ |
| 4.4 | erpnext-impl-hooks | ✅ |
| 4.5 | erpnext-impl-whitelisted | ✅ |
| 4.6 | erpnext-impl-jinja | ✅ |
| 4.7 | erpnext-impl-scheduler | ⏳ |
| 4.8 | erpnext-impl-customapp | ⏳ |

### ⏳ Fase 5: Error Handling Skills (0/7 - GEPLAND)
### ⏳ Fase 6: Agents (0/2 - GEPLAND)
### ⏳ Fase 7: Finalisatie (GEPLAND)

---

## Changelog

### 2026-01-18 (sessie 17) - FASE 4.6 COMPLEET

**Voltooid:**
- erpnext-impl-jinja skill compleet met:
  - SKILL.md: Main decision trees, template type selection, implementation workflows
  - references/decision-tree.md: Complete template type selection flowcharts
  - references/workflows.md: 8 step-by-step implementation workflows (Print Format, Email Template, Portal Page, Custom jenv methods, Letter Head, Report Print Format)
  - references/examples.md: 5 complete production-ready examples (Professional Invoice, Packing Slip, Order Confirmation Email, Customer Dashboard Portal, Custom Jinja Methods Library)
  - references/anti-patterns.md: 15 common template mistakes to avoid
- V16 Chrome PDF rendering documented
- Report Print Format JS templating clearly distinguished from Jinja

**Nieuwe voortgang**: ~61% (was ~57%)

### 2026-01-18 (sessie 16) - FASE 4.5 COMPLEET

**Voltooid:**
- erpnext-impl-whitelisted skill compleet met:
  - SKILL.md: Main decision trees, permission patterns, security rules
  - references/decision-tree.md: Complete API type and permission selection
  - references/workflows.md: 7 step-by-step implementation workflows
  - references/examples.md: 5 complete production-ready examples
  - references/anti-patterns.md: 12 common security mistakes to avoid
- v15+ rate limiting and type validation documented

**Nieuwe voortgang**: ~57% (was ~54%)

### 2026-01-18 (sessie 15) - FASE 4.4 COMPLEET

**Voltooid:**
- erpnext-impl-hooks skill compleet met:
  - SKILL.md: Main decision trees, hook selection, implementation patterns
  - references/decision-tree.md: Complete hook type selection flowcharts
  - references/workflows.md: 10 step-by-step implementation workflows
  - references/examples.md: 10 complete working examples
  - references/anti-patterns.md: 15 common mistakes to avoid
- V16 `extend_doctype_class` hook fully documented

**Issues opgeschoond:**
- Issue #6 gesloten (cleanup al gedaan)
- Issue #8 gesloten (documentation sync al gedaan)

**Nieuwe voortgang**: ~54% (was ~50%)

### 2026-01-18 (sessie 14) - FASE 4.3 COMPLEET

**Voltooid:**
- erpnext-impl-controllers skill compleet met:
  - SKILL.md: Main decision trees, hook selection, implementation patterns
  - references/decision-tree.md: Complete hook selection with execution orders
  - references/workflows.md: 10 implementation workflows
  - references/examples.md: 8 complete working examples
  - references/anti-patterns.md: 13 common mistakes to avoid

**Issues opgeschoond:**
- Issue #6 gesloten (cleanup al gedaan in eerdere sessie)
- Issue #8 gesloten (documentation sync al gedaan)

**Nieuwe voortgang**: ~50% (was ~46%)

### 2026-01-18 (sessie 13 cont.) - AMENDMENTS CLEANUP

**Amendments gearchiveerd:**
- 10 oude amendment bestanden verplaatst naar `docs/masterplan/amendments/archived/`
- `docs/masterplan/amendments/` nu alleen nog `archived/` subfolder
- Masterplan v3 is nu de enige actieve masterplan versie

**Bestanden gearchiveerd:**
- amendment-5-mid-project-review.md
- amendment-6-english-only-final-structure.md
- masterplan-aanpassing-fase-2_*.md (4 files)
- masterplan-aanvulling-fase-opsplitsingen.md
- masterplan-skill-uploads.md
- skill-uploads-voortgang*.md (2 files)

### 2026-01-18 (sessie 13) - MASTERPLAN V3 CONSOLIDATIE

**Masterplan geconsolideerd:**
- Alle amendments geïntegreerd in `erpnext-skills-masterplan-v3.md`
- V16 compatibility sectie toegevoegd met breaking changes en nieuwe features
- Versie matrix bijgewerkt (v14/v15/v16)

**V16 Nieuwe Features Gedocumenteerd:**
- `extend_doctype_class` hook (veiligere DocType extensie)
- Data masking (field-level privacy)
- UUID naming rule
- Chrome-based PDF generation
- Scheduler tick interval change (4min → 60sec)

**Issues status:**
- Issue #3 (Consolidate masterplan) → ✅ OPGELOST
- Issue #4 (V16 compatibility) → 🔄 Geïntegreerd in masterplan, review nog te doen

### 2026-01-18 (sessie 12) - DOCUMENTATIE SYNC & CLEANUP

**Documentatie bijgewerkt:**
- WAY_OF_WORK.md: Session Recovery Protocol + Project Status Tracking + English-only clarifications
- LESSONS_LEARNED.md: Sectie 9 (Session Recovery) + Sectie 10 (Single Source of Truth)
- README.md: Status tabel bijgewerkt naar 46% (13/28 skills)
- ROADMAP.md: Header "Single Source of Truth" + verplichte update na elke fase

**WAY_OF_WORK.md specifieke updates:**
- Verouderde "Dutch AND English" referenties verwijderd
- Commit message voorbeelden geüpdatet (geen NL+EN meer)
- Post-Phase checklist aangepast voor English-only
- Lesson #4 herschreven: "English-Only Skills" i.p.v. "Bilingual Takes Time"
- v14/v15 → v14/v15/v16 in requirements

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
