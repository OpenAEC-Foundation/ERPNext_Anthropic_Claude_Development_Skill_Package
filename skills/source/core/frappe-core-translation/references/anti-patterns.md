# Translation Anti-Patterns

Common mistakes that break string extraction, produce untranslatable strings, or cause runtime translation failures.

---

## Python Anti-Patterns

### AP-01: f-strings Inside _()

```python
# WRONG — f-string is evaluated BEFORE _(), extractor sees dynamic string
_(f"Hello {user_name}")
_(f"Created {count} items in {doctype}")

# CORRECT — literal string is extractable, .format() applied AFTER translation
_("Hello {0}").format(user_name)
_("Created {0} items in {1}").format(count, doctype)
```

**Why it breaks**: The Babel extractor parses the AST looking for `_("literal string")`. An f-string is an `ast.JoinedStr` node, not an `ast.Constant` — the extractor skips it entirely. The string NEVER appears in CSV/POT files.

---

### AP-02: String Concatenation Inside _()

```python
# WRONG — extractor sees _("Hello ") but not the full sentence
_("Hello " + user_name)
_("Created " + str(count) + " items")

# CORRECT
_("Hello {0}").format(user_name)
_("Created {0} items").format(count)
```

**Why it breaks**: The extractor only captures the string literal argument. `"Hello " + user_name` is a `BinOp` node, not a string constant. Even if it did extract `"Hello "`, translators cannot translate a sentence fragment.

---

### AP-03: Old-Style % Formatting Inside _()

```python
# WRONG — %s formatting is not extractable in all versions
_("Welcome %s") % user_name
_("Item %s: %d in stock") % (item_code, qty)

# CORRECT
_("Welcome {0}").format(user_name)
_("Item {0}: {1} in stock").format(item_code, qty)
```

**Why it breaks**: While `_("Welcome %s")` IS extractable (it is a string literal), the `%s` pattern causes problems: (1) translators may accidentally remove or reorder `%s` tokens, (2) positional `{0}` is clearer for translators who may need to reorder arguments for grammar, (3) Frappe convention is `.format()` exclusively.

---

### AP-04: Variables as _() Argument

```python
# WRONG — variable value unknown at extraction time
msg = "Hello World"
_(msg)

label = get_label_for(doctype)
_(label)

# CORRECT — use string literals
_("Hello World")

# If dynamic, ensure the source strings are extracted elsewhere
# and use _() at the point where the string is known
_("Sales Invoice")  # Extracted because it's a literal
```

**Why it breaks**: The extractor sees `_(msg)` — it cannot resolve what `msg` contains. The string is never added to the translation file.

**Exception**: DocType names passed to `_()` work at runtime because DocType labels are auto-extracted from JSON. But AVOID this pattern — it is fragile and confusing.

---

### AP-05: Spaces in Source Strings

```python
# WRONG — leading/trailing spaces are trimmed during extraction
_(" Hello World ")
_("  Sales Invoice  ")

# CORRECT — no leading/trailing spaces
_("Hello World")
_("Sales Invoice")
```

**Why it breaks**: The extractor or translation loader may strip whitespace, creating a mismatch between the extracted key and the runtime lookup key. The translation silently fails and returns the English string.

---

### AP-06: Multiline Strings

```python
# WRONG — newlines in source string cause extraction issues
_("This is a very long message that spans "
  "multiple lines in the source code")

# ACTUALLY OK — Python concatenates adjacent string literals at compile time
# The above IS extractable because Python sees it as one string.
# But AVOID it for clarity — use a single line or a variable:

# PREFERRED
_("This is a very long message that spans multiple lines in the source code")
```

**Note**: Adjacent string literal concatenation (without `+`) works because Python resolves it at compile time into a single `ast.Constant`. However, some older Frappe extractors may not handle this correctly. For safety, use single-line strings.

---

### AP-07: Ternary/Conditional Inside _()

```python
# WRONG — extractor may not handle conditional expression
_("item" if count == 1 else "items")

# CORRECT — translate each variant separately
_("item") if count == 1 else _("items")

# BETTER — use a complete sentence
_("{0} item").format(count) if count == 1 else _("{0} items").format(count)
```

---

### AP-08: _lt() on v14

```python
# WRONG — _lt() does not exist on v14
STATUS = _lt("Pending")  # NameError on v14

# CORRECT for v14 — wrap in a function
def get_status_label():
    return _("Pending")

# CORRECT for v15+ — _lt() is available
STATUS = _lt("Pending")
```

---

## JavaScript Anti-Patterns

### AP-09: Template Literals in __()

```javascript
// WRONG — template literal is not extractable
__(`Hello ${user_name}`)
__(`Created ${count} items in ${doctype}`)

// CORRECT — string literal with array substitutions
__("Hello {0}", [user_name])
__("Created {0} items in {1}", [count, doctype])
```

**Why it breaks**: The JS extractor (both regex in v14 and Babel tokenizer in v15+) looks for `__("...")` or `__('...')`. A template literal `` __(`...`) `` uses backticks, which the extractor does not match. The string is never extracted.

---

### AP-10: Concatenation in __()

```javascript
// WRONG
__("Hello " + user_name)
__("Item: " + item_code + " (" + qty + " in stock)")

// CORRECT
__("Hello {0}", [user_name])
__("Item: {0} ({1} in stock)", [item_code, qty])
```

---

### AP-11: Missing Array Wrapper for Substitutions

```javascript
// WRONG — second argument should be an array
__("Hello {0}", user_name)

// CORRECT
__("Hello {0}", [user_name])
```

**Why it breaks**: Without the array wrapper, Frappe's substitution logic may not correctly replace `{0}`. The behavior is undefined and version-dependent.

---

### AP-12: Confusing Substitutions with Context

```javascript
// WRONG — "Status" is treated as substitutions, not context
__("Open", "Status")

// CORRECT — null for substitutions, then context
__("Open", null, "Status")

// CORRECT — empty array also works
__("Open", [], "Status")
```

---

### AP-13: Dynamic String Construction Before __()

```javascript
// WRONG — variable not extractable
let key = "Sales " + doc_type;
__(key)

// WRONG — computed property
__(messages[error_code])

// CORRECT — use known string literals
__("Sales Invoice")
__("Sales Order")
```

---

## HTML/Jinja Anti-Patterns

### AP-14: Jinja Expressions Inside _()

```html
<!-- WRONG — Jinja variable inside _() -->
{{ _("Hello " + user) }}

<!-- CORRECT -->
{{ _("Hello {0}").format(user) }}
```

---

### AP-15: Translating HTML Tags

```html
<!-- WRONG — HTML tags should not be inside translatable strings -->
{{ _("<b>Important</b>: Fill all fields") }}

<!-- CORRECT — keep HTML outside, translate text only -->
<b>{{ _("Important") }}</b>: {{ _("Fill all fields") }}
```

**Why it breaks**: (1) HTML in translation strings confuses translators, (2) different languages may need different markup, (3) if a translator accidentally modifies the HTML, it breaks the UI.

---

### AP-16: Translating Whitespace-Sensitive Strings

```html
<!-- WRONG -->
{{ _("  Total:  ") }}

<!-- CORRECT -->
{{ _("Total:") }}
```

---

## General Anti-Patterns

### AP-17: Translating System Identifiers

```python
# WRONG — DocType names, field names, and status values are system identifiers
_("Sales Invoice")  # As a DocType name in frappe.get_doc()
frappe.get_doc(_("Sales Invoice"), name)  # WILL FAIL

# CORRECT — only translate for DISPLAY, never for LOGIC
frappe.get_doc("Sales Invoice", name)  # English DocType name for API
label = _("Sales Invoice")  # Translated for display only
```

---

### AP-18: Translating Inside frappe.throw() Without _()

```python
# WRONG — error message not translatable
frappe.throw("Customer is required")

# CORRECT — wrap in _()
frappe.throw(_("Customer is required"))

# CORRECT — with substitution
frappe.throw(_("Customer is required for {0}").format(doc.name))
```

ALWAYS wrap user-facing strings in `_()` or `__()`. This includes:
- `frappe.throw()`
- `frappe.msgprint()`
- `frappe.publish_realtime()` messages
- Dialog titles and messages
- Page titles and breadcrumbs

---

### AP-19: Splitting Sentences Across Multiple _() Calls

```python
# WRONG — translators cannot see full sentence
msg = _("You have") + " " + str(count) + " " + _("items in cart")

# CORRECT — one translatable unit per sentence
msg = _("You have {0} items in cart").format(count)
```

**Why it breaks**: Different languages have different word order. "You have 5 items" in Japanese is "5個のアイテムがあります" — the number comes first. Splitting the sentence makes correct translation impossible.

---

### AP-20: Forgetting to Clear Cache After Translation Changes

```python
# After adding/modifying translations:
# WRONG — translations not visible until cache cleared

# CORRECT — ALWAYS clear cache
# bench --site {site} clear-cache
# Or programmatically:
frappe.clear_cache()
```
