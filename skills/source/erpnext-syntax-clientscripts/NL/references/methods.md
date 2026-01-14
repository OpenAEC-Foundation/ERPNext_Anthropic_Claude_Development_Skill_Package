# Client Script Methods (NL)

## frm.* Methods

### Waarde Manipulatie

#### frm.set_value(fieldname, value)
Zet de waarde van een veld. Async, retourneert Promise.

```javascript
// Signature
frm.set_value(fieldname: string, value: any): Promise

// Enkele waarde
frm.set_value('status', 'Approved');

// Meerdere waarden
frm.set_value({
    status: 'Approved',
    priority: 'High',
    due_date: frappe.datetime.add_days(frappe.datetime.now_date(), 7)
});

// Met Promise handling
frm.set_value('status', 'Approved').then(() => {
    console.log('Value set successfully');
});
```

#### frm.doc.fieldname
Direct toegang tot veldwaarde (read-only patroon).

```javascript
let customer = frm.doc.customer;
let items = frm.doc.items;  // Array voor child tables
```

### Veld Display Properties

#### frm.toggle_display(fieldname, show)
Toont of verbergt een veld.

```javascript
// Signature
frm.toggle_display(fieldname: string | string[], show: boolean): void

// Enkel veld
frm.toggle_display('priority', frm.doc.status === 'Open');

// Meerdere velden
frm.toggle_display(['priority', 'due_date'], frm.doc.status === 'Open');
```

#### frm.toggle_reqd(fieldname, required)
Maakt veld verplicht of optioneel.

```javascript
// Signature
frm.toggle_reqd(fieldname: string | string[], required: boolean): void

frm.toggle_reqd('due_date', true);
frm.toggle_reqd(['email', 'phone'], frm.doc.customer_type === 'Company');
```

#### frm.toggle_enable(fieldname, enable)
Maakt veld bewerkbaar of read-only.

```javascript
// Signature
frm.toggle_enable(fieldname: string | string[], enable: boolean): void

frm.toggle_enable('amount', false);  // Read-only
frm.toggle_enable('amount', true);   // Editable
```

#### frm.set_df_property(fieldname, property, value)
Zet willekeurige veld property.

```javascript
// Signature
frm.set_df_property(fieldname: string, property: string, value: any): void

// Beschikbare properties
frm.set_df_property('status', 'options', ['New', 'Open', 'Closed']);
frm.set_df_property('amount', 'read_only', 1);
frm.set_df_property('description', 'hidden', 1);
frm.set_df_property('priority', 'reqd', 1);
frm.set_df_property('rate', 'precision', 4);
frm.set_df_property('notes', 'label', 'Internal Notes');
```

### Link Field Queries

#### frm.set_query(fieldname, [tablename], query_function)
Filtert opties in Link velden.

```javascript
// Signature (form level)
frm.set_query(fieldname: string, query_function: Function): void

// Signature (child table)
frm.set_query(fieldname: string, tablename: string, query_function: Function): void

// Simpele filter
frm.set_query('customer', () => ({
    filters: { disabled: 0, customer_type: 'Company' }
}));

// Met document context
frm.set_query('customer', () => ({
    filters: { territory: frm.doc.territory }
}));

// In child table
frm.set_query('item_code', 'items', (doc, cdt, cdn) => {
    let row = locals[cdt][cdn];
    return {
        filters: { 
            is_sales_item: 1,
            item_group: row.item_group || undefined
        }
    };
});

// Server-side query
frm.set_query('customer', () => ({
    query: 'myapp.queries.get_customers_by_region',
    filters: { region: frm.doc.region }
}));
```

### Child Table Methods

#### frm.add_child(tablename, values)
Voegt rij toe aan child table.

```javascript
// Signature
frm.add_child(tablename: string, values?: object): object

let row = frm.add_child('items', {
    item_code: 'ITEM-001',
    qty: 5,
    rate: 100
});
frm.refresh_field('items');  // VERPLICHT
```

#### frm.clear_table(tablename)
Verwijdert alle rijen uit child table.

```javascript
// Signature
frm.clear_table(tablename: string): void

frm.clear_table('items');
frm.refresh_field('items');  // VERPLICHT
```

#### frm.refresh_field(fieldname)
Hertekent veld in UI. **Verplicht na child table wijzigingen.**

```javascript
// Signature
frm.refresh_field(fieldname: string): void

frm.refresh_field('items');
frm.refresh_field('grand_total');
```

### Custom Buttons

#### frm.add_custom_button(label, action, [group])
Voegt custom button toe.

```javascript
// Signature
frm.add_custom_button(label: string, action: Function, group?: string): jQuery

// Standalone button
frm.add_custom_button(__('Generate Report'), () => {
    frappe.call({
        method: 'myapp.api.generate_report',
        args: { name: frm.doc.name }
    });
});

// Gegroepeerde button (dropdown)
frm.add_custom_button(__('Sales Invoice'), () => {
    // Create invoice
}, __('Create'));

frm.add_custom_button(__('Delivery Note'), () => {
    // Create delivery note
}, __('Create'));
```

#### frm.remove_custom_button(label, [group])
Verwijdert custom button.

```javascript
// Signature
frm.remove_custom_button(label: string, group?: string): void

frm.remove_custom_button(__('Generate Report'));
frm.remove_custom_button(__('Sales Invoice'), __('Create'));
```

#### frm.page.set_primary_action(label, action)
Zet primaire actie button.

```javascript
// Signature
frm.page.set_primary_action(label: string, action: Function): void

frm.page.set_primary_action(__('Submit'), () => {
    frm.call('custom_submit').then(() => frm.reload_doc());
});
```

### Utility Methods

#### frm.is_new()
Check of document nieuw is (nog niet opgeslagen).

```javascript
// Signature
frm.is_new(): boolean

if (frm.is_new()) {
    frm.set_value('status', 'Draft');
}
```

#### frm.reload_doc()
Herlaadt document van server.

```javascript
// Signature
frm.reload_doc(): Promise

await frm.reload_doc();
```

#### frm.call(method, args)
Roept method op document controller aan.

```javascript
// Signature
frm.call(method: string, args?: object): Promise

frm.call('calculate_taxes', { include_shipping: true })
    .then(r => {
        console.log(r.message);
    });
```

#### frm.save()
Slaat document op.

```javascript
// Signature
frm.save(callback?: Function): Promise

frm.save().then(() => {
    frappe.show_alert('Saved!');
});
```

#### frm.enable_save() / frm.disable_save()
Schakelt save button in/uit.

```javascript
frm.disable_save();  // Voorkomt opslaan
frm.enable_save();   // Sta opslaan toe
```

---

## frappe.* Client Methods

### Server Communication

#### frappe.call(options)
Roept whitelisted Python method aan.

```javascript
// Signature
frappe.call({
    method: string,           // Volledige method path
    args?: object,            // Arguments
    callback?: Function,      // Success callback
    error?: Function,         // Error callback
    async?: boolean,          // Default: true
    freeze?: boolean,         // Toon loading indicator
    freeze_message?: string,  // Custom loading message
    btn?: jQuery              // Button om te disablen
}): Promise

// Voorbeeld
frappe.call({
    method: 'myapp.api.get_customer_data',
    args: {
        customer: frm.doc.customer,
        include_orders: true
    },
    freeze: true,
    freeze_message: __('Loading customer data...'),
    callback: (r) => {
        if (r.message) {
            console.log(r.message);
        }
    },
    error: (r) => {
        frappe.msgprint(__('Error loading data'));
    }
});
```

#### frappe.db.get_value(doctype, name, fieldname)
Haalt veld waarde op van server.

```javascript
// Signature
frappe.db.get_value(
    doctype: string,
    name: string | object,  // Name of filters
    fieldname: string | string[]
): Promise

// Enkel veld
frappe.db.get_value('Customer', frm.doc.customer, 'credit_limit')
    .then(r => {
        console.log(r.message.credit_limit);
    });

// Meerdere velden
frappe.db.get_value('Customer', frm.doc.customer, ['credit_limit', 'territory'])
    .then(r => {
        console.log(r.message.credit_limit);
        console.log(r.message.territory);
    });

// Met filters
frappe.db.get_value('Customer', {customer_name: 'Test'}, 'name')
    .then(r => {
        console.log(r.message.name);
    });
```

#### frappe.db.get_list(doctype, args)
Haalt lijst van documents op.

```javascript
// Signature
frappe.db.get_list(doctype: string, args: object): Promise

frappe.db.get_list('Sales Order', {
    filters: { customer: frm.doc.customer },
    fields: ['name', 'grand_total', 'status'],
    order_by: 'creation desc',
    limit: 10
}).then(orders => {
    console.log(orders);
});
```

### User Interface

#### frappe.msgprint(message, [title])
Toont bericht dialoog.

```javascript
// Signature
frappe.msgprint(message: string | object, title?: string): void

frappe.msgprint(__('Operation completed'));
frappe.msgprint({
    title: __('Success'),
    message: __('Invoice created'),
    indicator: 'green'
});
```

#### frappe.throw(message)
Toont error en stopt executie.

```javascript
// Signature
frappe.throw(message: string): never

if (frm.doc.amount < 0) {
    frappe.throw(__('Amount cannot be negative'));
}
```

#### frappe.show_alert(message, [seconds])
Toont tijdelijke notificatie.

```javascript
// Signature
frappe.show_alert(message: string | object, seconds?: number): void

frappe.show_alert(__('Saved!'), 3);
frappe.show_alert({
    message: __('Order processed'),
    indicator: 'green'
}, 5);
```

#### frappe.confirm(message, if_yes, if_no)
Toont bevestigingsdialoog.

```javascript
// Signature
frappe.confirm(message: string, if_yes: Function, if_no?: Function): void

frappe.confirm(
    __('Are you sure you want to delete?'),
    () => {
        // User clicked Yes
        frm.call('delete_items');
    },
    () => {
        // User clicked No
    }
);
```

### Child Table Utilities

#### frappe.get_doc(cdt, cdn)
Haalt child row data op.

```javascript
// Signature
frappe.get_doc(cdt: string, cdn: string): object

frappe.ui.form.on('Sales Invoice Item', {
    qty(frm, cdt, cdn) {
        let row = frappe.get_doc(cdt, cdn);
        console.log(row.qty, row.rate);
    }
});
```

#### frappe.model.set_value(cdt, cdn, fieldname, value)
Zet waarde in child row.

```javascript
// Signature
frappe.model.set_value(cdt: string, cdn: string, fieldname: string, value: any): Promise

frappe.ui.form.on('Sales Invoice Item', {
    qty(frm, cdt, cdn) {
        let row = frappe.get_doc(cdt, cdn);
        frappe.model.set_value(cdt, cdn, 'amount', row.qty * row.rate);
    }
});
```

### Translation

#### __(message)
Vertaalt string.

```javascript
// Signature
__(message: string, replace?: object | string[], context?: string): string

frappe.msgprint(__('Hello World'));
frappe.msgprint(__('Hello {0}', [user_name]));
frappe.msgprint(__('Total: {0}', [frm.doc.grand_total]));
```

### Date/Time Utilities

```javascript
// Huidige datum (YYYY-MM-DD)
frappe.datetime.now_date()

// Huidige datetime
frappe.datetime.now_datetime()

// Dagen toevoegen
frappe.datetime.add_days('2024-01-01', 7)  // '2024-01-08'

// Maanden toevoegen
frappe.datetime.add_months('2024-01-01', 1)  // '2024-02-01'

// Datum formatteren
frappe.datetime.str_to_user('2024-01-15')  // Naar user format

// Vergelijken
frappe.datetime.get_diff(date1, date2)  // Verschil in dagen
```
