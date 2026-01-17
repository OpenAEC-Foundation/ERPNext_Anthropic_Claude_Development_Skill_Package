# ERPNext Skills Project - Instructies

## Projectdoel

Een complete ERPNext/Frappe Skills Package bouwen - 56 deterministische skills en agents die Claude in staat stellen foutloze ERPNext code te genereren.

---

## GitHub Repository

**Repo**: `OpenAEC-Foundation/ERPNext_Anthropic_Claude_Development_Skill_Package`  
**Type**: Privé  
**Branch**: main

### GitHub Toegang Instellen

Elke sessie: configureer de token uit `api-tokens.md`:

```bash
export GITHUB_TOKEN="<token_uit_api-tokens.md>"
```

Test:
```bash
curl -s -H "Authorization: Bearer $GITHUB_TOKEN" https://api.github.com/user
```

### Content Ophalen van GitHub

```bash
# Bestand lezen
curl -s -H "Authorization: Bearer $GITHUB_TOKEN" \
  -H "Accept: application/vnd.github.raw" \
  "https://api.github.com/repos/OpenAEC-Foundation/ERPNext_Anthropic_Claude_Development_Skill_Package/contents/PAD/NAAR/BESTAND.md"
```

**Veelgebruikte paden:**
| Document | Pad |
|----------|-----|
| Masterplan | `docs/masterplan/erpnext-skills-masterplan-v2.md` |
| Vooronderzoek | `docs/masterplan/erpnext-vooronderzoek.md` |
| Research docs | `docs/research/research-[topic].md` |
| Voortgang | `ROADMAP.md` |
| Geleerde lessen | `LESSONS_LEARNED.md` |
| Way of Work | `WAY_OF_WORK.md` |

---

## Verplichte GitHub Workflow

**REGEL**: Na ELKE voltooide fase MOET worden gepusht naar GitHub.

### Push Procedure

```bash
# 1. Encode bestand
CONTENT=$(base64 -w 0 /pad/naar/bestand.md)

# 2. Voor nieuw bestand
curl -X PUT -H "Authorization: Bearer $GITHUB_TOKEN" \
  "https://api.github.com/repos/OpenAEC-Foundation/ERPNext_Anthropic_Claude_Development_Skill_Package/contents/PAD/BESTAND.md" \
  -d '{"message":"Fase X.Y: beschrijving","content":"'$CONTENT'"}'

# 3. Voor update (SHA nodig)
SHA=$(curl -s -H "Authorization: Bearer $GITHUB_TOKEN" \
  "https://api.github.com/repos/.../contents/PAD/BESTAND.md" | grep '"sha"' | head -1 | cut -d'"' -f4)

curl -X PUT ... -d '{"message":"...","content":"...","sha":"'$SHA'"}'
```

### Commit Message Format
```
Fase [nummer]: [actie] [onderwerp]

Voorbeelden:
- Fase 2.10: Add erpnext-syntax-jinja skill (NL+EN)
- Fase 2.11: Complete scheduler research
```

---

## Kerngedrag

### 1. Research-First
ALTIJD eerst het relevante research document ophalen van GitHub voordat je ERPNext/Frappe code genereert of advies geeft.

### 2. Versie-Expliciet
ERPNext/Frappe code MOET versie-specifiek zijn (v14/v15). Bij verschillen: beide documenteren.

### 3. Geen Aannames
Verifieer aannames VOORDAT je uitwerkt. Vraag door bij onduidelijkheden.

### 4. One-Shot Uitvoering
- Geen proof-of-concepts
- Geen iteratieve verbeteringen achteraf  
- Direct definitieve kwaliteit

### 5. Deterministische Content
```
❌ "Je kunt X overwegen..."
✅ "ALTIJD X wanneer Y"
```

---

## Skill Creatie Standaarden

| Aspect | Vereiste |
|--------|----------|
| SKILL.md lengte | <500 regels |
| Talen | NL én EN versie |
| Content | Alleen geverifieerde feiten |
| References/ | Detail docs apart |

---

## Fase Opsplitsing Criteria

Split fase wanneer:
- Research document >700 regels
- Reference files >5
- Secties >8-10

---

## Communicatie

- **Taal**: Nederlands voor communicatie
- **Code comments**: Engels
- **Skill content**: Tweetalig (NL + EN)

---

## Wat Staat Waar

### In dit Claude Project (essentieel):
- `PROJECT_INSTRUCTIES.md` - Dit bestand
- `api-tokens.md` - GitHub/ERPNext credentials
- `SKILL.md` - Skill-creator template

### Op GitHub (ophalen wanneer nodig):
- Masterplan + amendments
- Alle research documenten
- Alle reference documenten  
- Voortgang tracking
- Geleerde lessen
- Way of Work methodologie

---

## Snelle Referentie

### Huidige Status
- **Fase**: 2.10 (Jinja Templates)
- **Voortgang**: ~38%
- **Voltooide skills**: 5 van 8 syntax skills

### Volgende Stappen
1. Fase 2.10: Jinja skill
2. Fase 2.11: Scheduler skill
3. Fase 2.12: Custom App skill

### Kritieke Technische Les
**Server Scripts Sandbox**: ALLE imports geblokkeerd!
```python
# ❌ FOUT
from frappe.utils import nowdate

# ✅ CORRECT  
date = frappe.utils.nowdate()
```

---

*Zie `LESSONS_LEARNED.md` op GitHub voor alle geleerde lessen.*
