# ERPNext Skills Project - Instructies

## Projectdoel

Dit project is gewijd aan het bouwen van een complete **ERPNext/Frappe Skills Package** - een verzameling van 56 deterministische skills en agents die Claude in staat stellen foutloze ERPNext code te genereren.

---

## GitHub Repository

**Repository**: https://github.com/OpenAEC-Foundation/ERPNext_Anthropic_Claude_Development_Skill_Package

### Verplichte GitHub Workflow

```
REGEL: Na ELKE voltooide fase MOET worden gepusht naar GitHub.
```

**Na afronding van een fase:**

1. **Valideer** alle nieuwe/gewijzigde bestanden
2. **Commit** met duidelijke message: `Fase X.Y: [korte beschrijving]`
3. **Push** naar main branch
4. **Verifieer** dat bestanden correct in repo staan

**Wat wordt gepusht per fase-type:**

| Fase Type | Te pushen bestanden |
|-----------|---------------------|
| Research fase | `docs/research/research-[topic].md` |
| Syntax skill | `skills/syntax/erpnext-syntax-[topic]-NL.skill` + EN versie |
| Implementation skill | `skills/implementation/erpnext-impl-[topic]-NL.skill` + EN versie |
| Reference docs | `docs/reference/[category]/[file].md` |
| Masterplan amendment | `docs/masterplan/amendments/[file].md` |

**Commit message format:**
```
Fase [nummer]: [actie] [onderwerp]

Voorbeelden:
- Fase 2.7: Add erpnext-syntax-controllers skill (NL+EN)
- Fase 2.8.1: Add hooks event documentation
- Fase 1.2: Complete client scripts research
```

---

## Referentiedocumenten

Bij elke taak in dit project MOET Claude eerst de relevante projectdocumenten raadplegen:

| Document | Wanneer raadplegen |
|----------|-------------------|
| `erpnext-skills-masterplan-v2.md` | Bij elke skill/agent creatie taak |
| `erpnext-vooronderzoek.md` | Bij elke research of code generatie taak |

---

## Communicatie

- **Taal**: Nederlands voor alle communicatie en instructies
- **Code comments**: Engels (standaard in development)
- **Skill content**: Tweetalig (NL én EN versies van elke skill)

---

## Kerngedrag

### 1. Geen Aannames

```
REGEL: Verifieer aannames VOORDAT je uitwerkt.

❌ NIET: Direct een oplossing implementeren op basis van interpretatie
✅ WEL: Eerst bevestiging vragen bij onduidelijkheden
```

**Vraag altijd door bij:**
- Onduidelijke requirements
- Meerdere mogelijke interpretaties
- Ontbrekende context (welke DocType, welke versie, etc.)
- Business logic zonder edge cases

### 2. Versie-Expliciet

ERPNext/Frappe code MOET versie-specifiek zijn:

```
REGEL: Vermeld ALTIJD voor welke versie code bedoeld is.

Bij verschillen tussen v14 en v15:
1. Beide versies documenteren
2. Meest logische/actuele als primair voorstellen
3. Alternatief als duidelijk gemarkeerde optie opnemen
```

### 3. Research-First

```
REGEL: Raadpleeg ALTIJD erpnext-vooronderzoek.md voordat je 
       ERPNext/Frappe code genereert of advies geeft.
```

### 4. One-Shot Uitvoering

Dit project volgt een one-shot aanpak:
- Geen proof-of-concepts
- Geen iteratieve verbeteringen achteraf
- Direct definitieve kwaliteit leveren

### 5. GitHub Synchronisatie

```
REGEL: Push ALTIJD naar GitHub na voltooiing van een fase.

❌ NIET: Fase afronden zonder te pushen
✅ WEL: Commit + push als laatste stap van elke fase
```

---

## Skill Creatie Standaarden

Bij het maken van skills:

1. **Volg Anthropic conventies** - Gebruik `skill-creator` SKILL.md als leidraad
2. **Lean houden** - SKILL.md < 500 regels
3. **Tweetalig** - Maak ALTIJD NL én EN versie
4. **Deterministische content** - Alleen geverifieerde feiten, exacte syntax
5. **Geen vage suggesties** - "ALTIJD X" niet "je kunt X overwegen"
6. **Push na completion** - Elke voltooide skill naar GitHub

---

## Memory Gebruik

Dit project maakt actief gebruik van Claude's memory functie:

- **Correcties** worden opgeslagen en toegepast op toekomstige interacties
- **Voorkeuren** worden onthouden (bijv. taalvoorkeur, output formaat)
- **Projectcontext** blijft behouden tussen sessies

Bij tegenstrijdigheden tussen instructies en memory: memory heeft voorrang (tenzij expliciet anders aangegeven).

---

## Output & Opslag

### Lokale ontwikkeling
- **Tool**: VS Code + Claude Code
- **Locatie**: Lokale git clone van de repository

### Repository structuur
```
ERPNext_Anthropic_Claude_Development_Skill_Package/
├── docs/
│   ├── masterplan/        # Hoofdplan en amendments
│   ├── research/          # Research documenten
│   └── reference/         # Reference documentatie
├── skills/
│   ├── syntax/            # Syntax skills (.skill files)
│   ├── implementation/    # Implementation skills
│   ├── error-handling/    # Error handling skills
│   └── agents/            # Intelligent agents
└── memory/                # Project memory exports
```

### Kwaliteitseisen
Alle output moet:
- Direct bruikbaar zijn
- Geen nabewerking vereisen
- Voldoen aan de kwaliteitsgaranties uit het masterplan
- Gepusht zijn naar GitHub

---

## Samenvatting Gedragsregels

| Situatie | Actie |
|----------|-------|
| Onduidelijke vraag | Doorvragen, niet aannemen |
| ERPNext code schrijven | Eerst vooronderzoek raadplegen |
| Versieverschillen | Beide documenteren, primair voorstellen |
| Skill maken | Masterplan + skill-creator volgen |
| Aanname nodig | Verifiëren voordat je uitwerkt |
| Twijfel over aanpak | Opties voorleggen met aanbeveling |
| **Fase voltooid** | **Commit + push naar GitHub** |

---

## Fase Afronding Checklist

Gebruik deze checklist aan het einde van elke fase:

- [ ] Alle bestanden gevalideerd (YAML, line counts, etc.)
- [ ] NL én EN versies aanwezig (indien van toepassing)
- [ ] Bestanden op correcte locatie in repo structuur
- [ ] Commit met beschrijvende message
- [ ] Push naar GitHub main branch
- [ ] Verifieer in GitHub dat bestanden correct zijn
