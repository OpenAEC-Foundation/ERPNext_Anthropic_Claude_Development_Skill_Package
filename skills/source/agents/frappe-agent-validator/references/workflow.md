# Code Validator Workflow - Detailed Steps

## Step 1: Identify Code Type

### Detection Rules

| If Code Contains... | Code Type |
|---------------------|-----------|
| `frappe.ui.form.on(` | Client Script |
| `# Server Script` or sandbox patterns | Server Script |
| `class X(Document):` | Controller |
| `doc_events = {`, `scheduler_events = {` | hooks.py |
| `{% ... %}`, `{{ ... }}` | Jinja Template |
| `@frappe.whitelist()` | Whitelisted Method |

### Context Clues

| Context | Code Type |
|---------|-----------|
| "My Server Script..." | Server Script |
| "In the Client Script..." | Client Script |
| "The controller for Sales Invoice..." | Controller |
| "My hooks.py has..." | hooks.py |

### When Ambiguous

Ask: "Is this code running in:"
- Browser (JavaScript) → Client Script
- Frappe UI Server Script editor → Server Script
- Python file in custom app → Controller or Whitelisted

## Step 2: Type-Specific Validation

### Server Script Validation

```
STEP 2A: SERVER SCRIPT CHECKS
═════════════════════════════

1. IMPORT SCAN [FATAL]
   └── Regex: ^import |^from .* import
   └── If found: FATAL - imports blocked in sandbox

2. VARIABLE REFERENCE CHECK [FATAL]
   └── Check for: self.*, document.*, this.
   └── If found: FATAL - should use doc.*

3. TRY/EXCEPT SCAN [WARNING]
   └── Regex: try:|except
   └── If found: WARNING - usually wrong in Server Scripts

4. EVENT NAME VERIFICATION
   └── If UI event "Before Save" → should be validate hook
   └── If UI event "After Save" → should be on_update hook
   └── Mismatch: ERROR

5. AVAILABLE NAMESPACE CHECK
   └── Verify only uses:
       - frappe.*
       - doc (for document)
       - None, True, False, int, float, str, list, dict
   └── Unknown reference: ERROR

6. FRAPPE API CHECK
   └── Common patterns that should work:
       - frappe.throw()
       - frappe.msgprint()
       - frappe.db.get_value()
       - frappe.db.set_value()
       - frappe.utils.*
       - frappe.get_doc()
       - frappe.new_doc()
```

### Client Script Validation

```
STEP 2B: CLIENT SCRIPT CHECKS
═════════════════════════════

1. SERVER API MISUSE [FATAL]
   └── Check for: frappe.db.*, frappe.get_doc( (without frappe.call)
   └── If found: FATAL - server-side only APIs

2. ASYNC HANDLING [FATAL]
   └── Check for: frappe.call() without callback/async
   └── Pattern: let x = frappe.call({...}) without callback
   └── If found: FATAL - will return undefined

3. FORM STRUCTURE CHECK
   └── Must be inside: frappe.ui.form.on('DocType', {...})
   └── Events should be: refresh, onload, validate, etc.

4. FIELD OPERATIONS CHECK
   └── After frm.set_value(): should have frm.refresh_field()
   └── Missing refresh: WARNING

5. FORM STATE CHECKS
   └── Operations on new doc: check frm.doc.__islocal
   └── Operations on submitted: check frm.doc.docstatus
   └── Missing checks: WARNING

6. COMMON PATTERNS VERIFICATION
   └── frm.trigger() - should be frm.trigger('fieldname')
   └── cur_frm usage - should use frm parameter instead
```

### Controller Validation

```
STEP 2C: CONTROLLER CHECKS
══════════════════════════

1. CLASS STRUCTURE [ERROR]
   └── Must extend Document or specific DocType class
   └── Pattern: class X(Document): or class X(SalesInvoice):

2. SUPER CALL CHECK [WARNING]
   └── Override methods should call super()
   └── Pattern: super().validate(), super().on_update()
   └── Missing: WARNING - may break parent logic

3. LIFECYCLE MODIFICATION CHECK [FATAL]
   └── In on_update: modifications to self.* won't save
   └── Pattern: self.field = X in on_update
   └── Should use: frappe.db.set_value()

4. CIRCULAR SAVE CHECK [FATAL]
   └── Pattern: self.save() in lifecycle hooks
   └── Pattern: doc.save() where doc is same document
   └── If found: FATAL - infinite loop

5. IMPORT VERIFICATION
   └── Imports ARE allowed (unlike Server Scripts)
   └── Check imports are valid Python modules
   └── Check frappe imports are correct paths

6. TRANSACTION BEHAVIOR UNDERSTANDING
   └── validate, before_*: rollback on error
   └── on_update, on_*: NO automatic rollback
   └── Document behavior based on hook type
```

### hooks.py Validation

```
STEP 2D: HOOKS.PY CHECKS
════════════════════════

1. STRUCTURE CHECK
   └── Valid Python dict syntax
   └── No syntax errors

2. HOOK NAME VERIFICATION
   └── doc_events: valid event names
   └── scheduler_events: valid frequency keys
   └── Valid names: validate, on_update, on_submit, etc.

3. PATH VERIFICATION
   └── Dotted paths should be valid Python paths
   └── Pattern: "app.module.function"
   └── Path should exist in codebase

4. VERSION-SPECIFIC HOOKS
   └── extend_doctype_class: v16+ only
   └── If found in v14/v15 code: ERROR
```

## Step 3: Universal Checks

### Security Validation

```
SECURITY CHECKS
═══════════════

1. SQL INJECTION [CRITICAL]
   └── Pattern: f"...{user_input}..." in SQL
   └── Pattern: "..." + user_input in SQL
   └── Should use: frappe.db.escape() or parameterized queries

2. PERMISSION BYPASS [CRITICAL]
   └── Pattern: ignore_permissions=True without justification
   └── Pattern: frappe.db.sql without permission check
   └── Should have: explicit permission checks

3. XSS VULNERABILITY [HIGH]
   └── Pattern: user input directly in frappe.msgprint(html)
   └── Should use: frappe.utils.escape_html()

4. SENSITIVE DATA [HIGH]
   └── Pattern: password, token, secret in log/print
   └── Should be: masked or omitted
```

### Error Handling Validation

```
ERROR HANDLING CHECKS
═════════════════════

1. SILENT FAILURE [HIGH]
   └── Pattern: except: pass
   └── Pattern: except Exception: pass without logging
   └── Should have: logging or re-raise

2. USER FEEDBACK [MEDIUM]
   └── Error occurs but no frappe.throw/msgprint
   └── Should have: user notification

3. ERROR SPECIFICITY [LOW]
   └── Pattern: except Exception:
   └── Should be: specific exception types
```

### Performance Validation

```
PERFORMANCE CHECKS
══════════════════

1. QUERY IN LOOP [HIGH]
   └── Pattern: for item in items: frappe.db.get_value()
   └── Should be: single query before loop

2. UNBOUNDED QUERY [MEDIUM]
   └── Pattern: frappe.get_all() without limit
   └── Should have: limit_page_length or filters

3. UNNECESSARY GET_DOC [LOW]
   └── Pattern: frappe.get_doc() when only one field needed
   └── Should be: frappe.db.get_value()
```

## Step 4: Version Compatibility Check

```
VERSION COMPATIBILITY
═════════════════════

1. V16-ONLY FEATURES
   └── extend_doctype_class: v16+
   └── naming_rule = "UUID": v16+
   └── pdf_renderer = "chrome": v16+
   └── data_masking: v16+

2. DEPRECATED PATTERNS
   └── frappe.bean(): deprecated, use frappe.get_doc()
   └── job_name: use job_id (v15+)

3. BEHAVIORAL DIFFERENCES
   └── Scheduler tick: 240s (v14) vs 60s (v15+)
   └── Document changes in checks
```

## Step 5: Generate Report

### Report Structure

```markdown
## Code Validation Report

### Summary
- Code Type: [type]
- Total Issues: X critical, Y warnings, Z suggestions
- Overall: [FAIL / PASS WITH WARNINGS / PASS]

### Critical Errors (🔴 Must Fix)
[Table of critical issues]

### Warnings (🟡 Should Fix)
[Table of warnings]

### Suggestions (🔵 Nice to Have)
[Table of suggestions]

### Corrected Code
[If critical errors exist, provide corrected version]

### Version Compatibility
[Compatibility matrix]
```

### Severity Classification

| Severity | Criteria | Action Required |
|----------|----------|-----------------|
| CRITICAL | Code will fail/crash | Must fix before deployment |
| HIGH | Significant bug/security issue | Should fix before deployment |
| MEDIUM | Potential issues | Fix when possible |
| LOW | Style/optimization | Optional improvement |
| SUGGESTION | Best practice | Consider for future |

### Corrected Code Guidelines

When providing corrected code:
1. Fix ALL critical errors
2. Fix HIGH severity issues
3. Add comments explaining changes
4. Preserve original structure where possible
5. Do not change working code unnecessarily
