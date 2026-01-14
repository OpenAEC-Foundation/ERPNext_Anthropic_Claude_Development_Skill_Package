# Masterplan Aanvulling: Skill Uploads per Fase

> **Datum**: 13 januari 2026
> **Betreft**: Overzicht welke .skill bestanden geÃ¼pload moeten worden per gesprek/fase

---

## Legenda

| Symbool | Betekenis |
|---------|-----------|
| âœ“ | Geen uploads nodig - alleen project files gebruiken |
| ðŸ“Ž | Upload vereist - specificeerde .skill bestand(en) bijvoegen |

---

## Fase 2: Syntax Skills (Research & Creatie)

### Research Stappen (2.1 - 2.6)

| Fase | Beschrijving | Uploads |
|------|--------------|---------|
| 2.1 | Research Controllers | âœ“ Geen |
| 2.2 | Research Hooks | âœ“ Geen |
| 2.3 | Research Whitelisted | âœ“ Geen |
| 2.4 | Research Jinja | âœ“ Geen |
| 2.5 | Research Scheduler | âœ“ Geen |
| 2.6.1 | Research Custom App (Basis) | âœ“ Geen |
| 2.6.2 | Research Custom App (Data) | âœ“ Geen |

### Skill Creatie Stappen (2.7 - 2.12)

| Fase | Beschrijving | Uploads |
|------|--------------|---------|
| 2.7.1 | CreÃ«er controllers skill (Basics) | âœ“ Geen |
| 2.7.2 | CreÃ«er controllers skill (Patterns) | âœ“ Geen |
| 2.8.1 | CreÃ«er hooks skill (Events) | âœ“ Geen |
| 2.8.2 | CreÃ«er hooks skill (Config) | ðŸ“Ž `erpnext-syntax-hooks.skill` (van 2.8.1) |
| 2.9 | CreÃ«er whitelisted skill | âœ“ Geen |
| 2.10 | CreÃ«er jinja skill | âœ“ Geen |
| 2.11 | CreÃ«er scheduler skill | âœ“ Geen |
| 2.12.1 | CreÃ«er customapp skill (Basis) | âœ“ Geen |
| 2.12.2 | CreÃ«er customapp skill (Data) | ðŸ“Ž `erpnext-syntax-customapp.skill` (van 2.12.1) |

---

## Fase 3: Core Skills

| Fase | Beschrijving | Uploads |
|------|--------------|---------|
| 3.1 | CreÃ«er database skill | âœ“ Geen |
| 3.2 | CreÃ«er permissions skill | âœ“ Geen |
| 3.3 | CreÃ«er api-patterns skill | âœ“ Geen |

**Toelichting**: Core skills zijn zelfstandig en vereisen geen eerdere syntax skills.

---

## Fase 4: Implementation Skills

| Fase | Beschrijving | Uploads |
|------|--------------|---------|
| 4.1 | CreÃ«er impl-clientscripts | ðŸ“Ž `erpnext-syntax-clientscripts.skill` |
| 4.2 | CreÃ«er impl-serverscripts | ðŸ“Ž `erpnext-syntax-serverscripts.skill` |
| 4.3 | CreÃ«er impl-controllers | ðŸ“Ž `erpnext-syntax-controllers.skill` |
| 4.4 | CreÃ«er impl-hooks | ðŸ“Ž `erpnext-syntax-hooks.skill` |
| 4.5 | CreÃ«er impl-whitelisted | ðŸ“Ž `erpnext-syntax-whitelisted.skill` |
| 4.6 | CreÃ«er impl-jinja | ðŸ“Ž `erpnext-syntax-jinja.skill` |
| 4.7 | CreÃ«er impl-scheduler | ðŸ“Ž `erpnext-syntax-scheduler.skill` |
| 4.8 | CreÃ«er impl-customapp | ðŸ“Ž `erpnext-syntax-customapp.skill` |

**Toelichting**: Elke implementation skill bouwt voort op de bijbehorende syntax skill om workflow patterns en decision trees te maken.

---

## Fase 5: Error Handling Skills

| Fase | Beschrijving | Uploads |
|------|--------------|---------|
| 5.1 | CreÃ«er errors-clientscripts | ðŸ“Ž `erpnext-syntax-clientscripts.skill` |
| 5.2 | CreÃ«er errors-serverscripts | ðŸ“Ž `erpnext-syntax-serverscripts.skill` |
| 5.3 | CreÃ«er errors-controllers | ðŸ“Ž `erpnext-syntax-controllers.skill` |
| 5.4 | CreÃ«er errors-hooks | ðŸ“Ž `erpnext-syntax-hooks.skill` |
| 5.5 | CreÃ«er errors-whitelisted | ðŸ“Ž `erpnext-syntax-whitelisted.skill` |
| 5.6 | CreÃ«er errors-jinja | ðŸ“Ž `erpnext-syntax-jinja.skill` |
| 5.7 | CreÃ«er errors-scheduler | ðŸ“Ž `erpnext-syntax-scheduler.skill` |

**Toelichting**: Error handling skills moeten de syntax kennen om foutpatronen te kunnen identificeren en corrigeren.

---

## Fase 6: Intelligent Agents

| Fase | Beschrijving | Uploads |
|------|--------------|---------|
| 6.1 | CreÃ«er erpnext-interpreter agent | ðŸ“Ž **ALLE syntax skills** (8 stuks) |
| 6.2 | CreÃ«er erpnext-validator agent | ðŸ“Ž **ALLE skills** (syntax + impl + errors) |

### Volledige Upload Lijst Fase 6.1

```
erpnext-syntax-clientscripts.skill
erpnext-syntax-serverscripts.skill
erpnext-syntax-controllers.skill
erpnext-syntax-hooks.skill
erpnext-syntax-whitelisted.skill
erpnext-syntax-jinja.skill
erpnext-syntax-scheduler.skill
erpnext-syntax-customapp.skill
```

### Volledige Upload Lijst Fase 6.2

Alle bovenstaande PLUS:
```
erpnext-impl-clientscripts.skill
erpnext-impl-serverscripts.skill
erpnext-impl-controllers.skill
erpnext-impl-hooks.skill
erpnext-impl-whitelisted.skill
erpnext-impl-jinja.skill
erpnext-impl-scheduler.skill
erpnext-impl-customapp.skill
erpnext-errors-clientscripts.skill
erpnext-errors-serverscripts.skill
erpnext-errors-controllers.skill
erpnext-errors-hooks.skill
erpnext-errors-whitelisted.skill
erpnext-errors-jinja.skill
erpnext-errors-scheduler.skill
```

**Totaal Fase 6.2**: 23 skill bestanden (of 46 als NL+EN apart)

---

## Fase 7: Finalisatie

| Fase | Beschrijving | Uploads |
|------|--------------|---------|
| 7.1 | Dependencies documenteren | ðŸ“Ž Alle skills (voor verificatie) |
| 7.2 | Final packaging | ðŸ“Ž Alle skills (voor bundeling) |

---

## Samenvatting per Aantal Uploads

| Fase Range | Uploads per Gesprek |
|------------|---------------------|
| 2.1 - 2.8.1 | 0 |
| 2.8.2, 2.12.2 | 1 (voorgaande deel) |
| 2.9 - 2.12.1 | 0 |
| 3.1 - 3.3 | 0 |
| 4.1 - 4.8 | 1 per gesprek |
| 5.1 - 5.7 | 1 per gesprek |
| 6.1 | 8 |
| 6.2 | 23 |
| 7.1 - 7.2 | Alle (~28) |

---

## Praktische Tips

### 1. Taalversie Kiezen
Je hoeft slechts **Ã©Ã©n taalversie** te uploaden (NL of EN). De inhoud is identiek, alleen de beschrijvingen verschillen.

### 2. Bestandsbeheer
Bewaar alle `.skill` bestanden in Ã©Ã©n lokale map, bijvoorbeeld:
```
ERPNext-Skills/
â”œâ”€â”€ completed/
â”‚   â”œâ”€â”€ erpnext-syntax-clientscripts-NL.skill
â”‚   â”œâ”€â”€ erpnext-syntax-clientscripts-EN.skill
â”‚   â”œâ”€â”€ erpnext-syntax-serverscripts-NL.skill
â”‚   â””â”€â”€ ...
â””â”€â”€ in-progress/
```

### 3. Bij Opgesplitste Fases (2.8, 2.12)
- Deel 1 maakt de basis skill
- Deel 2 **vereist upload** van deel 1 output om uit te breiden
- Na deel 2 is er Ã©Ã©n complete skill

### 4. Grote Upload Sessies (Fase 6+)
Bij veel uploads kun je overwegen:
- Skills in batches te uploaden als Claude traag reageert
- Alleen NL Ã³f EN versies te gebruiken (niet beide)

---

## Quick Reference: "Moet ik iets uploaden?"

```
Fase 2-3 (behalve 2.8.2/2.12.2)?  â†’ NEE
Fase 4.x?                         â†’ JA, 1 syntax skill
Fase 5.x?                         â†’ JA, 1 syntax skill  
Fase 6.1?                         â†’ JA, 8 syntax skills
Fase 6.2?                         â†’ JA, 23 skills
Fase 7?                           â†’ JA, alle skills
```

---

## Voortgang Bijhouden

Gebruik deze checklist om bij te houden welke skills compleet zijn:

### Syntax Skills (Fase 1-2)
- [x] erpnext-syntax-clientscripts (NL + EN)
- [x] erpnext-syntax-serverscripts (NL + EN)
- [ ] erpnext-syntax-controllers (NL + EN)
- [x] erpnext-syntax-hooks (NL + EN)
- [ ] erpnext-syntax-whitelisted (NL + EN)
- [ ] erpnext-syntax-jinja (NL + EN)
- [ ] erpnext-syntax-scheduler (NL + EN)
- [ ] erpnext-syntax-customapp (NL + EN)

### Core Skills (Fase 3)
- [ ] erpnext-core-database (NL + EN)
- [ ] erpnext-core-permissions (NL + EN)
- [ ] erpnext-core-api (NL + EN)

### Implementation Skills (Fase 4)
- [ ] erpnext-impl-clientscripts (NL + EN)
- [ ] erpnext-impl-serverscripts (NL + EN)
- [ ] erpnext-impl-controllers (NL + EN)
- [ ] erpnext-impl-hooks (NL + EN)
- [ ] erpnext-impl-whitelisted (NL + EN)
- [ ] erpnext-impl-jinja (NL + EN)
- [ ] erpnext-impl-scheduler (NL + EN)
- [ ] erpnext-impl-customapp (NL + EN)

### Error Handling Skills (Fase 5)
- [ ] erpnext-errors-clientscripts (NL + EN)
- [ ] erpnext-errors-serverscripts (NL + EN)
- [ ] erpnext-errors-controllers (NL + EN)
- [ ] erpnext-errors-hooks (NL + EN)
- [ ] erpnext-errors-whitelisted (NL + EN)
- [ ] erpnext-errors-jinja (NL + EN)
- [ ] erpnext-errors-scheduler (NL + EN)

### Agents (Fase 6)
- [ ] erpnext-interpreter (NL + EN)
- [ ] erpnext-validator (NL + EN)
