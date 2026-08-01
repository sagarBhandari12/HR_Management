from fastapi import APIRouter

from app.api.v1.routes import (
    audit_logs,
    auth,
    background_checks,
    departments,
    employees,
    employment_records,
    health,
    reports,
    users,
)

api_router = APIRouter()

# Include all feature routes
api_router.include_router(auth.router)
api_router.include_router(users.router)
api_router.include_router(departments.router)
api_router.include_router(employees.router)
api_router.include_router(employment_records.router)
api_router.include_router(background_checks.router)
api_router.include_router(reports.router)
api_router.include_router(audit_logs.router)
api_router.include_router(health.router)
