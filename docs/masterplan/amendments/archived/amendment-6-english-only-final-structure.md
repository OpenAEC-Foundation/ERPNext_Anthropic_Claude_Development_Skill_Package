# Masterplan Amendment 6: Engels-Only & Definitieve Structuur

> **Datum**: 17 januari 2026  
> **Project**: ERPNext Skills Package  
> **Type**: Strategische herziening + definitieve structuur

---

## 1. Strategische Beslissing: Engels-Only

### 1.1 Rationale

Na analyse van Anthropic's eigen skill library:
- **Geen** van Anthropic's skills is meertalig
- Skill instructies zijn voor Claude, niet voor eindgebruikers
- Claude kan Engelse instructies lezen en in elke taal antwoorden
- Meertalige skills voegen geen functionele waarde toe

### 1.2 Impact

| Metric | Oud (NL+EN) | Nieuw (EN-only) | Besparing |
|--------|:-----------:|:---------------:|:---------:|
| Totaal skills | 56 | **28** | 50% |
| Voltooide skills om te behouden | 25 EN versies | **13** | - |
| Nog te maken | 31 | **15** | 52% |

### 1.3 Besluit

**Nederlandse versies worden niet gemigreerd.** Alleen Engelse versies gaan naar de nieuwe structuur.

---

## 2. Definitieve Directory Structuur

```
ERPNext_Anthropic_Claude_Development_Skill_Package/
│
├── README.md                    # Project overview
├── ROADMAP.md                   # Single source of truth
├── LESSONS.md           # Geleerde lessen
├── WAY_OF_WORK.md              # Methodologie
│
├── docs/
│   ├── masterplan/
│   │   ├── erpnext-skills-masterplan-v2.md
│   │   └── amendments/
│   │       └── amendment-*.md
│   └── research/
│       └── research-*.md
│
└── skills/
    │
    ├── source/                  # Bronbestanden (Anthropic-conform)
    │   │
    │   ├── syntax/              # 8 skills
    │   │   ├── frappe-syntax-clientscripts/
    │   │   │   ├── SKILL.md
    │   │   │   └── references/
    │   │   ├── frappe-syntax-serverscripts/
    │   │   ├── frappe-syntax-controllers/
    │   │   ├── frappe-syntax-hooks/
    │   │   ├── frappe-syntax-whitelisted/
    │   │   ├── frappe-syntax-jinja/
    │   │   ├── frappe-syntax-scheduler/
    │   │   └── frappe-syntax-customapp/
    │   │
    │   ├── core/                # 3 skills
    │   │   ├── frappe-core-database/
    │   │   ├── frappe-core-permissions/
    │   │   └── frappe-core-api/
    │   │
    │   ├── impl/                # 8 skills
    │   │   ├── frappe-impl-clientscripts/
    │   │   ├── frappe-impl-serverscripts/
    │   │   ├── frappe-impl-controllers/
    │   │   ├── frappe-impl-hooks/
    │   │   ├── frappe-impl-whitelisted/
    │   │   ├── frappe-impl-jinja/
    │   │   ├── frappe-impl-scheduler/
    │   │   └── frappe-impl-customapp/
    │   │
    │   ├── errors/              # 7 skills
    │   │   ├── frappe-errors-clientscripts/
    │   │   ├── frappe-errors-serverscripts/
    │   │   ├── frappe-errors-controllers/
    │   │   ├── frappe-errors-hooks/
    │   │   ├── frappe-errors-database/
    │   │   ├── frappe-errors-permissions/
    │   │   └── frappe-errors-api/
    │   │
    │   └── agents/              # 2 agents
    │       ├── frappe-agent-interpreter/
    │       └── frappe-agent-validator/
    │
    └── packaged/                # .skill files voor distributie
        ├── frappe-syntax-clientscripts.skill
        ├── frappe-syntax-serverscripts.skill
        └── ... (28 .skill files totaal)
```

---

## 3. Skill Naming Conventions

| Aspect | Conventie | Voorbeeld |
|--------|-----------|-----------|
| Folder naam | `erpnext-{type}-{name}` | `frappe-syntax-clientscripts` |
| SKILL.md locatie | Direct in folder root | `frappe-syntax-clientscripts/SKILL.md` |
| Package naam | Folder naam + `.skill` | `frappe-syntax-clientscripts.skill` |
| References | In `references/` subfolder | `references/methods.md` |

**Geen taal suffix meer** - alles is Engels.

---

## 4. Migratie Plan

### 4.1 Te Migreren Skills (13 voltooide EN versies)

**Syntax Skills (8):**
| Skill | Huidige Locatie | Nieuwe Locatie |
|-------|-----------------|----------------|
| clientscripts | `skills/source/frappe-syntax-clientscripts/EN/` | `skills/source/syntax/frappe-syntax-clientscripts/` |
| serverscripts | `skills/source/frappe-syntax-serverscripts/EN/` | `skills/source/syntax/frappe-syntax-serverscripts/` |
| controllers | `skills/source/frappe-syntax-controllers/EN/` | `skills/source/syntax/frappe-syntax-controllers/` |
| hooks | `skills/source/frappe-syntax-hooks/EN/` | `skills/source/syntax/frappe-syntax-hooks/` |
| whitelisted | `skills/source/frappe-syntax-whitelisted/EN/` | `skills/source/syntax/frappe-syntax-whitelisted/` |
| jinja | `skills/source/.../EN/` | `skills/source/syntax/frappe-syntax-jinja/` |
| scheduler | `skills/source/.../EN/` | `skills/source/syntax/frappe-syntax-scheduler/` |
| customapp | `skills/source/.../EN/` | `skills/source/syntax/frappe-syntax-customapp/` |

**Core Skills (3):**
| Skill | Huidige Locatie | Nieuwe Locatie |
|-------|-----------------|----------------|
| database | `skills/EN/CORE/frappe-core-database/` | `skills/source/core/frappe-core-database/` |
| permissions | `skills/.../EN/` | `skills/source/core/frappe-core-permissions/` |
| api-patterns | `skills/EN/CORE/frappe-core-api/` | `skills/source/core/frappe-core-api/` |

**Impl Skills (1):**
| Skill | Huidige Locatie | Nieuwe Locatie |
|-------|-----------------|----------------|
| impl-clientscripts | `skills/source/frappe-impl-clientscripts/EN/` | `skills/source/impl/frappe-impl-clientscripts/` |

**Research (13) - blijft op huidige locatie:**
`docs/research/research-*.md` - geen wijziging nodig

### 4.2 Migratie Stappen

```
┌─────────────────────────────────────────────────────────────────────┐
│ STAP 1: Nieuwe directory structuur aanmaken                        │
├─────────────────────────────────────────────────────────────────────┤
│ skills/source/syntax/                                              │
│ skills/source/core/                                                │
│ skills/source/impl/                                                │
│ skills/source/errors/                                              │
│ skills/source/agents/                                              │
│ skills/packaged/                                                   │
└─────────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────────┐
│ STAP 2: Migreer EN versies naar nieuwe locaties                    │
├─────────────────────────────────────────────────────────────────────┤
│ Voor elke skill:                                                    │
│ 1. Kopieer EN/SKILL.md → nieuwe-locatie/SKILL.md                   │
│ 2. Kopieer EN/references/ → nieuwe-locatie/references/             │
│ 3. Verwijder taal-specifieke referenties in content                │
└─────────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────────┐
│ STAP 3: Valideer elke skill                                        │
├─────────────────────────────────────────────────────────────────────┤
│ python quick_validate.py skills/source/[cat]/[skill-name]          │
│ → Moet "Skill is valid!" returnen                                  │
└─────────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────────┐
│ STAP 4: Package elke skill                                         │
├─────────────────────────────────────────────────────────────────────┤
│ python package_skill.py skills/source/[cat]/[skill] skills/packaged/│
└─────────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────────┐
│ STAP 5: Cleanup oude structuur                                     │
├─────────────────────────────────────────────────────────────────────┤
│ Verwijder:                                                          │
│ • Alle NL/ folders                                                  │
│ • Oude EN/ folders (na verificatie)                                │
│ • skills/README.md (niet toegestaan)                               │
│ • Lege/obsolete folders                                            │
└─────────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────────┐
│ STAP 6: Update tracking documenten                                 │
├─────────────────────────────────────────────────────────────────────┤
│ • ROADMAP.md - nieuwe structuur, aangepaste counts                 │
│ • skills/README.md verwijderd (index niet nodig)                   │
└─────────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────────┐
│ STAP 7: Push alles naar GitHub                                     │
└─────────────────────────────────────────────────────────────────────┘
```

---

## 5. Herzien Project Overzicht

### 5.1 Nieuwe Skill Telling

| Categorie | Skills | Status |
|-----------|:------:|--------|
| Syntax | 8 | ✅ 8 compleet (te migreren) |
| Core | 3 | ✅ 3 compleet (te migreren) |
| Implementation | 8 | 🔄 1 compleet, 7 te maken |
| Error Handling | 7 | ⏳ 0 compleet, 7 te maken |
| Agents | 2 | ⏳ 0 compleet, 2 te maken |
| **TOTAAL** | **28** | **12 compleet, 16 te maken** |

### 5.2 Nieuwe Voortgang

```
OUDE TELLING (NL+EN):
Voltooid: 25 van 41 deliverables = ~61%

NIEUWE TELLING (EN-only):
Voltooid: 12 van 28 skills = ~43%
          + 13 research docs (100%)

Na migratie starten we effectief op ~43% met een schone structuur.
```

---

## 6. Geüpdatete Fase Planning

### Fase 4: Implementation Skills (7 remaining)

| Stap | Skill | Vereist |
|------|-------|---------|
| 4.2 | frappe-impl-serverscripts | research-server-scripts.md |
| 4.3 | frappe-impl-controllers | research-document-controllers.md |
| 4.4 | frappe-impl-hooks | research-document-hooks.md |
| 4.5 | frappe-impl-whitelisted | research-whitelisted-methods.md |
| 4.6 | frappe-impl-jinja | research-jinja-templates.md |
| 4.7 | frappe-impl-scheduler | research-scheduler-background-jobs.md |
| 4.8 | frappe-impl-customapp | research-custom-app-structure.md |

### Fase 5: Error Handling Skills (7 new)

| Stap | Skill |
|------|-------|
| 5.1 | frappe-errors-clientscripts |
| 5.2 | frappe-errors-serverscripts |
| 5.3 | frappe-errors-controllers |
| 5.4 | frappe-errors-hooks |
| 5.5 | frappe-errors-database |
| 5.6 | frappe-errors-permissions |
| 5.7 | frappe-errors-api |

### Fase 6: Agents (2 new)

| Stap | Agent |
|------|-------|
| 6.1 | frappe-agent-interpreter |
| 6.2 | frappe-agent-validator |

### Fase 7: Finalisatie

- Dependencies check
- Final packaging
- Documentation
- Release

---

## 7. Geüpdatete Fase Prompt Template

```
┌─────────────────────────────────────────────────────────────────────┐
│ FASE [X.Y] PROMPT TEMPLATE (v3 - Engels-Only)                      │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│ STAP 0: CONTEXT OPHALEN                                            │
│ ════════════════════════                                           │
│ 1. Haal ROADMAP.md op → Bevestig vorige fase compleet              │
│ 2. Haal relevant research document op                              │
│ 3. Output locatie: skills/source/[categorie]/[skill-name]/         │
│                                                                     │
│ STAP 1: SKILL FOLDER MAKEN                                         │
│ ══════════════════════════                                         │
│ [skill-name]/                                                       │
│ ├── SKILL.md              ← Engels, <500 regels                    │
│ └── references/                                                     │
│     └── [relevant].md                                               │
│                                                                     │
│ STAP 2: VALIDEER                                                   │
│ ════════════════                                                   │
│ python quick_validate.py [skill-folder]                            │
│ → Moet "Skill is valid!" returnen                                  │
│                                                                     │
│ STAP 3: PACKAGE                                                    │
│ ═══════════════                                                    │
│ python package_skill.py [skill-folder] skills/packaged/            │
│                                                                     │
│ STAP 4: PUSH                                                       │
│ ════════════                                                       │
│ • skills/source/[categorie]/[skill-name]/                          │
│ • skills/packaged/[skill-name].skill                               │
│ • ROADMAP.md                                                        │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
```

---

## 8. Samenvatting Wijzigingen

| Aspect | Oud | Nieuw |
|--------|-----|-------|
| Talen | NL + EN | **EN only** |
| Skill folders | 56 | **28** |
| Taal suffix in naam | `-nl`, `-en` | **Geen** |
| NL/EN subfolders | Ja | **Nee** |
| SKILL.md locatie | In taal subfolder | **Direct in root** |

---

*Dit amendment vervangt Amendment 5 v2 en is de definitieve structuur voor het project.*
