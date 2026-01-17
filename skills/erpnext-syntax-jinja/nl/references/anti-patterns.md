# Anti-Patterns: Fouten te Vermijden

> Veelgemaakte fouten in Jinja templates en hoe ze te voorkomen.

---

## ❌ Query in Loop (N+1 Problem)

### Fout

```jinja
{% for item in doc.items %}
    {% set stock = frappe.db.get_value("Bin", {"item_code": item.item_code}, "actual_qty") %}
    <p>{{ item.item_name }}: {{ stock }} in stock</p>
{% endfor %}
```

**Probleem**: Bij 100 items worden 100+ database queries uitgevoerd.

### Correct

```python
# In Python controller/print format script
def get_context(context):
    item_codes = [item.item_code for item in doc.items]
    bins = frappe.get_all("Bin", 
        filters={"item_code": ["in", item_codes]},
        fields=["item_code", "actual_qty"]
    )
    context.stock_qty = {b.item_code: b.actual_qty for b in bins}
```

```jinja
{% for item in doc.items %}
    <p>{{ item.item_name }}: {{ stock_qty.get(item.item_code, 0) }} in stock</p>
{% endfor %}
```

---

## ❌ Zware Berekeningen in Template

### Fout

```jinja
{% set complex_total = 0 %}
{% for item in doc.items %}
    {% set item_discount = item.rate * (item.discount_percentage / 100) %}
    {% set item_tax = (item.rate - item_discount) * 0.21 %}
    {% set item_total = (item.rate - item_discount + item_tax) * item.qty %}
    {% set complex_total = complex_total + item_total %}
{% endfor %}
<p>Total: {{ complex_total }}</p>
```

### Correct

Doe berekeningen in Python, niet in Jinja:

```python
# In controller
def get_context(context):
    total = 0
    for item in doc.items:
        discount = item.rate * (item.discount_percentage / 100)
        tax = (item.rate - discount) * 0.21
        total += (item.rate - discount + tax) * item.qty
    context.calculated_total = total
```

```jinja
<p>Total: {{ calculated_total }}</p>
```

---

## ❌ Ongeëscapete User Input (XSS Risico)

### Fout

```jinja
{# GEVAARLIJK - XSS risico #}
{{ user_comment | safe }}
{{ frappe.form_dict.search | safe }}
```

### Correct

```jinja
{# Automatisch escaped (veilig) #}
{{ user_comment }}

{# Alleen safe gebruiken voor vertrouwde admin content #}
{{ doc.terms | safe }}  {# Alleen als terms door admin is ingevoerd #}

{# Expliciet escapen bij twijfel #}
{{ potentially_unsafe | escape }}
```

---

## ❌ Hardcoded Strings (Niet Vertaalbaar)

### Fout

```jinja
<th>Invoice Number</th>
<th>Amount</th>
<p>Thank you for your business!</p>
```

### Correct

```jinja
<th>{{ _("Invoice Number") }}</th>
<th>{{ _("Amount") }}</th>
<p>{{ _("Thank you for your business!") }}</p>

{# Met variabelen #}
<p>{{ _("Total: {0}").format(doc.grand_total) }}</p>
```

---

## ❌ Geen Default Values

### Fout

```jinja
{# Kan falen als veld None is #}
<p>{{ doc.customer_group }}</p>
<p>{{ doc.notes | truncate(100) }}</p>
```

### Correct

```jinja
<p>{{ doc.customer_group | default('Not Set') }}</p>
<p>{{ doc.notes | default('') | truncate(100) }}</p>

{# Of met conditie #}
{% if doc.notes %}
    <p>{{ doc.notes | truncate(100) }}</p>
{% endif %}
```

---

## ❌ Verkeerde Currency Formatting

### Fout

```jinja
{# Geen currency symbol, verkeerd format #}
<p>{{ doc.grand_total }}</p>
<p>{{ "%.2f" | format(doc.grand_total) }}</p>
```

### Correct

```jinja
{# Gebruik get_formatted voor currency velden #}
<p>{{ doc.get_formatted("grand_total") }}</p>

{# Of frappe.format met fieldtype #}
<p>{{ frappe.format(doc.grand_total, {'fieldtype': 'Currency'}) }}</p>

{# Voor child table items - parent doc meegeven #}
{% for row in doc.items %}
    <td>{{ row.get_formatted("amount", doc) }}</td>
{% endfor %}
```

---

## ❌ Vergeten Loop Variables

### Fout

```jinja
{% for item in doc.items %}
    <tr class="{% if loop.index == 1 %}first{% endif %}">
        <td>{{ item.idx }}</td>  {# idx kan afwijken van loop positie #}
    </tr>
{% endfor %}
```

### Correct

```jinja
{% for item in doc.items %}
    <tr class="{% if loop.first %}first{% endif %}{% if loop.last %} last{% endif %}">
        <td>{{ loop.index }}</td>  {# Consistente nummering #}
    </tr>
{% endfor %}
```

### Beschikbare Loop Variables

| Variable | Beschrijving |
|----------|--------------|
| `loop.index` | 1-indexed positie |
| `loop.index0` | 0-indexed positie |
| `loop.first` | True bij eerste iteratie |
| `loop.last` | True bij laatste iteratie |
| `loop.length` | Totaal aantal items |

---

## ❌ Jinja Syntax in Report Print Formats

### Fout

```html
<!-- Dit werkt NIET in Report Print Formats -->
{% for item in data %}
    <tr><td>{{ item.name }}</td></tr>
{% endfor %}
```

### Correct

Report Print Formats gebruiken JavaScript templating:

```html
<!-- JS Template syntax voor Reports -->
{% for(var i=0; i<data.length; i++) { %}
<tr>
    <td>{%= data[i].name %}</td>
</tr>
{% } %}
```

**Let op**: Gebruik GEEN single quotes `'` in JS templates.

---

## ❌ Inefficiënt Document Ophalen

### Fout

```jinja
{# Volledig document ophalen voor één veld #}
{% set customer = frappe.get_doc("Customer", doc.customer) %}
<p>{{ customer.customer_group }}</p>
```

### Correct

```jinja
{# Alleen het benodigde veld ophalen #}
{% set customer_group = frappe.db.get_value("Customer", doc.customer, "customer_group") %}
<p>{{ customer_group }}</p>

{# Of meerdere velden tegelijk #}
{% set name, group = frappe.db.get_value("Customer", doc.customer, ["customer_name", "customer_group"]) %}
```

---

## ❌ Safe Render Uitschakelen Zonder Reden

### Fout

```python
# Zonder goede reden safe_render uitschakelen
def get_context(context):
    context.safe_render = False  # GEVAARLIJK
```

### Correct

Safe render beschermt tegen code injection. Alleen uitschakelen als absoluut noodzakelijk en je zeker weet dat alle input veilig is:

```python
def get_context(context):
    # Alleen uitschakelen met goede reden en na security review
    # context.safe_render = False
    pass
```

---

## Samenvatting: Best Practices

1. **ALTIJD** `_()` gebruiken voor user-facing strings
2. **ALTIJD** `get_formatted()` gebruiken voor currency/date velden
3. **NOOIT** queries in loops uitvoeren
4. **NOOIT** `| safe` gebruiken voor user input
5. **ALTIJD** default values gebruiken voor optionele velden
6. **ALTIJD** berekeningen in Python doen, niet in Jinja
7. **ONTHOUD** dat Report Print Formats JS gebruiken, niet Jinja
