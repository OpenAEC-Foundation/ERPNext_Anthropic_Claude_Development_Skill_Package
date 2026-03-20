# Complete hooks.py Voorbeelden

Praktische voorbeelden van complete hooks.py configuraties.

---

## Minimale hooks.py

```python
# Minimale hooks.py voor een nieuwe app
app_name = "myapp"
app_title = "My App"
app_publisher = "My Company"
app_description = "My custom ERPNext app"
app_email = "info@mycompany.com"
app_license = "MIT"
```

---

## Standaard Business App

Complete hooks.py voor een typische business app:

```python
app_name = "myapp"
app_title = "My App"
app_publisher = "My Company"
app_description = "Custom ERPNext extensions"
app_email = "info@mycompany.com"
app_license = "MIT"

required_apps = ["erpnext"]

# ============================================================
# Document Events - React op CRUD operaties
# ============================================================
doc_events = {
    # Wildcard - alle DocTypes
    "*": {
        "after_insert": "myapp.audit.log_creation"
    },
    # Sales Invoice specifiek
    "Sales Invoice": {
        "validate": "myapp.events.sales_invoice.validate",
        "on_submit": "myapp.events.sales_invoice.on_submit",
        "on_cancel": "myapp.events.sales_invoice.on_cancel"
    },
    # Sales Order
    "Sales Order": {
        "validate": [
            "myapp.events.sales_order.check_credit_limit",
            "myapp.events.sales_order.validate_items"
        ]
    }
}

# ============================================================
# Scheduled Tasks
# ============================================================
scheduler_events = {
    "daily": [
        "myapp.tasks.send_daily_digest",
        "myapp.tasks.cleanup_old_logs"
    ],
    "daily_long": [
        "myapp.tasks.sync_external_system"
    ],
    "cron": {
        "0 9 * * 1-5": ["myapp.tasks.weekday_morning_report"],
        "0 17 * * 5": ["myapp.tasks.weekly_summary"]
    }
}

# ============================================================
# Client-Side Data
# ============================================================
extend_bootinfo = "myapp.boot.extend_boot"

# ============================================================
# Custom Permissions
# ============================================================
permission_query_conditions = {
    "Sales Invoice": "myapp.permissions.si_query_conditions"
}
has_permission = {
    "Sales Invoice": "myapp.permissions.si_has_permission"
}

# ============================================================
# Fixtures - Configuratie Export
# ============================================================
fixtures = [
    {"dt": "Custom Field", "filters": [["module", "=", "My App"]]},
    {"dt": "Property Setter", "filters": [["module", "=", "My App"]]},
    {"dt": "Client Script", "filters": [["module", "=", "My App"]]},
    {"dt": "Role", "filters": [["name", "like", "MyApp%"]]}
]

# ============================================================
# Assets
# ============================================================
app_include_js = "/assets/myapp/js/myapp.min.js"
app_include_css = "/assets/myapp/css/myapp.min.css"

# ============================================================
# Form Script Extensions
# ============================================================
doctype_js = {
    "Sales Invoice": "public/js/sales_invoice.js",
    "Customer": "public/js/customer.js"
}
```

---

## Event Handler Bestanden

### myapp/events/sales_invoice.py

```python
import frappe
from frappe import _

def validate(doc, method=None):
    """Validatie voor Sales Invoice"""
    validate_minimum_margin(doc)
    calculate_commission(doc)

def validate_minimum_margin(doc):
    """Check minimum marge"""
    if doc.grand_total > 0:
        margin = (doc.grand_total - doc.total_cost) / doc.grand_total * 100
        if margin < 10:
            frappe.throw(_("Minimum margin of 10% required"))

def calculate_commission(doc):
    """Bereken sales commission"""
    if doc.sales_person:
        commission_rate = frappe.db.get_value(
            "Sales Person", doc.sales_person, "commission_rate"
        ) or 0
        doc.commission_amount = doc.grand_total * commission_rate / 100

def on_submit(doc, method=None):
    """Na submit van Sales Invoice"""
    create_commission_entry(doc)
    notify_accounts_team(doc)

def create_commission_entry(doc):
    """Maak commission journal entry"""
    if doc.commission_amount > 0:
        frappe.get_doc({
            "doctype": "Commission Entry",
            "sales_invoice": doc.name,
            "sales_person": doc.sales_person,
            "amount": doc.commission_amount
        }).insert(ignore_permissions=True)

def notify_accounts_team(doc):
    """Notificeer accounts bij grote facturen"""
    if doc.grand_total > 50000:
        frappe.sendmail(
            recipients=["accounts@mycompany.com"],
            subject=f"Large Invoice Submitted: {doc.name}",
            message=f"Invoice {doc.name} for {doc.grand_total} has been submitted."
        )

def on_cancel(doc, method=None):
    """Bij cancel: cleanup gerelateerde docs"""
    # Cancel commission entries
    commission_entries = frappe.get_all(
        "Commission Entry",
        filters={"sales_invoice": doc.name}
    )
    for entry in commission_entries:
        frappe.delete_doc("Commission Entry", entry.name)
```

### myapp/tasks.py

```python
import frappe
from frappe.utils import today, add_days, getdate

def send_daily_digest():
    """Stuur dagelijkse samenvatting naar sales team"""
    users = frappe.get_all(
        "User",
        filters={"enabled": 1, "user_type": "System User"},
        fields=["name", "email"]
    )
    
    for user in users:
        if "Sales User" in frappe.get_roles(user.name):
            digest = compile_sales_digest(user.name)
            if digest:
                frappe.sendmail(
                    recipients=[user.email],
                    subject=f"Daily Sales Digest - {today()}",
                    message=digest
                )

def compile_sales_digest(user):
    """Compile digest voor specifieke user"""
    pending_orders = frappe.db.count(
        "Sales Order",
        {"owner": user, "status": "Draft"}
    )
    todays_invoices = frappe.db.count(
        "Sales Invoice",
        {"owner": user, "posting_date": today()}
    )
    
    if pending_orders or todays_invoices:
        return f"""
        <h3>Your Daily Summary</h3>
        <ul>
            <li>Pending Orders: {pending_orders}</li>
            <li>Today's Invoices: {todays_invoices}</li>
        </ul>
        """
    return None

def cleanup_old_logs():
    """Verwijder logs ouder dan 30 dagen"""
    cutoff_date = add_days(today(), -30)
    
    frappe.db.delete(
        "Activity Log",
        {"creation": ["<", cutoff_date]}
    )
    frappe.db.commit()

def sync_external_system():
    """Sync met extern systeem (long running)"""
    # Dit kan lang duren, dus daily_long gebruiken
    pending_records = frappe.get_all(
        "Sync Queue",
        filters={"status": "Pending"},
        limit=1000
    )
    
    for record in pending_records:
        try:
            process_sync(record.name)
            frappe.db.set_value("Sync Queue", record.name, "status", "Completed")
        except Exception:
            frappe.db.set_value("Sync Queue", record.name, "status", "Failed")
            frappe.log_error(
                title=f"Sync Failed: {record.name}",
                message=frappe.get_traceback()
            )
        
        # Commit per record om memory te sparen
        frappe.db.commit()

def weekday_morning_report():
    """Weekdag ochtend rapport om 9:00"""
    # Wordt alleen ma-vr om 9:00 uitgevoerd (cron: 0 9 * * 1-5)
    yesterday = add_days(today(), -1)
    
    report = generate_daily_report(yesterday)
    
    frappe.sendmail(
        recipients=["management@mycompany.com"],
        subject=f"Daily Business Report - {yesterday}",
        message=report
    )

def weekly_summary():
    """Wekelijkse samenvatting vrijdag 17:00"""
    week_start = add_days(today(), -7)
    
    summary = generate_weekly_summary(week_start, today())
    
    frappe.sendmail(
        recipients=["management@mycompany.com"],
        subject=f"Weekly Summary - Week ending {today()}",
        message=summary
    )
```

### myapp/boot.py

```python
import frappe

def extend_boot(bootinfo):
    """Voeg app-specifieke data toe aan frappe.boot"""
    
    # App versie
    bootinfo.myapp_version = frappe.get_module("myapp").__version__
    
    # User-specifieke settings
    if frappe.session.user != "Guest":
        bootinfo.myapp_settings = get_user_settings()
        bootinfo.feature_flags = get_feature_flags()
    
    # Company defaults
    default_company = frappe.defaults.get_user_default("Company")
    if default_company:
        bootinfo.company_config = frappe.db.get_value(
            "Company",
            default_company,
            ["default_currency", "country"],
            as_dict=True
        )

def get_user_settings():
    """Haal user-specifieke settings op"""
    user = frappe.session.user
    
    return {
        "dashboard_layout": frappe.db.get_value("User", user, "dashboard_layout") or "default",
        "notification_preferences": get_notification_prefs(user)
    }

def get_feature_flags():
    """Feature flags voor conditional UI"""
    settings = frappe.get_single("My App Settings")
    
    return {
        "new_dashboard": settings.enable_new_dashboard,
        "beta_features": settings.enable_beta,
        "advanced_reports": settings.enable_advanced_reports
    }

def get_notification_prefs(user):
    """Notification preferences"""
    return frappe.db.get_value(
        "Notification Settings",
        user,
        ["email_notifications", "push_notifications"],
        as_dict=True
    ) or {}
```

### myapp/permissions.py

```python
import frappe

def si_query_conditions(user):
    """Filter Sales Invoices in list view"""
    if not user:
        user = frappe.session.user
    
    if user == "Administrator":
        return ""
    
    roles = frappe.get_roles(user)
    
    if "Accounts Manager" in roles:
        return ""
    
    if "Accounts User" in roles:
        # Alleen eigen company
        company = frappe.defaults.get_user_default("Company")
        if company:
            return f"`tabSales Invoice`.company = {frappe.db.escape(company)}"
    
    if "Sales User" in roles:
        # Alleen eigen facturen
        return f"`tabSales Invoice`.owner = {frappe.db.escape(user)}"
    
    return "1=0"

def si_has_permission(doc, user=None, permission_type=None):
    """Document-level permission voor Sales Invoice"""
    if not user:
        user = frappe.session.user
    
    # Closed invoices kunnen niet bewerkt worden
    if permission_type == "write" and doc.status == "Closed":
        return False
    
    # Fallback naar standaard
    return None
```

---

## DocType Override Voorbeeld

hooks.py met controller override:

```python
# hooks.py
override_doctype_class = {
    "Sales Invoice": "myapp.overrides.CustomSalesInvoice"
}
```

```python
# myapp/overrides.py
from erpnext.accounts.doctype.sales_invoice.sales_invoice import SalesInvoice

class CustomSalesInvoice(SalesInvoice):
    def validate(self):
        # ALTIJD super() eerst!
        super().validate()
        
        # Custom validatie
        self.validate_customer_status()
        self.apply_special_discount()
    
    def validate_customer_status(self):
        """Blokkeer facturen voor geblokeerde klanten"""
        customer_status = frappe.db.get_value(
            "Customer", self.customer, "status"
        )
        if customer_status == "Blocked":
            frappe.throw(f"Cannot create invoice for blocked customer {self.customer}")
    
    def apply_special_discount(self):
        """Automatische korting voor VIP klanten"""
        is_vip = frappe.db.get_value("Customer", self.customer, "is_vip")
        if is_vip and not self.discount_amount:
            self.discount_amount = self.grand_total * 0.05  # 5% VIP korting
```

---

## Jinja Extensions Voorbeeld

```python
# hooks.py
jenv = {
    "methods": [
        "myapp.jinja.methods"
    ],
    "filters": [
        "myapp.jinja.filters"
    ]
}
```

```python
# myapp/jinja/methods.py
import frappe

def get_customer_balance(customer):
    """Gebruik in template: {{ get_customer_balance(doc.customer) }}"""
    return frappe.db.get_value(
        "Customer", customer, "outstanding_amount"
    ) or 0

def format_address(address_name):
    """Gebruik: {{ format_address(doc.customer_address) }}"""
    if not address_name:
        return ""
    
    address = frappe.get_doc("Address", address_name)
    parts = [
        address.address_line1,
        address.address_line2,
        f"{address.pincode} {address.city}",
        address.country
    ]
    return "\n".join(filter(None, parts))
```

```python
# myapp/jinja/filters.py
def format_iban(value):
    """Gebruik in template: {{ bank_account | format_iban }}"""
    if not value:
        return ""
    # NL12 ABCD 0123 4567 89
    return " ".join([value[i:i+4] for i in range(0, len(value), 4)])

def highlight_negative(value):
    """Gebruik: {{ amount | highlight_negative }}"""
    if value < 0:
        return f'<span class="text-danger">{value}</span>'
    return str(value)
```

---

## Install/Migrate Hooks

```python
# hooks.py
before_install = "myapp.setup.before_install"
after_install = "myapp.setup.after_install"
after_migrate = "myapp.setup.after_migrate"
```

```python
# myapp/setup.py
import frappe

def before_install():
    """Check prerequisites"""
    # Verify ERPNext version
    pass

def after_install():
    """Post-installation setup"""
    create_default_roles()
    create_default_settings()

def create_default_roles():
    """Maak app-specifieke roles"""
    roles = ["MyApp User", "MyApp Manager"]
    for role in roles:
        if not frappe.db.exists("Role", role):
            frappe.get_doc({
                "doctype": "Role",
                "role_name": role
            }).insert()

def create_default_settings():
    """Initialiseer settings"""
    if not frappe.db.exists("My App Settings"):
        frappe.get_doc({
            "doctype": "My App Settings",
            "enable_feature_x": 1
        }).insert()

def after_migrate():
    """Na elke migrate"""
    clear_custom_cache()

def clear_custom_cache():
    """Clear app-specifieke cache"""
    frappe.cache().delete_key("myapp_config")
```
