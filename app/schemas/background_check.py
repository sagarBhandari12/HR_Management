from datetime import date, datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field

from app.integrations.base import ScenarioType
from app.models.background_check import CheckStatus, CheckType


class BackgroundCheckCreate(BaseModel):
    check_type: CheckType = Field(..., json_schema_extra={"example": CheckType.DBS})
    restricted_notes: Optional[str] = Field(None, json_schema_extra={"example": "Initial pre-employment check request"})


class BackgroundCheckExecutionRequest(BaseModel):
    scenario: ScenarioType = Field(default=ScenarioType.APPROVED, json_schema_extra={"example": ScenarioType.APPROVED})


class BackgroundCheckUpdate(BaseModel):
    status: Optional[CheckStatus] = None
    provider_reference: Optional[str] = Field(None, json_schema_extra={"example": "DBS-MANUAL-REF-001"})
    expiry_date: Optional[date] = None
    restricted_notes: Optional[str] = None


class BackgroundCheckResponse(BaseModel):
    id: int
    employee_id: int
    check_type: CheckType
    status: CheckStatus
    requested_at: datetime
    completed_at: Optional[datetime] = None
    provider_reference: Optional[str] = None
    expiry_date: Optional[date] = None
    restricted_notes: Optional[str] = None  # Will be sanitized to None for VIEWER role
    created_by: Optional[int] = None
    updated_by: Optional[int] = None
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
