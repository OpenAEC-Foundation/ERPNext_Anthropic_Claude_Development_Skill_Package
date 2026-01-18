# Boot Hooks Reference

Complete referentie voor `extend_bootinfo` en gerelateerde boot hooks in hooks.py.

---

## extend_bootinfo

Voeg globale waarden toe aan `frappe.boot` die beschikbaar zijn in client-side JavaScript.

### Syntax

```python
# In hooks.py
extend_bootinfo = "myapp.boot.extend_boot"
```

### Handler Implementatie

```python
# In myapp/boot.py
import frappe

def extend_boot(bootinfo):
    """
    bootinfo is een dict-like object dat wordt geïnjecteerd in frappe.boot
    
    Args:
        bootinfo: frappe.boot object (dict-like)
    """
    # Eenvoudige waarde
    bootinfo.my_app_version = "1.0.0"
    
    # Configuratie ophalen
    bootinfo.app_settings = frappe.get_single("My App Settings").as_dict()
    
    # User-specifieke data
    bootinfo.user_preferences = get_user_preferences(frappe.session.user)
```

### Client-Side Toegang

```javascript
// Overal in JavaScript beschikbaar na page load
console.log(frappe.boot.my_app_version);  // "1.0.0"
console.log(frappe.boot.app_settings);     // {key: value, ...}
console.log(frappe.boot.user_preferences); // {theme: "dark", ...}
```

---

## Wat frappe.boot Standaard Bevat

| Property | Inhoud |
|----------|--------|
| `frappe.boot.user` | Huidige user info |
| `frappe.boot.home_page` | Home page route |
| `frappe.boot.user_info` | User metadata |
| `frappe.boot.lang` | Actieve taal |
| `frappe.boot.sysdefaults` | System defaults |
| `frappe.boot.notification_settings` | Notification config |
| `frappe.boot.modules` | Beschikbare modules |
| `frappe.boot.module_list` | Module lijst |
| `frappe.boot.desk_settings` | Desk configuratie |

---

## Voorbeelden

### Feature Flags

```python
# myapp/boot.py
def extend_boot(bootinfo):
    settings = frappe.get_single("My App Settings")
    bootinfo.feature_flags = {
        "new_dashboard": settings.enable_new_dashboard,
        "beta_features": settings.enable_beta,
        "dark_mode": settings.allow_dark_mode
    }
```

```javascript
// Client-side
if (frappe.boot.feature_flags.new_dashboard) {
    load_new_dashboard();
}
```

### User Permissions Cache

```python
def extend_boot(bootinfo):
    user = frappe.session.user
    bootinfo.custom_permissions = {
        "can_approve_orders": has_approval_rights(user),
        "max_discount_percent": get_max_discount(user),
        "allowed_warehouses": get_user_warehouses(user)
    }
```

```javascript
// Client-side permission check
frappe.ui.form.on("Sales Order", {
    refresh(frm) {
        if (frappe.boot.custom_permissions.can_approve_orders) {
            frm.add_custom_button("Approve", () => approve_order(frm));
        }
    }
});
```

### Company Settings

```python
def extend_boot(bootinfo):
    if frappe.session.user != "Guest":
        default_company = frappe.defaults.get_user_default("Company")
        if default_company:
            bootinfo.company_settings = frappe.db.get_value(
                "Company", 
                default_company,
                ["default_currency", "country", "tax_id"],
                as_dict=True
            )
```

### API Endpoints

```python
def extend_boot(bootinfo):
    bootinfo.api_endpoints = {
        "external_api": frappe.get_single("API Settings").external_api_url,
        "webhook_url": frappe.utils.get_url("/api/method/myapp.webhook.handle")
    }
```

---

## Best Practices

### ✅ DO: Cache Waar Mogelijk

```python
def extend_boot(bootinfo):
    # Gebruik cache voor veelgebruikte data
    cache_key = f"user_settings:{frappe.session.user}"
    settings = frappe.cache().get_value(cache_key)
    
    if not settings:
        settings = compute_user_settings()
        frappe.cache().set_value(cache_key, settings, expires_in_sec=3600)
    
    bootinfo.user_settings = settings
```

### ✅ DO: Minimale Data

```python
def extend_boot(bootinfo):
    # GOED - alleen noodzakelijke velden
    bootinfo.company_info = frappe.db.get_value(
        "Company", 
        frappe.defaults.get_user_default("Company"),
        ["name", "default_currency"],
        as_dict=True
    )
```

### ❌ DON'T: Gevoelige Data

```python
# FOUT - API keys in frontend
def extend_boot(bootinfo):
    bootinfo.api_key = frappe.get_single("Settings").secret_api_key  # NOOIT!
```

### ❌ DON'T: Zware Queries

```python
# FOUT - te zwaar voor elke page load
def extend_boot(bootinfo):
    bootinfo.all_customers = frappe.get_all("Customer")  # Kan duizenden records zijn
```

---

## Gerelateerde Hooks

### on_session_creation

Triggered wanneer een nieuwe sessie wordt aangemaakt (login):

```python
# hooks.py
on_session_creation = "myapp.events.on_session_creation"

# myapp/events.py
def on_session_creation():
    """Geen argumenten - gebruik frappe.session"""
    frappe.log_error(f"New session: {frappe.session.user}")
```

### on_login

Triggered direct na succesvolle login:

```python
# hooks.py
on_login = "myapp.events.on_login"

# myapp/events.py
def on_login(login_manager):
    """
    Args:
        login_manager: frappe.auth.LoginManager instance
    """
    user = login_manager.user
    frappe.db.set_value("User", user, "last_login_ip", frappe.local.request_ip)
```

### on_logout

Triggered bij logout:

```python
# hooks.py
on_logout = "myapp.events.on_logout"

# myapp/events.py
def on_logout():
    """Cleanup bij logout"""
    frappe.cache().delete_key(f"user_cache:{frappe.session.user}")
```

---

## Volgorde van Uitvoering

```
1. User login succesvol
2. on_login hook
3. Session aangemaakt
4. on_session_creation hook
5. Boot data verzameld
6. extend_bootinfo hook
7. frappe.boot naar client gestuurd
```

---

## Debugging

### Boot Data Inspecteren

```javascript
// In browser console
console.log(frappe.boot);
console.log(JSON.stringify(frappe.boot.my_custom_key, null, 2));
```

### Server-Side Testen

```python
# In bench console
bootinfo = frappe._dict()
from myapp.boot import extend_boot
extend_boot(bootinfo)
print(bootinfo)
```

---

## Versie Verschillen

| Feature | v14 | v15 |
|---------|-----|-----|
| extend_bootinfo | ✅ | ✅ |
| on_session_creation | ✅ | ✅ |
| on_login / on_logout | ✅ | ✅ |
| Boot data compressie | - | ✅ Verbeterd |
