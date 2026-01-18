# Claude.ai Web Installation Guide

Install the ERPNext Skills Package in the Claude.ai web interface.

## Prerequisites

- **Plan**: Pro, Max, Team, or Enterprise
- **Feature**: Code Execution must be enabled

## Step 1: Enable Code Execution

1. Go to **Settings** (gear icon)
2. Navigate to **Capabilities**
3. Enable **Code execution and file creation**

## Step 2: Download Skills

### Option A: Download Pre-packaged Skills

Download the `.skill` files from the repository:

```
skills/packaged/
├── syntax-client-scripts.skill
├── syntax-server-scripts.skill
├── syntax-controllers.skill
... (28 .skill files)
```

Each `.skill` file is a ZIP archive ready for upload.

### Option B: Create ZIP Files Manually

For each skill you want to install:

1. Download the skill folder (e.g., `syntax-server-scripts/`)
2. Create a ZIP file with the folder as root:
   ```
   syntax-server-scripts.zip
   └── syntax-server-scripts/
       ├── SKILL.md
       └── references/
           └── ...
   ```

**Important**: The ZIP must contain the skill folder, not just its contents.

## Step 3: Upload Skills

1. Go to **Settings** > **Capabilities**
2. Scroll to the **Skills** section
3. Click **Upload skill**
4. Select your `.skill` or `.zip` file
5. Repeat for each skill you want to install

## Step 4: Verify Installation

1. Start a new conversation
2. Ask: "What ERPNext skills do you have access to?"
3. Claude should list your installed skills

## Managing Skills

### Toggle Skills On/Off

In **Settings** > **Capabilities** > **Skills**, use the toggle switch next to each skill to enable or disable it.

### Remove a Skill

1. Go to **Settings** > **Capabilities** > **Skills**
2. Find the skill you want to remove
3. Click the delete/remove option
4. Confirm deletion

## Recommended Installation Order

For most ERPNext development work, install these skills first:

### Essential (Start Here)
1. `syntax-server-scripts` - Server Script sandbox rules
2. `core-database` - Database operations
3. `impl-server-scripts` - Server Script workflows

### Extended (Add as Needed)
4. `syntax-client-scripts` - Client Script patterns
5. `syntax-controllers` - Controller methods
6. `core-permissions` - Permission system
7. `errors-server` - Server error handling

### Full Package
Install all 28 skills for comprehensive coverage.

## Skill Name Requirements

If you're creating ZIPs manually, ensure:

- Folder name is **lowercase**
- Only letters, numbers, and **hyphens** allowed
- Example: `syntax-server-scripts` ✅
- Example: `Syntax_Server_Scripts` ❌

## Team and Enterprise Plans

### Organization-Wide Skills

Admins can provision skills for all users:

1. Go to **Admin Settings** > **Capabilities**
2. Upload skills in the organization section
3. Skills appear for all users with a team indicator

### Individual Skills

Users can still upload personal skills that are private to their account.

## Troubleshooting

### "Skills appear greyed out"

- Check that Code Execution is enabled
- For Team/Enterprise: Check with your admin that Skills are enabled org-wide

### Upload fails

1. Check ZIP structure (folder must be at root)
2. Verify SKILL.md starts with `---` on line 1
3. Ensure skill name is lowercase with hyphens

### Skill doesn't trigger

- Make your request more specific
- Mention the skill type: "Using Server Script patterns..."
- Check that the skill is toggled ON in settings

## Storage and Privacy

- Custom skills are **private** to your account
- Skills run in Claude's secure sandboxed environment
- No data persists between sessions

## Next Steps

- Read [USAGE.md](../../USAGE.md) for skill overview
- Check individual skill documentation in `skills/source/*/SKILL.md`
- Review [LESSONS_LEARNED.md](../../LESSONS_LEARNED.md) for common pitfalls
