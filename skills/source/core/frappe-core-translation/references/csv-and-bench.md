# CSV Format, Bench Commands, and Custom App Translations

## CSV Translation Files

### File Location

```
apps/{app}/{app}/translations/{lang}.csv
```

Examples:
- `apps/erpnext/erpnext/translations/nl.csv` — Dutch translations for ERPNext
- `apps/myapp/myapp/translations/de.csv` — German translations for custom app

### CSV Format Specification

```csv
"source","translation","context"
"Sales Invoice","Verkoopfactuur",""
"Change","Wisselgeld","Coins"
"Change","Wijziging","Amendment"
"Created {0} records","Er zijn {0} records aangemaakt",""
```

### CSV Rules

| Rule | Details |
|------|---------|
| Encoding | ALWAYS UTF-8, no BOM |
| Quoting | ALWAYS double-quote ALL fields |
| Columns | Exactly 3: source, translation, context |
| Header | No header row — first row is data |
| Context | Empty string `""` when not needed (column MUST be present) |
| Placeholders | Keep `{0}`, `{1}` in translations — NEVER translate placeholders |
| Escaping | Use `""` to escape literal quotes: `"He said ""hello"""` |
| Line endings | LF or CRLF (Frappe handles both) |
| Sorting | No required order (but alphabetical by source is conventional) |

### Auto-Discovery

CSV files in the `translations/` directory are auto-discovered by Frappe. No `hooks.py` registration is needed.

### Language Codes

ALWAYS use standard language codes:

| Code | Language | Code | Language |
|------|----------|------|----------|
| `ar` | Arabic | `ja` | Japanese |
| `de` | German | `ko` | Korean |
| `es` | Spanish | `nl` | Dutch |
| `fr` | French | `pt` | Portuguese |
| `hi` | Hindi | `pt-BR` | Brazilian Portuguese |
| `it` | Italian | `zh` | Chinese (Simplified) |

Parent language fallback: `pt-BR` falls back to `pt` if a string is not found in `pt-BR`.

---

## PO/MO Files [v15+]

### File Location

```
apps/{app}/{app}/locale/{lang}/LC_MESSAGES/{app}.po   # Source (editable)
apps/{app}/{app}/locale/{lang}/LC_MESSAGES/{app}.mo   # Compiled (binary)
apps/{app}/{app}/locale/{app}.pot                      # Template (source strings)
```

### PO File Format (GNU gettext)

```po
# Translation for ERPNext
# Copyright (C) 2024 OpenAEC Foundation
msgid ""
msgstr ""
"Content-Type: text/plain; charset=UTF-8\n"
"Content-Transfer-Encoding: 8bit\n"

#: erpnext/selling/doctype/sales_invoice/sales_invoice.py:45
msgid "Sales Invoice"
msgstr "Verkoopfactuur"

#: erpnext/accounts/utils.py:120
msgctxt "Coins"
msgid "Change"
msgstr "Wisselgeld"

#: erpnext/accounts/utils.py:125
msgctxt "Amendment"
msgid "Change"
msgstr "Wijziging"

#: erpnext/stock/doctype/item/item.py:78
#, python-format
msgid "Created {0} records in {1}"
msgstr "Er zijn {0} records aangemaakt in {1}"
```

### PO vs CSV

| Aspect | CSV (v14+) | PO/MO (v15+) |
|--------|-----------|--------------|
| Format | Simple 3-column | Standard gettext |
| Tools | Text editor | Poedit, Weblate, Transifex |
| Source refs | None | File:line references |
| Compilation | Not needed | `bench compile-po-to-mo` required |
| Priority | Lower than MO | Higher than CSV |
| Recommended | Legacy / simple apps | New apps on v15+ |

### Migration from CSV to PO

```bash
# One-time migration — preserves all existing translations
bench migrate-csv-to-po --app {app}

# After migration, both CSV and PO can coexist
# MO files take priority over CSV at runtime
```

---

## Bench Commands

### Extract Untranslated Strings (All Versions)

```bash
# Export all untranslated strings for a language
bench --site {site} get-untranslated {lang} {output_file}

# Example
bench --site mysite.localhost get-untranslated nl untranslated-nl.csv
```

Output is a CSV file with untranslated source strings that you fill in.

### Import Translations (All Versions)

```bash
# Import completed translations
bench update-translations {lang} {untranslated_file} {translated_file}

# Example
bench update-translations nl untranslated-nl.csv translated-nl.csv
```

### Generate POT File [v15+]

```bash
# Generate .pot template with all extractable strings
bench generate-pot-file --app {app}

# Output: apps/{app}/{app}/locale/{app}.pot
# This is the "master template" — copy it to create new .po files
```

### Migrate CSV to PO [v15+]

```bash
# Convert existing CSV translations to PO format
bench migrate-csv-to-po --app {app}

# Creates PO files in apps/{app}/{app}/locale/{lang}/LC_MESSAGES/
```

### Compile PO to MO [v15+]

```bash
# Compile .po to binary .mo (REQUIRED for runtime use)
bench compile-po-to-mo --app {app}

# ALWAYS run this after editing .po files
# Without .mo files, PO translations are NOT loaded at runtime
```

### Clear Translation Cache

```bash
# ALWAYS clear cache after adding/modifying translations
bench --site {site} clear-cache
```

---

## Custom App Translation Workflow

### Complete Setup for a New Custom App

#### Step 1: Write Translatable Code

```python
# In your Python files
class MyController(Document):
    def validate(self):
        if not self.customer:
            frappe.throw(_("Customer is required for {0}").format(self.name))

        frappe.msgprint(_("Validation complete"))
```

```javascript
// In your JavaScript files
frappe.ui.form.on("My DocType", {
    refresh(frm) {
        frm.set_intro(__("Fill in all required fields before submitting"));
    },

    validate(frm) {
        if (!frm.doc.customer) {
            frappe.throw(__("Customer is required for {0}", [frm.doc.name]));
        }
    }
});
```

#### Step 2: Create Translation Directory

```bash
# For CSV (all versions)
mkdir -p apps/{app}/{app}/translations

# For PO [v15+]
# Directories are auto-created by bench generate-pot-file
```

#### Step 3: Extract Strings

```bash
# v14: Export untranslated
bench --site {site} get-untranslated nl untranslated.csv

# v15+: Generate POT template
bench generate-pot-file --app myapp
```

#### Step 4: Translate

For CSV: Edit the CSV file directly, adding translations in the second column.

For PO [v15+]:
1. Copy `.pot` to `locale/{lang}/LC_MESSAGES/{app}.po`
2. Edit with Poedit or any text editor
3. Fill in `msgstr` for each `msgid`

#### Step 5: Deploy

```bash
# For PO [v15+] — compile first
bench compile-po-to-mo --app myapp

# Clear cache (ALWAYS)
bench --site {site} clear-cache
```

#### Step 6: Verify

```python
# In bench console
bench --site {site} console

>>> frappe.local.lang = "nl"
>>> print(_("Customer is required for {0}").format("INV-001"))
# Should print Dutch translation
```

---

## Translation DocType (User Overrides)

The Translation DocType allows site administrators to override any translation at runtime without touching app code.

### Fields

| Field | Type | Description |
|-------|------|-------------|
| `source_text` | Data | Original English string |
| `translated_text` | Data | Translated string |
| `language` | Link (Language) | Target language code |
| `context` | Data | Optional disambiguation context |

### Priority

Translation DocType entries have the **HIGHEST priority** — they override both CSV and PO/MO translations.

### API Access

```python
# Add/update a user translation programmatically
doc = frappe.get_doc({
    "doctype": "Translation",
    "source_text": "Sales Invoice",
    "translated_text": "Factuur",
    "language": "nl",
    "context": ""
})
doc.insert(ignore_permissions=True)
frappe.clear_cache()  # ALWAYS clear after modifying translations
```

---

## Contributing Translations to Frappe/ERPNext

For contributing translations back to the Frappe or ERPNext repositories:

1. Use the [Frappe Weblate instance](https://translate.erpnext.com/) for community translations
2. NEVER submit PRs with CSV changes directly — use Weblate
3. For custom apps: include translations in your app's `translations/` or `locale/` directory
