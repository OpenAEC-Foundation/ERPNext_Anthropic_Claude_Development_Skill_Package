# Custom Bench Commands

## Overview

Frappe apps can register custom CLI commands that run via `bench`. Commands use the [Click](https://click.palletsprojects.com/) framework and are auto-discovered by bench from your app's `commands` module.

---

## Step 1: Create the Commands Module

Place commands in your app at one of these locations:

```
# Single file
frappe-bench/apps/my_app/my_app/commands.py

# Or as a package
frappe-bench/apps/my_app/my_app/commands/__init__.py
```

Bench automatically discovers `commands.py` (or `commands/__init__.py`) in every installed app. No `hooks.py` entry is required for basic discovery.

### Optional: Explicit Registration via hooks.py

If your commands live outside the default `commands` module, register them explicitly:

```python
# hooks.py
commands = [
    "my_app.custom_cli.commands"
]
```

This points bench to a custom module path containing the `commands` list.

---

## Step 2: Write Click Commands

### Minimal Command (No Site Context)

```python
# my_app/commands.py
import click

@click.command("hello")
def hello():
    """Say hello from my_app."""
    click.echo("Hello from my_app!")

commands = [hello]
```

Usage: `bench hello`

### Command With Site Context (Most Common)

Most commands need access to the Frappe database. Use `pass_context` and `get_site` from `frappe.commands`:

```python
# my_app/commands.py
import click
import frappe
from frappe.commands import pass_context, get_site

@click.command("sync-inventory")
@click.option("--warehouse", help="Warehouse name to sync")
@click.option("--dry-run", is_flag=True, help="Preview without changes")
@pass_context
def sync_inventory(context, warehouse=None, dry_run=False):
    """Sync inventory from external system."""
    site = get_site(context)
    frappe.init(site=site)
    frappe.connect()
    try:
        # Your logic here
        filters = {"warehouse": warehouse} if warehouse else {}
        items = frappe.get_all("Item", filters=filters, fields=["name", "item_code"])
        for item in items:
            if not dry_run:
                # perform sync
                pass
            click.echo(f"{'[DRY RUN] ' if dry_run else ''}Synced: {item.item_code}")
    except Exception as e:
        click.echo(f"Error: {e}", err=True)
        raise SystemExit(1)
    finally:
        frappe.destroy()

commands = [sync_inventory]
```

Usage: `bench --site mysite sync-inventory --warehouse "Main" --dry-run`

---

## Step 3: The Site Context Pattern

### CRITICAL: ALWAYS Follow This Pattern

When your command needs database access, you MUST use the init/connect/destroy lifecycle:

```python
@pass_context
def my_command(context, **kwargs):
    site = get_site(context)
    frappe.init(site=site)
    frappe.connect()
    try:
        # ALL your logic goes here
        pass
    finally:
        frappe.destroy()
```

### What Each Step Does

| Step | Purpose |
|------|---------|
| `get_site(context)` | Extracts site name from `--site` flag; raises `SiteNotSpecifiedError` if missing |
| `frappe.init(site)` | Loads site config, sets up module paths |
| `frappe.connect()` | Opens database connection |
| `frappe.destroy()` | Closes DB connection, cleans up thread locals |

### Rules

- **ALWAYS** call `frappe.destroy()` in a `finally` block — leaked connections cause pool exhaustion
- **ALWAYS** use `get_site(context)` — NEVER hardcode site names
- **NEVER** assume `frappe.db` is available without calling `frappe.connect()` first
- **NEVER** call `frappe.init()` more than once per command invocation

---

## Common Command Patterns

### Data Migration Command

```python
@click.command("migrate-legacy-data")
@click.option("--batch-size", default=100, help="Records per batch")
@click.option("--skip-existing", is_flag=True)
@pass_context
def migrate_legacy_data(context, batch_size=100, skip_existing=False):
    """Migrate data from legacy fields to new structure."""
    site = get_site(context)
    frappe.init(site=site)
    frappe.connect()
    try:
        records = frappe.get_all(
            "Sales Invoice",
            filters={"custom_legacy_id": ["is", "set"]},
            fields=["name", "custom_legacy_id"],
            limit_page_length=0
        )
        total = len(records)
        for i in range(0, total, batch_size):
            batch = records[i:i + batch_size]
            for record in batch:
                if skip_existing and frappe.db.exists("New DocType", record.custom_legacy_id):
                    continue
                # migration logic here
                pass
            frappe.db.commit()
            click.echo(f"Processed {min(i + batch_size, total)}/{total}")
        click.echo(f"Migration complete: {total} records processed")
    finally:
        frappe.destroy()
```

### Bulk Operation Command

```python
@click.command("bulk-update-status")
@click.argument("doctype")
@click.argument("status")
@click.option("--filters", help="JSON filters string")
@pass_context
def bulk_update_status(context, doctype, status, filters=None):
    """Bulk update workflow status for documents."""
    import json
    site = get_site(context)
    frappe.init(site=site)
    frappe.connect()
    try:
        filter_dict = json.loads(filters) if filters else {}
        docs = frappe.get_all(doctype, filters=filter_dict, pluck="name")
        for name in docs:
            doc = frappe.get_doc(doctype, name)
            doc.status = status
            doc.flags.ignore_permissions = True
            doc.save()
        frappe.db.commit()
        click.echo(f"Updated {len(docs)} {doctype} records to '{status}'")
    finally:
        frappe.destroy()
```

### Maintenance / Cleanup Command

```python
@click.command("cleanup-old-logs")
@click.option("--days", default=90, help="Delete logs older than N days")
@click.option("--confirm", is_flag=True, help="Actually delete (default is dry run)")
@pass_context
def cleanup_old_logs(context, days=90, confirm=False):
    """Remove old Error Log and Activity Log entries."""
    from frappe.utils import add_days, now_datetime
    site = get_site(context)
    frappe.init(site=site)
    frappe.connect()
    try:
        cutoff = add_days(now_datetime(), -days)
        for doctype in ["Error Log", "Activity Log", "Scheduled Job Log"]:
            count = frappe.db.count(doctype, {"creation": ["<", cutoff]})
            if confirm:
                frappe.db.delete(doctype, {"creation": ["<", cutoff]})
                frappe.db.commit()
                click.echo(f"Deleted {count} {doctype} records older than {days} days")
            else:
                click.echo(f"[DRY RUN] Would delete {count} {doctype} records older than {days} days")
        if not confirm:
            click.echo("Pass --confirm to actually delete records")
    finally:
        frappe.destroy()
```

---

## Multiple Commands in a Package

For apps with many commands, organize as a package:

```
my_app/commands/
├── __init__.py          # Aggregates all commands
├── data_commands.py     # Data migration commands
└── maintenance.py       # Maintenance commands
```

```python
# my_app/commands/__init__.py
from my_app.commands.data_commands import commands as data_commands
from my_app.commands.maintenance import commands as maintenance_commands

commands = data_commands + maintenance_commands
```

```python
# my_app/commands/data_commands.py
import click
from frappe.commands import pass_context, get_site

@click.command("import-data")
@pass_context
def import_data(context):
    # ...
    pass

commands = [import_data]
```

---

## Click Features Reference

### Useful Decorators and Types

| Feature | Example | Purpose |
|---------|---------|---------|
| `@click.option` | `--limit 100` | Named parameters with defaults |
| `@click.argument` | Positional arg | Required positional parameters |
| `@click.option(is_flag=True)` | `--verbose` | Boolean flags |
| `@click.option(type=click.Choice([...]))` | `--format csv` | Constrained choices |
| `@click.option(type=click.Path(exists=True))` | `--file /path` | File path validation |
| `@click.confirmation_option` | `--yes` | Skip confirmation prompt |
| `click.echo()` | Output text | Use instead of `print()` |
| `click.secho(..., fg="green")` | Colored output | Styled terminal output |
| `click.progressbar()` | Progress bar | Visual progress for long operations |

### Progress Bar Example

```python
with click.progressbar(records, label="Processing") as bar:
    for record in bar:
        # process each record
        pass
```

---

## Best Practices

1. **ALWAYS** use `frappe.destroy()` in `finally` — prevents connection leaks
2. **ALWAYS** commit in batches for bulk operations — prevents long-running transactions
3. **ALWAYS** provide `--dry-run` flags for destructive operations
4. **ALWAYS** use `click.echo()` instead of `print()` — respects output redirection
5. **NEVER** import `frappe` at module level if using `pass_context` — import inside the function or at top level but only use after `frappe.init()`
6. **NEVER** forget to export the `commands` list — bench silently ignores modules without it
7. **ALWAYS** add docstrings to commands — they appear in `bench --help` output
8. **ALWAYS** handle `KeyboardInterrupt` gracefully for long-running commands

---

## Troubleshooting

| Problem | Cause | Fix |
|---------|-------|-----|
| Command not found | Missing `commands` list export | Add `commands = [my_command]` at module level |
| `SiteNotSpecifiedError` | No `--site` flag passed | Use `bench --site mysite my-command` |
| `ImportError` on command | App not installed on bench | Run `bench get-app` and `bench install-app` |
| DB connection errors | Missing `frappe.connect()` | Add `frappe.init(site)` + `frappe.connect()` before DB access |
| Stale data after command | Missing `frappe.db.commit()` | ALWAYS commit after write operations |
| Command hangs on exit | Missing `frappe.destroy()` | ALWAYS call in `finally` block |
