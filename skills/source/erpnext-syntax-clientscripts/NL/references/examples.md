# Client Script Voorbeelden (NL)

## Voorbeeld 1: Basis Form Setup met Filters

```javascript
frappe.ui.form.on('Sales Order', {
    setup(frm) {
        // Filter customers op niet-disabled
        frm.set_query('customer', () => ({
            filters: { disabled: 0 }
        }));
        
        // Filter items in child table op sales items
        frm.set_query('item_code', 'items', () => ({
            filters: { 
                is_sales_item: 1,
                disabled: 0 
            }
        }));
    }
});
```

## Voorbeeld 2: Conditionele Veld Visibility

```javascript
frappe.ui.form.on('Sales Invoice', {
    refresh(frm) {
        // Toon shipping fields alleen als er shipping is
        let has_shipping = frm.doc.shipping_amount > 0;
        frm.toggle_display('shipping_address', has_shipping);
        frm.toggle_display('shipping_method', has_shipping);
        frm.toggle_reqd('shipping_address', has_shipping);
    },
    
    shipping_amount(frm) {
        // Hertrigger visibility bij wijziging
        frm.trigger('refresh');
    }
});
```

## Voorbeeld 3: Custom Buttons met Groepen

```javascript
frappe.ui.form.on('Sales Order', {
    refresh(frm) {
        // Alleen voor submitted documents
        if (frm.doc.docstatus === 1) {
            // Create dropdown met opties
            frm.add_custom_button(__('Sales Invoice'), () => {
                frappe.model.open_mapped_doc({
                    method: 'erpnext.selling.doctype.sales_order.sales_order.make_sales_invoice',
                    frm: frm
                });
            }, __('Create'));
            
            frm.add_custom_button(__('Delivery Note'), () => {
                frappe.model.open_mapped_doc({
                    method: 'erpnext.selling.doctype.sales_order.sales_order.make_delivery_note',
                    frm: frm
                });
            }, __('Create'));
            
            // Standalone button
            frm.add_custom_button(__('Send Email'), () => {
                frm.call('send_notification_email');
            });
        }
    }
});
```

## Voorbeeld 4: Validatie met frappe.throw

```javascript
frappe.ui.form.on('Sales Invoice', {
    validate(frm) {
        // Valideer totaal
        if (frm.doc.grand_total <= 0) {
            frappe.throw(__('Grand total must be greater than zero'));
        }
        
        // Valideer items
        if (!frm.doc.items || frm.doc.items.length === 0) {
            frappe.throw(__('At least one item is required'));
        }
        
        // Valideer datum
        if (frm.doc.due_date && frm.doc.due_date < frm.doc.posting_date) {
            frappe.throw(__('Due date cannot be before posting date'));
        }
        
        // Valideer per item
        frm.doc.items.forEach((item, idx) => {
            if (item.qty <= 0) {
                frappe.throw(__('Row {0}: Quantity must be positive', [idx + 1]));
            }
        });
    }
});
```

## Voorbeeld 5: Linked Data Ophalen

```javascript
frappe.ui.form.on('Sales Order', {
    customer(frm) {
        if (frm.doc.customer) {
            // Haal customer details op
            frappe.db.get_value('Customer', frm.doc.customer, 
                ['customer_group', 'territory', 'default_currency', 'credit_limit'])
                .then(r => {
                    if (r.message) {
                        frm.set_value('customer_group', r.message.customer_group);
                        frm.set_value('territory', r.message.territory);
                        frm.set_value('currency', r.message.default_currency);
                        
                        // Toon credit limit info
                        if (r.message.credit_limit) {
                            frappe.show_alert({
                                message: __('Credit limit: {0}', [r.message.credit_limit]),
                                indicator: 'blue'
                            });
                        }
                    }
                });
        }
    }
});
```

## Voorbeeld 6: Child Table Auto-Calculatie

```javascript
frappe.ui.form.on('Sales Invoice Item', {
    qty(frm, cdt, cdn) {
        calculate_row_amount(frm, cdt, cdn);
    },
    
    rate(frm, cdt, cdn) {
        calculate_row_amount(frm, cdt, cdn);
    },
    
    discount_percentage(frm, cdt, cdn) {
        calculate_row_amount(frm, cdt, cdn);
    },
    
    items_remove(frm) {
        calculate_totals(frm);
    }
});

function calculate_row_amount(frm, cdt, cdn) {
    let row = frappe.get_doc(cdt, cdn);
    let amount = row.qty * row.rate;
    
    if (row.discount_percentage) {
        amount = amount * (1 - row.discount_percentage / 100);
    }
    
    frappe.model.set_value(cdt, cdn, 'amount', amount);
    calculate_totals(frm);
}

function calculate_totals(frm) {
    let total = 0;
    frm.doc.items.forEach(item => {
        total += item.amount || 0;
    });
    
    frm.set_value('net_total', total);
    frm.set_value('grand_total', total * 1.21);  // BTW 21%
}
```

## Voorbeeld 7: Server Method Aanroep met Feedback

```javascript
frappe.ui.form.on('Sales Order', {
    refresh(frm) {
        if (!frm.is_new() && frm.doc.docstatus === 0) {
            frm.add_custom_button(__('Check Stock'), async () => {
                try {
                    let r = await frappe.call({
                        method: 'myapp.api.check_stock_availability',
                        args: { 
                            sales_order: frm.doc.name,
                            warehouse: frm.doc.set_warehouse
                        },
                        freeze: true,
                        freeze_message: __('Checking stock availability...')
                    });
                    
                    if (r.message.all_available) {
                        frappe.show_alert({
                            message: __('All items are available'),
                            indicator: 'green'
                        });
                    } else {
                        frappe.msgprint({
                            title: __('Stock Warning'),
                            message: __('The following items have insufficient stock: {0}', 
                                [r.message.unavailable_items.join(', ')]),
                            indicator: 'orange'
                        });
                    }
                } catch (e) {
                    frappe.msgprint({
                        title: __('Error'),
                        message: __('Could not check stock availability'),
                        indicator: 'red'
                    });
                }
            });
        }
    }
});
```

## Voorbeeld 8: Dynamische Veld Properties

```javascript
frappe.ui.form.on('Purchase Order', {
    refresh(frm) {
        // Status-based field properties
        let is_draft = frm.doc.docstatus === 0;
        let is_submitted = frm.doc.docstatus === 1;
        
        // Supplier niet wijzigbaar na submit
        frm.toggle_enable('supplier', is_draft);
        
        // Delivery date verplicht voor submitted
        frm.toggle_reqd('schedule_date', is_submitted);
    },
    
    supplier(frm) {
        if (frm.doc.supplier) {
            // Update payment terms gebaseerd op supplier
            frappe.db.get_value('Supplier', frm.doc.supplier, 'payment_terms')
                .then(r => {
                    if (r.message.payment_terms) {
                        frm.set_value('payment_terms_template', r.message.payment_terms);
                    }
                });
        }
    },
    
    order_type(frm) {
        // Wijzig beschikbare opties gebaseerd op type
        if (frm.doc.order_type === 'Shopping Cart') {
            frm.set_df_property('shipping_rule', 'reqd', 1);
            frm.set_df_property('shipping_rule', 'hidden', 0);
        } else {
            frm.set_df_property('shipping_rule', 'reqd', 0);
            frm.set_df_property('shipping_rule', 'hidden', 1);
        }
    }
});
```

## Voorbeeld 9: Bevestigingsdialoog voor Actie

```javascript
frappe.ui.form.on('Sales Invoice', {
    refresh(frm) {
        if (frm.doc.docstatus === 1 && frm.doc.outstanding_amount > 0) {
            frm.add_custom_button(__('Write Off'), () => {
                frappe.confirm(
                    __('Are you sure you want to write off {0}?', 
                        [format_currency(frm.doc.outstanding_amount, frm.doc.currency)]),
                    () => {
                        // Gebruiker bevestigde
                        frappe.call({
                            method: 'myapp.api.write_off_invoice',
                            args: { invoice: frm.doc.name },
                            callback: (r) => {
                                if (r.message) {
                                    frappe.show_alert({
                                        message: __('Invoice written off'),
                                        indicator: 'green'
                                    });
                                    frm.reload_doc();
                                }
                            }
                        });
                    },
                    () => {
                        // Gebruiker annuleerde
                        frappe.show_alert(__('Cancelled'));
                    }
                );
            });
        }
    }
});
```

## Voorbeeld 10: Child Table met Server-Side Query

```javascript
frappe.ui.form.on('Work Order', {
    setup(frm) {
        // Item filter met server-side query voor complexe logica
        frm.set_query('item_code', 'required_items', () => ({
            query: 'myapp.queries.get_bom_items',
            filters: {
                bom: frm.doc.bom_no,
                warehouse: frm.doc.source_warehouse
            }
        }));
    }
});

frappe.ui.form.on('Work Order Item', {
    item_code(frm, cdt, cdn) {
        let row = frappe.get_doc(cdt, cdn);
        
        if (row.item_code) {
            // Haal default warehouse en rate op
            frappe.call({
                method: 'frappe.client.get_value',
                args: {
                    doctype: 'Item',
                    filters: { name: row.item_code },
                    fieldname: ['item_name', 'stock_uom', 'valuation_rate']
                },
                callback: (r) => {
                    if (r.message) {
                        frappe.model.set_value(cdt, cdn, {
                            item_name: r.message.item_name,
                            uom: r.message.stock_uom,
                            rate: r.message.valuation_rate
                        });
                    }
                }
            });
        }
    }
});
```

## Voorbeeld 11: Async/Await Pattern

```javascript
frappe.ui.form.on('Customer', {
    async refresh(frm) {
        if (frm.is_new()) return;
        
        try {
            // Parallelle API calls
            let [orders, invoices, payments] = await Promise.all([
                frappe.db.count('Sales Order', { customer: frm.doc.name }),
                frappe.db.count('Sales Invoice', { customer: frm.doc.name }),
                frappe.call({
                    method: 'erpnext.accounts.utils.get_balance_on',
                    args: { party_type: 'Customer', party: frm.doc.name }
                })
            ]);
            
            // Update dashboard
            frm.dashboard.add_indicator(
                __('Orders: {0}', [orders]), 'blue'
            );
            frm.dashboard.add_indicator(
                __('Invoices: {0}', [invoices]), 'green'
            );
            frm.dashboard.add_indicator(
                __('Balance: {0}', [format_currency(payments.message)]), 
                payments.message > 0 ? 'orange' : 'green'
            );
        } catch (e) {
            console.error('Dashboard load error:', e);
        }
    }
});
```

## Voorbeeld 12: Complete CRUD met Child Table

```javascript
frappe.ui.form.on('Project', {
    refresh(frm) {
        if (!frm.is_new()) {
            // Button om meerdere taken toe te voegen
            frm.add_custom_button(__('Add Standard Tasks'), () => {
                frappe.call({
                    method: 'myapp.api.get_standard_tasks',
                    args: { project_type: frm.doc.project_type },
                    callback: (r) => {
                        if (r.message && r.message.length) {
                            // Clear bestaande taken
                            frm.clear_table('tasks');
                            
                            // Voeg nieuwe taken toe
                            r.message.forEach(task => {
                                frm.add_child('tasks', {
                                    title: task.title,
                                    description: task.description,
                                    expected_time: task.expected_time,
                                    status: 'Open'
                                });
                            });
                            
                            // Refresh en save
                            frm.refresh_field('tasks');
                            frm.dirty();  // Markeer als gewijzigd
                            
                            frappe.show_alert({
                                message: __('Added {0} tasks', [r.message.length]),
                                indicator: 'green'
                            });
                        }
                    }
                });
            });
        }
    }
});
```
