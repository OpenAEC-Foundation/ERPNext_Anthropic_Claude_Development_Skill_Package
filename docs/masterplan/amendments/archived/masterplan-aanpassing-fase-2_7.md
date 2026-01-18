# Masterplan Aanpassing: Opsplitsing Fase 2.7

> **Datum**: 13 januari 2026  
> **Betreft**: Fase 2.7 (CreÃ«er erpnext-syntax-controllers) opsplitsen in 2.7.1 en 2.7.2

---

## Reden voor Opsplitsing

De `erpnext-syntax-controllers` skill bevat uitgebreide content:
- **12 secties** in het research document (744 regels)
- **5 reference bestanden** gepland
- Complexe onderwerpen die zowel basics als geavanceerde patronen beslaan
- Logische scheiding mogelijk tussen "hoe controllers werken" en "hoe controllers uitbreiden"

### Impact op Nummering

| Origineel | Nieuw |
|-----------|-------|
| Stap 2.7: CreÃ«er erpnext-syntax-controllers | Stap 2.7.1: CreÃ«er skill Deel A (Basics) |
| - | Stap 2.7.2: CreÃ«er skill Deel B (Patterns) |
| Stap 2.8-2.11: Overige skills | Stap 2.8-2.11: Ongewijzigd |

---

## Inhoud Research Document (research-document-controllers.md)

Het research document bevat 12 secties:

| # | Sectie | Naar Deel |
|---|--------|-----------|
| 1 | CLASS STRUCTUUR | 2.7.1 |
| 2 | LIFECYCLE METHODS | 2.7.1 |
| 3 | SPECIALE METHODS | 2.7.1 |
| 4 | FLAGS SYSTEEM | 2.7.1 |
| 5 | WHITELISTED METHODS | 2.7.1 |
| 6 | AUTONAME PATTERNS | 2.7.1 |
| 7 | CONTROLLER OVERRIDE | 2.7.2 |
| 8 | SUBMITTABLE DOCUMENTS | 2.7.2 |
| 9 | VIRTUAL DOCTYPES | 2.7.2 |
| 10 | BEST PRACTICES | 2.7.2 |
| 11 | VERSIE VERSCHILLEN | 2.7.2 |
| 12 | ANTI-PATTERNS | 2.7.2 |

---

## Nieuwe Fase Definities

### Stap 2.7.1: CreÃ«er erpnext-syntax-controllers - Basics

**Focus**: Hoe Document Controllers werken - de fundamenten

**Onderzoeksonderwerpen uit research document**:
1. CLASS STRUCTUUR: Inheritance, naming conventions, type annotations (v15+)
2. LIFECYCLE METHODS: Complete EVENT_MAP met execution order
3. SPECIALE METHODS: get_doc_before_save, db_insert/update, run_method, reload, as_dict, queue_action, notify_update, add_comment
4. FLAGS SYSTEEM: Permission bypass, validation bypass, custom flags
5. WHITELISTED METHODS: @frappe.whitelist() decorator en aanroep patronen
6. AUTONAME PATTERNS: DocType configuratie en programmatische naming

**Output reference bestanden**:
- `lifecycle-methods.md` - Alle hooks met execution order diagrams
- `methods.md` - Alle doc.* methodes met signatures en voorbeelden
- `flags.md` - Flags systeem documentatie

---

### Stap 2.7.2: CreÃ«er erpnext-syntax-controllers - Patterns

**Focus**: Geavanceerde patronen voor uitbreiden en specialiseren van controllers

**Onderzoeksonderwerpen uit research document**:
7. CONTROLLER OVERRIDE: override_doctype_class en doc_events hooks
8. SUBMITTABLE DOCUMENTS: docstatus lifecycle (0â†’1â†’2)
9. VIRTUAL DOCTYPES: DocTypes zonder database tabel
10. BEST PRACTICES: Validation patterns, geen commits, permission checks
11. VERSIE VERSCHILLEN: v14 vs v15 features
12. ANTI-PATTERNS: Execution order aannames, recursive saves, heavy operations

**Output reference bestanden**:
- `examples.md` - Complete werkende controller voorbeelden
- `anti-patterns.md` - Wat te vermijden met correcte alternatieven

---

## Aangepaste Prompts

### PROMPT FASE 2.7.1 - CREÃ‹ER SKILL: erpnext-syntax-controllers (BASICS)

```
â”Œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”
â”‚ PROMPT FASE 2.7.1 - CREÃ‹ER SKILL: erpnext-syntax-controllers (A)   â”‚
â”œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”¤
â”‚                                                                     â”‚
â”‚ Gebruik research-document-controllers.md SECTIES 1-6 om het        â”‚
â”‚ EERSTE DEEL van de 'erpnext-syntax-controllers' skill te maken.    â”‚
â”‚                                                                     â”‚
â”‚ VEREISTEN:                                                          â”‚
â”‚ 1. Volg exact de Anthropic skill-creator richtlijnen               â”‚
â”‚ 2. Maak TWEE versies: NL en EN                                     â”‚
â”‚ 3. SKILL.md < 500 regels                                           â”‚
â”‚                                                                     â”‚
â”‚ TE VERWERKEN SECTIES:                                               â”‚
â”‚ â€¢ 1. CLASS STRUCTUUR - inheritance, naming, type annotations       â”‚
â”‚ â€¢ 2. LIFECYCLE METHODS - complete EVENT_MAP, execution order       â”‚
â”‚ â€¢ 3. SPECIALE METHODS - doc.* methodes                             â”‚
â”‚ â€¢ 4. FLAGS SYSTEEM - bypass flags, custom flags                    â”‚
â”‚ â€¢ 5. WHITELISTED METHODS - @frappe.whitelist() patterns           â”‚
â”‚ â€¢ 6. AUTONAME PATTERNS - naming configuratie                       â”‚
â”‚                                                                     â”‚
â”‚ TE MAKEN REFERENCE BESTANDEN:                                       â”‚
â”‚ references/                                                         â”‚
â”‚ â”œâ”€â”€ lifecycle-methods.md (hooks + execution order)                 â”‚
â”‚ â”œâ”€â”€ methods.md (alle doc.* methodes)                               â”‚
â”‚ â””â”€â”€ flags.md (flags systeem)                                       â”‚
â”‚                                                                     â”‚
â”‚ SKILL.MD FOCUS:                                                     â”‚
â”‚ - Frontmatter met triggers voor controller vragen                  â”‚
â”‚ - Quick reference: basis controller template                       â”‚
â”‚ - Decision tree: "welke hook gebruik ik wanneer?"                  â”‚
â”‚ - Lifecycle diagram (tekst-based)                                  â”‚
â”‚ - Verwijzingen naar reference files                                 â”‚
â”‚                                                                     â”‚
â”‚ LET OP: Dit is Deel A. Secties 7-12 komen in Deel B (2.7.2).       â”‚
â”‚                                                                     â”‚
â””â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”˜
```

### PROMPT FASE 2.7.2 - CREÃ‹ER SKILL: erpnext-syntax-controllers (PATTERNS)

```
â”Œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”
â”‚ PROMPT FASE 2.7.2 - CREÃ‹ER SKILL: erpnext-syntax-controllers (B)   â”‚
â”œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”¤
â”‚                                                                     â”‚
â”‚ Gebruik research-document-controllers.md SECTIES 7-12 om het       â”‚
â”‚ TWEEDE DEEL van de 'erpnext-syntax-controllers' skill te maken.    â”‚
â”‚                                                                     â”‚
â”‚ VOORWAARDE: Deel A (2.7.1) is compleet.                            â”‚
â”‚                                                                     â”‚
â”‚ TE VERWERKEN SECTIES:                                               â”‚
â”‚ â€¢ 7. CONTROLLER OVERRIDE - override_doctype_class, doc_events      â”‚
â”‚ â€¢ 8. SUBMITTABLE DOCUMENTS - docstatus lifecycle                   â”‚
â”‚ â€¢ 9. VIRTUAL DOCTYPES - custom data sources                        â”‚
â”‚ â€¢ 10. BEST PRACTICES - validation, commits, permissions            â”‚
â”‚ â€¢ 11. VERSIE VERSCHILLEN - v14 vs v15                              â”‚
â”‚ â€¢ 12. ANTI-PATTERNS - wat te vermijden                             â”‚
â”‚                                                                     â”‚
â”‚ TE MAKEN REFERENCE BESTANDEN:                                       â”‚
â”‚ references/                                                         â”‚
â”‚ â”œâ”€â”€ examples.md (complete werkende controllers)                    â”‚
â”‚ â””â”€â”€ anti-patterns.md (fouten en correcties)                        â”‚
â”‚                                                                     â”‚
â”‚ SKILL.MD AFRONDING:                                                 â”‚
â”‚ - Voeg override patterns sectie toe                                â”‚
â”‚ - Voeg submittable/virtual DocType secties toe                     â”‚
â”‚ - Integreer best practices in beslisboom                           â”‚
â”‚ - Voeg versie-specifieke notities toe waar relevant                â”‚
â”‚ - Valideer totale skill < 500 regels                               â”‚
â”‚                                                                     â”‚
â”‚ PACKAGING:                                                          â”‚
â”‚ - Combineer alle 5 reference bestanden                             â”‚
â”‚ - Valideer met quick_validate.py                                   â”‚
â”‚ - Package NL en EN versies als .skill bestanden                    â”‚
â”‚                                                                     â”‚
â””â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”˜
```

---

## Reference Bestanden Verdeling

### Totaaloverzicht (5 bestanden)

| Bestand | Aangemaakt in | Inhoud |
|---------|---------------|--------|
| `lifecycle-methods.md` | 2.7.1 | Hooks, EVENT_MAP, execution order |
| `methods.md` | 2.7.1 | Alle doc.* methodes met signatures |
| `flags.md` | 2.7.1 | Flags systeem (doc.flags, frappe.flags) |
| `examples.md` | 2.7.2 | Complete controllers incl. override, submittable |
| `anti-patterns.md` | 2.7.2 | Fouten en correcte alternatieven |

### Noot over Whitelisted Methods

Sectie 5 (Whitelisted Methods) behandelt de decorator binnen controllers. De standalone whitelisted API methods worden behandeld in een aparte skill (`erpnext-syntax-whitelisted` in fase 2.9).

---

## Aangepaste Exit Criteria

### Per Sub-Fase:

**2.7.1 Exit Criteria**:
- [ ] SKILL.md NL versie met secties 1-6 verwerkt
- [ ] SKILL.md EN versie
- [ ] Reference: lifecycle-methods.md
- [ ] Reference: methods.md
- [ ] Reference: flags.md
- [ ] Decision tree voor hook selectie

**2.7.2 Exit Criteria**:
- [ ] SKILL.md NL aangevuld met secties 7-12
- [ ] SKILL.md EN aangevuld
- [ ] Reference: examples.md
- [ ] Reference: anti-patterns.md
- [ ] Totale skill < 500 regels
- [ ] Gevalideerd met quick_validate.py
- [ ] NL en EN .skill packages

---

## Samenvatting Wijzigingen

| Item | Was | Wordt |
|------|-----|-------|
| Stap 2.7 | 1 skill creatie stap | 2.7.1 + 2.7.2 |
| Secties verwerkt | 12 in Ã©Ã©n keer | 6 + 6 (gesplitst) |
| Reference files | 5 in Ã©Ã©n keer | 3 + 2 (gesplitst) |
| Dependencies | Geen | 2.7.2 vereist 2.7.1 |

---

## Noot over Dependencies

De delen bouwen op elkaar voort:
- **2.7.1** kan zelfstandig worden uitgevoerd
- **2.7.2** vereist dat 2.7.1 compleet is (skill bestanden worden samengevoegd)

### Uitvoering in aparte gesprekken

Elk deel kan in een apart gesprek worden uitgevoerd:

1. **Gesprek 2.7.1**: 
   - Lees research-document-controllers.md
   - Focus op secties 1-6
   - Maak SKILL.md (basis structuur) + 3 reference files
   - Output: incomplete skill (alleen basics)

2. **Gesprek 2.7.2**:
   - Laad output van 2.7.1
   - Lees research-document-controllers.md secties 7-12
   - Vul SKILL.md aan + maak 2 extra reference files
   - Valideer en package complete skill

---

## Relatie met Andere Fases

| Fase | Status | Afhankelijkheid |
|------|--------|-----------------|
| 2.1 Research Controllers | âœ… Compleet | research-document-controllers.md |
| 2.7.1 Skill Basics | ðŸ”œ Uit te voeren | Research document |
| 2.7.2 Skill Patterns | â³ Wacht op 2.7.1 | 2.7.1 output + research document |
| 2.8 Hooks Skill | â³ Ongewijzigd | Geen dependency op 2.7 |
