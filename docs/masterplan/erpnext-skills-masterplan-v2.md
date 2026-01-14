# ERPNext Skills Package - Masterplan v2

## Visie & Doelstelling

Een complete, modulaire verzameling van deterministische skills die Claude instanties in staat stellen om foutloze ERPNext/Frappe code te genereren. Elke skill is lean, gefocust op één verantwoordelijkheid, en elimineert aannames door expliciete verificatie af te dwingen.

**Tweetalig**: Alle skills worden geleverd in Nederlands (NL) én Engels (EN).

**Uitvoering**: One-shot. Het volledige masterplan wordt in één doorlopende sessie uitgevoerd zonder iteraties of proof-of-concepts.

---

## Referentie Documenten

| Document | Locatie | Beschrijving |
|----------|---------|--------------|
| **Vooronderzoek** | `erpnext-vooronderzoek.md` | Initieel research document met alle ERPNext/Frappe scripting mechanismen, syntax voorbeelden, en best practices. Dit document vormt de basis voor alle skills. |
| **Masterplan** | `erpnext-skills-masterplan-v2.md` | Dit document - het uitvoeringsplan voor alle skills en agents. |

### Vooronderzoek Inhoud (erpnext-vooronderzoek.md)

Het vooronderzoek bevat gedocumenteerde kennis over:

1. **Client Scripts** - Form events, frm.* methods, child table handling
2. **Server Scripts** - Document events, API endpoints, scheduler, permission queries
3. **Document Controllers** - Lifecycle methods, execution order, flags
4. **hooks.py** - doc_events, scheduler_events, overrides, permissions
5. **Whitelisted Methods** - @frappe.whitelist() patterns
6. **Jinja Templates** - Print formats, beschikbare methods
7. **Background Jobs** - frappe.enqueue, queue types
8. **Best Practices** - Error handling, database, performance
9. **Decision Matrix** - Wanneer wat te gebruiken

**BELANGRIJK**: Bij het maken van elke skill MOET eerst `erpnext-vooronderzoek.md` worden geraadpleegd als startpunt. Aanvullend research bouwt voort op dit document.

---

## Kernprincipes

### 0. Vooronderzoek als Startpunt

Het initiële onderzoek is reeds uitgevoerd en gedocumenteerd:

```
📄 erpnext-vooronderzoek.md
```

Dit document bevat de basis research over alle 7 scripting mechanismen in ERPNext/Frappe:
- Client Scripts (JavaScript)
- Server Scripts (Python)
- Document Controllers
- hooks.py configuratie
- Jinja templates
- Scheduled jobs / Background jobs
- Whitelisted API methods

**Alle skills bouwen voort op dit vooronderzoek.** De fase-specifieke research prompts dienen om details te verifiëren, aan te vullen, en te actualiseren tegen de laatste Frappe v14/v15 documentatie.

### 1. Anthropic Conventies als Fundament

Alle skills en agents volgen **strikt** de officiële Anthropic documentatie en SDK's:

| Component | Bron | Toepassing |
|-----------|------|------------|
| Skill structuur | `skill-creator` SKILL.md | Frontmatter, progressive disclosure, references/ |
| Skill packaging | `package_skill.py` | Validatie en distributie |
| Agent patterns | Claude Agent SDK | Interpreter en Validator agents |

**Geen afwijkingen van officiële conventies.**

### 2. Research: Alles Tot In De Puntjes

De onderzoeksfase is de basis voor alles. Elk detail moet geverifieerd zijn.

**Verplichte bronnen (in volgorde van prioriteit):**

1. **Officiële Frappe Framework Documentatie** (docs.frappe.io)
   - Primaire bron voor alle API's en methods
   - Versie-specifiek: v14/v15

2. **Officiële ERPNext Documentatie** (docs.erpnext.com)
   - Business logic en module-specifieke patterns

3. **Frappe GitHub Repository**
   - Source code voor exacte method signatures
   - Issues en PR's voor bekende bugs/limitaties

4. **Community Best Practices**
   - Frappe Forum (discuss.frappe.io)
   - Alleen gebruiken indien:
     - ✅ Post is van 2023 of recenter
     - ✅ Bevestigd door meerdere gebruikers
     - ✅ Niet tegengesproken door officiële docs
     - ❌ NIET gebruiken als verouderd of onbevestigd

**Research vereisten per skill:**

| Aspect | Vereiste |
|--------|----------|
| Method signatures | 100% geverifieerd tegen docs/source |
| Parameters | Exact type, verplicht/optioneel, defaults |
| Return values | Exact type en structuur |
| Execution order | Gedocumenteerd met bronvermelding |
| Edge cases | Bekende limitaties en workarounds |
| Versie-compatibiliteit | Expliciet v14/v15 gemarkeerd |

### 3. Actualiteit Boven Alles

```
┌─────────────────────────────────────────────────────────────────────┐
│ GOUDEN REGEL: VEROUDERDE INFORMATIE = GEEN INFORMATIE              │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│ Elke opgenomen best practice, method, of pattern moet:             │
│                                                                     │
│ ✅ Werken in Frappe v14+ / ERPNext v14+                            │
│ ✅ Niet deprecated zijn                                             │
│ ✅ Bevestigd zijn in officiële documentatie OF source code         │
│                                                                     │
│ Bij twijfel over actualiteit:                                       │
│ → Verifieer tegen Frappe GitHub main branch                        │
│ → Of laat de informatie weg                                         │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
```

### 4. Determinisme en Zero-Aannames

Skills bevatten alleen:
- **Feiten** (geverifieerd)
- **Exacte syntax** (gekopieerd uit docs/source)
- **Expliciete instructies** (geen "je kunt overwegen")

Skills bevatten NOOIT:
- Aannames over gebruikersintentie
- Vage suggesties
- Onbevestigde patterns
- Verouderde methods

---

## Architectuur Overzicht

```
erpnext-skills/
├── NL/                                # Nederlandse versies
│   ├── AGENTS/
│   │   ├── erpnext-interpreter/
│   │   └── erpnext-validator/
│   ├── CORE/
│   ├── CLIENT-SCRIPTS/
│   ├── SERVER-SCRIPTS/
│   ├── CONTROLLERS/
│   ├── HOOKS/
│   ├── WHITELISTED/
│   ├── JINJA/
│   ├── SCHEDULER/
│   └── CUSTOM-APP/
│
└── EN/                                # Engelse versies
    └── [zelfde structuur als NL]
```

---

## Complete Skill & Agent Index

### Syntax Skills (8 × 2 talen = 16 files)
| ID | Skill Naam | Focus |
|----|------------|-------|
| SYN-CS | `erpnext-syntax-clientscripts` | JavaScript, frm.*, frappe.* |
| SYN-SS | `erpnext-syntax-serverscripts` | Python in sandbox |
| SYN-CT | `erpnext-syntax-controllers` | Document controller classes |
| SYN-HK | `erpnext-syntax-hooks` | hooks.py structuur |
| SYN-WL | `erpnext-syntax-whitelisted` | @frappe.whitelist() |
| SYN-JJ | `erpnext-syntax-jinja` | Jinja2 templates |
| SYN-SC | `erpnext-syntax-scheduler` | Cron, scheduler_events |
| SYN-CA | `erpnext-syntax-customapp` | App structuur |

### Implementation Skills (8 × 2 talen = 16 files)
| ID | Skill Naam | Focus |
|----|------------|-------|
| IMP-CS | `erpnext-impl-clientscripts` | Form events, async calls |
| IMP-SS | `erpnext-impl-serverscripts` | Doc events, API, scheduled |
| IMP-CT | `erpnext-impl-controllers` | Lifecycle, method chaining |
| IMP-HK | `erpnext-impl-hooks` | Event wiring, overrides |
| IMP-WL | `erpnext-impl-whitelisted` | Security, responses |
| IMP-JJ | `erpnext-impl-jinja` | Print, email, web |
| IMP-SC | `erpnext-impl-scheduler` | Jobs, queues, timeouts |
| IMP-CA | `erpnext-impl-customapp` | Fixtures, migrations |

### Error Handling Skills (7 × 2 talen = 14 files)
| ID | Skill Naam | Focus |
|----|------------|-------|
| ERR-CS | `erpnext-errors-clientscripts` | try/catch, user feedback |
| ERR-SS | `erpnext-errors-serverscripts` | throw, log, rollback |
| ERR-CT | `erpnext-errors-controllers` | Validation, transactions |
| ERR-HK | `erpnext-errors-hooks` | Hook isolation |
| ERR-WL | `erpnext-errors-whitelisted` | HTTP codes, responses |
| ERR-JJ | `erpnext-errors-jinja` | Fallbacks, missing data |
| ERR-SC | `erpnext-errors-scheduler` | Retry, notifications |

### Core Skills (3 × 2 talen = 6 files)
| ID | Skill Naam | Focus |
|----|------------|-------|
| CORE-DB | `erpnext-database` | frappe.db.*, queries |
| CORE-PM | `erpnext-permissions` | Roles, access control |
| CORE-API | `erpnext-api-patterns` | REST/RPC conventies |

### Agents (2 × 2 talen = 4 files)
| ID | Agent Naam | Functie |
|----|------------|---------|
| AGT-INT | `erpnext-interpreter` | Vage input → technische specs |
| AGT-VAL | `erpnext-validator` | Code verificatie tegen skills |

**TOTAAL: 28 Skills/Agents × 2 talen = 56 SKILL.md bestanden**

---

## Fase Planning met Prompts

---

## FASE 1: Research & Syntax Skills (Client + Server)

### Doel
Research uitvoeren en eerste twee syntax skills direct volledig opleveren

### Stap 1.1: Research Client Scripts
**Basis**: `erpnext-vooronderzoek.md` sectie 1 (Client Scripts)

**Aanvullende onderzoeksvragen:**
- Verificatie van alle form events en hun volgorde
- Aanvulling van frm.* methods met exacte signatures
- Verificatie van frappe.* client-side methods
- Verdieping child table event handling
- Actuele async patterns en pitfalls

```
┌─────────────────────────────────────────────────────────────────────┐
│ PROMPT FASE 1.1 - RESEARCH CLIENT SCRIPTS                          │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│ STARTPUNT: Lees eerst erpnext-vooronderzoek.md sectie 1            │
│ (Client Scripts) als basis.                                         │
│                                                                     │
│ Verifieer, verdiep en actualiseer de informatie voor v14/v15:      │
│                                                                     │
│ 1. EVENTS: Alle form-level events met exacte namen en execution    │
│    order. Wanneer wordt welk event getriggerd?                     │
│                                                                     │
│ 2. FRM METHODS: Complete lijst van frm.* methods met:              │
│    - Exacte method signature                                        │
│    - Parameter types (verplicht/optioneel)                         │
│    - Return type                                                    │
│    - Minimaal werkend voorbeeld                                     │
│                                                                     │
│ 3. FRAPPE CLIENT API: Alle frappe.* methods beschikbaar in         │
│    browser context (frappe.call, frappe.db.get_value, etc.)        │
│                                                                     │
│ 4. CHILD TABLES: Hoe child table events werken, syntax voor        │
│    items_add, items_remove, en row-level field changes             │
│                                                                     │
│ 5. ANTI-PATTERNS: Bekende fouten en wat te vermijden               │
│                                                                     │
│ ─────────────────────────────────────────────────────────────────── │
│ BRONVEREISTEN:                                                      │
│ • Basis: erpnext-vooronderzoek.md                                  │
│ • Primair: docs.frappe.io/framework (v14/v15 sectie)               │
│ • Secundair: Frappe GitHub source code voor verificatie            │
│ • Alleen community input van 2023+ en bevestigd werkend            │
│ • GEEN verouderde of deprecated methods opnemen                    │
│ • Bij elke method: noteer of het v14, v15, of beide is             │
│ ─────────────────────────────────────────────────────────────────── │
│                                                                     │
│ Output als gestructureerd research document met bronvermelding.    │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
```

### Stap 1.2: Research Server Scripts
```
┌─────────────────────────────────────────────────────────────────────┐
│ PROMPT FASE 1.2 - RESEARCH SERVER SCRIPTS                          │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│ STARTPUNT: Lees eerst erpnext-vooronderzoek.md sectie 2            │
│ (Server Scripts) als basis.                                         │
│                                                                     │
│ Verifieer, verdiep en actualiseer de informatie voor v14/v15:      │
│                                                                     │
│ 1. SCRIPT TYPES: Alle Server Script types (Document Event, API,    │
│    Scheduler Event, Permission Query) met configuratie opties      │
│                                                                     │
│ 2. SANDBOX: Welke Python modules/functies zijn beschikbaar in de   │
│    Server Script sandbox? Wat is NIET beschikbaar?                 │
│                                                                     │
│ 3. DOC OBJECT: Alle properties en methods op het 'doc' object      │
│                                                                     │
│ 4. FRAPPE API: Beschikbare frappe.* functies binnen server scripts │
│    (frappe.get_doc, frappe.db, frappe.throw, etc.)                 │
│                                                                     │
│ 5. EVENT MAPPING: UI event namen vs interne hook namen             │
│    (Before Save = validate, After Save = on_update, etc.)          │
│                                                                     │
│ 6. BEPERKINGEN: Wat kan NIET in Server Scripts vs Controllers?     │
│                                                                     │
│ ─────────────────────────────────────────────────────────────────── │
│ BRONVEREISTEN:                                                      │
│ • Basis: erpnext-vooronderzoek.md                                  │
│ • Primair: docs.frappe.io/framework (v14/v15 sectie)               │
│ • Secundair: Frappe GitHub source code voor verificatie            │
│ • Alleen community input van 2023+ en bevestigd werkend            │
│ • GEEN verouderde of deprecated methods opnemen                    │
│ • Bij elke method: noteer of het v14, v15, of beide is             │
│ ─────────────────────────────────────────────────────────────────── │
│                                                                     │
│ Output als gestructureerd research document met bronvermelding.    │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
```

### Stap 1.3: Maak eerste skill (NL + EN)
```
┌─────────────────────────────────────────────────────────────────────┐
│ PROMPT FASE 1.3 - CREËER SKILL: erpnext-syntax-clientscripts       │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│ Gebruik het research document uit stap 1.1 om de skill             │
│ 'erpnext-syntax-clientscripts' te maken.                           │
│                                                                     │
│ VEREISTEN:                                                          │
│ 1. Volg exact de Anthropic skill-creator richtlijnen               │
│ 2. Gebruik init_skill.py voor initialisatie                        │
│ 3. Maak TWEE versies: NL en EN                                     │
│                                                                     │
│ STRUCTUUR:                                                          │
│ erpnext-syntax-clientscripts/                                       │
│ ├── SKILL.md (lean, <500 regels)                                   │
│ └── references/                                                     │
│     ├── methods.md (alle frm.* signatures)                         │
│     ├── events.md (alle events met volgorde)                       │
│     ├── examples.md (10+ werkende voorbeelden)                     │
│     └── anti-patterns.md (wat te vermijden)                        │
│                                                                     │
│ SKILL.MD MOET BEVATTEN:                                             │
│ - Frontmatter met duidelijke triggers                              │
│ - Quick reference voor meest gebruikte patterns                    │
│ - Decision tree: "welke event gebruik ik wanneer?"                 │
│ - Links naar alle reference files                                   │
│                                                                     │
│ TOON GEEN AANNAMES - alleen geverifieerde informatie uit research. │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
```

### Stap 1.4: Maak tweede skill (NL + EN)
```
┌─────────────────────────────────────────────────────────────────────┐
│ PROMPT FASE 1.4 - CREËER SKILL: erpnext-syntax-serverscripts       │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│ Gebruik het research document uit stap 1.2 om de skill             │
│ 'erpnext-syntax-serverscripts' te maken.                           │
│                                                                     │
│ [Zelfde structuur en vereisten als 1.3]                            │
│                                                                     │
│ EXTRA VOOR SERVER SCRIPTS:                                          │
│ - Duidelijk onderscheid tussen script types                        │
│ - Sandbox beperkingen expliciet benoemen                           │
│ - Event name mapping tabel (UI → intern)                           │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
```

### Stap 1.5: Package Skills
```
┌─────────────────────────────────────────────────────────────────────┐
│ PROMPT FASE 1.5 - PACKAGE SKILLS                                   │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│ Package de gemaakte skills:                                         │
│                                                                     │
│ 1. Valideer met quick_validate.py                                  │
│ 2. Package met package_skill.py                                    │
│ 3. Ga direct door naar Fase 2                                      │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
```

### Exit Criteria Fase 1
- [ ] Research documenten voor Client Scripts en Server Scripts
- [ ] `erpnext-syntax-clientscripts` NL + EN compleet
- [ ] `erpnext-syntax-serverscripts` NL + EN compleet
- [ ] Skills gepackaged met package_skill.py

---

## FASE 2: Remaining Syntax Skills

### Doel
Alle 6 overige syntax skills compleet maken (beide talen)

### Stap 2.1: Research Controllers
```
┌─────────────────────────────────────────────────────────────────────┐
│ PROMPT FASE 2.1 - RESEARCH DOCUMENT CONTROLLERS                    │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│ STARTPUNT: Lees eerst erpnext-vooronderzoek.md sectie 3            │
│ (Document Controllers) als basis.                                   │
│                                                                     │
│ Verifieer, verdiep en actualiseer:                                 │
│                                                                     │
│ 1. CLASS STRUCTUUR: Hoe een controller class opbouwen              │
│    (imports, inheritance, naming conventions)                       │
│                                                                     │
│ 2. LIFECYCLE METHODS: Complete lijst met execution order:          │
│    autoname, before_naming, before_validate, validate,             │
│    before_save, before_insert, after_insert, on_update,            │
│    before_submit, on_submit, before_cancel, on_cancel,             │
│    on_trash, after_delete, on_change                               │
│                                                                     │
│ 3. SPECIALE METHODS: db_insert, db_update, run_method,            │
│    get_doc_before_save, etc.                                       │
│                                                                     │
│ 4. FLAGS: doc.flags systeem en standaard flags                     │
│                                                                     │
│ 5. WHITELISTED METHODS IN CONTROLLER: @frappe.whitelist()          │
│    binnen een controller class                                      │
│                                                                     │
│ ─────────────────────────────────────────────────────────────────── │
│ BRONVEREISTEN:                                                      │
│ • Basis: erpnext-vooronderzoek.md                                  │
│ • Primair: docs.frappe.io/framework (v14/v15 sectie)               │
│ • Secundair: Frappe GitHub source code voor verificatie            │
│ • Alleen community input van 2023+ en bevestigd werkend            │
│ • GEEN verouderde of deprecated methods opnemen                    │
│ ─────────────────────────────────────────────────────────────────── │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
```

### Stap 2.2: Research hooks.py
```
┌─────────────────────────────────────────────────────────────────────┐
│ PROMPT FASE 2.2 - RESEARCH HOOKS.PY                                │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│ STARTPUNT: Lees eerst erpnext-vooronderzoek.md sectie 4            │
│ (hooks.py Configuratie) als basis.                                  │
│                                                                     │
│ Verifieer, verdiep en actualiseer:                                 │
│                                                                     │
│ 1. DOC_EVENTS: Syntax en alle beschikbare events                   │
│ 2. SCHEDULER_EVENTS: all, hourly, daily, weekly, monthly, cron     │
│ 3. OVERRIDE HOOKS: override_whitelisted_methods,                   │
│    override_doctype_class                                           │
│ 4. PERMISSION HOOKS: permission_query_conditions, has_permission   │
│ 5. INCLUDE HOOKS: app_include_js, app_include_css, doctype_js      │
│ 6. BOOT HOOKS: extend_bootinfo                                     │
│ 7. FIXTURES: syntax en filters                                     │
│ 8. JENV: methods en filters toevoegen                              │
│                                                                     │
│ Voor elke hook: exacte syntax + werkend voorbeeld.                 │
│                                                                     │
│ ─────────────────────────────────────────────────────────────────── │
│ BRONVEREISTEN:                                                      │
│ • Basis: erpnext-vooronderzoek.md                                  │
│ • Primair: docs.frappe.io/framework (v14/v15 sectie)               │
│ • Secundair: Frappe GitHub source code voor verificatie            │
│ • Alleen community input van 2023+ en bevestigd werkend            │
│ • GEEN verouderde of deprecated hooks opnemen                      │
│ ─────────────────────────────────────────────────────────────────── │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
```

### Stap 2.3: Research Whitelisted Methods
```
┌─────────────────────────────────────────────────────────────────────┐
│ PROMPT FASE 2.3 - RESEARCH WHITELISTED METHODS                     │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│ STARTPUNT: Lees eerst erpnext-vooronderzoek.md sectie 5            │
│ (Whitelisted Methods) als basis.                                    │
│                                                                     │
│ Verifieer, verdiep en actualiseer:                                 │
│                                                                     │
│ 1. DECORATOR OPTIES: allow_guest, methods, xss_safe               │
│ 2. PARAMETER HANDLING: frappe.form_dict, type conversion          │
│ 3. RESPONSE PATTERNS: return value, frappe.response               │
│ 4. PERMISSIONS: frappe.has_permission checks                       │
│ 5. AANROEPEN: frappe.call syntax vanuit client                     │
│ 6. ERROR HANDLING: juiste manier om errors te returnen            │
│                                                                     │
│ ─────────────────────────────────────────────────────────────────── │
│ BRONVEREISTEN:                                                      │
│ • Basis: erpnext-vooronderzoek.md                                  │
│ • Primair: docs.frappe.io/framework (v14/v15 sectie)               │
│ • Secundair: Frappe GitHub source code voor verificatie            │
│ • Alleen community input van 2023+ en bevestigd werkend            │
│ • GEEN verouderde of deprecated patterns opnemen                   │
│ ─────────────────────────────────────────────────────────────────── │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
```

### Stap 2.4: Research Jinja
```
┌─────────────────────────────────────────────────────────────────────┐
│ PROMPT FASE 2.4 - RESEARCH JINJA TEMPLATES                         │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│ STARTPUNT: Lees eerst erpnext-vooronderzoek.md sectie 6            │
│ (Jinja Templates) als basis.                                        │
│                                                                     │
│ Verifieer, verdiep en actualiseer:                                 │
│                                                                     │
│ 1. BESCHIKBARE OBJECTEN: doc, frappe, frappe.utils                │
│ 2. FRAPPE METHODS IN JINJA: format, format_date, get_doc, etc.    │
│ 3. PRINT FORMATS: Specifieke context en variabelen                 │
│ 4. EMAIL TEMPLATES: Beschikbare variabelen                         │
│ 5. WEB TEMPLATES: Context en routing                               │
│ 6. CUSTOM FILTERS/METHODS: Via jenv hook                          │
│                                                                     │
│ ─────────────────────────────────────────────────────────────────── │
│ BRONVEREISTEN:                                                      │
│ • Basis: erpnext-vooronderzoek.md                                  │
│ • Primair: docs.frappe.io/framework (v14/v15 sectie)               │
│ • Secundair: Frappe GitHub source code voor verificatie            │
│ • Alleen community input van 2023+ en bevestigd werkend            │
│ • GEEN verouderde of deprecated syntax opnemen                     │
│ ─────────────────────────────────────────────────────────────────── │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
```

### Stap 2.5: Research Scheduler
```
┌─────────────────────────────────────────────────────────────────────┐
│ PROMPT FASE 2.5 - RESEARCH SCHEDULER & BACKGROUND JOBS             │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│ STARTPUNT: Lees eerst erpnext-vooronderzoek.md sectie 7            │
│ (Background Jobs & Scheduler) als basis.                            │
│                                                                     │
│ Verifieer, verdiep en actualiseer:                                 │
│                                                                     │
│ 1. SCHEDULER_EVENTS: Alle types en cron syntax                     │
│ 2. FRAPPE.ENQUEUE: Parameters, queues, timeouts                    │
│ 3. FRAPPE.ENQUEUE_DOC: Document method aanroepen                   │
│ 4. QUEUE TYPES: short, default, long - wanneer welke?             │
│ 5. ERROR HANDLING: Wat gebeurt bij job failure?                    │
│ 6. MONITORING: Hoe jobs monitoren?                                 │
│                                                                     │
│ ─────────────────────────────────────────────────────────────────── │
│ BRONVEREISTEN:                                                      │
│ • Basis: erpnext-vooronderzoek.md                                  │
│ • Primair: docs.frappe.io/framework (v14/v15 sectie)               │
│ • Secundair: Frappe GitHub source code voor verificatie            │
│ • Alleen community input van 2023+ en bevestigd werkend            │
│ • GEEN verouderde of deprecated patterns opnemen                   │
│ ─────────────────────────────────────────────────────────────────── │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
```

### Stap 2.6: Research Custom App
```
┌─────────────────────────────────────────────────────────────────────┐
│ PROMPT FASE 2.6 - RESEARCH CUSTOM APP STRUCTUUR                    │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│ STARTPUNT: Lees eerst erpnext-vooronderzoek.md voor context        │
│ over hoe alle scripting mechanismen samenkomen in een custom app.  │
│                                                                     │
│ Onderzoek custom app development structuur:                        │
│                                                                     │
│ 1. APP STRUCTUUR: Vereiste bestanden en directories                │
│ 2. SETUP.PY / PYPROJECT.TOML: Correcte configuratie               │
│ 3. __INIT__.PY: Wat moet erin?                                     │
│ 4. MODULES: Hoe modules toevoegen                                  │
│ 5. DEPENDENCIES: Hoe dependencies declareren                       │
│ 6. PATCHES: Migratie scripts schrijven                             │
│ 7. FIXTURES: Export en import                                      │
│                                                                     │
│ ─────────────────────────────────────────────────────────────────── │
│ BRONVEREISTEN:                                                      │
│ • Basis: erpnext-vooronderzoek.md                                  │
│ • Primair: docs.frappe.io/framework (v14/v15 sectie)               │
│ • Secundair: Frappe GitHub source code voor verificatie            │
│ • Alleen community input van 2023+ en bevestigd werkend            │
│ • GEEN verouderde of deprecated structuren opnemen                 │
│ ─────────────────────────────────────────────────────────────────── │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
```

### Stap 2.7-2.12: Creëer Skills
```
┌─────────────────────────────────────────────────────────────────────┐
│ PROMPT FASE 2.7-2.12 - CREËER SYNTAX SKILLS                        │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│ Voor elke categorie (Controllers, Hooks, Whitelisted, Jinja,       │
│ Scheduler, Custom App):                                             │
│                                                                     │
│ Gebruik het research document om de syntax skill te maken:         │
│ - erpnext-syntax-controllers                                        │
│ - erpnext-syntax-hooks                                              │
│ - erpnext-syntax-whitelisted                                        │
│ - erpnext-syntax-jinja                                              │
│ - erpnext-syntax-scheduler                                          │
│ - erpnext-syntax-customapp                                          │
│                                                                     │
│ Maak NL + EN versies. Volg zelfde structuur als Fase 1.            │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
```

### Exit Criteria Fase 2
- [ ] Research documenten voor alle 6 categorieën
- [ ] 6 syntax skills compleet (NL + EN = 12 SKILL.md files)
- [ ] Alle skills gepackaged

---

## FASE 3: Core Skills

### Doel
Cross-cutting concerns: database, permissions, API patterns

### Stap 3.1: Research & Create erpnext-database
```
┌─────────────────────────────────────────────────────────────────────┐
│ PROMPT FASE 3.1 - CORE SKILL: erpnext-database                     │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│ STARTPUNT: Lees erpnext-vooronderzoek.md sectie 9 (Best Practices) │
│ voor database gerelateerde patterns.                                │
│                                                                     │
│ Onderzoek en maak skill voor database operaties:                   │
│                                                                     │
│ RESEARCH:                                                           │
│ 1. frappe.db.* methods (get_value, get_all, set_value, sql, etc.) │
│ 2. frappe.get_doc, frappe.get_cached_doc, frappe.new_doc          │
│ 3. Query builders en filters                                       │
│ 4. Transacties: commit, rollback, savepoint                        │
│ 5. Performance: N+1 vermijden, caching                             │
│ 6. SQL injection preventie                                          │
│                                                                     │
│ SKILL FOCUS:                                                        │
│ - Welke method voor welke use case (decision tree)                 │
│ - Correcte filter syntax                                            │
│ - Performance best practices                                        │
│ - Veilige SQL patterns                                              │
│                                                                     │
│ ─────────────────────────────────────────────────────────────────── │
│ BRONVEREISTEN:                                                      │
│ • Basis: erpnext-vooronderzoek.md                                  │
│ • Primair: docs.frappe.io/framework (v14/v15 sectie)               │
│ • Secundair: Frappe GitHub source code voor verificatie            │
│ • Alleen community input van 2023+ en bevestigd werkend            │
│ • GEEN verouderde of deprecated methods opnemen                    │
│ ─────────────────────────────────────────────────────────────────── │
│                                                                     │
│ Maak NL + EN versies.                                               │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
```

### Stap 3.2: Research & Create erpnext-permissions
```
┌─────────────────────────────────────────────────────────────────────┐
│ PROMPT FASE 3.2 - CORE SKILL: erpnext-permissions                  │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│ STARTPUNT: Lees erpnext-vooronderzoek.md sectie 4 (hooks.py) voor  │
│ permission hooks en sectie 2 (Server Scripts) voor Permission      │
│ Query scripts.                                                      │
│                                                                     │
│ Onderzoek en maak skill voor permissions:                          │
│                                                                     │
│ RESEARCH:                                                           │
│ 1. Role-based permissions systeem                                  │
│ 2. frappe.has_permission() gebruik                                 │
│ 3. Permission Query Conditions                                      │
│ 4. User permissions                                                 │
│ 5. ignore_permissions flag                                          │
│ 6. Custom permission logic                                          │
│                                                                     │
│ SKILL FOCUS:                                                        │
│ - Wanneer welk permission type                                     │
│ - Veilig omgaan met ignore_permissions                             │
│ - Row-level security implementeren                                  │
│                                                                     │
│ ─────────────────────────────────────────────────────────────────── │
│ BRONVEREISTEN:                                                      │
│ • Basis: erpnext-vooronderzoek.md                                  │
│ • Primair: docs.frappe.io/framework (v14/v15 sectie)               │
│ • Secundair: Frappe GitHub source code voor verificatie            │
│ • Alleen community input van 2023+ en bevestigd werkend            │
│ • GEEN verouderde of deprecated patterns opnemen                   │
│ ─────────────────────────────────────────────────────────────────── │
│                                                                     │
│ Maak NL + EN versies.                                               │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
```

### Stap 3.3: Research & Create erpnext-api-patterns
```
┌─────────────────────────────────────────────────────────────────────┐
│ PROMPT FASE 3.3 - CORE SKILL: erpnext-api-patterns                 │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│ STARTPUNT: Lees erpnext-vooronderzoek.md sectie 5 (Whitelisted     │
│ Methods) en sectie 2 (Server Scripts - API type) als basis.        │
│                                                                     │
│ Onderzoek en maak skill voor API patterns:                         │
│                                                                     │
│ RESEARCH:                                                           │
│ 1. REST API conventies in Frappe                                   │
│ 2. frappe.response object                                          │
│ 3. Status codes en error responses                                 │
│ 4. Authentication methods                                           │
│ 5. Rate limiting                                                    │
│ 6. Webhook patterns                                                 │
│                                                                     │
│ SKILL FOCUS:                                                        │
│ - Consistente response formats                                      │
│ - Error response structuur                                          │
│ - Authenticatie best practices                                      │
│                                                                     │
│ ─────────────────────────────────────────────────────────────────── │
│ BRONVEREISTEN:                                                      │
│ • Basis: erpnext-vooronderzoek.md                                  │
│ • Primair: docs.frappe.io/framework (v14/v15 sectie)               │
│ • Secundair: Frappe GitHub source code voor verificatie            │
│ • Alleen community input van 2023+ en bevestigd werkend            │
│ • GEEN verouderde of deprecated patterns opnemen                   │
│ ─────────────────────────────────────────────────────────────────── │
│                                                                     │
│ Maak NL + EN versies.                                               │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
```

### Exit Criteria Fase 3
- [ ] 3 core skills compleet (NL + EN = 6 SKILL.md files)
- [ ] Alle skills gepackaged

---

## FASE 4: Implementation Skills

### Doel
Workflow patterns en decision trees voor correcte implementatie

### Prompt Template voor alle Implementation Skills
```
┌─────────────────────────────────────────────────────────────────────┐
│ PROMPT FASE 4.x - IMPLEMENTATION SKILL: [categorie]                │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│ STARTPUNT: Lees erpnext-vooronderzoek.md voor de relevante sectie  │
│ en de bijbehorende syntax skill uit Fase 1/2.                      │
│                                                                     │
│ Maak implementation skill voor [categorie].                        │
│                                                                     │
│ FOCUS:                                                              │
│ 1. DECISION TREE: "Ik wil X bereiken, welke aanpak?"              │
│    - Feature type → aanbevolen implementatie                       │
│    - Wanneer client vs server                                       │
│    - Wanneer script vs controller vs hook                          │
│                                                                     │
│ 2. WORKFLOW PATTERNS:                                               │
│    - Stapsgewijze implementatie guides                             │
│    - "Als je X wilt, doe dan Y"                                    │
│                                                                     │
│ 3. INTEGRATIE:                                                      │
│    - Hoe combineert dit met andere lagen?                          │
│    - Verwijzingen naar relevante CORE skills                       │
│                                                                     │
│ 4. REAL-WORLD EXAMPLES:                                             │
│    - 5+ complete implementatie voorbeelden                         │
│    - Van requirement → werkende code                                │
│                                                                     │
│ STRUCTUUR:                                                          │
│ references/                                                         │
│ ├── decision-tree.md                                                │
│ ├── workflows.md                                                    │
│ └── examples.md                                                     │
│                                                                     │
│ ─────────────────────────────────────────────────────────────────── │
│ CONVENTIES:                                                         │
│ • Basis: erpnext-vooronderzoek.md                                  │
│ • Volg Anthropic skill-creator richtlijnen exact                   │
│ • Alle voorbeelden moeten v14/v15 compatibel zijn                  │
│ • Geen deprecated patterns of methods gebruiken                    │
│ • Bij twijfel: verifieer tegen Frappe source code                  │
│ ─────────────────────────────────────────────────────────────────── │
│                                                                     │
│ Maak NL + EN versies.                                               │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
```

### Skills te maken in Fase 4
1. erpnext-impl-clientscripts
2. erpnext-impl-serverscripts
3. erpnext-impl-controllers
4. erpnext-impl-hooks
5. erpnext-impl-whitelisted
6. erpnext-impl-jinja
7. erpnext-impl-scheduler
8. erpnext-impl-customapp

### Exit Criteria Fase 4
- [ ] 8 implementation skills compleet (NL + EN = 16 SKILL.md files)
- [ ] Elke skill bevat decision tree
- [ ] Elke skill bevat minimaal 5 voorbeelden
- [ ] Alle skills gepackaged

---

## FASE 5: Error Handling Skills

### Doel
Robuuste code met correcte foutafhandeling

### Prompt Template voor alle Error Handling Skills
```
┌─────────────────────────────────────────────────────────────────────┐
│ PROMPT FASE 5.x - ERROR HANDLING SKILL: [categorie]                │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│ STARTPUNT: Lees erpnext-vooronderzoek.md sectie 9 (Best Practices) │
│ voor error handling patterns.                                       │
│                                                                     │
│ Maak error handling skill voor [categorie].                        │
│                                                                     │
│ FOCUS:                                                              │
│ 1. ERROR TYPES:                                                     │
│    - Validation errors (user-facing)                               │
│    - System errors (developer-facing)                              │
│    - Wanneer frappe.throw vs raise                                 │
│                                                                     │
│ 2. LOGGING:                                                         │
│    - frappe.log_error patterns                                     │
│    - Wat loggen, wat niet                                          │
│    - Error context meegeven                                         │
│                                                                     │
│ 3. RECOVERY:                                                        │
│    - Transaction rollback                                           │
│    - Graceful degradation                                           │
│    - Retry patterns                                                 │
│                                                                     │
│ 4. USER FEEDBACK:                                                   │
│    - Duidelijke foutmeldingen                                       │
│    - Geen technische details naar gebruiker                        │
│                                                                     │
│ STRUCTUUR:                                                          │
│ references/                                                         │
│ ├── error-types.md                                                  │
│ ├── logging-patterns.md                                             │
│ └── recovery-patterns.md                                            │
│                                                                     │
│ ─────────────────────────────────────────────────────────────────── │
│ CONVENTIES:                                                         │
│ • Basis: erpnext-vooronderzoek.md                                  │
│ • Volg Anthropic skill-creator richtlijnen exact                   │
│ • Alle error patterns moeten v14/v15 compatibel zijn               │
│ • Geen deprecated error handling methods gebruiken                 │
│ • Bij twijfel: verifieer tegen Frappe source code                  │
│ ─────────────────────────────────────────────────────────────────── │
│                                                                     │
│ Maak NL + EN versies.                                               │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
```

### Skills te maken in Fase 5
1. erpnext-errors-clientscripts
2. erpnext-errors-serverscripts
3. erpnext-errors-controllers
4. erpnext-errors-hooks
5. erpnext-errors-whitelisted
6. erpnext-errors-jinja
7. erpnext-errors-scheduler

### Exit Criteria Fase 5
- [ ] 7 error handling skills compleet (NL + EN = 14 SKILL.md files)
- [ ] Elke skill bevat error type decision tree
- [ ] Elke skill bevat logging voorbeelden
- [ ] Alle skills gepackaged

---

## FASE 6: Agents

### Doel
Intelligente assistenten voor interpretatie en validatie, gebouwd volgens Claude Agent SDK conventies

### Agent Design Principes

```
┌─────────────────────────────────────────────────────────────────────┐
│ CLAUDE AGENT SDK CONVENTIES                                        │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│ Agents volgen officiële Anthropic Agent SDK patterns:              │
│                                                                     │
│ • Agents zijn skills met uitgebreide decision logic                │
│ • Agents VRAGEN door bij onduidelijkheid (geen aannames)           │
│ • Agents verwijzen naar andere skills voor uitvoering              │
│ • Agents hebben duidelijke input/output contracten                 │
│                                                                     │
│ STRUCTUUR:                                                          │
│ agent-name/                                                         │
│ ├── SKILL.md (agent instructies en gedragsregels)                  │
│ └── references/                                                     │
│     ├── decision-logic.md (wanneer wat vragen)                     │
│     └── output-formats.md (gestructureerde outputs)                │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
```

### Stap 6.1: ERPNext Interpreter Agent
```
┌─────────────────────────────────────────────────────────────────────┐
│ PROMPT FASE 6.1 - AGENT: erpnext-interpreter                       │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│ Maak een interpreter agent die vage requirements vertaalt naar     │
│ technische specificaties.                                           │
│                                                                     │
│ AGENT GEDRAG:                                                       │
│                                                                     │
│ 1. ANALYSEER INPUT:                                                 │
│    - Identificeer wat de gebruiker wil bereiken                    │
│    - Detecteer ontbrekende informatie                              │
│                                                                     │
│ 2. VRAAG DOOR (max 3 vragen per keer):                             │
│    □ Welke DocType(s) zijn betrokken?                              │
│    □ Moet dit client-side of server-side?                          │
│    □ Welke trigger/event?                                           │
│    □ Welke velden zijn betrokken?                                  │
│    □ Wat zijn de edge cases?                                        │
│    □ Zijn er permissie vereisten?                                  │
│                                                                     │
│ 3. OUTPUT TECHNISCHE SPEC:                                          │
│    - Implementatie type (client script, server script, etc.)       │
│    - Benodigde events/hooks                                         │
│    - Pseudo-code of stappenplan                                     │
│    - Verwijzing naar relevante skills                              │
│                                                                     │
│ VERIFICATIE REGELS:                                                 │
│ - NOOIT aannemen welke DocType                                     │
│ - ALTIJD bevestigen client vs server                               │
│ - ALTIJD vragen naar edge cases bij business logic                 │
│                                                                     │
│ Maak NL + EN versies.                                               │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
```

### Stap 6.2: ERPNext Validator Agent
```
┌─────────────────────────────────────────────────────────────────────┐
│ PROMPT FASE 6.2 - AGENT: erpnext-validator                         │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│ Maak een validator agent die gegenereerde code checkt.             │
│                                                                     │
│ AGENT GEDRAG:                                                       │
│                                                                     │
│ 1. IDENTIFICEER CODE TYPE:                                          │
│    - Client Script / Server Script / Controller / etc.             │
│                                                                     │
│ 2. LAAD RELEVANTE SKILLS:                                           │
│    - Corresponderende SYNTAX skill                                  │
│    - Corresponderende ERROR skill                                   │
│    - Relevante CORE skills                                          │
│                                                                     │
│ 3. VALIDEER TEGEN REGELS:                                           │
│    □ Syntax correct?                                                │
│    □ Juiste method signatures?                                      │
│    □ Error handling aanwezig?                                       │
│    □ Permissions gecheckt?                                          │
│    □ Performance issues?                                            │
│                                                                     │
│ 4. OUTPUT RAPPORT:                                                  │
│    ✅ Wat is correct                                                │
│    ❌ Wat moet gefixed (met fix suggestie)                         │
│    ⚠️ Warnings (optionele verbeteringen)                           │
│                                                                     │
│ Maak NL + EN versies.                                               │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
```

### Exit Criteria Fase 6
- [ ] 2 agents compleet (NL + EN = 4 SKILL.md files)
- [ ] Agents gepackaged

---

## FASE 7: Finalisatie & Packaging

### Doel
Alles samenvoegen en distribueerbaar maken

### Stap 7.1: Cross-Skill Dependencies
```
┌─────────────────────────────────────────────────────────────────────┐
│ PROMPT FASE 7.1 - DOCUMENTEER DEPENDENCIES                         │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│ Maak een dependency matrix voor alle skills:                       │
│                                                                     │
│ 1. Welke skills verwijzen naar welke andere skills?                │
│ 2. Welke skills moeten samen geladen worden?                       │
│ 3. Wat is de aanbevolen laadvolgorde?                              │
│                                                                     │
│ Output: dependencies.md met matrix en instructies.                 │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
```

### Stap 7.2: Final Packaging
```
┌─────────────────────────────────────────────────────────────────────┐
│ PROMPT FASE 7.2 - PACKAGE ALLE SKILLS                              │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│ 1. Valideer alle skills met quick_validate.py                      │
│ 2. Package elke skill met package_skill.py                         │
│ 3. Maak master index met alle skills en beschrijvingen             │
│ 4. Maak installatie instructies                                     │
│                                                                     │
│ Output:                                                             │
│ - 56 .skill bestanden (28 NL + 28 EN)                              │
│ - INDEX.md met overzicht                                            │
│ - INSTALL.md met instructies                                        │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
```

### Exit Criteria Fase 7
- [ ] Dependency matrix compleet
- [ ] Alle 56 .skill files gepackaged
- [ ] INDEX.md en INSTALL.md compleet

---

## Uitvoering Overzicht

| Fase | Focus | Deliverables |
|------|-------|--------------|
| 1 | Research + Client/Server Syntax | 2 syntax skills (4 files) |
| 2 | Remaining Syntax | 6 syntax skills (12 files) |
| 3 | Core Skills | 3 core skills (6 files) |
| 4 | Implementation | 8 impl skills (16 files) |
| 5 | Error Handling | 7 error skills (14 files) |
| 6 | Agents | 2 agents (4 files) |
| 7 | Finalisatie | Packaging + docs |

**TOTAAL: 56 SKILL.md files + supporting docs**

**Uitvoeringsmodus**: Sequentieel, one-shot, geen iteraties

---

## Kwaliteitsgaranties

### Per Skill
- [ ] SKILL.md < 500 regels
- [ ] Frontmatter met duidelijke triggers
- [ ] Decision tree of quick reference
- [ ] Minimaal 3 werkende voorbeelden
- [ ] Anti-patterns gedocumenteerd
- [ ] NL én EN versie

### Per Fase
- [ ] Research document aanwezig (waar van toepassing)
- [ ] Alle skills gepackaged
- [ ] Exit criteria afgevinkt

### Totaal
- [ ] Interpreter agent kan vage input verwerken
- [ ] Validator agent detecteert fouten
- [ ] Alle 56 skills compleet en gepackaged
- [ ] Geen syntax errors in skill voorbeelden

---

## Appendix: File Teller

```
SYNTAX SKILLS:      8 × 2 talen = 16 files
IMPLEMENTATION:     8 × 2 talen = 16 files  
ERROR HANDLING:     7 × 2 talen = 14 files
CORE SKILLS:        3 × 2 talen =  6 files
AGENTS:             2 × 2 talen =  4 files
─────────────────────────────────────────
TOTAAL SKILL.md:                  56 files

SUPPORTING DOCS:
- dependencies.md
- INDEX.md  
- INSTALL.md
- Research docs (8 categorieën)
```
