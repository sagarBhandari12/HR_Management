from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, EmailStr, Field

from app.models.user import UserRole


class UserCreate(BaseModel):
    email: EmailStr = Field(..., json_schema_extra={"example": "hr.officer@regent.ac.uk"})
    full_name: str = Field(..., min_length=2, max_length=255, json_schema_extra={"example": "Sarah Jenkins"})
    password: str = Field(..., min_length=8, json_schema_extra={"example": "SecurePassword123!"})
    role: UserRole = Field(default=UserRole.VIEWER, json_schema_extra={"example": UserRole.HR_OFFICER})


class UserUpdate(BaseModel):
    email: Optional[EmailStr] = None
    full_name: Optional[str] = Field(None, min_length=2, max_length=255)
    role: Optional[UserRole] = None
    is_active: Optional[bool] = None


class UserResponse(BaseModel):
    id: int
    email: EmailStr
    full_name: str
    role: UserRole
    is_active: bool
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
