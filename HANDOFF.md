# HANDOFF — ERPNext/Frappe ERP Skill Package

> Snelle overdracht voor nieuwe sessies. Lees dit VOOR je begint.

## Status

- **Package versie**: v1.2 (28 skills, feature-complete)
- **CLAUDE.md**: Upgraded naar v2 template (alle protocols P-000a t/m P-010)
- **V2 upgrade**: GEPLAND — van 28 ERPNext-specifieke skills naar 53 Frappe Framework skills
- **CI/CD**: quality.yml workflow toegevoegd

## Wat is er (v1.2)

| Categorie | Aantal | Skills |
|-----------|:------:|--------|
| syntax/ | 8 | clientscripts, controllers, customapp, hooks, jinja, scheduler, serverscripts, whitelisted |
| core/ | 3 | api-patterns, database, permissions |
| impl/ | 8 | clientscripts, controllers, customapp, hooks, jinja, scheduler, serverscripts, whitelisted |
| errors/ | 7 | api, clientscripts, controllers, database, hooks, permissions, serverscripts |
| agents/ | 2 | code-interpreter, code-validator |
| **Totaal** | **28** | |

## Skill Format Compliance (v1.2 vs v2 standaard)

De bestaande 28 skills zijn al GROTENDEELS compliant met de v2 standaard:

| Criterium | Status | Opmerking |
|-----------|:------:|-----------|
| Folded scalar `>` in description | COMPLIANT | Alle 28 skills gebruiken `>` |
| "Use when..." trigger format | COMPLIANT | Alle 28 skills beginnen met "Use when" |
| Keywords in description | COMPLIANT | Alle 28 skills bevatten Keywords |
| English-only content | COMPLIANT | D-001 |
| SKILL.md < 500 lines | COMPLIANT | D-003 |
| references/ directory | COMPLIANT | Alle 28 skills hebben references/ |
| license: MIT in frontmatter | DEELS | Sommige skills gebruiken LGPL-3.0 |
| metadata.author field | ONTBREEKT | Geen metadata block in frontmatter |
| metadata.version field | ONTBREEKT | Geen metadata block in frontmatter |
| compatibility format | AFWIJKEND | Gebruikt oud format zonder "Designed for Claude Code" prefix |

## Wat v2 upgrade betekent

De v2 upgrade bestaat uit twee delen:

### Deel 1: Bestaande skills upgraden
- Rename: `erpnext-*` naar `frappe-*` (28 skills)
- YAML frontmatter aanpassen: license naar MIT, metadata block toevoegen
- Compatibility string updaten naar nieuw format
- Repo rename: `ERPNext_Anthropic_Claude_Development_Skill_Package` naar `Frappe_Claude_Skill_Package`

### Deel 2: Nieuwe skills toevoegen (25 stuks)
- Nieuwe categorieen: ops/ (9), testing/ (2)
- Uitbreiding syntax/ (+2), core/ (+4), impl/ (+5), agents/ (+3)
- Prioriteiten: P0 (5) → P1 (5) → P2 (6) → P3 (7)

### V2 Key Documents
- Tech Spec: `docs/masterplan/frappe-skill-package-tech-spec-v2.md`
- Gap Analysis: `docs/masterplan/frappe-skill-package-gap-analysis.md`

## Governance Files

| Bestand | Aanwezig | Status |
|---------|:--------:|--------|
| CLAUDE.md | JA | Volledig upgraded naar v2 template |
| ROADMAP.md | JA | Uitgebreid met v2 planning |
| WAY_OF_WORK.md | JA | Originele 7-fase methodologie |
| DECISIONS.md | JA | 15+ genummerde beslissingen (D-001 t/m D-015) |
| LESSONS.md | JA | Technische en proces-lessen gedocumenteerd |
| SOURCES.md | JA | Verified Frappe/ERPNext doc URLs |
| REQUIREMENTS.md | JA | Quality criteria gedefinieerd |
| CHANGELOG.md | JA | Keep a Changelog format |
| INDEX.md | JA | Volledige skill catalogus |
| LICENSE.md | JA | Bestaat (controleer of dit MIT is) |
| HANDOFF.md | JA | Dit bestand |
| README.md | JA | GitHub landing page |
| .github/workflows/quality.yml | JA | CI/CD quality workflow |

## Open Ontwerpvragen (voor v2 start)

1. **Repo naam exact**: `Frappe_Claude_Skill_Package` (voorgesteld)
2. **Bestaande skills inhoudelijk updaten?** Alleen rename of ook content herzien?
3. **hooks.py skill splitsen?** 15 hooks nu → 50+ hooks bestaan
4. **Ops skills**: generiek of Hetzner-specifiek?
5. **ERPNext-specifieke module skills later?** (Accounting, HR, Manufacturing)

## Volgende Sessie

1. Lees ROADMAP.md — bepaal of v2 upgrade gestart moet worden
2. Lees de v2 Tech Spec en Gap Analysis
3. Bespreek de open ontwerpvragen met de gebruiker
4. Start met V2.2 (rename operatie) als besluit genomen is
