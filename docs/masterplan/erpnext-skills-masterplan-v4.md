# ERPNext Skills Package - Masterplan v4

> **Geconsolideerde versie** - Post-release planning met Fase 8  
> **Datum**: 18 januari 2026  
> **Status**: Fase 1-7 COMPLEET | Fase 8 ACTIEF  
> **Vervangt**: masterplan-v3.md

---

## Document Geschiedenis

| Versie | Datum | Wijzigingen |
|--------|-------|-------------|
| v1 | jan 2026 | Initieel masterplan |
| v2 | jan 2026 | Fase opsplitsingen |
| v3 | 18 jan 2026 | Engels-only, V16 compatibility, consolidatie amendments |
| **v4** | **18 jan 2026** | **Fase 8 toegevoegd, kritische reflectie, test strategie** |

### Gerelateerde Documenten

| Document | Doel | Locatie |
|----------|------|---------|
| ROADMAP.md | Single source of truth voor status | `/ROADMAP.md` |
| WAY_OF_WORK.md | Methodologie en workflows | `/WAY_OF_WORK.md` |
| LESSONS.md | Technische en proces lessen | `/LESSONS.md` |
| DEPENDENCIES.md | Skill afhankelijkheden | `/docs/DEPENDENCIES.md` |
| Amendment 5 | Mid-project review | `/docs/masterplan/amendments/archived/` |
| Amendment 6 | Engels-only beslissing | `/docs/masterplan/amendments/archived/` |

---

## Visie & Doelstelling

Een complete, modulaire verzameling van **28 deterministische skills** die Claude instanties in staat stellen om foutloze ERPNext/Frappe code te genereren voor **versies 14, 15 en 16**.

### Kernprincipes

| Principe | Beschrijving | Referentie |
|----------|--------------|------------|
| **Engels-only** | Skills zijn instructies voor Claude, niet voor eindgebruikers | Amendment 6 |
| **Research-first** | Geen skill zonder gedegen onderzoek | WAY_OF_WORK.md §5 |
| **Determinisme** | Alleen geverifieerde feiten, geen aannames | LESSONS.md §7 |
| **Versie-expliciet** | Alle code gemarkeerd met v14/v15/v16 | Masterplan v3 |
| **One-shot kwaliteit** | Direct definitieve kwaliteit | WAY_OF_WORK.md §6 |
| **Test-verified** | Skills getest in daadwerkelijk gebruik | **NIEUW in v4** |

---

## Project Status Overzicht

### Fase 1-7: COMPLEET ✅

| Fase | Beschrijving | Deliverables | Status |
|------|--------------|--------------|:------:|
| 1 | Research | 13 documenten | ✅ |
| 2 | Syntax Skills | 8 skills | ✅ |
| 3 | Core Skills | 3 skills | ✅ |
| 4 | Implementation Skills | 8 skills | ✅ |
| 5 | Error Handling Skills | 7 skills | ✅ |
| 6 | Agents | 2 agents | ✅ |
| 7 | Finalisatie | INDEX, INSTALL, README v1.0 | ✅ |

**28/28 skills structureel compleet.**

### Fase 8: Post-Release Verbeteringen 🔄

| Stap | Focus | Issues | Status |
|------|-------|:------:|:------:|
| 8.1 | Kritische Reflectie & Audit | - | ⏳ |
| 8.2 | V16 Skill Updates | #10, #4 | ⏳ |
| 8.3 | Validatie & Testing | - | ⏳ |
| 8.4 | Agent Skills Standaard | #9 | ⏳ |
| 8.5 | Claude Code Native Format | #5 | ⏳ |
| 8.6 | How-to-use Documentatie | #11 | ⏳ |
| 8.7 | Final Polish & v1.1 Release | #12 | ⏳ |

---

## Kritische Reflectie (Sessie 21)

### Wat hebben we daadwerkelijk gedaan vs. geclaimed?

| Claim | Realiteit | Gap |
|-------|-----------|-----|
| "28 skills compleet" | 28 skills bestaan structureel | ✅ Geen gap |
| "V16 compatible" | 9 skills missen V16 frontmatter | ❌ Issue #10 |
| "Alle skills gevalideerd" | Niet met official tooling | ❌ Actie nodig |
| "Skills werken in Claude" | Nooit systematisch getest | ❌ Actie nodig |
| "Production ready" | Ongetest in echte workflows | ⚠️ Risico |

### Fundamentele Vraag: Wat is "klaar"?

```
┌─────────────────────────────────────────────────────────────────────┐
│ DEFINITIE VAN "COMPLEET"                                            │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│ Level 1: Structureel Compleet                          ✅ BEREIKT   │
│ • Alle 28 skills bestaan                                           │
│ • SKILL.md in elke folder root                                     │
│ • Frontmatter aanwezig                                             │
│                                                                     │
│ Level 2: Inhoudelijk Correct                           ⚠️ DEELS    │
│ • V16 consistent gedocumenteerd                        → Issue #10 │
│ • Geen factual errors                                  → Te testen │
│ • Versie markers overal                                → Te checken│
│                                                                     │
│ Level 3: Technisch Gevalideerd                         ❌ NIET     │
│ • quick_validate.py passed                             → Te doen   │
│ • package_skill.py werkt                               → Te doen   │
│ • .skill files gegenereerd                             → Te doen   │
│                                                                     │
│ Level 4: Functioneel Getest                            ❌ NIET     │
│ • Skills laden in Claude                               → Te doen   │
│ • ERPNext code generatie werkt                         → Te doen   │
│ • Edge cases getest                                    → Te doen   │
│                                                                     │
│ Level 5: Gebruiker Gevalideerd                         ❌ NIET     │
│ • How-to-use documentatie compleet                     → Issue #11 │
│ • Installation guide getest                            → Te doen   │
│ • User feedback verwerkt                               → Toekomst  │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
```

### Geleerde Les: "100% Compleet" ≠ "100% Kwaliteit"

> **Toe te voegen aan LESSONS.md Sectie 12**
>
> Skills kunnen structureel compleet zijn maar functioneel niet getest.
> Het verschil tussen "we hebben het gemaakt" en "het werkt" is cruciaal.
> Altijd expliciet zijn over welk niveau van "compleet" bedoeld wordt.

---

## Open Issues Overzicht

### GitHub Issues

| # | Titel | Prioriteit | Fase 8 Stap |
|---|-------|:----------:|:-----------:|
| #4 | V16 compatibility review | 🟡 | 8.2 |
| #5 | Claude Code native format | 🟡 | 8.5 |
| #9 | Agent Skills standaard review | 🟡 | 8.4 |
| #10 | V16 skill updates (9 skills) | 🔴 | 8.2 |
| #11 | How-to-use documentatie | 🟢 | 8.6 |
| #12 | Masterplan v4 + Fase 8 | 🟡 | 8.7 |

### Interne Actiepunten (geen GitHub issue)

| Actie | Prioriteit | Fase 8 Stap |
|-------|:----------:|:-----------:|
| Validatie met quick_validate.py | 🔴 | 8.3 |
| Validatie met package_skill.py | 🔴 | 8.3 |
| Skills testen in Claude | 🔴 | 8.3 |
| LESSONS updaten | 🟡 | 8.1 |
| Project instructies updaten | 🟡 | 8.7 |

---

## Fase 8: Gedetailleerde Planning

### 8.1 Kritische Reflectie & Audit

**Doel**: Vastleggen wat we geleerd hebben en documentatie actualiseren.

**Deliverables**:
- [ ] LESSONS.md uitbreiden met secties 12-14
- [ ] WAY_OF_WORK.md reviewen op actualiteit
- [ ] Dit masterplan (v4) afronden en pushen

**Nieuwe LESSONS secties**:

```markdown
## Sectie 12: "Compleet" vs "Kwaliteit"
- Structureel compleet ≠ functioneel getest
- Expliciet zijn over niveau van completeness
- Test strategie vanaf begin plannen

## Sectie 13: V16 Compatibility Proces
- V16 kwam halverwege project
- Retrofit is lastiger dan vanaf begin
- Lesson: Versie compatibility vanaf dag 1

## Sectie 14: Test Strategie (Ontbrak!)
- Geen systematische tests uitgevoerd
- Risico: Problemen pas in productie ontdekt
- Aanbeveling: Test suite als onderdeel van skill development
```

**Referenties**:
- LESSONS.md huidige secties 1-11
- WAY_OF_WORK.md fase 7 (validation)
- Sessie 21 reflectie notities

---

### 8.2 V16 Skill Updates

**Doel**: Alle 28 skills volledig V16 compatible maken.

**GitHub Issues**: #10, #4

**Te updaten skills (9)**:

| Skill | Probleem | Actie |
|-------|----------|-------|
| syntax-jinja | Mist Chrome PDF, v16 in frontmatter | Uitgebreide update |
| syntax-scheduler | v16 niet in frontmatter | Frontmatter update |
| syntax-clientscripts | v16 niet in description | Description update |
| syntax-serverscripts | v16 niet in description | Description update |
| syntax-whitelisted | Geen versie info | Frontmatter toevoegen |
| syntax-customapp | v16 niet in frontmatter | Frontmatter update |
| impl-clientscripts | v16 niet in version statement | Version update |
| impl-serverscripts | v16 niet in version statement | Version update |
| frappe-core-api | Geen versie info | Frontmatter toevoegen |

**Workflow per skill**:

```
┌─────────────────────────────────────────────────────────────────────┐
│ V16 UPDATE WORKFLOW                                                 │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│ STAP 1: Research                                                   │
│ • Check of V16 breaking changes heeft voor dit skill type          │
│ • Bronnen: docs.frappe.io, github.com/frappe/frappe                │
│                                                                     │
│ STAP 2: Update Frontmatter                                         │
│ • Voeg v16 toe aan frappe_versions array                           │
│ • Of update description met v14/v15/v16                            │
│                                                                     │
│ STAP 3: Update Content (indien nodig)                              │
│ • Version Differences tabel toevoegen/updaten                      │
│ • V16-specifieke features documenteren                             │
│                                                                     │
│ STAP 4: Valideer                                                   │
│ • Check SKILL.md < 500 regels                                      │
│ • Check frontmatter YAML valid                                     │
│                                                                     │
│ STAP 5: Push                                                       │
│ • Commit: "Fase 8.2: V16 update [skill-name]"                      │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
```

**Speciale aandacht: syntax-jinja**

Dit is de enige skill die V16-specifieke content mist (Chrome PDF rendering).

Te documenteren:
- Chrome-based PDF rendering vs wkhtmltopdf
- CSS verschillen/verbeteringen
- Configuratie opties
- Migration notes voor bestaande templates

**Referenties**:
- V16 Compatibility audit (sessie 21)
- Masterplan v3 "V16 Compatibility Review Checklist"
- docs.frappe.io/framework (v16 sectie)

**Exit criteria**:
- [ ] Alle 9 skills updated
- [ ] Issue #10 gesloten
- [ ] Issue #4 gesloten

---

### 8.3 Validatie & Testing

**Doel**: Technisch valideren dat skills correct zijn en functioneel testen.

**Geen GitHub issue** - Intern ontdekt als gap.

#### 8.3.1 Structurele Validatie

**Tool**: quick_validate.py (Anthropic official)

```bash
# Voor elke skill:
python quick_validate.py skills/source/[category]/[skill-name]

# Verwachte output: "Skill is valid!"
```

**Validatie checklist per skill**:
- [ ] name: kebab-case, max 64 chars
- [ ] description: aanwezig, max 1024 chars, bevat triggers
- [ ] SKILL.md in folder root
- [ ] SKILL.md < 500 regels
- [ ] Geen verboden bestanden (README.md, etc.)

**Deliverable**: Validatie rapport voor alle 28 skills

#### 8.3.2 Package Generatie

**Tool**: package_skill.py (Anthropic official)

```bash
# Voor elke skill:
python package_skill.py skills/source/[cat]/[skill] skills/packaged/

# Resultaat: [skill-name].skill bestand
```

**Deliverable**: 28 .skill bestanden in skills/packaged/

#### 8.3.3 Functionele Testing

**NIEUW** - Dit ontbrak in ons proces!

**Test Strategie**:

```
┌─────────────────────────────────────────────────────────────────────┐
│ FUNCTIONELE TEST WORKFLOW                                           │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│ TEST 1: Skill Loading                                              │
│ • Upload skill naar Claude Project                                  │
│ • Verifieer dat Claude skill herkent                               │
│ • Check trigger activatie                                          │
│                                                                     │
│ TEST 2: Code Generatie                                             │
│ • Vraag Claude om ERPNext code te genereren                        │
│ • Verifieer correcte syntax                                        │
│ • Check versie-specifieke code                                     │
│                                                                     │
│ TEST 3: Edge Cases                                                 │
│ • Server Script zonder imports (kritiek!)                          │
│ • Controller vs Server Script keuze                                │
│ • V16-specifieke features                                          │
│                                                                     │
│ TEST 4: Anti-Pattern Detection                                     │
│ • Vraag om code die anti-patterns zou triggeren                    │
│ • Verifieer dat Claude waarschuwt                                  │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
```

**Minimum test cases per skill type**:

| Skill Type | Test Cases |
|------------|------------|
| Syntax | 3 code generatie requests |
| Implementation | 2 workflow scenarios |
| Error Handling | 2 error scenario's |
| Agents | 1 end-to-end interpretatie/validatie |

**Deliverable**: Test rapport met pass/fail per skill

**Referenties**:
- LESSONS.md §1.1 (Server Script sandbox)
- Amendment 5 (tooling requirements)
- WAY_OF_WORK.md §6 (validation)

**Exit criteria**:
- [ ] Alle 28 skills gevalideerd met quick_validate.py
- [ ] Alle 28 .skill packages gegenereerd
- [ ] Minimum test cases uitgevoerd
- [ ] Test rapport gedocumenteerd

---

### 8.4 Agent Skills Standaard Review

**Doel**: Package valideren tegen officiële Agent Skills standaard.

**GitHub Issue**: #9

**Te onderzoeken**:

| Aspect | Bron | Actie |
|--------|------|-------|
| YAML frontmatter spec | agentskills.io/specification | Valideren |
| Name conventions | agentskills.io | Verifiëren |
| Description limits | agentskills.io | Checken |
| skills-ref library | github.com/agentskills/agentskills | Testen |
| Terminologie "agents" | Anthropic docs | Evalueren |

**Workflow**:

```
┌─────────────────────────────────────────────────────────────────────┐
│ AGENT SKILLS STANDAARD REVIEW                                       │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│ STAP 1: Research agentskills.io                                    │
│ • Specification document lezen                                      │
│ • Verschil met Anthropic conventions identificeren                 │
│                                                                     │
│ STAP 2: Test met skills-ref library                                │
│ • npm install skills-ref (of equivalent)                           │
│ • Valideer onze skills tegen standaard                             │
│                                                                     │
│ STAP 3: Gap Analysis                                               │
│ • Wat voldoet wel/niet?                                            │
│ • Wat is blocking vs nice-to-have?                                 │
│                                                                     │
│ STAP 4: Besluit                                                    │
│ • Compliance prioriteit bepalen                                    │
│ • Updates plannen indien nodig                                     │
│                                                                     │
│ STAP 5: Terminologie Review                                        │
│ • Is "agents/" folder juiste naam?                                 │
│ • Onze "agents" zijn eigenlijk "advanced skills"                   │
│ • Hernoemen naar "orchestrators" of behouden?                      │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
```

**Referenties**:
- https://agentskills.io/specification
- https://github.com/agentskills/agentskills
- https://github.com/anthropics/skills
- Issue #9 beschrijving

**Exit criteria**:
- [ ] Specification document geanalyseerd
- [ ] Validatie met skills-ref uitgevoerd
- [ ] Gap analysis gedocumenteerd
- [ ] Besluit over compliance genomen
- [ ] Issue #9 gesloten of omgezet naar concrete taken

---

### 8.5 Claude Code Native Format

**Doel**: Repository omzetten naar plug-and-play Claude Code project.

**GitHub Issue**: #5

**Te implementeren**:

| Component | Beschrijving | Status |
|-----------|--------------|:------:|
| CLAUDE.md | Project instructies in root | ⏳ |
| .claude/settings.json | Project configuratie | ⏳ |
| .claude/commands/ | Custom commands | ⏳ |
| Skills integratie | Skills beschikbaar voor Claude Code | ⏳ |

**Workflow**:

```
┌─────────────────────────────────────────────────────────────────────┐
│ CLAUDE CODE NATIVE FORMAT                                           │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│ STAP 1: Research                                                   │
│ • docs.anthropic.com/claude-code/ doorlezen                        │
│ • Bestaande Claude Code projects analyseren                        │
│ • Best practices identificeren                                     │
│                                                                     │
│ STAP 2: CLAUDE.md Ontwerpen                                        │
│ • Project context voor Claude                                      │
│ • Beschikbare skills beschrijven                                   │
│ • ERPNext development richtlijnen                                  │
│                                                                     │
│ STAP 3: .claude/ Directory                                         │
│ • settings.json configuratie                                       │
│ • Eventuele custom commands                                        │
│                                                                     │
│ STAP 4: Testen                                                     │
│ • Clone repo in nieuwe omgeving                                    │
│ • Open met Claude Code                                             │
│ • Verifieer dat skills automatisch beschikbaar zijn               │
│                                                                     │
│ STAP 5: Documenteren                                               │
│ • README.md updaten met Claude Code instructies                    │
│ • INSTALL.md aanvullen                                             │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
```

**Referenties**:
- https://docs.anthropic.com/claude-code/
- Issue #5 beschrijving
- Bestaande INSTALL.md

**Exit criteria**:
- [ ] CLAUDE.md aanwezig en getest
- [ ] .claude/ directory ingericht
- [ ] Plug-and-play werkt
- [ ] Issue #5 gesloten

---

### 8.6 How-to-use Documentatie

**Doel**: Gebruikers kunnen skills eenvoudig laden en gebruiken.

**GitHub Issue**: #11

**Te creëren documentatie**:

| Document | Inhoud | Locatie |
|----------|--------|---------|
| USAGE.md | Algemene gebruiksinstructies | `/USAGE.md` |
| claude-code.md | Claude Code specifiek | `/docs/usage/` |
| claude-desktop.md | Desktop app specifiek | `/docs/usage/` |
| claude-web.md | Web interface specifiek | `/docs/usage/` |

**Research per platform**:

```
┌─────────────────────────────────────────────────────────────────────┐
│ PLATFORM RESEARCH                                                   │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│ CLAUDE CODE (CLI)                                                  │
│ • Hoe skills toe te voegen aan project                             │
│ • .claude/ directory structuur                                     │
│ • CLAUDE.md rol                                                    │
│ • Best practices workflow                                          │
│ Bronnen: docs.anthropic.com/claude-code/                           │
│                                                                     │
│ CLAUDE DESKTOP APP                                                 │
│ • Skills toevoegen via UI                                          │
│ • Project configuratie                                             │
│ • Memory integratie                                                │
│ Bronnen: support.claude.com                                        │
│                                                                     │
│ CLAUDE.AI WEB                                                      │
│ • Projects feature                                                 │
│ • Skill uploads                                                    │
│ • Artifacts gebruik                                                │
│ Bronnen: docs.claude.com                                           │
│                                                                     │
│ CLAUDE MOBILE                                                      │
│ • Beschikbaarheid skills                                           │
│ • Beperkingen                                                      │
│ Bronnen: App documentatie                                          │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
```

**Documentatie structuur**:

```markdown
# USAGE.md Template

## Quick Start (< 5 minuten)
1. Download skills
2. Upload naar Claude
3. Start coding

## Platform-Specifieke Guides
- [Claude Code](docs/usage/claude-code.md)
- [Claude Desktop](docs/usage/claude-desktop.md)
- [Claude Web](docs/usage/claude-web.md)

## Welke Skills Wanneer?
Decision tree voor skill selectie

## Troubleshooting
Veelvoorkomende problemen en oplossingen

## Examples
Voorbeeldworkflows
```

**Referenties**:
- https://docs.anthropic.com/claude-code/
- https://support.claude.com/
- https://docs.claude.com/
- Issue #11 beschrijving
- Bestaande INSTALL.md

**Exit criteria**:
- [ ] USAGE.md compleet
- [ ] Platform-specifieke guides compleet
- [ ] README.md quick start geüpdatet
- [ ] Issue #11 gesloten

---

### 8.7 Final Polish & v1.1 Release

**Doel**: Alle losse eindjes afronden en v1.1 releasen.

**GitHub Issue**: #12

**Checklist**:

| Taak | Status |
|------|:------:|
| Alle issues #4, #5, #9, #10, #11 gesloten | ⏳ |
| LESSONS.md compleet met secties 12-14 | ⏳ |
| Project instructies geüpdatet | ⏳ |
| README.md naar v1.1 | ⏳ |
| CHANGELOG.md bijgewerkt | ⏳ |
| ROADMAP.md finaal | ⏳ |
| Issue #12 gesloten | ⏳ |

**Project Instructies Update**:

```
TE REVIEWEN:
□ Status claims verwijderen (ROADMAP is single source)
□ Fase 8 context toevoegen
□ Test workflow toevoegen
□ How-to-use referenties toevoegen
□ Verouderde percentages verwijderen
```

**README.md v1.1 Updates**:

- [ ] Badges actualiseren
- [ ] "Getting Started" verbeteren
- [ ] Link naar USAGE.md
- [ ] Claude Code instructies
- [ ] Test status badge (optional)

**Exit criteria**:
- [ ] Alle Fase 8 stappen compleet
- [ ] Alle GitHub issues gesloten
- [ ] v1.1 tag aangemaakt
- [ ] Release notes gepubliceerd

---

## Fase 8 Volgorde & Dependencies

```
┌─────────────────────────────────────────────────────────────────────┐
│ FASE 8 DEPENDENCY GRAPH                                             │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│ 8.1 Kritische Reflectie ────┐                                      │
│     (LESSONS)       │                                      │
│                             ▼                                      │
│ 8.2 V16 Skill Updates ──────┼──► 8.3 Validatie & Testing          │
│     (#10, #4)               │         (alle skills)                │
│                             │              │                       │
│ 8.4 Agent Skills Standaard ─┘              │                       │
│     (#9)                                   │                       │
│                                            ▼                       │
│ 8.5 Claude Code Format ◄───────────────────┤                       │
│     (#5)                                   │                       │
│                                            │                       │
│ 8.6 How-to-use Docs ◄──────────────────────┘                       │
│     (#11)                                                          │
│                                                                     │
│              ▼                                                      │
│ 8.7 Final Polish & v1.1 ◄── Alle voorgaande stappen               │
│     (#12)                                                          │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
```

**Aanbevolen volgorde**:
1. **8.1** eerst (reflectie vastleggen terwijl vers)
2. **8.2** en **8.4** kunnen parallel
3. **8.3** na 8.2 (V16 updates eerst)
4. **8.5** na 8.3 (gevalideerde skills nodig)
5. **8.6** na 8.5 (Claude Code setup nodig voor docs)
6. **8.7** als laatste (consolidatie)

---

## V16 Compatibility Matrix (Actueel)

### Features per Skill Type

| V16 Feature | Relevante Skills | Status |
|-------------|------------------|:------:|
| `extend_doctype_class` | syntax-hooks, impl-hooks | ✅ |
| Data Masking | frappe-core-permissions | ✅ |
| UUID Naming | syntax-controllers | ✅ |
| Chrome PDF | syntax-jinja, impl-jinja | ⚠️ Alleen impl |
| Scheduler 60s tick | syntax-scheduler, impl-scheduler | ✅ |

### Skills V16 Frontmatter Status

| Skill | V16 in Frontmatter | V16 Content |
|-------|:------------------:|:-----------:|
| syntax-hooks | ✅ | ✅ |
| syntax-controllers | ✅ | ✅ |
| syntax-jinja | ❌ | ❌ |
| syntax-scheduler | ⚠️ | ✅ |
| syntax-clientscripts | ⚠️ | N.v.t. |
| syntax-serverscripts | ⚠️ | N.v.t. |
| syntax-whitelisted | ❌ | N.v.t. |
| syntax-customapp | ❌ | N.v.t. |
| impl-hooks | ✅ | ✅ |
| impl-jinja | ✅ | ✅ |
| impl-controllers | ✅ | N.v.t. |
| impl-whitelisted | ✅ | N.v.t. |
| impl-scheduler | ✅ | N.v.t. |
| impl-customapp | ✅ | N.v.t. |
| impl-clientscripts | ⚠️ | N.v.t. |
| impl-serverscripts | ⚠️ | N.v.t. |
| frappe-core-database | ✅ | N.v.t. |
| frappe-core-permissions | ✅ | ✅ |
| frappe-core-api | ❌ | N.v.t. |
| errors-* (7) | ✅ | N.v.t. |
| agents (2) | N.v.t. | N.v.t. |

**Legenda**: ✅ Aanwezig | ⚠️ Impliciet/Deels | ❌ Ontbreekt | N.v.t. Niet van toepassing

---

## Kritieke Technische Waarschuwingen

> **Ongewijzigd van v3** - Deze blijven cruciaal

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

> Zie: LESSONS.md §1.1

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
    self.status = "Updated"

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

## Skill Creatie Template (V4)

> Uitgebreid met test stap

```
┌─────────────────────────────────────────────────────────────────────┐
│ SKILL DEVELOPMENT WORKFLOW (V4 - Met Testing)                       │
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
│ □ Versie markers (v14/v15/v16) in frontmatter                     │
│ □ V16-specifieke features gedocumenteerd (indien relevant)         │
│ □ Version Differences tabel (indien relevant)                      │
│                                                                     │
│ STAP 3: VALIDATIE                                              NEW │
│ ═══════════════════                                                │
│ □ python quick_validate.py [skill-folder]                          │
│ □ python package_skill.py [skill-folder] skills/packaged/          │
│                                                                     │
│ STAP 4: FUNCTIONELE TEST                                       NEW │
│ ══════════════════════════                                         │
│ □ Skill uploaden naar Claude                                       │
│ □ Trigger activatie verifiëren                                     │
│ □ Code generatie testen (min 2 requests)                          │
│                                                                     │
│ STAP 5: PUSH                                                       │
│ ════════════════                                                   │
│ • skills/source/[categorie]/[skill-name]/                          │
│ • skills/packaged/[skill-name].skill                               │
│ • ROADMAP.md (verplicht!)                                          │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
```

---

## Kwaliteitsgaranties (V4)

### Per Skill

- [ ] SKILL.md < 500 regels
- [ ] Frontmatter met name + description (triggers)
- [ ] V16 in versie specificatie
- [ ] Decision tree of quick reference
- [ ] Minimaal 3 werkende voorbeelden
- [ ] Anti-patterns gedocumenteerd
- [ ] quick_validate.py passed
- [ ] Functioneel getest in Claude **NEW**

### Per Fase

- [ ] Alle skills gepusht naar GitHub
- [ ] Alle .skill packages gegenereerd **NEW**
- [ ] ROADMAP.md bijgewerkt
- [ ] Test rapport beschikbaar **NEW**

### Totaal Project

- [ ] 28 skills structureel compleet
- [ ] 28 skills gevalideerd met tooling
- [ ] 28 .skill packages beschikbaar
- [ ] V16 compatibility volledig
- [ ] Functionele tests uitgevoerd
- [ ] How-to-use documentatie compleet **NEW**
- [ ] Claude Code format beschikbaar **NEW**

---

## Research Bronnen

### Officieel (Prioriteit 1)

| Bron | URL | Voor |
|------|-----|------|
| Frappe Docs | docs.frappe.io | Framework API |
| ERPNext Docs | docs.erpnext.com | ERPNext specifiek |
| Frappe GitHub | github.com/frappe/frappe | Source verificatie |
| Anthropic Docs | docs.anthropic.com | Claude Code |
| Claude Support | support.claude.com | Desktop/Web |
| Agent Skills | agentskills.io | Skills standaard |

### Community (Prioriteit 2, alleen 2024+)

| Bron | URL | Voor |
|------|-----|------|
| Frappe Forum | discuss.frappe.io | Real-world issues |
| GitHub Issues | github.com/frappe/*/issues | Bug reports |

---

## Changelog

| Datum | Versie | Wijzigingen |
|-------|--------|-------------|
| 18 jan 2026 | v4 | Fase 8 toegevoegd, kritische reflectie, test strategie, V16 matrix actueel |
| 18 jan 2026 | v3 | Engels-only, V16 compatibility, consolidatie |
| 17 jan 2026 | v2 | Fase opsplitsingen |
| jan 2026 | v1 | Initieel masterplan |

---

*Laatste update: 18 januari 2026*
*Vervangt: masterplan-v3.md*
*Status: ACTIEF WERKDOCUMENT*
