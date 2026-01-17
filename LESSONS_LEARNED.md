# LESSONS LEARNED - ERPNext Skills Package

> **Project**: ERPNext Anthropic Claude Development Skill Package  
> **Laatste update**: 17 januari 2026  
> **Doel**: Documentatie van alle geleerde lessen tijdens development

---

## 1. Technische Lessen: Frappe/ERPNext

### 1.1 Server Scripts Sandbox Environment

**De belangrijkste technische ontdekking van het project.**

Server Scripts draaien in een RestrictedPython sandbox waar **ALLE import statements geblokkeerd** zijn:

```python
# ❌ FOUT - Werkt NIET in Server Scripts
from frappe.utils import nowdate, getdate
import json

# ✅ CORRECT - Alles via frappe namespace
date = frappe.utils.nowdate()
data = frappe.parse_json(json_string)
```

**Pre-loaded in sandbox:**
- `frappe` - Volledig framework
- `frappe.utils.*` - Utilities (ZONDER import)
- `json` module (via `frappe.parse_json`, `frappe.as_json`)
- `dict`, `list`, `_dict` - Data structures

### 1.2 Client Scripts vs Server Scripts

| Aspect | Client Script | Server Script |
|--------|--------------|---------------|
| Runs in | Browser (JavaScript) | Server (Python sandbox) |
| Access | DOM, UI, frm object | Database, documents |
| Imports | Normal JS imports | ❌ GEEN imports toegestaan |
| Debugging | Browser console | Server logs |

### 1.3 Document Controllers vs Server Scripts

| Wanneer | Kies |
|---------|------|
| Custom app development | Document Controller |
| Quick customization zonder code deployment | Server Script |
| Complex multi-document logic | Document Controller |
| Simple field validation | Server Script |

### 1.4 Hooks.py Patterns

**Kritieke volgorde bij app loading:**
1. `app_include_js/css` - Geladen op elke pagina
2. `doc_events` - Per DocType event handlers
3. `scheduler_events` - Cron-achtige taken

**Anti-pattern**: Circular imports in hooks.py → Gebruik lazy loading.

---

## 2. Project Management Lessen

### 2.1 Research-First Aanpak

**Altijd** research document maken VOORDAT skill development begint:

```
┌─────────────────────────────────────────────────────────────────────┐
│ 1. Research Document (docs/research/research-[topic].md)           │
│    └─→ Officiële docs + GitHub source verificatie                  │
│                                                                     │
│ 2. Skill Development (skills/source/[cat]/[skill]/)                │
│    └─→ SKILL.md + references/ gebaseerd op research                │
│                                                                     │
│ 3. Packaging & Validatie                                           │
│    └─→ quick_validate.py + package_skill.py                        │
└─────────────────────────────────────────────────────────────────────┘
```

### 2.2 Fase Opsplitsing Criteria

Split een fase wanneer:
- Research document > 700 regels
- Meer dan 5 reference files nodig
- Meer dan 8-10 secties in één skill

### 2.3 Single Source of Truth

| Document | Functie |
|----------|---------|
| ROADMAP.md | Actuele project status |
| Masterplan | Oorspronkelijke visie |
| Amendments | Specifieke wijzigingen |
| LESSONS_LEARNED.md | Technische & proces lessen |

---

## 3. Claude/AI Workflow Lessen

### 3.1 Context Window Management

- Claude's filesystem reset tussen sessies
- **ALTIJD** pushen naar GitHub na elke fase
- Grote taken opsplitsen in meerdere conversaties

### 3.2 Effectieve Prompts

```
STAP 0: CONTEXT OPHALEN (verplicht)
├── Haal ROADMAP.md op
├── Haal relevant research document op
└── Bevestig output locaties

STAP 1-N: Uitvoering
└── Concrete, verifieerbare deliverables

LAATSTE STAP: Push naar GitHub
```

### 3.3 Verificatie Workflow

Na elke AI-gegenereerde output:
1. ✅ Structuur klopt?
2. ✅ Inhoud correct?
3. ✅ Gepusht naar GitHub?
4. ✅ ROADMAP bijgewerkt?

---

## 4. Skill Development Lessen

### 4.1 Anthropic Skill Structuur (Definitief)

```
skill-name/
├── SKILL.md           ← DIRECT in root (VERPLICHT)
└── references/        ← Detail documentatie
    ├── methods.md
    ├── examples.md
    └── anti-patterns.md
```

**NIET toegestaan in skill folders:**
- README.md
- CHANGELOG.md
- Taal subfolders (NL/, EN/)

### 4.2 SKILL.md Vereisten

| Aspect | Vereiste |
|--------|----------|
| Frontmatter | `name` + `description` (verplicht) |
| Name format | kebab-case, max 64 chars |
| Description | Bevat triggers, max 1024 chars |
| Body | < 500 regels |
| Taal | Engels |

### 4.3 Progressive Disclosure

```
Level 1: Metadata (altijd geladen)     ~100 woorden
Level 2: SKILL.md body (bij trigger)   <500 regels
Level 3: References (on-demand)        Onbeperkt
```

---

## 5. GitHub Integratie Lessen

### 5.1 API Configuratie

**Vereiste project settings:**
- Network: "Package managers only"
- Additional domains: `api.github.com`, `github.com`
- **Nieuwe conversatie nodig** na domain toevoegen

### 5.2 Standaard Workflow

```bash
# 1. Token instellen
export GITHUB_TOKEN="..."

# 2. Bestand uploaden
CONTENT=$(base64 -w 0 bestand.md)
curl -X PUT -H "Authorization: Bearer $GITHUB_TOKEN" \
  "https://api.github.com/.../contents/path/bestand.md" \
  -d '{"message":"...","content":"'$CONTENT'"}'

# 3. Bestand updaten (SHA nodig)
SHA=$(curl ... | grep sha | cut -d'"' -f4)
curl -X PUT ... -d '{"message":"...","content":"...","sha":"'$SHA'"}'
```

### 5.3 Commit Message Conventie

```
Fase [nummer]: [actie] [onderwerp]

Voorbeelden:
- Fase 2.5: Add erpnext-syntax-hooks skill
- Cleanup: Remove old NL/EN structure
- Fix: Correct SKILL.md frontmatter
```

---

## 6. Kritieke Ontdekkingen

### 6.1 Anthropic Tooling Compatibiliteit

**Ontdekt tijdens mid-project review:**

Onze oorspronkelijke structuur met NL/EN subfolders was **NIET compatibel** met Anthropic's `package_skill.py`:

```python
# package_skill.py verwacht:
skill_md = skill_path / "SKILL.md"  # DIRECT in root!
```

**Impact**: Volledige herstructurering nodig.

### 6.2 Engels-Only Beslissing

**Analyse van Anthropic's eigen skills:**
- Geen enkele Anthropic skill is meertalig
- Skill instructies zijn voor Claude, niet voor gebruikers
- Claude kan Engelse instructies lezen en in elke taal antwoorden

**Besluit**: Nederlandse skills geschrapt → 56 skills → 28 skills (50% reductie)

### 6.3 Validatie Regels

Uit `quick_validate.py`:

| Veld | Vereiste | Max |
|------|----------|:---:|
| `name` | kebab-case (a-z, 0-9, -) | 64 |
| `description` | String, geen < > | 1024 |
| `compatibility` | Optional | 500 |
| SKILL.md | In folder ROOT | - |

---

## 7. Anti-Patterns

### 7.1 Project Structuur

| ❌ Fout | ✅ Correct |
|---------|-----------|
| NL/EN subfolders | Aparte skills per taal |
| SKILL.md in subfolder | SKILL.md in root |
| README.md in skill | Geen README in skill |
| Inconsistente naamgeving | Strict kebab-case |

### 7.2 Development Workflow

| ❌ Fout | ✅ Correct |
|---------|-----------|
| Direct beginnen met code | Research-first |
| Pas achteraf pushen | Push na elke fase |
| Geen validatie | quick_validate.py gebruiken |
| Handmatig packagen | package_skill.py gebruiken |

### 7.3 Frappe/ERPNext

| ❌ Fout | ✅ Correct |
|---------|-----------|
| `from frappe.utils import x` | `frappe.utils.x()` |
| `import json` in Server Script | `frappe.parse_json()` |
| Direct SQL zonder escaping | `frappe.db.sql` met parameters |

---

## 8. Best Practices Samenvatting

### 8.1 Project Setup

1. ✅ Lees platform documentatie volledig (skill-creator/SKILL.md)
2. ✅ Test tooling VOORDAT je structuur kiest
3. ✅ Definieer directory structuur expliciet in masterplan
4. ✅ Plan checkpoints na elke hoofdfase

### 8.2 Skill Development

1. ✅ Research document eerst
2. ✅ SKILL.md < 500 regels, details in references/
3. ✅ Valideer met `quick_validate.py`
4. ✅ Package met `package_skill.py`
5. ✅ Push source + package naar GitHub

### 8.3 Quality Control

1. ✅ Elke fase eindigt met push
2. ✅ ROADMAP.md is altijd actueel
3. ✅ Lessons learned continu documenteren
4. ✅ Verificatie na migraties/herstructurering

---

## 9. Top 10 Lessen

| # | Les |
|---|-----|
| 1 | **Test platform tooling VOORDAT je structuur kiest** |
| 2 | **Server Scripts: GEEN imports, alles via frappe namespace** |
| 3 | **Research-first: documenteer voordat je bouwt** |
| 4 | **Push na ELKE fase - Claude's filesystem reset** |
| 5 | **SKILL.md moet DIRECT in skill folder root staan** |
| 6 | **Engels-only is Anthropic best practice** |
| 7 | **Eén source of truth voor status (ROADMAP.md)** |
| 8 | **Split grote fases proactief (>700 regels research)** |
| 9 | **Valideer altijd met officiële tooling** |
| 10 | **Documenteer lessons learned continu** |

---

## Changelog

| Datum | Wijziging |
|-------|-----------|
| 2026-01-17 | Volledige herschrijving na mid-project review |
| 2026-01-17 | Engels-only beslissing gedocumenteerd |
| 2026-01-17 | Anthropic tooling compatibiliteit toegevoegd |
| 2026-01-17 | Cleanup van duplicaat secties |

---

*Dit document wordt continu bijgewerkt met nieuwe inzichten.*
