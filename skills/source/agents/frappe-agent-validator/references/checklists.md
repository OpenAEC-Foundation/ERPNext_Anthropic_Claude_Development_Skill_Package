# Code Validation Checklists

## Server Script Checklist

### Fatal Errors (🔴 Code Will Not Work)

- [ ] **No import statements**
  - ❌ `import json`
  - ❌ `from frappe.utils import nowdate`
  - ❌ `from datetime import datetime`
  - ✅ Use `frappe.parse_json()`, `frappe.utils.nowdate()`, etc.

- [ ] **Correct document variable**
  - ❌ `self.field_name`
  - ❌ `document.field_name`
  - ❌ `this.field_name`
  - ✅ `doc.field_name`

- [ ] **No undefined variables**
  - Only available: `doc`, `frappe`, `None`, `True`, `False`
  - Built-in types: `int`, `float`, `str`, `list`, `dict`, `set`, `tuple`

- [ ] **Correct event for purpose**
  - Validation logic → must be in `validate` event
  - Post-save logic → must be in `on_update` event
  - Pre-submit logic → must be in `before_submit` event

### Errors (🟠 Code May Fail)

- [ ] **API type has method and path**
  ```python
  # API Script must define
  frappe.response["message"] = result
  ```

- [ ] **Permission Query returns condition string**
  ```python
  # Permission Query must return string or None
  conditions = f"`tabCustomer`.`account_manager` = {frappe.db.escape(frappe.session.user)}"
  ```

- [ ] **Scheduler has proper cron syntax**
  ```python
  # Cron: minute hour day month weekday
  # Every day at 2 AM: "0 2 * * *"
  ```

### Warnings (🟡 Should Fix)

- [ ] **No try/except blocks**
  - Server Scripts don't need try/except for validation
  - Just use `frappe.throw()` to stop operation

- [ ] **Null checks before operations**
  ```python
  # ❌ Risky
  doc.customer.lower()
  
  # ✅ Safe
  if doc.customer:
      doc.customer.lower()
  ```

- [ ] **Using frappe.throw() not frappe.msgprint() for blocking**
  - `frappe.throw()` → blocks and rolls back
  - `frappe.msgprint()` → shows message, continues

---

## Client Script Checklist

### Fatal Errors (🔴 Code Will Not Work)

- [ ] **No server-side APIs**
  - ❌ `frappe.db.get_value()`
  - ❌ `frappe.db.set_value()`
  - ❌ `frappe.get_doc()`
  - ❌ `frappe.db.sql()`
  - ✅ Use `frappe.call()` to call server methods

- [ ] **Async handling for frappe.call()**
  ```javascript
  // ❌ WRONG - result is undefined
  let result = frappe.call({method: 'mymethod'});
  
  // ✅ CORRECT - use callback
  frappe.call({
      method: 'mymethod',
      callback: function(r) {
          // use r.message here
      }
  });
  
  // ✅ CORRECT - use async/await
  let r = await frappe.call({method: 'mymethod', async: false});
  ```

- [ ] **Correct form event structure**
  ```javascript
  // Must wrap in frappe.ui.form.on
  frappe.ui.form.on('DocType', {
      refresh(frm) {
          // code here
      }
  });
  ```

### Errors (🟠 Code May Fail)

- [ ] **refresh_field after set_value**
  ```javascript
  // ❌ Field may not update visually
  frm.set_value('field', value);
  
  // ✅ Force UI refresh
  frm.set_value('field', value);
  frm.refresh_field('field');
  ```

- [ ] **Use frm parameter, not cur_frm**
  ```javascript
  // ❌ Deprecated, may fail in some contexts
  cur_frm.doc.field
  
  // ✅ Use parameter
  refresh(frm) {
      frm.doc.field
  }
  ```

### Warnings (🟡 Should Fix)

- [ ] **Check form state for conditional logic**
  ```javascript
  // Check if new document
  if (frm.doc.__islocal) { }
  
  // Check if submitted
  if (frm.doc.docstatus === 1) { }
  
  // Check if cancelled
  if (frm.doc.docstatus === 2) { }
  ```

- [ ] **Await or callback for async operations**
  - Don't mix sync and async code
  - Always handle async completion

---

## Controller Checklist

### Fatal Errors (🔴 Code Will Not Work)

- [ ] **No self modification in on_update**
  ```python
  # ❌ Changes NOT saved
  def on_update(self):
      self.status = "Updated"
  
  # ✅ Use db_set or set_value
  def on_update(self):
      frappe.db.set_value(self.doctype, self.name, "status", "Updated")
      # or
      self.db_set("status", "Updated")
  ```

- [ ] **No circular save**
  ```python
  # ❌ Infinite loop
  def validate(self):
      self.save()
  
  # ❌ Also infinite loop
  def on_update(self):
      doc = frappe.get_doc(self.doctype, self.name)
      doc.save()
  ```

- [ ] **Correct class inheritance**
  ```python
  # ✅ Correct
  from frappe.model.document import Document
  class MyDocType(Document):
      pass
  
  # ✅ Also correct for overrides
  from erpnext.selling.doctype.sales_order.sales_order import SalesOrder
  class CustomSalesOrder(SalesOrder):
      pass
  ```

### Errors (🟠 Code May Fail)

- [ ] **Call super() in overrides**
  ```python
  # ❌ May break parent validation
  def validate(self):
      self.custom_validation()
  
  # ✅ Preserve parent logic
  def validate(self):
      super().validate()
      self.custom_validation()
  ```

- [ ] **Understand transaction behavior**
  ```python
  # These rollback on exception:
  # - validate, before_validate
  # - before_save, before_insert
  # - before_submit, before_cancel
  
  # These do NOT rollback on exception:
  # - on_update, after_insert
  # - on_submit, on_cancel
  ```

### Warnings (🟡 Should Fix)

- [ ] **Error handling for external calls**
  ```python
  # ✅ Handle external API failures
  try:
      response = requests.post(url, data=data)
      response.raise_for_status()
  except requests.RequestException as e:
      frappe.log_error(f"API call failed: {e}")
      frappe.throw(_("Could not connect to external service"))
  ```

---

## hooks.py Checklist

### Fatal Errors (🔴 Code Will Not Work)

- [ ] **Valid Python syntax**
  - No trailing commas that break syntax
  - Proper string quoting
  - Valid dict structure

- [ ] **Correct hook names**
  ```python
  # ✅ Valid doc_events
  doc_events = {
      "Sales Invoice": {
          "validate": "app.module.function",
          "on_update": "app.module.function",
          "on_submit": "app.module.function",
      }
  }
  
  # ✅ Valid scheduler_events
  scheduler_events = {
      "daily": ["app.module.function"],
      "hourly": ["app.module.function"],
      "cron": {
          "0 2 * * *": ["app.module.function"]
      }
  }
  ```

- [ ] **Valid function paths**
  - Path must be: "app_name.module.submodule.function"
  - Function must exist and be importable

### Errors (🟠 Code May Fail)

- [ ] **Version-specific hooks**
  ```python
  # ❌ v16 only - will fail on v14/v15
  extend_doctype_class = {
      "Sales Invoice": ["app.extensions.SalesInvoiceMixin"]
  }
  ```

### Warnings (🟡 Should Fix)

- [ ] **Permission hooks should not throw**
  ```python
  # has_permission and permission_query_conditions
  # should return values, not throw errors
  ```

---

## Jinja Template Checklist

### Fatal Errors (🔴 Code Will Not Work)

- [ ] **Correct tag syntax**
  ```jinja
  {# Comment #}
  {{ variable }}
  {% control structure %}
  ```

- [ ] **Closed control blocks**
  ```jinja
  {% for item in items %}
      {{ item.name }}
  {% endfor %}  {# Don't forget endfor #}
  
  {% if condition %}
      Content
  {% endif %}  {# Don't forget endif #}
  ```

### Errors (🟠 Code May Fail)

- [ ] **Safe variable access**
  ```jinja
  {# ❌ May fail if None #}
  {{ doc.customer.name }}
  
  {# ✅ Safe with default #}
  {{ doc.customer.name or '' }}
  {{ doc.customer.name | default('') }}
  ```

- [ ] **Use frappe.format for currency/dates**
  ```jinja
  {# ❌ Raw value #}
  {{ doc.grand_total }}
  
  {# ✅ Properly formatted #}
  {{ frappe.format(doc.grand_total, {'fieldtype': 'Currency'}) }}
  ```

---

## Whitelisted Method Checklist

### Fatal Errors (🔴 Code Will Not Work)

- [ ] **Has @frappe.whitelist() decorator**
  ```python
  @frappe.whitelist()
  def my_method(param1, param2):
      pass
  ```

- [ ] **Returns JSON-serializable data**
  ```python
  # ❌ Can't serialize
  return frappe.get_doc("DocType", name)  # Returns object
  
  # ✅ Serializable
  return frappe.get_doc("DocType", name).as_dict()
  ```

### Errors (🟠 Code May Fail)

- [ ] **Permission checking**
  ```python
  @frappe.whitelist()
  def sensitive_operation(docname):
      # ✅ Check permissions
      if not frappe.has_permission("DocType", "write", docname):
          frappe.throw(_("Not permitted"), frappe.PermissionError)
  ```

- [ ] **Guest access explicit**
  ```python
  # Public endpoint (no login required)
  @frappe.whitelist(allow_guest=True)
  def public_method():
      pass
  
  # Default: requires login
  @frappe.whitelist()
  def authenticated_method():
      pass
  ```

### Warnings (🟡 Should Fix)

- [ ] **Parameter validation**
  ```python
  @frappe.whitelist()
  def update_status(docname, status):
      # ✅ Validate parameters
      if not docname:
          frappe.throw(_("Document name required"))
      if status not in ["Active", "Inactive"]:
          frappe.throw(_("Invalid status"))
  ```

---

## Universal Security Checklist

### Critical (🔴 Security Risk)

- [ ] **No SQL injection**
  ```python
  # ❌ Vulnerable
  frappe.db.sql(f"SELECT * FROM tabUser WHERE name = '{user_input}'")
  
  # ✅ Safe - parameterized
  frappe.db.sql("SELECT * FROM tabUser WHERE name = %s", [user_input])
  
  # ✅ Safe - escaped
  frappe.db.sql(f"SELECT * FROM tabUser WHERE name = {frappe.db.escape(user_input)}")
  ```

- [ ] **Permission checks present**
  ```python
  # ✅ Check before operations
  frappe.has_permission("DocType", "read", docname)
  frappe.has_permission("DocType", "write", docname)
  ```

- [ ] **No hardcoded credentials**
  ```python
  # ❌ Never do this
  api_key = "sk-1234567890"
  
  # ✅ Use site config or environment
  api_key = frappe.conf.get("external_api_key")
  ```

### High (🟠 Security Concern)

- [ ] **XSS prevention in HTML output**
  ```python
  # ❌ Vulnerable
  frappe.msgprint(f"<b>{user_input}</b>")
  
  # ✅ Escaped
  frappe.msgprint(f"<b>{frappe.utils.escape_html(user_input)}</b>")
  ```

- [ ] **Sensitive data not logged**
  ```python
  # ❌ Bad
  frappe.log_error(f"Login attempt with password: {password}")
  
  # ✅ Masked
  frappe.log_error(f"Login attempt for user: {username}")
  ```
