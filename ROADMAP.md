# 📊 ERPNext Skills Package - Roadmap & Status

> **Laatste update**: 2026-01-17  
> **Huidige fase**: 2.10 (Jinja Templates Skill)

---

## Quick Status

| Categorie | Voltooid | In Progress | Gepland | Totaal |
|-----------|:--------:|:-----------:|:-------:|:------:|
| Research | 9 | 0 | 0 | 9 |
| Syntax Skills | 5 | 0 | 3 | 8 |
| Core Skills | 0 | 0 | 3 | 3 |
| Implementation Skills | 0 | 0 | 8 | 8 |
| Error Handling Skills | 0 | 0 | 7 | 7 |
| Agents | 0 | 0 | 2 | 2 |
| **Totaal** | **14** | **0** | **23** | **37** |

**Voortgang**: ██████░░░░░░░░░░░░░░ ~38%

---

## Fase Overzicht

### ✅ Fase 1: Foundational Research & Initial Skills (COMPLEET)

| Stap | Beschrijving | Status | Output |
|------|--------------|:------:|--------|
| 1.1 | Research Client Scripts | ✅ | `research-client-scripts.md` |
| 1.2 | Research Server Scripts | ✅ | `research-server-scripts.md` |
| 1.3 | Skill: erpnext-syntax-clientscripts | ✅ | NL + EN `.skill` files |
| 1.4 | Skill: erpnext-syntax-serverscripts | ✅ | NL + EN `.skill` files |
| 1.5 | Validatie & Packaging Fase 1 | ✅ | `FASE_1_VALIDATIE_RAPPORT.md` |

---

### 🔄 Fase 2: Syntax Skills (5/8 COMPLEET)

#### Research (COMPLEET)
| Stap | Beschrijving | Status | Output |
|------|--------------|:------:|--------|
| 2.1 | Research Controllers | ✅ | `research-document-controllers.md` |
| 2.2 | Research Hooks | ✅ | `research-document-hooks.md` |
| 2.3 | Research Whitelisted | ✅ | `research-whitelisted-methods.md` |
| 2.4 | Research Jinja | ✅ | `research-jinja-templates.md` |
| 2.5 | Research Scheduler | ✅ | `research-scheduler-background-jobs.md` |
| 2.6.1 | Research Custom App Structure | ✅ | `research-custom-app-structure.md` |
| 2.6.2 | Research Custom App Data | ✅ | `research-customapp-datamanagement.md` |

#### Skills (5/8 COMPLEET)
| Stap | Skill | Status | Output |
|------|-------|:------:|--------|
| 2.7.1 | Controllers (Part 1) | ✅ | Reference files |
| 2.7.2 | Controllers (Part 2) | ✅ | NL + EN `.skill` files |
| 2.8.1 | Hooks (Part 1) | ✅ | Reference files |
| 2.8.2 | Hooks (Part 2) | ✅ | NL + EN `.skill` files |
| 2.9.1 | Whitelisted (Part 1) | ✅ | Reference files |
| 2.9.2 | Whitelisted (Part 2) | ✅ | NL + EN `.skill` files |
| 2.10 | Jinja Templates | ⏳ | **Volgende** |
| 2.11 | Scheduler/Background Jobs | ⏳ | Gepland |
| 2.12.1 | Custom App (Setup) | ⏳ | Gepland |
| 2.12.2 | Custom App (Data) | ⏳ | Gepland |

---

### ⏳ Fase 3: Core Skills (Gepland)

| Stap | Skill | Status | Dependencies |
|------|-------|:------:|--------------|
| 3.1 | erpnext-database | ⏳ | Fase 2 compleet |
| 3.2 | erpnext-permissions | ⏳ | Fase 2 compleet |
| 3.3 | erpnext-api-patterns | ⏳ | Fase 2 compleet |

---

### ⏳ Fase 4: Implementation Skills (Gepland)

Elke impl-skill vereist upload van corresponderende syntax skill.

| Stap | Skill | Status | Upload Vereist |
|------|-------|:------:|----------------|
| 4.1 | erpnext-impl-clientscripts | ⏳ | syntax-clientscripts |
| 4.2 | erpnext-impl-serverscripts | ⏳ | syntax-serverscripts |
| 4.3 | erpnext-impl-controllers | ⏳ | syntax-controllers |
| 4.4 | erpnext-impl-hooks | ⏳ | syntax-hooks |
| 4.5 | erpnext-impl-whitelisted | ⏳ | syntax-whitelisted |
| 4.6 | erpnext-impl-jinja | ⏳ | syntax-jinja |
| 4.7 | erpnext-impl-scheduler | ⏳ | syntax-scheduler |
| 4.8 | erpnext-impl-customapp | ⏳ | syntax-customapp |

---

### ⏳ Fase 5: Error Handling Skills (Gepland)

| Stap | Skill | Status | Upload Vereist |
|------|-------|:------:|----------------|
| 5.1 | erpnext-errors-clientscripts | ⏳ | syntax-clientscripts |
| 5.2 | erpnext-errors-serverscripts | ⏳ | syntax-serverscripts |
| 5.3 | erpnext-errors-controllers | ⏳ | syntax-controllers |
| 5.4 | erpnext-errors-hooks | ⏳ | syntax-hooks |
| 5.5 | erpnext-errors-whitelisted | ⏳ | syntax-whitelisted |
| 5.6 | erpnext-errors-jinja | ⏳ | syntax-jinja |
| 5.7 | erpnext-errors-scheduler | ⏳ | syntax-scheduler |

---

### ⏳ Fase 6: Intelligent Agents (Gepland)

| Stap | Agent | Functie | Uploads Vereist |
|------|-------|---------|-----------------|
| 6.1 | erpnext-interpreter | Vage input → technische specs | 8 syntax skills |
| 6.2 | erpnext-validator | Code verificatie tegen skills | 23 skills (syntax + impl + errors) |

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
| erpnext-syntax-controllers | ✅ | ✅ | lifecycle-methods, methods, flags, examples, anti-patterns |
| erpnext-syntax-hooks | ✅ | ✅ | doc-events, scheduler-events, bootinfo, overrides, permissions, fixtures |
| erpnext-syntax-whitelisted | ✅ | ✅ | decorator-options, parameter-handling, response-patterns, client-calls |

---

## Research Documenten Status

| Document | Regels | Status |
|----------|:------:|:------:|
| `research-client-scripts.md` | ~600 | ✅ |
| `research-server-scripts.md` | ~500 | ✅ |
| `research-document-controllers.md` | ~744 | ✅ |
| `research-document-hooks.md` | ~868 | ✅ |
| `research-whitelisted-methods.md` | ~834 | ✅ |
| `research-jinja-templates.md` | ~650 | ✅ |
| `research-scheduler-background-jobs.md` | ~550 | ✅ |
| `research-custom-app-structure.md` | ~550 | ✅ |
| `research-customapp-datamanagement.md` | ~600 | ✅ |

---

## Fase Opsplitsing Criteria

Fases worden opgesplitst wanneer:
- Meer dan 700 research regels
- Meer dan 5 reference files nodig
- Meer dan 8-10 secties in skill

---

## Belangrijke Ontdekkingen

Gedocumenteerd in `LESSONS_LEARNED.md`:

1. **Server Scripts Sandbox**: Alle imports geblokkeerd - gebruik `frappe.utils.*` namespace
2. **hooks.py Resolution**: "Last writer wins" principe
3. **Scheduler**: v15 tick interval 60s (was 4 min in v14)
4. **on_change hook**: Triggert na ELKE modificatie inclusief `db_set`
5. **Wijzigingen na on_update**: Worden NIET automatisch opgeslagen

---

## Volgende Stappen

1. **Fase 2.10**: Jinja Templates skill maken
2. **Fase 2.11**: Scheduler skill maken
3. **Fase 2.12**: Custom App skill maken
4. **Fase 3**: Core skills (database, permissions, api-patterns)

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

### 2026-01-17
- ROADMAP geüpdatet met correcte skill status
- Controllers skill bevestigd als compleet
- Voortgang aangepast naar 38%
- LESSONS_LEARNED.md toegevoegd

### 2026-01-14
- PROJECT_AUDIT uitgevoerd
- Whitelisted skill voltooid
- GitHub push workflow getest

### 2026-01-13
- Fase 2.7 (Controllers) + 2.8 (Hooks) + 2.9 (Whitelisted) compleet
- Alle research documenten voltooid
- Masterplan amendments geconsolideerd
