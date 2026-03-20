# Decorator Options Reference

Volledige documentatie van alle `@frappe.whitelist()` parameters.

## Signature

```python
def whitelist(
    allow_guest: bool = False,
    xss_safe: bool = False,
    methods: list[str] | None = None
) -> Callable
```

## Parameters

### allow_guest

| Waarde | Gedrag |
|--------|--------|
| `False` (default) | Alleen ingelogde users kunnen de method aanroepen |
| `True` | Ook niet-ingelogde users (Guest role) kunnen aanroepen |

```python
# Standaard - alleen authenticated users
@frappe.whitelist()
def internal_api():
    return {"data": "only for logged in users"}

# Public - iedereen kan aanroepen
@frappe.whitelist(allow_guest=True)
def public_api():
    return {"status": "available"}
```

**Wanneer `allow_guest=True` gebruiken:**
- Publieke informatie endpoints (status, versie)
- Contact formulieren
- Registratie endpoints
- Webhook ontvangers

**âš ï¸ Let op**: Bij `allow_guest=True` is extra input validatie essentieel.

### methods

| Waarde | Toegestane HTTP Methods |
|--------|------------------------|
| `None` (default) | GET, POST, PUT, DELETE |
| `["GET"]` | Alleen GET |
| `["POST"]` | Alleen POST |
| `["GET", "POST"]` | GET en POST |

```python
# Alleen lees-operaties
@frappe.whitelist(methods=["GET"])
def get_status(order_id):
    return frappe.db.get_value("Sales Order", order_id, "status")

# Alleen schrijf-operaties
@frappe.whitelist(methods=["POST"])
def update_status(order_id, status):
    frappe.db.set_value("Sales Order", order_id, "status", status)
    return {"updated": True}

# Meerdere methods
@frappe.whitelist(methods=["GET", "POST"])
def data_endpoint(param):
    if frappe.request.method == "GET":
        return get_data(param)
    else:
        return save_data(param)
```

**Best Practice**: Gebruik `methods=["GET"]` voor read-only endpoints en `methods=["POST"]` voor write operaties.

### xss_safe

| Waarde | Gedrag |
|--------|--------|
| `False` (default) | HTML in response wordt ge-escaped |
| `True` | HTML wordt NIET ge-escaped |

```python
# HTML content retourneren
@frappe.whitelist(xss_safe=True)
def get_html_content():
    return "<strong>Bold text</strong>"

# Zonder xss_safe zou dit worden: &lt;strong&gt;Bold text&lt;/strong&gt;
```

**âš ï¸ Waarschuwing**: Gebruik `xss_safe=True` alleen wanneer:
- Je gecontroleerde HTML retourneert
- Input grondig is gevalideerd
- XSS attacks niet mogelijk zijn

## Combinaties

### Public POST Endpoint

```python
@frappe.whitelist(allow_guest=True, methods=["POST"])
def submit_contact_form(name, email, message):
    """
    Contact formulier - publiek toegankelijk, alleen POST.
    """
    # Valideer input extra zorgvuldig bij guest access
    if not name or not email:
        frappe.throw(_("Name and email are required"))
    
    doc = frappe.get_doc({
        "doctype": "Contact Form Submission",
        "name1": name,
        "email": email,
        "message": message
    })
    doc.insert(ignore_permissions=True)
    
    return {"success": True}
```

### Public HTML Endpoint

```python
@frappe.whitelist(allow_guest=True, xss_safe=True)
def get_public_page():
    """
    Publieke HTML pagina - geen escaping.
    """
    return frappe.render_template("myapp/templates/public.html", {})
```

### Read-Only Internal API

```python
@frappe.whitelist(methods=["GET"])
def get_dashboard_data():
    """
    Dashboard data - alleen lezen, alleen ingelogde users.
    """
    if not frappe.has_permission("Sales Order", "read"):
        frappe.throw(_("Not permitted"), frappe.PermissionError)
    
    return {
        "total_orders": frappe.db.count("Sales Order"),
        "pending": frappe.db.count("Sales Order", {"status": "Draft"})
    }
```

## Foutmeldingen bij Verkeerd Gebruik

| Situatie | Error |
|----------|-------|
| Niet-ingelogde user op non-guest method | `frappe.AuthenticationError` |
| Verkeerde HTTP method | `405 Method Not Allowed` |
| Geen `@frappe.whitelist()` decorator | `Method not found` |

## Checklist

Bij het maken van een nieuwe whitelisted method:

- [ ] Decorator toegevoegd: `@frappe.whitelist()`
- [ ] `allow_guest` correct ingesteld (default is veilig)
- [ ] `methods` beperkt indien mogelijk
- [ ] Permission check aanwezig (tenzij `allow_guest=True` met publieke data)
- [ ] Input validatie aanwezig
