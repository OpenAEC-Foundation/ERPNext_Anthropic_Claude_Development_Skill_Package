# Jinja Templates - Complete Decision Trees

> Detailed flowcharts for selecting the right template type and implementation approach.

---

## Decision Tree: Template Type Selection

```
WHAT IS YOUR OUTPUT GOAL?
│
├─► Printable PDF document?
│   │
│   │ WHAT ARE YOU PRINTING?
│   │
│   ├─► Standard DocType document?
│   │   │ (Invoice, Quote, PO, etc.)
│   │   │
│   │   │ HOW COMPLEX IS THE LAYOUT?
│   │   │
│   │   ├─► Simple: fields in rows/columns
│   │   │   └── Print Format Builder (Setup > Print)
│   │   │       - No coding needed
│   │   │       - Drag-drop interface
│   │   │       - Limited customization
│   │   │
│   │   ├─► Medium: custom headers, conditional sections
│   │   │   └── Custom HTML Print Format (Jinja)
│   │   │       - Create via Setup > Print Format
│   │   │       - Full Jinja control
│   │   │       - Embedded CSS
│   │   │
│   │   └─► Complex: multi-page, signatures, images
│   │       └── Custom HTML Print Format (Jinja)
│   │           - May need @page CSS
│   │           - Consider V16 Chrome PDF benefits
│   │           - Test page breaks carefully
│   │
│   ├─► Query Report results?
│   │   └── Report Print Format (JAVASCRIPT!)
│   │       ⚠️ NOT Jinja!
│   │       ⚠️ Uses {%= %} and {% %}
│   │       - Create in Report DocType
│   │       - Access: data[], filters, report_summary
│   │
│   ├─► Script Report results?
│   │   └── Report Print Format (JAVASCRIPT!)
│   │       ⚠️ Same as Query Report
│   │       - Has access to columns[], data[]
│   │
│   └─► Standalone letter/certificate?
│       └── Letter Head + Print Format
│           - Letter Head: company logo, address
│           - Print Format: document content
│
├─► Email content?
│   │
│   │ IS IT LINKED TO A DOCTYPE?
│   │
│   ├─► Yes (e.g., invoice reminder)
│   │   └── Email Template with DocType
│   │       - Setup > Email > Email Template
│   │       - Link to specific DocType
│   │       - Access: doc object
│   │
│   ├─► No (standalone email)
│   │   └── Email Template without DocType
│   │       - Pass custom context when sending
│   │
│   └─► System notification?
│       └── Notification (Setup > Notification)
│           - Built-in Jinja in message field
│           - Auto-triggered on events
│
├─► Customer-facing web page?
│   │
│   │ AUTHENTICATION REQUIRED?
│   │
│   ├─► Public (anyone can view)
│   │   └── Portal Page (www/*.html)
│   │       - Check user != 'Guest' for sections
│   │       - No login required
│   │
│   ├─► Logged-in users only
│   │   └── Portal Page with permission check
│   │       - Add to context.py: if guest redirect
│   │       - Use frappe.session for user data
│   │
│   └─► Customer portal (view their orders, etc.)
│       └── Portal Page with DocType context
│           - Filter data by current user/customer
│           - Use permission_query patterns
│
└─► Reusable template logic?
    │
    │ WHAT KIND OF REUSE?
    │
    ├─► Formatting function (e.g., phone formatter)
    │   └── Custom Jinja filter (hooks.py jenv.filters)
    │       - Usage: {{ value | my_filter }}
    │
    ├─► Data retrieval (e.g., get company logo)
    │   └── Custom Jinja method (hooks.py jenv.methods)
    │       - Usage: {{ my_method(arg) }}
    │
    └─► Template snippet (e.g., address block)
        └── Template include
            - Save in templates/includes/
            - Usage: {% include "path/to/snippet.html" %}
```

---

## Decision Tree: Print Format Creation Method

```
WHERE SHOULD THE PRINT FORMAT LIVE?
│
├─► Database (editable via UI)?
│   │
│   │ WHO WILL MAINTAIN IT?
│   │
│   ├─► End users/administrators
│   │   └── Create via UI (Setup > Print Format)
│   │       - Easy to modify
│   │       - Site-specific
│   │       - No deployment needed
│   │
│   └─► Developers (but stored in DB)
│       └── Create via UI, export as fixture
│           ```python
│           # hooks.py
│           fixtures = [
│               {"dt": "Print Format", "filters": [
│                   ["name", "=", "My Invoice Format"]
│               ]}
│           ]
│           ```
│
└─► Code (version controlled)?
    │
    │ HOW TO STRUCTURE?
    │
    └─► Create Print Format record + HTML file
        ```
        myapp/
        ├── print_format/
        │   └── my_invoice_format/
        │       ├── my_invoice_format.json  # DocType record
        │       └── my_invoice_format.html  # Template content
        ```
```

---

## Decision Tree: Portal Page Context

```
WHAT DATA DOES YOUR PAGE NEED?
│
├─► Static page (no dynamic data)?
│   └── HTML only, no .py file needed
│       ```
│       www/about.html  # Just Jinja template
│       ```
│
├─► Dynamic data from database?
│   │
│   │ WHAT PERMISSION MODEL?
│   │
│   ├─► Public data (no login required)
│   │   └── get_context with public filters
│   │       ```python
│   │       def get_context(context):
│   │           context.items = frappe.get_all(
│   │               "Item",
│   │               filters={"is_public": 1}
│   │           )
│   │       ```
│   │
│   ├─► User-specific data
│   │   └── get_context with user filters
│   │       ```python
│   │       def get_context(context):
│   │           if frappe.session.user == "Guest":
│   │               frappe.throw("Login required")
│   │           context.orders = frappe.get_all(
│   │               "Sales Order",
│   │               filters={"owner": frappe.session.user}
│   │           )
│   │       ```
│   │
│   └─► Customer portal data
│       └── get_context with customer link
│           ```python
│           def get_context(context):
│               customer = get_customer_for_user()
│               context.invoices = frappe.get_all(
│                   "Sales Invoice",
│                   filters={"customer": customer}
│               )
│           ```
│
├─► Form submission handling?
│   │
│   │ WHAT TYPE OF FORM?
│   │
│   ├─► Simple contact form
│   │   └── Use frappe.form_dict + frappe.sendmail
│   │
│   ├─► Create document
│   │   └── Use web form (Setup > Web Form)
│   │       - Built-in CSRF protection
│   │       - Automatic validation
│   │
│   └─► Custom action
│       └── Whitelisted API + client JS
│           - @frappe.whitelist(allow_guest=True)
│           - AJAX call from portal
│
└─► URL parameters?
    └── Access via frappe.form_dict
        ```python
        # URL: /page?id=123&type=invoice
        def get_context(context):
            doc_id = frappe.form_dict.get("id")
            doc_type = frappe.form_dict.get("type")
        ```
```

---

## Decision Tree: Jinja Custom Extensions

```
WHAT DO YOU WANT TO ADD TO JINJA?
│
├─► New function available in templates?
│   │
│   │ DOES IT TRANSFORM A VALUE?
│   │
│   ├─► Yes (input → output transformation)
│   │   └── Custom filter
│   │       ```python
│   │       # hooks.py
│   │       jenv = {"filters": ["myapp.jinja.filters"]}
│   │       
│   │       # myapp/jinja/filters.py
│   │       def uppercase(value):
│   │           return str(value).upper()
│   │       
│   │       # Template usage
│   │       {{ name | uppercase }}
│   │       ```
│   │
│   └─► No (retrieves data or performs action)
│       └── Custom method
│           ```python
│           # hooks.py
│           jenv = {"methods": ["myapp.jinja.methods"]}
│           
│           # myapp/jinja/methods.py
│           def get_weather(city):
│               return fetch_weather_api(city)
│           
│           # Template usage
│           {{ get_weather("London") }}
│           ```
│
├─► Reusable HTML snippet?
│   │
│   │ IS IT PARAMETERIZED?
│   │
│   ├─► Yes (accepts variables)
│   │   └── Macro
│   │       ```jinja
│   │       {% macro address_block(address) %}
│   │       <div class="address">
│   │           {{ address.address_line1 }}<br>
│   │           {{ address.city }}, {{ address.pincode }}
│   │       </div>
│   │       {% endmacro %}
│   │       
│   │       {{ address_block(customer_address) }}
│   │       ```
│   │
│   └─► No (static content)
│       └── Include
│           ```jinja
│           {% include "templates/includes/footer.html" %}
│           ```
│
└─► Global variable?
    └── Use extend_bootinfo hook
        ```python
        # hooks.py
        extend_bootinfo = "myapp.boot.extend"
        
        # myapp/boot.py
        def extend(bootinfo):
            bootinfo.company_settings = get_settings()
        
        # Accessible in JS and via frappe.boot
        ```
```

---

## Decision Tree: Styling Approach

```
HOW SHOULD YOU STYLE YOUR TEMPLATE?
│
├─► Print Format?
│   │
│   │ WHAT'S YOUR TARGET?
│   │
│   ├─► PDF output (primary use)
│   │   └── Embedded <style> block
│   │       ```jinja
│   │       <style>
│   │           /* Use print-friendly CSS */
│   │           @page { margin: 1cm; }
│   │           .page-break { page-break-before: always; }
│   │           
│   │           /* Avoid: flexbox (wkhtmltopdf), vh/vw units */
│   │           /* V16 Chrome PDF: flexbox OK */
│   │       </style>
│   │       ```
│   │
│   └─► Screen + PDF
│       └── Embedded styles with @media print
│           ```css
│           @media screen { .screen-only { display: block; } }
│           @media print { .screen-only { display: none; } }
│           ```
│
├─► Email Template?
│   └── Inline styles ONLY
│       ```jinja
│       {# Email clients ignore <style> blocks #}
│       <table style="width: 100%; border-collapse: collapse;">
│           <tr style="background: #f5f5f5;">
│               <td style="padding: 10px;">Content</td>
│           </tr>
│       </table>
│       ```
│
└─► Portal Page?
    │
    │ APP-SPECIFIC OR FRAPPE THEME?
    │
    ├─► Match Frappe/ERPNext theme
    │   └── Use Bootstrap classes
    │       ```jinja
    │       <div class="container">
    │           <div class="row">
    │               <div class="col-md-6">
    │                   <button class="btn btn-primary">
    │       ```
    │
    └─► Custom styling
        └── Add CSS via web_include_css hook
            ```python
            # hooks.py
            web_include_css = ["/assets/myapp/css/portal.css"]
            ```
```

---

## Decision Tree: Template Debugging

```
TEMPLATE NOT WORKING? WHAT'S THE SYMPTOM?
│
├─► Blank output?
│   │
│   ├─► Check: Is doc available?
│   │   ```jinja
│   │   <!-- Debug: {{ doc }} -->
│   │   <!-- Debug: {{ doc.name if doc else 'NO DOC' }} -->
│   │   ```
│   │
│   ├─► Check: Syntax error hiding exception?
│   │   - Look in Error Log
│   │   - Check browser console for API errors
│   │
│   └─► Check: Wrong template type?
│       - Report Print Format ≠ Jinja
│       - Uses {%= %} not {{ }}
│
├─► "Undefined" error?
│   │
│   ├─► Variable doesn't exist
│   │   ```jinja
│   │   {# Add default #}
│   │   {{ doc.custom_field | default('') }}
│   │   ```
│   │
│   ├─► Method not available
│   │   - Not all frappe.* methods work in Jinja
│   │   - Check available methods in syntax skill
│   │
│   └─► Context not passed
│       - Portal: Check get_context returns context
│       - Email: Check context dict in sendmail call
│
├─► Wrong formatting?
│   │
│   ├─► Currency showing raw number
│   │   ```jinja
│   │   {# ❌ Wrong #}
│   │   {{ doc.grand_total }}
│   │   
│   │   {# ✅ Correct #}
│   │   {{ doc.get_formatted("grand_total") }}
│   │   ```
│   │
│   └─► Date in wrong format
│       ```jinja
│       {# Use format_date for display #}
│       {{ frappe.format_date(doc.posting_date) }}
│       ```
│
├─► HTML showing as text?
│   └── Missing safe filter (use carefully!)
│       ```jinja
│       {# Only for trusted HTML content #}
│       {{ doc.terms | safe }}
│       ```
│
└─► Translations not working?
    │
    ├─► Missing _() wrapper
    │   ```jinja
    │   {{ _("Invoice") }}  {# Not just "Invoice" #}
    │   ```
    │
    └─► Translation not in system
        - Add via Setup > Translations
        - Or translations/*.csv in app
```

---

## Quick Reference: Template Type Summary

| Need | Template Type | Location | Key Objects |
|------|---------------|----------|-------------|
| DocType PDF | Print Format (Jinja) | Setup > Print | `doc`, `frappe` |
| Report PDF | Report Print Format (JS!) | Report record | `data[]`, `filters` |
| Email | Email Template | Setup > Email | `doc`, `frappe` |
| Notification | Notification | Setup > Notification | `doc`, event data |
| Portal | www/*.html + *.py | myapp/www/ | custom context |
| Snippet | Template include | templates/includes/ | passed variables |
