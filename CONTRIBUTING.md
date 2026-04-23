# Contributing

Thanks for your interest. This is a narrow, focused linter — 7 rules on a single axis. We plan to keep it that way.

## Scope

**In-scope:** bug fixes, new rules that detect *additional* scaffold-level failure modes, better input handling, docs, test coverage.

**Out-of-scope:**

- Rule-logic analysis (contradictions, coverage gaps) — that belongs in [rule-audit](https://github.com/hermes-labs-ai/rule-audit).
- Agent-config structural analysis (tool descriptions, role hierarchy, HERM scoring) — that belongs in [lintlang](https://github.com/hermes-labs-ai/lintlang).
- Anything that adds a runtime dependency.
- Semantic understanding via LLM calls — the point of this tool is zero-inference static analysis.

Open an issue first if you're unsure.

## Development setup

```bash
git clone https://github.com/hermes-labs-ai/scaffold-lint
cd scaffold-lint
python -m venv .venv
source .venv/bin/activate          # Windows: .venv\Scripts\activate
pip install -e ".[dev]"
```

## Running the checks

```bash
ruff check .
pytest -ra
```

CI runs the same commands on Python 3.10–3.13 across Linux, macOS, and Windows.

## Adding a new rule

1. Add the detector function in `src/scaffold_lint/detectors/scaffold_rules.py`.
2. Register it in `SCAFFOLD_RULES` with a `level` (ERROR/WARN/INFO) and a `description`.
3. Add a test in `tests/test_scaffold_rules.py` that exercises the detector on (a) a prompt it should flag and (b) a prompt it should not.
4. Update `CHANGELOG.md` under `[Unreleased]`.

Rule-naming convention: `SHOUTING_SNAKE_CASE`. Short, describes the failure mode (`SCAFFOLD_TOO_LONG`, not `TOO_LONG`).

## Pull request checklist

- [ ] `ruff check .` passes
- [ ] `pytest -ra` passes
- [ ] No new runtime dependency added
- [ ] `CHANGELOG.md` updated under `[Unreleased]`
- [ ] Test added for new rules; existing tests still pass
- [ ] No backward-incompatible schema change without a major-version bump

## Filing issues

Minimum useful report: Python version, OS, exact command, the prompt text (or a minimal reproducer), observed output, expected output.

## Code of conduct

See [CODE_OF_CONDUCT.md](CODE_OF_CONDUCT.md).

## License

By contributing, you agree that your contributions are licensed under the MIT License (see [LICENSE](LICENSE)).
