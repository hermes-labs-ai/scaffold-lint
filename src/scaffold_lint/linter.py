"""Core linter engine for scaffold-lint."""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path

from scaffold_lint.detectors.base import Issue
from scaffold_lint.detectors.scaffold_rules import ScaffoldDetector


@dataclass
class LintResult:
    source: str
    issues: list[Issue] = field(default_factory=list)

    @property
    def errors(self) -> list[Issue]:
        from scaffold_lint.detectors.base import Level
        return [i for i in self.issues if i.level == Level.ERROR]

    @property
    def warnings(self) -> list[Issue]:
        from scaffold_lint.detectors.base import Level
        return [i for i in self.issues if i.level == Level.WARN]

    @property
    def infos(self) -> list[Issue]:
        from scaffold_lint.detectors.base import Level
        return [i for i in self.issues if i.level == Level.INFO]

    def has_errors(self) -> bool:
        return len(self.errors) > 0


class Linter:
    """Runs all registered detectors against a prompt."""

    def __init__(self) -> None:
        self._detectors = [ScaffoldDetector()]

    def lint(self, text: str, source: str = "<text>") -> LintResult:
        issues: list[Issue] = []
        for detector in self._detectors:
            issues.extend(detector.detect(text))
        return LintResult(source=source, issues=issues)


def lint_text(text: str) -> LintResult:
    """Convenience: lint a string directly."""
    return Linter().lint(text, source="<text>")


def lint_file(path: str | Path) -> LintResult:
    """Convenience: lint a file on disk."""
    p = Path(path)
    text = p.read_text(encoding="utf-8")
    return Linter().lint(text, source=str(p))
