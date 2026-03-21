# Frappe Claude Skill Package — Index

> 60 deterministic skills for Frappe Framework v14-v16 development and operations.

## Quick Stats

| Category | Count | Purpose |
|----------|:-----:|---------|
| syntax/ | 13 | Code syntax reference |
| core/ | 11 | Cross-cutting concerns |
| impl/ | 14 | Implementation workflows |
| errors/ | 7 | Error handling |
| ops/ | 8 | Operations & deployment |
| agents/ | 5 | Intelligent agents |
| testing/ | 2 | Quality & CI/CD |
| **Total** | **60** | |

## Skills by Category

### syntax/ — Code Syntax Reference

| Skill | Description |
|-------|-------------|
| [frappe-syntax-clientscripts](skills/source/syntax/frappe-syntax-clientscripts/) | Use when writing client-side JavaScript for ERPNext/Frappe form events, field manipulation, server calls, or child table handling in v14/v15/v16. |
| [frappe-syntax-controllers](skills/source/syntax/frappe-syntax-controllers/) | Use when writing Python Document Controllers for ERPNext/Frappe DocTypes. |
| [frappe-syntax-customapp](skills/source/syntax/frappe-syntax-customapp/) | Use when building Frappe custom apps from scratch. |
| [frappe-syntax-doctypes](skills/source/syntax/frappe-syntax-doctypes/) | Use when creating or modifying DocType JSON definitions, choosing fieldtypes, configuring naming rules, adding child tables, or setting up tree structures. |
| [frappe-syntax-hooks](skills/source/syntax/frappe-syntax-hooks/) | Use when configuring Frappe hooks.py for app events, scheduler tasks, document events, fixtures, boot session, jenv customization, or website routing. |
| [frappe-syntax-hooks-events](skills/source/syntax/frappe-syntax-hooks-events/) | Use when implementing document lifecycle hooks via doc_events in hooks.py, understanding event execution order, or extending/overriding document behavior from another app. |
| [frappe-syntax-jinja](skills/source/syntax/frappe-syntax-jinja/) | Use when writing Jinja templates for ERPNext/Frappe Print Formats, Email Templates, and Portal Pages. |
| [frappe-syntax-print](skills/source/syntax/frappe-syntax-print/) | Use when creating print formats or generating PDFs in Frappe v14-v16. Covers Jinja, Print Designer, Letter Head, get_pdf(). |
| [frappe-syntax-query-builder](skills/source/syntax/frappe-syntax-query-builder/) | Use when building database queries with frappe.qb in Frappe v14-v16. Covers joins, aggregation, cross-DB compatibility. |
| [frappe-syntax-reports](skills/source/syntax/frappe-syntax-reports/) | Use when building Query Reports, Script Reports, or configuring Report Builder, including chart data integration. |
| [frappe-syntax-scheduler](skills/source/syntax/frappe-syntax-scheduler/) | Use when configuring scheduler events and background jobs in Frappe/ERPNext v14/v15/v16. |
| [frappe-syntax-serverscripts](skills/source/syntax/frappe-syntax-serverscripts/) | Use when writing Python code for ERPNext/Frappe Server Scripts including Document Events, API endpoints, Scheduler Events, and Permission Queries. |
| [frappe-syntax-whitelisted](skills/source/syntax/frappe-syntax-whitelisted/) | Use when creating Frappe Whitelisted Methods (Python API endpoints) for v14/v15/v16. |

### core/ — Cross-Cutting Concerns

| Skill | Description |
|-------|-------------|
| [frappe-core-api](skills/source/core/frappe-core-api/) | Use when building ERPNext/Frappe API integrations (v14/v15/v16) including REST API, RPC API, authentication, webhooks, and rate limiting. |
| [frappe-core-cache](skills/source/core/frappe-core-cache/) | Use when implementing Redis caching, cache invalidation, or distributed locking in Frappe. |
| [frappe-core-database](skills/source/core/frappe-core-database/) | Use when performing database operations in ERPNext/Frappe v14-v16. |
| [frappe-core-files](skills/source/core/frappe-core-files/) | Use when handling file uploads, attachments, private/public file access, or S3 storage configuration. |
| [frappe-core-logging](skills/source/core/frappe-core-logging/) | Use when implementing logging, error tracking, or monitoring in Frappe v14-v16. Covers frappe.logger(), log_error(), Sentry. |
| [frappe-core-notifications](skills/source/core/frappe-core-notifications/) | Use when implementing email notifications, system alerts, Assignment Rules, Auto Repeat, or ToDo items. |
| [frappe-core-permissions](skills/source/core/frappe-core-permissions/) | Use when implementing the Frappe/ERPNext permission system. |
| [frappe-core-search](skills/source/core/frappe-core-search/) | Use when implementing search functionality in Frappe v14-v16. Covers link search, global search, SQLiteSearch FTS5. |
| [frappe-core-translation](skills/source/core/frappe-core-translation/) | Use when implementing translations/i18n in Frappe v14-v16 apps. Covers _(), __(), CSV/PO files, string extraction. |
| [frappe-core-utils](skills/source/core/frappe-core-utils/) | Use when working with utility functions in Frappe v14-v16. Covers 140+ date, number, string, validation functions. |
| [frappe-core-workflow](skills/source/core/frappe-core-workflow/) | Use when creating or modifying Frappe Workflows, defining states and transitions, adding action conditions, or troubleshooting workflow permission errors. |

### impl/ — Implementation Workflows

| Skill | Description |
|-------|-------------|
| [frappe-impl-clientscripts](skills/source/impl/frappe-impl-clientscripts/) | Use when implementing client-side form features in Frappe/ERPNext: field visibility, cascading filters, calculated fields, custom buttons, server calls, form validation, child table logic, debugging. |
| [frappe-impl-controllers](skills/source/impl/frappe-impl-controllers/) | Use when building Document Controllers in a custom Frappe app: file creation, lifecycle hooks, validation, autoname, submittable workflows, controller override. |
| [frappe-impl-customapp](skills/source/impl/frappe-impl-customapp/) | Use when building a custom Frappe app from scratch. |
| [frappe-impl-hooks](skills/source/impl/frappe-impl-hooks/) | Use when implementing hooks.py configurations in a Frappe custom app. |
| [frappe-impl-integrations](skills/source/impl/frappe-impl-integrations/) | Use when implementing OAuth providers, Connected Apps, Webhooks, Payment Gateways, or Data Import/Export in Frappe. |
| [frappe-impl-jinja](skills/source/impl/frappe-impl-jinja/) | Use when building Jinja templates in Frappe: Print Formats, Email Templates, Notification templates, Portal Pages, and custom Jinja methods. |
| [frappe-impl-reports](skills/source/impl/frappe-impl-reports/) | Use when building Script Reports, Query Reports, dashboard charts, or Number Cards in ERPNext. |
| [frappe-impl-scheduler](skills/source/impl/frappe-impl-scheduler/) | Use when implementing scheduled tasks and background jobs in Frappe v14/v15/v16. |
| [frappe-impl-serverscripts](skills/source/impl/frappe-impl-serverscripts/) | Use when implementing server-side features via Setup > Server Script: document validation, auto-fill, API endpoints, scheduled tasks, permission queries. |
| [frappe-impl-ui-components](skills/source/impl/frappe-impl-ui-components/) | Use when building custom dialogs, extending List View, creating Page controllers, or adding Kanban/Calendar views and realtime updates. |
| [frappe-impl-website](skills/source/impl/frappe-impl-website/) | Use when building portal pages, Web Forms, website routes, or configuring themes and SEO in Frappe. |
| [frappe-impl-whitelisted](skills/source/impl/frappe-impl-whitelisted/) | Use when building API endpoints with @frappe.whitelist() in Frappe. |
| [frappe-impl-workflow](skills/source/impl/frappe-impl-workflow/) | Use when implementing document Workflows, approval chains, or state-based transitions in Frappe. |
| [frappe-impl-workspace](skills/source/impl/frappe-impl-workspace/) | Use when creating or customizing Workspace pages in Frappe v14-v16. Covers shortcuts, number cards, charts, JSON format. |

### errors/ — Error Handling

| Skill | Description |
|-------|-------------|
| [frappe-errors-api](skills/source/errors/frappe-errors-api/) | Use when debugging or handling API errors in Frappe/ERPNext v14/v15/v16. |
| [frappe-errors-clientscripts](skills/source/errors/frappe-errors-clientscripts/) | Use when debugging or preventing errors in Frappe Client Scripts. |
| [frappe-errors-controllers](skills/source/errors/frappe-errors-controllers/) | Use when debugging or preventing errors in Frappe Document Controllers. |
| [frappe-errors-database](skills/source/errors/frappe-errors-database/) | Use when handling database errors in Frappe/ERPNext. |
| [frappe-errors-hooks](skills/source/errors/frappe-errors-hooks/) | Use when debugging hooks.py errors in Frappe/ERPNext. |
| [frappe-errors-permissions](skills/source/errors/frappe-errors-permissions/) | Use when debugging or handling permission errors in Frappe/ERPNext. |
| [frappe-errors-serverscripts](skills/source/errors/frappe-errors-serverscripts/) | Use when debugging or preventing errors in Frappe Server Scripts. |

### ops/ — Operations & Deployment

| Skill | Description |
|-------|-------------|
| [frappe-ops-app-lifecycle](skills/source/ops/frappe-ops-app-lifecycle/) | Use when scaffolding a new Frappe app, configuring app settings, building assets, running tests, deploying, updating, or publishing to marketplace. |
| [frappe-ops-backup](skills/source/ops/frappe-ops-backup/) | Use when configuring backups, restoring sites, encrypting backup files, scheduling automated backups, or planning disaster recovery. |
| [frappe-ops-bench](skills/source/ops/frappe-ops-bench/) | Use when running bench commands, managing sites, configuring multi-tenancy, or setting up domains. |
| [frappe-ops-cloud](skills/source/ops/frappe-ops-cloud/) | Use when working with Frappe Cloud, Press API, provisioning sites, or managing benches on Frappe Cloud infrastructure. |
| [frappe-ops-deployment](skills/source/ops/frappe-ops-deployment/) | Use when deploying Frappe/ERPNext to production, configuring Nginx or Supervisor, setting up Docker, enabling SSL, or hardening security. |
| [frappe-ops-frontend-build](skills/source/ops/frappe-ops-frontend-build/) | Use when configuring frontend asset bundling, migrating from build.json (v14) to esbuild (v15+), or troubleshooting SCSS/CSS compilation. |
| [frappe-ops-performance](skills/source/ops/frappe-ops-performance/) | Use when tuning MariaDB, configuring Redis memory, sizing Gunicorn workers, setting up CDN, or profiling slow queries. |
| [frappe-ops-upgrades](skills/source/ops/frappe-ops-upgrades/) | Use when upgrading Frappe/ERPNext between major versions (v14 to v15, v15 to v16), troubleshooting failed migrations, or planning rollback. |

### agents/ — Intelligent Agents

| Skill | Description |
|-------|-------------|
| [frappe-agent-architect](skills/source/agents/frappe-agent-architect/) | Use when designing multi-app Frappe architectures, deciding whether to split functionality into separate apps, or implementing cross-app communication patterns. |
| [frappe-agent-debugger](skills/source/agents/frappe-agent-debugger/) | Use when debugging Frappe errors, using bench console for live inspection, analyzing tracebacks, or reading Frappe log files. |
| [frappe-agent-interpreter](skills/source/agents/frappe-agent-interpreter/) | Use when receiving vague or unclear ERPNext/Frappe development requests that need interpretation. |
| [frappe-agent-migrator](skills/source/agents/frappe-agent-migrator/) | Use when migrating a Frappe app between major versions, detecting breaking API changes, or resolving post-migration errors. |
| [frappe-agent-validator](skills/source/agents/frappe-agent-validator/) | Use when reviewing or validating Frappe/ERPNext code against best practices and common pitfalls. |

### testing/ — Quality & CI/CD

| Skill | Description |
|-------|-------------|
| [frappe-testing-cicd](skills/source/testing/frappe-testing-cicd/) | Use when setting up CI/CD pipelines for Frappe apps, configuring GitHub Actions test workflows, or adding linting and security scanning. |
| [frappe-testing-unit](skills/source/testing/frappe-testing-unit/) | Use when writing unit tests, integration tests, creating test fixtures, or running tests with bench run-tests. |

---

## Quick Selection Guide

```
What do you need to build?
│
├─► Form behavior / UX
│   └─► syntax-clientscripts + impl-clientscripts + errors-clientscripts
│
├─► Quick server logic (no custom app)
│   └─► syntax-serverscripts + impl-serverscripts + errors-serverscripts
│
├─► Full DocType customization
│   └─► syntax-controllers + syntax-doctypes + impl-controllers + errors-controllers
│       + core-database + core-permissions
│
├─► Extend existing ERPNext DocType
│   └─► syntax-hooks + syntax-hooks-events + impl-hooks + errors-hooks
│
├─► Build API endpoints
│   └─► syntax-whitelisted + impl-whitelisted + core-api + errors-api
│
├─► Print formats / Templates / PDF
│   └─► syntax-print + syntax-jinja + impl-jinja
│
├─► Reports & Dashboards
│   └─► syntax-reports + impl-reports
│
├─► Scheduled automation
│   └─► syntax-scheduler + impl-scheduler + syntax-hooks
│
├─► Complete custom app
│   └─► syntax-customapp + impl-customapp + ops-app-lifecycle
│
├─► Workflows & Approvals
│   └─► core-workflow + impl-workflow
│
├─► External integrations
│   └─► impl-integrations + core-api + errors-api
│
├─► UI components (dialogs, lists, realtime)
│   └─► impl-ui-components + impl-clientscripts
│
├─► Website / Portal
│   └─► impl-website + syntax-jinja + impl-jinja
│
├─► Translation / i18n
│   └─► core-translation
│
├─► Utility functions (date, money, string)
│   └─► core-utils
│
├─► Search functionality
│   └─► core-search
│
├─► Logging & error tracking
│   └─► core-logging + agent-debugger
│
├─► Workspace / Dashboard
│   └─► impl-workspace + impl-ui-components
│
├─► Complex database queries
│   └─► syntax-query-builder + core-database
│
├─► Deploy to production
│   └─► ops-deployment + ops-bench + ops-performance + ops-backup
│
├─► CI/CD & Testing
│   └─► testing-unit + testing-cicd
│
├─► Version upgrade (v14→v15→v16)
│   └─► ops-upgrades + agent-migrator
│
├─► Multi-app architecture
│   └─► agent-architect + ops-app-lifecycle
│
├─► Debug an error
│   └─► agent-debugger + relevant errors/* skill
│
└─► Don't know where to start?
    └─► agent-interpreter (will analyze your request and recommend skills)
```

---

## Related Documentation

| Document | Description |
|----------|-------------|
| [README.md](README.md) | Project overview and installation |
| [ROADMAP.md](ROADMAP.md) | Project status and history |
| [LESSONS.md](LESSONS.md) | Technical discoveries |
| [WAY_OF_WORK.md](WAY_OF_WORK.md) | 7-phase methodology |
| [CHANGELOG.md](CHANGELOG.md) | Version history |

---

*Frappe Claude Skill Package v3.0 | 60 skills | Last updated: 2026-03-21*
