# ERPNext Skills Package - Masterplan v3

> **Geconsolideerde versie** - Integreert alle amendments en V16 compatibility  
> **Datum**: 18 januari 2026  
> **Status**: Actief werkdocument

---

## Visie & Doelstelling

Een complete, modulaire verzameling van **28 deterministische skills** die Claude instanties in staat stellen om foutloze ERPNext/Frappe code te genereren voor **versies 14, 15 en 16**.

### Kernprincipes

| Principe | Beschrijving |
|----------|--------------|
| **Engels-only** | Skills zijn instructies voor Claude, niet voor eindgebruikers. Claude leest EN, antwoordt in elke taal. |
| **Research-first** | Geen skill zonder gedegen onderzoek tegen officiële bronnen |
| **Determinisme** | Alleen geverifieerde feiten, geen aannames of vage suggesties |
| **Versie-expliciet** | Alle code is gemarkeerd met versie-compatibiliteit (v14/v15/v16) |
| **One-shot kwaliteit** | Direct definitieve kwaliteit, geen iteraties of PoC's |

---

## Versie Compatibility Matrix

### Ondersteunde Versies

| Versie | Framework | Release | Support Status |
|--------|-----------|---------|----------------|
| **v14** | Frappe 14 | 2022 | LTS (tot dec 2025) |
| **v15** | Frappe 15 | 2023 | Current |
| **v16** | Frappe 16 | Jan 2026 | Latest |

### V16 Breaking Changes & Nieuwe Features

Deze wijzigingen MOETEN in alle relevante skills worden gedocumenteerd:

#### 1. Nieuwe Hook: `extend_doctype_class` (V16+)

```python
# hooks.py - V16+ ONLY
extend_doctype_class = {
    "Sales Invoice": ["app.extensions.SalesInvoiceMixin"]
}
```

**Impact**: Veiligere manier om DocType classes uit te breiden zonder overschrijven.
- Meerdere apps kunnen dezelfde DocType extenden
- Werkt bovenop `override_doctype_class`
- **Relevante skills**: frappe-syntax-hooks, frappe-impl-hooks

#### 2. Data Masking (V16+)

Field-level data masking voor privacy compliance:
```python
# In DocType field configuration
"data_masking": True
```
**Relevante skills**: frappe-core-permissions

#### 3. UUID Naming Rule (V16+)

Nieuwe naming optie voor globally unique identifiers:
```python
# In DocType
naming_rule = "UUID"
```
**Relevante skills**: frappe-syntax-controllers

#### 4. Performance Verbeteringen

- ~2x snellere pagina loads (Frappe Caffeine architecture)
- Geoptimaliseerde accounting reports
- **Geen code changes nodig** - automatisch

#### 5. UI Refresh

- Nieuwe icons, sidebars, workspaces
- Full-width desk by default
- **Geen code changes nodig** - automatisch

#### 6. Chrome-based PDF Generation (V16+)

Print Formats kunnen nu Chrome-based PDF generatie gebruiken i.p.v. wkhtmltopdf:
```python
# In Print Format
pdf_renderer = "chrome"  # of "wkhtmltopdf"
```
**Relevante skills**: frappe-syntax-jinja, frappe-impl-jinja

#### 7. Scheduler Tick Interval Change

| Versie | Tick Interval |
|--------|---------------|
| v14 | 4 minuten |
| v15+ | 60 seconden |

**Relevante skills**: frappe-syntax-scheduler

---

## Definitieve Directory Structuur

```
ERPNext_Anthropic_Claude_Development_Skill_Package/
│
├── README.md                    # Project overview
├── ROADMAP.md                   # Single source of truth voor status
├── LESSONS.md           # Technische lessen
├── WAY_OF_WORK.md              # Methodologie
│
├── docs/
│   ├── masterplan/
│   │   ├── erpnext-skills-masterplan-v3.md  ← DIT DOCUMENT
│   │   └── amendments/archived/              # Oude amendments
│   └── research/
│       └── research-*.md        # 13 research documenten
│
└── skills/
    ├── source/                  # Bronbestanden (Anthropic-conform)
    │   ├── syntax/              # 8 skills
    │   ├── core/                # 3 skills
    │   ├── impl/                # 8 skills
    │   ├── errors/              # 7 skills
    │   └── agents/              # 2 agents
    │
    └── packaged/                # .skill files voor distributie
```

### Skill Folder Structuur

```
erpnext-{type}-{name}/
├── SKILL.md                     # Hoofdbestand (<500 regels)
└── references/
    ├── methods.md               # Method signatures
    ├── examples.md              # Werkende voorbeelden
    └── anti-patterns.md         # Wat te vermijden
```

---

## Complete Skill Index (28 Skills)

### Syntax Skills (8)

| ID | Skill | Focus | V16 Updates |
|----|-------|-------|-------------|
| SYN-CS | `frappe-syntax-clientscripts` | JavaScript, frm.*, frappe.* | Geen |
| SYN-SS | `frappe-syntax-serverscripts` | Python in sandbox | Geen |
| SYN-CT | `frappe-syntax-controllers` | Document controller classes | UUID naming |
| SYN-HK | `frappe-syntax-hooks` | hooks.py structuur | `extend_doctype_class` |
| SYN-WL | `frappe-syntax-whitelisted` | @frappe.whitelist() | Geen |
| SYN-JJ | `frappe-syntax-jinja` | Jinja2 templates | Chrome PDF |
| SYN-SC | `frappe-syntax-scheduler` | Cron, scheduler_events | Tick interval |
| SYN-CA | `frappe-syntax-customapp` | App structuur | CI workflow |

### Core Skills (3)

| ID | Skill | Focus | V16 Updates |
|----|-------|-------|-------------|
| CORE-DB | `frappe-core-database` | frappe.db.*, queries | Query performance |
| CORE-PM | `frappe-core-permissions` | Roles, access control | Data masking |
| CORE-API | `frappe-core-api` | REST/RPC conventies | Geen |

### Implementation Skills (8)

| ID | Skill | Focus |
|----|-------|-------|
| IMP-CS | `frappe-impl-clientscripts` | Form events, async calls |
| IMP-SS | `frappe-impl-serverscripts` | Doc events, API, scheduled |
| IMP-CT | `frappe-impl-controllers` | Lifecycle, method chaining |
| IMP-HK | `frappe-impl-hooks` | Event wiring, overrides, `extend_doctype_class` |
| IMP-WL | `frappe-impl-whitelisted` | Security, responses |
| IMP-JJ | `frappe-impl-jinja` | Print, email, web |
| IMP-SC | `frappe-impl-scheduler` | Jobs, queues, timeouts |
| IMP-CA | `frappe-impl-customapp` | Fixtures, migrations |

### Error Handling Skills (7)

| ID | Skill | Focus |
|----|-------|-------|
| ERR-CS | `frappe-errors-clientscripts` | try/catch, user feedback |
| ERR-SS | `frappe-errors-serverscripts` | throw, log, rollback |
| ERR-CT | `frappe-errors-controllers` | Validation, transactions |
| ERR-HK | `frappe-errors-hooks` | Hook isolation |
| ERR-DB | `frappe-errors-database` | Query errors, deadlocks |
| ERR-PM | `frappe-errors-permissions` | Permission denied handling |
| ERR-API | `frappe-errors-api` | HTTP codes, responses |

### Agents (2)

| ID | Agent | Functie |
|----|-------|---------|
| AGT-INT | `frappe-agent-interpreter` | Vage input → technische specs |
| AGT-VAL | `frappe-agent-validator` | Code verificatie tegen skills |

---

## Kritieke Technische Waarschuwingen

### ⚠️ Server Script Sandbox (ALLE VERSIES)

```python
# ❌ FOUT - Werkt NOOIT in Server Scripts
from frappe.utils import nowdate
import json

# ✅ CORRECT - Via frappe namespace
date = frappe.utils.nowdate()
data = frappe.parse_json(json_string)
```

**Dit is de #1 oorzaak van AI-gegenereerde ERPNext code failures.**

### ⚠️ UI Event vs Hook Name Mapping

| UI Event | Interne Hook |
|----------|--------------|
| Before Save | `validate` |
| After Save | `on_update` |
| Before Submit | `before_submit` |
| After Submit | `on_submit` |

### ⚠️ Controller Changes na on_update

```python
# ❌ FOUT - Wijzigingen niet opgeslagen
def on_update(self):
    self.status = "Updated"  # Niet automatisch opgeslagen!

# ✅ CORRECT - Expliciet opslaan
def on_update(self):
    frappe.db.set_value(self.doctype, self.name, "status", "Updated")
```

### ⚠️ has_permission Hook Beperking

```python
# has_permission kan alleen WEIGEREN, niet TOEKENNEN
def has_permission(doc, user, permission_type):
    if some_condition:
        return False  # Weiger toegang
    return None  # Fallback naar standaard (niet True!)
```

---

## Fase Planning

### Huidige Status (18 jan 2026)

| Fase | Beschrijving | Status | Voltooid |
|------|--------------|--------|----------|
| 1 | Research | ✅ COMPLEET | 13/13 docs |
| 2 | Syntax Skills | ✅ COMPLEET | 8/8 skills |
| 3 | Core Skills | ✅ COMPLEET | 3/3 skills |
| 4 | Implementation Skills | 🔄 IN PROGRESS | 2/8 skills |
| 5 | Error Handling | ⏳ GEPLAND | 0/7 skills |
| 6 | Agents | ⏳ GEPLAND | 0/2 agents |
| 7 | Finalisatie | ⏳ GEPLAND | - |

**Totale voortgang**: ~46% (13/28 skills voltooid)

### Fase 4: Implementation Skills (Huidig)

| Stap | Skill | Status | Research Doc |
|------|-------|--------|--------------|
| 4.1 | frappe-impl-clientscripts | ✅ | research-client-scripts.md |
| 4.2 | frappe-impl-serverscripts | ✅ | research-server-scripts.md |
| 4.3 | frappe-impl-controllers | ⏳ NEXT | research-document-controllers.md |
| 4.4 | frappe-impl-hooks | ⏳ | research-document-hooks.md |
| 4.5 | frappe-impl-whitelisted | ⏳ | research-whitelisted-methods.md |
| 4.6 | frappe-impl-jinja | ⏳ | research-jinja-templates.md |
| 4.7 | frappe-impl-scheduler | ⏳ | research-scheduler-background-jobs.md |
| 4.8 | frappe-impl-customapp | ⏳ | research-custom-app-structure.md |

### Fase 5: Error Handling Skills

| Stap | Skill | Basis |
|------|-------|-------|
| 5.1 | frappe-errors-clientscripts | syntax-clientscripts + impl-clientscripts |
| 5.2 | frappe-errors-serverscripts | syntax-serverscripts + impl-serverscripts |
| 5.3 | frappe-errors-controllers | syntax-controllers + impl-controllers |
| 5.4 | frappe-errors-hooks | syntax-hooks + impl-hooks |
| 5.5 | frappe-errors-database | core-database |
| 5.6 | frappe-errors-permissions | core-permissions |
| 5.7 | frappe-errors-api | core-api-patterns |

### Fase 6: Agents

| Stap | Agent | Doel |
|------|-------|------|
| 6.1 | frappe-agent-interpreter | Vage requirements → technische specs |
| 6.2 | frappe-agent-validator | Code validatie tegen alle skills |

### Fase 7: Finalisatie

1. V16 Compatibility Review van alle voltooide skills
2. Dependencies matrix
3. Final packaging (28 .skill files)
4. INDEX.md en INSTALL.md
5. Archive oude amendments

---

## V16 Compatibility Review Checklist

Bij voltooiing van Fase 4-6, review alle skills voor:

- [ ] `extend_doctype_class` hook gedocumenteerd (syntax-hooks, impl-hooks)
- [ ] Data masking optie gedocumenteerd (permissions)
- [ ] UUID naming gedocumenteerd (syntax-controllers)
- [ ] Chrome PDF optie gedocumenteerd (syntax-jinja, impl-jinja)
- [ ] Scheduler tick interval correct (syntax-scheduler)
- [ ] Versie markers (v14/v15/v16) bij alle code voorbeelden
- [ ] Deprecated patterns verwijderd

---

## Research Bronnen Prioriteit

1. **Officiële Frappe Docs** (docs.frappe.io) - v16 sectie
2. **Frappe GitHub** (github.com/frappe/frappe) - main branch
3. **ERPNext Docs** (docs.erpnext.com)
4. **Community** (discuss.frappe.io) - alleen 2024+ posts

### V16-Specifieke Bronnen

- Frappe v16 Release Notes: https://frappe.io/blog
- Frappe v16 Hooks Docs: https://docs.frappe.io/framework/user/en/python-api/hooks
- ERPNext v16 Changelog: https://github.com/frappe/erpnext/releases

---

## Skill Creatie Template (V3)

```
┌─────────────────────────────────────────────────────────────────────┐
│ FASE [X.Y] - SKILL: [naam]                                         │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│ STAP 0: CONTEXT                                                    │
│ ════════════════                                                   │
│ 1. Haal ROADMAP.md op → Bevestig vorige fase compleet              │
│ 2. Haal relevant research document op                              │
│ 3. Output locatie: skills/source/[categorie]/[skill-name]/         │
│                                                                     │
│ STAP 1: MAAK SKILL                                                 │
│ ═══════════════════                                                │
│ [skill-name]/                                                       │
│ ├── SKILL.md              ← Engels, <500 regels                    │
│ └── references/                                                     │
│     └── [relevant].md                                               │
│                                                                     │
│ STAP 2: V16 CHECK                                                  │
│ ═════════════════                                                  │
│ □ Versie markers (v14/v15/v16) aanwezig?                          │
│ □ V16-specifieke features gedocumenteerd?                         │
│ □ Deprecated patterns verwijderd?                                  │
│                                                                     │
│ STAP 3: PUSH                                                       │
│ ════════════════                                                   │
│ • skills/source/[categorie]/[skill-name]/                          │
│ • ROADMAP.md (verplicht!)                                          │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
```

---

## Geïntegreerde Amendments

Dit masterplan v3 consolideert:

| Amendment | Inhoud | Status |
|-----------|--------|--------|
| Amendment 5 | Mid-project review, structuur herziening | ✅ Geïntegreerd |
| Amendment 6 | Engels-only beslissing, definitieve structuur | ✅ Geïntegreerd |
| Fase opsplitsingen | Research/skill splits per fase | ✅ Geïntegreerd |
| Skill uploads | Voortgangsrapportages | ✅ Geïntegreerd |
| **V16 Compatibility** | Nieuwe features en breaking changes | ✅ **NIEUW** |

---

## Kwaliteitsgaranties

### Per Skill

- [ ] SKILL.md < 500 regels
- [ ] Frontmatter met duidelijke triggers
- [ ] Decision tree of quick reference
- [ ] Minimaal 3 werkende voorbeelden per versie
- [ ] Anti-patterns gedocumenteerd
- [ ] Versie markers (v14/v15/v16) aanwezig

### Per Fase

- [ ] Alle skills gepusht naar GitHub
- [ ] ROADMAP.md bijgewerkt
- [ ] V16 compatibility verified

### Totaal Project

- [ ] 28 skills compleet en gepackaged
- [ ] V16 compatibility review afgerond
- [ ] Dependencies matrix compleet
- [ ] Alle code voorbeelden getest

---

*Laatste update: 18 januari 2026*
*Vervangt: masterplan-v2 + alle amendments*
