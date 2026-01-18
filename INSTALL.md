# ERPNext Skills Package - Installation Guide

> How to install and use the ERPNext Skills Package with Claude.

---

## Installation Methods

### Method 1: Claude.ai Project (Recommended)

The simplest way to use these skills is via Claude.ai Projects.

1. **Create a new Project** in Claude.ai
2. **Upload skills** to Project Knowledge:
   - Upload individual `SKILL.md` files
   - Or upload entire skill folders (SKILL.md + references/)
3. **Start chatting** - Claude will automatically use the relevant skills

**Tip**: Start with the skills you need most frequently. Claude performs best with focused skill sets.

---

### Method 2: Claude Code Plugin

For Claude Code users, install as a plugin marketplace:

```bash
# Register the marketplace
/plugin marketplace add OpenAEC-Foundation/ERPNext_Anthropic_Claude_Development_Skill_Package

# Install all ERPNext skills
/plugin install erpnext-skills@openaec-erpnext-skills
```

After installation, reference skills naturally:
```
"Use the Server Script syntax skill to create a validation for Sales Invoice"
```

---

### Method 3: Manual Integration

For custom setups or API usage:

1. **Clone the repository**:
   ```bash
   git clone https://github.com/OpenAEC-Foundation/ERPNext_Anthropic_Claude_Development_Skill_Package.git
   ```

2. **Navigate to skills**:
   ```
   skills/source/
   ├── syntax/     # 8 skills
   ├── core/       # 3 skills
   ├── impl/       # 8 skills
   ├── errors/     # 7 skills
   └── agents/     # 2 agents
   ```

3. **Include in your system prompt** or context as needed.

---

## Recommended Skill Sets

### For ERPNext Customization
Upload these skills for typical ERPNext customization work:

| Skill Set | Skills to Upload |
|-----------|------------------|
| **Minimal** | syntax-clientscripts, syntax-serverscripts, database |
| **Standard** | + syntax-controllers, syntax-hooks, permissions |
| **Complete** | + all impl-* and errors-* skills |
| **With Agents** | + code-interpreter, code-validator |

### For Custom App Development
```
syntax-customapp
syntax-controllers
syntax-hooks
impl-customapp
impl-controllers
impl-hooks
database
permissions
```

### For API Development
```
syntax-whitelisted
api-patterns
impl-whitelisted
errors-api
permissions
```

---

## Skill Structure

Each skill follows the Agent Skills standard:

```
skill-name/
├── SKILL.md          # Main instructions (<500 lines)
└── references/       # Detailed documentation
    ├── examples.md
    ├── patterns.md
    └── anti-patterns.md
```

**SKILL.md** contains:
- YAML frontmatter with name and description
- Core patterns and decision trees
- Quick reference tables
- Critical rules

**references/** contains:
- Detailed examples
- Complete API documentation
- Anti-patterns to avoid

---

## Usage Tips

### 1. Start with Agents
If unsure which skills you need, start with:
- `code-interpreter` - Analyzes requirements and recommends skills
- `code-validator` - Validates generated code

### 2. Load Progressively
```
Request: "Create a Server Script for invoice validation"

Claude loads:
1. syntax-serverscripts (how to write)
2. database (for queries)
3. impl-serverscripts (workflow)
4. errors-serverscripts (robustness)
```

### 3. Reference Skills Explicitly
You can explicitly request a skill:
```
"Using the erpnext-syntax-controllers skill, show me
 how to implement UUID naming in v16"
```

### 4. Version Awareness
Always specify your Frappe/ERPNext version:
```
"I'm on ERPNext v15. Create a Server Script for..."
```

---

## Critical Knowledge

### Server Script Sandbox Limitation

**⚠️ IMPORTANT**: Server Scripts run in a RestrictedPython sandbox.

```python
# ❌ WRONG - All imports are blocked
from frappe.utils import nowdate
import json

# ✅ CORRECT - Use frappe namespace directly
date = frappe.utils.nowdate()
data = frappe.parse_json(json_string)
```

This is the #1 cause of AI-generated ERPNext code failures. All skills in this package are designed with this limitation in mind.

---

## Troubleshooting

### Skills not being used?
- Ensure SKILL.md is in the root of the skill folder
- Check that the description matches your request
- Try explicitly referencing the skill by name

### Getting outdated patterns?
- Specify your Frappe/ERPNext version
- Ask Claude to check for v16-specific features
- Reference the Version Differences sections

### Code not working?
- Use the `code-validator` agent to validate
- Check the relevant `errors-*` skill for common issues
- Verify sandbox compatibility for Server Scripts

---

## Support

- **GitHub Issues**: [OpenAEC-Foundation/ERPNext_Anthropic_Claude_Development_Skill_Package](https://github.com/OpenAEC-Foundation/ERPNext_Anthropic_Claude_Development_Skill_Package/issues)
- **Documentation**: See INDEX.md for skill overview
- **Dependencies**: See docs/DEPENDENCIES.md for skill relationships

---

*ERPNext Skills Package v1.0 | Last updated: 2026-01-18*
