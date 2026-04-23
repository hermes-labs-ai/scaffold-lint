# scaffold-lint

**Static linter for LLM prompt scaffolds.** Catches oversized scaffolds, incompatible technique mixes, and scaffolding that's doing your task description's job.

[![PyPI](https://img.shields.io/pypi/v/scaffold-lint.svg)](https://pypi.org/project/scaffold-lint/)
[![Python](https://img.shields.io/pypi/pyversions/scaffold-lint.svg)](https://pypi.org/project/scaffold-lint/)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![CI](https://github.com/hermes-labs-ai/scaffold-lint/actions/workflows/ci.yml/badge.svg)](https://github.com/hermes-labs-ai/scaffold-lint/actions/workflows/ci.yml)
[![Hermes Seal](https://img.shields.io/badge/hermes--seal-manifest%20staged-blue)](https://github.com/hermes-labs-ai/scaffold-lint)

If you're scaffolding an LLM prompt with step-by-step + evidential + format constraints all at once and wondering whether it's helping or hurting — this tells you.

## Pain

- Your prompt is 1,500 tokens because every review cycle added "just one more" scaffold.
- You mixed evidential ("cite your sources") + step-by-step + strict format — all three are fighting each other and small models collapse.
- You wrote metaphorical scaffolding ("think like a senior engineer") that works on Opus and silently fails on a 2B local model.
- You added `NOT` / contrastive instructions as a false-positive fix but never measured whether the model was FP-heavy to begin with.
- You're scaffolding heavily because the task description is vague — but the task description does ~85% of the work and no amount of scaffolding fixes that.

## Install

```bash
pip install scaffold-lint
```

Python 3.10+. Zero runtime dependencies (stdlib only).

## Quick start

```bash
scaffold-lint lint system_prompt.md
```

Real output against a 1,041-token scaffold-heavy prompt:

```
scaffold-lint — system_prompt.md
────────────────────────────────────────────────────────────
  [WARN] SCAFFOLD_TOO_LONG: Estimated 1041 tokens (>500). Scaffolds have diminishing returns beyond 500 tokens.
  [WARN] SCAFFOLD_STACKING: Multiple scaffold techniques detected: evidential, step_by_step, format. Scaffolds are subadditive — choose one.

  0 error(s), 2 warning(s), 0 info(s)
```

List all detectors:

```bash
scaffold-lint rules
```

```
RULE                           LEVEL    DESCRIPTION
───────────────────────────────────────────────────────────────────────────
ABSTRACT_NO_SIZE_CHECK         WARN     Metaphorical/abstract language without model size context. Fails on small models (<2B).
CONFIDENCE_NO_CALIBRATION      WARN     Confidence language without calibration context. Specify FP/FN bias first.
CONTRASTIVE_DETECTED           INFO     Contrastive NOT scaffold detected. Only helps with FP-heavy models — measure bias first.
SCAFFOLD_OVERREACH             WARN     Heavy scaffolding with weak task description. Task desc does 85% of the work — clarify it first.
SCAFFOLD_STACKING              WARN     Multiple scaffold techniques detected. Scaffolds are subadditive — choose one.
SCAFFOLD_TOO_LONG              WARN     Scaffold exceeds 500 estimated tokens. Diminishing returns beyond this threshold.
TASK_DESC_MISSING              ERROR    No clear task description. Use an explicit task statement or imperative verb.

7 rules total
```

## Library usage

```python
from scaffold_lint import lint_text, lint_file

result = lint_text("You are an expert engineer. Think step-by-step. Cite sources. Output JSON only.")
for issue in result.issues:
    print(f"{issue.level.value}: {issue.rule}: {issue.message}")
```

## What each rule flags

| Rule | Level | Fires when |
|---|---|---|
| `TASK_DESC_MISSING` | ERROR | No clear imperative task statement. The prompt is all scaffolding, no instruction. |
| `SCAFFOLD_TOO_LONG` | WARN | Scaffold exceeds ~500 estimated tokens. Returns diminish past that. |
| `SCAFFOLD_STACKING` | WARN | 2+ scaffold techniques (evidential + step-by-step + format + chain-of-thought) mixed in the same prompt. They're subadditive — pick one. |
| `SCAFFOLD_OVERREACH` | WARN | Heavy scaffolding applied to a prompt with a weak task description. Fix the task statement before adding scaffolding. |
| `ABSTRACT_NO_SIZE_CHECK` | WARN | Metaphorical scaffolding ("think like a…") without model-size context. Breaks on local models under 2B. |
| `CONFIDENCE_NO_CALIBRATION` | WARN | "Be confident / be accurate" language without a calibration direction (FP-heavy vs FN-heavy). |
| `CONTRASTIVE_DETECTED` | INFO | Contrastive `NOT` patterns detected. Only helps on FP-heavy models; measure bias before keeping them. |

## When to use it

- You're maintaining an LLM prompt that grew organically over many edits.
- You're deploying to multiple model tiers (Opus / Sonnet / Haiku / local) and need to flag scaffolding that only works on the big ones.
- You want a CI gate that catches scaffold bloat before it hits production.
- You're auditing someone else's prompt and need a structured diagnostic.

## When not to use it

- Single-turn chat where the "prompt" is just a question — there's no scaffold to lint.
- Non-English prompts — the rule heuristics are English-only today.
- Deep semantic analysis of rules inside the prompt (use [**rule-audit**](https://github.com/hermes-labs-ai/rule-audit) for that).
- Structural analysis of agent configs with tool descriptions and role hierarchies (use [**lintlang**](https://github.com/hermes-labs-ai/lintlang) for that).

scaffold-lint, lintlang, and rule-audit each analyze a different axis of the same prompt. On any real system prompt, running all three typically produces zero-overlap findings.

## Running the tests

```bash
git clone https://github.com/hermes-labs-ai/scaffold-lint
cd scaffold-lint
pip install -e ".[dev]"
pytest
```

31 tests. Zero runtime dependencies; `pytest` and `ruff` only for development.

## License

MIT — see [LICENSE](LICENSE).

---

## About Hermes Labs

[Hermes Labs](https://hermes-labs.ai) builds AI audit infrastructure for enterprise AI systems — EU AI Act readiness, ISO 42001 evidence bundles, continuous compliance monitoring, agent-level risk testing. We work with teams shipping AI into regulated environments.

**Our OSS philosophy — read this if you're deciding whether to depend on us:**

- **Everything we release is free, forever.** MIT or Apache-2.0. No "open core," no SaaS tier upsell, no paid version with the features you actually need. You can run this repo commercially, without talking to us.
- **We open-source our own infrastructure.** The tools we release are what Hermes Labs uses internally — we don't publish demo code, we publish production code.
- **We sell audit work, not licenses.** If you want an ANNEX-IV pack, an ISO 42001 evidence bundle, gap analysis against the EU AI Act, or agent-level red-teaming delivered as a report, that's at [hermes-labs.ai](https://hermes-labs.ai). If you just want the code to run it yourself, it's right here.

**The Hermes Labs OSS audit stack** (public, production-grade, no SaaS):

**Static audit** (before deployment)
- [**lintlang**](https://github.com/hermes-labs-ai/lintlang) — Static linter for AI agent configs, tool descriptions, system prompts. HERM v1.1 scoring + H1-H7 structural detectors. `pip install lintlang`
- [**rule-audit**](https://github.com/hermes-labs-ai/rule-audit) — Static prompt audit — contradictions, coverage gaps, priority ambiguities, absoluteness issues
- [**intent-verify**](https://github.com/hermes-labs-ai/intent-verify) — Repo intent verification + spec-drift checks

**Runtime observability** (while the agent runs)
- [**little-canary**](https://github.com/hermes-labs-ai/little-canary) — Prompt injection detection via sacrificial canary-model probes
- [**suy-sideguy**](https://github.com/hermes-labs-ai/suy-sideguy) — Runtime policy guard — user-space enforcement + forensic reports
- [**colony-probe**](https://github.com/hermes-labs-ai/colony-probe) — Prompt confidentiality audit — detects system-prompt reconstruction

**Regression & scoring** (to prove what changed)
- [**hermes-jailbench**](https://github.com/hermes-labs-ai/hermes-jailbench) — Jailbreak regression benchmark. `pip install hermes-jailbench`
- [**agent-convergence-scorer**](https://github.com/hermes-labs-ai/agent-convergence-scorer) — Score how similar N agent outputs are. `pip install agent-convergence-scorer`

**Supporting infra**
- [**claude-router**](https://github.com/hermes-labs-ai/claude-router) · [**zer0dex**](https://github.com/hermes-labs-ai/zer0dex) · [**forgetted**](https://github.com/hermes-labs-ai/forgetted) · [**quick-gate-python**](https://github.com/hermes-labs-ai/quick-gate-python) · [**quick-gate-js**](https://github.com/hermes-labs-ai/quick-gate-js) · [**repo-audit**](https://github.com/hermes-labs-ai/repo-audit)

Natural pairing: `scaffold-lint` catches *how much* scaffolding you have. `lintlang` catches *how well-structured* it is. `rule-audit` catches *what the rules inside it contradict*. Run all three in CI.

---

Built by [Hermes Labs](https://hermes-labs.ai) · [@roli-lpci](https://github.com/roli-lpci)
