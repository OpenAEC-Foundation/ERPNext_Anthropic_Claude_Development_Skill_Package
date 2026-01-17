# Workflow Patterns: Client Script Implementatie (NL)

## Workflow 1: Master-Detail Form

**Use case**: Order form met klantgegevens die automatisch invullen.

### Stap 1: Ontwerp
```
Customer (link) → customer_name, territory, credit_limit (read-only)
```

### Stap 2: Implementatie

```javascript
frappe.ui.form.on('Sales Order', {
    setup(frm) {
        // Read-only velden markeren
        frm.set_df_property('customer_name', 'read_only', 1);
        frm.set_df_property('territory', 'read_only', 1);
    },
    
    refresh(frm) {
        // Toon krediet indicator
        if (frm.doc.credit_limit) {
            frm.dashboard.add_indicator(
                __('Credit: {0}', [format_currency(frm.doc.credit_limit)]),
                'blue'
            );
        }
    },
    
    async customer(frm) {
        if (!frm.doc.customer) {
            frm.set_value({
                customer_name: '',
                territory: '',
                credit_limit: 0
            });
            return;
        }
        
        try {
            let r = await frappe.db.get_value('Customer', frm.doc.customer, 
                ['customer_name', 'territory', 'credit_limit']);
            
            if (r.message) {
                frm.set_value(r.message);
            }
        } catch (e) {
            frappe.show_alert({
                message: __('Could not fetch customer details'),
                indicator: 'red'
            });
        }
    }
});
```

---

## Workflow 2: Conditional Form Sections

**Use case**: Toon verschillende velden op basis van document type.

### Stap 1: Ontwerp
```
order_type = "Standard" → standard_fields zichtbaar
order_type = "Blanket"  → blanket_fields zichtbaar
order_type = "Maintenance" → maintenance_fields zichtbaar
```

### Stap 2: Implementatie

```javascript
frappe.ui.form.on('Sales Order', {
    refresh(frm) {
        frm.trigger('order_type');
    },
    
    order_type(frm) {
        const type = frm.doc.order_type;
        
        // Verberg alle type-specifieke secties
        frm.toggle_display('standard_section', false);
        frm.toggle_display('blanket_section', false);
        frm.toggle_display('maintenance_section', false);
        
        // Toon relevante sectie
        if (type === 'Standard') {
            frm.toggle_display('standard_section', true);
        } else if (type === 'Blanket') {
            frm.toggle_display('blanket_section', true);
            frm.toggle_reqd('blanket_order', true);
        } else if (type === 'Maintenance') {
            frm.toggle_display('maintenance_section', true);
            frm.toggle_reqd(['maintenance_schedule', 'service_level'], true);
        }
    }
});
```

---

## Workflow 3: Real-time Price Calculation

**Use case**: Prijs berekenen met staffelkortingen.

### Stap 1: Ontwerp
```
qty < 10:  standaard prijs
qty 10-50: 5% korting
qty > 50:  10% korting
```

### Stap 2: Implementatie

```javascript
frappe.ui.form.on('Quotation Item', {
    item_code(frm, cdt, cdn) {
        fetch_item_price(frm, cdt, cdn);
    },
    
    qty(frm, cdt, cdn) {
        apply_discount(frm, cdt, cdn);
        calculate_amount(frm, cdt, cdn);
    },
    
    rate(frm, cdt, cdn) {
        calculate_amount(frm, cdt, cdn);
    },
    
    discount_percentage(frm, cdt, cdn) {
        calculate_amount(frm, cdt, cdn);
    }
});

async function fetch_item_price(frm, cdt, cdn) {
    let row = frappe.get_doc(cdt, cdn);
    if (!row.item_code) return;
    
    let r = await frappe.db.get_value('Item Price', 
        {item_code: row.item_code, selling: 1},
        'price_list_rate'
    );
    
    if (r.message) {
        frappe.model.set_value(cdt, cdn, 'rate', r.message.price_list_rate);
    }
}

function apply_discount(frm, cdt, cdn) {
    let row = frappe.get_doc(cdt, cdn);
    let discount = 0;
    
    if (row.qty >= 50) {
        discount = 10;
    } else if (row.qty >= 10) {
        discount = 5;
    }
    
    frappe.model.set_value(cdt, cdn, 'discount_percentage', discount);
}

function calculate_amount(frm, cdt, cdn) {
    let row = frappe.get_doc(cdt, cdn);
    let discount_factor = 1 - (row.discount_percentage || 0) / 100;
    let amount = (row.qty || 0) * (row.rate || 0) * discount_factor;
    
    frappe.model.set_value(cdt, cdn, 'amount', amount);
}
```

---

## Workflow 4: Document Creation Wizard

**Use case**: Sales Order → Sales Invoice met één klik.

### Stap 1: Ontwerp
```
1. Button "Create Invoice" zichtbaar bij submitted Sales Order
2. Klik opent bevestigingsdialog
3. Na bevestiging: maak invoice, open in nieuw scherm
```

### Stap 2: Implementatie

```javascript
frappe.ui.form.on('Sales Order', {
    refresh(frm) {
        // Button alleen bij submitted, niet gefactureerd
        if (frm.doc.docstatus === 1 && frm.doc.per_billed < 100) {
            frm.add_custom_button(__('Sales Invoice'), () => {
                create_invoice(frm);
            }, __('Create'));
        }
    }
});

function create_invoice(frm) {
    frappe.confirm(
        __('Create Sales Invoice from this Sales Order?'),
        async () => {
            try {
                let r = await frappe.call({
                    method: 'erpnext.selling.doctype.sales_order.sales_order.make_sales_invoice',
                    args: { source_name: frm.doc.name },
                    freeze: true,
                    freeze_message: __('Creating Invoice...')
                });
                
                if (r.message) {
                    frappe.model.sync(r.message);
                    frappe.set_route('Form', 'Sales Invoice', r.message.name);
                }
            } catch (e) {
                frappe.msgprint({
                    title: __('Error'),
                    message: __('Could not create invoice: {0}', [e.message]),
                    indicator: 'red'
                });
            }
        }
    );
}
```

---

## Workflow 5: Multi-Step Validation

**Use case**: Complexe validatie met meerdere checks.

### Stap 1: Ontwerp
```
1. Check: items aanwezig
2. Check: totaal > 0
3. Check: klant niet geblokkeerd
4. Check: kredietlimiet OK (server call)
```

### Stap 2: Implementatie

```javascript
frappe.ui.form.on('Sales Order', {
    async validate(frm) {
        // Stap 1: Items check
        if (!frm.doc.items || frm.doc.items.length === 0) {
            frappe.throw(__('Please add at least one item'));
        }
        
        // Stap 2: Totaal check
        if (frm.doc.grand_total <= 0) {
            frappe.throw(__('Order total must be greater than zero'));
        }
        
        // Stap 3 & 4: Server validatie
        let r = await frappe.call({
            method: 'myapp.validations.validate_sales_order',
            args: {
                customer: frm.doc.customer,
                amount: frm.doc.grand_total
            }
        });
        
        if (r.message) {
            if (r.message.customer_disabled) {
                frappe.throw(__('Customer {0} is disabled', [frm.doc.customer]));
            }
            if (r.message.credit_exceeded) {
                frappe.throw(__('Credit limit exceeded by {0}', 
                    [format_currency(r.message.exceeded_by)]));
            }
        }
    }
});
```

---

## Workflow 6: Auto-populate Child Table

**Use case**: Selecteer template → vul items automatisch in.

```javascript
frappe.ui.form.on('Sales Order', {
    async order_template(frm) {
        if (!frm.doc.order_template) return;
        
        // Bevestig als er al items zijn
        if (frm.doc.items && frm.doc.items.length > 0) {
            let confirmed = await new Promise(resolve => {
                frappe.confirm(
                    __('This will replace existing items. Continue?'),
                    () => resolve(true),
                    () => resolve(false)
                );
            });
            
            if (!confirmed) {
                frm.set_value('order_template', '');
                return;
            }
        }
        
        // Haal template items op
        let template = await frappe.db.get_doc(
            'Order Template', 
            frm.doc.order_template
        );
        
        // Clear en vul
        frm.clear_table('items');
        
        for (let tpl_item of template.items) {
            frm.add_child('items', {
                item_code: tpl_item.item_code,
                qty: tpl_item.qty,
                rate: tpl_item.rate
            });
        }
        
        frm.refresh_field('items');
        frappe.show_alert({
            message: __('Added {0} items from template', [template.items.length]),
            indicator: 'green'
        });
    }
});
```

---

## Workflow 7: Real-time Collaboration Indicator

**Use case**: Toon wie document aan het bewerken is.

```javascript
frappe.ui.form.on('Project', {
    onload(frm) {
        if (!frm.is_new()) {
            // Publiceer dat we dit document bekijken
            frappe.realtime.emit('viewing_document', {
                doctype: frm.doc.doctype,
                name: frm.doc.name,
                user: frappe.session.user
            });
            
            // Luister naar anderen
            frappe.realtime.on('viewing_document', (data) => {
                if (data.doctype === frm.doc.doctype && 
                    data.name === frm.doc.name &&
                    data.user !== frappe.session.user) {
                    
                    frappe.show_alert({
                        message: __('User {0} is also viewing this document', 
                            [data.user]),
                        indicator: 'yellow'
                    }, 10);
                }
            });
        }
    }
});
```
