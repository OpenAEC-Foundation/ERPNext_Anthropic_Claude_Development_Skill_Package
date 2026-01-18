# LESSONS LEARNED - ERPNext Skills Package

> **Project**: ERPNext Anthropic Claude Development Skill Package  
> **Laatste update**: 18 januari 2026  
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

## 9. Session Recovery Protocol

**Geleerd uit**: Meerdere sessie-onderbrekingen door crashes/disconnects.

### Het Probleem

Claude's filesystem reset tussen sessies. Bij een onderbroken sessie:
- Sommige bestanden zijn wel gepusht naar GitHub
- Andere bestanden zijn verloren
- Context over voortgang is weg

### De Oplossing

**Bij elke sessie die een vervolg zou kunnen zijn:**

1. **Scan GitHub state EERST**
   ```bash
   # Check recente commits
   curl -s -H "Authorization: Bearer $GITHUB_TOKEN" \
     ".../commits?per_page=5"
   
   # Check specifieke directories
   curl -s -H "Authorization: Bearer $GITHUB_TOKEN" \
     ".../contents/skills/source/[category]"
   ```

2. **Check ROADMAP.md changelog**
   - Laatste entry datum
   - Laatst voltooide fase/stap
   - Genoemde bestanden

3. **Identificeer onderbrekingspunt**
   - Vergelijk ROADMAP met actual files
   - Wat bestaat wel/niet in repo?

4. **Vraag bevestiging VOORDAT je verdergaat**
   ```
   "Ik zie dat fase X.Y gedeeltelijk voltooid is. 
   De volgende bestanden zijn al gepusht: [lijst]
   De volgende ontbreken: [lijst]
   Zal ik verdergaan vanaf [specifieke stap]?"
   ```

### Preventie

- Push elk bestand direct na creatie
- Update ROADMAP.md na elke significante stap
- Atomic commits (één logische wijziging per commit)

### Key Principle

> "GitHub is de source of truth. ALTIJD repo state scannen voordat je aanneemt dat je opnieuw moet beginnen."

---

## 10. Single Source of Truth voor Project Status

**Geleerd uit**: Verwarring door dubbele tracking in Claude Project Instructies én ROADMAP.md

### Het Probleem

Status tracking op meerdere plekken:
- Claude Project Instructies zeiden "Fase 2.10, 38%"
- ROADMAP.md zei "Fase 4, 46%"
- Welke is correct? → Verwarring en tijdverlies

### De Oplossing

**ROADMAP.md is de ENIGE plek voor status tracking.**

| Document | Bevat | Bevat NIET |
|----------|-------|------------|
| Claude Project Instructies | HOW to work | WHERE we are |
| ROADMAP.md | Current status, progress, changelog | Methodology |
| WAY_OF_WORK.md | Methodology, workflows | Status |

### Implementatie Regels

1. **Nooit status hardcoden in instructies**
   - Instructies verwijzen naar ROADMAP
   - Status is altijd actueel via GitHub

2. **ROADMAP update is VERPLICHT na elke fase**
   - Changelog entry met datum
   - Status tabel updaten
   - "Volgende Stappen" bijwerken

3. **Session start: ROADMAP eerst ophalen**
   - Check laatste changelog entry
   - Bevestig huidige fase
   - Dan pas verdergaan

### Key Principle

> "Als ROADMAP niet bijgewerkt is, weet de volgende sessie niet waar we gebleven zijn."

---

## 11. Top 10 Lessen

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
| 10 | **Scan GitHub EERST bij sessie-hervatting** |

---

## 12. "Compleet" vs "Kwaliteit"

**Geleerd uit**: Fase 7 "PROJECT COMPLEET" → Fase 8 reflectie toonde gaps

### Het Probleem

We verklaarden "100% compleet" terwijl:
- ✅ 28 skills structureel aanwezig
- ❌ 9 skills missen V16 frontmatter
- ❌ Geen systematische validatie met tooling uitgevoerd
- ❌ Geen functionele tests in Claude gedaan
- ❌ Skills nooit daadwerkelijk gebruikt voor code generatie

### De Definitie Matrix

```
┌─────────────────────────────────────────────────────────────────────┐
│ NIVEAU VAN "COMPLEET"                                               │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│ Level 1: Structureel Compleet                                      │
│ • Alle bestanden bestaan                                           │
│ • Correcte directory structuur                                     │
│ • Frontmatter aanwezig                                             │
│ → Dit hadden we ✅                                                  │
│                                                                     │
│ Level 2: Inhoudelijk Correct                                       │
│ • Geen factual errors                                              │
│ • Versie markers consistent                                        │
│ • Alle features gedocumenteerd                                     │
│ → Dit dachten we, maar V16 gaps ⚠️                                 │
│                                                                     │
│ Level 3: Technisch Gevalideerd                                     │
│ • quick_validate.py passed                                         │
│ • package_skill.py succesvol                                       │
│ • .skill bestanden gegenereerd                                     │
│ → Dit niet gedaan ❌                                                │
│                                                                     │
│ Level 4: Functioneel Getest                                        │
│ • Skills laden in Claude                                           │
│ • Triggers activeren correct                                       │
│ • Code generatie werkt                                             │
│ → Dit niet gedaan ❌                                                │
│                                                                     │
│ Level 5: Productie Bewezen                                         │
│ • Echte ERPNext projecten                                          │
│ • User feedback verwerkt                                           │
│ • Edge cases getest                                                │
│ → Toekomst                                                         │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
```

### De Les

> **"We hebben het gemaakt" ≠ "Het werkt"**

Structurele completeness is een milestone, niet de finish line. Zonder validatie en testing is "compleet" een aanname.

### Preventie voor Toekomstige Projecten

1. **Definieer "done" expliciet per fase**
   - Welk niveau van compleet is vereist?
   - Wat zijn de exit criteria?

2. **Bouw validatie in de workflow**
   - Niet als laatste stap
   - Na elke skill, niet na alle skills

3. **Plan functionele tests vanaf begin**
   - Niet "als we tijd hebben"
   - Als onderdeel van de definitie van done

### Key Principle

> "100% structureel compleet kan nog steeds 0% functioneel getest zijn. Wees expliciet over welk niveau je claimt."

---

## 13. V16 Compatibility Mid-Project

**Geleerd uit**: ERPNext V16 release tijdens projectontwikkeling

### De Situatie

- Project gestart met scope: V14 + V15
- ERPNext V16 released tijdens ontwikkeling
- Besluit: V16 alsnog toevoegen aan scope
- Resultaat: Retrofit nodig in reeds "voltooide" skills

### Het Probleem

V16 toevoegen achteraf betekende:
- Opnieuw door alle skills gaan
- Sommige skills al "afgevinkt" in ROADMAP
- Inconsistente V16 coverage (sommige wel, sommige niet)
- 9 skills met ontbrekende V16 vermelding ontdekt in audit

### Retrofit vs Vanaf Begin

| Aspect | Retrofit | Vanaf Begin |
|--------|----------|-------------|
| Tijdsinvestering | Hoog (dubbel werk) | Normaal |
| Consistentie | Risico op gaps | Uniform |
| Motivatie | Laag ("was al klaar") | Hoog (onderdeel van werk) |
| Fouten | Meer kans | Minder kans |

### Wat We Anders Hadden Kunnen Doen

1. **Versie scope lock bij start**
   - Expliciete beslissing: "V14+V15 only, V16 is v2.0"
   - Of: wacht tot V16 stabiel is

2. **Versie-agnostisch ontwerpen**
   - Frontmatter: `frappe_versions: [14, 15, 16+]`
   - Content: "Version Differences" tabel standaard

3. **Monitoring van releases**
   - Frappe release calendar volgen
   - Scope beslissing herzien bij major release

### Key Principle

> "Versie scope wijzigen mid-project is technische schuld. Beter: expliciet scopen of versie-agnostisch ontwerpen."

---

## 14. Test Strategie (Ontbrak!)

**Geleerd uit**: Fase 8 reflectie - skills nooit daadwerkelijk getest

### Wat Ontbrak

Geen enkele skill is:
- ✅ Structureel gevalideerd met `quick_validate.py`
- ✅ Gepackaged met `package_skill.py`
- ❌ Geladen in Claude om te zien of trigger werkt
- ❌ Gebruikt om ERPNext code te genereren
- ❌ Getest op edge cases (bijv. V16-specifieke code)

### Waarom Het Ontbrak

1. **Niet in masterplan**
   - Fase 7 was "Finalisatie" → docs, cleanup
   - Geen "Testing" fase gepland

2. **Aanname van correctheid**
   - "Research was grondig"
   - "Voorbeelden komen uit officiële docs"
   - "Dus het zal wel werken"

3. **Tijd/scope druk**
   - 28 skills is veel
   - Focus op "af krijgen"
   - Testing voelt als "extra"

### Test Strategie voor Skills (Alsnog/Toekomst)

```
┌─────────────────────────────────────────────────────────────────────┐
│ SKILL TEST WORKFLOW                                                 │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│ LEVEL 1: Structurele Validatie (per skill)                         │
│ □ python quick_validate.py [skill-folder]                          │
│ □ Output: "Skill is valid!" of errors                              │
│                                                                     │
│ LEVEL 2: Package Generatie (per skill)                             │
│ □ python package_skill.py [skill-folder] output/                   │
│ □ Output: [skill-name].skill bestand                               │
│                                                                     │
│ LEVEL 3: Loading Test (per skill)                                  │
│ □ Upload skill naar Claude Project                                 │
│ □ Vraag: "Welke skills heb je geladen?"                            │
│ □ Verifieer: skill naam + beschrijving correct                     │
│                                                                     │
│ LEVEL 4: Trigger Test (per skill)                                  │
│ □ Gebruik een trigger phrase uit de description                    │
│ □ Verifieer: Claude activeert skill content                        │
│                                                                     │
│ LEVEL 5: Functionele Test (per skill type)                         │
│ □ Syntax skill: "Genereer een [X] voor ERPNext"                    │
│ □ Impl skill: "Help me [workflow] implementeren"                   │
│ □ Error skill: "Ik krijg deze error: [X]"                          │
│ □ Agent: End-to-end code interpretatie/validatie                   │
│                                                                     │
│ LEVEL 6: Edge Case Test                                            │
│ □ V16-specifieke code request                                      │
│ □ Anti-pattern scenario (moet waarschuwen)                         │
│ □ Ambigue vraag (moet juiste skill kiezen)                         │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
```

### Minimum Viable Testing

Als tijd beperkt is, minimaal:
- **Alle skills**: Level 1 + 2 (tooling validatie)
- **Sample per categorie**: Level 3-5 (1 syntax, 1 impl, 1 error, 1 agent)
- **Kritieke skills**: Level 6 (server-scripts vanwege sandbox issue)

### Key Principle

> "Een skill zonder test is een aanname. Plan testing als onderdeel van development, niet als afterthought."

---

---

## 15. GitHub API Workflow Patterns

**Geleerd uit**: 40+ gesprekken met intensief GitHub API gebruik

### Bewezen Effectieve Patronen

#### SHA Retrieval voor Updates

```bash
# ALTIJD SHA eerst ophalen bij file updates
SHA=$(curl -s -H "Authorization: Bearer $GITHUB_TOKEN" \
  "https://api.github.com/repos/.../contents/path/file.md" \
  | grep '"sha"' | head -1 | cut -d'"' -f4)

# Dan pas update met SHA
curl -X PUT ... -d '{"message":"...","content":"...","sha":"'$SHA'"}'
```

**Waarom**: Zonder SHA krijg je conflict errors bij bestaande bestanden.

#### Base64 Encoding

```bash
# ALTIJD -w 0 gebruiken voor line wrapping te voorkomen
CONTENT=$(base64 -w 0 bestand.md)
```

**Waarom**: Zonder `-w 0` bevat de base64 output newlines die JSON breken.

#### Raw Content Ophalen

```bash
# Voor leesbare content (geen JSON wrapper)
curl -s -H "Authorization: Bearer $GITHUB_TOKEN" \
  -H "Accept: application/vnd.github.raw" \
  "https://api.github.com/.../contents/path"
```

**Waarom**: Geeft direct markdown/text content i.p.v. base64-encoded JSON.

### Batch Operations Strategy

| Scenario | Aanpak |
|----------|--------|
| <5 bestanden | Direct via API per file |
| 5-20 bestanden | Download lokaal → valideer → batch upload |
| >20 bestanden | Download alles → lokale processing → staged commits |

### Key Principle

> "GitHub API is reliable maar stateful. SHA management en encoding zijn de #1 failure points."

---

## 16. YAML Frontmatter Gotchas

**Geleerd uit**: Fase 8.3 validatie - 18 skills hadden parsing issues

### Het Probleem

18 van 28 skills faalden initiële validatie vanwege YAML frontmatter issues:

```yaml
# ❌ FOUT - "Triggers:" wordt geïnterpreteerd als YAML mapping
description: Syntax skill for Client Scripts. Triggers: help with ERPNext

# ✅ CORRECT - Quoted string voorkomt YAML parsing
description: "Syntax skill for Client Scripts. Triggers: help with ERPNext"

# ✅ ALTERNATIEF - Folded scalar voor lange descriptions
description: >
  Syntax skill for Client Scripts. Triggers: help with ERPNext 
  client-side form interactions, validation, and server calls.
```

### YAML Valkuilen Checklist

| Issue | Symptoom | Oplossing |
|-------|----------|-----------|
| Colon in value | `mapping values not allowed` | Quote de hele string |
| Multi-line | Truncated content | Gebruik `>` of `\|` |
| Special chars | Parse errors | Quote + escape |
| Embedded quotes | Nesting errors | Use opposite quote type |

### Key Principle

> "YAML is subtiel. Elke description met ':' of andere special characters MOET gequoted worden."

---

## 17. Context Window Overflow Recovery

**Geleerd uit**: Sessie 22 - mid-sessie overflow na grote validatie operatie

### Recovery Protocol

1. **Scan GitHub state** - Check recente commits en vergelijk met verwachte bestanden
2. **Check ROADMAP.md** - Laatste changelog entry, komt status overeen?
3. **Identificeer gaps** - Welke bestanden zijn verloren?
4. **Communiceer en hervat** - "Status: X gepusht, Y ontbreekt"

### Preventie Tips

- Push incrementeel (na elk bestand)
- Monitor output bij grote operaties
- Checkpoint commits tussentijds
- Max 5-10 files per conversatie-segment

### Key Principle

> "Context overflow is onvermijdelijk bij grote operaties. Plan voor recovery, push vroeg en vaak."

---

## 18. Agent Skills vs Claude Agent SDK

**Geleerd uit**: Fase 7 - ontdekking van agentskills.io standaard

| Aspect | Agent Skills | Claude Agent SDK |
|--------|--------------|------------------|
| Type | Instructie-gebaseerd | Programmatisch |
| Format | YAML + Markdown | Python/TypeScript |
| Doel | Claude capability extension | Autonomous agent building |
| Website | agentskills.io | docs.anthropic.com/sdk |
| Ons package | ✅ Agent Skills | ❌ Niet van toepassing |

### Key Principle

> "Ken het ecosysteem. 'Agent Skills' (instructies voor Claude) ≠ 'Agent SDK' (code om agents te bouwen)."

---

## 19. GitHub Community Standards

**Geleerd uit**: Fase 8.8 planning - gap analyse tegen GitHub best practices

GitHub meet repository "community health" op 7 criteria:

| File | Doel | Ons |
|------|------|:---:|
| README.md | Project overview | ✅ |
| LICENSE | Legal terms | ✅ |
| CODE_OF_CONDUCT.md | Community behavior | ⏳ |
| CONTRIBUTING.md | How to contribute | ⏳ |
| SECURITY.md | Vulnerability reporting | ⏳ |
| Issue templates | Structured bug reports | ⏳ |
| PR template | Structured contributions | ⏳ |

**Score**: 2/7 → 7/7 (Doel na Fase 8.8)

### Key Principle

> "Open source is meer dan code. Community health files zijn essentieel voor professionele repositories."

---

## 20. Skill Validation Workflow Optimization

**Geleerd uit**: Fase 8.3 - batch validatie van 28 skills

### Ontdekte Issues

| Issue Type | Aantal | Root Cause |
|------------|:------:|------------|
| YAML quoting | 18 | Unquoted colons in descriptions |
| Line limit exceeded | 3 | Content niet in references verplaatst |

### Geoptimaliseerde Workflow

1. **Bulk Download** - Alle skills lokaal
2. **Batch Validation** - `quick_validate.py` op alles
3. **Pattern-Based Fixing** - Sed/grep voor bulk fixes
4. **Re-validate** - Tot 0 errors
5. **Batch Upload** - Alles in één sessie

### Key Principle

> "Bulk lokaal verwerken is 3x sneller dan per-file API operaties."

---

## 21. Tool Knowledge Accumulation

**Geleerd uit**: 40+ gesprekken met dezelfde toolset

### Effectieve Tool Combinaties

| Task | Tools | Sequence |
|------|-------|----------|
| File update | bash → view → str_replace → bash | Check → Read → Edit → Verify |
| Multi-file create | create_file (loop) → present_files | Create batch → Present once |
| GitHub push | bash (encode) → bash (PUT) | Encode → Upload |

### Key Principle

> "Tool mastery komt van patronen herkennen. De beste workflows combineren tools in vaste sequences."

---

## Top 22 Lessen (Finale Update)

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
| 10 | **Scan GitHub EERST bij sessie-hervatting** |
| 11 | **"Structureel compleet" ≠ "Functioneel getest"** |
| 12 | **Versie scope wijzigen mid-project = technische schuld** |
| 13 | **Plan testing als onderdeel van development** |
| 14 | **Definieer "done" expliciet met levels** |
| 15 | **GitHub API workflow > proprietary formats** |
| 16 | **SHA management en base64 encoding zijn GitHub API failure points** |
| 17 | **YAML descriptions met ':' MOETEN gequoted worden** |
| 18 | **Plan voor context overflow: push incrementeel** |
| 19 | **Agent Skills ≠ Agent SDK - ken het verschil** |
| 20 | **Community health files essentieel voor open source** |
| 21 | **Bulk lokaal verwerken is 3x sneller dan per-file API** |
| 22 | **Tool mastery = patroonherkenning + vaste sequences** |

---

## Changelog

| Datum | Wijziging |
|-------|-----------|
| 2026-01-18 | Sectie 15-21 toegevoegd: Sessie 24 chat analyse (40+ gesprekken) |
| 2026-01-18 | Top 15 → Top 22 uitgebreid |
| 2026-01-18 | Sectie 12-14 toegevoegd: Post-release reflecties |
| 2026-01-18 | Sectie 10 toegevoegd: Single Source of Truth voor tracking |
| 2026-01-18 | Sectie 9 toegevoegd: Session Recovery Protocol |
| 2026-01-17 | Volledige herschrijving na mid-project review |
| 2026-01-17 | Engels-only beslissing gedocumenteerd |
| 2026-01-17 | Anthropic tooling compatibiliteit toegevoegd |
| 2026-01-17 | Cleanup van duplicaat secties |

---

*Dit document wordt continu bijgewerkt met nieuwe inzichten.*
