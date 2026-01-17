# Complete Implementation Examples (EN)

## Example 1: Project Tracking Form

**Requirements**:
- Show "completion_date" only when status = "Completed"
- Calculate "days_elapsed" automatically
- Validate that completion_date is after start_date

```javascript
frappe.ui.form.on('Project Task', {
    setup(frm) {
        // Filter assignee to active users
        frm.set_query('assigned_to', () => ({
            filters: { enabled: 1 }
        }));
    },
    
    refresh(frm) {
        frm.trigger('status');
        
        // Calculate days since start
        if (frm.doc.start_date && !frm.is_new()) {
            let start = frappe.datetime.str_to_obj(frm.doc.start_date);
            let now = frappe.datetime.now_date();
            let days = frappe.datetime.get_day_diff(now, start);
            frm.set_value('days_elapsed', days);
        }
    },
    
    status(frm) {
        let is_completed = frm.doc.status === 'Completed';
        frm.toggle_display('completion_date', is_completed);
        frm.toggle_reqd('completion_date', is_completed);
        
        // Auto-fill completion_date
        if (is_completed && !frm.doc.completion_date) {
            frm.set_value('completion_date', frappe.datetime.now_date());
        }
    },
    
    validate(frm) {
        if (frm.doc.completion_date && frm.doc.start_date) {
            if (frm.doc.completion_date < frm.doc.start_date) {
                frappe.throw(__('Completion date cannot be before start date'));
            }
        }
    }
});
```

---

## Example 2: Invoice with Tax Calculation

**Requirements**:
- Calculate tax per line
- Calculate document totals
- Round to 2 decimals

```javascript
frappe.ui.form.on('Custom Invoice', {
    tax_rate(frm) {
        recalculate_all_rows(frm);
    },
    
    items_remove(frm) {
        calculate_totals(frm);
    }
});

frappe.ui.form.on('Custom Invoice Item', {
    qty(frm, cdt, cdn) {
        calculate_row(frm, cdt, cdn);
    },
    
    rate(frm, cdt, cdn) {
        calculate_row(frm, cdt, cdn);
    },
    
    amount(frm, cdt, cdn) {
        calculate_row_tax(frm, cdt, cdn);
    },
    
    tax_amount(frm) {
        calculate_totals(frm);
    }
});

function calculate_row(frm, cdt, cdn) {
    let row = frappe.get_doc(cdt, cdn);
    let amount = flt(row.qty) * flt(row.rate);
    frappe.model.set_value(cdt, cdn, 'amount', flt(amount, 2));
}

function calculate_row_tax(frm, cdt, cdn) {
    let row = frappe.get_doc(cdt, cdn);
    let tax_rate = flt(frm.doc.tax_rate) || 21;
    let tax_amount = flt(row.amount) * tax_rate / 100;
    frappe.model.set_value(cdt, cdn, 'tax_amount', flt(tax_amount, 2));
}

function recalculate_all_rows(frm) {
    (frm.doc.items || []).forEach(row => {
        calculate_row_tax(frm, row.doctype, row.name);
    });
}

function calculate_totals(frm) {
    let subtotal = 0;
    let total_tax = 0;
    
    (frm.doc.items || []).forEach(row => {
        subtotal += flt(row.amount);
        total_tax += flt(row.tax_amount);
    });
    
    frm.set_value({
        'subtotal': flt(subtotal, 2),
        'total_tax': flt(total_tax, 2),
        'grand_total': flt(subtotal + total_tax, 2)
    });
}
```

---

## Example 3: Wizard-style Document

**Requirements**:
- 3 steps: Basic → Details → Review
- Navigation with buttons
- Validation per step

```javascript
frappe.ui.form.on('Onboarding Form', {
    refresh(frm) {
        // Hide all sections, show only current step
        update_step_visibility(frm);
        
        // Navigation buttons
        if (frm.doc.current_step !== 'step_1') {
            frm.add_custom_button(__('Previous'), () => {
                go_to_previous_step(frm);
            });
        }
        
        if (frm.doc.current_step !== 'step_3') {
            frm.add_custom_button(__('Next'), () => {
                go_to_next_step(frm);
            }, null, 'primary');
        }
    }
});

function update_step_visibility(frm) {
    const steps = ['step_1', 'step_2', 'step_3'];
    const current = frm.doc.current_step || 'step_1';
    
    steps.forEach(step => {
        frm.toggle_display(`${step}_section`, step === current);
    });
    
    // Progress indicator
    let step_num = steps.indexOf(current) + 1;
    frm.set_intro(__('Step {0} of 3', [step_num]), 'blue');
}

async function go_to_next_step(frm) {
    // Validate current step
    let valid = await validate_current_step(frm);
    if (!valid) return;
    
    const step_order = ['step_1', 'step_2', 'step_3'];
    let current_idx = step_order.indexOf(frm.doc.current_step || 'step_1');
    
    if (current_idx < step_order.length - 1) {
        await frm.set_value('current_step', step_order[current_idx + 1]);
        frm.refresh();
    }
}

function go_to_previous_step(frm) {
    const step_order = ['step_1', 'step_2', 'step_3'];
    let current_idx = step_order.indexOf(frm.doc.current_step || 'step_1');
    
    if (current_idx > 0) {
        frm.set_value('current_step', step_order[current_idx - 1]);
        frm.refresh();
    }
}

async function validate_current_step(frm) {
    const step = frm.doc.current_step || 'step_1';
    
    if (step === 'step_1') {
        if (!frm.doc.full_name || !frm.doc.email) {
            frappe.msgprint(__('Please fill Name and Email'));
            return false;
        }
    } else if (step === 'step_2') {
        if (!frm.doc.department) {
            frappe.msgprint(__('Please select a Department'));
            return false;
        }
    }
    
    return true;
}
```

---

## Example 4: Dependent Filters with Server Query

**Requirements**:
- Country → City → Address (cascading)
- Custom server query for complex filtering

```javascript
frappe.ui.form.on('Customer Location', {
    setup(frm) {
        // City filtered by country
        frm.set_query('city', () => {
            if (!frm.doc.country) {
                frappe.msgprint(__('Please select a Country first'));
                return { filters: { name: '' } }; // No results
            }
            return {
                filters: { country: frm.doc.country }
            };
        });
        
        // Address with custom server query
        frm.set_query('address', () => ({
            query: 'myapp.queries.get_addresses_for_city',
            filters: {
                city: frm.doc.city,
                address_type: 'Office'
            }
        }));
    },
    
    country(frm) {
        // Clear dependent fields
        frm.set_value('city', '');
        frm.set_value('address', '');
    },
    
    city(frm) {
        // Clear address when city changes
        frm.set_value('address', '');
    }
});
```

**Server-side query** (`myapp/queries.py`):
```python
import frappe

@frappe.whitelist()
def get_addresses_for_city(doctype, txt, searchfield, start, page_len, filters):
    city = filters.get('city')
    address_type = filters.get('address_type')
    
    return frappe.db.sql("""
        SELECT name, address_line1, city
        FROM `tabAddress`
        WHERE city = %(city)s
        AND address_type = %(address_type)s
        AND (name LIKE %(txt)s OR address_line1 LIKE %(txt)s)
        LIMIT %(start)s, %(page_len)s
    """, {
        'city': city,
        'address_type': address_type,
        'txt': f'%{txt}%',
        'start': start,
        'page_len': page_len
    })
```

---

## Example 5: Real-time Dashboard in Form

**Requirements**:
- Show KPIs at top of form
- Update on refresh
- Clickable links to related docs

```javascript
frappe.ui.form.on('Customer', {
    async refresh(frm) {
        if (frm.is_new()) return;
        
        // Fetch statistics
        let stats = await frappe.call({
            method: 'myapp.api.get_customer_stats',
            args: { customer: frm.doc.name }
        });
        
        if (stats.message) {
            render_dashboard(frm, stats.message);
        }
    }
});

function render_dashboard(frm, stats) {
    // Remove existing dashboard
    frm.dashboard.clear_headline();
    
    // Add indicators
    frm.dashboard.add_indicator(
        __('Orders: {0}', [stats.total_orders]),
        stats.total_orders > 0 ? 'blue' : 'gray'
    );
    
    frm.dashboard.add_indicator(
        __('Revenue: {0}', [format_currency(stats.total_revenue)]),
        'green'
    );
    
    frm.dashboard.add_indicator(
        __('Outstanding: {0}', [format_currency(stats.outstanding)]),
        stats.outstanding > 0 ? 'orange' : 'green'
    );
    
    // Add links
    frm.dashboard.set_headline_alert(`
        <a class="btn btn-xs btn-default" 
           onclick="frappe.set_route('List', 'Sales Order', {'customer': '${frm.doc.name}'})">
            ${__('View Orders')}
        </a>
        <a class="btn btn-xs btn-default" 
           onclick="frappe.set_route('List', 'Sales Invoice', {'customer': '${frm.doc.name}'})">
            ${__('View Invoices')}
        </a>
    `);
}
```

---

## Example 6: File Upload with Preview

**Requirements**:
- Upload image to custom field
- Show preview immediately
- Validate file type

```javascript
frappe.ui.form.on('Product', {
    refresh(frm) {
        // Preview existing image
        if (frm.doc.product_image) {
            show_image_preview(frm);
        }
        
        // Custom upload button
        if (!frm.is_new()) {
            frm.add_custom_button(__('Upload Image'), () => {
                new frappe.ui.FileUploader({
                    doctype: frm.doc.doctype,
                    docname: frm.doc.name,
                    folder: 'Home/Products',
                    restrictions: {
                        allowed_file_types: ['image/*'],
                        max_file_size: 2 * 1024 * 1024 // 2MB
                    },
                    on_success: (file_doc) => {
                        frm.set_value('product_image', file_doc.file_url);
                        frm.save();
                    }
                });
            });
        }
    },
    
    product_image(frm) {
        show_image_preview(frm);
    }
});

function show_image_preview(frm) {
    if (frm.doc.product_image) {
        // Add preview to form
        let preview_html = `
            <div class="product-preview" style="margin: 10px 0;">
                <img src="${frm.doc.product_image}" 
                     style="max-width: 200px; max-height: 200px; border: 1px solid #d1d8dd;">
            </div>
        `;
        
        // Remove existing preview
        frm.$wrapper.find('.product-preview').remove();
        
        // Add after image field
        frm.get_field('product_image').$wrapper.append(preview_html);
    }
}
```

---

## Example 7: Keyboard Shortcuts

**Requirements**:
- Ctrl+S = Save
- Ctrl+D = Duplicate
- Esc = Cancel

```javascript
frappe.ui.form.on('Quick Entry', {
    onload(frm) {
        // Register shortcuts
        frappe.ui.keys.add_shortcut({
            shortcut: 'ctrl+d',
            action: () => duplicate_document(frm),
            description: __('Duplicate Document'),
            page: frm.page
        });
        
        frappe.ui.keys.add_shortcut({
            shortcut: 'escape',
            action: () => {
                if (frm.is_dirty()) {
                    frappe.confirm(
                        __('Discard changes?'),
                        () => frm.reload_doc()
                    );
                }
            },
            description: __('Cancel Changes'),
            page: frm.page
        });
    }
});

async function duplicate_document(frm) {
    if (frm.is_new()) {
        frappe.msgprint(__('Save document first'));
        return;
    }
    
    let new_doc = frappe.model.copy_doc(frm.doc);
    new_doc.name = '';
    new_doc.docstatus = 0;
    
    frappe.set_route('Form', frm.doc.doctype, new_doc.name);
}
```

---

## Example 8: Bulk Actions on Child Table

**Requirements**:
- Select multiple rows
- Apply action to selection
- Update all selected rows

```javascript
frappe.ui.form.on('Purchase Order', {
    refresh(frm) {
        if (!frm.is_new()) {
            frm.add_custom_button(__('Mark Selected as Received'), () => {
                mark_items_received(frm);
            });
        }
    }
});

function mark_items_received(frm) {
    let selected = frm.get_selected();
    
    if (!selected.items || selected.items.length === 0) {
        frappe.msgprint(__('Please select items first'));
        return;
    }
    
    frappe.confirm(
        __('Mark {0} items as received?', [selected.items.length]),
        () => {
            selected.items.forEach(cdn => {
                frappe.model.set_value('Purchase Order Item', cdn, {
                    'received_qty': frappe.get_doc('Purchase Order Item', cdn).qty,
                    'received_date': frappe.datetime.now_date()
                });
            });
            
            frm.refresh_field('items');
            frappe.show_alert({
                message: __('Updated {0} items', [selected.items.length]),
                indicator: 'green'
            });
        }
    );
}
```

---

## Example 9: Print/Export with Custom Format

**Requirements**:
- Custom print button
- Export to Excel

```javascript
frappe.ui.form.on('Report Document', {
    refresh(frm) {
        if (!frm.is_new() && frm.doc.docstatus === 1) {
            frm.add_custom_button(__('Print Report'), () => {
                // Open print preview with specific format
                frm.print_doc('Custom Report Format');
            }, __('Actions'));
            
            frm.add_custom_button(__('Export to Excel'), () => {
                export_to_excel(frm);
            }, __('Actions'));
        }
    }
});

function export_to_excel(frm) {
    // Build data for export
    let data = [];
    
    // Header
    data.push(['Item', 'Quantity', 'Rate', 'Amount']);
    
    // Rows
    (frm.doc.items || []).forEach(row => {
        data.push([row.item_code, row.qty, row.rate, row.amount]);
    });
    
    // Total
    data.push(['', '', 'Total:', frm.doc.grand_total]);
    
    // Download
    frappe.tools.downloadify(data, null, frm.doc.name);
}
```

---

## Example 10: Form with Dynamic Tab Visibility

**Requirements**:
- Hide tabs based on user role
- Lazy load tab content

```javascript
frappe.ui.form.on('Employee Record', {
    refresh(frm) {
        // Hide sensitive tabs for non-HR
        if (!frappe.user_roles.includes('HR Manager')) {
            frm.toggle_display('salary_tab', false);
            frm.toggle_display('documents_tab', false);
        }
        
        // Lazy load performance data
        if (frappe.user_roles.includes('HR Manager')) {
            frm.trigger('load_performance_data');
        }
    },
    
    async load_performance_data(frm) {
        // Only load if tab not yet loaded
        if (frm._performance_loaded) return;
        
        let r = await frappe.call({
            method: 'hr_app.api.get_performance_data',
            args: { employee: frm.doc.name }
        });
        
        if (r.message) {
            frm.set_value('performance_score', r.message.score);
            frm.set_value('last_review_date', r.message.last_review);
            frm._performance_loaded = true;
        }
    }
});
```
