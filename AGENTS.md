# AGENTS.md — scaffold-lint

Instructions for AI agents contributing to or using this tool.

## What this tool does

Reads an LLM prompt (file or text) and runs 7 static detectors for scaffold-level failure modes:

| Rule | Level | Catches |
|---|---|---|
| `TASK_DESC_MISSING` | ERROR | No imperative task statement |
| `SCAFFOLD_TOO_LONG` | WARN | >500 estimated tokens |
| `SCAFFOLD_STACKING` | WARN | Multiple techniques mixed (subadditive) |
| `SCAFFOLD_OVERREACH` | WARN | Heavy scaffolding, weak task desc |
| `ABSTRACT_NO_SIZE_CHECK` | WARN | Metaphorical scaffolding, no model-size context |
| `CONFIDENCE_NO_CALIBRATION` | WARN | Confidence language, no calibration direction |
| `CONTRASTIVE_DETECTED` | INFO | `NOT`-pattern scaffolds (note: FP-heavy only) |

Zero LLM calls. Python 3.10+. Zero runtime dependencies.

## When to use

- CI gate on prompt changes ("did this PR bloat the scaffold?")
- Multi-tier deployment audit ("does this scaffold break on small models?")
- Post-hoc review of a prompt that "evolved organically"

## When NOT to use

- Rule-logic analysis → use [rule-audit](https://github.com/hermes-labs-ai/rule-audit)
- Agent-config structural lint → use [lintlang](https://github.com/hermes-labs-ai/lintlang)
- Semantic understanding → this is deterministic regex/heuristic analysis

scaffold-lint, lintlang, and rule-audit analyze different axes. Run all three.

## Minimal invocation — CLI

```bash
scaffold-lint lint system_prompt.md
scaffold-lint lint --text "You are a helpful assistant. Think step-by-step. Output JSON."
scaffold-lint lint system_prompt.md --json | jq .
scaffold-lint lint system_prompt.md --fail-on-error  # exit 1 on any ERROR
scaffold-lint rules                                    # list all 7 detectors
```

## Minimal invocation — library

```python
from scaffold_lint import lint_text, lint_file

result = lint_text("Think step-by-step. Cite sources. Output JSON.")
print(result.errors, result.warnings, result.infos)
for issue in result.issues:
    print(f"{issue.level.value}: {issue.rule} — {issue.message}")
```

## Expected output shape

```json
{
  "source": "<file path or '<text>'>",
  "issue_count": 2,
  "issues": [
    {"level": "WARN", "rule": "SCAFFOLD_TOO_LONG", "message": "Estimated 1041 tokens (>500)...", "line": null},
    {"level": "WARN", "rule": "SCAFFOLD_STACKING", "message": "Multiple scaffold techniques detected...", "line": null}
  ]
}
```

## Exit codes

- `0` — success (or no ERROR-level issues, with `--fail-on-error`)
- `1` — file not found, or ERROR-level issue with `--fail-on-error`

## Known limitations

- English prompts only.
- Token count is *estimated* (split + multiplier), not BPE-exact. Threshold is 500 ± ~10%.
- `SCAFFOLD_STACKING` uses keyword heuristics; it will miss techniques that don't match the keyword list. PRs welcome.
- No line numbers in output today; `issue.line` is always `null`.
- No auto-fix mode.

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md). Scope guardrails there.

## Trust

- Staged `hermes-seal` v1 manifest at `.hermes-seal.yaml`. Signature granted out-of-band by the Hermes Labs internal sealing toolchain.
- SBOM at `sbom.cdx.json`.
- Zero runtime dependencies by design.

## About Hermes Labs

[Hermes Labs](https://hermes-labs.ai) builds AI audit infrastructure for enterprise AI systems — EU AI Act, ISO 42001, agent-level risk. We open-source what we use internally. Everything is MIT, fully free, no SaaS tier. Audit work is paid; the code is not.
