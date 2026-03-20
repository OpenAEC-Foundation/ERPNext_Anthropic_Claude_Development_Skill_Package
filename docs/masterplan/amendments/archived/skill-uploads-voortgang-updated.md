# ERPNext Skills: Voortgang & Upload Dependencies

> **Update** | 14 januari 2026 | Fase 2.9.2 voltooid

---

## ✅ Voltooide Skills (4 van 8 syntax skills)

| Skill | NL | EN | Status |
|-------|----|----|--------|
| frappe-syntax-clientscripts | ✅ | ✅ | Compleet |
| frappe-syntax-serverscripts | ✅ | ✅ | Compleet |
| frappe-syntax-hooks | ✅ | ✅ | Compleet |
| frappe-syntax-whitelisted | ✅ | ✅ | **Compleet (fase 2.9.1 + 2.9.2)** |

---

## 📋 Resterende Fases & Upload Requirements

### Fase 2: Syntax Skills (resterende)

| Fase | Beschrijving | Uploads Nodig | Status |
|------|--------------|---------------|--------|
| ~~2.9.1~~ | ~~Whitelisted (Core API)~~ | ~~✗ Geen~~ | ✅ Voltooid |
| ~~2.9.2~~ | ~~Whitelisted (Security)~~ | ~~✗ Geen~~ | ✅ Voltooid |
| 2.10 | Jinja Templates | ✗ Geen | ⏳ Volgende |
| 2.11 | Scheduler/Background Jobs | ✗ Geen | ⏳ |
| 2.12.1 | Custom App (Setup) | ✗ Geen | ⏳ |
| 2.12.2 | Custom App (Data) | 📎 `frappe-syntax-customapp` (van 2.12.1) | ⏳ |

### Fase 3: Core Skills

| Fase | Beschrijving | Uploads Nodig |
|------|--------------|---------------|
| 3.1 | Database Patterns | ✗ Geen |
| 3.2 | Permissions | ✗ Geen |
| 3.3 | API Patterns | ✗ Geen |

### Fase 4: Implementation Skills (elk 1 upload)

| Fase | Skill | Upload Vereist |
|------|-------|----------------|
| 4.1 | impl-clientscripts | 📎 `frappe-syntax-clientscripts` |
| 4.2 | impl-serverscripts | 📎 `frappe-syntax-serverscripts` |
| 4.3 | impl-controllers | 📎 `frappe-syntax-controllers` |
| 4.4 | impl-hooks | 📎 `frappe-syntax-hooks` |
| 4.5 | impl-whitelisted | 📎 `frappe-syntax-whitelisted` |
| 4.6 | impl-jinja | 📎 `frappe-syntax-jinja` |
| 4.7 | impl-scheduler | 📎 `frappe-syntax-scheduler` |
| 4.8 | impl-customapp | 📎 `frappe-syntax-customapp` |

### Fase 5: Error Handling Skills (elk 1 upload)

| Fase | Skill | Upload Vereist |
|------|-------|----------------|
| 5.1 | errors-clientscripts | 📎 `frappe-syntax-clientscripts` |
| 5.2 | errors-serverscripts | 📎 `frappe-syntax-serverscripts` |
| 5.3 | errors-controllers | 📎 `frappe-syntax-controllers` |
| 5.4 | errors-hooks | 📎 `frappe-syntax-hooks` |
| 5.5 | errors-whitelisted | 📎 `frappe-syntax-whitelisted` |
| 5.6 | errors-jinja | 📎 `frappe-syntax-jinja` |
| 5.7 | errors-scheduler | 📎 `frappe-syntax-scheduler` |

### Fase 6: Intelligent Agents

| Fase | Beschrijving | Uploads Vereist |
|------|--------------|-----------------|
| 6.1 | erpnext-interpreter | 📎 **8 syntax skills** (alle) |
| 6.2 | erpnext-validator | 📎 **23 skills** (syntax + impl + errors) |

### Fase 7: Finalisatie

| Fase | Beschrijving | Uploads Vereist |
|------|--------------|-----------------|
| 7.1 | Dependencies documenteren | 📎 Alle skills |
| 7.2 | Final packaging | 📎 Alle skills |

---

## 📊 Quick Reference

```
Fase 2.10 - 2.11 + 2.12.1  → Geen uploads
Fase 2.12.2               → 1 upload (van 2.12.1)
Fase 3.x                  → Geen uploads
Fase 4.x                  → 1 upload per gesprek
Fase 5.x                  → 1 upload per gesprek
Fase 6.1                  → 8 uploads
Fase 6.2                  → 23 uploads
Fase 7                    → Alle (~28)
```

---

## ⚠️ Nog Te Maken Syntax Skills (4)

| Skill | Research | Status |
|-------|----------|--------|
| frappe-syntax-jinja | ✅ research-jinja-templates.md | 📜 Fase 2.10 (volgende) |
| frappe-syntax-scheduler | ✅ research-scheduler-background-jobs.md | ⏳ Fase 2.11 |
| frappe-syntax-controllers | ✅ research-document-controllers.md | ⏳ Fase 2.7* |
| frappe-syntax-customapp | ✅ research-customapp-*.md | ⏳ Fase 2.12 |

*\* Controllers skill lijkt nog niet gemaakt - verifiëren!*

---

## 📝 Verificatie Checklist

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
- [x] **frappe-syntax-whitelisted (NL + EN)** ← NIEUW
- [ ] frappe-syntax-controllers ❓
- [ ] frappe-syntax-jinja
- [ ] frappe-syntax-scheduler
- [ ] frappe-syntax-customapp

---

## ❓ Openstaande Vraag

**Controllers skill status onduidelijk** - Het masterplan noemt fase 2.7.1/2.7.2 voor controllers, maar er zijn geen controller .skill bestanden geüpload. 

Mogelijke verklaringen:
1. Nog niet gemaakt (dan moet dit vóór verder gaan)
2. Gemaakt maar niet geüpload
3. Anders genummerd in de planning

**Actie**: Bevestig status controllers skill vóór verder gaan.

---

## 📦 Fase 2.9 Deliverables

**frappe-syntax-whitelisted-nl.skill** (28 KB)
- SKILL.md (337 regels)
- 8 reference files: decorator-options, parameter-handling, response-patterns, client-calls, permission-patterns, error-handling, examples, anti-patterns

**frappe-syntax-whitelisted-en.skill** (27 KB)
- SKILL.md (337 regels)  
- 8 reference files (zelfde structuur als NL)
