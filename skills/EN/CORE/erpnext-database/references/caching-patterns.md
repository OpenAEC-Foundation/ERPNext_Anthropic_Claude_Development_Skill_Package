# Caching Patterns Reference

## Redis Cache Basis

### Set en Get
```python
# Simpele waarde
frappe.cache.set_value('my_key', 'my_value')
value = frappe.cache.get_value('my_key')

# Dict/lijst
frappe.cache.set_value('user_data', {'name': 'Admin', 'role': 'System Manager'})
data = frappe.cache.get_value('user_data')

# Met expiry (seconden)
frappe.cache.set_value('temp_key', 'value', expires_in_sec=3600)  # 1 uur
frappe.cache.set_value('short_lived', 'value', expires_in_sec=300)  # 5 min
```

### Delete
```python
frappe.cache.delete_value('my_key')
```

---

## Hash Operations

Voor complexe objecten waar velden apart geüpdatet moeten worden.

```python
# Set individuele velden
frappe.cache.hset('user|admin', 'name', 'Administrator')
frappe.cache.hset('user|admin', 'email', 'admin@example.com')
frappe.cache.hset('user|admin', 'last_login', '2024-01-15')

# Get enkel veld
name = frappe.cache.hget('user|admin', 'name')

# Get alle velden
user_data = frappe.cache.hgetall('user|admin')
# {'name': 'Administrator', 'email': 'admin@example.com', 'last_login': '2024-01-15'}

# Delete veld
frappe.cache.hdel('user|admin', 'last_login')
```

---

## Cached Document Access

### get_cached_doc
```python
# Cached document - sneller dan get_doc
doc = frappe.get_cached_doc('Company', 'My Company')

# Gebruik wanneer:
# - Document wijzigt niet vaak
# - Read-only operaties
# - Frequent opgevraagd

# NIET gebruiken wanneer:
# - Altijd actuele data nodig
# - Direct na wijzigingen
```

### get_cached_value
```python
# Cached enkele waarde
country = frappe.get_cached_value('Company', 'My Company', 'country')
```

---

## @redis_cache Decorator

### Basis Gebruik
```python
from frappe.utils.caching import redis_cache

@redis_cache
def expensive_calculation(param1, param2):
    # Tijdrovende berekening
    import time
    time.sleep(2)
    return param1 + param2

# Eerste call: 2 seconden
result = expensive_calculation(10, 20)

# Volgende calls: instant (uit cache)
result = expensive_calculation(10, 20)
```

### Met TTL (Time To Live)
```python
@redis_cache(ttl=300)  # 5 minuten
def get_dashboard_data(user):
    return calculate_dashboard(user)

@redis_cache(ttl=3600)  # 1 uur
def get_monthly_report(month, year):
    return generate_report(month, year)
```

### Cache Invalideren
```python
@redis_cache
def get_user_stats(user):
    return calculate_stats(user)

# Cache handmatig legen
get_user_stats.clear_cache()
```

---

## Cache Patterns

### Dashboard Data
```python
def get_dashboard_data():
    cache_key = f"dashboard_{frappe.session.user}"
    
    # Check cache
    data = frappe.cache.get_value(cache_key)
    if data:
        return data
    
    # Bereken als niet in cache
    data = compute_dashboard()
    
    # Store met expiry
    frappe.cache.set_value(cache_key, data, expires_in_sec=300)
    
    return data
```

### Invalidatie bij Wijziging
```python
class MyDocType(Document):
    def on_update(self):
        # Invalideer gerelateerde caches
        frappe.cache.delete_value(f"stats_{self.user}")
        frappe.cache.delete_value(f"dashboard_{self.user}")
```

### Bulk Cache
```python
def cache_all_companies():
    companies = frappe.get_all('Company', fields=['name', 'country', 'currency'])
    for company in companies:
        frappe.cache.hset('companies', company.name, company)

def get_company_from_cache(name):
    return frappe.cache.hget('companies', name)
```

---

## Best Practices

### 1. Kies Juiste TTL
```python
# Configuratie data - lange TTL
@redis_cache(ttl=3600)  # 1 uur
def get_system_settings():
    pass

# Snel veranderende data - korte TTL
@redis_cache(ttl=60)  # 1 minuut
def get_active_users():
    pass

# Statische data - geen TTL (tot handmatige invalidatie)
@redis_cache
def get_country_list():
    pass
```

### 2. Goede Cache Keys
```python
# ✅ Duidelijk en uniek
cache_key = f"user_stats_{user}_{month}_{year}"
cache_key = f"report_{report_type}_{date}"

# ❌ Te generiek
cache_key = "stats"
cache_key = "data"
```

### 3. Graceful Degradation
```python
def get_data_with_fallback():
    try:
        data = frappe.cache.get_value('my_key')
        if data:
            return data
    except Exception:
        pass  # Redis down, fallback naar database
    
    return fetch_from_database()
```

### 4. Client-side Cache
Frappe implementeert automatisch client-side caching in `frappe.local.cache` om herhaalde Redis calls binnen één request te voorkomen.

```python
# Binnen één request:
frappe.cache.get_value('key')  # Redis call
frappe.cache.get_value('key')  # Uit local cache (geen Redis call)
```

---

## Site-Specific Keys

Frappe prefixed automatisch alle cache keys met site context:

```python
# Site: site1.example.com
frappe.cache.set_value('key', 'value')
# Werkelijke key: site1.example.com|key

# Site: site2.example.com  
frappe.cache.set_value('key', 'value')
# Werkelijke key: site2.example.com|key
```

Dit betekent dat dezelfde key op verschillende sites aparte waarden kan hebben.
