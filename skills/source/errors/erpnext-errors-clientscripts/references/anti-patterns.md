# Anti-Patterns - Client Script Error Handling

Common mistakes to avoid when handling errors in Frappe/ERPNext Client Scripts.

---

## 1. Using frappe.throw() Outside validate Event

### ❌ WRONG

```javascript
frappe.ui.form.on('Sales Order', {
    customer(frm) {
        if (!frm.doc.customer) {
            // This stops execution but doesn't prevent user from saving!
            frappe.throw(__('Customer is required'));
        }
    }
});
```

### ✅ CORRECT

```javascript
frappe.ui.form.on('Sales Order', {
    customer(frm) {
        if (!frm.doc.customer) {
            // Use msgprint for non-blocking error
            frappe.msgprint({
                title: __('Warning'),
                message: __('Customer is required'),
                indicator: 'orange'
            });
        }
    },
    
    validate(frm) {
        // Use throw ONLY in validate to prevent save
        if (!frm.doc.customer) {
            frappe.throw(__('Customer is required'));
        }
    }
});
```

**Why**: `frappe.throw()` only prevents save when used in `validate` event. Elsewhere, it just stops script execution but the user can still save the form.

---

## 2. Not Handling Async Errors

### ❌ WRONG

```javascript
frappe.ui.form.on('Sales Order', {
    customer(frm) {
        // No error handling - silent failure!
        frappe.call({
            method: 'myapp.api.get_customer',
            args: { customer: frm.doc.customer }
        }).then(r => {
            frm.set_value('credit_limit', r.message.credit_limit);
        });
    }
});
```

### ✅ CORRECT

```javascript
frappe.ui.form.on('Sales Order', {
    async customer(frm) {
        try {
            const r = await frappe.call({
                method: 'myapp.api.get_customer',
                args: { customer: frm.doc.customer }
            });
            
            if (r.message) {
                frm.set_value('credit_limit', r.message.credit_limit);
            }
        } catch (error) {
            console.error('Failed to fetch customer:', error);
            frappe.show_alert({
                message: __('Could not load customer details'),
                indicator: 'orange'
            }, 5);
        }
    }
});
```

**Why**: Unhandled Promise rejections fail silently, leaving users confused when features don't work.

---

## 3. Throwing on First Error

### ❌ WRONG

```javascript
frappe.ui.form.on('Sales Order', {
    validate(frm) {
        if (!frm.doc.customer) {
            frappe.throw(__('Customer is required'));
        }
        // User has to save multiple times to find all errors
        if (!frm.doc.delivery_date) {
            frappe.throw(__('Delivery Date is required'));
        }
        if (!frm.doc.items.length) {
            frappe.throw(__('Items are required'));
        }
    }
});
```

### ✅ CORRECT

```javascript
frappe.ui.form.on('Sales Order', {
    validate(frm) {
        const errors = [];
        
        if (!frm.doc.customer) {
            errors.push(__('Customer is required'));
        }
        if (!frm.doc.delivery_date) {
            errors.push(__('Delivery Date is required'));
        }
        if (!frm.doc.items?.length) {
            errors.push(__('At least one item is required'));
        }
        
        // Show all errors at once
        if (errors.length) {
            frappe.throw({
                title: __('Please fix the following'),
                message: errors.join('<br>')
            });
        }
    }
});
```

**Why**: Users shouldn't have to save multiple times to discover all validation errors.

---

## 4. Exposing Technical Errors to Users

### ❌ WRONG

```javascript
frappe.ui.form.on('Sales Order', {
    async customer(frm) {
        try {
            await frappe.call({ method: 'myapp.api.get_data' });
        } catch (error) {
            // Exposing technical details to user!
            frappe.throw(error.stack);
            // Or: frappe.throw(JSON.stringify(error));
        }
    }
});
```

### ✅ CORRECT

```javascript
frappe.ui.form.on('Sales Order', {
    async customer(frm) {
        try {
            await frappe.call({ method: 'myapp.api.get_data' });
        } catch (error) {
            // Log technical details for developers
            console.error('API Error:', error);
            
            // Show user-friendly message
            frappe.msgprint({
                title: __('Error'),
                message: __('Could not load data. Please try again or contact support.'),
                indicator: 'red'
            });
        }
    }
});
```

**Why**: Technical error messages confuse users and may expose sensitive information.

---

## 5. Using Native JavaScript Dialogs

### ❌ WRONG

```javascript
frappe.ui.form.on('Sales Order', {
    validate(frm) {
        if (frm.doc.grand_total > 100000) {
            // Native dialogs block the thread and look unprofessional
            if (!confirm('Large order. Are you sure?')) {
                return false;  // Doesn't work as expected anyway
            }
        }
    },
    
    customer(frm) {
        alert('Customer selected!');  // Never use alert()
    }
});
```

### ✅ CORRECT

```javascript
frappe.ui.form.on('Sales Order', {
    refresh(frm) {
        // Add confirmation button instead of validate check
        if (frm.doc.grand_total > 100000 && frm.doc.docstatus === 0) {
            frm.dashboard.set_headline(
                __('Large order - please verify before submitting'),
                'orange'
            );
        }
    },
    
    customer(frm) {
        frappe.show_alert({
            message: __('Customer selected'),
            indicator: 'green'
        }, 2);
    }
});
```

**Why**: `alert()` and `confirm()` block JavaScript execution, look outdated, and can't be styled to match the application.

---

## 6. Not Handling Null/Undefined Values

### ❌ WRONG

```javascript
frappe.ui.form.on('Sales Order', {
    customer(frm) {
        // Crashes if customer not set or API returns nothing
        frappe.call({
            method: 'frappe.client.get_value',
            args: { doctype: 'Customer', name: frm.doc.customer, fieldname: 'credit_limit' },
            callback(r) {
                frm.set_value('credit_limit', r.message.credit_limit);  // r.message could be null!
            }
        });
    }
});
```

### ✅ CORRECT

```javascript
frappe.ui.form.on('Sales Order', {
    customer(frm) {
        if (!frm.doc.customer) {
            frm.set_value('credit_limit', 0);
            return;
        }
        
        frappe.call({
            method: 'frappe.client.get_value',
            args: { doctype: 'Customer', name: frm.doc.customer, fieldname: 'credit_limit' },
            callback(r) {
                frm.set_value('credit_limit', r.message?.credit_limit || 0);
            },
            error() {
                frm.set_value('credit_limit', 0);
            }
        });
    }
});
```

**Why**: Always assume data might be missing. Use optional chaining (`?.`) and defaults.

---

## 7. Ignoring the error Callback

### ❌ WRONG

```javascript
frappe.call({
    method: 'myapp.api.process',
    args: { doc: frm.doc.name },
    callback(r) {
        frappe.show_alert({ message: 'Done!', indicator: 'green' });
    }
    // No error callback - user has no idea if it failed
});
```

### ✅ CORRECT

```javascript
frappe.call({
    method: 'myapp.api.process',
    args: { doc: frm.doc.name },
    callback(r) {
        if (r.message) {
            frappe.show_alert({ message: __('Done!'), indicator: 'green' });
        }
    },
    error(r) {
        console.error('Process failed:', r);
        frappe.msgprint({
            title: __('Error'),
            message: __('Processing failed. Please try again.'),
            indicator: 'red'
        });
    }
});
```

**Why**: Without error handling, failures are silent and users don't know to retry.

---

## 8. Swallowing Errors Silently

### ❌ WRONG

```javascript
frappe.ui.form.on('Sales Order', {
    async validate(frm) {
        try {
            await frappe.call({ method: 'myapp.api.validate' });
        } catch (error) {
            // Error swallowed - save proceeds despite failure!
        }
    }
});
```

### ✅ CORRECT

```javascript
frappe.ui.form.on('Sales Order', {
    async validate(frm) {
        try {
            await frappe.call({ method: 'myapp.api.validate' });
        } catch (error) {
            console.error('Validation failed:', error);
            frappe.throw(__('Validation failed. Please try again.'));
        }
    }
});
```

**Why**: If validation is important enough to exist, failures should block the save.

---

## 9. Not Using Translation Wrapper

### ❌ WRONG

```javascript
frappe.throw('Customer is required');
frappe.msgprint('Order saved successfully');
frappe.show_alert({ message: 'Processing...', indicator: 'blue' });
```

### ✅ CORRECT

```javascript
frappe.throw(__('Customer is required'));
frappe.msgprint(__('Order saved successfully'));
frappe.show_alert({ message: __('Processing...'), indicator: 'blue' });
```

**Why**: Without `__()`, messages won't be translated for non-English users.

---

## 10. Using console.log in Production

### ❌ WRONG

```javascript
frappe.ui.form.on('Sales Order', {
    validate(frm) {
        console.log('Validating order');
        console.log('Customer:', frm.doc.customer);
        console.log('Items:', frm.doc.items);
        // ... validation logic
    }
});
```

### ✅ CORRECT

```javascript
const DEBUG = frappe.boot.developer_mode;

function debug(...args) {
    if (DEBUG) console.log('[SalesOrder]', ...args);
}

frappe.ui.form.on('Sales Order', {
    validate(frm) {
        debug('Validating order');
        debug('Customer:', frm.doc.customer);
        // ... validation logic
    }
});
```

**Why**: Console output clutters browser logs in production and may expose sensitive data.

---

## 11. Not Disabling Controls During Async Operations

### ❌ WRONG

```javascript
frm.add_custom_button(__('Process'), async () => {
    // User can click multiple times!
    await frappe.call({ method: 'myapp.api.process' });
    frm.reload_doc();
});
```

### ✅ CORRECT

```javascript
frm.add_custom_button(__('Process'), async () => {
    const btn = frm.page.btn_primary;  // Or find button by selector
    
    try {
        btn.prop('disabled', true);
        frm.disable_save();
        
        await frappe.call({
            method: 'myapp.api.process',
            freeze: true,
            freeze_message: __('Processing...')
        });
        
        frm.reload_doc();
    } catch (error) {
        frappe.msgprint(__('Processing failed'));
    } finally {
        btn.prop('disabled', false);
        frm.enable_save();
    }
});
```

**Why**: Users might click buttons multiple times, causing duplicate operations.

---

## 12. Mixing Async Patterns

### ❌ WRONG

```javascript
frappe.ui.form.on('Sales Order', {
    // Mixing .then() and await causes confusion
    async customer(frm) {
        frappe.call({
            method: 'myapp.api.get_data'
        }).then(r => {
            frm.set_value('field', r.message);
        });
        
        // This runs before the call completes!
        await doSomethingElse();
    }
});
```

### ✅ CORRECT

```javascript
frappe.ui.form.on('Sales Order', {
    async customer(frm) {
        // Consistent async/await pattern
        try {
            const r = await frappe.call({
                method: 'myapp.api.get_data'
            });
            
            frm.set_value('field', r.message);
            await doSomethingElse();
        } catch (error) {
            console.error(error);
        }
    }
});
```

**Why**: Mixing `.then()` and `await` leads to unpredictable execution order and hard-to-debug issues.

---

## 13. Hardcoding Error Messages

### ❌ WRONG

```javascript
if (amount > 100000) {
    frappe.throw('Amount exceeds 100000');
}
```

### ✅ CORRECT

```javascript
const MAX_AMOUNT = 100000;

if (amount > MAX_AMOUNT) {
    frappe.throw(__('Amount cannot exceed {0}', [format_currency(MAX_AMOUNT)]));
}
```

**Why**: Magic numbers are hard to maintain. Dynamic messages are clearer.

---

## Quick Checklist: Error Handling Review

Before deploying client scripts, verify:

- [ ] All `frappe.throw()` calls are only in `validate` event
- [ ] All async operations have try/catch
- [ ] All validation errors are collected and shown together
- [ ] Technical errors are logged to console, not shown to users
- [ ] All user-facing strings use `__()`
- [ ] null/undefined cases are handled
- [ ] Server call errors are handled
- [ ] Controls are disabled during async operations
- [ ] No console.log statements in production code
- [ ] No native `alert()`, `confirm()`, or `prompt()` calls
