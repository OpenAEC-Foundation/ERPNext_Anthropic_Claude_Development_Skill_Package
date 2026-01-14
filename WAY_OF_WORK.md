# Way of Work: Developing AI Skill Packages with Claude

> A methodology for creating comprehensive, deterministic skill and agent packages for open source projects using Claude AI

## Overview

This document describes a proven methodology for developing AI skill packages that enable Claude instances to generate flawless code for specific frameworks or technologies. This approach was developed and validated during the creation of the ERPNext/Frappe Skills Package project.

The methodology emphasizes:
- **Deep research before development**
- **Deterministic, verifiable content**
- **One-shot execution without iterations**
- **Bilingual delivery (or multi-language)**
- **Version control integration**

---

## The 7-Phase Methodology

```
┌─────────────────────────────────────────────────────────────────────────┐
│                        SKILL PACKAGE DEVELOPMENT                        │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                         │
│   Phase 1          Phase 2         Phase 3         Phase 4             │
│   ┌──────┐        ┌──────┐        ┌──────┐        ┌──────┐             │
│   │ DEEP │   →    │PRELIM│   →    │ REQ  │   →    │MASTER│             │
│   │RESRCH│        │RESRCH│        │DEFINE│        │ PLAN │             │
│   └──────┘        └──────┘        └──────┘        └──────┘             │
│                                                                         │
│   Phase 5          Phase 6         Phase 7                              │
│   ┌──────┐        ┌──────┐        ┌──────┐                              │
│   │TOPIC │   →    │SKILL │   →    │VALID │                              │
│   │RESRCH│        │CREATE│        │+PUSH │                              │
│   └──────┘        └──────┘        └──────┘                              │
│                                                                         │
└─────────────────────────────────────────────────────────────────────────┘
```

---

## Phase 1: Deep Research

### Purpose
Gain comprehensive understanding of the target technology/framework before any planning begins.

### Activities
- Explore official documentation extensively
- Identify all major mechanisms/APIs/patterns
- Discover edge cases and version differences
- Find common pitfalls and anti-patterns
- Gather real-world examples

### Output
Raw knowledge and insights (may be informal notes or conversation)

### Key Principle
> "You cannot create deterministic skills for something you don't deeply understand."

### Example from ERPNext Project
We started by exploring all scripting mechanisms in ERPNext/Frappe:
- Client Scripts (JavaScript)
- Server Scripts (Python sandbox)
- Document Controllers
- hooks.py configuration
- Jinja templates
- Scheduler/Background jobs
- Whitelisted API methods

This revealed critical insights like the Server Script sandbox blocking all imports - a fundamental limitation that would affect all code generation.

---

## Phase 2: Preliminary Research Document

### Purpose
Consolidate deep research into a structured reference document that serves as the foundation for all subsequent work.

### Activities
- Organize findings into logical sections
- Document syntax patterns with examples
- Create decision matrices (when to use what)
- Note version differences explicitly
- List sources and verification status

### Output
`vooronderzoek.md` or `preliminary-research.md` - A comprehensive reference document

### Structure Template
```markdown
# [Technology] Preliminary Research

## 1. Overview
Brief description of the technology landscape

## 2. Mechanism A
### Syntax
### Use Cases
### Version Differences
### Anti-patterns

## 3. Mechanism B
[repeat structure]

## N. Decision Matrix
When to use which mechanism

## Sources
- Official documentation links
- GitHub source code references
- Community resources (dated 2023+)
```

### Key Principle
> "The preliminary research document becomes the single source of truth for all skill development."

---

## Phase 3: Requirements Definition

### Purpose
Define what the skill package must achieve and establish quality criteria.

### Activities
- Identify target users (other Claude instances, developers)
- Define skill categories needed
- Establish constraints (line limits, structure requirements)
- Set quality guarantees
- Determine language requirements (bilingual, etc.)

### Output
Clear requirements document or section in masterplan

### Key Questions to Answer
1. What problems should the skills solve?
2. What should a Claude instance be able to do after loading these skills?
3. What quality guarantees do we provide?
4. What are the structural constraints (Anthropic conventions)?
5. What languages/versions must be supported?

### Example Requirements (ERPNext Project)
- Skills must be deterministic (no assumptions)
- SKILL.md files must stay under 500 lines
- All skills in Dutch AND English
- Version-explicit for ERPNext v14 and v15
- Follow official Anthropic skill-creator conventions
- One-shot execution (no proof-of-concepts)

---

## Phase 4: Detailed Masterplan

### Purpose
Create a comprehensive, phased execution plan with prompts for each step.

### Activities
- Break work into logical phases
- Define dependencies between phases
- Create ready-to-use prompts for each phase
- Establish exit criteria per phase
- Plan for phase splitting when complexity exceeds thresholds

### Output
`masterplan.md` - Detailed execution plan

### Masterplan Structure
```markdown
# [Project] Masterplan

## Vision & Goals
## Architecture Overview
## Complete Skill/Agent Index

## Phase 1: [Name]
### Goal
### Steps with Prompts
### Exit Criteria
### Dependencies

## Phase 2: [Name]
[repeat structure]

## Quality Guarantees
## Appendices
```

### Phase Splitting Criteria
Split a phase when:
- More than 700 lines of research content
- More than 5 reference files required
- More than 8-10 distinct sections
- Estimated execution exceeds conversation limits

### Key Principle
> "The masterplan should be detailed enough that each phase can be executed in a separate conversation without loss of context."

---

## Phase 5: Topic-Specific Research

### Purpose
Before creating each skill, conduct focused research on that specific topic.

### Activities
- Verify preliminary research against current documentation
- Deepen understanding of specific APIs/methods
- Gather additional examples
- Document version-specific behaviors
- Identify anti-patterns specific to this topic

### Output
`research-[topic].md` - Detailed research document per skill topic

### Research Document Structure
```markdown
# Research: [Topic]

## 1. Overview
## 2. Core Concepts
## 3. API Reference
## 4. Examples
## 5. Version Differences (v14 vs v15)
## 6. Anti-patterns
## 7. Best Practices
## 8. Sources

### For Skill Creation
- Key sections to include in SKILL.md
- Reference files needed
- Decision trees to create
```

### Key Principle
> "Never create a skill based on assumptions. Always verify against official documentation and source code."

---

## Phase 6: Skill Creation

### Purpose
Transform research into actionable, deterministic skills following platform conventions.

### Activities
- Create SKILL.md with quick reference and decision trees
- Create reference files (methods.md, examples.md, anti-patterns.md, etc.)
- Validate structure and line counts
- Create all language versions
- Package into distributable format

### Output
Complete skill packages (`.skill` files or folder structures)

### Skill Structure (Anthropic Convention)
```
skill-name/
├── SKILL.md              # Main file (<500 lines)
│   ├── YAML frontmatter
│   ├── Quick Reference
│   ├── Decision Trees
│   ├── Essential Patterns
│   └── Links to references
└── references/
    ├── methods.md        # Complete API signatures
    ├── events.md         # Event listings
    ├── examples.md       # Working code examples
    └── anti-patterns.md  # What NOT to do
```

### SKILL.md Principles
1. **Lean**: Stay under 500 lines
2. **Deterministic**: "ALWAYS do X" not "consider doing X"
3. **Decision-oriented**: Include decision trees for common choices
4. **Reference-linked**: Detailed info in reference files

### Key Principle
> "A skill should enable another Claude instance to generate correct code on the first attempt, without needing clarification."

---

## Phase 7: Validation & Version Control

### Purpose
Ensure quality and preserve all work in version control.

### Activities
- Validate YAML frontmatter
- Check line counts
- Verify all language versions are complete
- Package skills
- Commit with descriptive messages
- Push to GitHub
- Verify repository state

### Output
- Validated skill packages
- Updated GitHub repository

### Commit Message Format
```
Phase [number]: [action] [subject]

Examples:
- Phase 2.7: Add erpnext-syntax-controllers skill (NL+EN)
- Phase 2.8.1: Add hooks event documentation
- Phase 1.2: Complete server scripts research
```

### Post-Phase Checklist
- [ ] All files validated
- [ ] All language versions present
- [ ] Files in correct repository location
- [ ] Commit with descriptive message
- [ ] Push to GitHub
- [ ] Verify files in repository

### Key Principle
> "Every completed phase must be pushed to version control. Work that isn't committed doesn't exist."

---

## Project Organization

### Recommended Repository Structure
```
project-root/
├── README.md
├── SKILL.md                    # Main project skill (if applicable)
├── docs/
│   ├── masterplan/
│   │   ├── masterplan.md       # Main plan
│   │   ├── vooronderzoek.md    # Preliminary research
│   │   └── amendments/         # Plan adjustments
│   ├── research/               # Topic research documents
│   └── reference/              # Quick reference docs
├── skills/
│   ├── syntax/                 # Syntax skills
│   ├── implementation/         # Implementation skills
│   ├── error-handling/         # Error handling skills
│   └── agents/                 # Intelligent agents
└── memory/                     # Project memory exports
```

### Document Naming Conventions
| Type | Pattern | Example |
|------|---------|---------|
| Research | `research-[topic].md` | `research-client-scripts.md` |
| Skill | `erpnext-syntax-[topic]-[lang].skill` | `erpnext-syntax-hooks-NL.skill` |
| Amendment | `masterplan-aanpassing-fase-[x].md` | `masterplan-aanpassing-fase-2_6.md` |

---

## Key Success Factors

### 1. Research Before Action
Never start creating skills without thorough research. Assumptions lead to incorrect or incomplete skills.

### 2. One-Shot Mindset
Plan thoroughly so each phase can be executed correctly the first time. No "we'll fix it later" mentality.

### 3. Deterministic Content
Skills must provide clear, unambiguous guidance. Avoid phrases like:
- ❌ "You might want to consider..."
- ❌ "It's often good practice to..."
- ✅ "ALWAYS use X when Y"
- ✅ "NEVER do X because Y"

### 4. Version Explicitness
Always document which versions of the target technology are supported and note any differences.

### 5. Verification Loop
```
Research → Verify → Document → Verify → Create → Validate
```

### 6. Version Control Discipline
Commit and push after every completed phase. This ensures:
- Work is never lost
- Progress is trackable
- Collaboration is possible
- Rollback is available

---

## Handling Complexity

### When to Split Phases
Monitor these thresholds:

| Metric | Threshold | Action |
|--------|-----------|--------|
| Research lines | >700 | Split into sub-phases |
| Reference files | >5 | Consider splitting |
| Sections | >8-10 | Split by logical grouping |
| Conversation length | Near limit | Split remaining work |

### Phase Split Process
1. Identify logical division points
2. Create amendment document
3. Update masterplan
4. Ensure sub-phases are independent (no circular dependencies)
5. Document the split rationale

---

## Tools & Resources

### Essential Tools
- **Web Search**: For current documentation verification
- **Project Knowledge Search**: For accessing project documents
- **File Creation/Editing**: For document creation
- **Bash Tools**: For validation scripts, line counts
- **GitHub API**: For version control operations

### Validation Scripts
- `quick_validate.py` - YAML frontmatter validation
- `package_skill.py` - Skill packaging
- `wc -l` - Line count verification

### Research Sources (Priority Order)
1. Official documentation (highest priority)
2. GitHub source code
3. Community resources (recent only, 2023+)

---

## Lessons Learned

### From the ERPNext Project

1. **Sandbox Limitations Matter**: We discovered that Frappe Server Scripts block all imports - this fundamental limitation affected all code generation guidance.

2. **Phase Splitting is Normal**: Complex topics like hooks.py and custom apps required splitting into multiple sub-phases. Plan for this.

3. **Memory Helps Continuity**: Using Claude's memory feature to store project context greatly improved consistency across conversations.

4. **Bilingual Takes Time**: Creating both language versions doubles the work but makes the package more accessible.

5. **GitHub Integration is Essential**: Pushing after each phase prevents work loss and enables collaboration.

---

## Template: Starting a New Skill Package Project

### Initial Prompt
```
I want to create a comprehensive skill package for [TECHNOLOGY] that will 
enable Claude instances to generate correct [TECHNOLOGY] code.

Let's start with deep research:
1. What are all the major mechanisms/APIs in [TECHNOLOGY]?
2. What are common pitfalls and anti-patterns?
3. What version differences exist?

Document your findings - this will become our preliminary research.
```

### After Research
```
Based on our research, let's define requirements:
1. What skills do we need? (syntax, implementation, error handling, agents?)
2. What languages should we support?
3. What quality guarantees do we want to provide?

Then create a detailed masterplan with phases and prompts.
```

### For Each Phase
```
Execute Phase [X.Y]: [Name]

Follow the masterplan prompt. After completion:
1. Validate all outputs
2. Commit: "Phase [X.Y]: [description]"
3. Push to GitHub
4. Verify repository state
```

---

## Conclusion

This methodology transforms the challenge of creating comprehensive AI skill packages into a manageable, systematic process. By emphasizing research, planning, and version control, it ensures that the resulting skills are:

- **Accurate**: Based on verified information
- **Deterministic**: Providing clear guidance
- **Complete**: Covering all relevant aspects
- **Maintainable**: Organized and version-controlled

The key insight is that **skills are only as good as the research behind them**. Invest time in understanding the technology deeply before attempting to codify that knowledge into skills.

---

*This methodology was developed during the ERPNext/Frappe Skills Package project by the OpenAEC Foundation, January 2025.*
