# Mid-Project Review & Masterplan Amendment 5 (v2)

> **Datum**: 17 januari 2026  
> **Project**: ERPNext Skills Package  
> **Versie**: 2 - Bijgewerkt na Anthropic tooling analyse

---

## Deel 1: Mid-Project Review

### 1.1 Voortgang Samenvatting

| Categorie | Gepland | Voltooid | Percentage |
|-----------|:-------:|:--------:|:----------:|
| Research documenten | 13 | 13 | 100% |
| Syntax Skills | 8 | 8 | 100% |
| Core Skills | 3 | 3 | 100% |
| Implementation Skills | 8 | 1 | 12.5% |
| Error Handling Skills | 7 | 0 | 0% |
| Agents | 2 | 0 | 0% |
| **TOTAAL** | **41** | **25** | **~61%** |

### 1.2 Kritieke Ontdekking: Tooling Incompatibiliteit

**Tijdens deze review ontdekten we dat onze skill structuur NIET compatibel is met Anthropic's officiële tooling.**

**Het probleem:**
```
# Onze structuur (FOUT):
skill-name/
├── NL/
│   └── SKILL.md     ← package_skill.py vindt dit NIET
└── EN/
    └── SKILL.md

# Anthropic verwacht:
skill-name/
└── SKILL.md         ← DIRECT in skill folder root
```

**Impact:**
- `quick_validate.py` faalt
- `package_skill.py` faalt  
- Handmatige workarounds nodig voor packaging
- Niet toekomstbestendig

### 1.3 Wat Gaat Goed ✅

1. **Content kwaliteit is hoog** - Research grondig, skills deterministisch
2. **Frontmatter correct** - name + description conform spec
3. **Progressive disclosure** - SKILL.md lean, details in references/
4. **GitHub workflow werkt** - Alles wordt gepusht

### 1.4 Wat Moet Veranderen ❌

1. **Directory structuur** - Van NL/EN subfolders naar aparte skills
2. **Skill naming** - Taal suffix in naam (`-nl`, `-en`)
3. **Package strategie** - Conform officiële tooling

---

## Deel 2: Nieuwe Directory Structuur (Anthropic Conform)

### 2.1 Officiële Anthropic Skill Structuur

```
skill-name/
├── SKILL.md              ← VERPLICHT in root
├── references/           ← On-demand documentatie
│   ├── methods.md
│   ├── examples.md
│   └── anti-patterns.md
├── scripts/              ← Optioneel: uitvoerbare code
└── assets/               ← Optioneel: templates, images
```

**Validatie regels (uit quick_validate.py):**
- SKILL.md MOET in root staan
- Name: kebab-case, max 64 chars
- Description: max 1024 chars, geen < of >
- Frontmatter: alleen name, description, license, metadata, compatibility, allowed-tools

### 2.2 Nieuwe Structuur voor Meertalige Skills

**Elke taalversie is een APARTE skill:**

```
ERPNext_Anthropic_Claude_Development_Skill_Package/
│
├── docs/
│   ├── masterplan/
│   │   └── amendments/
│   └── research/
│
└── skills/
    ├── syntax/
    │   ├── erpnext-syntax-clientscripts-nl/
    │   │   ├── SKILL.md
    │   │   └── references/
    │   │       ├── methods.md
    │   │       ├── events.md
    │   │       ├── examples.md
    │   │       └── anti-patterns.md
    │   │
    │   ├── erpnext-syntax-clientscripts-en/
    │   │   ├── SKILL.md
    │   │   └── references/
    │   │       └── [zelfde structuur]
    │   │
    │   ├── erpnext-syntax-serverscripts-nl/
    │   ├── erpnext-syntax-serverscripts-en/
    │   └── ... (16 syntax skill folders totaal)
    │
    ├── core/
    │   ├── erpnext-database-nl/
    │   ├── erpnext-database-en/
    │   ├── erpnext-permissions-nl/
    │   ├── erpnext-permissions-en/
    │   ├── erpnext-api-patterns-nl/
    │   └── erpnext-api-patterns-en/
    │
    ├── impl/
    │   ├── erpnext-impl-clientscripts-nl/
    │   ├── erpnext-impl-clientscripts-en/
    │   └── ... (16 impl skill folders totaal)
    │
    ├── errors/
    │   └── ... (14 error skill folders totaal)
    │
    ├── agents/
    │   ├── erpnext-interpreter-nl/
    │   ├── erpnext-interpreter-en/
    │   ├── erpnext-validator-nl/
    │   └── erpnext-validator-en/
    │
    └── packaged/
        ├── erpnext-syntax-clientscripts-nl.skill
        ├── erpnext-syntax-clientscripts-en.skill
        └── ... (56 .skill packages totaal)
```

### 2.3 Naming Conventions

| Element | Convention | Voorbeeld |
|---------|------------|-----------|
| Skill folder | `{prefix}-{type}-{topic}-{lang}` | `erpnext-syntax-clientscripts-nl` |
| Package file | `{folder-name}.skill` | `erpnext-syntax-clientscripts-nl.skill` |
| Reference files | `{descriptive-name}.md` | `methods.md`, `examples.md` |

**Prefixes:**
- `erpnext-syntax-*` - Syntax skills
- `erpnext-impl-*` - Implementation skills
- `erpnext-errors-*` - Error handling skills
- `erpnext-*` - Core skills (geen type prefix)
- `erpnext-interpreter-*`, `erpnext-validator-*` - Agents

**Taal suffixes:**
- `-nl` - Nederlandse versie
- `-en` - Engelse versie

### 2.4 Folder Totalen

| Categorie | Skills | × Talen | Folders |
|-----------|:------:|:-------:|:-------:|
| Syntax | 8 | 2 | 16 |
| Core | 3 | 2 | 6 |
| Implementation | 8 | 2 | 16 |
| Error Handling | 7 | 2 | 14 |
| Agents | 2 | 2 | 4 |
| **TOTAAL** | **28** | **2** | **56** |

---

## Deel 3: Migratie Plan

### 3.1 Overzicht Huidige vs Nieuwe Locaties

**Syntax Skills:**
| Huidig | Nieuw |
|--------|-------|
| `skills/source/erpnext-syntax-clientscripts/NL/` | `skills/syntax/erpnext-syntax-clientscripts-nl/` |
| `skills/source/erpnext-syntax-clientscripts/EN/` | `skills/syntax/erpnext-syntax-clientscripts-en/` |

**Core Skills:**
| Huidig | Nieuw |
|--------|-------|
| `skills/NL/CORE/erpnext-database/` | `skills/core/erpnext-database-nl/` |
| `skills/EN/CORE/erpnext-database/` | `skills/core/erpnext-database-en/` |

### 3.2 Migratie Stappen

```
┌─────────────────────────────────────────────────────────────────────┐
│ MIGRATIE PROCEDURE                                                  │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│ STAP 1: Nieuwe structuur aanmaken                                  │
│ ─────────────────────────────────                                  │
│ • Maak skills/syntax/, skills/core/, etc. folders                  │
│ • Maak elke skill folder met -nl/-en suffix                        │
│                                                                     │
│ STAP 2: Content verplaatsen                                        │
│ ─────────────────────────────                                      │
│ • Verplaats SKILL.md naar nieuwe folder ROOT                       │
│ • Verplaats references/ folder mee                                 │
│ • Verifieer dat SKILL.md DIRECT in skill folder staat              │
│                                                                     │
│ STAP 3: Valideren                                                  │
│ ────────────────                                                   │
│ • Run quick_validate.py op ELKE skill folder                       │
│ • Fix eventuele validation errors                                  │
│                                                                     │
│ STAP 4: Repackagen                                                 │
│ ─────────────────                                                  │
│ • Run package_skill.py op elke skill                               │
│ • Verplaats .skill files naar skills/packaged/                     │
│                                                                     │
│ STAP 5: Opruimen                                                   │
│ ───────────────                                                    │
│ • Verwijder oude folder structuur                                  │
│ • Verwijder README.md uit skills/ (niet toegestaan per Anthropic)  │
│ • Update alle documentatie verwijzingen                            │
│                                                                     │
│ STAP 6: Pushen en verifiëren                                       │
│ ──────────────────────────────                                     │
│ • Push alle wijzigingen naar GitHub                                │
│ • Verifieer structuur in GitHub web interface                      │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
```

### 3.3 Geschatte Tijd

| Stap | Geschatte tijd |
|------|----------------|
| Nieuwe structuur aanmaken | 10 min |
| Content verplaatsen (25 skills × 2) | 45 min |
| Valideren | 15 min |
| Repackagen | 20 min |
| Opruimen | 10 min |
| Pushen en verifiëren | 15 min |
| **TOTAAL** | **~2 uur** |

---

## Deel 4: Checkpoints Systeem

### 4.1 Verplichte Checkpoints

```
┌─────────────────────────────────────────────────────────────────────┐
│ CHECKPOINT NA ELKE HOOFDFASE                                       │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│ 1. VALIDATIE (5 min)                                               │
│    □ Run quick_validate.py op alle nieuwe skills                   │
│    □ Alle skills MOETEN "Skill is valid!" returnen                 │
│    □ NL én EN versies compleet?                                    │
│                                                                     │
│ 2. PACKAGING (5 min)                                               │
│    □ Run package_skill.py op alle nieuwe skills                    │
│    □ .skill files gegenereerd in skills/packaged/                  │
│                                                                     │
│ 3. GITHUB SYNC (5 min)                                             │
│    □ Alle source folders gepusht                                   │
│    □ Alle .skill packages gepusht                                  │
│    □ ROADMAP.md bijgewerkt                                         │
│                                                                     │
│ 4. LESSONS LEARNED (5 min)                                         │
│    □ Nieuwe inzichten → LESSONS_LEARNED.md                         │
│    □ Problemen tegengekomen → documenteren                         │
│                                                                     │
│ 5. GO/NO-GO                                                        │
│    □ Alle validaties geslaagd → Volgende fase                      │
│    □ Issues gevonden → FIX voordat we doorgaan                     │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
```

### 4.2 Checkpoint Momenten

| Na Fase | Checkpoint Type |
|---------|-----------------|
| Migratie | **STRUCTUUR VALIDATIE** |
| Fase 4 (alle impl) | Standaard |
| Fase 5 (alle errors) | Standaard |
| Fase 6 (agents) | Standaard |
| Fase 7 (final) | **FINAL REVIEW** |

---

## Deel 5: Geüpdatete Fase Prompts

### 5.1 Fase Prompt Template (Nieuw)

```
┌─────────────────────────────────────────────────────────────────────┐
│ FASE [X.Y] PROMPT TEMPLATE                                         │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│ ═══════════════════════════════════════════════════════════════════│
│ STAP 0: CONTEXT OPHALEN (VERPLICHT)                                │
│ ═══════════════════════════════════════════════════════════════════│
│                                                                     │
│ 1. Haal ROADMAP.md op → Check status                               │
│ 2. Haal relevant research document op                              │
│ 3. (Indien impl/error) Haal syntax skill op                        │
│ 4. Bevestig vorige fase is COMPLEET en GEVALIDEERD                 │
│                                                                     │
│ ═══════════════════════════════════════════════════════════════════│
│ STAP 1: SKILL CREATIE                                              │
│ ═══════════════════════════════════════════════════════════════════│
│                                                                     │
│ Maak TWEE aparte skill folders:                                     │
│                                                                     │
│ skills/[categorie]/[skill-name]-nl/                                │
│ ├── SKILL.md          ← DIRECT in root!                            │
│ └── references/                                                     │
│                                                                     │
│ skills/[categorie]/[skill-name]-en/                                │
│ ├── SKILL.md          ← DIRECT in root!                            │
│ └── references/                                                     │
│                                                                     │
│ ═══════════════════════════════════════════════════════════════════│
│ STAP 2: VALIDATIE (VERPLICHT)                                      │
│ ═══════════════════════════════════════════════════════════════════│
│                                                                     │
│ Run voor BEIDE taalversies:                                         │
│                                                                     │
│ python quick_validate.py skills/[cat]/[skill]-nl                   │
│ python quick_validate.py skills/[cat]/[skill]-en                   │
│                                                                     │
│ MOET "Skill is valid!" returnen. Zo niet → FIX EERST              │
│                                                                     │
│ ═══════════════════════════════════════════════════════════════════│
│ STAP 3: PACKAGING                                                  │
│ ═══════════════════════════════════════════════════════════════════│
│                                                                     │
│ python package_skill.py skills/[cat]/[skill]-nl skills/packaged/   │
│ python package_skill.py skills/[cat]/[skill]-en skills/packaged/   │
│                                                                     │
│ ═══════════════════════════════════════════════════════════════════│
│ STAP 4: PUSH NAAR GITHUB                                           │
│ ═══════════════════════════════════════════════════════════════════│
│                                                                     │
│ Push:                                                               │
│ • skills/[categorie]/[skill]-nl/                                   │
│ • skills/[categorie]/[skill]-en/                                   │
│ • skills/packaged/[skill]-nl.skill                                 │
│ • skills/packaged/[skill]-en.skill                                 │
│ • ROADMAP.md (update status)                                        │
│                                                                     │
│ ═══════════════════════════════════════════════════════════════════│
│ STAP 5: BEVESTIGING                                                │
│ ═══════════════════════════════════════════════════════════════════│
│                                                                     │
│ Rapporteer:                                                         │
│ • Validatie resultaat (beide moeten "valid" zijn)                  │
│ • GitHub locaties                                                   │
│ • Volgende stap                                                     │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
```

---

## Deel 6: Actieplan

### 6.1 Directe Acties

| # | Actie | Status |
|---|-------|:------:|
| 1 | LESSONS_LEARNED.md updaten met tooling les | ✅ |
| 2 | Amendment 5 updaten met correcte structuur | 🔄 (dit document) |
| 3 | Besluit: Migratie nu of later? | ⏳ |

### 6.2 Migratie Beslissing

**Optie A: Nu migreren (AANBEVOLEN)**
- Schone basis voor resterende 31 skills
- Officiële tooling werkt
- ~2 uur werk

**Optie B: Aan het eind migreren**
- Meer werk later (56 skills i.p.v. 25)
- Twee systemen onderhouden
- Risico op meer inconsistentie

### 6.3 Na Migratie: Resterende Werk

| Fase | Skills | Folders te maken |
|------|:------:|:----------------:|
| 4.2-4.8 | 7 impl | 14 |
| 5 | 7 error | 14 |
| 6 | 2 agent | 4 |
| **TOTAAL** | **16** | **32** |

---

## Deel 7: Conclusie

### 7.1 Samenvatting Wijzigingen in Amendment 5 v2

| Aspect | v1 | v2 |
|--------|----|----|
| Directory structuur | NL/EN subfolders | Aparte skill folders met -nl/-en suffix |
| Validatie | Niet gespecificeerd | quick_validate.py verplicht |
| Packaging | Handmatig | package_skill.py verplicht |
| Totaal folders | 28 | 56 |

### 7.2 Kernboodschap

> **De officiële Anthropic tooling is de standaard.**
> 
> Onze skills MOETEN valideren met `quick_validate.py` en packagen met `package_skill.py`. Elke afwijking van de verwachte structuur creëert technische schuld.

---

*Amendment 5 v2 - 17 januari 2026*
*Bijgewerkt na Anthropic tooling analyse*
