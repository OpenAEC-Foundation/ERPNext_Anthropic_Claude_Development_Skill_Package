# Translation API Reference

## Python: `_()`

### Signature

```python
frappe._(msg: str, lang: str | None = None, context: str | None = None) -> str
```

The `_` function is imported globally in Frappe. No explicit import needed in `.py` files within a Frappe app.

### Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `msg` | `str` | required | Source string to translate (MUST be a string literal) |
| `lang` | `str \| None` | `None` | Override language (defaults to user's language or `frappe.local.lang`) |
| `context` | `str \| None` | `None` | Disambiguation context for identical source strings |

### Basic Usage

```python
# Simple translation
title = _("Sales Invoice")

# With positional substitution — ALWAYS use .format()
message = _("Created {0} records in {1}").format(count, doctype)

# With context for disambiguation
label1 = _("Change", context="Coins")    # Wisselgeld (Dutch)
label2 = _("Change", context="Amendment") # Wijziging (Dutch)

# Force specific language
german_title = _("Sales Invoice", lang="de")
```

### Positional Placeholders

ALWAYS use `{0}`, `{1}`, `{2}` etc. for substitutions:

```python
# One placeholder
_("Welcome {0}").format(user_name)

# Multiple placeholders
_("{0} of {1} completed").format(done, total)

# Reuse same placeholder
_("{0} created {0}'s profile").format(user_name)
```

### Where _() Is Available

| Context | Available | Notes |
|---------|-----------|-------|
| Controller `.py` files | Yes | Auto-imported |
| `hooks.py` | Yes | But AVOID translating hook values |
| Jinja `.html` templates | Yes | Use `{{ _("text") }}` |
| Whitelisted API methods | Yes | Auto-imported |
| Standalone scripts | No | Must `import frappe` first |

---

## Python: `_lt()` (Lazy Translation) [v15+]

### Signature

```python
frappe._lt(msg: str, context: str | None = None) -> LazyTranslator
```

### Purpose

`_lt()` returns a `LazyTranslator` object that defers translation until the string is actually used (cast to `str`). This is REQUIRED for module-level constants because at module load time, `frappe.local.lang` may not be set yet.

### Usage

```python
# Module-level constant — ALWAYS use _lt() here [v15+]
STATUS_LABELS = {
    "open": _lt("Open"),
    "closed": _lt("Closed"),
    "pending": _lt("Pending", context="Status"),
}

# Translation happens when the string is rendered
def get_status_label(status):
    return str(STATUS_LABELS[status])  # Translated at this point
```

### When to Use _lt() vs _()

| Scenario | Use | Why |
|----------|-----|-----|
| Inside a function/method | `_()` | Language context is available |
| Module-level constant | `_lt()` [v15+] | Language not set at import time |
| Class attribute | `_lt()` [v15+] | Same as module-level |
| Default function argument | `_lt()` [v15+] | Evaluated at definition time |

### v14 Workaround (No _lt())

```python
# v14: Move constants inside functions
def get_status_labels():
    return {
        "open": _("Open"),
        "closed": _("Closed"),
    }
```

---

## JavaScript: `__()`

### Signature

```javascript
__(msg, substitutions, context)
```

### Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `msg` | `string` | required | Source string to translate (MUST be a string literal) |
| `substitutions` | `Array \| null` | `null` | Array of values for `{0}`, `{1}`, etc. |
| `context` | `string \| null` | `null` | Disambiguation context |

### Basic Usage

```javascript
// Simple translation
let title = __("Sales Invoice");

// With substitutions — ALWAYS pass as array
let message = __("Created {0} records", [count]);

// Multiple substitutions
let msg = __("{0} of {1} completed", [done, total]);

// With context
let label = __("Change", null, "Coins");

// With both substitutions and context
let text = __("Deleted {0}", [name], "Action");
```

### Where __() Is Available

| Context | Available | Notes |
|---------|-----------|-------|
| `.js` files (client-side) | Yes | Globally available |
| `.vue` files `<script>` | Yes | Globally available |
| `.vue` files `<template>` | Yes | Use `{{ __("text") }}` |
| Node.js / server-side JS | No | Frappe does not support server-side JS translation |

### Substitution Array Rules

```javascript
// CORRECT: Array with positional values
__("Hello {0}, you have {1} items", [user_name, item_count]);

// CORRECT: null substitutions when only context needed
__("Open", null, "Status");

// WRONG: Object substitutions — NOT supported
__("Hello {name}", {name: user_name});  // WILL NOT WORK

// WRONG: No array — second arg treated as substitutions
__("Hello", "context");  // "context" is NOT treated as context!
```

---

## Jinja Templates

### In `.html` files (Jinja2)

```html
<!-- Simple -->
<h1>{{ _("Sales Invoice") }}</h1>

<!-- With substitution -->
<p>{{ _("Created {0} records").format(count) }}</p>

<!-- With context -->
<span>{{ _("Change", context="Coins") }}</span>

<!-- In attributes -->
<input placeholder="{{ _('Search') }}">

<!-- Conditional -->
{% if is_new %}
    {{ _("New Record") }}
{% else %}
    {{ _("Existing Record") }}
{% endif %}
```

### In Print Formats (Jinja)

```html
<!-- Print format specific -->
<div class="print-heading">{{ _("Tax Invoice") }}</div>
<td>{{ _("Item") }}</td>
<td>{{ _("Quantity") }}</td>
```

---

## Translation Loading

### How Frappe Loads Translations at Runtime

1. **Boot**: `frappe.get_lang_dict()` loads all translations for current language
2. **Merge order** (last wins):
   - Framework translations (frappe app)
   - Installed app translations (in app install order)
   - User translations (Translation DocType)
3. **Cache**: Translations cached in Redis; cleared on `bench clear-cache`

### Force Language for a Block

```python
# Temporarily switch language
with frappe.utils.change_language("de"):
    german_text = _("Sales Invoice")
    # All _() calls inside this block use German

# Back to original language here
```

### Get Current Language

```python
# Current user's language
lang = frappe.local.lang  # e.g., "nl"

# Specific user's language
lang = frappe.db.get_value("User", user, "language")

# Site default language
lang = frappe.db.get_default("lang") or "en"
```

```javascript
// JavaScript
let lang = frappe.boot.lang;  // e.g., "nl"
```

---

## Number and Date Formatting

Frappe handles number/date localization separately from string translation:

```python
# Number formatting (uses system settings, NOT translation)
from frappe.utils import fmt_money
formatted = fmt_money(1234.56, currency="EUR")  # "€ 1.234,56" (NL)

# Date formatting
from frappe.utils import formatdate
formatted = formatdate("2024-01-15")  # "15-01-2024" (NL)
```

```javascript
// JavaScript
let formatted = format_currency(1234.56, "EUR");
let date = frappe.datetime.str_to_user("2024-01-15");
```

NEVER translate number/date formats manually — ALWAYS use Frappe's formatting utilities.
