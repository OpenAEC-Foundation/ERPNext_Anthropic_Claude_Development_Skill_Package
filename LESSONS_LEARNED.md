# Lessons Learned: ERPNext Skills Package Project

> **Project**: ERPNext/Frappe Skills Package voor Claude  
> **Periode**: Januari 2025 - Januari 2026  
> **Organisatie**: OpenAEC Foundation

Dit document bevat alle geleerde lessen uit het ontwikkelen van een comprehensive AI skill package voor een open source project. De lessen zijn bruikbaar voor iedereen die een soortgelijk project wil opzetten.

---

## Inhoudsopgave

1. [Technische Lessen: Frappe/ERPNext](#1-technische-lessen-frappeerpnext)
2. [Project Management Lessen](#2-project-management-lessen)
3. [Claude/AI Workflow Lessen](#3-claudeai-workflow-lessen)
4. [Skill Development Lessen](#4-skill-development-lessen)
5. [GitHub Integratie Lessen](#5-github-integratie-lessen)
6. [Valkuilen en Oplossingen](#6-valkuilen-en-oplossingen)
7. [Best Practices Samenvatting](#7-best-practices-samenvatting)
8. [**META-LESSEN: Project Structuur & Planning**](#8-meta-lessen-project-structuur--planning) ← NIEUW

---

## 1. Technische Lessen: Frappe/ERPNext

### 1.1 Server Script Sandbox - KRITIEKE ONTDEKKING

**De belangrijkste technische les van dit project:**

Frappe Server Scripts draaien in een **RestrictedPython sandbox** die ALLE import statements blokkeert.

```python
# ❌ FOUT - Geeft altijd error
from frappe.utils import nowdate
import json

# ✅ CORRECT - Gebruik pre-loaded namespace
date = frappe.utils.nowdate()
data = frappe.parse_json(json_string)
```

**Impact**: Dit beïnvloedt ALLE code generatie voor Server Scripts. Elke AI bot die ERPNext code genereert moet deze beperking kennen.

**Beschikbare alternatieven in de sandbox:**

| In plaats van import | Gebruik direct |
|---------------------|----------------|
| `from frappe.utils import nowdate` | `frappe.utils.nowdate()` |
| `from datetime import timedelta` | `frappe.utils.add_days()` |
| `import json` | `frappe.parse_json()` |
| `import re` | Niet beschikbaar - gebruik Python string methods |

### 1.2 Versieverschillen v14 vs v15

| Feature | v14 | v15 | Impact |
|---------|-----|-----|--------|
| **Scheduler tick** | 4 min | 60 sec | Jobs draaien vaker in v15 |
| **Job deduplicatie** | `job_name` | `job_id` + `is_job_enqueued()` | `job_name` is deprecated |
| **Nieuwe hooks** | - | `before_discard`, `on_discard` | Extra lifecycle events |
| **Type annotations** | ❌ | ✅ Auto-generated | Betere IDE support |
| **Controller extends** | `override_doctype_class` | + `extend_doctype_class` (v16) | Veiliger overrides |

### 1.3 hooks.py Resolutie

**"Last writer wins" principe**: Bij conflicterende hooks tussen apps wint de laatst geladen app.

**Kritiek**: `bench migrate` is VERPLICHT na elke wijziging in `scheduler_events`. Zonder migrate worden wijzigingen niet opgepikt!

### 1.4 on_change Hook Gedrag

De `on_change` hook triggert na ELKE wijziging, inclusief `db_set()` operaties. Dit kan onverwachte loops veroorzaken.

```python
# ❌ FOUT - Kan infinite loop veroorzaken
def on_change(doc, method):
    frappe.db.set_value(doc.doctype, doc.name, "counter", doc.counter + 1)
    # ^ Dit triggert on_change opnieuw!

# ✅ CORRECT - Gebruik update_modified=False of flags
def on_change(doc, method):
    if doc.flags.get("in_on_change"):
        return
    doc.flags.in_on_change = True
    frappe.db.set_value(doc.doctype, doc.name, "counter", doc.counter + 1, 
                        update_modified=False)
```

### 1.5 Wijzigingen na on_update

Wijzigingen aan `self` in `on_update` worden NIET automatisch opgeslagen - het document is al naar de database geschreven.

```python
# ❌ FOUT - Wijziging gaat verloren
def on_update(self):
    self.status = "Completed"  # Niet opgeslagen!

# ✅ CORRECT - Gebruik db_set
def on_update(self):
    frappe.db.set_value(self.doctype, self.name, "status", "Completed")
```

### 1.6 Queue Timeouts

| Queue | Timeout | Gebruik |
|-------|---------|---------┤
| short | 300s (5 min) | Snelle operaties |
| default | 300s (5 min) | Normale taken |
| long | 1500s (25 min) | Zware verwerking |

### 1.9 Database Operaties - Fase 3 Ontdekkingen

**Drie abstractieniveaus kiezen:**

```
High-level ORM     → frappe.get_doc()      → Met validaties, langzamer
Mid-level Query    → frappe.db.get_list()  → Sneller, met/zonder permissions
Low-level SQL      → frappe.db.sql()       → Snelst, geen bescherming
```

**REGEL**: Altijd hoogst mogelijke abstractieniveau gebruiken.

**Kritieke Insights:**

1. **`db_set` bypassed ALLES** - Geen validate, geen on_update, geen permissions
2. **Transaction hooks (v15+)** - `frappe.db.after_rollback.add()` en `frappe.db.after_commit.add()`
3. **get_list vs get_all** - `get_list` past permissions toe, `get_all` niet
4. **v16 Breaking Changes** - Aggregatie syntax is veranderd
5. **SQL Injection risico** - Altijd parameterized queries gebruiken
6. **N+1 Query Problem** - Batch fetch in plaats van loop queries

---

## 2. Project Management Lessen

### 2.1 Fase Opsplitsing Criteria

**Wanneer een fase splitsen:**

| Criterium | Drempelwaarde | Actie |
|-----------|---------------|-------|
| Research document regels | >700 | Splitsen |
| Reference files | >5 | Splitsen |
| Secties/onderwerpen | >8-10 | Splitsen |
| Gespreksduur | Near limit | Splitsen |

### 2.2 Research-First Aanpak

**Gouden regel**: Nooit skills maken zonder grondige research.

### 2.3 One-Shot Mindset

**Principe**: Plan grondig zodat elke fase in één keer correct uitgevoerd kan worden.

### 2.4 Bilingual Overhead

Het maken van NL én EN versies **verdubbelt** de tijd maar vergroot het bereik aanzienlijk.

---

## 3. Claude/AI Workflow Lessen

### 3.1 Memory Gebruik

Claude's memory feature is essentieel voor project continuïteit.

### 3.2 Filesystem Reset

**Kritiek**: Het Claude filesystem reset tussen sessies!

### 3.3 Conversation Length Management

Complexe fases kunnen het gesprekslimiet bereiken.

### 3.4 Token Opslaan

GitHub tokens worden NIET onthouden tussen sessies. Sla op in `api-tokens.md`.

---

## 4. Skill Development Lessen

### 4.1 Anthropic Conventies

| Component | Vereiste |
|-----------|----------|
| SKILL.md | <500 regels, lean |
| Frontmatter | Correct YAML |
| References/ | Detail docs apart |
| Decision trees | In SKILL.md |

### 4.2 Deterministische Content

```markdown
# ❌ FOUT - Te vaag
"Je kunt overwegen om X te gebruiken..."

# ✅ CORRECT - Deterministisch
"ALTIJD X gebruiken wanneer Y"
```

### 4.3 Versie-Expliciet

**ALTIJD** documenteren voor welke versie code bedoeld is.

---

## 5. GitHub Integratie Lessen

### 5.1 Token Setup

Fine-grained PAT met Contents (R/W), Metadata (R), Issues (R/W).

### 5.2 Claude Project Settings

Network: "Package managers only" + `api.github.com`, `github.com` in allowed domains.

**KRITIEK**: Domain toevoegingen werken pas in een NIEUW gesprek!

### 5.3 Git Clone Beperking

`git clone` werkt NIET - gebruik GitHub API voor alle operaties.

### 5.4 Push Na Elke Fase

**Regel**: Werk dat niet gecommit is, bestaat niet.

---

## 6. Valkuilen en Oplossingen

| Valkuil | Oplossing |
|---------|-----------|
| Aannemen zonder verifiëren | Altijd web search, check source code |
| Te grote fases | Monitor criteria, split proactief |
| Geen GitHub sync | Push na ELKE fase |
| Token vergeten | Token in project knowledge |
| Domains niet werkend | Nieuw gesprek starten |

---

## 7. Best Practices Samenvatting

### Research
1. ✅ Start met officiële documentatie
2. ✅ Verifieer tegen GitHub source code
3. ✅ Alleen community input van 2023+

### Skill Development
1. ✅ SKILL.md <500 regels
2. ✅ Deterministische formulering
3. ✅ Decision trees voor complexe keuzes

### Version Control
1. ✅ Push na ELKE fase
2. ✅ Beschrijvende commit messages
3. ✅ Verifieer push succesvol

---

## 8. META-LESSEN: Project Structuur & Planning

> **Toegevoegd**: 17 januari 2026 (Mid-Project Review)
> 
> Deze sectie bevat de belangrijkste lessen over HOE je een skill package project moet opzetten - niet de technische inhoud, maar de project structuur en planning zelf.

### 8.1 DEFINIEER DIRECTORY STRUCTUUR VOORAF

**Wat ging fout:**
We begonnen zonder expliciete directory conventies. Het masterplan beschreef WÁT we gingen maken, maar niet WAAR het moest komen. Resultaat na 61% voortgang:

```
❌ Chaotische structuur die organisch groeide:
skills/
├── packaged/          ← sommige .skill files
├── syntax/            ← andere .skill files  
├── source/            ← sommige bronbestanden
├── impl/              ← weer andere .skill files
├── NL/CORE/           ← core skills NL
├── EN/CORE/           ← core skills EN
├── erpnext-syntax-jinja/     ← losse folder
├── erpnext-syntax-customapp/ ← losse folder
└── erpnext-permissions/      ← nog een losse folder
```

**Wat we hadden moeten doen:**

```
✅ Definieer VOORAF in het masterplan:

skills/
├── source/                    # ALLE bronbestanden
│   ├── syntax/
│   │   └── [skill-naam]/
│   │       ├── NL/
│   │       │   ├── SKILL.md
│   │       │   └── references/
│   │       └── EN/
│   ├── core/
│   ├── impl/
│   ├── errors/
│   └── agents/
│
└── packaged/                  # ALLE .skill packages
    ├── syntax/
    ├── core/
    ├── impl/
    ├── errors/
    └── agents/
```

**Les**: Neem een sectie "Directory Conventies" op in elk masterplan met:
- Exacte paden voor elk bestandstype
- Naming conventions (lowercase, hyphens, taal suffix)
- Voorbeelden van complete paden

---

### 8.2 SPECIFICEER DELIVERABLES PER FASE

**Wat ging fout:**
Het masterplan zei "maak skill X" maar specificeerde niet:
- Moeten we source files pushen?
- Moeten we .skill packages pushen?
- Beide?
- Waar precies?

**Wat we hadden moeten doen:**

```
┌─────────────────────────────────────────────────────────────────────┐
│ DELIVERABLES TEMPLATE - Opnemen in masterplan                      │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│ Per voltooide skill worden ALTIJD gepusht:                         │
│                                                                     │
│ 1. SOURCE FILES                                                    │
│    skills/source/[categorie]/[skill]/NL/SKILL.md                   │
│    skills/source/[categorie]/[skill]/NL/references/*.md            │
│    skills/source/[categorie]/[skill]/EN/SKILL.md                   │
│    skills/source/[categorie]/[skill]/EN/references/*.md            │
│                                                                     │
│ 2. PACKAGES                                                        │
│    skills/packaged/[categorie]/[skill]-NL.skill                    │
│    skills/packaged/[categorie]/[skill]-EN.skill                    │
│                                                                     │
│ 3. STATUS UPDATE                                                   │
│    ROADMAP.md (nieuwe status)                                       │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
```

**Les**: Elk masterplan moet een "Deliverables Checklist" bevatten die EXACT specificeert wat er gepusht moet worden per fase-type.

---

### 8.3 BOUW CHECKPOINTS IN VANAF HET BEGIN

**Wat ging fout:**
We hadden geen formele tussentijdse evaluatiemomenten gepland. We werkten fase na fase zonder te stoppen om te evalueren:
- Is de structuur nog logisch?
- Zijn er patronen die we kunnen verbeteren?
- Moeten we het plan aanpassen?

**Wat we hadden moeten doen:**

```
MASTERPLAN CHECKPOINT SCHEMA

Fase 1-2 (Syntax Skills)
    ↓
┌───────────────────────────────┐
│ CHECKPOINT A                  │
│ - Structuur evaluatie         │
│ - Zijn conventies werkbaar?   │
│ - Lessons learned update      │
└───────────────────────────────┘
    ↓
Fase 3 (Core Skills)
    ↓
┌───────────────────────────────┐
│ CHECKPOINT B                  │
│ - Quality check               │
│ - Cross-references correct?   │
└───────────────────────────────┘
    ↓
Fase 4-5 (Impl + Error Skills)
    ↓
┌───────────────────────────────┐
│ CHECKPOINT C (MID-PROJECT)    │
│ - Volledige review            │
│ - Directory cleanup indien    │
│   nodig                       │
│ - Plan aanpassen              │
└───────────────────────────────┘
    ↓
Fase 6-7 (Agents + Finalisatie)
    ↓
┌───────────────────────────────┐
│ FINAL REVIEW                  │
└───────────────────────────────┘
```

**Les**: Plan checkpoints VOORAF in het masterplan, niet achteraf wanneer problemen al zijn ontstaan.

---

### 8.4 HOUD ÉÉN SINGLE SOURCE OF TRUTH

**Wat ging fout:**
We hadden meerdere documenten die status bijhielden:
- ROADMAP.md (actuele status)
- Masterplan (oorspronkelijke planning)
- 8 verschillende amendments
- WAY_OF_WORK.md (methodologie)

Soms was onduidelijk welk document "de waarheid" was.

**Wat we hadden moeten doen:**

```
DOCUMENT HIËRARCHIE - Definieer vooraf

┌─────────────────────────────────────────────────────────────────────┐
│ SINGLE SOURCE OF TRUTH: ROADMAP.md                                 │
│ - Bevat: Actuele status, voortgang, wat is voltooid                │
│ - Update: Na ELKE fase                                              │
│ - Dit is altijd de meest actuele informatie                        │
└─────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────┐
│ REFERENTIE: Masterplan                                             │
│ - Bevat: Oorspronkelijke visie, fase definities, prompts           │
│ - Update: Alleen bij fundamentele wijzigingen                      │
│ - Blijft stabiel als referentiepunt                                │
└─────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────┐
│ WIJZIGINGEN: Amendments (genummerd)                                │
│ - Bevat: Specifieke aanpassingen op masterplan                     │
│ - Update: Wanneer plan wijzigt                                      │
│ - Altijd met rationale en datum                                     │
└─────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────┐
│ KENNIS: LESSONS_LEARNED.md                                         │
│ - Bevat: Technische en proces inzichten                            │
│ - Update: Na nieuwe ontdekkingen                                    │
│ - Bruikbaar voor toekomstige projecten                             │
└─────────────────────────────────────────────────────────────────────┘
```

**Les**: Definieer vooraf welk document waarvoor dient en wat de "single source of truth" is voor projectstatus.

---

### 8.5 CONSOLIDEER AMENDMENTS PERIODIEK

**Wat ging fout:**
We maakten 8 losse amendments:
- masterplan-aanpassing-fase-2_6.md
- masterplan-aanpassing-fase-2_7.md
- masterplan-aanpassing-fase-2_9.md
- masterplan-aanpassing-fase-2_10-2_11.md
- masterplan-aanvulling-fase-opsplitsingen.md
- masterplan-skill-uploads.md
- skill-uploads-voortgang.md
- skill-uploads-voortgang-updated.md

Dit maakt het moeilijk om het complete, actuele plan te reconstrueren.

**Wat we hadden moeten doen:**

```
AMENDMENT CONSOLIDATIE REGEL

Na elke 3-5 amendments OF bij een checkpoint:
→ Consolideer alle actieve amendments in één "Amendment Summary"
→ Archiveer oude amendments naar amendments/archive/
→ Houd alleen actuele, geconsolideerde versie actief

Voorbeeld:
amendments/
├── archive/
│   ├── amendment-1-fase-2_6.md
│   ├── amendment-2-fase-2_7.md
│   └── ...
├── CONSOLIDATED-AMENDMENTS-v2.md  ← Actuele geconsolideerde versie
└── amendment-6-nieuwste.md        ← Meest recente, nog niet geconsolideerd
```

**Les**: Plan periodieke consolidatie van amendments om overzicht te behouden.

---

### 8.6 NEEM "CONTEXT OPHALEN" OP IN ELKE PROMPT

**Wat ging fout:**
Fase prompts in het masterplan begonnen direct met de taak, zonder expliciet te zeggen:
1. Haal eerst de actuele status op
2. Controleer of vorige fase compleet is
3. Haal benodigde bronnen op

Dit leidde soms tot werk dat niet goed aansloot op de vorige fase.

**Wat we hadden moeten doen:**

```
┌─────────────────────────────────────────────────────────────────────┐
│ STANDAARD PROMPT STRUCTUUR                                         │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│ ═══════════════════════════════════════════════════════════════════│
│ STAP 0: CONTEXT OPHALEN (VERPLICHT - ALTIJD EERSTE)                │
│ ═══════════════════════════════════════════════════════════════════│
│                                                                     │
│ 1. Haal ROADMAP.md op → Check huidige status                       │
│ 2. Bevestig dat vorige fase COMPLEET is                            │
│ 3. Haal benodigde bronnen op (research docs, skills)               │
│ 4. Bevestig directory conventies                                    │
│                                                                     │
│ PAS DAARNA:                                                        │
│                                                                     │
│ ═══════════════════════════════════════════════════════════════════│
│ STAP 1: ONDERZOEK                                                  │
│ ═══════════════════════════════════════════════════════════════════│
│ [fase-specifieke instructies]                                       │
│                                                                     │
│ ═══════════════════════════════════════════════════════════════════│
│ STAP 2: UITWERKING                                                 │
│ ═══════════════════════════════════════════════════════════════════│
│ [fase-specifieke instructies]                                       │
│                                                                     │
│ ═══════════════════════════════════════════════════════════════════│
│ STAP 3: PUSH & VERIFICATIE (VERPLICHT - ALTIJD LAATSTE)            │
│ ═══════════════════════════════════════════════════════════════════│
│ 1. Push alle deliverables naar correcte locaties                   │
│ 2. Update ROADMAP.md                                                │
│ 3. Verifieer push succesvol                                         │
│ 4. Rapporteer aan gebruiker                                         │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
```

**Les**: Elke fase-prompt moet beginnen met "STAP 0: Context Ophalen" en eindigen met "STAP N: Push & Verificatie".

---

### 8.7 TEST DE WORKFLOW VOOR JE BEGINT

**Wat ging fout:**
We ontdekten pas tijdens het project dat:
- `git clone` niet werkt in Claude's container
- Domain toevoegingen pas werken in een nieuw gesprek
- Het filesystem reset tussen sessies

Dit kostte tijd om op te lossen.

**Wat we hadden moeten doen:**

```
PRE-PROJECT CHECKLIST - Voordat je aan een skill package begint

□ GitHub API workflow testen
  - Token configureren
  - Test push/pull via API
  - Documenteer exacte commando's

□ Claude container limitaties identificeren
  - Welke tools werken?
  - Welke niet?
  - Workarounds documenteren

□ Project settings configureren
  - Network settings
  - Allowed domains
  - Test in NIEUW gesprek

□ Directory structuur aanmaken
  - Maak lege structuur aan
  - Push naar GitHub
  - Bevestig dat structuur klopt

□ Eerste fase als pilot
  - Eén skill volledig doorlopen
  - Alle stappen testen
  - Workflow documenteren
  - Pas masterplan aan indien nodig
```

**Les**: Doe een "pilot fase" waarin je de hele workflow test voordat je het volledige project plant.

---

### 8.8 SAMENVATTING: WAT WE ANDERS ZOUDEN DOEN

Als we dit project opnieuw zouden beginnen:

| Aspect | Wat we deden | Wat we zouden doen |
|--------|--------------|-------------------|
| **Directory structuur** | Niet vooraf gedefinieerd | Exact pad per bestandstype in masterplan |
| **Deliverables** | Impliciet | Expliciete checklist per fase-type |
| **Checkpoints** | Geen | Ingebouwd na elke hoofdfase |
| **Source of truth** | Meerdere documenten | ROADMAP.md als single source |
| **Amendments** | 8 losse bestanden | Periodiek consolideren |
| **Prompts** | Direct naar taak | Altijd beginnen met context ophalen |
| **Workflow** | Ontdekken tijdens project | Pilot fase vooraf |

---

### 8.9 TEMPLATE: MASTERPLAN SECTIE "PROJECT CONVENTIES"

Voeg deze sectie toe aan elk toekomstig masterplan:

```markdown
## Project Conventies

### Directory Structuur
[Exacte structuur met voorbeeldpaden]

### Naming Conventions
- Skill namen: lowercase-met-hyphens
- Taal suffix: -NL of -EN (hoofdletters)
- Packages: skill-naam-TAAL.skill

### Deliverables Per Fase Type
| Fase Type | Source Files | Packages | Status Update |
|-----------|--------------|----------|---------------|
| Research  | docs/research/research-[topic].md | - | ROADMAP.md |
| Syntax    | skills/source/syntax/[skill]/[taal]/ | skills/packaged/syntax/ | ROADMAP.md |
| Impl      | skills/source/impl/[skill]/[taal]/ | skills/packaged/impl/ | ROADMAP.md |
| Error     | skills/source/errors/[skill]/[taal]/ | skills/packaged/errors/ | ROADMAP.md |
| Agent     | skills/source/agents/[agent]/[taal]/ | skills/packaged/agents/ | ROADMAP.md |

### Checkpoints
- Na Fase X: [beschrijving]
- Na Fase Y: [beschrijving]
- Mid-Project: [beschrijving]
- Final: [beschrijving]

### Document Hiërarchie
- ROADMAP.md: Single source of truth voor status
- Masterplan: Oorspronkelijke visie (stabiel)
- Amendments: Wijzigingen (genummerd, periodiek consolideren)
- LESSONS_LEARNED.md: Inzichten voor toekomstige projecten
```

---

## Appendix: Quick Reference Cards

### A. Server Script Sandbox Cheat Sheet

```
✅ BESCHIKBAAR                    ❌ NIET BESCHIKBAAR
─────────────────────────────────────────────────────
frappe.db.*                      import statements
frappe.utils.*                   open() / file access
frappe.get_doc()                 os / subprocess
frappe.new_doc()                 eval() / exec()
frappe.throw()                   requests / http
frappe.msgprint()                External libraries
frappe.parse_json()              __import__
frappe.session.user              compile()
```

### B. Fase Opsplitsing Decision Tree

```
Research document >700 regels?
├── Ja → SPLIT
└── Nee → Reference files >5?
          ├── Ja → SPLIT
          └── Nee → Secties >8-10?
                    ├── Ja → SPLIT
                    └── Nee → Doorgaan met fase
```

### C. GitHub Push Checklist

```
□ Alle bestanden gevalideerd
□ NL én EN versies aanwezig (indien van toepassing)
□ Commit message: "Fase X.Y: [beschrijving]"
□ Push naar main branch
□ Verifieer in GitHub web interface
```

### D. Nieuwe Sessie Checklist

```
□ GitHub token uit api-tokens.md
□ export GITHUB_TOKEN="..."
□ Test: curl met token naar api.github.com
□ Indien domains gewijzigd: nieuw gesprek nodig
```

### E. Masterplan Conventies Checklist (NIEUW)

```
□ Directory structuur gedefinieerd met exacte paden
□ Deliverables per fase-type gespecificeerd
□ Checkpoints ingepland na elke hoofdfase
□ Single source of truth aangewezen (ROADMAP.md)
□ Amendment consolidatie schema
□ Alle prompts beginnen met "STAP 0: Context Ophalen"
□ Pilot fase gepland om workflow te testen
```

---

*Dit document is een levend document en wordt bijgewerkt naarmate het project vordert.*

*Laatst bijgewerkt: 17 januari 2026 - Mid-Project Review toegevoegd (Sectie 8)*

---

## 8. Project Structuur Lessen (Mid-Project Review)

> **Context**: Deze lessen komen uit een mid-project review na ~61% voltooiing. Ze zijn bijzonder waardevol omdat ze problemen identificeren die we TIJDENS het project ontdekten - en hoe je ze kunt voorkomen.

### 8.1 Directory Structuur Vooraf Definiëren

**Wat ging fout:**
We begonnen met bouwen zonder een expliciete directory structuur in het masterplan. Dit resulteerde in organische groei:

```
# Wat we kregen (chaos):
skills/
├── packaged/          ← sommige .skill files
├── syntax/            ← andere .skill files  
├── source/            ← sommige bronbestanden
├── NL/CORE/           ← core skills hier
├── erpnext-syntax-jinja/     ← losse folder
└── erpnext-permissions/      ← nog een losse folder

# Wat we hadden moeten definiëren:
skills/
├── source/[categorie]/[skill]/[taal]/
└── packaged/[categorie]/[skill]-[TAAL].skill
```

**Les voor de toekomst:**

```
┌─────────────────────────────────────────────────────────────────────┐
│ REGEL: Definieer EXACTE directory structuur in masterplan          │
│        VOORDAT je begint met bouwen.                                │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│ Specificeer voor ELKE deliverable:                                  │
│ • Exact pad waar het bestand moet komen                            │
│ • Naming convention (lowercase, hyphens, taal suffix)              │
│ • Relatie tussen source files en packages                          │
│                                                                     │
│ Voorbeeld in masterplan:                                            │
│                                                                     │
│ "Syntax skill 'clientscripts' wordt opgeslagen als:                │
│  - Source: skills/source/syntax/erpnext-syntax-clientscripts/NL/   │
│  - Package: skills/packaged/syntax/erpnext-syntax-clientscripts-NL.skill" │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
```

### 8.2 Tussentijdse Evaluatie Checkpoints Inplannen

**Wat ging fout:**
Het masterplan had geen formele evaluatiemomenten. We gingen "gewoon door" van fase naar fase zonder te stoppen om te reflecteren. Problemen stapelden zich op.

**Les voor de toekomst:**

```
┌─────────────────────────────────────────────────────────────────────┐
│ REGEL: Plan VERPLICHTE checkpoints na elke hoofdfase               │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│ Checkpoint template (5-10 minuten):                                │
│                                                                     │
│ 1. VERIFICATIE                                                     │
│    □ Alle deliverables aanwezig?                                   │
│    □ Alles gepusht naar version control?                           │
│    □ Status tracking bijgewerkt?                                   │
│                                                                     │
│ 2. KWALITEITSCHECK                                                 │
│    □ Steekproef 1-2 deliverables op kwaliteit                      │
│    □ Voldoet aan conventies?                                       │
│                                                                     │
│ 3. LESSONS LEARNED                                                 │
│    □ Nieuwe inzichten documenteren                                 │
│    □ Proces verbeteringen nodig?                                   │
│                                                                     │
│ 4. GO/NO-GO                                                        │
│    □ Issues gevonden → FIX voordat we doorgaan                     │
│    □ Alles OK → Volgende fase                                      │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
```

**Aanbevolen checkpoint momenten:**
- Na elke hoofdfase (niet sub-fase)
- Halverwege het project (mid-project review)
- Voor de laatste fase (pre-final review)

### 8.3 Single Source of Truth voor Status

**Wat ging fout:**
We hadden meerdere documenten die status bijhielden:
- ROADMAP.md (actuele status)
- Masterplan (oorspronkelijke planning)
- Amendments (wijzigingen)
- Commit messages (impliciete status)

Dit leidde tot verwarring over "waar staan we nu eigenlijk?"

**Les voor de toekomst:**

```
┌─────────────────────────────────────────────────────────────────────┐
│ REGEL: Eén document is de SINGLE SOURCE OF TRUTH voor status       │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│ Duidelijke scheiding:                                               │
│                                                                     │
│ ROADMAP.md (of STATUS.md)                                          │
│ └── SINGLE SOURCE voor huidige status                              │
│     • Wat is voltooid                                               │
│     • Wat is in progress                                            │
│     • Wat is gepland                                                │
│     • Changelog met datums                                          │
│                                                                     │
│ MASTERPLAN.md                                                       │
│ └── Oorspronkelijke visie en planning                              │
│     • Wordt NIET bijgewerkt voor status                            │
│     • Blijft als referentie voor oorspronkelijke intentie          │
│                                                                     │
│ AMENDMENTS/                                                         │
│ └── Wijzigingen aan het plan                                       │
│     • Nieuwe fases, structuurwijzigingen                           │
│     • Verwijst naar ROADMAP voor status impact                     │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
```

### 8.4 Amendments Consolideren

**Wat ging fout:**
We eindigden met 8+ losse amendments, elk voor een specifieke aanpassing. Dit maakte het moeilijk om het "huidige plan" te begrijpen zonder alle documenten te lezen.

**Les voor de toekomst:**

```
┌─────────────────────────────────────────────────────────────────────┐
│ REGEL: Consolideer amendments periodiek                            │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│ Opties:                                                             │
│                                                                     │
│ A. MASTERPLAN VERSIONING                                           │
│    Na 3-5 amendments → Maak masterplan-v3.md                       │
│    Incorporeer alle wijzigingen                                     │
│    Archiveer oude amendments                                        │
│                                                                     │
│ B. CONSOLIDATED AMENDMENTS                                          │
│    Na elke hoofdfase → Merge alle sub-amendments                   │
│    Houd één "current-amendments.md" actueel                        │
│                                                                     │
│ C. LIVING DOCUMENT                                                  │
│    Update masterplan direct (met change tracking)                  │
│    Git history toont wijzigingen                                    │
│                                                                     │
│ Aanbeveling: Optie A voor grote projecten, Optie C voor kleine     │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
```

### 8.5 Fase Prompts Moeten Context Ophalen Bevatten

**Wat ging fout:**
Onze fase prompts begonnen direct met "doe X". Ze specificeerden niet dat Claude eerst de huidige status en relevante documenten moest ophalen. Dit leidde tot:
- Soms verkeerde aannames over wat al gedaan was
- Gemiste context uit eerdere fases
- Inconsistenties tussen fases

**Les voor de toekomst:**

```
┌─────────────────────────────────────────────────────────────────────┐
│ REGEL: Elke fase prompt begint met STAP 0: CONTEXT OPHALEN         │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│ STAP 0: CONTEXT OPHALEN (VERPLICHT)                                │
│ ═══════════════════════════════════                                │
│                                                                     │
│ Voordat je begint met deze fase:                                    │
│                                                                     │
│ 1. Haal ROADMAP.md op                                              │
│    → Bevestig vorige fase is COMPLEET                              │
│    → Check huidige status                                           │
│                                                                     │
│ 2. Haal relevante bronnen op                                       │
│    → Research documenten                                            │
│    → Eerdere skills indien nodig                                    │
│                                                                     │
│ 3. Bevestig directory structuur                                     │
│    → Waar moeten outputs komen?                                     │
│    → Welke naming conventions?                                      │
│                                                                     │
│ PAS DAARNA: Start met de eigenlijke fase                           │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
```

### 8.6 Source en Package Relatie Expliciet Maken

**Wat ging fout:**
Het masterplan specificeerde niet of we:
- Alleen source files moesten bewaren
- Alleen packages moesten bewaren
- Beide moesten bewaren (en zo ja, waar)

Dit leidde tot inconsistente opslag.

**Les voor de toekomst:**

```
┌─────────────────────────────────────────────────────────────────────┐
│ REGEL: Specificeer source/package strategie in masterplan          │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│ Opties:                                                             │
│                                                                     │
│ A. ALLEEN SOURCE (aanbevolen voor development)                     │
│    skills/source/                                                   │
│    • SKILL.md en references/ worden gepusht                        │
│    • .skill packages worden ON DEMAND gegenereerd                  │
│    • Minder dubbel werk                                             │
│                                                                     │
│ B. ALLEEN PACKAGES (aanbevolen voor distribution)                  │
│    skills/packaged/                                                 │
│    • Alleen .skill files worden gepusht                            │
│    • Source files zijn "build artifacts"                           │
│    • Moeilijker te reviewen/bewerken                               │
│                                                                     │
│ C. BEIDE (onze uiteindelijke keuze)                                │
│    skills/source/    → Voor development en review                  │
│    skills/packaged/  → Voor distribution                           │
│    • Meer werk, maar meeste flexibiliteit                          │
│    • MOET consistent gehouden worden                               │
│                                                                     │
│ KIES ÉÉN STRATEGIE en documenteer het in het masterplan.           │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
```

---

## 9. AI-Assisted Development Lessen

### 9.1 Claude's Filesystem Reset

**Kritieke les:**
Claude's werkdirectory (`/home/claude`) reset tussen sessies. Alles wat niet gepusht wordt naar externe opslag (GitHub) gaat verloren.

**Implicaties:**
- NOOIT een sessie eindigen zonder te pushen
- Download belangrijke artifacts indien GitHub niet beschikbaar
- Gebruik project knowledge voor essentiële referenties

```
┌─────────────────────────────────────────────────────────────────────┐
│ SESSIE AFSLUITING CHECKLIST                                        │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│ □ Alle nieuwe bestanden gepusht naar GitHub?                       │
│ □ ROADMAP.md bijgewerkt met huidige status?                        │
│ □ Belangrijke artifacts gedownload (indien nodig)?                 │
│ □ Volgende stap gedocumenteerd?                                    │
│                                                                     │
│ ⚠️ NIETS in /home/claude overleeft de sessie!                      │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
```

### 9.2 Memory vs Project Knowledge vs GitHub

**Wanneer wat gebruiken:**

| Storage Type | Persistentie | Gebruik voor |
|--------------|--------------|--------------|
| **Memory** | Tussen sessies | Projectregels, voorkeuren, correcties |
| **Project Knowledge** | Permanent | Referentie docs, tokens, instructies |
| **GitHub** | Permanent | Alle project deliverables |
| **Filesystem** | Alleen sessie | Tijdelijk werk |

**Les:**
Zorg dat ALLE deliverables naar GitHub gaan. Memory en Project Knowledge zijn voor meta-informatie, niet voor de eigenlijke output.

### 9.3 Conversation Length Management

**Probleem:**
Complexe fases kunnen het gesprekslimiet bereiken voordat ze af zijn.

**Preventieve maatregelen:**

```
┌─────────────────────────────────────────────────────────────────────┐
│ FASE COMPLEXITEIT CHECK (vooraf)                                   │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│ Research document > 700 regels?           → SPLIT de fase          │
│ Verwacht > 5 reference files?             → SPLIT de fase          │
│ Verwacht > 10 code voorbeelden?           → SPLIT de fase          │
│ Meerdere sub-onderwerpen > 3?             → Overweeg split         │
│                                                                     │
│ BIJ TWIJFEL: Split. Kleinere fases zijn beter dan incomplete.      │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
```

**Tijdens de fase:**
- Push incrementeel (niet alleen aan het eind)
- Monitor voortgang
- Bij ~70% gesprekscapaciteit: overweeg af te ronden en door te gaan in nieuw gesprek

---

## 10. Masterplan Design Lessen

### 10.1 Wat een Goed Masterplan MOET Bevatten

Gebaseerd op onze ervaring, dit zijn de essentiële secties:

```markdown
# Masterplan Template voor AI Skill Packages

## 1. Visie & Doelen
- Wat bouwen we?
- Voor wie?
- Success criteria?

## 2. Directory Structuur (EXPLICIET!)
- Exacte paden voor ELKE deliverable type
- Naming conventions
- Source vs Package strategie

## 3. Deliverables Index
- Complete lijst van ALLE te maken items
- Gegroepeerd per categorie
- Met verwachte output formaat

## 4. Fase Planning met Prompts
- Elke fase heeft een complete prompt
- Prompts bevatten STAP 0: CONTEXT OPHALEN
- Prompts specificeren exacte output locaties

## 5. Checkpoint Schema
- Wanneer evalueren we?
- Wat checken we?
- Go/No-Go criteria?

## 6. Single Source of Truth Definities
- Welk document bevat status?
- Welk document bevat planning?
- Hoe gaan we om met wijzigingen?

## 7. Kwaliteitscriteria
- Per deliverable type
- Meetbaar en verifieerbaar

## 8. GitHub Workflow
- Wat pushen we wanneer?
- Commit message format?
- Branch strategie?
```

### 10.2 Wat Wij Misten (en Jij Niet Moet Missen)

| Wat we misten | Gevolg | Hoe te voorkomen |
|---------------|--------|------------------|
| Expliciete directory structuur | Chaos in repo | Sectie 2 in masterplan |
| Checkpoint momenten | Problemen stapelden zich op | Sectie 5 in masterplan |
| Source/Package strategie | Inconsistente opslag | Sectie 2 in masterplan |
| Context ophalen in prompts | Soms verkeerde aannames | STAP 0 in elke prompt |
| Single source of truth | Verwarring over status | Sectie 6 in masterplan |

---

## 11. Samenvatting: Top 10 Lessen voor Skill Package Development

1. **Definieer directory structuur VOORAF** - Tot op bestandsniveau
2. **Plan verplichte checkpoints** - Na elke hoofdfase
3. **Eén document is de status truth** - ROADMAP.md, niet meerdere
4. **Elke prompt begint met context ophalen** - STAP 0 is verplicht
5. **Push na ELKE fase** - Claude's filesystem reset
6. **Split grote fases proactief** - Beter te klein dan te groot
7. **Specificeer source/package strategie** - Beiden of één, maar expliciet
8. **Consolideer amendments periodiek** - Voorkom document sprawl
9. **Research eerst, altijd** - Nooit bouwen zonder verificatie
10. **Documenteer lessons learned continu** - Niet alleen aan het eind

---

*Toegevoegd tijdens Mid-Project Review - 17 januari 2026*


---

## 12. Anthropic Tooling Compatibiliteit (Kritieke Ontdekking)

> **Ontdekt tijdens**: Mid-Project Review, sessie 10
> **Impact**: Hoog - Onze skill structuur was niet compatibel met officiële Anthropic tooling

### 12.1 Het Probleem

We ontdekten dat onze meertalige folder structuur **NIET werkt** met Anthropic's officiële `package_skill.py` en `quick_validate.py` scripts.

**Wat Anthropic's tooling verwacht:**
```
skill-name/
├── SKILL.md          ← DIRECT in de skill folder root
└── references/
```

**Wat wij hadden gebouwd:**
```
skill-name/
├── NL/
│   ├── SKILL.md      ← In subfolder = FAALT VALIDATIE
│   └── references/
└── EN/
    ├── SKILL.md
    └── references/
```

**De fout in `package_skill.py` (regel 42-44):**
```python
skill_md = skill_path / "SKILL.md"
if not skill_md.exists():
    print(f"❌ Error: SKILL.md not found in {skill_path}")
```

### 12.2 Waarom Dit Belangrijk Is

1. **Officiële tooling werkt niet** - We kunnen `package_skill.py` niet gebruiken
2. **Validatie faalt** - `quick_validate.py` vindt geen SKILL.md
3. **Niet toekomstbestendig** - Als Anthropic tooling verandert, zijn we niet compatibel
4. **Distributie probleem** - Anderen kunnen onze skills niet standaard packagen

### 12.3 De Juiste Structuur

**Elke taalversie moet een APARTE skill zijn:**

```
skills/source/
├── erpnext-syntax-clientscripts-nl/    ← Aparte skill folder
│   ├── SKILL.md                         ← Direct in root
│   └── references/
│       ├── methods.md
│       ├── events.md
│       └── examples.md
│
├── erpnext-syntax-clientscripts-en/    ← Aparte skill folder
│   ├── SKILL.md                         ← Direct in root
│   └── references/
│       └── ...
```

**Implicaties:**
- 28 skills × 2 talen = **56 aparte skill folders**
- Folder naam = Package naam (automatisch)
- Geen speciale taal-handling nodig

### 12.4 Validatie Regels (uit quick_validate.py)

```
┌─────────────────────────────────────────────────────────────────────┐
│ ANTHROPIC SKILL VALIDATIE REGELS                                   │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│ SKILL.md LOCATIE                                                   │
│ • MOET direct in skill folder root staan                           │
│ • NIET in subfolders                                                │
│                                                                     │
│ FRONTMATTER (YAML)                                                 │
│ • Toegestane keys: name, description, license, metadata,           │
│   compatibility, allowed-tools                                      │
│ • GEEN andere keys toestaan                                         │
│                                                                     │
│ NAME VELD                                                          │
│ • Verplicht                                                         │
│ • kebab-case: alleen a-z, 0-9, en hyphens                          │
│ • Mag niet starten/eindigen met hyphen                             │
│ • Geen dubbele hyphens (--)                                        │
│ • Maximum 64 karakters                                              │
│                                                                     │
│ DESCRIPTION VELD                                                   │
│ • Verplicht                                                         │
│ • Geen angle brackets (< of >)                                     │
│ • Maximum 1024 karakters                                            │
│ • MOET triggers bevatten (wanneer skill activeren)                 │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
```

### 12.5 Wat We Verkeerd Deden

| Fout | Waarom het gebeurde | Hoe voorkomen |
|------|---------------------|---------------|
| Taal subfolders | Leek logisch voor organisatie | Check tooling VOORDAT je structuur kiest |
| Niet getest met officiële tools | Aangenomen dat het zou werken | Test met `quick_validate.py` DIRECT na eerste skill |
| Documentatie niet volledig gelezen | Focus op content, niet tooling | Lees HELE skill-creator SKILL.md inclusief scripts/ |

### 12.6 Les voor de Toekomst

```
┌─────────────────────────────────────────────────────────────────────┐
│ REGEL: Test met officiële tooling VOORDAT je verder bouwt          │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│ Bij het maken van een skill package:                                │
│                                                                     │
│ 1. Maak EERSTE skill                                                │
│ 2. Run quick_validate.py DIRECT                                    │
│ 3. Run package_skill.py DIRECT                                     │
│ 4. VERIFIEER dat .skill bestand correct is                         │
│ 5. PAS DAARNA door naar volgende skills                            │
│                                                                     │
│ Als je dit niet doet, kun je 25+ skills bouwen die allemaal        │
│ herstructurering nodig hebben (zoals ons overkwam).                │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
```

### 12.7 Meertalige Skills - De Juiste Aanpak

Aangezien Anthropic geen standaard heeft voor meertalige skills:

**Conventie: Taal suffix in skill naam**

```
erpnext-syntax-clientscripts-nl    ← Nederlandse versie
erpnext-syntax-clientscripts-en    ← Engelse versie
```

**Voordelen:**
- 100% conform Anthropic tooling
- Duidelijk welke taal
- Standaard packaging werkt
- Geen custom scripts nodig

**Nadelen:**
- Meer folders (56 i.p.v. 28)
- Reference files gedupliceerd
- Meer onderhoud bij updates

**Afweging:** De voordelen van tooling-compatibiliteit wegen zwaarder dan de nadelen van duplicatie. Tooling-compatibiliteit is essentieel voor distributie en toekomstige updates.

---

## 13. Samenvatting: Uitgebreide Top 15 Lessen

Bijgewerkt met nieuwe ontdekkingen:

1. **Definieer directory structuur VOORAF** - Tot op bestandsniveau
2. **Plan verplichte checkpoints** - Na elke hoofdfase
3. **Eén document is de status truth** - ROADMAP.md, niet meerdere
4. **Elke prompt begint met context ophalen** - STAP 0 is verplicht
5. **Push na ELKE fase** - Claude's filesystem reset
6. **Split grote fases proactief** - Beter te klein dan te groot
7. **Specificeer source/package strategie** - Beiden of één, maar expliciet
8. **Consolideer amendments periodiek** - Voorkom document sprawl
9. **Research eerst, altijd** - Nooit bouwen zonder verificatie
10. **Documenteer lessons learned continu** - Niet alleen aan het eind
11. **TEST MET OFFICIËLE TOOLING DIRECT** - Na eerste skill, niet na 25
12. **Lees volledige documentatie** - Inclusief scripts en voorbeelden
13. **Meertalig = aparte skills** - Niet subfolders
14. **Folder naam = package naam** - Kies namen zorgvuldig
15. **Server Script sandbox blokkeert imports** - Gebruik frappe.* namespace

---

*Toegevoegd na Anthropic tooling analyse - 17 januari 2026*


---

## 12. Anthropic Skill Tooling Compatibiliteit

> **Ontdekt tijdens**: Mid-Project Review, Sessie 10
> **Impact**: HOOG - Onze hele directory structuur was incompatibel met officiële tooling

### 12.1 De Kritieke Ontdekking

Wij ontwikkelden een meertalige skill structuur zonder de officiële Anthropic tooling te testen:

```
# WAT WIJ DEDEN (FOUT):
erpnext-syntax-clientscripts/
├── NL/
│   ├── SKILL.md          ← In subfolder
│   └── references/
└── EN/
    ├── SKILL.md
    └── references/

# WAT ANTHROPIC VERWACHT:
erpnext-syntax-clientscripts/
├── SKILL.md              ← DIRECT in root
└── references/
```

**Het probleem**: `package_skill.py` zoekt naar `SKILL.md` direct in de skill folder:

```python
skill_md = skill_path / "SKILL.md"
if not skill_md.exists():
    print(f"❌ Error: SKILL.md not found in {skill_path}")
    return None
```

### 12.2 Wat We Hadden Moeten Doen

```
┌─────────────────────────────────────────────────────────────────────┐
│ REGEL: Test de officiële tooling VOORDAT je een structuur kiest    │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│ Bij het starten van een skill package project:                     │
│                                                                     │
│ 1. LEES de skill-creator SKILL.md volledig                         │
│ 2. BEKIJK de scripts (package_skill.py, quick_validate.py)         │
│ 3. MAAK een test skill met de officiële init_skill.py              │
│ 4. TEST packaging VOORDAT je 10+ skills maakt                      │
│                                                                     │
│ "Measure twice, cut once"                                          │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
```

### 12.3 Meertalige Skills: De Juiste Aanpak

Anthropic documentatie zegt **niets** over meertalige skills. Dit betekent:
- Geen speciale ondersteuning in tooling
- Elke taalversie moet een **aparte skill** zijn

**Correcte structuur voor meertalige skills:**

```
skills/source/syntax/
├── erpnext-syntax-clientscripts-nl/    ← Aparte skill voor NL
│   ├── SKILL.md
│   └── references/
│       ├── methods.md
│       ├── events.md
│       └── examples.md
│
├── erpnext-syntax-clientscripts-en/    ← Aparte skill voor EN
│   ├── SKILL.md
│   └── references/
│       └── ...
│
└── ...
```

**Gevolgen:**
- 28 skills × 2 talen = **56 aparte skill folders**
- Meer folders, maar 100% compatibel met tooling
- `package_skill.py` werkt out-of-the-box
- Skill naam = folder naam (automatisch)

### 12.4 Validatie Regels uit quick_validate.py

| Aspect | Vereiste | Max Length |
|--------|----------|:----------:|
| `name` | kebab-case (a-z, 0-9, hyphens) | 64 chars |
| `description` | String, geen < of > | 1024 chars |
| `compatibility` | Optional string | 500 chars |
| Frontmatter keys | Alleen: name, description, license, metadata, compatibility | - |
| SKILL.md locatie | **DIRECT in skill folder root** | - |

### 12.5 Wat NIET in een Skill Mag (Officieel)

Anthropic is expliciet:

> "Do NOT create extraneous documentation or auxiliary files, including:
> - README.md
> - INSTALLATION_GUIDE.md
> - QUICK_REFERENCE.md
> - CHANGELOG.md"

**Actie**: Verwijder alle README.md bestanden uit skill folders.

### 12.6 De Drie Folder Types in een Skill

| Folder | Doel | Wordt geladen in context? |
|--------|------|:-------------------------:|
| `references/` | Documentatie voor Claude | On-demand |
| `scripts/` | Uitvoerbare code (Python/Bash) | Kan uitgevoerd worden zonder laden |
| `assets/` | Templates, images voor output | Nee - alleen voor output |

**Wij gebruiken alleen `references/`** - dat is correct voor documentatie-skills.

### 12.7 Checklist voor Nieuwe Skill Packages

Voordat je begint met een skill package project:

```
□ Lees skill-creator/SKILL.md volledig
□ Bekijk en begrijp package_skill.py
□ Bekijk en begrijp quick_validate.py
□ Test init_skill.py met een dummy skill
□ Test packaging workflow end-to-end
□ Documenteer afwijkingen van standaard (bijv. meertaligheid)
□ Plan directory structuur die werkt met officiële tooling
```

### 12.8 Impact op Ons Project

| Aspect | Voor deze ontdekking | Na correctie |
|--------|---------------------|--------------|
| Skill folders | 28 (met NL/EN subfolders) | 56 (aparte skills per taal) |
| Tooling compatibel | ❌ Nee | ✅ Ja |
| Handmatig packagen | Ja (eigen zip scripts) | Nee (officiële tooling) |
| Onderhoudbaarheid | Matig | Beter |

---

## 13. Samenvatting Nieuwe Lessen (Sessie 10)

| # | Les | Categorie |
|---|-----|-----------|
| 1 | Test officiële tooling VOORDAT je structuur kiest | Planning |
| 2 | Meertalige skills = aparte skill folders per taal | Structuur |
| 3 | SKILL.md moet DIRECT in skill folder root staan | Structuur |
| 4 | Geen README.md in skill folders | Conventies |
| 5 | Lees package_skill.py en quick_validate.py | Tooling |
| 6 | Description max 1024 chars, name max 64 chars | Validatie |

---

*Toegevoegd na Anthropic Tooling Analyse - 17 januari 2026, Sessie 10*


---

## 14. Engels-Only Skills: De Strategische Beslissing

> **Besloten tijdens**: Mid-Project Review, Sessie 10
> **Impact**: Projectomvang gehalveerd (56 → 28 skills)

### 14.1 De Analyse

We onderzochten Anthropic's eigen skill library:

| Anthropic Skill | Taal | Meertalig? |
|-----------------|------|:----------:|
| docx | Engels | ❌ |
| pdf | Engels | ❌ |
| pptx | Engels | ❌ |
| xlsx | Engels | ❌ |
| frontend-design | Engels | ❌ |
| skill-creator | Engels | ❌ |

**Bevinding**: Anthropic maakt GEEN meertalige skills. Hun documentatie zegt niets over internationalisatie.

### 14.2 Waarom Engels-Only Beter Is

```
┌─────────────────────────────────────────────────────────────────────┐
│ SKILL INSTRUCTIES ZIJN VOOR CLAUDE, NIET VOOR GEBRUIKERS           │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│ Claude kan:                                                         │
│ ✅ Engelse skill-instructies lezen                                 │
│ ✅ Nederlandse/Duitse/Franse vragen begrijpen                      │
│ ✅ In elke taal antwoorden                                         │
│ ✅ Code met comments in elke taal genereren                        │
│                                                                     │
│ Conclusie: De taal van SKILL.md beïnvloedt de output NIET.         │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
```

### 14.3 Voordelen van Engels-Only

| Aspect | Tweetalig (oud) | Engels-only (nieuw) |
|--------|:---------------:|:-------------------:|
| Skill folders | 56 | **28** |
| Onderhoud bij updates | 2× werk | **1× werk** |
| Consistentie | Risico op drift | **Gegarandeerd** |
| Conformiteit Anthropic | Afwijkend | **100%** |
| Reference file duplicatie | Ja | **Nee** |

### 14.4 De Les

```
┌─────────────────────────────────────────────────────────────────────┐
│ REGEL: Volg de impliciete best practices van het platform          │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│ Als het platform (Anthropic) iets NIET doet in hun eigen skills,   │
│ is dat waarschijnlijk een bewuste keuze. Vraag jezelf af:          │
│                                                                     │
│ "Waarom doet Anthropic dit niet in hun eigen implementatie?"       │
│                                                                     │
│ Mogelijke antwoorden:                                               │
│ • Het is niet nodig (zoals meertalige skills)                      │
│ • Het werkt niet goed                                               │
│ • Het voegt geen waarde toe                                         │
│                                                                     │
│ Volg het platform tenzij je een ZEER goede reden hebt om af te     │
│ wijken én bereid bent het extra werk te doen.                      │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
```

### 14.5 Impact op Project

| Metric | Voor | Na | Besparing |
|--------|:----:|:--:|:---------:|
| Totaal skill folders | 56 | 28 | 50% |
| Nog te maken folders | 31 | 15 | 52% |
| Reference files | ~168 | ~84 | 50% |
| Geschatte tijd resterend | ~16 uur | ~8 uur | 50% |

### 14.6 Wat Te Doen Met Bestaande NL Skills

**Besluit**: Nederlandse versies worden NIET gemigreerd, alleen Engelse versies.

De NL content was niet verspild - het hielp bij het ontwikkelen en valideren van de skill structuur. Maar voor de finale versie behouden we alleen Engels.

---

*Toegevoegd na strategische beslissing - 17 januari 2026, Sessie 10*
