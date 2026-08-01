# Requirements Traceability Matrix

**System:** Regent College London HR Management RESTful API  
**Assessment:** SWE7301 Assessment 2  

---

| Req ID | Business / Functional Requirement | API Endpoint / Module | Implementation Layer | Automated Test Suite Target |
|---|---|---|---|---|
| **REQ-01** | User authentication with JWT & Argon2 hashing | `POST /api/v1/auth/login` | `core/security.py`, `services/authentication.py` | `tests/unit/test_security.py`, `tests/system/test_auth_api.py` |
| **REQ-02** | Initial CLI administrator creation | `scripts/create_admin.py` | `scripts/create_admin.py` | `tests/integration/test_admin_script.py` |
| **REQ-03** | User management & Role Assignment (`ADMIN` only) | `POST/GET/PATCH /api/v1/users` | `services/users.py`, `api/v1/routes/users.py` | `tests/system/test_users_api.py` |
| **REQ-04** | Role-Based Access Control (`ADMIN`, `HR_OFFICER`, `VIEWER`) | All endpoints / `dependencies.py` | `api/dependencies.py` | `tests/unit/test_rbac.py`, `tests/system/test_rbac_api.py` |
| **REQ-05** | Department Management & active employee deletion block | `POST/GET/DELETE /api/v1/departments` | `services/departments.py` | `tests/unit/test_department_rules.py`, `tests/system/test_departments_api.py` |
| **REQ-06** | Employee Creation with unique number & work email | `POST /api/v1/employees` | `services/employees.py`, `models/employee.py` | `tests/integration/test_employee_repo.py`, `tests/system/test_employees_api.py` |
| **REQ-07** | Employee Pagination, Search, Filtering & Safe Sorting | `GET /api/v1/employees` | `repositories/employees.py` | `tests/system/test_employee_search_api.py` |
| **REQ-08** | Employee Soft Deactivation & Controlled Reactivation | `DELETE/POST /api/v1/employees/{id}/*` | `services/employees.py` | `tests/unit/test_employee_rules.py`, `tests/system/test_employee_deactivation_api.py` |
| **REQ-09** | Employment Record Management & Date Validation | `/api/v1/employees/{id}/employment-records` | `services/employment_records.py` | `tests/unit/test_employment_rules.py`, `tests/system/test_employment_records_api.py` |
| **REQ-10** | Background Check Initiation & Restricted Notes Privacy | `/api/v1/employees/{id}/background-checks` | `services/background_checks.py` | `tests/system/test_background_checks_api.py` |
| **REQ-11** | Mock Provider Integration (DBS, Home Office, Credit, Bank) | `/background-checks/{id}/execute` | `integrations/` providers & factory | `tests/unit/test_mock_providers.py`, `tests/system/test_mock_execution_api.py` |
| **REQ-12** | Deterministic Provider Scenarios (Success, Rejection, Timeout) | `BackgroundCheckExecutionRequest` | `integrations/*_provider.py` | `tests/unit/test_provider_scenarios.py` |
| **REQ-13** | HR Metrics Reporting (Headcount, Status, Expiring RTW) | `/api/v1/reports/*` | `services/reports.py` | `tests/system/test_reports_api.py` |
| **REQ-14** | Automated Immutable Audit Logging | `GET /api/v1/audit-logs` | `services/auditing.py`, DB Listeners | `tests/integration/test_audit_logging.py`, `tests/system/test_audit_api.py` |
| **REQ-15** | Database Dual-Mode (SQLite dev/test, PostgreSQL prod) | `app/db/session.py` | `db/session.py`, `docker-compose.yml` | `tests/integration/test_db_session.py` |
| **REQ-16** | System Health and Database Diagnostic Endpoints | `/health`, `/health/database`, `/version` | `api/v1/routes/health.py` | `tests/system/test_health_api.py` |
