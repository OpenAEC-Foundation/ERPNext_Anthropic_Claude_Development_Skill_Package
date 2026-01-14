# Masterplan Aanpassing: Opsplitsing Fase 2.10 en 2.11

> **Datum**: 14 januari 2026  
> **Betreft**: Fase 2.10 (Jinja Templates) en Fase 2.11 (Scheduler) opsplitsen

---

## Overzicht Opsplitsingen

| Originele Fase | Nieuwe Fases | Reden |
|----------------|--------------|-------|
| 2.10 (Jinja) | 2.10.1 + 2.10.2 | 928 regels, 8 ref files, 11 secties |
| 2.11 (Scheduler) | 2.11.1 + 2.11.2 | 751 regels, 7 ref files, 12 secties |

---

# DEEL A: Opsplitsing Fase 2.10 (Jinja Templates)

## Reden voor Opsplitsing

De `erpnext-syntax-jinja` skill bevat uitgebreide content:
- **11 secties** in het research document (928 regels)
- **8 reference bestanden** gepland
- Logische scheiding mogelijk tussen "templating basics" en "custom uitbreidingen"

### Criteria Check

| Criterium | Drempel | Werkelijk | Status |
|-----------|---------|-----------|--------|
| Research regels | â‰¤700 | 928 | âš ï¸ Overschreden |
| Reference files | â‰¤5 | 8 | âš ï¸ Overschreden |
| Secties | â‰¤8-10 | 11 | âš ï¸ Overschreden |

**Conclusie**: 3 van 3 criteria overschreden â†’ opsplitsing conform vastgestelde regels.

---

## Inhoud Research Document (research-jinja-templates.md)

Het research document bevat 11 secties:

| # | Sectie | Regels | Naar Deel |
|---|--------|--------|-----------|
| 1 | BESCHIKBARE OBJECTEN IN JINJA CONTEXT | 23-58 | 2.10.1 |
| 2 | FRAPPE METHODS IN JINJA | 60-271 | 2.10.1 |
| 3 | PRINT FORMATS | 274-470 | 2.10.1 |
| 4 | EMAIL TEMPLATES | 473-550 | 2.10.1 |
| 5 | PORTAL PAGES | 553-623 | 2.10.2 |
| 6 | CUSTOM METHODS VIA HOOKS (jenv) | 625-697 | 2.10.2 |
| 7 | STANDARD JINJA FILTERS & FUNCTIONS | 700-765 | 2.10.1 |
| 8 | SECURITY & BEST PRACTICES | 768-816 | 2.10.2 |
| 9 | REPORT PRINT FORMATS (Client-Side) | 819-846 | 2.10.2 |
| 10 | VERSIE VERSCHILLEN | 849-859 | 2.10.2 |
| 11 | ANTI-PATTERNS | 862-903 | 2.10.2 |

---

## Logische Scheiding

### Deel A (2.10.1): Core Templating
**Vraag die wordt beantwoord**: "Hoe gebruik ik Jinja in Frappe voor print formats en email templates?"

Focus op:
- Beschikbare objecten en context
- Frappe methods binnen templates
- Print format creatie
- Email template patterns
- Standaard Jinja filters

### Deel B (2.10.2): Advanced & Custom
**Vraag die wordt beantwoord**: "Hoe maak ik portal pages en voeg ik custom Jinja methods toe?"

Focus op:
- Portal pages met Python controllers
- Custom methods/filters via jenv hooks
- Security best practices
- Report Print Formats (JS templating)
- Versie verschillen en anti-patterns

---

## Nieuwe Fase Definities

### Stap 2.10.1: CreÃ«er erpnext-syntax-jinja - Core Templating

**Onderzoeksonderwerpen uit research document**:
1. BESCHIKBARE OBJECTEN IN JINJA CONTEXT - doc, frappe, session
2. FRAPPE METHODS IN JINJA - format, get_doc, get_all, db methods
3. PRINT FORMATS - structuur, child tables, styling
4. EMAIL TEMPLATES - doc context, field access
7. STANDARD JINJA FILTERS - length, default, safe, escape

**Output reference bestanden**:
- `available-objects.md` - Alle beschikbare objecten per context type
- `methods.md` - Alle frappe.* methods met signatures en voorbeelden
- `print-formats.md` - Print format patterns en voorbeelden
- `email-templates.md` - Email template patterns

---

### Stap 2.10.2: CreÃ«er erpnext-syntax-jinja - Advanced & Custom

**Onderzoeksonderwerpen uit research document**:
5. PORTAL PAGES - www templates, Python controllers, routing
6. CUSTOM METHODS VIA HOOKS (jenv) - custom methods en filters
8. SECURITY & BEST PRACTICES - safe render, escaping, performance
9. REPORT PRINT FORMATS - JS templating syntax (niet Jinja!)
10. VERSIE VERSCHILLEN - v14 vs v15
11. ANTI-PATTERNS - N+1 queries, heavy calculations, XSS

**Output reference bestanden**:
- `portal-pages.md` - Web template patterns met controllers
- `custom-jenv.md` - Custom methods/filters via hooks.py
- `examples.md` - Complete werkende voorbeelden
- `anti-patterns.md` - Wat te vermijden met correcte alternatieven

---

## Aangepaste Prompts

### PROMPT FASE 2.10.1 - CREÃ‹ER SKILL: erpnext-syntax-jinja (CORE)

```
â”Œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”
â”‚ PROMPT FASE 2.10.1 - CREÃ‹ER SKILL: erpnext-syntax-jinja (A)        â”‚
â”œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”¤
â”‚                                                                     â”‚
â”‚ Gebruik research-jinja-templates.md SECTIES 1-4 en 7 om het        â”‚
â”‚ EERSTE DEEL van de 'erpnext-syntax-jinja' skill te maken.          â”‚
â”‚                                                                     â”‚
â”‚ VEREISTEN:                                                          â”‚
â”‚ 1. Volg exact de Anthropic skill-creator richtlijnen               â”‚
â”‚ 2. Maak TWEE versies: NL en EN                                     â”‚
â”‚ 3. SKILL.md < 500 regels                                           â”‚
â”‚                                                                     â”‚
â”‚ TE VERWERKEN SECTIES:                                               â”‚
â”‚ â€¢ 1. BESCHIKBARE OBJECTEN - doc, frappe, session per context       â”‚
â”‚ â€¢ 2. FRAPPE METHODS - format, get_doc, db methods                  â”‚
â”‚ â€¢ 3. PRINT FORMATS - structuur, child tables, styling              â”‚
â”‚ â€¢ 4. EMAIL TEMPLATES - doc context, field access                   â”‚
â”‚ â€¢ 7. STANDARD JINJA FILTERS - length, default, safe                â”‚
â”‚                                                                     â”‚
â”‚ TE MAKEN REFERENCE BESTANDEN:                                       â”‚
â”‚ references/                                                         â”‚
â”‚ â”œâ”€â”€ available-objects.md (context per template type)               â”‚
â”‚ â”œâ”€â”€ methods.md (frappe.* methods in Jinja)                         â”‚
â”‚ â”œâ”€â”€ print-formats.md (print format patterns)                       â”‚
â”‚ â””â”€â”€ email-templates.md (email template patterns)                   â”‚
â”‚                                                                     â”‚
â”‚ SKILL.MD FOCUS:                                                     â”‚
â”‚ - Frontmatter met triggers voor Jinja/template vragen              â”‚
â”‚ - Quick reference: basis print format template                     â”‚
â”‚ - Context table: welke objecten in welke template type             â”‚
â”‚ - Decision tree: "welke template type gebruik ik?"                 â”‚
â”‚ - Verwijzingen naar reference files                                 â”‚
â”‚                                                                     â”‚
â”‚ LET OP: Dit is Deel A. Secties 5-6, 8-11 komen in Deel B (2.10.2). â”‚
â”‚                                                                     â”‚
â””â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”˜
```

### PROMPT FASE 2.10.2 - CREÃ‹ER SKILL: erpnext-syntax-jinja (ADVANCED)

```
â”Œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”
â”‚ PROMPT FASE 2.10.2 - CREÃ‹ER SKILL: erpnext-syntax-jinja (B)        â”‚
â”œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”¤
â”‚                                                                     â”‚
â”‚ Gebruik research-jinja-templates.md SECTIES 5-6 en 8-11 om het     â”‚
â”‚ TWEEDE DEEL van de 'erpnext-syntax-jinja' skill te maken.          â”‚
â”‚                                                                     â”‚
â”‚ VOORWAARDE: Deel A (2.10.1) is compleet.                           â”‚
â”‚                                                                     â”‚
â”‚ TE VERWERKEN SECTIES:                                               â”‚
â”‚ â€¢ 5. PORTAL PAGES - www templates, controllers, routing            â”‚
â”‚ â€¢ 6. CUSTOM METHODS VIA HOOKS - jenv hook, custom filters          â”‚
â”‚ â€¢ 8. SECURITY & BEST PRACTICES - safe render, escaping             â”‚
â”‚ â€¢ 9. REPORT PRINT FORMATS - JS templating (NIET Jinja!)            â”‚
â”‚ â€¢ 10. VERSIE VERSCHILLEN - v14 vs v15                              â”‚
â”‚ â€¢ 11. ANTI-PATTERNS - N+1, heavy calcs, XSS                        â”‚
â”‚                                                                     â”‚
â”‚ TE MAKEN REFERENCE BESTANDEN:                                       â”‚
â”‚ references/                                                         â”‚
â”‚ â”œâ”€â”€ portal-pages.md (web templates met controllers)                â”‚
â”‚ â”œâ”€â”€ custom-jenv.md (custom methods/filters via hooks)              â”‚
â”‚ â”œâ”€â”€ examples.md (complete werkende voorbeelden)                    â”‚
â”‚ â””â”€â”€ anti-patterns.md (fouten en correcties)                        â”‚
â”‚                                                                     â”‚
â”‚ SKILL.MD AFRONDING:                                                 â”‚
â”‚ - Voeg portal pages sectie toe                                     â”‚
â”‚ - Voeg security checklist toe                                      â”‚
â”‚ - Documenteer Report Print Formats als UITZONDERING (JS!)          â”‚
â”‚ - Voeg versie-specifieke notities toe                              â”‚
â”‚ - Valideer totale skill < 500 regels                               â”‚
â”‚                                                                     â”‚
â”‚ PACKAGING:                                                          â”‚
â”‚ - Combineer alle 8 reference bestanden                             â”‚
â”‚ - Valideer met quick_validate.py                                   â”‚
â”‚ - Package NL en EN versies als .skill bestanden                    â”‚
â”‚                                                                     â”‚
â””â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”˜
```

---

## Reference Bestanden Verdeling (Fase 2.10)

| Bestand | Aangemaakt in | Inhoud |
|---------|---------------|--------|
| `available-objects.md` | 2.10.1 | Context objecten per template type |
| `methods.md` | 2.10.1 | frappe.* methods in Jinja |
| `print-formats.md` | 2.10.1 | Print format patterns |
| `email-templates.md` | 2.10.1 | Email template patterns |
| `portal-pages.md` | 2.10.2 | Web templates met controllers |
| `custom-jenv.md` | 2.10.2 | Custom methods/filters via hooks |
| `examples.md` | 2.10.2 | Complete werkende voorbeelden |
| `anti-patterns.md` | 2.10.2 | Fouten en correcties |

---

## Exit Criteria Fase 2.10

### 2.10.1 Exit Criteria:
- [ ] SKILL.md NL versie met secties 1-4, 7 verwerkt
- [ ] SKILL.md EN versie
- [ ] Reference: available-objects.md
- [ ] Reference: methods.md
- [ ] Reference: print-formats.md
- [ ] Reference: email-templates.md
- [ ] Context table voor template types

### 2.10.2 Exit Criteria:
- [ ] SKILL.md NL aangevuld met secties 5-6, 8-11
- [ ] SKILL.md EN aangevuld
- [ ] Reference: portal-pages.md
- [ ] Reference: custom-jenv.md
- [ ] Reference: examples.md
- [ ] Reference: anti-patterns.md
- [ ] Report Print Formats gedocumenteerd als JS uitzondering
- [ ] Totale skill < 500 regels
- [ ] Gevalideerd met quick_validate.py
- [ ] NL en EN .skill packages

---

# DEEL B: Opsplitsing Fase 2.11 (Scheduler/Background Jobs)

## Reden voor Opsplitsing

De `erpnext-syntax-scheduler` skill bevat uitgebreide content:
- **12 secties** in het research document (751 regels)
- **7 reference bestanden** gepland
- Logische scheiding mogelijk tussen "scheduler events" en "background jobs"

### Criteria Check

| Criterium | Drempel | Werkelijk | Status |
|-----------|---------|-----------|--------|
| Research regels | â‰¤700 | 751 | âš ï¸ Overschreden |
| Reference files | â‰¤5 | 7 | âš ï¸ Overschreden |
| Secties | â‰¤8-10 | 12 | âš ï¸ Overschreden |

**Conclusie**: 3 van 3 criteria overschreden â†’ opsplitsing conform vastgestelde regels.

---

## Inhoud Research Document (research-scheduler-background-jobs.md)

Het research document bevat 12 secties:

| # | Sectie | Regels | Naar Deel |
|---|--------|--------|-----------|
| 1 | SCHEDULER_EVENTS (hooks.py) | 25-136 | 2.11.1 |
| 2 | FRAPPE.ENQUEUE - Complete API | 138-226 | 2.11.1 |
| 3 | FRAPPE.ENQUEUE_DOC | 228-284 | 2.11.1 |
| 4 | QUEUE TYPES EN TIMEOUTS | 287-350 | 2.11.1 |
| 5 | JOB DEDUPLICATIE | 352-405 | 2.11.2 |
| 6 | ERROR HANDLING IN JOBS | 407-458 | 2.11.2 |
| 7 | MONITORING EN DEBUG | 460-540 | 2.11.2 |
| 8 | CONFIGURABLE SCHEDULER EVENTS | 543-561 | 2.11.2 |
| 9 | SCHEDULER USER CONTEXT | 564-589 | 2.11.1 |
| 10 | BEST PRACTICES | 592-636 | 2.11.2 |
| 11 | VERSIE VERSCHILLEN | 640-664 | 2.11.2 |
| 12 | ANTI-PATTERNS | 668-727 | 2.11.2 |

---

## Logische Scheiding

### Deel A (2.11.1): Scheduler & Enqueue Basics
**Vraag die wordt beantwoord**: "Hoe plan ik taken in Frappe en hoe start ik background jobs?"

Focus op:
- scheduler_events in hooks.py
- frappe.enqueue() en enqueue_doc()
- Queue types en timeouts
- Administrator context

### Deel B (2.11.2): Job Management & Monitoring
**Vraag die wordt beantwoord**: "Hoe maak ik jobs robuust en hoe monitor ik ze?"

Focus op:
- Job deduplicatie (job_id vs job_name)
- Error handling in jobs
- Monitoring via RQ doctypes
- Best practices en anti-patterns
- v14 vs v15 verschillen

---

## Nieuwe Fase Definities

### Stap 2.11.1: CreÃ«er erpnext-syntax-scheduler - Basics

**Onderzoeksonderwerpen uit research document**:
1. SCHEDULER_EVENTS - all, hourly, daily, cron syntax
2. FRAPPE.ENQUEUE - alle parameters, callbacks
3. FRAPPE.ENQUEUE_DOC - controller methods async
4. QUEUE TYPES EN TIMEOUTS - short, default, long
9. SCHEDULER USER CONTEXT - Administrator, owner setting

**Output reference bestanden**:
- `scheduler-events.md` - Alle event types met cron syntax
- `enqueue-api.md` - Complete frappe.enqueue/enqueue_doc parameters
- `queues.md` - Queue types, timeouts, custom queues

---

### Stap 2.11.2: CreÃ«er erpnext-syntax-scheduler - Advanced

**Onderzoeksonderwerpen uit research document**:
5. JOB DEDUPLICATIE - job_id, is_job_enqueued()
6. ERROR HANDLING IN JOBS - logging, failed job notifications
7. MONITORING EN DEBUG - RQ Worker/Job, bench doctor, logs
8. CONFIGURABLE SCHEDULER EVENTS - runtime configuration
10. BEST PRACTICES - commit per record, realtime feedback
11. VERSIE VERSCHILLEN - v14 vs v15 (scheduler tick, job_name deprecation)
12. ANTI-PATTERNS - blocking wait, infinite retry, missing commits

**Output reference bestanden**:
- `error-handling.md` - Error patterns en logging
- `monitoring.md` - RQ doctypes, bench commands, logging
- `examples.md` - Complete werkende voorbeelden
- `anti-patterns.md` - Wat te vermijden

---

## Aangepaste Prompts

### PROMPT FASE 2.11.1 - CREÃ‹ER SKILL: erpnext-syntax-scheduler (BASICS)

```
â”Œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”
â”‚ PROMPT FASE 2.11.1 - CREÃ‹ER SKILL: erpnext-syntax-scheduler (A)    â”‚
â”œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”¤
â”‚                                                                     â”‚
â”‚ Gebruik research-scheduler-background-jobs.md SECTIES 1-4 en 9 om  â”‚
â”‚ het EERSTE DEEL van de 'erpnext-syntax-scheduler' skill te maken.  â”‚
â”‚                                                                     â”‚
â”‚ VEREISTEN:                                                          â”‚
â”‚ 1. Volg exact de Anthropic skill-creator richtlijnen               â”‚
â”‚ 2. Maak TWEE versies: NL en EN                                     â”‚
â”‚ 3. SKILL.md < 500 regels                                           â”‚
â”‚                                                                     â”‚
â”‚ TE VERWERKEN SECTIES:                                               â”‚
â”‚ â€¢ 1. SCHEDULER_EVENTS - all, hourly, daily, cron                   â”‚
â”‚ â€¢ 2. FRAPPE.ENQUEUE - alle parameters, callbacks                   â”‚
â”‚ â€¢ 3. FRAPPE.ENQUEUE_DOC - controller methods async                 â”‚
â”‚ â€¢ 4. QUEUE TYPES - short, default, long, timeouts                  â”‚
â”‚ â€¢ 9. SCHEDULER USER CONTEXT - Administrator, owner setting         â”‚
â”‚                                                                     â”‚
â”‚ TE MAKEN REFERENCE BESTANDEN:                                       â”‚
â”‚ references/                                                         â”‚
â”‚ â”œâ”€â”€ scheduler-events.md (event types + cron syntax)                â”‚
â”‚ â”œâ”€â”€ enqueue-api.md (complete API parameters)                       â”‚
â”‚ â””â”€â”€ queues.md (queue types en timeouts)                            â”‚
â”‚                                                                     â”‚
â”‚ SKILL.MD FOCUS:                                                     â”‚
â”‚ - Frontmatter met triggers voor scheduler/background job vragen    â”‚
â”‚ - Quick reference: basis scheduler event template                  â”‚
â”‚ - Cron syntax cheatsheet                                           â”‚
â”‚ - Decision tree: "welke queue gebruik ik?"                         â”‚
â”‚ - BELANGRIJKE NOOT: bench migrate na scheduler_events wijzigingen  â”‚
â”‚                                                                     â”‚
â”‚ LET OP: Dit is Deel A. Secties 5-8, 10-12 komen in Deel B.         â”‚
â”‚                                                                     â”‚
â””â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”˜
```

### PROMPT FASE 2.11.2 - CREÃ‹ER SKILL: erpnext-syntax-scheduler (ADVANCED)

```
â”Œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”
â”‚ PROMPT FASE 2.11.2 - CREÃ‹ER SKILL: erpnext-syntax-scheduler (B)    â”‚
â”œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”¤
â”‚                                                                     â”‚
â”‚ Gebruik research-scheduler-background-jobs.md SECTIES 5-8, 10-12   â”‚
â”‚ om het TWEEDE DEEL van de 'erpnext-syntax-scheduler' skill te      â”‚
â”‚ maken.                                                              â”‚
â”‚                                                                     â”‚
â”‚ VOORWAARDE: Deel A (2.11.1) is compleet.                           â”‚
â”‚                                                                     â”‚
â”‚ TE VERWERKEN SECTIES:                                               â”‚
â”‚ â€¢ 5. JOB DEDUPLICATIE - job_id, is_job_enqueued()                  â”‚
â”‚ â€¢ 6. ERROR HANDLING - logging, notifications                       â”‚
â”‚ â€¢ 7. MONITORING - RQ Worker/Job, bench doctor                      â”‚
â”‚ â€¢ 8. CONFIGURABLE SCHEDULER EVENTS - runtime config                â”‚
â”‚ â€¢ 10. BEST PRACTICES - commit per record, realtime                 â”‚
â”‚ â€¢ 11. VERSIE VERSCHILLEN - v14 vs v15 breaking changes             â”‚
â”‚ â€¢ 12. ANTI-PATTERNS - blocking wait, infinite retry                â”‚
â”‚                                                                     â”‚
â”‚ TE MAKEN REFERENCE BESTANDEN:                                       â”‚
â”‚ references/                                                         â”‚
â”‚ â”œâ”€â”€ error-handling.md (error patterns en logging)                  â”‚
â”‚ â”œâ”€â”€ monitoring.md (RQ doctypes, bench commands)                    â”‚
â”‚ â”œâ”€â”€ examples.md (complete werkende voorbeelden)                    â”‚
â”‚ â””â”€â”€ anti-patterns.md (fouten en correcties)                        â”‚
â”‚                                                                     â”‚
â”‚ SKILL.MD AFRONDING:                                                 â”‚
â”‚ - Voeg deduplicatie sectie toe (v14 vs v15 syntax!)                â”‚
â”‚ - Voeg monitoring cheatsheet toe                                   â”‚
â”‚ - Documenteer v14â†’v15 migratie (job_name â†’ job_id)                 â”‚
â”‚ - Valideer totale skill < 500 regels                               â”‚
â”‚                                                                     â”‚
â”‚ PACKAGING:                                                          â”‚
â”‚ - Combineer alle 7 reference bestanden                             â”‚
â”‚ - Valideer met quick_validate.py                                   â”‚
â”‚ - Package NL en EN versies als .skill bestanden                    â”‚
â”‚                                                                     â”‚
â””â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”˜
```

---

## Reference Bestanden Verdeling (Fase 2.11)

| Bestand | Aangemaakt in | Inhoud |
|---------|---------------|--------|
| `scheduler-events.md` | 2.11.1 | Event types + cron syntax |
| `enqueue-api.md` | 2.11.1 | frappe.enqueue parameters |
| `queues.md` | 2.11.1 | Queue types en timeouts |
| `error-handling.md` | 2.11.2 | Error patterns en logging |
| `monitoring.md` | 2.11.2 | RQ doctypes, bench commands |
| `examples.md` | 2.11.2 | Complete werkende voorbeelden |
| `anti-patterns.md` | 2.11.2 | Fouten en correcties |

---

## Exit Criteria Fase 2.11

### 2.11.1 Exit Criteria:
- [ ] SKILL.md NL versie met secties 1-4, 9 verwerkt
- [ ] SKILL.md EN versie
- [ ] Reference: scheduler-events.md
- [ ] Reference: enqueue-api.md
- [ ] Reference: queues.md
- [ ] Cron syntax cheatsheet opgenomen
- [ ] "bench migrate" waarschuwing duidelijk gedocumenteerd

### 2.11.2 Exit Criteria:
- [ ] SKILL.md NL aangevuld met secties 5-8, 10-12
- [ ] SKILL.md EN aangevuld
- [ ] Reference: error-handling.md
- [ ] Reference: monitoring.md
- [ ] Reference: examples.md
- [ ] Reference: anti-patterns.md
- [ ] v14â†’v15 migratie gedocumenteerd (job_name deprecation)
- [ ] Totale skill < 500 regels
- [ ] Gevalideerd met quick_validate.py
- [ ] NL en EN .skill packages

---

# Samenvatting Alle Wijzigingen

## Impact op Nummering

| Origineel | Nieuw | Focus |
|-----------|-------|-------|
| Stap 2.10 | Stap 2.10.1 | Jinja Core Templating |
| - | Stap 2.10.2 | Jinja Advanced & Custom |
| Stap 2.11 | Stap 2.11.1 | Scheduler Basics |
| - | Stap 2.11.2 | Scheduler Advanced |
| Stap 2.12 | Stap 2.12 | Ongewijzigd (reeds gesplitst in 2.12.1 + 2.12.2) |

## Dependencies

| Fase | Vereist | Zelfstandig uitvoerbaar |
|------|---------|-------------------------|
| 2.10.1 | Geen | âœ… Ja |
| 2.10.2 | 2.10.1 output | âŒ Nee |
| 2.11.1 | Geen | âœ… Ja |
| 2.11.2 | 2.11.1 output | âŒ Nee |

## Uploads Vereist

Conform `masterplan-skill-uploads.md`:

| Fase | Uploads |
|------|---------|
| 2.10.1 | âœ“ Geen |
| 2.10.2 | âœ“ Geen (output 2.10.1 in zelfde project) |
| 2.11.1 | âœ“ Geen |
| 2.11.2 | âœ“ Geen (output 2.11.1 in zelfde project) |

---

## Totaal Overzicht Fase 2 Na Alle Opsplitsingen

| Stap | Skill | Status |
|------|-------|--------|
| 2.1 | Research Client Scripts | âœ… Compleet |
| 2.2 | Research Server Scripts | âœ… Compleet |
| 2.3 | Research Whitelisted Methods | âœ… Compleet |
| 2.4 | Research Jinja Templates | âœ… Compleet |
| 2.5 | Research Scheduler | âœ… Compleet |
| 2.6 | Research Custom App | âœ… Compleet |
| 2.7.1 | Controllers - Basics | âœ… Compleet |
| 2.7.2 | Controllers - Advanced | âœ… Compleet |
| 2.8.1 | Hooks - Events | âœ… Compleet |
| 2.8.2 | Hooks - Configuration | âœ… Compleet |
| 2.9.1 | Whitelisted - Core API | ðŸ”œ Volgende |
| 2.9.2 | Whitelisted - Security | â³ Wacht op 2.9.1 |
| 2.10.1 | Jinja - Core Templating | â³ Wacht op 2.9.2 |
| 2.10.2 | Jinja - Advanced | â³ Wacht op 2.10.1 |
| 2.11.1 | Scheduler - Basics | â³ Wacht op 2.10.2 |
| 2.11.2 | Scheduler - Advanced | â³ Wacht op 2.11.1 |
| 2.12.1 | Custom App - Structure | â³ Wacht op 2.11.2 |
| 2.12.2 | Custom App - Data | â³ Wacht op 2.12.1 |

---

## Noot: Consistentie Opsplitsingslogica

Alle opsplitsingen volgen hetzelfde patroon:

| Deel A | Deel B |
|--------|--------|
| Fundamenten ("hoe werkt het?") | Geavanceerd ("hoe maak ik het robuust?") |
| Basis syntax en API | Security, errors, best practices |
| Kan zelfstandig functioneren | Bouwt voort op Deel A |
| ~50% van reference files | ~50% van reference files |

Dit zorgt voor:
1. **Voorspelbare structuur** - elke skill volgt zelfde opbouw
2. **Natuurlijke leerflow** - basis â†’ geavanceerd
3. **Beheersbare gesprekken** - â‰¤5 reference files per sessie
4. **Parallelle werking mogelijk** - Deel A's kunnen parallel worden gemaakt
