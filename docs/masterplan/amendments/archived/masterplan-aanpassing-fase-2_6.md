# Masterplan Aanpassing: Opsplitsing Fase 2.6

> **Datum**: 13 januari 2026  
> **Betreft**: Fase 2.6 (Research Custom App) opsplitsen in 2.6.1 en 2.6.2

---

## Reden voor Opsplitsing

De `erpnext-syntax-customapp` skill is de grootste syntax skill in het project:
- **8 reference bestanden** gepland (vs 4-5 voor andere skills)
- **16 secties** in het research document
- Te veel content voor één gesprek/sessie

### Impact op Nummering

| Origineel | Nieuw |
|-----------|-------|
| Stap 2.6: Research Custom App | Stap 2.6.1: Research Custom App - Deel A |
| - | Stap 2.6.2: Research Custom App - Deel B |
| Stap 2.7-2.12: Creëer Skills | Stap 2.7-2.11: Creëer Skills (5 skills) |
| - | Stap 2.12.1: Creëer erpnext-syntax-customapp Deel A |
| - | Stap 2.12.2: Creëer erpnext-syntax-customapp Deel B |

---

## Nieuwe Fase Definities

### Stap 2.6.1: Research Custom App - Basis Structuur

**Focus**: Hoe een Frappe app opzetten en configureren

**Onderzoeksonderwerpen**:
1. APP STRUCTUUR: Vereiste bestanden en directories (bench new-app output)
2. PYPROJECT.TOML / SETUP.PY: Correcte configuratie
3. __INIT__.PY: Vereiste inhoud (__version__)
4. MODULES: modules.txt en module structuur
5. DEPENDENCIES: Hoe dependencies declareren

**Output reference bestanden**:
- `structure.md` - Volledige directory structuur
- `pyproject-toml.md` - pyproject.toml configuratie
- `modules.md` - Module organisatie

---

### Stap 2.6.2: Research Custom App - Data Management

**Focus**: Hoe data beheren over versies en releases

**Onderzoeksonderwerpen**:
6. PATCHES: Migratie scripts schrijven (patches.txt structuur)
7. FIXTURES: Export en import van configuratie data

**Output reference bestanden**:
- `patches.md` - Patch schrijven en structuur
- `fixtures.md` - Fixtures configuratie
- `examples.md` - Complete werkende app voorbeelden
- `anti-patterns.md` - Wat te vermijden

---

## Aangepaste Prompts

### PROMPT FASE 2.6.1 - RESEARCH CUSTOM APP: BASIS STRUCTUUR

```
┌─────────────────────────────────────────────────────────────────────┐
│ PROMPT FASE 2.6.1 - RESEARCH CUSTOM APP: BASIS STRUCTUUR           │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│ STARTPUNT: Lees eerst erpnext-vooronderzoek.md voor context        │
│ over hoe alle scripting mechanismen samenkomen in een custom app.  │
│                                                                     │
│ Onderzoek custom app BASIS structuur (Deel A):                     │
│                                                                     │
│ 1. APP STRUCTUUR: Vereiste bestanden en directories                │
│    - Output van `bench new-app`                                    │
│    - Verplichte vs optionele bestanden                             │
│    - Directory layout conventies                                    │
│                                                                     │
│ 2. PYPROJECT.TOML / SETUP.PY:                                      │
│    - v15 pyproject.toml formaat (primair)                          │
│    - v14 setup.py formaat (legacy)                                 │
│    - Alle configuratie opties                                       │
│                                                                     │
│ 3. __INIT__.PY:                                                    │
│    - Verplichte __version__ variabele                              │
│    - Optionele imports en setup                                     │
│                                                                     │
│ 4. MODULES:                                                         │
│    - modules.txt structuur                                          │
│    - Module directories en bestanden                                │
│    - DocType organisatie binnen modules                            │
│                                                                     │
│ 5. DEPENDENCIES:                                                    │
│    - Frappe/ERPNext versie requirements                            │
│    - Python package dependencies                                    │
│    - app_include_* voor assets                                      │
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
│ Output als gestructureerd research document met bronvermelding.    │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
```

### PROMPT FASE 2.6.2 - RESEARCH CUSTOM APP: DATA MANAGEMENT

```
┌─────────────────────────────────────────────────────────────────────┐
│ PROMPT FASE 2.6.2 - RESEARCH CUSTOM APP: DATA MANAGEMENT           │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│ STARTPUNT: Bouw voort op research uit Fase 2.6.1.                  │
│                                                                     │
│ Onderzoek custom app DATA management (Deel B):                     │
│                                                                     │
│ 1. PATCHES (Migraties):                                            │
│    - patches.txt structuur en syntax                               │
│    - INI-style secties: [pre_model_sync], [post_model_sync]        │
│    - Patch functie implementatie                                    │
│    - Atomic operations en error handling                           │
│    - bench migrate gedrag                                           │
│                                                                     │
│ 2. FIXTURES:                                                        │
│    - hooks.py fixtures configuratie                                │
│    - Export filters syntax                                          │
│    - Sync gedrag bij migrate                                        │
│    - Wanneer fixtures vs patches gebruiken                         │
│                                                                     │
│ 3. COMPLETE VOORBEELDEN:                                            │
│    - Minimale werkende app                                          │
│    - App met custom DocTypes                                        │
│    - App met API endpoints                                          │
│    - App die ERPNext uitbreidt                                      │
│                                                                     │
│ 4. ANTI-PATTERNS:                                                   │
│    - Veelgemaakte fouten                                            │
│    - Wat te vermijden bij patches                                   │
│    - Fixtures valkuilen                                             │
│    - Dependency problemen                                           │
│                                                                     │
│ ─────────────────────────────────────────────────────────────────── │
│ BRONVEREISTEN:                                                      │
│ • Primair: docs.frappe.io/framework (v14/v15 sectie)               │
│ • Secundair: Frappe GitHub source code voor verificatie            │
│ • Alleen community input van 2023+ en bevestigd werkend            │
│ • GEEN verouderde of deprecated patterns opnemen                   │
│ ─────────────────────────────────────────────────────────────────── │
│                                                                     │
│ Output als gestructureerd research document met bronvermelding.    │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
```

---

## Aangepaste Stap 2.7-2.12: Skill Creatie

### Stap 2.7-2.11: Creëer Skills (5 van 6)

Ongewijzigd voor:
- 2.7: erpnext-syntax-controllers
- 2.8: erpnext-syntax-hooks
- 2.9: erpnext-syntax-whitelisted
- 2.10: erpnext-syntax-jinja
- 2.11: erpnext-syntax-scheduler

### Stap 2.12.1: Creëer erpnext-syntax-customapp Deel A

```
┌─────────────────────────────────────────────────────────────────────┐
│ PROMPT FASE 2.12.1 - CREËER SKILL: erpnext-syntax-customapp (A)    │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│ Gebruik research document uit Fase 2.6.1 om het EERSTE DEEL        │
│ van de 'erpnext-syntax-customapp' skill te maken.                  │
│                                                                     │
│ VEREISTEN:                                                          │
│ 1. Volg exact de Anthropic skill-creator richtlijnen               │
│ 2. Maak TWEE versies: NL en EN                                     │
│                                                                     │
│ TE MAKEN REFERENCE BESTANDEN:                                       │
│ references/                                                         │
│ ├── structure.md (directory structuur)                             │
│ ├── pyproject-toml.md (configuratie)                               │
│ └── modules.md (module organisatie)                                │
│                                                                     │
│ SKILL.MD FOCUS:                                                     │
│ - Frontmatter met triggers voor app setup vragen                   │
│ - Quick start: minimale app in 5 stappen                           │
│ - Decision tree: "welke bestanden heb ik nodig?"                   │
│ - Verwijzingen naar reference files                                 │
│                                                                     │
│ LET OP: Dit is Deel A. SKILL.md wordt in Deel B afgerond.          │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
```

### Stap 2.12.2: Creëer erpnext-syntax-customapp Deel B

```
┌─────────────────────────────────────────────────────────────────────┐
│ PROMPT FASE 2.12.2 - CREËER SKILL: erpnext-syntax-customapp (B)    │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│ Gebruik research document uit Fase 2.6.2 om het TWEEDE DEEL        │
│ van de 'erpnext-syntax-customapp' skill te maken.                  │
│                                                                     │
│ VOORWAARDE: Deel A (2.12.1) is compleet.                           │
│                                                                     │
│ TE MAKEN REFERENCE BESTANDEN:                                       │
│ references/                                                         │
│ ├── patches.md (migratie scripts)                                  │
│ ├── fixtures.md (data export/import)                               │
│ ├── examples.md (complete app voorbeelden)                         │
│ └── anti-patterns.md (wat te vermijden)                            │
│                                                                     │
│ SKILL.MD AFRONDING:                                                 │
│ - Voeg patches/fixtures secties toe aan SKILL.md                   │
│ - Voeg complete voorbeelden sectie toe                             │
│ - Finaliseer decision tree                                          │
│ - Valideer totale skill < 500 regels                               │
│                                                                     │
│ PACKAGING:                                                          │
│ - Combineer alle 7 reference bestanden                             │
│ - Valideer met quick_validate.py                                   │
│ - Package NL en EN versies                                          │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
```

---

## Aangepaste Exit Criteria Fase 2

### Origineel:
- [ ] Research documenten voor alle 6 categorieën
- [ ] 6 syntax skills compleet (NL + EN = 12 SKILL.md files)
- [ ] Alle skills gepackaged

### Nieuw:
- [ ] Research documenten voor alle 6 categorieën (7 documenten totaal)
  - Controllers, Hooks, Whitelisted, Jinja, Scheduler
  - Custom App Deel A (structuur)
  - Custom App Deel B (data management)
- [ ] 6 syntax skills compleet (NL + EN = 12 SKILL.md files)
- [ ] Alle skills gepackaged

---

## Samenvatting Wijzigingen

| Item | Was | Wordt |
|------|-----|-------|
| Stap 2.6 | 1 research stap | 2.6.1 + 2.6.2 |
| Stap 2.12 | Onderdeel van 2.7-2.12 | 2.12.1 + 2.12.2 (expliciet) |
| Research docs | 6 | 7 (Custom App gesplitst) |
| Reference files customapp | 8 in één keer | 3 + 5 (gesplitst) |
| Dependencies | Geen | 2.6.2 bouwt voort op 2.6.1 |
| | | 2.12.2 vereist 2.12.1 |

---

## Noot over Dependencies

Hoewel de delen op elkaar voortbouwen, zijn ze **zelfstandig uitvoerbaar**:
- Fase 2.6.2 kan starten zonder 2.6.1 (de onderwerpen zijn onafhankelijk)
- Fase 2.12.2 vereist wel 2.12.1 (skill bestanden moeten samengevoegd worden)

Als alternatief kan 2.12 ook als **twee aparte skills** worden behandeld:
- `erpnext-syntax-customapp-structure`
- `erpnext-syntax-customapp-data`

Dit zou echter afwijken van het oorspronkelijke ontwerp (1 skill per mechanisme).
