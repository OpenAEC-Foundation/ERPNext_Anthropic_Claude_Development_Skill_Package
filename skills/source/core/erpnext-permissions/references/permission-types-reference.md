# Permission Types Reference

> Reference for erpnext-permissions skill

---

## Standard Permission Types

### Document-Level Permissions

| Permission | Code | Description | Usage |
|------------|------|-------------|-------|
| `read` | `frappe.has_permission(dt, "read")` | View document | All DocTypes |
| `write` | `frappe.has_permission(dt, "write")` | Edit/update document | All DocTypes |
| `create` | `frappe.has_permission(dt, "create")` | Create new document | All DocTypes |
| `delete` | `frappe.has_permission(dt, "delete")` | Delete document | All DocTypes |
| `select` | `frappe.has_permission(dt, "select")` | Select in Link field | All DocTypes (v14+) |

### Workflow Permissions (Submittable DocTypes)

| Permission | Code | Description | Prerequisite |
|------------|------|-------------|--------------|
| `submit` | `frappe.has_permission(dt, "submit")` | Submit document | `is_submittable = 1` |
| `cancel` | `frappe.has_permission(dt, "cancel")` | Cancel submitted doc | `is_submittable = 1` |
| `amend` | `frappe.has_permission(dt, "amend")` | Amend cancelled doc | `is_submittable = 1` |

### Action Permissions

| Permission | Code | Description |
|------------|------|-------------|
| `report` | N/A | Access Report Builder for DocType |
| `export` | N/A | Export records to Excel/CSV |
| `import` | N/A | Import records via Data Import |
| `share` | N/A | Share document with other users |
| `print` | N/A | Print document or generate PDF |
| `email` | N/A | Send email for document |

---

## Permission Options

### If Owner

Restricts permission to documents created by the user.

```json
{
  "role": "Sales User",
  "permlevel": 0,
  "read": 1,
  "write": 1,
  "if_owner": 1
}
```

**Effect**: Sales User can only read/write Sales Orders they created.

### Set User Permissions

Allows user to create User Permissions for other users.

```json
{
  "role": "Sales Manager",
  "permlevel": 0,
  "set_user_permissions": 1
}
```

---

## Permission Levels (Perm Levels)

### Concept

Group fields into levels (0-9) for separate permission control.

### Configuration

```json
// In DocType field definition
{
  "fieldname": "salary",
  "fieldtype": "Currency",
  "permlevel": 1
}

// In DocType permissions
{
  "role": "HR Manager",
  "permlevel": 1,
  "read": 1,
  "write": 1
}
```

### Rules

1. Level 0 MUST be granted before higher levels
2. Levels don't imply hierarchy (2 is not "higher" than 1)
3. Levels group fields, roles grant access to groups
4. Section break with permlevel affects all fields in section

### Example: Field-Level Security

```
Field: employee_name    permlevel: 0  → Everyone can see
Field: phone           permlevel: 0  → Everyone can see  
Field: salary          permlevel: 1  → Only HR Manager
Field: bank_account    permlevel: 1  → Only HR Manager
Field: performance     permlevel: 2  → Only Department Head
```

---

## Automatic Roles

| Role | Assigned To | Use Case |
|------|-------------|----------|
| `Guest` | All users (including anonymous) | Public website pages |
| `All` | All registered users | Basic authenticated access |
| `Administrator` | Only Administrator user | Full system control |
| `Desk User` | System Users (v15+) | Desk/backend access |

### Usage in DocType

```json
{
  "permissions": [
    {"role": "Guest", "read": 1},
    {"role": "All", "read": 1, "write": 1}
  ]
}
```

---

## Custom Permission Types (v16+)

### Creating Custom Permission

1. Enable Developer Mode
2. Create Permission Type record:
   - Name: `approve`
   - DocType: `Sales Order`
3. Export as fixture
4. Use in Role Permission Manager

### Checking Custom Permission

```python
if frappe.has_permission(doc, "approve"):
    approve_document(doc)
else:
    frappe.throw("Not permitted to approve", frappe.PermissionError)
```

---

## Permission Precedence

1. **Administrator** - Always has all permissions
2. **Role Permissions** - Based on assigned roles
3. **User Permissions** - Restricts to specific documents
4. **has_permission hook** - Can only deny
5. **Sharing** - Grants access to shared documents
6. **if_owner** - Further restricts to owned documents

---

## Quick Decision Table

| I want to... | Use |
|--------------|-----|
| Control who can create documents | `create` permission |
| Let users only edit their own docs | `if_owner` option |
| Hide salary field from most users | Permission Level |
| Restrict access to specific customers | User Permission |
| Add custom "approve" action | Custom Permission Type |
| Programmatically deny access | `has_permission` hook |
