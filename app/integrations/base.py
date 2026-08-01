from abc import ABC, abstractmethod
from datetime import date
from enum import Enum
from typing import Any, Dict, Optional

from pydantic import BaseModel

from app.models.background_check import CheckStatus


class ScenarioType(str, Enum):
    APPROVED = "approved"
    REJECTED = "rejected"
    REVIEW_REQUIRED = "review_required"
    UNAVAILABLE = "unavailable"
    TIMEOUT = "timeout"


class CheckProviderResult(BaseModel):
    provider_name: str
    request_identifier: str
    status: CheckStatus
    provider_reference: Optional[str] = None
    completion_date: Optional[date] = None
    expiry_date: Optional[date] = None
    notes: Optional[str] = None
    error_code: Optional[str] = None
    raw_payload: Optional[Dict[str, Any]] = None


class BaseCheckProvider(ABC):
    """Abstract base interface for background check provider adapters."""

    @property
    @abstractmethod
    def provider_name(self) -> str:
        """Name of the external provider integration."""
        pass

    @abstractmethod
    def execute_check(
        self,
        employee_data: Dict[str, Any],
        scenario: ScenarioType = ScenarioType.APPROVED,
    ) -> CheckProviderResult:
        """Executes a simulated background check for a specific controlled scenario."""
        pass
