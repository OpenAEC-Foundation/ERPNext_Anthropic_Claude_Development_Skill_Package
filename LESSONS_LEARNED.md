# Lessons Learned: ERPNext Skills Package Project

> **Project**: ERPNext/Frappe Skills Package voor Claude
> **Periode**: Januari 2025 - Januari 2026
> **Organisatie**: OpenAEC Foundation

Dit document bevat alle geleerde lessen uit het ontwikkelen van een comprehensive AI skill package voor een open source project. De lessen zijn bruikbaar voor iedereen die een soortgelijk project wil opzetten.

---

## Inhoudsopgave

1. [Technische Lessen: Frappe/ERPNext](#1-technische-lessen-frappeerpnext)
2. [Project Management Lessen](#2-project-management-lessen)
3. [Claude/AI Workflow Lessen](#3-claudeai-workflow-lessen)
4. [Skill Development Lessen](#4-skill-development-lessen)
5. [GitHub Integratie Lessen](#5-github-integratie-lessen)
6. [Valkuilen en Oplossingen](#6-valkuilen-en-oplossingen)
7. [Best Practices Samenvatting](#7-best-practices-samenvatting)

---

## 1. Technische Lessen: Frappe/ERPNext

### 1.1 Server Script Sandbox - KRITIEKE ONTDEKKING

**De belangrijkste technische les van dit project:**

Frappe Server Scripts draaien in een **RestrictedPython sandbox** die ALLE import statements blokkeert.

```python
# ❌ FOUT - Geeft altijd error
from frappe.utils import nowdate
import json

# ✅ CORRECT - Gebruik pre-loaded namespace
date = frappe.utils.nowdate()
data = frappe.parse_json(json_string)
```

**Impact**: Dit beïnvloedt ALLE code generatie voor Server Scripts. Elke AI bot die ERPNext code genereert moet deze beperking kennen.

**Beschikbare alternatieven in de sandbox:**

| In plaats van import | Gebruik direct |
|---------------------|----------------|
| `from frappe.utils import nowdate` | `frappe.utils.nowdate()` |
| `from datetime import timedelta` | `frappe.utils.add_days()` |
| `import json` | `frappe.parse_json()` |
| `import re` | Niet beschikbaar - gebruik Python string methods |

### 1.2 Versieverschillen v14 vs v15

| Feature | v14 | v15 | Impact |
|---------|-----|-----|--------|
| **Scheduler tick** | 4 min | 60 sec | Jobs draaien vaker in v15 |
| **Job deduplicatie** | `job_name` | `job_id` + `is_job_enqueued()` | `job_name` is deprecated |
| **Nieuwe hooks** | - | `before_discard`, `on_discard` | Extra lifecycle events |
| **Type annotations** | ❌ | ✅ Auto-generated | Betere IDE support |
| **Controller extends** | `override_doctype_class` | + `extend_doctype_class` (v16) | Veiliger overrides |

### 1.3 hooks.py Resolutie

**"Last writer wins" principe**: Bij conflicterende hooks tussen apps wint de laatst geladen app.

**Kritiek**: `bench migrate` is VERPLICHT na elke wijziging in `scheduler_events`. Zonder migrate worden wijzigingen niet opgepikt!

### 1.4 on_change Hook Gedrag

De `on_change` hook triggert na ELKE wijziging, inclusief `db_set()` operaties. Dit kan onverwachte loops veroorzaken.

```python
# ❌ FOUT - Kan infinite loop veroorzaken
def on_change(doc, method):
    frappe.db.set_value(doc.doctype, doc.name, "counter", doc.counter + 1)
    # ^ Dit triggert on_change opnieuw!

# ✅ CORRECT - Gebruik update_modified=False of flags
def on_change(doc, method):
    if doc.flags.get("in_on_change"):
        return
    doc.flags.in_on_change = True
    frappe.db.set_value(doc.doctype, doc.name, "counter", doc.counter + 1, 
                        update_modified=False)
```

### 1.5 Wijzigingen na on_update

Wijzigingen aan `self` in `on_update` worden NIET automatisch opgeslagen - het document is al naar de database geschreven.

```python
# ❌ FOUT - Wijziging gaat verloren
def on_update(self):
    self.status = "Completed"  # Niet opgeslagen!

# ✅ CORRECT - Gebruik db_set
def on_update(self):
    frappe.db.set_value(self.doctype, self.name, "status", "Completed")
```

### 1.6 Queue Timeouts

| Queue | Timeout | Gebruik |
|-------|---------|---------|
| short | 300s (5 min) | Snelle operaties |
| default | 300s (5 min) | Normale taken |
| long | 1500s (25 min) | Zware verwerking |

---

## 2. Project Management Lessen

### 2.1 Fase Opsplitsing Criteria

**Wanneer een fase splitsen:**

| Criterium | Drempelwaarde | Actie |
|-----------|---------------|-------|
| Research document regels | >700 | Splitsen |
| Reference files | >5 | Splitsen |
| Secties/onderwerpen | >8-10 | Splitsen |
| Gespreksduur | Near limit | Splitsen |

**Opsplitsingsproces:**
1. Identificeer logische scheiding (fundamentals vs. advanced)
2. Maak amendment document
3. Zorg dat delen onafhankelijk zijn (geen circular dependencies)
4. Documenteer de rationale

### 2.2 Research-First Aanpak

**Gouden regel**: Nooit skills maken zonder grondige research.

Onze workflow:
1. **Deep research** - Officiële docs, GitHub source, community (2023+)
2. **Preliminary document** - Gestructureerde samenvatting
3. **Verificatie** - Tegen source code controleren
4. **Skill creatie** - Pas na volledige verificatie

### 2.3 One-Shot Mindset

**Principe**: Plan grondig zodat elke fase in één keer correct uitgevoerd kan worden.

- Geen "we fixen het later"
- Geen proof-of-concepts
- Direct definitieve kwaliteit

### 2.4 Bilingual Overhead

Het maken van NL én EN versies **verdubbelt** de tijd maar vergroot het bereik aanzienlijk.

**Tip**: Maak eerst de primaire taal volledig, vertaal dan systematisch. Niet gelijktijdig ontwikkelen.

---

## 3. Claude/AI Workflow Lessen

### 3.1 Memory Gebruik

Claude's memory feature is essentieel voor project continuïteit:
- Correcties worden onthouden
- Voorkeuren blijven behouden
- Context blijft over sessies heen

**Tip**: Gebruik memory_user_edits tool voor belangrijke projectregels.

### 3.2 Filesystem Reset

**Kritiek**: Het Claude filesystem reset tussen sessies!

**Oplossingen**:
- Push naar GitHub na elke fase
- Download belangrijke bestanden
- Gebruik project knowledge voor persistente docs

### 3.3 Conversation Length Management

Complexe fases kunnen het gesprekslimiet bereiken.

**Oplossingen**:
- Pre-split grote fases
- Monitor voortgang
- Save incrementeel naar GitHub

### 3.4 Token Opslaan

GitHub tokens worden NIET onthouden tussen sessies.

**Oplossing**: Sla tokens op in een `api-tokens.md` bestand in project knowledge (regenereer na sessie voor veiligheid!).

---

## 4. Skill Development Lessen

### 4.1 Anthropic Conventies

**Strikt volgen van officiële conventies is essentieel:**

| Component | Vereiste |
|-----------|----------|
| SKILL.md | <500 regels, lean |
| Frontmatter | Correct YAML |
| References/ | Detail docs apart |
| Decision trees | In SKILL.md |

### 4.2 Deterministische Content

Skills moeten onambigueus zijn:

```markdown
# ❌ FOUT - Te vaag
"Je kunt overwegen om X te gebruiken..."
"Het is vaak een goed idee om..."

# ✅ CORRECT - Deterministisch
"ALTIJD X gebruiken wanneer Y"
"NOOIT Z doen omdat [reden]"
```

### 4.3 Skill Structuur

Effectieve skill organisatie:

```
skill-name/
├── SKILL.md              # <500 regels, quick reference
└── references/
    ├── methods.md        # Complete API signatures
    ├── events.md         # Event listings
    ├── examples.md       # Werkende code voorbeelden
    └── anti-patterns.md  # Wat NIET te doen
```

### 4.4 Versie-Expliciet

**ALTIJD** documenteren voor welke versie code bedoeld is:

```python
# v14/v15 compatible
def my_function():
    pass

# v15+ only (nieuw)
def v15_only_function():
    pass
```

---

## 5. GitHub Integratie Lessen

### 5.1 Token Setup

**Fine-grained Personal Access Token vereisten:**

| Permission | Setting | Waarvoor |
|------------|---------|----------|
| Contents | Read and write | Push/pull code |
| Metadata | Read-only | Repo info |
| Issues | Read and write | Issues aanmaken |

**Resource owner**: Organisatie (niet persoonlijk account)

### 5.2 Claude Project Settings

**Vereiste configuratie:**

| Setting | Waarde |
|---------|--------|
| Network | "Package managers only" |
| Additional domains | `api.github.com`, `github.com` |

**KRITIEK**: Domain toevoegingen werken pas in een NIEUW gesprek!

### 5.3 Git Clone Beperking

`git clone` werkt NIET in Claude's container (proxy blokkeert).

**Oplossing**: Gebruik GitHub API voor alle operaties:

```bash
# Content ophalen
curl -H "Authorization: Bearer $TOKEN" \
  -H "Accept: application/vnd.github.raw" \
  "https://api.github.com/repos/owner/repo/contents/path/file.md"

# Content pushen
curl -X PUT -H "Authorization: Bearer $TOKEN" \
  "https://api.github.com/repos/owner/repo/contents/path/file.md" \
  -d '{"message":"commit msg","content":"base64_content","sha":"file_sha"}'
```

### 5.4 Push Na Elke Fase

**Regel**: Werk dat niet gecommit is, bestaat niet.

Na elke voltooide fase:
1. Valideer bestanden
2. Commit met beschrijvende message
3. Push naar GitHub
4. Verifieer in repo

---

## 6. Valkuilen en Oplossingen

### 6.1 Valkuil: Aannemen zonder Verifiëren

**Probleem**: Claude kan verouderde of incorrecte informatie hebben.

**Oplossing**: 
- Altijd web search voor actuele docs
- Verifieer tegen GitHub source code
- Community input alleen van 2023+

### 6.2 Valkuil: Te Grote Fases

**Probleem**: Fase wordt te groot voor één gesprek.

**Oplossing**: 
- Monitor criteria (>700 regels, >5 files, >8 secties)
- Split proactief, niet reactief
- Documenteer split in amendment

### 6.3 Valkuil: Geen GitHub Sync

**Probleem**: Werk verloren door filesystem reset.

**Oplossing**: 
- Push na ELKE fase
- Geen uitzonderingen
- Verifieer dat push gelukt is

### 6.4 Valkuil: Token Vergeten

**Probleem**: Nieuwe sessie, geen GitHub toegang.

**Oplossing**: 
- Token in project knowledge (api-tokens.md)
- Regenereer na sessie voor veiligheid
- Documenteer alle vereiste permissions

### 6.5 Valkuil: Domains Niet Werkend

**Probleem**: Domains toegevoegd maar werken niet.

**Oplossing**: 
- Domains werken pas in NIEUW gesprek
- Niet alleen refresh, echt nieuw gesprek starten
- Test met curl naar api.github.com

---

## 7. Best Practices Samenvatting

### Research

1. ✅ Start met officiële documentatie
2. ✅ Verifieer tegen GitHub source code
3. ✅ Alleen community input van 2023+
4. ✅ Documenteer bronnen
5. ❌ Nooit aannemen zonder verificatie

### Skill Development

1. ✅ SKILL.md <500 regels
2. ✅ Deterministische formulering
3. ✅ Decision trees voor complexe keuzes
4. ✅ Beide taalversies maken
5. ✅ Anti-patterns documenteren
6. ❌ Geen vage suggesties

### Project Management

1. ✅ Research before action
2. ✅ Monitor fase complexiteit
3. ✅ Split proactief bij criteria overschrijding
4. ✅ One-shot mindset
5. ✅ Document everything
6. ❌ Geen "we fixen het later"

### Version Control

1. ✅ Push na ELKE fase
2. ✅ Beschrijvende commit messages
3. ✅ Verifieer push succesvol
4. ✅ Token in project knowledge
5. ❌ Nooit werk ongecommit laten

### Claude Workflow

1. ✅ Memory voor belangrijke regels
2. ✅ Project knowledge voor persistente docs
3. ✅ Nieuw gesprek na settings wijzigingen
4. ✅ Download belangrijke bestanden
5. ❌ Niet vertrouwen op filesystem persistence

---

## Appendix: Quick Reference Cards

### A. Server Script Sandbox Cheat Sheet

```
✅ BESCHIKBAAR                    ❌ NIET BESCHIKBAAR
─────────────────────────────────────────────────────
frappe.db.*                      import statements
frappe.utils.*                   open() / file access
frappe.get_doc()                 os / subprocess
frappe.new_doc()                 eval() / exec()
frappe.throw()                   requests / http
frappe.msgprint()                External libraries
frappe.parse_json()              __import__
frappe.session.user              compile()
```

### B. Fase Opsplitsing Decision Tree

```
Research document >700 regels?
├── Ja → SPLIT
└── Nee → Reference files >5?
          ├── Ja → SPLIT
          └── Nee → Secties >8-10?
                    ├── Ja → SPLIT
                    └── Nee → Doorgaan met fase
```

### C. GitHub Push Checklist

```
□ Alle bestanden gevalideerd
□ NL én EN versies aanwezig (indien van toepassing)
□ Commit message: "Fase X.Y: [beschrijving]"
□ Push naar main branch
□ Verifieer in GitHub web interface
```

### D. Nieuwe Sessie Checklist

```
□ GitHub token uit api-tokens.md
□ export GITHUB_TOKEN="..."
□ Test: curl met token naar api.github.com
□ Indien domains gewijzigd: nieuw gesprek nodig
```

---

*Dit document is een levend document en wordt bijgewerkt naarmate het project vordert.*

*Laatst bijgewerkt: 17 januari 2026*

### 1.9 Database Operaties - Fase 3 Ontdekkingen

**Drie abstractieniveaus kiezen:**

```
High-level ORM     → frappe.get_doc()      → Met validaties, langzamer
Mid-level Query    → frappe.db.get_list()  → Sneller, met/zonder permissions
Low-level SQL      → frappe.db.sql()       → Snelst, geen bescherming
```

**REGEL**: Altijd hoogst mogelijke abstractieniveau gebruiken.

**Kritieke Insights:**

1. **`db_set` bypassed ALLES** - Geen validate, geen on_update, geen permissions
   ```python
   # Alleen gebruiken voor:
   # - Hidden fields
   # - Counters/timestamps
   # - Background jobs waar je ZEKER weet wat je doet
   ```

2. **Transaction hooks (v15+)** - Nieuwe manier om rollback te handlen
   ```python
   frappe.db.after_rollback.add(cleanup_function)
   frappe.db.after_commit.add(notify_function)
   ```

3. **get_list vs get_all** - Subtiel maar belangrijk
   - `get_list` → Past user permissions toe
   - `get_all` → Geen permissions, admin-level access

4. **v16 Breaking Changes** - Aggregatie syntax is veranderd!
   ```python
   # v14/v15: fields=['count(name) as count']
   # v16:     fields=[{'COUNT': 'name', 'as': 'count'}]
   ```

5. **SQL Injection risico is REËEL** - Zelfs in interne scripts
   ```python
   # ❌ NOOIT
   frappe.db.sql(f"SELECT * FROM `tabUser` WHERE name = '{input}'")
   
   # ✅ ALTIJD
   frappe.db.sql("SELECT * FROM `tabUser` WHERE name = %(name)s", {'name': input})
   ```

6. **N+1 Query Problem** - Grootste performance killer
   ```python
   # Batch fetch in plaats van loop queries
   docs = frappe.get_all('Customer', filters={'name': ['in', names]})
   ```

