---
name: erpnext-impl-clientscripts
description: "Implementatie workflows en decision trees voor ERPNext Client Scripts. Gebruik wanneer je moet bepalen HOE je een client-side feature implementeert: form validaties, dynamische UI, server integratie, child table logica. Triggers: hoe implementeer ik, wanneer gebruik ik, welke aanpak, client script workflow, form logica bouwen, UI dynamisch maken, velden berekenen."
---

# ERPNext Client Scripts - Implementatie (NL)

Deze skill helpt je bepalen HOE je client-side features implementeert. Voor exacte syntax, zie `erpnext-syntax-clientscripts`.

**Versie**: v14/v15 compatible

## Hoofdbeslissing: Client of Server?

```
┌─────────────────────────────────────────────────────────┐
│ Moet de logica ALTIJD uitgevoerd worden?                │
│ (ook bij imports, API calls, Server Scripts)            │
├─────────────────────────────────────────────────────────┤
│ JA → Server-side (Controller of Server Script)          │
│ NEE → Wat is het primaire doel?                         │
│       ├── UI feedback/UX verbetering → Client Script    │
│       ├── Velden tonen/verbergen → Client Script        │
│       ├── Link filters → Client Script                  │
│       ├── Data validatie → BEIDE (client + server)      │
│       └── Berekeningen → Afhankelijk van criticiteit    │
└─────────────────────────────────────────────────────────┘
```

**Vuistregel**: Client Scripts voor UX, Server voor integriteit.

## Decision Tree: Welk Event?

```
WAT WIL JE BEREIKEN?
│
├─► Link field filters instellen
│   └── setup (eenmalig, vroeg in lifecycle)
│
├─► Custom buttons toevoegen
│   └── refresh (na elke form load/save)
│
├─► Velden tonen/verbergen op basis van conditie
│   └── refresh + {fieldname} (beide nodig)
│
├─► Validatie voor opslaan
│   └── validate (met frappe.throw bij fout)
│
├─► Actie na succesvol opslaan
│   └── after_save
│
├─► Berekening bij veld wijziging
│   └── {fieldname}
│
├─► Child table rij toegevoegd
│   └── {tablename}_add
│
├─► Child table veld gewijzigd
│   └── Child DocType event: {fieldname}
│
└─► Eenmalige initialisatie
    └── setup of onload
```

→ Zie [references/decision-tree.md](references/decision-tree.md) voor complete beslisboom.

## Implementatie Workflows

### Workflow 1: Dynamische Veld Visibility

**Scenario**: Toon "delivery_date" alleen als "requires_delivery" is aangevinkt.

```javascript
frappe.ui.form.on('Sales Order', {
    refresh(frm) {
        // Initiële staat bij form load
        frm.trigger('requires_delivery');
    },
    
    requires_delivery(frm) {
        // Toggle bij checkbox change EN refresh
        frm.toggle_display('delivery_date', frm.doc.requires_delivery);
        frm.toggle_reqd('delivery_date', frm.doc.requires_delivery);
    }
});
```

**Waarom beide events?**
- `refresh`: Zet juiste staat bij form open
- `{fieldname}`: Reageert op gebruiker interactie

### Workflow 2: Cascading Dropdowns

**Scenario**: Filter "city" op basis van geselecteerde "country".

```javascript
frappe.ui.form.on('Customer', {
    setup(frm) {
        // Filter MOET in setup voor consistentie
        frm.set_query('city', () => ({
            filters: {
                country: frm.doc.country || ''
            }
        }));
    },
    
    country(frm) {
        // Clear city wanneer country wijzigt
        frm.set_value('city', '');
    }
});
```

### Workflow 3: Automatische Berekeningen

**Scenario**: Bereken totaal in child table met korting.

```javascript
frappe.ui.form.on('Sales Invoice', {
    discount_percentage(frm) {
        calculate_totals(frm);
    }
});

frappe.ui.form.on('Sales Invoice Item', {
    qty(frm, cdt, cdn) {
        calculate_row_amount(frm, cdt, cdn);
    },
    
    rate(frm, cdt, cdn) {
        calculate_row_amount(frm, cdt, cdn);
    },
    
    amount(frm) {
        // Herbereken document totaal bij rij wijziging
        calculate_totals(frm);
    }
});

function calculate_row_amount(frm, cdt, cdn) {
    let row = frappe.get_doc(cdt, cdn);
    frappe.model.set_value(cdt, cdn, 'amount', row.qty * row.rate);
}

function calculate_totals(frm) {
    let total = 0;
    (frm.doc.items || []).forEach(row => {
        total += row.amount || 0;
    });
    
    let discount = total * (frm.doc.discount_percentage || 0) / 100;
    frm.set_value('grand_total', total - discount);
}
```

### Workflow 4: Server Data Ophalen

**Scenario**: Vul klantgegevens in bij selectie van customer.

```javascript
frappe.ui.form.on('Sales Order', {
    async customer(frm) {
        if (!frm.doc.customer) {
            // Clear velden als customer leeggemaakt
            frm.set_value({
                customer_name: '',
                territory: '',
                credit_limit: 0
            });
            return;
        }
        
        // Haal klantgegevens op
        let r = await frappe.db.get_value('Customer', 
            frm.doc.customer, 
            ['customer_name', 'territory', 'credit_limit']
        );
        
        if (r.message) {
            frm.set_value({
                customer_name: r.message.customer_name,
                territory: r.message.territory,
                credit_limit: r.message.credit_limit
            });
        }
    }
});
```

### Workflow 5: Validatie met Server Check

**Scenario**: Controleer kredietlimiet voor opslaan.

```javascript
frappe.ui.form.on('Sales Order', {
    async validate(frm) {
        if (frm.doc.customer && frm.doc.grand_total) {
            let r = await frappe.call({
                method: 'myapp.api.check_credit',
                args: {
                    customer: frm.doc.customer,
                    amount: frm.doc.grand_total
                }
            });
            
            if (r.message && !r.message.allowed) {
                frappe.throw(__('Credit limit exceeded. Available: {0}', 
                    [r.message.available]));
            }
        }
    }
});
```

→ Zie [references/workflows.md](references/workflows.md) voor meer workflow patterns.

## Integratie Matrix

| Client Script Actie | Vereist Server-side |
|---------------------|---------------------|
| Link filters | Optioneel: custom query |
| Server data ophalen | `frappe.db.*` of whitelisted method |
| Document method aanroepen | `@frappe.whitelist()` in controller |
| Complexe validatie | Server Script of controller validation |
| Document aanmaken | `frappe.db.insert` of whitelisted method |

### Client + Server Combinatie

```javascript
// CLIENT: frm.call roept controller method aan
frm.call('calculate_taxes')
    .then(() => frm.reload_doc());

// SERVER (controller): MOET @frappe.whitelist hebben
class SalesInvoice(Document):
    @frappe.whitelist()
    def calculate_taxes(self):
        # complexe berekening
        self.tax_amount = self.grand_total * 0.21
        self.save()
```

## Checklist: Implementatie Stappen

### Nieuwe Client Script Feature

1. **[ ] Bepaal scope**
   - Alleen UI/UX? → Alleen client script
   - Data integriteit? → Ook server validatie

2. **[ ] Kies events**
   - Gebruik decision tree hierboven
   - Combineer refresh + fieldname voor visibility

3. **[ ] Implementeer basis**
   - Start met `frappe.ui.form.on`
   - Test met console.log eerst

4. **[ ] Voeg error handling toe**
   - `try/catch` rond async calls
   - `frappe.throw` voor validatie fouten

5. **[ ] Test edge cases**
   - Nieuw document (frm.is_new())
   - Leeg veld (null checks)
   - Child table leeg/gevuld

6. **[ ] Vertaal strings**
   - Alle UI tekst in `__()`

## Kritieke Regels

| Regel | Waarom |
|-------|--------|
| `refresh_field()` na child table wijziging | UI synchronisatie |
| `set_query` in `setup` event | Consistente filter werking |
| `frappe.throw()` voor validatie, niet `msgprint` | Stop save actie |
| Async/await voor server calls | Voorkom race conditions |
| Check `frm.is_new()` voor buttons | Voorkom errors op nieuw doc |

## Gerelateerde Skills

- `erpnext-syntax-clientscripts` — Exacte syntax en method signatures
- `erpnext-errors-clientscripts` — Error handling patterns
- `erpnext-syntax-whitelisted` — Server methods voor frm.call
- `erpnext-database` — frappe.db.* client-side API

→ Zie [references/examples.md](references/examples.md) voor 10+ complete implementatie voorbeelden.
