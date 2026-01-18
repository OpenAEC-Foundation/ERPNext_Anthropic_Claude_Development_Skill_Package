# Masterplan Aanvulling: Analyse Fase Opsplitsingen

> **Datum**: 13 januari 2026  
> **Betreft**: Systematische analyse van alle resterende fases op basis van criteria uit 2.6 en 2.7 opsplitsingen

---

## Vastgestelde Criteria voor Opsplitsing

Op basis van de opsplitsingen van Fase 2.6 en 2.7 zijn de volgende criteria geÃ¯dentificeerd:

| Criterium | Drempelwaarde | Bron |
|-----------|---------------|------|
| **Reference files** | >4-5 per gesprek = te veel | Fase 2.6 (8 files â†’ 3+5 split) |
| **Secties/onderwerpen** | >8-10 per gesprek = te veel | Fase 2.7 (12 secties â†’ 6+6 split) |
| **Logische scheiding** | Moet conceptueel gescheiden zijn | Beide opsplitsingen |
| **Dependencies** | Minimaal, bij voorkeur geen | Fase 2.6 (delen onafhankelijk) |
| **Gespreksduur** | One-shot per sub-fase | Project principe |

---

## Analyse per Fase

### Fase 2 (Syntax Skills) - REEDS OPGESPLITST

| Stap | Status | Actie |
|------|--------|-------|
| 2.6 (Custom App) | âœ… Opgesplitst | 2.6.1 + 2.6.2 |
| 2.7 (Controllers) | âœ… Opgesplitst | 2.7.1 + 2.7.2 |
| 2.8 (Hooks) | âš ï¸ Nog te analyseren | Zie hieronder |
| 2.9-2.11 | â¸ï¸ Onbekend | Analyseren tijdens uitvoering |

#### Fase 2.8 (Hooks) - Aanbeveling: OPSPLITSEN

Het **research-document-hooks.md** bevat:
- **868 regels** (groter dan controllers met 744 regels)
- **12 secties** (gelijk aan controllers)
- **8 geplande reference files**

**Aanbevolen opsplitsing**:

| Nieuwe Fase | Focus | Secties | Reference Files |
|-------------|-------|---------|-----------------|
| **2.8.1** | Event Hooks | doc_events, scheduler_events, bootinfo | 3 bestanden |
| **2.8.2** | Configuration Hooks | overrides, fixtures, permissions, assets, jinja, andere | 5 bestanden |

---

### Fase 3 (Core Skills) - AANBEVELING: NIET OPSPLITSEN

| Stap | Onderwerpen | Reference Files | Risico |
|------|-------------|-----------------|--------|
| 3.1 Database | 6 | ~3 | Beheersbaar |
| 3.2 Permissions | 6 | ~3 | Beheersbaar |
| 3.3 API Patterns | 6 | ~3 | Beheersbaar |

**Reden**: Elke skill heeft ~6 onderwerpen en ~3 reference files. Dit valt binnen de drempelwaarden.

**MAAR**: Fase 3.1 (Database) is potentieel groot als de research uitgebreider wordt. Aanbeveling: monitor tijdens uitvoering en splits indien nodig.

---

### Fase 4 (Implementation Skills) - AANBEVELING: EXPLICIETE STAPPEN

Het masterplan groepeert 8 skills onder Ã©Ã©n fase met een template. Dit is onduidelijk:
- Worden alle 8 skills in Ã©Ã©n gesprek gemaakt?
- Of is elk een apart gesprek?

**Aanbevolen verduidelijking**:

| Stap | Skill | Verwachte omvang |
|------|-------|------------------|
| 4.1 | erpnext-impl-clientscripts | 3 reference files |
| 4.2 | erpnext-impl-serverscripts | 3 reference files |
| 4.3 | erpnext-impl-controllers | 3 reference files |
| 4.4 | erpnext-impl-hooks | 3 reference files |
| 4.5 | erpnext-impl-whitelisted | 3 reference files |
| 4.6 | erpnext-impl-jinja | 3 reference files |
| 4.7 | erpnext-impl-scheduler | 3 reference files |
| 4.8 | erpnext-impl-customapp | 3 reference files |

**Impact**: 8 aparte stappen in plaats van 1 gebundelde fase. Elk gesprek maakt 1 skill met NL + EN versies.

**Niet opsplitsen per skill**: Elke impl-skill heeft slechts 3 reference files, wat binnen de drempelwaarde valt.

---

### Fase 5 (Error Handling Skills) - AANBEVELING: EXPLICIETE STAPPEN

Zelfde situatie als Fase 4:

| Stap | Skill | Verwachte omvang |
|------|-------|------------------|
| 5.1 | erpnext-errors-clientscripts | 3 reference files |
| 5.2 | erpnext-errors-serverscripts | 3 reference files |
| 5.3 | erpnext-errors-controllers | 3 reference files |
| 5.4 | erpnext-errors-hooks | 3 reference files |
| 5.5 | erpnext-errors-whitelisted | 3 reference files |
| 5.6 | erpnext-errors-jinja | 3 reference files |
| 5.7 | erpnext-errors-scheduler | 3 reference files |

**Impact**: 7 aparte stappen in plaats van 1 gebundelde fase.

---

### Fase 6 (Agents) - AANBEVELING: NIET OPSPLITSEN

| Stap | Agent | Reference Files |
|------|-------|-----------------|
| 6.1 | erpnext-interpreter | 2 |
| 6.2 | erpnext-validator | 2 |

**Reden**: Elk agent heeft slechts 2 reference files. Dit is ruim binnen de drempelwaarde.

---

### Fase 7 (Finalisatie) - AANBEVELING: NIET OPSPLITSEN

| Stap | Taak | Complexiteit |
|------|------|--------------|
| 7.1 | Dependencies documenteren | Laag |
| 7.2 | Packaging alle skills | Hoog maar procedureel |

**Reden**: Fase 7 is procedureel en kan in Ã©Ã©n gesprek worden afgerond.

---

## Samenvatting Aanbevelingen

### Directe Opsplitsing Vereist

| Fase | Reden | Actie |
|------|-------|-------|
| **2.8 (Hooks)** | 12 secties, 8 reference files | Split naar 2.8.1 + 2.8.2 |

### Verduidelijking Vereist (geen opsplitsing per skill)

| Fase | Reden | Actie |
|------|-------|-------|
| **4 (Impl)** | 8 skills onduidelijk gegroepeerd | Expliciet 4.1-4.8 benoemen |
| **5 (Errors)** | 7 skills onduidelijk gegroepeerd | Expliciet 5.1-5.7 benoemen |

### Geen Actie Vereist

| Fase | Reden |
|------|-------|
| 3 (Core) | Binnen drempelwaarden |
| 6 (Agents) | Binnen drempelwaarden |
| 7 (Finalisatie) | Procedureel |

---

## Voorgestelde Gedetailleerde Opsplitsing Fase 2.8

### Stap 2.8.1: CreÃ«er erpnext-syntax-hooks - Event Hooks

**Focus**: Hooks die reageren op events

**Secties uit research document**:
1. DOC_EVENTS - Document lifecycle hooks
2. SCHEDULER_EVENTS - Cron en tijd-gebaseerde hooks
3. BOOTINFO - Opstartgegevens hooks

**Output reference bestanden**:
- `doc-events.md` - Alle doc_events met signatures
- `scheduler-events.md` - Cron syntax en configuratie
- `bootinfo.md` - Boot hooks en extend_bootinfo

---

### Stap 2.8.2: CreÃ«er erpnext-syntax-hooks - Configuration Hooks

**Focus**: Hooks voor configuratie en overrides

**Secties uit research document**:
4. OVERRIDE HOOKS - Override systeem
5. FIXTURES - Data export/import configuratie
6. PERMISSION HOOKS - Permission gerelateerde hooks
7. ASSET INCLUDES - CSS/JS includes
8. JINJA ENVIRONMENT - Template uitbreidingen
9. ANDERE ESSENTIÃ‹LE HOOKS - Overige hooks
10. COMPLETE REFERENCE TABEL - Naslagwerk
11. ANTI-PATTERNS - Wat te vermijden
12. VERSIE VERSCHILLEN - v14 vs v15

**Output reference bestanden**:
- `overrides.md` - Override patterns en override_doctype_class
- `fixtures.md` - Fixtures configuratie
- `permissions.md` - Permission hooks
- `examples.md` - Complete hooks.py voorbeelden
- `anti-patterns.md` - Fouten en correcties

---

## Aangepaste Fasenummering na Wijzigingen

### Fase 2 (met opsplitsingen)

| Origineel | Nieuw | Beschrijving |
|-----------|-------|--------------|
| 2.1-2.5 | Ongewijzigd | Research stappen |
| 2.6 | 2.6.1 + 2.6.2 | Custom App (reeds gedaan) |
| 2.7 | 2.7.1 + 2.7.2 | Controllers (reeds gedaan) |
| 2.8 | **2.8.1 + 2.8.2** | **Hooks (nieuw)** |
| 2.9 | Ongewijzigd | Whitelisted |
| 2.10 | Ongewijzigd | Jinja |
| 2.11 | Ongewijzigd | Scheduler |
| 2.12 | 2.12.1 + 2.12.2 | Custom App skill (reeds gedaan) |

### Fase 4 (verduidelijking)

| Nieuw | Skill |
|-------|-------|
| 4.1 | erpnext-impl-clientscripts |
| 4.2 | erpnext-impl-serverscripts |
| 4.3 | erpnext-impl-controllers |
| 4.4 | erpnext-impl-hooks |
| 4.5 | erpnext-impl-whitelisted |
| 4.6 | erpnext-impl-jinja |
| 4.7 | erpnext-impl-scheduler |
| 4.8 | erpnext-impl-customapp |

### Fase 5 (verduidelijking)

| Nieuw | Skill |
|-------|-------|
| 5.1 | erpnext-errors-clientscripts |
| 5.2 | erpnext-errors-serverscripts |
| 5.3 | erpnext-errors-controllers |
| 5.4 | erpnext-errors-hooks |
| 5.5 | erpnext-errors-whitelisted |
| 5.6 | erpnext-errors-jinja |
| 5.7 | erpnext-errors-scheduler |

---

## Totaal Impact op Gesprekken

| Fase | Origineel Gesprekken | Na Wijzigingen |
|------|---------------------|----------------|
| 2 | ~12 | ~14 (+2 door 2.8 split) |
| 3 | 3 | 3 (ongewijzigd) |
| 4 | 1 (of 8?) | 8 (expliciet) |
| 5 | 1 (of 7?) | 7 (expliciet) |
| 6 | 2 | 2 (ongewijzigd) |
| 7 | 2 | 2 (ongewijzigd) |
| **Totaal** | **~21-36** | **~36** |

De wijziging maakt het aantal gesprekken expliciet in plaats van ambigu.

---

## Noot: Monitor Tijdens Uitvoering

De volgende fases kunnen tijdens uitvoering alsnog opsplitsing vereisen als de content groter blijkt dan verwacht:

| Fase | Risico | Trigger voor opsplitsing |
|------|--------|--------------------------|
| 3.1 (Database) | Medium | Als research >800 regels wordt |
| 2.9 (Whitelisted) | Laag | Als research >600 regels |
| 2.10 (Jinja) | Laag | Als research >600 regels |
| 2.11 (Scheduler) | Laag | Als research >600 regels |

Aanbeveling: na elk research document de omvang beoordelen voordat de skill creatie start.

---

## Appendix: Criteria Checklist voor Toekomstige Opsplitsingen

Gebruik deze checklist bij elke nieuwe fase:

```
â–¡ Aantal reference files per gesprek â‰¤ 5
â–¡ Aantal secties/onderwerpen per gesprek â‰¤ 8-10
â–¡ Totaal regels research document â‰¤ 700
â–¡ Logische scheiding tussen delen mogelijk
â–¡ Dependencies tussen delen minimaal of geen
â–¡ Elk deel is zelfstandig begrijpelijk
```

Als 2+ criteria overschreden worden â†’ opsplitsing overwegen.
