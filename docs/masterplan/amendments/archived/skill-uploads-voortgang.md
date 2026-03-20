# ERPNext Skills: Voortgang & Upload Dependencies

> **Tussentijdse check** | 14 januari 2026

---

## âœ… Voltooide Skills (3 van 8 syntax skills)

| Skill | NL | EN | Status |
|-------|----|----|--------|
| frappe-syntax-clientscripts | âœ… | âœ… | Compleet |
| frappe-syntax-serverscripts | âœ… | âœ… | Compleet |
| frappe-syntax-hooks | âœ… | âœ… | Compleet |

---

## ðŸ“‹ Resterende Fases & Upload Requirements

### Fase 2: Syntax Skills (resterende)

| Fase | Beschrijving | Uploads Nodig |
|------|--------------|---------------|
| 2.9.1 | Whitelisted (Core API) | âœ— Geen |
| **2.9.2** | Whitelisted (Security) | âœ— Geen* |
| 2.10 | Jinja Templates | âœ— Geen |
| 2.11 | Scheduler/Background Jobs | âœ— Geen |
| 2.12.1 | Custom App (Setup) | âœ— Geen |
| 2.12.2 | Custom App (Data) | ðŸ“Ž `frappe-syntax-customapp` (van 2.12.1) |

*\* 2.9.2 heeft output van 2.9.1 nodig, maar die zit al in project files*

### Fase 3: Core Skills

| Fase | Beschrijving | Uploads Nodig |
|------|--------------|---------------|
| 3.1 | Database Patterns | âœ— Geen |
| 3.2 | Permissions | âœ— Geen |
| 3.3 | API Patterns | âœ— Geen |

### Fase 4: Implementation Skills (elk 1 upload)

| Fase | Skill | Upload Vereist |
|------|-------|----------------|
| 4.1 | impl-clientscripts | ðŸ“Ž `frappe-syntax-clientscripts` |
| 4.2 | impl-serverscripts | ðŸ“Ž `frappe-syntax-serverscripts` |
| 4.3 | impl-controllers | ðŸ“Ž `frappe-syntax-controllers` |
| 4.4 | impl-hooks | ðŸ“Ž `frappe-syntax-hooks` |
| 4.5 | impl-whitelisted | ðŸ“Ž `frappe-syntax-whitelisted` |
| 4.6 | impl-jinja | ðŸ“Ž `frappe-syntax-jinja` |
| 4.7 | impl-scheduler | ðŸ“Ž `frappe-syntax-scheduler` |
| 4.8 | impl-customapp | ðŸ“Ž `frappe-syntax-customapp` |

### Fase 5: Error Handling Skills (elk 1 upload)

| Fase | Skill | Upload Vereist |
|------|-------|----------------|
| 5.1 | errors-clientscripts | ðŸ“Ž `frappe-syntax-clientscripts` |
| 5.2 | errors-serverscripts | ðŸ“Ž `frappe-syntax-serverscripts` |
| 5.3 | errors-controllers | ðŸ“Ž `frappe-syntax-controllers` |
| 5.4 | errors-hooks | ðŸ“Ž `frappe-syntax-hooks` |
| 5.5 | errors-whitelisted | ðŸ“Ž `frappe-syntax-whitelisted` |
| 5.6 | errors-jinja | ðŸ“Ž `frappe-syntax-jinja` |
| 5.7 | errors-scheduler | ðŸ“Ž `frappe-syntax-scheduler` |

### Fase 6: Intelligent Agents

| Fase | Beschrijving | Uploads Vereist |
|------|--------------|-----------------|
| 6.1 | erpnext-interpreter | ðŸ“Ž **8 syntax skills** (alle) |
| 6.2 | erpnext-validator | ðŸ“Ž **23 skills** (syntax + impl + errors) |

### Fase 7: Finalisatie

| Fase | Beschrijving | Uploads Vereist |
|------|--------------|-----------------|
| 7.1 | Dependencies documenteren | ðŸ“Ž Alle skills |
| 7.2 | Final packaging | ðŸ“Ž Alle skills |

---

## ðŸ“Š Quick Reference

```
Fase 2.9 - 2.11 + 2.12.1  â†’ Geen uploads
Fase 2.12.2               â†’ 1 upload (van 2.12.1)
Fase 3.x                  â†’ Geen uploads
Fase 4.x                  â†’ 1 upload per gesprek
Fase 5.x                  â†’ 1 upload per gesprek
Fase 6.1                  â†’ 8 uploads
Fase 6.2                  â†’ 23 uploads
Fase 7                    â†’ Alle (~28)
```

---

## âš ï¸ Nog Te Maken Syntax Skills (5)

| Skill | Research | Status |
|-------|----------|--------|
| frappe-syntax-whitelisted | âœ… research-whitelisted-methods.md | ðŸ”œ Fase 2.9 |
| frappe-syntax-jinja | âœ… research-jinja-templates.md | â³ Fase 2.10 |
| frappe-syntax-scheduler | âœ… research-scheduler-background-jobs.md | â³ Fase 2.11 |
| frappe-syntax-controllers | âœ… research-document-controllers.md | â³ Fase 2.7* |
| frappe-syntax-customapp | âœ… research-customapp-*.md | â³ Fase 2.12 |

*\* Controllers skill lijkt nog niet gemaakt - verifiÃ«ren!*

---

## ðŸ” Verificatie Checklist

Voltooide research documenten:
- [x] research-client-scripts.md
- [x] research-server-scripts.md  
- [x] research-document-controllers.md
- [x] research-document-hooks.md
- [x] research-whitelisted-methods.md
- [x] research-jinja-templates.md
- [x] research-scheduler-background-jobs.md
- [x] research-custom-app-structure.md
- [x] research-customapp-datamanagement.md

Voltooide skills (packages):
- [x] frappe-syntax-clientscripts (NL + EN)
- [x] frappe-syntax-serverscripts (NL + EN)
- [x] frappe-syntax-hooks (NL + EN)
- [ ] frappe-syntax-controllers â“
- [ ] frappe-syntax-whitelisted
- [ ] frappe-syntax-jinja
- [ ] frappe-syntax-scheduler
- [ ] frappe-syntax-customapp

---

## â“ Openstaande Vraag

**Controllers skill status onduidelijk** - Het masterplan noemt fase 2.7.1/2.7.2 voor controllers, maar er zijn geen controller .skill bestanden geÃ¼pload. 

Mogelijke verklaringen:
1. Nog niet gemaakt (dan moet dit vÃ³Ã³r 2.9.2)
2. Gemaakt maar niet geÃ¼pload
3. Anders genummerd in de planning

**Actie**: Bevestig status controllers skill vÃ³Ã³r verder gaan.
