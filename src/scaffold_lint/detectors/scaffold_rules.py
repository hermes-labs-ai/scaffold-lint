"""Scaffold-specific lint rules for LLM prompt analysis.

7 rules derived from Hermes Labs prompt-linter prototype:
  TASK_DESC_MISSING        ERROR  — no clear task description
  SCAFFOLD_STACKING        WARN   — multiple techniques detected (subadditive)
  SCAFFOLD_TOO_LONG        WARN   — >500 tokens (diminishing returns)
  ABSTRACT_NO_SIZE_CHECK   WARN   — metaphorical language without model size
  CONFIDENCE_NO_CALIBRATION WARN  — confidence without bias context
  CONTRASTIVE_DETECTED     INFO   — contrastive patterns (FP-heavy note)
  SCAFFOLD_OVERREACH       WARN   — scaffold doing task's job
"""

from __future__ import annotations

import re

from scaffold_lint.detectors.base import BaseDetector, Issue, Level

# Registry: rule_id -> {level, description}
SCAFFOLD_RULES: dict[str, dict[str, str]] = {
    "TASK_DESC_MISSING": {
        "level": "ERROR",
        "description": "No clear task description. Use an explicit task statement or imperative verb.",
    },
    "SCAFFOLD_STACKING": {
        "level": "WARN",
        "description": "Multiple scaffold techniques detected. Scaffolds are subadditive — choose one.",
    },
    "SCAFFOLD_TOO_LONG": {
        "level": "WARN",
        "description": "Scaffold exceeds 500 estimated tokens. Diminishing returns beyond this threshold.",
    },
    "ABSTRACT_NO_SIZE_CHECK": {
        "level": "WARN",
        "description": "Metaphorical/abstract language without model size context. Fails on small models (<2B).",
    },
    "CONFIDENCE_NO_CALIBRATION": {
        "level": "WARN",
        "description": "Confidence language without calibration context. Specify FP/FN bias first.",
    },
    "CONTRASTIVE_DETECTED": {
        "level": "INFO",
        "description": "Contrastive NOT scaffold detected. Only helps with FP-heavy models — measure bias first.",
    },
    "SCAFFOLD_OVERREACH": {
        "level": "WARN",
        "description": (
            "Heavy scaffolding with weak task description. "
            "Task desc does 85% of the work — clarify it first."
        ),
    },
}


class ScaffoldDetector(BaseDetector):
    """Runs all 7 scaffold-specific lint rules against a prompt."""

    def detect(self, text: str) -> list[Issue]:
        issues: list[Issue] = []
        lowered = text.lower()

        issues.extend(self._check_task_description(lowered))
        issues.extend(self._check_scaffold_tokens(text))
        issues.extend(self._check_scaffold_stacking(lowered))
        issues.extend(self._check_abstract_language(lowered))
        issues.extend(self._check_confidence_without_calibration(lowered))
        issues.extend(self._check_contrastive_patterns(lowered))
        issues.extend(self._check_scaffold_overreach(lowered))

        return issues

    # ------------------------------------------------------------------ #
    # Individual rule checks
    # ------------------------------------------------------------------ #

    def _check_task_description(self, lowered: str) -> list[Issue]:
        task_keywords = [
            r"task:", r"your task", r"instructions?:", r"objective:",
            r"output:", r"classify", r"summarize", r"extract",
            r"analyze", r"explain", r"generate", r"provide",
        ]
        has_keyword = any(re.search(kw, lowered) for kw in task_keywords)
        has_imperative = bool(re.search(
            r"^(classify|summarize|extract|analyze|explain|generate|provide|"
            r"return|list|identify|find|create|write|build)\b",
            lowered, re.MULTILINE,
        ))
        if not (has_keyword or has_imperative):
            return [Issue(
                level=Level.ERROR,
                rule="TASK_DESC_MISSING",
                message=(
                    'No clear task description found. '
                    'Start with explicit task: "Your task is to..." or imperative verb.'
                ),
            )]
        return []

    def _check_scaffold_tokens(self, text: str) -> list[Issue]:
        # Heuristic: word count + parenthetical structure
        estimated = len(text.split()) + len(re.findall(r"\([^)]*\)", text))
        if estimated > 500:
            return [Issue(
                level=Level.WARN,
                rule="SCAFFOLD_TOO_LONG",
                message=(
                    f"Estimated {estimated} tokens (>500). "
                    "Scaffolds have diminishing returns beyond 500 tokens."
                ),
            )]
        return []

    def _check_scaffold_stacking(self, lowered: str) -> list[Issue]:
        scaffold_patterns: dict[str, str] = {
            "contrastive":  r"\b(contrastive|contrast|vs|versus|negative|incorrect)\b",
            "evidential":   r"\b(evidence|reason|because|korean evidential|citation)\b",
            "metaphorical": r"\b(like|as if|imagine|metaphor|analogy)\b",
            "nonsense":     r"\b(nonsense|silly|absurd|ridiculous)\b",
            "step_by_step": r"\b(step|step-by-step|reasoning|chain of thought|cot)\b",
            "format":       r"\b(format|json|xml|structured|template)\b",
        }
        detected = [
            name for name, pattern in scaffold_patterns.items()
            if re.search(pattern, lowered)
        ]
        if len(detected) > 1:
            return [Issue(
                level=Level.WARN,
                rule="SCAFFOLD_STACKING",
                message=(
                    f"Multiple scaffold techniques detected: {', '.join(detected)}. "
                    "Scaffolds are subadditive — choose one."
                ),
            )]
        return []

    def _check_abstract_language(self, lowered: str) -> list[Issue]:
        abstract_patterns = [
            r"\b(imagine|envision|picture|conceptually|abstractly|metaphor|analogy)\b",
            r"\bas if\b",
            r"\blike a\b",
        ]
        has_abstract = any(re.search(p, lowered) for p in abstract_patterns)
        if not has_abstract:
            return []
        has_size = bool(re.search(
            r"\b(model size|2b|4b|7b|14b|small model|large model|parameters?)\b", lowered
        ))
        if not has_size:
            return [Issue(
                level=Level.WARN,
                rule="ABSTRACT_NO_SIZE_CHECK",
                message=(
                    "Abstract/metaphorical language detected but no model size check. "
                    "Metaphorical scaffolds fail on small models (<2B)."
                ),
            )]
        return []

    def _check_confidence_without_calibration(self, lowered: str) -> list[Issue]:
        confidence_patterns = [
            r"\b(confidence|certain|sure|definitely|absolutely|guarantee)\b",
            r"\b(high confidence|low confidence)\b",
        ]
        calibration_patterns = [
            r"\b(calibrat|bias|fp|fn|false positive|false negative|accuracy|precision|recall)\b",
        ]
        has_confidence = any(re.search(p, lowered) for p in confidence_patterns)
        has_calibration = any(re.search(p, lowered) for p in calibration_patterns)
        if has_confidence and not has_calibration:
            return [Issue(
                level=Level.WARN,
                rule="CONFIDENCE_NO_CALIBRATION",
                message=(
                    "Confidence language used without calibration context. "
                    "Specify FP/FN bias before using confidence scores."
                ),
            )]
        return []

    def _check_contrastive_patterns(self, lowered: str) -> list[Issue]:
        contrastive_patterns = [
            r"\b(contrastive|contrast|vs|versus|incorrect|wrong|bad example|anti-pattern)\b",
        ]
        if any(re.search(p, lowered) for p in contrastive_patterns):
            return [Issue(
                level=Level.INFO,
                rule="CONTRASTIVE_DETECTED",
                message=(
                    "Contrastive NOT scaffold detected. "
                    "Note: Only helps with FP-heavy models — measure bias first."
                ),
            )]
        return []

    def _check_scaffold_overreach(self, lowered: str) -> list[Issue]:
        scaffold_heavy = bool(re.search(
            r"\b(step|reason|example|context|format|structure|provide)\b", lowered
        ))
        weak_task = bool(re.search(
            r"\b(handle|do it|make it|handle this|deal with|take care of)\b", lowered
        ))
        if scaffold_heavy and weak_task:
            return [Issue(
                level=Level.WARN,
                rule="SCAFFOLD_OVERREACH",
                message=(
                    "Heavy scaffolding detected but weak task description. "
                    "Task description does 85% of the work — clarify it first."
                ),
            )]
        return []
