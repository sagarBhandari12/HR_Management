"""Pydantic v2 schemas package for request validation and response DTOs."""

from app.schemas.auth import LoginRequest, Token, TokenData
from app.schemas.common import ErrorResponse, PaginatedResponse
from app.schemas.department import DepartmentCreate, DepartmentResponse, DepartmentUpdate
from app.schemas.employee import EmployeeCreate, EmployeeResponse, EmployeeUpdate
from app.schemas.user import UserCreate, UserResponse, UserUpdate

__all__ = [
    "LoginRequest",
    "Token",
    "TokenData",
    "UserCreate",
    "UserUpdate",
    "UserResponse",
    "DepartmentCreate",
    "DepartmentUpdate",
    "DepartmentResponse",
    "EmployeeCreate",
    "EmployeeUpdate",
    "EmployeeResponse",
    "ErrorResponse",
    "PaginatedResponse",
]
