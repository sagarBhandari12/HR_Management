from typing import Optional

from pydantic import BaseModel, EmailStr, Field


class LoginRequest(BaseModel):
    email: EmailStr = Field(..., json_schema_extra={"example": "admin@regent.ac.uk"})
    password: str = Field(..., min_length=6, json_schema_extra={"example": "AdminPassword123!"})


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"
    role: str
    expires_in_seconds: int


class TokenData(BaseModel):
    sub: Optional[str] = None
    role: Optional[str] = None
