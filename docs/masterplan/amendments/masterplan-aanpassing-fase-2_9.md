# Masterplan Aanpassing: Opsplitsing Fase 2.9

> **Datum**: 13 januari 2026  
> **Betreft**: Fase 2.9 (CreÃ«er erpnext-syntax-whitelisted) opsplitsen in 2.9.1 en 2.9.2

---

## Reden voor Opsplitsing

De `erpnext-syntax-whitelisted` skill bevat uitgebreide content:
- **10 secties** in het research document (834 regels)
- **8 reference bestanden** gepland
- Complexe onderwerpen die zowel API basics als security patterns beslaan
- Logische scheiding mogelijk tussen "hoe APIs maken" en "hoe APIs beveiligen"

### Criteria Check

| Criterium | Drempel | Werkelijk | Status |
|-----------|---------|-----------|--------|
| Research regels | â‰¤700 | 834 | âš ï¸ Overschreden |
| Reference files | â‰¤5 | 8 | âš ï¸ Overschreden |
| Secties | â‰¤8-10 | 10 | âš¡ Borderline |

**Conclusie**: 2 van 3 criteria overschreden â†’ opsplitsing conform vastgestelde regels.

### Impact op Nummering

| Origineel | Nieuw |
|-----------|-------|
| Stap 2.9: CreÃ«er erpnext-syntax-whitelisted | Stap 2.9.1: CreÃ«er skill Deel A (Core API) |
| - | Stap 2.9.2: CreÃ«er skill Deel B (Security & Errors) |
| Stap 2.10-2.12: Overige skills | Stap 2.10-2.12: Ongewijzigd |

---

## Inhoud Research Document (research-whitelisted-methods.md)

Het research document bevat 10 secties:

| # | Sectie | Regels | Naar Deel |
|---|--------|--------|-----------|
| 1 | DECORATOR OPTIES | 22-88 | 2.9.1 |
| 2 | PARAMETER HANDLING | 91-163 | 2.9.1 |
| 3 | RESPONSE PATTERNS | 166-270 | 2.9.1 |
| 4 | PERMISSIONS | 272-379 | 2.9.2 |
| 5 | AANROEPEN VANUIT CLIENT | 382-512 | 2.9.1 |
| 6 | ERROR HANDLING | 515-618 | 2.9.2 |
| 7 | VERSIE VERSCHILLEN | 622-643 | 2.9.2 |
| 8 | BEST PRACTICES | 646-747 | 2.9.2 |
| 9 | ANTI-PATTERNS | 750-806 | 2.9.2 |
| 10 | SAMENVATTING VOOR SKILL CREATIE | 810-834 | Beide |

---

## Nieuwe Fase Definities

### Stap 2.9.1: CreÃ«er erpnext-syntax-whitelisted - Core API

**Focus**: Hoe Whitelisted Methods werken - de fundamenten van API creatie

**Onderzoeksonderwerpen uit research document**:
1. DECORATOR OPTIES: @frappe.whitelist() parameters (allow_guest, methods, xss_safe)
2. PARAMETER HANDLING: Request parameters, type conversion, JSON parsing, type annotations (v15+)
3. RESPONSE PATTERNS: Return values, frappe.response object, response types, file downloads, HTTP status codes
5. AANROEPEN VANUIT CLIENT: frappe.call(), frm.call(), REST API calls, endpoints

**Output reference bestanden**:
- `decorator-options.md` - Alle decorator parameters met voorbeelden
- `parameter-handling.md` - Request parameters en type conversion
- `response-patterns.md` - Response types en structuren
- `client-calls.md` - frappe.call() en frm.call() voorbeelden

---

### Stap 2.9.2: CreÃ«er erpnext-syntax-whitelisted - Security & Errors

**Focus**: Beveiliging, foutafhandeling en best practices voor productie-klare APIs

**Onderzoeksonderwerpen uit research document**:
4. PERMISSIONS: frappe.has_permission(), frappe.only_for(), security overwegingen
6. ERROR HANDLING: frappe.throw(), exception types, error logging, response structuren
7. VERSIE VERSCHILLEN: v14 vs v15 features (API v2, type validation, rate limiting)
8. BEST PRACTICES: Permission checks, input validatie, HTTP methods, documentatie, rate limiting
9. ANTI-PATTERNS: Security fouten, SQL injection, sensitive data in errors

**Output reference bestanden**:
- `permission-patterns.md` - Security best practices en permission checks
- `error-handling.md` - Error patterns en exception types
- `examples.md` - Complete werkende API voorbeelden
- `anti-patterns.md` - Wat te vermijden met correcte alternatieven

---

## Aangepaste Prompts

### PROMPT FASE 2.9.1 - CREÃ‹ER SKILL: erpnext-syntax-whitelisted (CORE API)

```
â”Œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”
â”‚ PROMPT FASE 2.9.1 - CREÃ‹ER SKILL: erpnext-syntax-whitelisted (A)   â”‚
â”œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”¤
â”‚                                                                     â”‚
â”‚ Gebruik research-whitelisted-methods.md SECTIES 1-3 en 5 om het    â”‚
â”‚ EERSTE DEEL van de 'erpnext-syntax-whitelisted' skill te maken.    â”‚
â”‚                                                                     â”‚
â”‚ VEREISTEN:                                                          â”‚
â”‚ 1. Volg exact de Anthropic skill-creator richtlijnen               â”‚
â”‚ 2. Maak TWEE versies: NL en EN                                     â”‚
â”‚ 3. SKILL.md < 500 regels                                           â”‚
â”‚                                                                     â”‚
â”‚ TE VERWERKEN SECTIES:                                               â”‚
â”‚ â€¢ 1. DECORATOR OPTIES - @frappe.whitelist() parameters             â”‚
â”‚ â€¢ 2. PARAMETER HANDLING - request params, type conversion          â”‚
â”‚ â€¢ 3. RESPONSE PATTERNS - return values, frappe.response            â”‚
â”‚ â€¢ 5. AANROEPEN VANUIT CLIENT - frappe.call(), frm.call()          â”‚
â”‚                                                                     â”‚
â”‚ TE MAKEN REFERENCE BESTANDEN:                                       â”‚
â”‚ references/                                                         â”‚
â”‚ â”œâ”€â”€ decorator-options.md (alle decorator parameters)               â”‚
â”‚ â”œâ”€â”€ parameter-handling.md (request parameters)                     â”‚
â”‚ â”œâ”€â”€ response-patterns.md (response types)                          â”‚
â”‚ â””â”€â”€ client-calls.md (JS aanroep patronen)                          â”‚
â”‚                                                                     â”‚
â”‚ SKILL.MD FOCUS:                                                     â”‚
â”‚ - Frontmatter met triggers voor API/whitelisted vragen             â”‚
â”‚ - Quick reference: basis whitelisted method template               â”‚
â”‚ - Decision tree: "welke decorator opties gebruik ik?"              â”‚
â”‚ - Client-server flow diagram (tekst-based)                         â”‚
â”‚ - Verwijzingen naar reference files                                 â”‚
â”‚                                                                     â”‚
â”‚ LET OP: Dit is Deel A. Secties 4 en 6-9 komen in Deel B (2.9.2).  â”‚
â”‚                                                                     â”‚
â””â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”˜
```

### PROMPT FASE 2.9.2 - CREÃ‹ER SKILL: erpnext-syntax-whitelisted (SECURITY & ERRORS)

```
â”Œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”
â”‚ PROMPT FASE 2.9.2 - CREÃ‹ER SKILL: erpnext-syntax-whitelisted (B)   â”‚
â”œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”¤
â”‚                                                                     â”‚
â”‚ Gebruik research-whitelisted-methods.md SECTIES 4 en 6-9 om het    â”‚
â”‚ TWEEDE DEEL van de 'erpnext-syntax-whitelisted' skill te maken.    â”‚
â”‚                                                                     â”‚
â”‚ VOORWAARDE: Deel A (2.9.1) is compleet.                            â”‚
â”‚                                                                     â”‚
â”‚ TE VERWERKEN SECTIES:                                               â”‚
â”‚ â€¢ 4. PERMISSIONS - frappe.has_permission(), frappe.only_for()      â”‚
â”‚ â€¢ 6. ERROR HANDLING - frappe.throw(), exception types              â”‚
â”‚ â€¢ 7. VERSIE VERSCHILLEN - v14 vs v15 (API v2, rate limiting)       â”‚
â”‚ â€¢ 8. BEST PRACTICES - security, validation, documentatie           â”‚
â”‚ â€¢ 9. ANTI-PATTERNS - security fouten, SQL injection                â”‚
â”‚                                                                     â”‚
â”‚ TE MAKEN REFERENCE BESTANDEN:                                       â”‚
â”‚ references/                                                         â”‚
â”‚ â”œâ”€â”€ permission-patterns.md (security best practices)               â”‚
â”‚ â”œâ”€â”€ error-handling.md (error patterns)                             â”‚
â”‚ â”œâ”€â”€ examples.md (complete werkende APIs)                           â”‚
â”‚ â””â”€â”€ anti-patterns.md (fouten en correcties)                        â”‚
â”‚                                                                     â”‚
â”‚ SKILL.MD AFRONDING:                                                 â”‚
â”‚ - Voeg security checklist sectie toe                               â”‚
â”‚ - Voeg error handling patronen toe                                 â”‚
â”‚ - Integreer best practices in beslisboom                           â”‚
â”‚ - Voeg versie-specifieke notities toe waar relevant                â”‚
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

## Reference Bestanden Verdeling

### Totaaloverzicht (8 bestanden)

| Bestand | Aangemaakt in | Inhoud |
|---------|---------------|--------|
| `decorator-options.md` | 2.9.1 | @frappe.whitelist() parameters |
| `parameter-handling.md` | 2.9.1 | Request parameters, type conversion |
| `response-patterns.md` | 2.9.1 | Response types, frappe.response |
| `client-calls.md` | 2.9.1 | frappe.call(), frm.call(), REST |
| `permission-patterns.md` | 2.9.2 | Security checks, role restrictions |
| `error-handling.md` | 2.9.2 | Error patterns, exception types |
| `examples.md` | 2.9.2 | Complete werkende API voorbeelden |
| `anti-patterns.md` | 2.9.2 | Security fouten en correcties |

### Relatie met Controllers Skill

De `erpnext-syntax-controllers` skill (fase 2.7) behandelt `@frappe.whitelist()` binnen controller context (frm.call naar controller methods). Deze skill focust op **standalone API methods** - de volledige API laag los van DocType controllers.

**Overlap intentioneel vermijden**:
- Controllers skill: `frm.call('method_name')` â†’ controller method
- Whitelisted skill: `frappe.call({method: 'app.module.function'})` â†’ standalone API

---

## Aangepaste Exit Criteria

### Per Sub-Fase:

**2.9.1 Exit Criteria**:
- [ ] SKILL.md NL versie met secties 1-3, 5 verwerkt
- [ ] SKILL.md EN versie
- [ ] Reference: decorator-options.md
- [ ] Reference: parameter-handling.md
- [ ] Reference: response-patterns.md
- [ ] Reference: client-calls.md
- [ ] Decision tree voor decorator opties

**2.9.2 Exit Criteria**:
- [ ] SKILL.md NL aangevuld met secties 4, 6-9
- [ ] SKILL.md EN aangevuld
- [ ] Reference: permission-patterns.md
- [ ] Reference: error-handling.md
- [ ] Reference: examples.md
- [ ] Reference: anti-patterns.md
- [ ] Security checklist opgenomen
- [ ] Totale skill < 500 regels
- [ ] Gevalideerd met quick_validate.py
- [ ] NL en EN .skill packages

---

## Samenvatting Wijzigingen

| Item | Was | Wordt |
|------|-----|-------|
| Stap 2.9 | 1 skill creatie stap | 2.9.1 + 2.9.2 |
| Secties verwerkt | 10 in Ã©Ã©n keer | 4 + 6 (gesplitst) |
| Reference files | 8 in Ã©Ã©n keer | 4 + 4 (gesplitst) |
| Dependencies | Geen | 2.9.2 vereist 2.9.1 |

---

## Noot over Dependencies

De delen bouwen op elkaar voort:
- **2.9.1** kan zelfstandig worden uitgevoerd
- **2.9.2** vereist dat 2.9.1 compleet is (skill bestanden worden samengevoegd)

### Uitvoering in aparte gesprekken

Elk deel kan in een apart gesprek worden uitgevoerd:

1. **Gesprek 2.9.1**: 
   - Lees research-whitelisted-methods.md
   - Focus op secties 1-3, 5 (Core API)
   - Maak SKILL.md (basis structuur) + 4 reference files
   - Output: incomplete skill (alleen API basics)

2. **Gesprek 2.9.2**:
   - Laad output van 2.9.1
   - Lees research-whitelisted-methods.md secties 4, 6-9
   - Vul SKILL.md aan + maak 4 extra reference files
   - Valideer en package complete skill

---

## Relatie met Andere Fases

| Fase | Status | Afhankelijkheid |
|------|--------|-----------------|
| 2.3 Research Whitelisted | âœ… Compleet | research-whitelisted-methods.md |
| 2.9.1 Skill Core API | ðŸ“œ Uit te voeren | Research document |
| 2.9.2 Skill Security | â³ Wacht op 2.9.1 | 2.9.1 output + research document |
| 2.10 Jinja Skill | â³ Ongewijzigd | Geen dependency op 2.9 |

---

## Uploads Vereist

Conform `masterplan-skill-uploads.md`:

| Fase | Uploads |
|------|---------|
| 2.9.1 | âœ” Geen |
| 2.9.2 | âœ” Geen (output 2.9.1 in zelfde project) |

---

## Noot: Monitoring Volgende Fases

Na deze opsplitsing, de status van overige fases:

| Fase | Research Regels | Reference Files | Actie |
|------|-----------------|-----------------|-------|
| 2.10 (Jinja) | ~500 (geschat) | ~4 | Monitor |
| 2.11 (Scheduler) | ~450 (geschat) | ~4 | Monitor |
| 2.12 (Custom App) | Reeds gesplitst | 3 + 5 | âœ… |

Aanbeveling: bij start 2.10 en 2.11 eerst research document omvang beoordelen.
