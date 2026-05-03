"""Validation result models and reporting helpers."""

from __future__ import annotations

import logging
from dataclasses import dataclass, field

logger = logging.getLogger(__name__)


@dataclass
class CheckResult:
    """Outcome of a single validation check."""

    name: str
    passed: bool
    message: str


@dataclass
class ValidationReport:
    """Aggregated results of all validation checks."""

    checks: list[CheckResult] = field(default_factory=list)

    @property
    def passed(self) -> int:
        return sum(1 for c in self.checks if c.passed)

    @property
    def failed(self) -> int:
        return sum(1 for c in self.checks if not c.passed)

    @property
    def all_passed(self) -> bool:
        return self.failed == 0

    def log_summary(self) -> None:
        logger.info("=" * 60)
        logger.info("VALIDATION REPORT")
        logger.info("=" * 60)
        for check in self.checks:
            status = "PASS" if check.passed else "FAIL"
            logger.info("  [%s] %s — %s", status, check.name, check.message)
        logger.info("-" * 60)
        logger.info(
            "  Total: %d checks — %d passed, %d failed",
            len(self.checks), self.passed, self.failed,
        )
        logger.info("=" * 60)
