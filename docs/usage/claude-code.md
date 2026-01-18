# Claude Code Installation Guide

Install the ERPNext Skills Package in Claude Code for terminal-based development.

## Installation Methods

### Method 1: Personal Skills (Recommended)

Personal skills are available across all your projects.

```bash
# Clone the repository
git clone https://github.com/OpenAEC-Foundation/ERPNext_Anthropic_Claude_Development_Skill_Package.git

# Copy skills to personal directory
cp -r ERPNext_Anthropic_Claude_Development_Skill_Package/skills/source/* ~/.claude/skills/

# Verify installation
ls ~/.claude/skills/
```

Expected output:
```
syntax-client-scripts/
syntax-server-scripts/
syntax-controllers/
... (28 skill folders)
```

### Method 2: Project Skills (Team Sharing)

Project skills are committed to version control and shared with your team.

```bash
# In your ERPNext project directory
mkdir -p .claude/skills

# Copy skills
cp -r /path/to/ERPNext_Anthropic_Claude_Development_Skill_Package/skills/source/* .claude/skills/

# Commit to version control
git add .claude/skills
git commit -m "Add ERPNext development skills"
```

### Method 3: Selective Installation

Install only the skills you need:

```bash
# Example: Install only Server Script related skills
cp -r skills/source/syntax-server-scripts ~/.claude/skills/
cp -r skills/source/impl-server-scripts ~/.claude/skills/
cp -r skills/source/errors-server ~/.claude/skills/
```

## Verification

Start Claude Code and verify skills are loaded:

```bash
claude
```

Then ask:
```
What ERPNext skills do you have access to?
```

Claude should list all installed skills with their descriptions.

## Skill Priority

If the same skill exists in multiple locations, priority is (highest first):

1. **Managed** - Organization admin settings
2. **Personal** - `~/.claude/skills/`
3. **Project** - `.claude/skills/`
4. **Plugin** - Marketplace plugins

## Using with CLAUDE.md

Create a `CLAUDE.md` in your project root for project-specific context:

```markdown
# ERPNext Project Configuration

## Framework Version
This project uses Frappe/ERPNext v15.

## Coding Standards
- Use Server Scripts only for simple validations
- Prefer Controllers for complex business logic
- Always handle permissions explicitly

## Custom Apps
- `custom_app/` - Our custom ERPNext app
```

## Troubleshooting

### Skills not appearing

1. Check YAML syntax in SKILL.md files:
   ```bash
   head -10 ~/.claude/skills/syntax-server-scripts/SKILL.md
   ```
   
2. Run Claude with debug mode:
   ```bash
   claude --debug
   ```

3. Verify file permissions:
   ```bash
   ls -la ~/.claude/skills/
   ```

### Wrong skill triggered

Make your request more specific. Instead of:
```
Help me with a script
```

Use:
```
Help me create a Server Script for Sales Order validation
```

### Scripts not executing

Ensure execute permissions:
```bash
chmod +x ~/.claude/skills/*/scripts/*.py 2>/dev/null
```

## Updating Skills

```bash
cd ERPNext_Anthropic_Claude_Development_Skill_Package
git pull
cp -r skills/source/* ~/.claude/skills/
```

## Monorepo Support

Claude Code automatically discovers skills in nested directories. If you're editing files in `packages/erpnext-custom/`, Claude also looks for skills in `packages/erpnext-custom/.claude/skills/`.

## Next Steps

- Read [USAGE.md](../../USAGE.md) for skill overview
- Check individual skill documentation in `skills/source/*/SKILL.md`
- Review [LESSONS_LEARNED.md](../../LESSONS_LEARNED.md) for common pitfalls
