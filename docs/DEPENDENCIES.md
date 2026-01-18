# ERPNext Skills Package - Dependencies Matrix

> Dit document beschrijft de afhankelijkheden tussen skills in het package.
> Skills kunnen standalone of in combinatie worden gebruikt.

---

## Dependency Types

| Type | Beschrijving |
|------|-------------|
| **Required** | Skill MOET geladen zijn voor correct functioneren |
| **Recommended** | Skill verbetert output maar is niet verplicht |
| **Related** | Thematisch gerelateerd, geen technische dependency |

---

## Skill Categories Overview

```
┌─────────────────────────────────────────────────────────────────────┐
│                    SKILL HIERARCHY                                  │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│  LAYER 1: FOUNDATION (Syntax Skills)                                │
│  ════════════════════════════════════                               │
│  These define HOW to write code. No dependencies.                   │
│                                                                     │
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐      │
│  │ syntax-         │  │ syntax-         │  │ syntax-         │      │
│  │ clientscripts   │  │ serverscripts   │  │ controllers     │      │
│  └─────────────────┘  └─────────────────┘  └─────────────────┘      │
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐      │
│  │ syntax-hooks    │  │ syntax-         │  │ syntax-jinja    │      │
│  │                 │  │ whitelisted     │  │                 │      │
│  └─────────────────┘  └─────────────────┘  └─────────────────┘      │
│  ┌─────────────────┐  ┌─────────────────┐                           │
│  │ syntax-         │  │ syntax-         │                           │
│  │ scheduler       │  │ customapp       │                           │
│  └─────────────────┘  └─────────────────┘                           │
│                                                                     │
│  LAYER 2: CORE (Cross-cutting concerns)                             │
│  ════════════════════════════════════════                           │
│  These define WHAT APIs to use. Reference syntax skills.            │
│                                                                     │
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐      │
│  │ database        │  │ permissions     │  │ api-patterns    │      │
│  │ (frappe.db)     │  │ (access ctrl)   │  │ (REST/RPC)      │      │
│  └─────────────────┘  └─────────────────┘  └─────────────────┘      │
│                                                                     │
│  LAYER 3: IMPLEMENTATION (Workflow guidance)                        │
│  ══════════════════════════════════════════                         │
│  These define HOW TO IMPLEMENT. Use syntax + core skills.           │
│                                                                     │
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐      │
│  │ impl-           │  │ impl-           │  │ impl-           │      │
│  │ clientscripts   │  │ serverscripts   │  │ controllers     │      │
│  └─────────────────┘  └─────────────────┘  └─────────────────┘      │
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐      │
│  │ impl-hooks      │  │ impl-           │  │ impl-jinja      │      │
│  │                 │  │ whitelisted     │  │                 │      │
│  └─────────────────┘  └─────────────────┘  └─────────────────┘      │
│  ┌─────────────────┐  ┌─────────────────┐                           │
│  │ impl-scheduler  │  │ impl-customapp  │                           │
│  └─────────────────┘  └─────────────────┘                           │
│                                                                     │
│  LAYER 4: ERROR HANDLING                                            │
│  ═══════════════════════                                            │
│  These define HOW TO HANDLE ERRORS. Reference all other layers.     │
│                                                                     │
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐      │
│  │ errors-         │  │ errors-         │  │ errors-         │      │
│  │ clientscripts   │  │ serverscripts   │  │ controllers     │      │
│  └─────────────────┘  └─────────────────┘  └─────────────────┘      │
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐      │
│  │ errors-hooks    │  │ errors-database │  │ errors-         │      │
│  │                 │  │                 │  │ permissions     │      │
│  └─────────────────┘  └─────────────────┘  └─────────────────┘      │
│  ┌─────────────────┐                                                │
│  │ errors-api      │                                                │
│  └─────────────────┘                                                │
│                                                                     │
│  LAYER 5: AGENTS (Orchestration)                                    │
│  ═══════════════════════════════                                    │
│  These ORCHESTRATE other skills. Depend on all layers.              │
│                                                                     │
│  ┌─────────────────┐  ┌─────────────────┐                           │
│  │ code-           │  │ code-           │                           │
│  │ interpreter     │  │ validator       │                           │
│  └─────────────────┘  └─────────────────┘                           │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
```

---

## Detailed Dependencies

### Syntax Skills (Layer 1)

| Skill | Required | Recommended | Related |
|-------|----------|-------------|---------|
| `syntax-clientscripts` | - | - | syntax-serverscripts |
| `syntax-serverscripts` | - | - | syntax-clientscripts, syntax-controllers |
| `syntax-controllers` | - | - | syntax-hooks |
| `syntax-hooks` | - | syntax-controllers | syntax-customapp |
| `syntax-whitelisted` | - | - | syntax-serverscripts, api-patterns |
| `syntax-jinja` | - | - | - |
| `syntax-scheduler` | - | syntax-hooks | - |
| `syntax-customapp` | - | syntax-hooks, syntax-controllers | - |

**Note**: Syntax skills have NO required dependencies - they are foundational.

---

### Core Skills (Layer 2)

| Skill | Required | Recommended | Related |
|-------|----------|-------------|---------|
| `database` | - | - | permissions |
| `permissions` | - | database | - |
| `api-patterns` | - | syntax-whitelisted | - |

---

### Implementation Skills (Layer 3)

| Skill | Required | Recommended | Related |
|-------|----------|-------------|---------|
| `impl-clientscripts` | syntax-clientscripts | database | errors-clientscripts |
| `impl-serverscripts` | syntax-serverscripts | database, permissions | errors-serverscripts |
| `impl-controllers` | syntax-controllers | database, permissions | errors-controllers |
| `impl-hooks` | syntax-hooks | syntax-controllers | errors-hooks |
| `impl-whitelisted` | syntax-whitelisted | api-patterns, permissions | errors-api |
| `impl-jinja` | syntax-jinja | - | - |
| `impl-scheduler` | syntax-scheduler | syntax-hooks | - |
| `impl-customapp` | syntax-customapp | syntax-hooks, syntax-controllers | - |

---

### Error Handling Skills (Layer 4)

| Skill | Required | Recommended | Related |
|-------|----------|-------------|---------|
| `errors-clientscripts` | syntax-clientscripts | impl-clientscripts | - |
| `errors-serverscripts` | syntax-serverscripts | impl-serverscripts | errors-database |
| `errors-controllers` | syntax-controllers | impl-controllers | errors-database |
| `errors-hooks` | syntax-hooks | impl-hooks | - |
| `errors-database` | database | - | errors-serverscripts, errors-controllers |
| `errors-permissions` | permissions | - | errors-api |
| `errors-api` | api-patterns | impl-whitelisted | errors-permissions |

---

### Agent Skills (Layer 5)

| Skill | Required | Recommended | Related |
|-------|----------|-------------|---------|
| `code-interpreter` | - | ALL syntax skills | code-validator |
| `code-validator` | - | ALL skills | code-interpreter |

**Note**: Agents orchestrate skills dynamically. They reference other skills in their output but don't technically "depend" on them.

---

## Common Skill Combinations

### For Client-Side Development
```
syntax-clientscripts
  + impl-clientscripts
  + errors-clientscripts
  + database (for frappe.call patterns)
```

### For Server Scripts
```
syntax-serverscripts
  + impl-serverscripts
  + errors-serverscripts
  + database
  + permissions
```

### For Custom App Development
```
syntax-customapp
  + syntax-controllers
  + syntax-hooks
  + impl-customapp
  + impl-controllers
  + impl-hooks
  + database
  + permissions
```

### For API Development
```
syntax-whitelisted
  + api-patterns
  + impl-whitelisted
  + errors-api
  + permissions
```

### For Complete Code Generation (Agent-assisted)
```
code-interpreter (requirements → specs)
  → ALL relevant syntax + impl skills
  → code-validator (validation)
  → ALL relevant errors skills
```

---

## Loading Strategy

### Progressive Loading
Skills should be loaded progressively based on task:

1. **First**: Load relevant syntax skill(s)
2. **Then**: Load relevant core skill(s) if needed
3. **Then**: Load relevant impl skill(s) for workflow
4. **Finally**: Load relevant errors skill(s) for robustness

### Agent-Directed Loading
When using agents:
- `code-interpreter` determines which skills are needed
- `code-validator` validates against relevant skills
- Both agents include skill recommendations in output

---

## Version Compatibility

All skills in this package are compatible with:
- Frappe Framework v14, v15, v16
- ERPNext v14, v15, v16

Version-specific features are clearly marked within each skill.

---

*Last updated: 2026-01-18*
