# Claude Desktop Installation Guide

Install the ERPNext Skills Package in the Claude Desktop application.

## Prerequisites

- **Plan**: Pro, Max, Team, or Enterprise
- **Feature**: Code Execution must be enabled
- **App**: Claude Desktop app installed ([download](https://claude.ai/download))

## Installation Steps

The Claude Desktop app uses the same skill system as Claude.ai web. Follow these steps:

### Step 1: Enable Code Execution

1. Open Claude Desktop
2. Click the **Settings** icon (gear)
3. Navigate to **Capabilities**
4. Enable **Code execution and file creation**

### Step 2: Upload Skills

1. Download skills from the repository:
   - Pre-packaged: `skills/packaged/*.skill`
   - Or ZIP the skill folders manually

2. In Claude Desktop, go to **Settings** > **Capabilities**

3. Scroll to **Skills** section

4. Click **Upload skill** and select your file

5. Repeat for each skill

### Step 3: Verify

Start a new conversation and ask:
```
What ERPNext skills do you have access to?
```

## Syncing with Claude.ai Web

Skills uploaded in Claude Desktop **sync automatically** with Claude.ai web (and vice versa) since they share the same account settings.

Upload once, use everywhere (except mobile).

## Offline Usage

Skills are stored in your account settings. Once loaded into a conversation, they work offline until the conversation ends.

However, uploading new skills requires an internet connection.

## Desktop-Specific Features

### Keyboard Shortcuts

- `Cmd/Ctrl + N` - New conversation
- `Cmd/Ctrl + ,` - Open settings

### File Handling

Claude Desktop can read files directly from your system when you drag-and-drop or use the attachment button. Combined with skills, you can:

1. Drop an ERPNext Python file
2. Ask: "Review this controller using ERPNext best practices"
3. Claude uses the `agent-code-review` skill automatically

## Recommended Workflow

For ERPNext development with Claude Desktop:

1. **Install skills** once (they persist)
2. **Create a Project** for your ERPNext work
3. **Add project docs** (custom app structure, requirements)
4. **Use skills** for code generation and review

Projects + Skills = Powerful combination:
- Projects provide context (your specific app)
- Skills provide expertise (ERPNext patterns)

## Troubleshooting

### Skills not appearing after upload

1. Restart Claude Desktop
2. Check Settings > Capabilities > Skills
3. Ensure the skill toggle is ON

### App crashes on skill upload

1. Check ZIP file isn't corrupted
2. Ensure ZIP structure is correct (folder at root)
3. Try a smaller skill first to test

### Skills from web not showing

1. Sign out and sign back in
2. Check internet connection
3. Wait a few minutes for sync

## System Requirements

| OS | Minimum Version |
|----|-----------------|
| macOS | 11.0 (Big Sur) |
| Windows | 10 (64-bit) |
| Linux | Ubuntu 20.04+ |

## Next Steps

- Read [USAGE.md](../../USAGE.md) for skill overview
- See [claude-web.md](claude-web.md) for detailed upload instructions
- Review [LESSONS_LEARNED.md](../../LESSONS_LEARNED.md) for common pitfalls
