# Permission Types Reference

## Standard Permission Types

| Permission | Description | Applies To |
|------------|-------------|------------|
| `read` | View document | All DocTypes |
| `write` | Edit document | All DocTypes |
| `create` | Create new document | All DocTypes |
| `delete` | Delete document | All DocTypes |
| `submit` | Submit document | Submittable DocTypes only |
| `cancel` | Cancel submitted document | Submittable DocTypes only |
| `amend` | Amend cancelled document | Submittable DocTypes only |
| `report` | View in Report Builder | All DocTypes |
| `export` | Export to Excel/CSV | All DocTypes |
| `import` | Import via Data Import | All DocTypes |
| `share` | Share document with others | All DocTypes |
| `print` | Print document/generate PDF | All DocTypes |
| `email` | Send email for document | All DocTypes |
| `select` | Select in Link field (v14+) | All DocTypes |

## Special Permission Options

| Option | Description |
|--------|-------------|
| `if_owner` | Permission applies only if user created the document |
| `set_user_permissions` | Can set user permissions for other users |

## Permission Levels (Perm Levels)

Perm Levels group fields for separate access control:

- **Level 0**: Default level, all fields start here
- **Levels 1-9**: Custom groupings for restricted fields

**Critical Rule**: Level 0 MUST be granted before higher levels can be granted.

### Example: Hide Salary Field

```python
# In Customize Form or DocType JSON
{
    "fieldname": "salary",
    "fieldtype": "Currency",
    "permlevel": 1  # Only roles with Level 1 access can see/edit
}
```

## DocType Permissions Configuration

```json
{
  "permissions": [
    {
      "role": "Sales User",
      "permlevel": 0,
      "read": 1,
      "write": 1,
      "create": 1,
      "delete": 0,
      "submit": 0,
      "cancel": 0,
      "amend": 0,
      "report": 1,
      "export": 1,
      "import": 0,
      "share": 1,
      "print": 1,
      "email": 1,
      "if_owner": 0
    }
  ]
}
```

## Automatic Roles

| Role | Assigned To | Purpose |
|------|-------------|---------|
| `Guest` | Everyone (incl. unauthenticated) | Public access |
| `All` | All registered users | Catch-all for authenticated users |
| `Administrator` | Only `Administrator` user | Full system access |
| `Desk User` | Users with `user_type = "System User"` (v15+) | Desk access |

## Custom Permission Types (v16+, Experimental)

```python
# Check custom permission in code
if frappe.has_permission(doc, "approve"):
    approve_document(doc)
else:
    frappe.throw("Not permitted", frappe.PermissionError)
```

**Setup for Custom Permission Types**:
1. Enable developer mode
2. Create Permission Type record
3. Assign via Role Permission Manager
4. Export as fixture
