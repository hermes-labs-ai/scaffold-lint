"""scaffold-lint — Static linter for LLM prompt scaffolds."""

__version__ = "0.1.0"

from scaffold_lint.linter import Linter, LintResult, lint_file, lint_text

__all__ = [
    "LintResult",
    "Linter",
    "__version__",
    "lint_file",
    "lint_text",
]
