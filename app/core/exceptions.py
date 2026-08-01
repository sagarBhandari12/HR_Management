from typing import Any, Optional

from fastapi import Request, status
from fastapi.responses import JSONResponse


class BaseAppException(Exception):
    """Base exception class for application-level errors."""

    def __init__(
        self,
        message: str,
        status_code: int = status.HTTP_400_BAD_REQUEST,
        code: str = "BAD_REQUEST",
        details: Optional[Any] = None,
    ):
        self.message = message
        self.status_code = status_code
        self.code = code
        self.details = details
        super().__init__(self.message)


class NotFoundException(BaseAppException):
    def __init__(self, message: str = "Resource not found", details: Optional[Any] = None):
        super().__init__(
            message=message,
            status_code=status.HTTP_404_NOT_FOUND,
            code="NOT_FOUND",
            details=details,
        )


class ConflictException(BaseAppException):
    def __init__(self, message: str = "Resource conflict", details: Optional[Any] = None):
        super().__init__(
            message=message,
            status_code=status.HTTP_409_CONFLICT,
            code="CONFLICT",
            details=details,
        )


class UnauthorizedException(BaseAppException):
    def __init__(self, message: str = "Authentication credentials were invalid or missing"):
        super().__init__(
            message=message,
            status_code=status.HTTP_401_UNAUTHORIZED,
            code="UNAUTHORIZED",
        )


class ForbiddenException(BaseAppException):
    def __init__(self, message: str = "You do not have permission to perform this action"):
        super().__init__(
            message=message,
            status_code=status.HTTP_403_FORBIDDEN,
            code="FORBIDDEN",
        )


class UnprocessableEntityException(BaseAppException):
    def __init__(self, message: str = "Unprocessable entity", details: Optional[Any] = None):
        super().__init__(
            message=message,
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            code="UNPROCESSABLE_ENTITY",
            details=details,
        )


class ServiceUnavailableException(BaseAppException):
    def __init__(self, message: str = "External service unavailable"):
        super().__init__(
            message=message,
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            code="SERVICE_UNAVAILABLE",
        )


class GatewayTimeoutException(BaseAppException):
    def __init__(self, message: str = "External provider timeout"):
        super().__init__(
            message=message,
            status_code=status.HTTP_504_GATEWAY_TIMEOUT,
            code="GATEWAY_TIMEOUT",
        )


async def app_exception_handler(request: Request, exc: BaseAppException) -> JSONResponse:
    """Global handler for application domain exceptions."""
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": {
                "code": exc.code,
                "message": exc.message,
                "details": exc.details,
            }
        },
    )
