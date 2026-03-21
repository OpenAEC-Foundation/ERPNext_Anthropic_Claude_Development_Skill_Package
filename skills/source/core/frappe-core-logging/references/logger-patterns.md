# Logger API & Patterns — frappe.logger()

## Basic Usage

```python
# ALWAYS specify module name — creates separate log file per module
logger = frappe.logger("my_app")

# Standard Python logging API
logger.debug("Processing batch of 100 items")
logger.info("Successfully synced 50 records")
logger.warning("API rate limit approaching: 80% used")
logger.error("Payment gateway returned 503", exc_info=True)
logger.critical("Database connection pool exhausted")
```

## Logger Parameters

```python
frappe.logger(
    module="my_app",       # → sites/{site}/logs/my_app.log
    with_more_info=False,  # True → appends form_dict to each log line
    allow_site=True,       # True → site-level logs; str → specific site
    filter=None,           # Custom logging.Filter function
    max_size=100_000,      # 100KB per file (default)
    file_count=20          # 20 backup files (default)
)
```

## Common Patterns

### Module-Level Logger

```python
# In your app's Python module — create once, reuse everywhere
import frappe

def process_payments():
    logger = frappe.logger("payment_gateway")
    logger.info("Starting payment batch processing")

    for payment in payments:
        try:
            result = gateway.charge(payment)
            logger.debug(f"Payment {payment.name}: {result.status}")
        except Exception as e:
            logger.error(f"Payment {payment.name} failed: {e}", exc_info=True)
            # Also create visible Error Log for admin
            frappe.log_error(
                title=f"Payment failed: {payment.name}",
                reference_doctype="Payment Entry",
                reference_name=payment.name
            )

    logger.info(f"Batch complete: {len(payments)} payments processed")
```

### Background Job Logging

```python
def sync_inventory():
    logger = frappe.logger("inventory_sync", max_size=500_000, file_count=10)
    logger.info("Inventory sync started")

    try:
        items = fetch_from_erp()
        logger.info(f"Fetched {len(items)} items from ERP")

        for item in items:
            update_stock(item)

        logger.info("Inventory sync completed successfully")
    except Exception:
        logger.error("Inventory sync failed", exc_info=True)
        frappe.log_error(title="Inventory sync failed")
        raise
```

### Request Context Logging

```python
# with_more_info=True → SiteContextFilter adds form_dict to logs
logger = frappe.logger("api_audit", with_more_info=True)
logger.info("API endpoint accessed")
# Log output includes: site name + sanitized request data
# Sensitive fields (password, token, secret, key, pwd) auto-masked as "********"
```

### Custom Filter

```python
import logging

class MinLevelFilter(logging.Filter):
    def __init__(self, min_level):
        self.min_level = min_level

    def filter(self, record):
        return record.levelno >= self.min_level

# Only log WARNING and above for this specific logger
logger = frappe.logger("noisy_module", filter=MinLevelFilter(logging.WARNING))
```

## Stream Logging (Docker/Container)

For containerized deployments where file logging is impractical:

```bash
# Environment variable — all loggers go to stderr instead of files
export FRAPPE_STREAM_LOGGING=1
```

This replaces `RotatingFileHandler` with a `StreamHandler(stderr)`.

## Changing Log Level at Runtime

```python
# Set globally — clears all cached loggers
frappe.utils.logger.set_log_level("DEBUG")

# Affects all subsequent frappe.logger() calls
# Reset by restarting workers/gunicorn
```

## Log File Locations

```
frappe-bench/
├── logs/                          # Bench-level (all sites)
│   ├── frappe.log                 # Default frappe logger
│   ├── frappe.web.log             # HTTP request log
│   ├── web.error.log              # Supervisor HTTP errors
│   ├── worker.error.log           # Supervisor job errors
│   └── monitor.json.log           # Performance metrics
└── sites/
    └── mysite.localhost/
        └── logs/                  # Site-level
            ├── my_app.log         # frappe.logger("my_app")
            ├── payment_gateway.log
            └── inventory_sync.log
```

## Database Query Logging

```python
# Log a specific query's execution time
result = frappe.db.sql("SELECT ...", debug=True)
# Prints: query text + execution time via frappe.log()

# Log ALL queries (site_config.json)
# "logging": 2
# WARNING: massive I/O — development only!
```
