# Security Policy

## Supported Versions

| Version | Supported          |
| ------- | ------------------ |
| 1.x     | :white_check_mark: |

## Reporting a Vulnerability

This project contains documentation and skill definitions for Claude AI. It does not include executable code that runs on your systems.

However, if you discover a security issue (such as credentials accidentally committed, or skill content that could lead to insecure code generation), please report it responsibly:

### How to Report

1. **Do NOT open a public issue**
2. Email the maintainers directly or use GitHub's private vulnerability reporting feature
3. Include:
   - Description of the issue
   - Location (file path, line numbers)
   - Potential impact
   - Suggested fix (if any)

### What to Expect

- Acknowledgment within 48 hours
- Status update within 7 days
- Fix timeline depends on severity

### Scope

Security concerns for this project include:

- Accidentally committed credentials or tokens
- Skill content that generates insecure ERPNext/Frappe code
- Documentation that recommends insecure practices

## Security Best Practices for Users

When using these skills with Claude:

1. Never commit API keys or tokens to repositories
2. Always review generated code before deploying to production
3. Follow ERPNext/Frappe security guidelines for permissions and data access
4. Use environment variables for sensitive configuration
