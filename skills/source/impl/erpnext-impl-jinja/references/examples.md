# Jinja Templates - Complete Examples

> Production-ready examples for common template scenarios.

---

## Example 1: Professional Sales Invoice Print Format

A complete, professional invoice suitable for business use.

```jinja
<style>
    /* Base styles */
    .invoice { font-family: 'Segoe UI', Arial, sans-serif; font-size: 11px; color: #333; }
    
    /* Header */
    .invoice-header { display: table; width: 100%; margin-bottom: 30px; }
    .company-section { display: table-cell; width: 60%; vertical-align: top; }
    .company-logo { max-height: 60px; max-width: 180px; margin-bottom: 10px; }
    .company-name { font-size: 18px; font-weight: bold; color: #2c3e50; }
    .company-details { color: #666; line-height: 1.6; }
    .invoice-title-section { display: table-cell; width: 40%; text-align: right; vertical-align: top; }
    .invoice-title { font-size: 28px; font-weight: bold; color: #2c3e50; margin-bottom: 10px; }
    .invoice-number { font-size: 14px; color: #666; }
    
    /* Parties */
    .parties { display: table; width: 100%; margin-bottom: 30px; }
    .bill-to, .ship-to { display: table-cell; width: 50%; vertical-align: top; }
    .party-label { font-weight: bold; color: #2c3e50; margin-bottom: 5px; text-transform: uppercase; font-size: 10px; }
    .party-name { font-weight: bold; font-size: 13px; }
    .party-address { color: #666; line-height: 1.5; }
    
    /* Meta info */
    .meta-table { width: 100%; margin-bottom: 20px; }
    .meta-table td { padding: 5px 10px; }
    .meta-table .label { background: #f5f5f5; font-weight: bold; width: 150px; }
    
    /* Items table */
    .items-table { width: 100%; border-collapse: collapse; margin-bottom: 30px; }
    .items-table th { background: #2c3e50; color: white; padding: 10px; text-align: left; font-weight: normal; }
    .items-table th.text-right { text-align: right; }
    .items-table td { padding: 10px; border-bottom: 1px solid #eee; }
    .items-table tr:nth-child(even) { background: #fafafa; }
    .item-code { color: #999; font-size: 10px; }
    
    /* Totals */
    .totals-section { display: table; width: 100%; }
    .totals-notes { display: table-cell; width: 50%; vertical-align: top; }
    .totals-table-wrapper { display: table-cell; width: 50%; }
    .totals-table { width: 100%; }
    .totals-table td { padding: 8px; }
    .totals-table .label { text-align: right; }
    .totals-table .value { text-align: right; width: 150px; }
    .totals-table .grand-total { font-size: 16px; font-weight: bold; background: #2c3e50; color: white; }
    
    /* Footer */
    .invoice-footer { margin-top: 40px; padding-top: 20px; border-top: 1px solid #ddd; }
    .terms { font-size: 10px; color: #666; }
    
    /* Print adjustments */
    @media print {
        .invoice { padding: 0; }
    }
</style>

{# Get company data #}
{% set company = frappe.get_doc("Company", doc.company) %}

<div class="invoice">
    <!-- Header -->
    <div class="invoice-header">
        <div class="company-section">
            {% if company.company_logo %}
            <img src="{{ company.company_logo }}" class="company-logo" alt="">
            {% endif %}
            <div class="company-name">{{ company.company_name }}</div>
            <div class="company-details">
                {% if company.company_description %}{{ company.company_description }}<br>{% endif %}
                {% if company.phone_no %}{{ _("Tel") }}: {{ company.phone_no }}<br>{% endif %}
                {% if company.email %}{{ company.email }}<br>{% endif %}
                {% if company.website %}{{ company.website }}{% endif %}
            </div>
        </div>
        <div class="invoice-title-section">
            <div class="invoice-title">{{ doc.select_print_heading or _("INVOICE") }}</div>
            <div class="invoice-number">{{ doc.name }}</div>
        </div>
    </div>
    
    <!-- Bill To / Ship To -->
    <div class="parties">
        <div class="bill-to">
            <div class="party-label">{{ _("Bill To") }}</div>
            <div class="party-name">{{ doc.customer_name }}</div>
            <div class="party-address">
                {{ doc.address_display | safe if doc.address_display else '' }}
            </div>
        </div>
        {% if doc.shipping_address_name %}
        <div class="ship-to">
            <div class="party-label">{{ _("Ship To") }}</div>
            <div class="party-address">
                {{ doc.shipping_address | safe if doc.shipping_address else '' }}
            </div>
        </div>
        {% endif %}
    </div>
    
    <!-- Invoice Meta -->
    <table class="meta-table">
        <tr>
            <td class="label">{{ _("Invoice Date") }}</td>
            <td>{{ doc.get_formatted("posting_date") }}</td>
            <td class="label">{{ _("Due Date") }}</td>
            <td>{{ doc.get_formatted("due_date") }}</td>
        </tr>
        {% if doc.po_no %}
        <tr>
            <td class="label">{{ _("Customer PO") }}</td>
            <td>{{ doc.po_no }}</td>
            <td class="label">{{ _("PO Date") }}</td>
            <td>{{ doc.get_formatted("po_date") if doc.po_date else '' }}</td>
        </tr>
        {% endif %}
        {% if doc.contact_display %}
        <tr>
            <td class="label">{{ _("Contact") }}</td>
            <td colspan="3">{{ doc.contact_display }}</td>
        </tr>
        {% endif %}
    </table>
    
    <!-- Items -->
    <table class="items-table">
        <thead>
            <tr>
                <th style="width: 5%">#</th>
                <th style="width: 35%">{{ _("Item") }}</th>
                <th style="width: 20%">{{ _("Description") }}</th>
                <th class="text-right" style="width: 10%">{{ _("Qty") }}</th>
                <th class="text-right" style="width: 15%">{{ _("Rate") }}</th>
                <th class="text-right" style="width: 15%">{{ _("Amount") }}</th>
            </tr>
        </thead>
        <tbody>
            {% for item in doc.items %}
            <tr>
                <td>{{ item.idx }}</td>
                <td>
                    {{ item.item_name }}
                    {% if item.item_code != item.item_name %}
                    <div class="item-code">{{ item.item_code }}</div>
                    {% endif %}
                </td>
                <td>{{ (item.description | truncate(80)) if item.description else '' }}</td>
                <td class="text-right">{{ item.qty }} {{ item.uom }}</td>
                <td class="text-right">{{ item.get_formatted("rate", doc) }}</td>
                <td class="text-right">{{ item.get_formatted("amount", doc) }}</td>
            </tr>
            {% endfor %}
        </tbody>
    </table>
    
    <!-- Totals -->
    <div class="totals-section">
        <div class="totals-notes">
            {% if doc.remarks %}
            <p><strong>{{ _("Remarks") }}:</strong><br>{{ doc.remarks }}</p>
            {% endif %}
        </div>
        <div class="totals-table-wrapper">
            <table class="totals-table">
                <tr>
                    <td class="label">{{ _("Subtotal") }}</td>
                    <td class="value">{{ doc.get_formatted("net_total") }}</td>
                </tr>
                {% if doc.discount_amount %}
                <tr>
                    <td class="label">{{ _("Discount") }}</td>
                    <td class="value">-{{ doc.get_formatted("discount_amount") }}</td>
                </tr>
                {% endif %}
                {% for tax in doc.taxes %}
                <tr>
                    <td class="label">{{ tax.description }}</td>
                    <td class="value">{{ tax.get_formatted("tax_amount", doc) }}</td>
                </tr>
                {% endfor %}
                <tr class="grand-total">
                    <td class="label">{{ _("Grand Total") }}</td>
                    <td class="value">{{ doc.get_formatted("grand_total") }}</td>
                </tr>
                {% if doc.outstanding_amount and doc.outstanding_amount != doc.grand_total %}
                <tr>
                    <td class="label">{{ _("Paid Amount") }}</td>
                    <td class="value">{{ doc.get_formatted("paid_amount") if doc.paid_amount else doc.get_formatted("grand_total") }}</td>
                </tr>
                <tr>
                    <td class="label"><strong>{{ _("Balance Due") }}</strong></td>
                    <td class="value"><strong>{{ doc.get_formatted("outstanding_amount") }}</strong></td>
                </tr>
                {% endif %}
            </table>
        </div>
    </div>
    
    <!-- Footer -->
    <div class="invoice-footer">
        {% if doc.terms %}
        <div class="terms">
            <strong>{{ _("Terms and Conditions") }}</strong><br>
            {{ doc.terms | safe }}
        </div>
        {% endif %}
    </div>
</div>
```

---

## Example 2: Packing Slip Print Format

```jinja
<style>
    .packing-slip { font-family: Arial, sans-serif; font-size: 12px; }
    .header { border-bottom: 2px solid #333; padding-bottom: 10px; margin-bottom: 20px; }
    .title { font-size: 24px; font-weight: bold; }
    .addresses { display: table; width: 100%; margin: 20px 0; }
    .address-box { display: table-cell; width: 50%; padding: 10px; border: 1px solid #ddd; }
    .address-label { font-weight: bold; margin-bottom: 5px; }
    .items-table { width: 100%; border-collapse: collapse; margin: 20px 0; }
    .items-table th { background: #333; color: white; padding: 10px; text-align: left; }
    .items-table td { padding: 10px; border-bottom: 1px solid #ddd; }
    .checkbox { width: 20px; height: 20px; border: 2px solid #333; display: inline-block; }
    .signature-section { margin-top: 50px; }
    .signature-line { width: 200px; border-bottom: 1px solid #333; margin-top: 40px; }
</style>

<div class="packing-slip">
    <div class="header">
        <div class="title">{{ _("PACKING SLIP") }}</div>
        <p>{{ doc.name }} | {{ doc.get_formatted("posting_date") }}</p>
    </div>
    
    <div class="addresses">
        <div class="address-box">
            <div class="address-label">{{ _("Ship From") }}:</div>
            {% set company = frappe.get_doc("Company", doc.company) %}
            <strong>{{ company.company_name }}</strong><br>
            {{ company.address or '' }}
        </div>
        <div class="address-box">
            <div class="address-label">{{ _("Ship To") }}:</div>
            <strong>{{ doc.customer_name }}</strong><br>
            {{ doc.shipping_address | safe if doc.shipping_address else doc.address_display | safe }}
        </div>
    </div>
    
    <table class="items-table">
        <thead>
            <tr>
                <th style="width: 5%"><span class="checkbox"></span></th>
                <th style="width: 15%">{{ _("Item Code") }}</th>
                <th style="width: 40%">{{ _("Description") }}</th>
                <th style="width: 15%">{{ _("Qty Ordered") }}</th>
                <th style="width: 15%">{{ _("Qty Packed") }}</th>
                <th style="width: 10%">{{ _("UOM") }}</th>
            </tr>
        </thead>
        <tbody>
            {% for item in doc.items %}
            <tr>
                <td><span class="checkbox"></span></td>
                <td>{{ item.item_code }}</td>
                <td>{{ item.item_name }}</td>
                <td>{{ item.qty }}</td>
                <td>________</td>
                <td>{{ item.uom }}</td>
            </tr>
            {% endfor %}
        </tbody>
    </table>
    
    <p><strong>{{ _("Total Items") }}:</strong> {{ doc.items | length }}</p>
    <p><strong>{{ _("Total Qty") }}:</strong> {{ doc.total_qty }}</p>
    
    {% if doc.remarks %}
    <p><strong>{{ _("Notes") }}:</strong> {{ doc.remarks }}</p>
    {% endif %}
    
    <div class="signature-section">
        <table style="width: 100%;">
            <tr>
                <td style="width: 50%;">
                    <div class="signature-line"></div>
                    <p>{{ _("Packed By") }}</p>
                </td>
                <td style="width: 50%;">
                    <div class="signature-line"></div>
                    <p>{{ _("Checked By") }}</p>
                </td>
            </tr>
        </table>
    </div>
</div>
```

---

## Example 3: Email Template - Order Confirmation

```jinja
<div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto; background: #f9f9f9; padding: 20px;">
    <div style="background: white; padding: 30px; border-radius: 5px;">
        <!-- Header -->
        <div style="text-align: center; margin-bottom: 30px;">
            {% set company = frappe.get_doc("Company", doc.company) %}
            {% if company.company_logo %}
            <img src="{{ company.company_logo }}" style="max-height: 50px;" alt="">
            {% endif %}
            <h1 style="color: #2c3e50; margin: 20px 0 10px;">{{ _("Order Confirmation") }}</h1>
            <p style="color: #666;">{{ _("Thank you for your order!") }}</p>
        </div>
        
        <!-- Greeting -->
        <p>{{ _("Dear") }} {{ doc.customer_name }},</p>
        <p>{{ _("We have received your order and it is being processed. Here are your order details:") }}</p>
        
        <!-- Order Info -->
        <div style="background: #f5f5f5; padding: 15px; border-radius: 5px; margin: 20px 0;">
            <table style="width: 100%;">
                <tr>
                    <td style="padding: 5px 0;"><strong>{{ _("Order Number") }}:</strong></td>
                    <td style="text-align: right;">{{ doc.name }}</td>
                </tr>
                <tr>
                    <td style="padding: 5px 0;"><strong>{{ _("Order Date") }}:</strong></td>
                    <td style="text-align: right;">{{ frappe.format_date(doc.transaction_date) }}</td>
                </tr>
                <tr>
                    <td style="padding: 5px 0;"><strong>{{ _("Delivery Date") }}:</strong></td>
                    <td style="text-align: right;">{{ frappe.format_date(doc.delivery_date) if doc.delivery_date else _("To be confirmed") }}</td>
                </tr>
            </table>
        </div>
        
        <!-- Items -->
        <h3 style="color: #2c3e50; border-bottom: 2px solid #eee; padding-bottom: 10px;">{{ _("Order Items") }}</h3>
        <table style="width: 100%; border-collapse: collapse;">
            {% for item in doc.items %}
            <tr style="border-bottom: 1px solid #eee;">
                <td style="padding: 10px 0;">
                    <strong>{{ item.item_name }}</strong>
                    {% if item.item_code != item.item_name %}
                    <br><small style="color: #999;">{{ item.item_code }}</small>
                    {% endif %}
                </td>
                <td style="padding: 10px 0; text-align: center;">× {{ item.qty }}</td>
                <td style="padding: 10px 0; text-align: right;">{{ item.get_formatted("amount", doc) }}</td>
            </tr>
            {% endfor %}
        </table>
        
        <!-- Totals -->
        <table style="width: 100%; margin-top: 20px;">
            <tr>
                <td style="padding: 5px 0;">{{ _("Subtotal") }}</td>
                <td style="text-align: right;">{{ doc.get_formatted("net_total") }}</td>
            </tr>
            {% if doc.total_taxes_and_charges %}
            <tr>
                <td style="padding: 5px 0;">{{ _("Tax") }}</td>
                <td style="text-align: right;">{{ doc.get_formatted("total_taxes_and_charges") }}</td>
            </tr>
            {% endif %}
            <tr style="font-size: 18px; font-weight: bold;">
                <td style="padding: 10px 0; border-top: 2px solid #333;">{{ _("Total") }}</td>
                <td style="padding: 10px 0; border-top: 2px solid #333; text-align: right;">{{ doc.get_formatted("grand_total") }}</td>
            </tr>
        </table>
        
        <!-- Shipping Address -->
        {% if doc.shipping_address_name %}
        <h3 style="color: #2c3e50; margin-top: 30px;">{{ _("Shipping Address") }}</h3>
        <p style="background: #f5f5f5; padding: 15px; border-radius: 5px;">
            {{ doc.shipping_address | safe }}
        </p>
        {% endif %}
        
        <!-- Footer -->
        <div style="margin-top: 30px; padding-top: 20px; border-top: 1px solid #eee; text-align: center; color: #666;">
            <p>{{ _("If you have any questions, please contact us.") }}</p>
            {% if company.phone_no %}
            <p>{{ _("Phone") }}: {{ company.phone_no }}</p>
            {% endif %}
            {% if company.email %}
            <p>{{ _("Email") }}: {{ company.email }}</p>
            {% endif %}
        </div>
    </div>
</div>
```

---

## Example 4: Portal Page - Customer Dashboard

### www/customer-dashboard/index.py

```python
import frappe

def get_context(context):
    # Require login
    if frappe.session.user == "Guest":
        frappe.local.flags.redirect_location = "/login"
        raise frappe.Redirect
    
    context.title = "My Dashboard"
    context.no_cache = True
    
    # Get customer for this user
    customer = get_customer()
    if not customer:
        context.error = "No customer account linked to your profile"
        return context
    
    context.customer_name = frappe.db.get_value("Customer", customer, "customer_name")
    
    # Summary stats
    context.stats = {
        "total_orders": frappe.db.count("Sales Order", {"customer": customer, "docstatus": 1}),
        "pending_orders": frappe.db.count("Sales Order", {"customer": customer, "docstatus": 1, "status": ["not in", ["Completed", "Closed"]]}),
        "total_invoices": frappe.db.count("Sales Invoice", {"customer": customer, "docstatus": 1}),
        "outstanding_amount": get_outstanding_amount(customer)
    }
    
    # Recent orders
    context.recent_orders = frappe.get_all(
        "Sales Order",
        filters={"customer": customer, "docstatus": 1},
        fields=["name", "transaction_date", "grand_total", "status"],
        order_by="transaction_date desc",
        limit_page_length=5
    )
    
    # Pending invoices
    context.pending_invoices = frappe.get_all(
        "Sales Invoice",
        filters={"customer": customer, "docstatus": 1, "outstanding_amount": [">", 0]},
        fields=["name", "posting_date", "grand_total", "outstanding_amount", "due_date"],
        order_by="due_date asc",
        limit_page_length=10
    )
    
    return context

def get_customer():
    """Get customer linked to current user"""
    contact = frappe.db.get_value(
        "Contact",
        {"user": frappe.session.user},
        "name"
    )
    if contact:
        link = frappe.db.get_value(
            "Dynamic Link",
            {"parent": contact, "link_doctype": "Customer"},
            "link_name"
        )
        return link
    return None

def get_outstanding_amount(customer):
    """Get total outstanding amount"""
    result = frappe.db.sql("""
        SELECT COALESCE(SUM(outstanding_amount), 0)
        FROM `tabSales Invoice`
        WHERE customer = %s AND docstatus = 1
    """, customer)
    return result[0][0] if result else 0
```

### www/customer-dashboard/index.html

```jinja
{% extends "templates/web.html" %}

{% block title %}{{ _("My Dashboard") }}{% endblock %}

{% block page_content %}
<div class="container py-4">
    {% if error %}
        <div class="alert alert-warning">{{ error }}</div>
    {% else %}
    
    <!-- Header -->
    <div class="d-flex justify-content-between align-items-center mb-4">
        <div>
            <h1>{{ _("Welcome") }}, {{ customer_name }}</h1>
            <p class="text-muted">{{ frappe.get_fullname() }}</p>
        </div>
        <a href="/orders" class="btn btn-primary">{{ _("View All Orders") }}</a>
    </div>
    
    <!-- Stats Cards -->
    <div class="row mb-4">
        <div class="col-md-3">
            <div class="card text-center">
                <div class="card-body">
                    <h2 class="text-primary">{{ stats.total_orders }}</h2>
                    <p class="text-muted mb-0">{{ _("Total Orders") }}</p>
                </div>
            </div>
        </div>
        <div class="col-md-3">
            <div class="card text-center">
                <div class="card-body">
                    <h2 class="text-warning">{{ stats.pending_orders }}</h2>
                    <p class="text-muted mb-0">{{ _("Pending Orders") }}</p>
                </div>
            </div>
        </div>
        <div class="col-md-3">
            <div class="card text-center">
                <div class="card-body">
                    <h2 class="text-info">{{ stats.total_invoices }}</h2>
                    <p class="text-muted mb-0">{{ _("Total Invoices") }}</p>
                </div>
            </div>
        </div>
        <div class="col-md-3">
            <div class="card text-center">
                <div class="card-body">
                    <h2 class="text-danger">{{ frappe.format(stats.outstanding_amount, {'fieldtype': 'Currency'}) }}</h2>
                    <p class="text-muted mb-0">{{ _("Outstanding") }}</p>
                </div>
            </div>
        </div>
    </div>
    
    <div class="row">
        <!-- Recent Orders -->
        <div class="col-md-6">
            <div class="card">
                <div class="card-header">
                    <h5 class="mb-0">{{ _("Recent Orders") }}</h5>
                </div>
                <div class="card-body">
                    {% if recent_orders %}
                    <table class="table table-sm">
                        <thead>
                            <tr>
                                <th>{{ _("Order") }}</th>
                                <th>{{ _("Date") }}</th>
                                <th>{{ _("Status") }}</th>
                                <th class="text-right">{{ _("Total") }}</th>
                            </tr>
                        </thead>
                        <tbody>
                            {% for order in recent_orders %}
                            <tr>
                                <td><a href="/orders/{{ order.name }}">{{ order.name }}</a></td>
                                <td>{{ frappe.format_date(order.transaction_date) }}</td>
                                <td>
                                    <span class="badge badge-{% if order.status == 'Completed' %}success{% elif order.status == 'To Deliver and Bill' %}primary{% else %}secondary{% endif %}">
                                        {{ order.status }}
                                    </span>
                                </td>
                                <td class="text-right">{{ frappe.format(order.grand_total, {'fieldtype': 'Currency'}) }}</td>
                            </tr>
                            {% endfor %}
                        </tbody>
                    </table>
                    {% else %}
                    <p class="text-muted">{{ _("No orders yet") }}</p>
                    {% endif %}
                </div>
            </div>
        </div>
        
        <!-- Pending Invoices -->
        <div class="col-md-6">
            <div class="card">
                <div class="card-header">
                    <h5 class="mb-0">{{ _("Pending Invoices") }}</h5>
                </div>
                <div class="card-body">
                    {% if pending_invoices %}
                    <table class="table table-sm">
                        <thead>
                            <tr>
                                <th>{{ _("Invoice") }}</th>
                                <th>{{ _("Due") }}</th>
                                <th class="text-right">{{ _("Outstanding") }}</th>
                            </tr>
                        </thead>
                        <tbody>
                            {% for inv in pending_invoices %}
                            <tr>
                                <td><a href="/invoices/{{ inv.name }}">{{ inv.name }}</a></td>
                                <td>
                                    {% set days_overdue = frappe.utils.date_diff(frappe.utils.nowdate(), inv.due_date) %}
                                    {% if days_overdue > 0 %}
                                    <span class="text-danger">{{ days_overdue }} {{ _("days overdue") }}</span>
                                    {% else %}
                                    {{ frappe.format_date(inv.due_date) }}
                                    {% endif %}
                                </td>
                                <td class="text-right">{{ frappe.format(inv.outstanding_amount, {'fieldtype': 'Currency'}) }}</td>
                            </tr>
                            {% endfor %}
                        </tbody>
                    </table>
                    {% else %}
                    <p class="text-success">{{ _("No pending invoices!") }}</p>
                    {% endif %}
                </div>
            </div>
        </div>
    </div>
    
    {% endif %}
</div>
{% endblock %}
```

---

## Example 5: Custom Jinja Methods Library

### myapp/jinja_utils/__init__.py

```python
# Empty - just makes it a package
```

### myapp/jinja_utils/methods.py

```python
"""
Custom Jinja methods available in all templates.
Register in hooks.py: jenv = {"methods": ["myapp.jinja_utils.methods"]}
"""
import frappe
from frappe.utils import flt, cint

def get_company_logo(company_name):
    """
    Get company logo URL.
    
    Usage: {{ get_company_logo(doc.company) }}
    Returns: URL string or empty string
    """
    if not company_name:
        return ""
    return frappe.db.get_value("Company", company_name, "company_logo") or ""

def get_company_info(company_name, field=None):
    """
    Get company information.
    
    Usage: 
        {{ get_company_info(doc.company) }}  # Returns full doc
        {{ get_company_info(doc.company, "phone_no") }}  # Returns specific field
    """
    if not company_name:
        return "" if field else {}
    
    if field:
        return frappe.db.get_value("Company", company_name, field) or ""
    
    return frappe.get_doc("Company", company_name).as_dict()

def format_address(address_name, format="html"):
    """
    Format address for display.
    
    Usage:
        {{ format_address(doc.customer_address) | safe }}
        {{ format_address(doc.customer_address, "text") }}
    """
    if not address_name:
        return ""
    
    try:
        address = frappe.get_doc("Address", address_name)
    except frappe.DoesNotExistError:
        return ""
    
    parts = []
    if address.address_line1:
        parts.append(address.address_line1)
    if address.address_line2:
        parts.append(address.address_line2)
    
    city_line = []
    if address.city:
        city_line.append(address.city)
    if address.state:
        city_line.append(address.state)
    if address.pincode:
        city_line.append(address.pincode)
    if city_line:
        parts.append(", ".join(city_line))
    
    if address.country:
        parts.append(address.country)
    
    separator = "<br>" if format == "html" else "\n"
    return separator.join(parts)

def get_item_image(item_code, size="medium"):
    """
    Get item image URL.
    
    Usage: {{ get_item_image(item.item_code) }}
    """
    if not item_code:
        return ""
    
    image = frappe.db.get_value("Item", item_code, "image")
    return image if image else ""

def get_customer_balance(customer):
    """
    Get customer outstanding balance.
    
    Usage: {{ get_customer_balance(doc.customer) }}
    """
    if not customer:
        return 0
    
    result = frappe.db.sql("""
        SELECT COALESCE(SUM(debit - credit), 0)
        FROM `tabGL Entry`
        WHERE party_type = 'Customer'
        AND party = %s
        AND is_cancelled = 0
    """, customer)
    
    return flt(result[0][0]) if result else 0

def get_stock_qty(item_code, warehouse=None):
    """
    Get stock quantity for item.
    
    Usage: 
        {{ get_stock_qty(item.item_code) }}  # All warehouses
        {{ get_stock_qty(item.item_code, "Main Warehouse") }}
    """
    if not item_code:
        return 0
    
    filters = {"item_code": item_code}
    if warehouse:
        filters["warehouse"] = warehouse
    
    result = frappe.db.sql("""
        SELECT COALESCE(SUM(actual_qty), 0)
        FROM `tabBin`
        WHERE item_code = %s
        {warehouse_filter}
    """.format(
        warehouse_filter="AND warehouse = %s" if warehouse else ""
    ), (item_code, warehouse) if warehouse else (item_code,))
    
    return flt(result[0][0]) if result else 0

def number_to_words(number, currency=""):
    """
    Convert number to words (simplified).
    
    Usage: {{ number_to_words(doc.grand_total, doc.currency) }}
    """
    # Simplified implementation - use a proper library in production
    from frappe.utils import money_in_words
    return money_in_words(number, currency)
```

### myapp/jinja_utils/filters.py

```python
"""
Custom Jinja filters available in all templates.
Register in hooks.py: jenv = {"filters": ["myapp.jinja_utils.filters"]}
"""
import re

def phone_format(value, country="US"):
    """
    Format phone number.
    
    Usage: {{ doc.phone | phone_format }}
    """
    if not value:
        return ""
    
    # Remove non-digits
    digits = re.sub(r'\D', '', str(value))
    
    # Format based on length
    if len(digits) == 10:
        return f"({digits[:3]}) {digits[3:6]}-{digits[6:]}"
    elif len(digits) == 11 and digits[0] == '1':
        return f"+1 ({digits[1:4]}) {digits[4:7]}-{digits[7:]}"
    
    return value

def initials(value, max_chars=2):
    """
    Get initials from name.
    
    Usage: {{ doc.customer_name | initials }}
    """
    if not value:
        return ""
    
    words = str(value).split()
    return "".join(word[0].upper() for word in words[:max_chars])

def nl2br(value):
    """
    Convert newlines to <br> tags.
    
    Usage: {{ doc.description | nl2br | safe }}
    """
    if not value:
        return ""
    return str(value).replace("\n", "<br>")

def pluralize(count, singular, plural=None):
    """
    Return singular or plural based on count.
    
    Usage: {{ items|length }} {{ items|length | pluralize("item", "items") }}
    """
    if plural is None:
        plural = singular + "s"
    
    return singular if count == 1 else plural

def mask_email(value):
    """
    Mask email for privacy.
    
    Usage: {{ doc.email | mask_email }}
    Returns: j***@example.com
    """
    if not value or "@" not in value:
        return value
    
    local, domain = value.split("@", 1)
    if len(local) > 1:
        masked = local[0] + "***"
    else:
        masked = "***"
    
    return f"{masked}@{domain}"

def highlight(value, term):
    """
    Highlight search term in text.
    
    Usage: {{ doc.description | highlight(search_term) | safe }}
    """
    if not value or not term:
        return value
    
    pattern = re.compile(f'({re.escape(term)})', re.IGNORECASE)
    return pattern.sub(r'<mark>\1</mark>', str(value))
```

### hooks.py Registration

```python
# myapp/hooks.py
jenv = {
    "methods": [
        "myapp.jinja_utils.methods"
    ],
    "filters": [
        "myapp.jinja_utils.filters"
    ]
}
```

---

## Quick Reference: Example Usage

| Need | Example Code |
|------|--------------|
| Company logo | `{{ get_company_logo(doc.company) }}` |
| Format address | `{{ format_address(doc.customer_address) \| safe }}` |
| Phone format | `{{ doc.phone \| phone_format }}` |
| Customer balance | `{{ get_customer_balance(doc.customer) }}` |
| Initials | `{{ doc.customer_name \| initials }}` |
| Newlines to BR | `{{ doc.notes \| nl2br \| safe }}` |
| Mask email | `{{ doc.email \| mask_email }}` |
