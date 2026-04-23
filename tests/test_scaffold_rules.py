"""Tests for the 7 scaffold-specific lint rules."""

from __future__ import annotations

import pytest

from scaffold_lint.detectors.base import Level
from scaffold_lint.detectors.scaffold_rules import ScaffoldDetector
from scaffold_lint.linter import lint_text


@pytest.fixture
def detector() -> ScaffoldDetector:
    return ScaffoldDetector()


# ──────────────────────────────────────────────
# TASK_DESC_MISSING
# ──────────────────────────────────────────────

class TestTaskDescMissing:
    def test_triggers_on_vague_prompt(self, detector):
        issues = detector.detect("You are a helpful assistant. Be nice.")
        rules = [i.rule for i in issues]
        assert "TASK_DESC_MISSING" in rules

    def test_passes_with_task_keyword(self, detector):
        issues = detector.detect("Your task is to classify the following text.")
        rules = [i.rule for i in issues]
        assert "TASK_DESC_MISSING" not in rules

    def test_passes_with_imperative(self, detector):
        issues = detector.detect("Classify the sentiment of the following text.")
        rules = [i.rule for i in issues]
        assert "TASK_DESC_MISSING" not in rules

    def test_error_level(self, detector):
        issues = detector.detect("Just be helpful.")
        errors = [i for i in issues if i.rule == "TASK_DESC_MISSING"]
        assert errors and errors[0].level == Level.ERROR


# ──────────────────────────────────────────────
# SCAFFOLD_STACKING
# ──────────────────────────────────────────────

class TestScaffoldStacking:
    def test_triggers_on_multiple_techniques(self, detector):
        prompt = "Classify sentiment. Imagine you are a judge. Step 1: read. Format as JSON."
        issues = detector.detect(prompt)
        rules = [i.rule for i in issues]
        assert "SCAFFOLD_STACKING" in rules

    def test_no_trigger_on_single_technique(self, detector):
        issues = detector.detect("Classify the text. Format your output as JSON.")
        # Only 'format' pattern — should not trigger stacking
        rules = [i.rule for i in issues]
        assert "SCAFFOLD_STACKING" not in rules

    def test_warn_level(self, detector):
        prompt = "Classify. Imagine this. Step-by-step reasoning required."
        issues = detector.detect(prompt)
        stacking = [i for i in issues if i.rule == "SCAFFOLD_STACKING"]
        assert stacking and stacking[0].level == Level.WARN


# ──────────────────────────────────────────────
# SCAFFOLD_TOO_LONG
# ──────────────────────────────────────────────

class TestScaffoldTooLong:
    def test_triggers_on_long_prompt(self, detector):
        long_prompt = "Classify sentiment carefully and thoroughly. " * 120  # ~600 words
        issues = detector.detect(long_prompt)
        rules = [i.rule for i in issues]
        assert "SCAFFOLD_TOO_LONG" in rules

    def test_no_trigger_on_short_prompt(self, detector):
        issues = detector.detect("Classify the sentiment of this text.")
        rules = [i.rule for i in issues]
        assert "SCAFFOLD_TOO_LONG" not in rules


# ──────────────────────────────────────────────
# ABSTRACT_NO_SIZE_CHECK
# ──────────────────────────────────────────────

class TestAbstractNoSizeCheck:
    def test_triggers_on_imagine_without_size(self, detector):
        issues = detector.detect("Imagine you are a magical being who classifies sentiment.")
        rules = [i.rule for i in issues]
        assert "ABSTRACT_NO_SIZE_CHECK" in rules

    def test_no_trigger_when_size_mentioned(self, detector):
        issues = detector.detect("Imagine you are a 7b model that classifies sentiment.")
        rules = [i.rule for i in issues]
        assert "ABSTRACT_NO_SIZE_CHECK" not in rules

    def test_no_trigger_without_abstract_language(self, detector):
        issues = detector.detect("Classify the sentiment of the text.")
        rules = [i.rule for i in issues]
        assert "ABSTRACT_NO_SIZE_CHECK" not in rules

    def test_warn_level(self, detector):
        issues = detector.detect("Imagine a helpful assistant. Classify this.")
        warn = [i for i in issues if i.rule == "ABSTRACT_NO_SIZE_CHECK"]
        assert warn and warn[0].level == Level.WARN


# ──────────────────────────────────────────────
# CONFIDENCE_NO_CALIBRATION
# ──────────────────────────────────────────────

class TestConfidenceNoCalibration:
    def test_triggers_on_confidence_without_calibration(self, detector):
        issues = detector.detect(
            "Imagine you are a magical being who classifies sentiment with confidence."
        )
        rules = [i.rule for i in issues]
        assert "CONFIDENCE_NO_CALIBRATION" in rules

    def test_no_trigger_when_calibration_present(self, detector):
        issues = detector.detect(
            "Classify with confidence. Bias toward false positive reduction."
        )
        rules = [i.rule for i in issues]
        assert "CONFIDENCE_NO_CALIBRATION" not in rules

    def test_no_trigger_without_confidence_language(self, detector):
        issues = detector.detect("Classify the sentiment.")
        rules = [i.rule for i in issues]
        assert "CONFIDENCE_NO_CALIBRATION" not in rules

    def test_warn_level(self, detector):
        issues = detector.detect("Return a confidence score for each label.")
        warn = [i for i in issues if i.rule == "CONFIDENCE_NO_CALIBRATION"]
        assert warn and warn[0].level == Level.WARN


# ──────────────────────────────────────────────
# CONTRASTIVE_DETECTED
# ──────────────────────────────────────────────

class TestContrastiveDetected:
    def test_triggers_on_contrastive_language(self, detector):
        issues = detector.detect("Classify the text. Provide a correct vs incorrect label.")
        rules = [i.rule for i in issues]
        assert "CONTRASTIVE_DETECTED" in rules

    def test_no_trigger_without_contrastive(self, detector):
        issues = detector.detect("Classify the sentiment of this text.")
        rules = [i.rule for i in issues]
        assert "CONTRASTIVE_DETECTED" not in rules

    def test_info_level(self, detector):
        issues = detector.detect("Identify the wrong answer versus the correct one.")
        info = [i for i in issues if i.rule == "CONTRASTIVE_DETECTED"]
        assert info and info[0].level == Level.INFO


# ──────────────────────────────────────────────
# SCAFFOLD_OVERREACH
# ──────────────────────────────────────────────

class TestScaffoldOverreach:
    def test_triggers_on_heavy_scaffold_weak_task(self, detector):
        prompt = (
            "Provide context and structured reasoning with step-by-step examples. "
            "Handle this appropriately."
        )
        issues = detector.detect(prompt)
        rules = [i.rule for i in issues]
        assert "SCAFFOLD_OVERREACH" in rules

    def test_no_trigger_on_clear_task(self, detector):
        prompt = "Classify the sentiment. Provide step-by-step reasoning."
        issues = detector.detect(prompt)
        rules = [i.rule for i in issues]
        assert "SCAFFOLD_OVERREACH" not in rules

    def test_warn_level(self, detector):
        prompt = "Provide examples and structure. Just handle it."
        issues = detector.detect(prompt)
        warn = [i for i in issues if i.rule == "SCAFFOLD_OVERREACH"]
        assert warn and warn[0].level == Level.WARN


# ──────────────────────────────────────────────
# Integration via lint_text
# ──────────────────────────────────────────────

class TestLintTextIntegration:
    def test_hackathon_trigger_prompt(self):
        """The ship-criteria prompt must trigger ABSTRACT_NO_SIZE_CHECK + CONFIDENCE_NO_CALIBRATION."""
        result = lint_text(
            "Imagine you are a magical being who classifies sentiment with confidence"
        )
        rules = [i.rule for i in result.issues]
        assert "ABSTRACT_NO_SIZE_CHECK" in rules
        assert "CONFIDENCE_NO_CALIBRATION" in rules

    def test_result_has_issues_list(self):
        result = lint_text("You are helpful.")
        assert isinstance(result.issues, list)

    def test_clean_prompt_minimal_issues(self):
        """A well-formed prompt should not trigger TASK_DESC_MISSING."""
        result = lint_text("Classify the sentiment of the following review as positive or negative.")
        rules = [i.rule for i in result.issues]
        assert "TASK_DESC_MISSING" not in rules
