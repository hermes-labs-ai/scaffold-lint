"""CLI entry point for scaffold-lint."""

from __future__ import annotations

import argparse
import contextlib
import json
import sys
from pathlib import Path

# Force UTF-8 stdout so box-drawing characters render on Windows cp1252 consoles.
# Safe no-op on terminals that already support UTF-8.
if hasattr(sys.stdout, "reconfigure"):
    with contextlib.suppress(Exception):
        sys.stdout.reconfigure(encoding="utf-8")

from scaffold_lint import __version__
from scaffold_lint.detectors.scaffold_rules import SCAFFOLD_RULES
from scaffold_lint.linter import LintResult, lint_file, lint_text

# ANSI colours
_RED = "\033[31m"
_YELLOW = "\033[33m"
_CYAN = "\033[36m"
_RESET = "\033[0m"
_BOLD = "\033[1m"

_LEVEL_COLOR = {
    "ERROR": _RED,
    "WARN": _YELLOW,
    "INFO": _CYAN,
}


def _fmt_issue_terminal(issue) -> str:
    color = _LEVEL_COLOR.get(issue.level.value, "")
    return f"  {color}{_BOLD}[{issue.level.value}]{_RESET} {issue.rule}: {issue.message}"


def _print_result_terminal(result: LintResult) -> None:
    print(f"\n{_BOLD}scaffold-lint{_RESET} — {result.source}")
    print("─" * 60)
    if not result.issues:
        print(f"  {_CYAN}No issues found.{_RESET}")
    else:
        for issue in result.issues:
            print(_fmt_issue_terminal(issue))
    counts = f"{len(result.errors)} error(s), {len(result.warnings)} warning(s), {len(result.infos)} info(s)"
    print(f"\n  {counts}")
    print()


def _print_result_json(result: LintResult) -> None:
    output = {
        "source": result.source,
        "issue_count": len(result.issues),
        "issues": [
            {
                "level": i.level.value,
                "rule": i.rule,
                "message": i.message,
                "line": i.line,
            }
            for i in result.issues
        ],
    }
    print(json.dumps(output, indent=2))


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="scaffold-lint",
        description=(
            "Static linter for LLM prompt scaffolds — catches oversized scaffolds "
            "and incompatible technique mixes. Part of the Hermes Labs static-audit stack."
        ),
    )
    parser.add_argument("--version", action="version", version=f"scaffold-lint {__version__}")

    sub = parser.add_subparsers(dest="command")

    # ── lint command ─────────────────────────────────────────────────
    lint_parser = sub.add_parser("lint", help="Lint a prompt file or inline text")
    lint_parser.add_argument("file", nargs="?", help="Prompt file to lint")
    lint_parser.add_argument(
        "--text", "-t",
        metavar="TEXT",
        help="Lint inline text instead of a file",
    )
    lint_parser.add_argument(
        "--json",
        action="store_true",
        dest="json_output",
        help="Machine-readable JSON output",
    )
    lint_parser.add_argument(
        "--fail-on-error",
        action="store_true",
        help="Exit with code 1 if any ERROR-level issues are found",
    )

    # ── rules command ────────────────────────────────────────────────
    sub.add_parser("rules", help="List all available lint rules")

    args = parser.parse_args(argv)

    if args.command == "lint":
        return _cmd_lint(args)
    elif args.command == "rules":
        return _cmd_rules()
    else:
        parser.print_help()
        return 0


def _cmd_lint(args: argparse.Namespace) -> int:
    if args.text:
        result = lint_text(args.text)
    elif args.file:
        path = Path(args.file)
        if not path.exists():
            print(f"Error: file not found: {args.file}", file=sys.stderr)
            return 1
        result = lint_file(path)
    else:
        print("Error: provide a file path or --text TEXT", file=sys.stderr)
        return 1

    if args.json_output:
        _print_result_json(result)
    else:
        _print_result_terminal(result)

    if args.fail_on_error and result.has_errors():
        return 1
    return 0


def _cmd_rules() -> int:
    print()
    print(f"  {'RULE':<30} {'LEVEL':<8} DESCRIPTION")
    print("  " + "─" * 75)
    for rule_id, info in sorted(SCAFFOLD_RULES.items()):
        print(f"  {rule_id:<30} {info['level']:<8} {info['description']}")
    print()
    print(f"  {len(SCAFFOLD_RULES)} rules total")
    print()
    return 0


if __name__ == "__main__":
    sys.exit(main())
