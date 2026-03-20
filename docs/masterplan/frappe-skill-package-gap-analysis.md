# Frappe Framework Skill Package — Gap Analysis

> **Doel**: Volledige dekking van het Frappe Framework + ERPNext + Bench/Cloud/Ops stack
> **Huidige staat**: 28 skills (v1.2) — uitsluitend gericht op ERPNext development
> **Datum**: 2026-03-20
> **Auteur**: Freek / OpenAEC Foundation

---

## Methodologie

Deze audit mapt het **volledige Frappe Framework** (zoals gedocumenteerd op docs.frappe.io, de GitHub source, en v16 release notes) tegen de huidige 28 skills. Elke Frappe capability is geclassificeerd als:

- ✅ **Gedekt** — Dedicated skill of substantieel behandeld in bestaande skill
- 🟡 **Gedeeltelijk** — Zijdelings geraakt maar geen dedicated/complete dekking
- ❌ **Ontbreekt** — Niet of nauwelijks aanwezig

De analyse is opgesplitst in 7 lagen, van Frappe core tot productie-infrastructuur.

---

## Laag 1: DocType System & Data Model

Het hart van Frappe — alles draait om DocTypes.

| Capability | Status | Huidige dekking | Gap |
|---|---|---|---|
| DocType JSON schema design | ❌ | Alleen naming in `syntax-controllers` | **Geen skill voor fieldtypes, options, depends_on, mandatory_depends_on, fetch_from, unique, in_list_view, search_index, etc.** Claude maakt hier structureel fouten bij schema-generatie. |
| Child/Table DocType design | 🟡 | Iteratie in client/server scripts | Geen dedicated patterns voor parent-child relaties, `parenttype`/`parentfield`, idx management |
| Single DocType | 🟡 | Kort in `database` (get_single_value) | Geen patterns voor Settings-stijl DocTypes, `is_virtual`, wanneer Single vs Regular |
| Virtual DocType | 🟡 | Kort in `syntax-controllers` | Geen implementatie-patterns, `get_list`/`get_count` overrides, externe data bronnen |
| DocType field types reference | ❌ | — | **Ontbreekt volledig**: alle 40+ fieldtypes (Link, Dynamic Link, Table MultiSelect, Geolocation, Barcode, Duration, JSON, Markdown, etc.) met hun opties en gedrag |
| Link field mechanics | 🟡 | `set_query` in client scripts | Geen server-side link validation, `fetch_from`, `fetch_if_empty`, cascading links |
| Naming rules (comprehensive) | 🟡 | autoname in controllers | Ontbreekt: `naming_rule` vs `autoname`, Expression naming, hash, Prompt, custom series management |
| Tree DocType (NestedSet) | 🟡 | 1 regel in controllers | **Geen patterns** voor hiërarchische data, `lft`/`rgt`, `get_ancestors`, `get_descendants`, rebuild tree |
| Customize Form / Custom Field | ❌ | Alleen fixtures-export | **Geen programmatische patterns**: `create_custom_fields()`, `make_property_setter()`, migrating customizations |
| Property Setter | ❌ | Alleen als fixture | Geen API-patterns voor runtime doctype customization |
| DocType Actions & Links | ❌ | — | Ontbreekt: dashboard links, document links, standard actions |
| Workspace configuration | ❌ | — | Desk Workspace DocType, shortcuts, charts, number cards |

### Aanbevolen nieuwe skills voor Laag 1

1. **`frappe-doctype-design`** (syntax + impl) — Schema design, fieldtypes, naming rules, tree doctypes, virtual doctypes
2. **`frappe-customization-api`** (syntax + impl) — Custom Fields, Property Setters, Customize Form, programmatic customization

---

## Laag 2: Reports & Data Analysis

Een van de meest gebruikte features in elk ERPNext project — en volledig afwezig.

| Capability | Status | Huidige dekking | Gap |
|---|---|---|---|
| Report Builder | ❌ | — | Geen documentatie over no-code reports |
| Query Report | ❌ | — | **Kritiek**: `execute()` functie, columns format, filters, prepared_report, chart data. Claude genereert hier vaak fout gevormde columns. |
| Script Report | ❌ | — | **Kritiek**: JavaScript report met `frappe.query_report`, add_total_row, custom formatters, report actions |
| Report Print Format | 🟡 | Waarschuwing in Jinja skill dat het JS is | Geen JS templating patterns (`{%= %}`) |
| Number Card | ❌ | — | DocType, custom method, aggregation |
| Dashboard Chart | ❌ | — | Chart sources, custom chart, report chart |
| Dashboard | ❌ | — | Dashboard DocType, dashboard customization |
| Prepared Report | ❌ | — | Async report generation voor grote datasets |

### Aanbevolen nieuwe skills voor Laag 2

3. **`frappe-reports`** (syntax + impl + errors) — Query Report, Script Report, Report Builder, Report Print Format, chart data, Prepared Report

---

## Laag 3: Workflow & Business Process

| Capability | Status | Huidige dekking | Gap |
|---|---|---|---|
| Workflow Engine | ❌ | 1 regel in code-interpreter | **Kritiek**: Workflow DocType, states, transitions, conditions, actions, `apply_workflow` |
| Workflow Actions | ❌ | — | User-assigned workflow actions, approval chain |
| Assignment Rules | ❌ | — | Auto-assignment based on conditions |
| Auto Repeat | ❌ | — | Recurring document creation |
| Notification system | ❌ | — | **Kritiek**: Notification DocType, email/system/SMS alerts, condition-based triggers, Jinja in notifications |
| Email sending | 🟡 | `frappe.sendmail` in events | Geen Email Account setup, Email Queue, tracking, bulk email |
| Email receiving | ❌ | — | Email Account configuration, email-to-document linking |
| ToDo / Assignment | ❌ | — | `frappe.assign_to`, ToDo DocType, assignment patterns |
| Comment system | ❌ | — | `doc.add_comment()`, comment types, activity log |
| Tags | ❌ | — | `doc.add_tag()`, tag-based filtering |
| Sharing | 🟡 | `add_share` in permissions | Geen complete sharing patterns |
| Energy Points / Gamification | ❌ | — | Point rules, leaderboard |

### Aanbevolen nieuwe skills voor Laag 3

4. **`frappe-workflow`** (syntax + impl + errors) — Workflow engine, states, transitions, actions, approval chains
5. **`frappe-notifications-email`** (syntax + impl) — Notification DocType, email sending/receiving, Email Account, templates, bulk email
6. **`frappe-automation`** (impl) — Assignment Rules, Auto Repeat, ToDo/Assignment patterns, Comments, Tags

---

## Laag 4: Frontend & UI Framework

| Capability | Status | Huidige dekking | Gap |
|---|---|---|---|
| Form Scripts (Client Scripts) | ✅ | Volledig gedekt | — |
| List View customization | ❌ | — | `frappe.listview_settings`, custom indicators, bulk actions, sidebar filters |
| Page API | ❌ | — | Custom pages (`frappe.ui.Page`), toolbars, sidebars |
| Dialog API (JS) | ❌ | — | `frappe.ui.Dialog`, multi-step dialogs, field configuration |
| Dialog API (Python) | ❌ | — | `frappe.ui.Dialog` from Python, server-side dialog prompts |
| Controls API | ❌ | — | Custom field controls, control lifecycle |
| Tree View | ❌ | — | Tree DocType rendering, tree events |
| Kanban View | ❌ | — | Kanban board configuration, custom columns |
| Calendar View | ❌ | — | Calendar events, scheduling UI |
| Image View | ❌ | — | Image field rendering, gallery view |
| Map View | ❌ | — | Geolocation rendering |
| Chart API (JS) | ❌ | — | `frappe.ui.Chart`, custom charting |
| Scanner API | ❌ | — | Barcode/QR scanning in forms |
| Realtime / Socket.IO | ❌ | — | **Belangrijk**: `frappe.publish_realtime()`, `frappe.realtime.on()`, progress indicators, live updates |
| Form Tours | ❌ | — | Interactive onboarding tours |
| Desk Sidebar / Search | ❌ | — | Awesome Bar, global search customization |
| Frappe UI (Vue.js, v15+) | ❌ | — | Het nieuwe frontend framework, relevant voor v15/v16 custom pages |

### Aanbevolen nieuwe skills voor Laag 4

7. **`frappe-ui-components`** (syntax + impl) — Dialog API, List View settings, Page API, Tree View, Kanban, Calendar, Chart API, Scanner
8. **`frappe-realtime`** (syntax + impl) — Socket.IO patterns, `publish_realtime`, progress bars, live updates

---

## Laag 5: Web & Portal Framework

| Capability | Status | Huidige dekking | Gap |
|---|---|---|---|
| Portal Pages (www/) | 🟡 | Basis in Jinja impl | Geen complete portal architecture |
| Web Forms | ❌ | — | **Belangrijk**: Web Form DocType, guest submissions, file uploads, payment integration, custom scripts |
| Website Settings | ❌ | — | Navbar, footer, homepage, theme |
| Website Route Rules | ❌ | — | `website_route_rules` hook, URL patterns |
| Blog | ❌ | — | Blog Post/Category, website context |
| Web Templates | ❌ | — | Reusable web components (v14+) |
| Website Theme / CSS | ❌ | — | Custom themes, SCSS compilation |
| Guest access patterns | ❌ | — | Public pages, rate limiting, CSRF |
| SEO | ❌ | — | Meta tags, Open Graph, sitemap |
| Web Page / Landing Pages | ❌ | — | Static and dynamic web pages |

### Aanbevolen nieuwe skills voor Laag 5

9. **`frappe-website-portal`** (syntax + impl) — Web Forms, Portal Pages, Website Settings, routes, guest access, themes, SEO

---

## Laag 6: System Services & Integrations

| Capability | Status | Huidige dekking | Gap |
|---|---|---|---|
| File handling | ❌ | — | **Belangrijk**: File DocType, `frappe.get_file()`, `save_file()`, upload handling, S3/cloud storage |
| Redis / Caching | 🟡 | Basis in database skill | Geen dedicated patterns: `frappe.cache()`, `@redis_cache`, invalidation, distributed locking, cache stampede |
| Full Text Search | ❌ | — | `FullTextSearch` API, search index, `frappe.utils.global_search` |
| Translation / i18n | 🟡 | `_()` in meerdere skills | Geen translation file management, CSV translations, custom app translations, RTL |
| Logging | 🟡 | `frappe.log_error` overal | Geen structured logging, log levels, log cleanup, monitoring integration |
| OAuth / Connected Apps | ❌ | — | OAuth2 provider/consumer, Social Login, Connected Apps |
| Webhooks (inbound/outbound) | 🟡 | Basis in API patterns | Geen Webhook DocType configuratie, secret validation, retry logic |
| Payment Gateway integration | ❌ | — | Payment Request, payment controller |
| Data Import/Export | ❌ | — | Data Import DocType, CSV patterns, bulk import, import log |
| Print Designer | ❌ | — | Nieuw in v15/v16: drag-drop print format builder |
| Document Naming Series mgmt | ❌ | — | Naming Series DocType, series management, prefix changes |
| Letter Head | ❌ | — | Letter Head DocType, per-company headers |
| Bulk operations | ❌ | — | `frappe.utils.background_jobs`, bulk update patterns, progress tracking |

### Aanbevolen nieuwe skills voor Laag 6

10. **`frappe-file-handling`** (syntax + impl) — File DocType, uploads, S3, private/public files, file URL patterns
11. **`frappe-cache-redis`** (syntax + impl) — Redis patterns, `@redis_cache`, invalidation, locking
12. **`frappe-integrations`** (syntax + impl) — OAuth, Connected Apps, Webhooks (DocType), Payment Gateway, Data Import/Export
13. **`frappe-print-system`** (syntax + impl) — Print Designer, Letter Head, Naming Series management, print settings

---

## Laag 7: Bench, Deployment & Operations

Dit is de laag die jullie specifiek nodig hebben voor Impertio — provisioning, hosting, operations.

| Capability | Status | Huidige dekking | Gap |
|---|---|---|---|
| Bench CLI | ❌ | Alleen `bench new-app`, `bench migrate` | **Kritiek voor ops**: Volledige bench commando referentie, site management, multi-tenancy |
| Site management | ❌ | — | `bench new-site`, `bench drop-site`, site config, domain mapping |
| Multi-tenancy | ❌ | — | DNS-based routing, site_config.json per site, shared vs dedicated workers |
| Backup & Restore | ❌ | — | `bench backup`, `bench restore`, encrypted backups, S3 backup, scheduled backups |
| bench doctor & diagnostics | ❌ | — | Health checks, worker status, queue monitoring |
| MariaDB management | ❌ | — | Database tuning, `common_site_config.json`, connection pooling, slow query logging |
| Redis configuration | ❌ | — | Cache/Queue/Socket.IO Redis instances, memory management |
| Nginx / reverse proxy | ❌ | — | `bench setup nginx`, SSL, custom domains, rate limiting |
| Supervisor / systemd | ❌ | — | `bench setup supervisor`, worker management, process monitoring |
| Frappe Cloud / FC API | ❌ | — | **Jullie usecase**: API voor site provisioning, bench management, app deployment |
| Press (self-hosted cloud) | ❌ | — | Self-hosted Frappe Cloud alternative, agent-based deployment |
| Hetzner + Frappe hosting | ❌ | — | **Jullie specifieke stack**: Server provisioning, DNS, SSL, monitoring op Hetzner |
| bench update & upgrades | ❌ | — | Version upgrades, migration path, breaking changes, rollback |
| bench build & assets | ❌ | — | Frontend build pipeline, asset compilation, bundle optimization |
| Docker deployment | ❌ | — | frappe-docker, compose setup, production containers |
| Production setup | ❌ | — | `bench setup production`, fail2ban, firewall, security hardening |
| Performance tuning | ❌ | — | Gunicorn workers, Redis memory, MariaDB buffer pool, CDN |
| Monitoring & alerting | ❌ | — | Error tracking, uptime monitoring, log aggregation |
| App installation/removal | ❌ | — | `bench install-app`, `bench remove-app`, app dependencies, ordering |
| Migrate patterns | ❌ | — | `bench migrate` internals, patch ordering, troubleshooting failed migrations |

### Aanbevolen nieuwe skills voor Laag 7

14. **`frappe-bench-cli`** (syntax + impl) — Complete bench referentie, site management, multi-tenancy, domains
15. **`frappe-deployment`** (impl + errors) — Production setup (Nginx, Supervisor, SSL), Docker, security hardening
16. **`frappe-backup-restore`** (syntax + impl) — Backup strategieën, restore, encrypted backups, S3, disaster recovery
17. **`frappe-cloud-provisioning`** (syntax + impl) — Frappe Cloud API, Press, site provisioning, bench management
18. **`frappe-hosting-hetzner`** (impl) — Jullie specifieke Hetzner stack: server setup, DNS, monitoring, scaling
19. **`frappe-performance`** (impl) — MariaDB tuning, Redis optimization, Gunicorn workers, caching strategies, CDN
20. **`frappe-upgrades-migration`** (impl + errors) — Version upgrades, migration troubleshooting, rollback, breaking changes

---

## Laag 8: App Development Lifecycle (End-to-End)

Het hele verhaal van idee → app → productie. De bestaande `frappe-syntax-customapp` en `frappe-impl-customapp` dekken de basisstructuur (pyproject.toml, modules.txt, patches, fixtures), maar het volledige plaatje ontbreekt grotendeels.

| Capability | Status | Huidige dekking | Gap |
|---|---|---|---|
| **App scaffolding** (`bench new-app`) | 🟡 | Basis in customapp skills | Geen uitleg wat elk gegenereerd bestand doet, waarom, en hoe je het aanpast |
| **App configuratie patterns** | ❌ | — | Settings DocType pattern (Single DocType voor app config), `after_install` data seeding, setup defaults, onboarding |
| **Setup Wizard** | ❌ | — | `setup_wizard_requires` hook, setup stages, post-install configuratie, wizard slides |
| **Module Def** | ❌ | — | Module Def DocType, module-level icon/label/description, module visibility |
| **hooks.py comprehensive** | 🟡 | ~15 hooks gedekt | **30+ hooks ontbreken**: `doctype_list_js`, `doctype_tree_js`, `doctype_calendar_js`, `override_doctype_dashboards`, `standard_portal_menu_items`, `default_mail_footer`, `website_generators`, `website_route_rules`, `on_session_creation`, `on_logout`, `auth_hooks`, `get_website_user_home_page`, `boot_session`, `website_context`, `update_website_context`, `jinja`, `override_doctype_class` (v14) vs `extend_doctype_class` (v16) interplay, `export_python_type_annotations`, `sounds`, `notification_config`, `get_help_messages`, `leaderboards`, `default_letter_heads`, etc. |
| **Frontend build pipeline** | ❌ | — | **Belangrijk**: `build.json` (v14) vs esbuild (v15+), `bundle_map`, welke files waar, SCSS/Less compilatie, `bench build --app`, asset bundling strategie |
| **`bench get-app`** | ❌ | — | Installeren van GitHub, specifieke branch/tag, private repos met SSH keys, `--resolve-deps` |
| **`bench install-app` / `bench remove-app`** | ❌ | — | Installatie op bestaande site, volgorde bij dependencies, migratie bij install, uninstall cleanup |
| **`bench console` / development tools** | ❌ | — | `bench console` (iPython), `bench mariadb`, `bench --site execute`, `bench clear-cache`, `bench clear-website-cache`, `bench set-config developer_mode 1` |
| **Development mode vs Production** | ❌ | — | `developer_mode` implicaties (auto-reload, debug toolbar, schema sync), wanneer aan/uit, veiligheid |
| **App dependencies & load order** | 🟡 | `required_apps` in hooks.py | Geen uitleg over installatie-volgorde, dependency resolution, conflicten, `frappe` als implicit dependency |
| **App versioning & releases** | ❌ | — | Semantic versioning in `__init__.py`, CHANGELOG management, GitHub releases, tagging, `bench switch-to-branch` |
| **App publishing / Marketplace** | ❌ | — | Frappe Marketplace publicatie, `frappecloud.com` app listing, metadata, screenshots, pricing |
| **Custom Desk Pages** | ❌ | — | `frappe.ui.Page` in Python + JS, toolbar, sidebar, body, breadcrumbs — volledig custom admin pagina's (anders dan portal/www) |
| **App update lifecycle** | 🟡 | Patches basis in customapp | Geen uitleg over het hele update-verhaal: hoe een app-update door een klant-site stroomt (`bench update` → `bench migrate` → patches → fixtures → build) |
| **Multi-app architectuur** | ❌ | — | Wanneer 1 app vs meerdere apps, app composability, shared DocTypes, cross-app hooks, base app + vertical pattern |
| **App documentation patterns** | ❌ | — | README structuur voor Frappe apps, docs integratie, Frappe Wiki, user documentation |
| **App debugging** | ❌ | — | `bench console` debugging, `frappe.logger()`, Python debugger (`pdb`/`ipdb`), browser devtools voor Frappe, `bench set-config developer_mode`, `frappe.flags.in_test` |

### Aanbevolen nieuwe skills voor Laag 8

22. **`frappe-app-lifecycle`** (impl) — End-to-end: scaffolding → development → build → test → deploy → update → publish. Setup Wizard, Module Def, app configuration patterns, development mode, debugging.
23. **`frappe-hooks-comprehensive`** (syntax) — Complete hooks.py referentie met ALLE 50+ hooks, niet alleen de 15 die nu gedekt zijn. Met decision tree welke hook wanneer.
24. **`frappe-frontend-build`** (syntax + impl) — Build pipeline, esbuild (v15+) vs build.json (v14), asset bundling, SCSS, bench build, custom bundles.
25. **`frappe-multi-app-architecture`** (impl) — Wanneer split je in meerdere apps, dependency management, cross-app patterns, marketplace publicatie.

---

## Laag 0: Testing & Quality (Cross-cutting)

| Capability | Status | Huidige dekking | Gap |
|---|---|---|---|
| Unit testing | ❌ | — | **Kritiek**: `frappe.tests.utils`, `IntegrationTestCase`, `UnitTestCase`, test setup |
| Test fixtures | ❌ | — | `test_records.json`, factory patterns, test data management |
| Test CLI | ❌ | — | `bench run-tests`, `--module`, `--doctype`, `--test`, parallel testing |
| CI/CD patterns | ❌ | — | GitHub Actions voor Frappe apps, test matrix, lint, semgrep |
| Code quality | ❌ | — | Frappe-specific linting rules, type hints (v15+), pre-commit hooks |
| API testing | ❌ | — | Testing whitelisted methods, integration tests met auth |

### Aanbevolen nieuwe skills voor Laag 0

21. **`frappe-testing`** (syntax + impl) — Unit/integration tests, fixtures, bench run-tests, CI/CD, code quality

---

## Samenvatting

### Huidige dekking vs Frappe surface area

| Laag | Capabilities | Gedekt | Gedeeltelijk | Ontbreekt |
|---|---|---|---|---|
| 1. DocType System | 12 | 0 | 5 | 7 |
| 2. Reports | 8 | 0 | 1 | 7 |
| 3. Workflow & Process | 12 | 0 | 2 | 10 |
| 4. Frontend & UI | 17 | 1 | 0 | 16 |
| 5. Web & Portal | 10 | 0 | 1 | 9 |
| 6. System Services | 13 | 0 | 4 | 9 |
| 7. Bench & Ops | 20 | 0 | 0 | 20 |
| **8. App Lifecycle** | **17** | **0** | **4** | **13** |
| 0. Testing | 6 | 0 | 0 | 6 |
| **Totaal** | **115** | **1** | **17** | **97** |

**Conclusie**: De huidige 28 skills dekken ~16% van het Frappe surface area, geconcentreerd op de Python/JS development loop. 97 capabilities zijn niet of nauwelijks gedekt.

### Voorgestelde roadmap (25 nieuwe skills)

| Prioriteit | Skills | Rationale |
|---|---|---|
| **P0 — Must have** | `frappe-doctype-design`, `frappe-reports`, `frappe-workflow`, `frappe-testing`, `frappe-app-lifecycle` | Komen in elk project voor, hoge fout-frequentie bij Claude |
| **P1 — High value** | `frappe-notifications-email`, `frappe-ui-components`, `frappe-realtime`, `frappe-website-portal`, `frappe-file-handling`, `frappe-hooks-comprehensive` | Veel voorkomend in implementaties, complex genoeg voor dedicated skill |
| **P2 — Operations** | `frappe-bench-cli`, `frappe-deployment`, `frappe-backup-restore`, `frappe-performance`, `frappe-upgrades-migration`, `frappe-frontend-build` | Jullie Impertio/Hetzner usecase, essentieel voor managed hosting & app development |
| **P3 — Specialized** | `frappe-cloud-provisioning`, `frappe-hosting-hetzner`, `frappe-customization-api`, `frappe-automation`, `frappe-cache-redis`, `frappe-integrations`, `frappe-print-system`, `frappe-multi-app-architecture` | Specifieke usecases, hoge waarde maar lagere frequentie |

### Herstructurering voorstel

De huidige repo heet `ERPNext_Anthropic_Claude_Development_Skill_Package`. Met deze uitbreiding dekt het heel Frappe. Voorstel:

```
frappe-skill-package/
├── skills/source/
│   ├── frappe-core/          # Laag 1: DocType, customization
│   ├── frappe-reports/       # Laag 2: Reports & analytics
│   ├── frappe-workflow/      # Laag 3: Workflow, notifications, automation
│   ├── frappe-frontend/      # Laag 4: UI components, realtime
│   ├── frappe-web/           # Laag 5: Website, portal, web forms
│   ├── frappe-services/      # Laag 6: Files, cache, integrations, print
│   ├── frappe-ops/           # Laag 7: Bench, deployment, hosting, monitoring
│   ├── frappe-app-dev/       # Laag 8: App lifecycle, hooks, build, multi-app, publishing
│   ├── frappe-testing/       # Laag 0: Testing, CI/CD, quality
│   └── erpnext/              # Bestaande 28 skills (hernoemd van syntax/core/impl/errors/agents)
│       ├── syntax/
│       ├── core/
│       ├── impl/
│       ├── errors/
│       └── agents/
```

ERPNext wordt dan een **submodule** van het grotere Frappe skill package, precies zoals je suggereerde.
