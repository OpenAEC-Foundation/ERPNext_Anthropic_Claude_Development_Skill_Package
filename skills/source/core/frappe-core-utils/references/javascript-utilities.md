# JavaScript Utilities — frappe.utils

## String & Data

```javascript
// HTML
frappe.utils.escape_html('<script>alert("xss")</script>')  // "&lt;script&gt;..."
frappe.utils.unescape_html("&lt;p&gt;")                    // "<p>"
frappe.utils.html2text("<p>Hello <b>World</b></p>")        // "Hello World"
frappe.utils.strip_whitespace(html)    // Remove empty paragraphs and excess breaks
frappe.utils.is_html("<p>test</p>")    // true
frappe.utils.is_html("plain text")    // false

// JSON
frappe.utils.is_json('{"a": 1}')      // true
frappe.utils.parse_json('{"a": 1}')   // {a: 1} — safe parse with fallback

// URL
frappe.utils.is_url("https://example.com")  // true

// String formatting
frappe.utils.to_title_case("hello world")   // "Hello World"
frappe.utils.comma_and(["a", "b", "c"])     // "a, b, and c"
frappe.utils.comma_or(["a", "b", "c"])      // "a, b, or c"
frappe.utils.comma_sep(["a", "b"], ", ")    // "a, b"

// Array operations
frappe.utils.unique([1, 2, 2, 3])           // [1, 2, 3]
frappe.utils.sort(list, "property_name")    // sort by property
frappe.utils.remove_nulls({a: 1, b: null})  // {a: 1}
frappe.utils.intersection([1,2,3], [2,3,4]) // [2, 3]
frappe.utils.arrays_equal([1,2], [1,2])     // true
```

## Formatting & Numbers

```javascript
// Format any value per fieldtype
frappe.format(1234.56, {fieldtype: "Currency"})  // "$ 1,234.56"
frappe.format("2024-03-15", {fieldtype: "Date"}) // "15-03-2024" (user pref)

// Number formatting
frappe.utils.shorten_number(1234567)        // "1.2M"
frappe.utils.shorten_number(1500, 1)        // "1.5K"
frappe.utils.get_number_of_decimals(3.14)   // 2

// Duration
frappe.utils.get_formatted_duration(3661)   // "1h 1m 1s"
frappe.utils.seconds_to_duration(3661)      // {hours: 1, minutes: 1, seconds: 1}
frappe.utils.duration_to_seconds("1h 30m")  // 5400

// Type validation
frappe.utils.validate_type("42", "number")  // 42 (converts)
```

## DOM & UI

```javascript
// Scroll with highlight
frappe.utils.scroll_to(element, {
    animate: true,
    offset: -50,
    callback: () => console.log("scrolled"),
    highlight: true
});

// Clipboard
frappe.utils.copy_to_clipboard("text to copy");
// Shows "Copied to clipboard" toast automatically

// Sound
frappe.utils.play_sound("click");  // plays /assets/frappe/sounds/click.mp3

// Responsive breakpoints
frappe.utils.is_xs()     // < 576px
frappe.utils.is_sm()     // 576-768px
frappe.utils.is_md()     // 768-992px
frappe.utils.is_mobile() // < 768px (most commonly used)
frappe.utils.is_mac()    // macOS detection
```

## URL & Routing

```javascript
// Current route
frappe.get_route()                    // ["Form", "Sales Order", "SO-001"]
frappe.set_route("Form", "Customer", "CUST-001")

// URL parameters
frappe.utils.get_args_dict_from_url("?status=Open&type=Lead")
// {status: "Open", type: "Lead"}

frappe.utils.get_url_from_dict({status: "Open", type: "Lead"})
// "status=Open&type=Lead"

// File links
frappe.utils.get_file_link("/files/image.png")
// Full URL to the file
```

## File & Media

```javascript
frappe.utils.is_image_file("photo.jpg")   // true
frappe.utils.is_image_file("doc.pdf")     // false
frappe.utils.is_video_file("clip.mp4")    // true

frappe.utils.file_name_ellipsis("very_long_filename_example.pdf", 20)
// "very_long_fi...le.pdf"

// Image resizing
frappe.utils.resize_image(file, (dataURL) => {
    // Use resized image data URL
});
```

## Functional Utilities

```javascript
// Throttle — execute at most once per delay
const throttled = frappe.utils.throttle(() => {
    frappe.call({method: "search", args: {q: input.value}});
}, 300);
input.addEventListener("input", throttled);

// Debounce — wait until activity stops
const debounced = frappe.utils.debounce(() => {
    save_draft();
}, 1000);
textarea.addEventListener("input", debounced);

// Sleep (Promise-based)
await frappe.utils.sleep(500);  // wait 500ms

// Deep equality
frappe.utils.deep_equal({a: 1, b: [2]}, {a: 1, b: [2]})  // true
```

## Security (from common.js)

```javascript
// XSS sanitization
xss_sanitise('<img onerror="alert(1)">')  // sanitized string

// Redirect protection
sanitise_redirect("https://evil.com")     // blocked
sanitise_redirect("/app/home")            // allowed

// HTML stripping
strip_html("<p>Hello <b>World</b></p>")   // "Hello World"

// Abbreviations
get_abbr("Coca Cola", 2)                  // "CC"
```
