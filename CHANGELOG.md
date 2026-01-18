# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- CONTRIBUTING.md with skill development guidelines
- SECURITY.md with vulnerability disclosure policy
- CHANGELOG.md (this file)
- GitHub issue and PR templates

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
