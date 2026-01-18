# Examples - API Error Handling

Complete working examples of API error handling in Frappe/ERPNext.

---

## Example 1: Complete API Module

```python
# myapp/api.py
"""
Complete API module with comprehensive error handling.
"""
import frappe
from frappe import _

# =============================================================================
# ORDER MANAGEMENT API
# =============================================================================

@frappe.whitelist()
def create_sales_order(customer, items, delivery_date=None):
    """
    Create a new Sales Order.
    
    Args:
        customer: Customer name
        items: List of items [{item_code, qty, rate}]
        delivery_date: Optional delivery date
        
    Returns:
        dict: {status: success, order_name: SO-xxxxx}
    """
    # Validate customer
    if not customer:
        frappe.throw(_("Customer is required"), exc=frappe.ValidationError)
    
    if not frappe.db.exists("Customer", customer):
        frappe.throw(
            _("Customer '{0}' not found").format(customer),
            exc=frappe.DoesNotExistError
        )
    
    # Validate items
    if not items:
        frappe.throw(_("At least one item is required"), exc=frappe.ValidationError)
    
    if isinstance(items, str):
        items = frappe.parse_json(items)
    
    # Validate each item
    for i, item in enumerate(items):
        if not item.get("item_code"):
            frappe.throw(
                _("Item {0}: item_code is required").format(i + 1),
                exc=frappe.ValidationError
            )
        
        if not frappe.db.exists("Item", item["item_code"]):
            frappe.throw(
                _("Item '{0}' not found").format(item["item_code"]),
                exc=frappe.DoesNotExistError
            )
        
        qty = item.get("qty", 0)
        if not qty or qty <= 0:
            frappe.throw(
                _("Item {0}: quantity must be greater than zero").format(i + 1),
                exc=frappe.ValidationError
            )
    
    # Check permission
    if not frappe.has_permission("Sales Order", "create"):
        frappe.throw(
            _("You don't have permission to create Sales Orders"),
            exc=frappe.PermissionError
        )
    
    # Create order
    try:
        order = frappe.get_doc({
            "doctype": "Sales Order",
            "customer": customer,
            "delivery_date": delivery_date or frappe.utils.add_days(frappe.utils.today(), 7),
            "items": [
                {
                    "item_code": item["item_code"],
                    "qty": item["qty"],
                    "rate": item.get("rate", 0)
                }
                for item in items
            ]
        })
        
        order.insert()
        
        return {
            "status": "success",
            "order_name": order.name,
            "grand_total": order.grand_total
        }
        
    except frappe.DuplicateEntryError:
        frappe.throw(
            _("A duplicate order was detected"),
            exc=frappe.DuplicateEntryError
        )
    except Exception as e:
        frappe.log_error(
            f"Order creation failed for customer {customer}\n\n{frappe.get_traceback()}",
            "Sales Order API Error"
        )
        frappe.throw(_("Failed to create order. Please try again."))


@frappe.whitelist()
def get_order_status(order_name):
    """
    Get Sales Order status and details.
    """
    if not order_name:
        frappe.throw(_("Order name is required"), exc=frappe.ValidationError)
    
    if not frappe.db.exists("Sales Order", order_name):
        frappe.throw(
            _("Sales Order '{0}' not found").format(order_name),
            exc=frappe.DoesNotExistError
        )
    
    if not frappe.has_permission("Sales Order", "read", order_name):
        frappe.throw(
            _("You don't have permission to view this order"),
            exc=frappe.PermissionError
        )
    
    order = frappe.get_doc("Sales Order", order_name)
    
    return {
        "name": order.name,
        "customer": order.customer,
        "status": order.status,
        "docstatus": order.docstatus,
        "grand_total": order.grand_total,
        "delivery_status": order.delivery_status,
        "billing_status": order.billing_status,
        "items_count": len(order.items)
    }


@frappe.whitelist()
def cancel_order(order_name, reason=None):
    """
    Cancel a Sales Order.
    """
    if not order_name:
        frappe.throw(_("Order name is required"), exc=frappe.ValidationError)
    
    if not frappe.db.exists("Sales Order", order_name):
        frappe.throw(
            _("Sales Order '{0}' not found").format(order_name),
            exc=frappe.DoesNotExistError
        )
    
    order = frappe.get_doc("Sales Order", order_name)
    
    # Check cancel permission
    if not order.has_permission("cancel"):
        frappe.throw(
            _("You don't have permission to cancel this order"),
            exc=frappe.PermissionError
        )
    
    # Business validation
    if order.docstatus != 1:
        frappe.throw(
            _("Only submitted orders can be cancelled"),
            exc=frappe.ValidationError
        )
    
    if order.per_delivered > 0:
        frappe.throw(
            _("Cannot cancel order with deliveries. Cancel deliveries first."),
            exc=frappe.ValidationError
        )
    
    try:
        order.flags.ignore_permissions = True
        order.cancel()
        
        # Log cancellation reason
        if reason:
            frappe.get_doc({
                "doctype": "Comment",
                "comment_type": "Info",
                "reference_doctype": "Sales Order",
                "reference_name": order_name,
                "content": f"Cancelled: {reason}"
            }).insert(ignore_permissions=True)
        
        return {
            "status": "success",
            "message": _("Order cancelled successfully")
        }
        
    except Exception as e:
        frappe.log_error(frappe.get_traceback(), f"Cancel Order Error: {order_name}")
        frappe.throw(_("Failed to cancel order: {0}").format(str(e)))


# =============================================================================
# BULK OPERATIONS
# =============================================================================

@frappe.whitelist()
def bulk_update_orders(order_names, updates):
    """
    Bulk update multiple orders.
    
    Args:
        order_names: List of order names
        updates: Dict of fields to update
        
    Returns:
        dict: {success: [...], failed: [...], permission_denied: [...]}
    """
    if not order_names:
        frappe.throw(_("No orders specified"), exc=frappe.ValidationError)
    
    if isinstance(order_names, str):
        order_names = frappe.parse_json(order_names)
    
    if isinstance(updates, str):
        updates = frappe.parse_json(updates)
    
    if not updates:
        frappe.throw(_("No updates specified"), exc=frappe.ValidationError)
    
    # Validate update fields
    allowed_fields = ["delivery_date", "po_no", "customer_address"]
    invalid_fields = [f for f in updates.keys() if f not in allowed_fields]
    if invalid_fields:
        frappe.throw(
            _("Cannot update fields: {0}").format(", ".join(invalid_fields)),
            exc=frappe.ValidationError
        )
    
    results = {
        "success": [],
        "failed": [],
        "permission_denied": [],
        "not_found": []
    }
    
    for order_name in order_names:
        # Check existence
        if not frappe.db.exists("Sales Order", order_name):
            results["not_found"].append(order_name)
            continue
        
        # Check permission
        if not frappe.has_permission("Sales Order", "write", order_name):
            results["permission_denied"].append(order_name)
            continue
        
        try:
            # Update each field
            for field, value in updates.items():
                frappe.db.set_value("Sales Order", order_name, field, value)
            
            results["success"].append(order_name)
            
        except Exception as e:
            results["failed"].append({
                "name": order_name,
                "error": str(e)
            })
    
    frappe.db.commit()
    
    return results
```

---

## Example 2: Client-Side Implementation

```javascript
// myapp/public/js/order_api.js

/**
 * Order API Client
 * 
 * Provides clean interface for order management API with
 * comprehensive error handling.
 */
const OrderAPI = {
    
    /**
     * Create a new sales order
     */
    async create(customer, items, deliveryDate = null) {
        return this._call("myapp.api.create_sales_order", {
            customer: customer,
            items: items,
            delivery_date: deliveryDate
        }, __("Creating order..."));
    },
    
    /**
     * Get order status
     */
    async getStatus(orderName) {
        return this._call("myapp.api.get_order_status", {
            order_name: orderName
        }, __("Loading order..."));
    },
    
    /**
     * Cancel an order
     */
    async cancel(orderName, reason = null) {
        return this._call("myapp.api.cancel_order", {
            order_name: orderName,
            reason: reason
        }, __("Cancelling order..."));
    },
    
    /**
     * Bulk update orders
     */
    async bulkUpdate(orderNames, updates) {
        return this._call("myapp.api.bulk_update_orders", {
            order_names: orderNames,
            updates: updates
        }, __("Updating orders..."));
    },
    
    /**
     * Internal call method with error handling
     */
    _call(method, args, freezeMessage) {
        return new Promise((resolve, reject) => {
            frappe.call({
                method: method,
                args: args,
                freeze: true,
                freeze_message: freezeMessage,
                callback: (r) => {
                    if (r.message) {
                        resolve(r.message);
                    } else {
                        resolve(null);
                    }
                },
                error: (r) => {
                    this._handleError(r);
                    reject(r);
                }
            });
        });
    },
    
    /**
     * Handle API errors
     */
    _handleError(error) {
        let title = __("Error");
        let message = __("An error occurred");
        let indicator = "red";
        
        // Extract error details
        if (error._server_messages) {
            try {
                const messages = JSON.parse(error._server_messages);
                if (messages.length > 0) {
                    const msg = JSON.parse(messages[0]);
                    message = msg.message || msg;
                }
            } catch (e) {}
        }
        
        // Set title based on error type
        switch (error.exc_type) {
            case "ValidationError":
                title = __("Validation Error");
                break;
            case "PermissionError":
                title = __("Permission Denied");
                message = message || __("You don't have permission for this action");
                break;
            case "DoesNotExistError":
                title = __("Not Found");
                break;
            case "DuplicateEntryError":
                title = __("Duplicate Entry");
                indicator = "orange";
                break;
        }
        
        // Network error
        if (!error.status) {
            title = __("Network Error");
            message = __("Unable to connect to server");
            indicator = "orange";
        }
        
        frappe.msgprint({
            title: title,
            message: message,
            indicator: indicator
        });
    }
};

// =============================================================================
// FORM INTEGRATION
// =============================================================================

frappe.ui.form.on("Sales Order", {
    refresh: function(frm) {
        if (frm.doc.docstatus === 1) {
            frm.add_custom_button(__("Cancel with Reason"), async function() {
                const reason = await new Promise((resolve) => {
                    frappe.prompt({
                        fieldname: "reason",
                        fieldtype: "Small Text",
                        label: __("Cancellation Reason"),
                        reqd: 1
                    }, (values) => resolve(values.reason));
                });
                
                try {
                    const result = await OrderAPI.cancel(frm.doc.name, reason);
                    frappe.show_alert({
                        message: result.message,
                        indicator: "green"
                    });
                    frm.reload_doc();
                } catch (e) {
                    // Error already handled by OrderAPI
                }
            }, __("Actions"));
        }
    }
});

// =============================================================================
// BULK OPERATIONS PAGE
// =============================================================================

frappe.pages["bulk-order-update"].on_page_load = function(wrapper) {
    const page = frappe.ui.make_app_page({
        parent: wrapper,
        title: __("Bulk Order Update"),
        single_column: true
    });
    
    page.main.html(`
        <div class="bulk-update-form">
            <p>${__("Select orders and fields to update")}</p>
            <div id="order-list"></div>
            <button class="btn btn-primary btn-update">
                ${__("Update Selected")}
            </button>
        </div>
    `);
    
    page.main.find(".btn-update").on("click", async function() {
        const selectedOrders = getSelectedOrders();
        const updates = getUpdateValues();
        
        if (selectedOrders.length === 0) {
            frappe.msgprint(__("Please select at least one order"));
            return;
        }
        
        try {
            const result = await OrderAPI.bulkUpdate(selectedOrders, updates);
            
            // Show summary
            let summary = [];
            if (result.success.length > 0) {
                summary.push(__("{0} orders updated", [result.success.length]));
            }
            if (result.permission_denied.length > 0) {
                summary.push(__("{0} orders: permission denied", [result.permission_denied.length]));
            }
            if (result.not_found.length > 0) {
                summary.push(__("{0} orders: not found", [result.not_found.length]));
            }
            if (result.failed.length > 0) {
                summary.push(__("{0} orders: failed", [result.failed.length]));
            }
            
            frappe.msgprint({
                title: __("Update Complete"),
                message: summary.join("<br>"),
                indicator: result.failed.length > 0 ? "orange" : "green"
            });
            
        } catch (e) {
            // Error already handled
        }
    });
};
```

---

## Example 3: External Integration

```python
# myapp/integrations/shipping_api.py
"""
Shipping provider integration with comprehensive error handling.
"""
import frappe
from frappe import _
import requests
import time

class ShippingAPIError(Exception):
    """Custom exception for shipping API errors."""
    pass


class ShippingAPI:
    """
    Shipping provider API client.
    """
    
    def __init__(self):
        self.settings = frappe.get_single("Shipping Settings")
        self.base_url = self.settings.api_url.rstrip("/")
        self.api_key = self.settings.get_password("api_key")
        self.max_retries = 3
        self.timeout = 30
    
    def create_shipment(self, delivery_note_name):
        """
        Create shipment for delivery note.
        
        Returns:
            dict: {tracking_number, label_url, estimated_delivery}
        """
        # Get delivery note
        if not frappe.db.exists("Delivery Note", delivery_note_name):
            frappe.throw(
                _("Delivery Note not found"),
                exc=frappe.DoesNotExistError
            )
        
        dn = frappe.get_doc("Delivery Note", delivery_note_name)
        
        # Validate address
        if not dn.shipping_address_name:
            frappe.throw(
                _("Shipping address is required"),
                exc=frappe.ValidationError
            )
        
        # Build request
        payload = self._build_shipment_payload(dn)
        
        # Make API call
        try:
            response = self._post("/shipments", payload)
            
            # Update delivery note
            frappe.db.set_value(
                "Delivery Note",
                delivery_note_name,
                {
                    "tracking_number": response["tracking_number"],
                    "shipping_label_url": response.get("label_url"),
                    "estimated_delivery": response.get("estimated_delivery")
                }
            )
            frappe.db.commit()
            
            return response
            
        except ShippingAPIError as e:
            frappe.log_error(
                f"Shipment creation failed for {delivery_note_name}: {str(e)}",
                "Shipping API Error"
            )
            frappe.throw(str(e))
    
    def track_shipment(self, tracking_number):
        """
        Get shipment tracking info.
        """
        if not tracking_number:
            frappe.throw(
                _("Tracking number is required"),
                exc=frappe.ValidationError
            )
        
        try:
            return self._get(f"/tracking/{tracking_number}")
        except ShippingAPIError as e:
            if "not found" in str(e).lower():
                frappe.throw(
                    _("Tracking number not found"),
                    exc=frappe.DoesNotExistError
                )
            raise
    
    def cancel_shipment(self, tracking_number):
        """
        Cancel a shipment.
        """
        try:
            return self._delete(f"/shipments/{tracking_number}")
        except ShippingAPIError as e:
            if "already picked up" in str(e).lower():
                frappe.throw(
                    _("Cannot cancel - shipment already picked up"),
                    exc=frappe.ValidationError
                )
            raise
    
    def _build_shipment_payload(self, dn):
        """Build API payload from delivery note."""
        address = frappe.get_doc("Address", dn.shipping_address_name)
        
        return {
            "reference": dn.name,
            "recipient": {
                "name": dn.customer_name,
                "address_line1": address.address_line1,
                "address_line2": address.address_line2,
                "city": address.city,
                "state": address.state,
                "postal_code": address.pincode,
                "country": address.country,
                "phone": address.phone
            },
            "packages": [
                {
                    "weight": item.total_weight or 1,
                    "description": item.item_name
                }
                for item in dn.items
            ]
        }
    
    def _get(self, endpoint, params=None):
        return self._request("GET", endpoint, params=params)
    
    def _post(self, endpoint, data):
        return self._request("POST", endpoint, json=data)
    
    def _delete(self, endpoint):
        return self._request("DELETE", endpoint)
    
    def _request(self, method, endpoint, **kwargs):
        """
        Make API request with retry logic.
        """
        url = f"{self.base_url}{endpoint}"
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        last_error = None
        
        for attempt in range(self.max_retries):
            try:
                response = requests.request(
                    method=method,
                    url=url,
                    headers=headers,
                    timeout=self.timeout,
                    **kwargs
                )
                
                # Success
                if response.status_code in [200, 201]:
                    return response.json()
                
                # Parse error
                error_msg = self._parse_error(response)
                
                # Auth error
                if response.status_code == 401:
                    raise ShippingAPIError(_("Authentication failed. Check API key."))
                
                # Client error - don't retry
                if 400 <= response.status_code < 500:
                    raise ShippingAPIError(error_msg)
                
                # Rate limit
                if response.status_code == 429:
                    wait = int(response.headers.get("Retry-After", 60))
                    time.sleep(min(wait, 120))
                    continue
                
                # Server error - retry
                last_error = error_msg
                time.sleep(2 ** attempt)
                continue
                
            except requests.exceptions.Timeout:
                last_error = "Request timed out"
                time.sleep(2 ** attempt)
                
            except requests.exceptions.ConnectionError:
                last_error = "Connection failed"
                time.sleep(2 ** attempt)
                
            except ShippingAPIError:
                raise
                
            except Exception as e:
                last_error = str(e)
                frappe.log_error(frappe.get_traceback(), "Shipping API Error")
        
        raise ShippingAPIError(
            _("Shipping service unavailable: {0}").format(last_error)
        )
    
    def _parse_error(self, response):
        """Extract error message from response."""
        try:
            data = response.json()
            return data.get("error", {}).get("message") or data.get("message") or str(data)
        except Exception:
            return response.text[:200]


# =============================================================================
# WHITELISTED METHODS
# =============================================================================

@frappe.whitelist()
def create_shipment(delivery_note):
    """Create shipment API endpoint."""
    api = ShippingAPI()
    return api.create_shipment(delivery_note)


@frappe.whitelist()
def track_shipment(tracking_number):
    """Track shipment API endpoint."""
    api = ShippingAPI()
    return api.track_shipment(tracking_number)


@frappe.whitelist()
def cancel_shipment(tracking_number):
    """Cancel shipment API endpoint."""
    api = ShippingAPI()
    return api.cancel_shipment(tracking_number)
```

---

## Quick Reference

### Server-Side Error Throwing

```python
# Validation error (HTTP 417)
frappe.throw(_("Invalid input"), exc=frappe.ValidationError)

# Not found (HTTP 404)
frappe.throw(_("Not found"), exc=frappe.DoesNotExistError)

# Permission denied (HTTP 403)
frappe.throw(_("Access denied"), exc=frappe.PermissionError)

# Duplicate (HTTP 409)
frappe.throw(_("Duplicate"), exc=frappe.DuplicateEntryError)
```

### Client-Side Error Handling

```javascript
frappe.call({
    method: "...",
    callback: (r) => { /* success */ },
    error: (r) => {
        if (r.exc_type === "ValidationError") { }
        else if (r.exc_type === "PermissionError") { }
        else if (r.exc_type === "DoesNotExistError") { }
        else if (!r.status) { /* network error */ }
    }
});
```
