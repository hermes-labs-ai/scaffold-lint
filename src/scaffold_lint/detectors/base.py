"""Base detector class for scaffold-lint."""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum


class Level(str, Enum):
    ERROR = "ERROR"
    WARN = "WARN"
    INFO = "INFO"


@dataclass
class Issue:
    level: Level
    rule: str
    message: str
    line: int = 0

    def __str__(self) -> str:
        return f"[{self.level.value}] {self.rule}: {self.message}"


class BaseDetector:
    """Base class for all scaffold-lint detectors."""

    def detect(self, text: str) -> list[Issue]:
        raise NotImplementedError
