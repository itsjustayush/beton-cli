"""Shared domain models used by Beton commands and platform adapters."""

from dataclasses import dataclass, field
from enum import Enum
from typing import Any


class ResultStatus(str, Enum):
    SUCCESS = "success"
    DENIED = "denied"
    UNAVAILABLE = "unavailable"
    NEEDS_AUTH = "needs_auth"
    DRY_RUN = "dry_run"


@dataclass(slots=True)
class ActionResult:
    status: ResultStatus
    message: str
    detail: str | None = None
    data: dict[str, Any] = field(default_factory=dict)

    @property
    def ok(self) -> bool:
        return self.status in {ResultStatus.SUCCESS, ResultStatus.DRY_RUN}


@dataclass(slots=True)
class Capability:
    name: str
    available: bool
    detail: str = ""
