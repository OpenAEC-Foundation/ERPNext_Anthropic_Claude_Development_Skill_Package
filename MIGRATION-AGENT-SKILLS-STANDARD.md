# Migratie naar Agent Skills Standaard — Audit & Actiepunten

**Package:** ERPNext_Anthropic_Claude_Development_Skill_Package
**Datum:** 2026-03-19
**Status:** YAML frontmatter aanwezig maar minimaal, uitbreiding nodig

---

## Huidige situatie

Alle 28 SKILL.md bestanden bevatten YAML frontmatter met `name` en `description`. Dit is het minimum voor progressive disclosure. Maar er ontbreken velden die het Blender-Bonsai package wél heeft: `license`, `compatibility`, en `metadata`.

De directorystructuur gebruikt `skills/source/` terwijl het Blender package `skills/{technology}/` direct gebruikt. Dit is een inconsistentie.

## Wat werkt

- YAML frontmatter met `name` en `description` → progressive disclosure is actief
- SKILL.md body's zijn compact → progressive disclosure werkt correct
- Inhoud is deterministisch en van hoge kwaliteit (WRONG→CORRECT patronen)
- Documentatie (WAY_OF_WORK, LESSONS, INDEX) is uitstekend

## Verbeterpunten

### 1. Frontmatter uitbreiden naar Blender-package niveau

**Huidige stijl (minimaal):**
```yaml
---
name: frappe-syntax-serverscripts
description: Complete syntax reference for Frappe Server Scripts...
---
```

**Aanbevolen stijl (volledig + trigger-geoptimaliseerd):**
```yaml
---
name: frappe-syntax-serverscripts
description: >
  Use when writing Python code for ERPNext/Frappe Server Scripts including
  Document Events, API endpoints, Scheduler Events, and Permission Queries.
  Prevents the #1 AI mistake: using import statements in Server Scripts
  (sandbox blocks ALL imports). Covers frappe.* methods, event name mapping,
  and correct v14/v15/v16 syntax. Keywords: Server Script, frappe, ERPNext,
  sandbox, import, doc event, validate, on_submit, before_save.
license: MIT
compatibility: "Claude Code, Claude.ai Projects, Claude API. ERPNext v14-16."
metadata:
  author: OpenAEC-Foundation
  version: "1.0"
---
```

Uitbreidingen per veld:
- **description**: herschrijven met "Use when..." trigger, anti-pattern vermelding, en keywords
- **license**: `MIT` (staat al in LICENSE bestand, maar moet ook in frontmatter)
- **compatibility**: welke Claude-platforms en ERPNext-versies
- **metadata**: auteur en versienummer voor traceerbaarheid

### 2. Description optimaliseren voor triggering

De `description` is het belangrijkste veld — Claude gebruikt dit om te beslissen of een skill geladen moet worden. Alle 28 descriptions moeten herschreven worden naar een formaat dat:

1. **Begint met "Use when..."** — vertelt Claude wanneer te activeren
2. **De #1 fout benoemt** die de skill voorkomt
3. **Keywords bevat** die matchen met typische gebruikersvragen
4. **ERPNext versies vermeldt** die gedekt worden

### 3. Globale installatie documenteren

Voeg aan INSTALL.md of USAGE.md de volgende sectie toe:

```markdown
### Globale installatie (Claude Code CLI)

Kopieer alle skills naar je globale skills directory zodat ze in elk project beschikbaar zijn:

cp -r skills/source/* ~/.claude/skills/

De skills gebruiken progressive disclosure: bij startup laadt Claude alleen
de name en description (~100 tokens per skill). De volledige instructies
worden pas geladen wanneer een skill relevant is voor je vraag.

28 skills × ~100 tokens = ~2.800 tokens startup-overhead. Dit is verwaarloosbaar
op een context window van 200k tokens.
```

### 4. Directorystructuur afstemmen

Dit package gebruikt `skills/source/{category}/{skill-name}/` terwijl het Blender package `skills/{technology}/{category}/{skill-name}/` gebruikt.

Twee opties:
- **Optie A (aanbevolen):** behoud huidige structuur maar documenteer het verschil. ERPNext is één technologie, dus de extra `source/` laag is niet nodig maar ook niet schadelijk.
- **Optie B:** hernoem `skills/source/` naar `skills/erpnext/` zodat het consistent is met het Blender package. Dit is een breaking change voor bestaande gebruikers.

## Takenlijst

- [ ] Alle 28 frontmatter blocks uitbreiden met `license`, `compatibility`, `metadata`
- [ ] Alle 28 `description` velden herschrijven naar trigger-geoptimaliseerd formaat ("Use when...")
- [ ] INSTALL.md/USAGE.md bijwerken met globale installatie-instructies en progressive disclosure uitleg
- [ ] Controleer dat alle description velden keywords bevatten die matchen met typische ERPNext development vragen
- [ ] Besluit nemen over directorystructuur (`skills/source/` vs `skills/erpnext/`)

## Referenties

- [Agent Skills standaard](https://agentskills.org)
- [Anthropic Skill Authoring Best Practices](https://platform.claude.com/docs/en/agents-and-tools/agent-skills/best-practices)
- [Claude Code Skills documentatie](https://code.claude.com/docs/en/skills)
- [Progressive Disclosure architectuur](https://www.anthropic.com/engineering/equipping-agents-for-the-real-world-with-agent-skills)
- [Blender-Bonsai package frontmatter](../Blender-Bonsai-ifcOpenshell-Sverchok-Claude-Skill-Package/) — referentie voor volledig frontmatter-formaat
