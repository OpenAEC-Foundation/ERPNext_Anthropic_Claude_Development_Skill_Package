# String & Validation Functions — frappe.utils

## String Processing

```python
from frappe.utils import (
    strip_html, escape_html, is_html,
    comma_and, comma_or, comma_sep,
    to_markdown, md_to_html, markdown,
    unique, random_string, get_abbr, mask_string
)

# HTML operations
strip_html("<p>Hello <b>World</b></p>")    # "Hello World"
escape_html('<script>alert("xss")</script>') # "&lt;script&gt;..."
is_html("<p>test</p>")                      # True
is_html("plain text")                       # False

# List joining (localization-aware)
comma_and(["Alice", "Bob", "Charlie"])   # "Alice, Bob, and Charlie"
comma_or(["red", "blue", "green"])       # "red, blue, or green"
comma_sep(["a", "b", "c"])              # "a, b, c"

# Markdown ↔ HTML
to_markdown("<h1>Title</h1><p>Text</p>")  # "# Title\n\nText"
md_to_html("# Title\n\nText")             # "<h1>Title</h1>\n<p>Text</p>"
markdown("**bold** text", sanitize=True)   # "<p><strong>bold</strong> text</p>"

# Data utilities
unique([1, 2, 2, 3, 1])                # [1, 2, 3] — preserves order
random_string(10)                        # "aB3xK9mP2q"
get_abbr("Coca Cola Company")           # "CC"
get_abbr("Coca Cola Company", max_len=3) # "CCC"

# Privacy masking [v16+]
mask_string("1234567890")                           # "1234***890"
mask_string("1234567890", show_first=2, show_last=2) # "12******90"
mask_string("secret", mask_char="#")                 # "secr##"
```

## More String Utilities

```python
from frappe.utils import (
    bold, filter_strip_join, strip,
    get_string_between, list_to_str
)

bold("important")                     # "<b>important</b>"
filter_strip_join(["a", "", "b", None, "c"])  # "a, b, c"
strip("  hello  ")                    # "hello"
get_string_between("(hello)", "(", ")")  # "hello"
list_to_str(["a", "b"], sep=" | ")    # "a | b"
```

## Validation Functions

### Email

```python
from frappe.utils import validate_email_address

# Returns valid email(s) or empty string
validate_email_address("user@example.com")          # "user@example.com"
validate_email_address("invalid-email")              # ""
validate_email_address("user@example.com", throw=True)  # raises on invalid

# Handles multiple emails
validate_email_address("a@b.com, c@d.com")           # "a@b.com, c@d.com"
```

### URL

```python
from frappe.utils import validate_url

validate_url("https://example.com")                  # True
validate_url("not-a-url")                            # False
validate_url("ftp://files.example.com")              # True
validate_url("http://example.com", valid_schemes=["https"])  # False
validate_url("https://example.com", throw=True)      # raises on invalid
```

### Phone

```python
from frappe.utils import validate_phone_number

validate_phone_number("+1-555-123-4567")             # True
validate_phone_number("invalid")                      # False
validate_phone_number("+31612345678", throw=True)     # raises on invalid

# v16+: With country code validation
from frappe.utils import validate_phone_number_with_country_code
validate_phone_number_with_country_code("+31612345678", "phone")
```

### JSON

```python
from frappe.utils import validate_json_string

validate_json_string('{"key": "value"}')             # True
validate_json_string('not json')                      # False
```

### IBAN [v16+]

```python
from frappe.utils import validate_iban, is_valid_iban

validate_iban("NL91ABNA0417164300")                  # None (valid)
validate_iban("INVALID", throw=True)                  # raises
is_valid_iban("NL91ABNA0417164300")                  # True
```

## Data Manipulation

```python
from frappe.utils import (
    parse_json, safe_json_loads,
    has_common, is_subset,
    generate_hash, sha256_hash,
    evaluate_filters, compare,
    create_batch
)

# JSON parsing (safe — handles None/empty)
parse_json('{"key": "value"}')     # {"key": "value"}
parse_json(None)                    # None (no crash)
parse_json("")                      # "" (no crash)

# v16+: With default fallback
safe_json_loads('invalid', default={})  # {}

# Set operations
has_common(["a", "b"], ["b", "c"])  # True
is_subset(["a"], ["a", "b", "c"])   # True

# Hashing
generate_hash("my-string", length=8)  # "a1b2c3d4"
sha256_hash("my-string")              # full SHA-256 hash

# Filter evaluation
evaluate_filters(
    {"status": "Open", "priority": "High"},
    [["status", "=", "Open"], ["priority", "=", "High"]]
)  # True

# Batch processing
for batch in create_batch(large_list, batch_size=500):
    process(batch)
```

## Encoding

```python
from frappe.utils import safe_encode, safe_decode, encode

safe_encode("hello")          # b"hello" (str to bytes, UTF-8)
safe_decode(b"hello")         # "hello" (bytes to str, UTF-8)
encode({"key": "value"})      # '{"key": "value"}' (JSON string)
```
