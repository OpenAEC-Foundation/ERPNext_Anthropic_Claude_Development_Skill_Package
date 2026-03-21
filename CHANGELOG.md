# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [3.0.0] - 2026-03-21

### Added
- 7 new skills: frappe-core-translation, frappe-core-utils, frappe-syntax-print, frappe-syntax-query-builder, frappe-impl-workspace, frappe-core-logging, frappe-core-search
- 13 new reference files extending 12 existing skills (controls-api, tree-view, generators, print-format-decision, email-system, module-workspace-shipping, document-api-complete, custom-commands, request-lifecycle, advanced-debugging, frappe-packages, data-masking, type-stubs)

### Changed
- Total skill count: 53 → 60
- Framework coverage: ~85% → ~95%
- INDEX.md rebuilt with all 60 skills and expanded selection guide
- README.md updated with v3.0 stats

## [2.0.0] - 2026-03-20

### Added
- 25 new skills (ops, testing, agents, syntax, core, impl categories)
- All 28 existing skills fully rewritten with fresh research
- Renamed erpnext-* → frappe-* (all 28 existing skills)

### Changed
- Total skill count: 28 → 53
- Framework coverage: ~16% → ~85%
- 7 categories (added ops/, testing/)

## [1.2.0] - 2026-01-18

### Added
- CONTRIBUTING.md with skill development guidelines
- SECURITY.md with vulnerability disclosure policy
- CHANGELOG.md
- GitHub issue and PR templates
- REQUIREMENTS.md with quality criteria
- DECISIONS.md with 15 numbered architectural decisions (D-001 to D-015)
- SOURCES.md with all verified documentation URLs

### Changed
- Renamed LESSONS_LEARNED.md to LESSONS.md (workflow template alignment)
- All 28 SKILL.md frontmatters migrated to YAML folded block scalar (`>`) format

## [1.1.0] - 2026-01-18

### Added
- USAGE.md with platform-specific guides (Claude.ai, Claude Code, API)
- Complete README overhaul with quick start guide

### Changed
- All 28 skills updated for ERPNext/Frappe V16 compatibility
- Agent Skills now follow standard skill structure
- Improved validation: 28/28 skills pass all checks

### Fixed
- V16-specific syntax changes in 9 skills
- Agent SKILL.md files now under 500 lines

## [1.0.0] - 2026-01-17

### Added
- Initial release with 28 skills and agents
- 13 research documents
- 8 syntax skills (Client Scripts, Server Scripts, Hooks, Controllers, Whitelisted Methods, Jinja Templates, Scheduler, Custom App)
- 3 core skills (Database, Permissions, API Patterns)
- 8 implementation skills
- 7 error handling skills
- 2 agents (Code Review, Development)
- Full V14/V15 compatibility
- Validation tools (quick_validate.py, package_skill.py)
- Comprehensive documentation

### Notes
- Server Scripts use RestrictedPython sandbox - no imports allowed
- All code examples verified against official Frappe documentation
