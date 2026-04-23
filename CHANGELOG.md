# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.1.0] — 2026-04-22

Initial public release of scaffold-lint.

### Added

- 7 scaffold-lint rules:
  - `TASK_DESC_MISSING` (ERROR) — no clear imperative task statement
  - `SCAFFOLD_TOO_LONG` (WARN) — scaffold exceeds ~500 estimated tokens
  - `SCAFFOLD_STACKING` (WARN) — 2+ scaffold techniques mixed (subadditive)
  - `SCAFFOLD_OVERREACH` (WARN) — heavy scaffolding over weak task description
  - `ABSTRACT_NO_SIZE_CHECK` (WARN) — metaphorical scaffolding without model-size context
  - `CONFIDENCE_NO_CALIBRATION` (WARN) — confidence language without calibration direction
  - `CONTRASTIVE_DETECTED` (INFO) — contrastive `NOT` patterns detected
- `scaffold-lint lint <file>` CLI with `--text`, `--json`, `--fail-on-error` flags
- `scaffold-lint rules` CLI to list all detectors
- `scaffold_lint.lint_text` / `scaffold_lint.lint_file` library API
- Python 3.10+ support
- Zero runtime dependencies (stdlib only)

### Origin

Extracted and renamed from the internal "lintlang-v2" scaffold-linter prototype
(developed during the Hermes Labs Hackathon Round 2, 2026-04-17). The `lintlang`
name was retained internally but caused a package-name collision with the canonical
[lintlang](https://github.com/roli-lpci/lintlang) (HERM + H1-H7 structural linter
for agent configs). Publishing under the new name `scaffold-lint` resolves that
collision and communicates scope more clearly.

[0.1.0]: https://github.com/roli-lpci/scaffold-lint/releases/tag/v0.1.0
