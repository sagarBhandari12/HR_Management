# Acceptance Test-Driven Development (ATDD) Specification

**System:** Regent College London HR Management RESTful API  
**Module:** SWE7301 Assessment 2  

---

## Acceptance Test Suite Execution Table

| Test ID | Requirement | User Story Scenario (Given / When / Then) | Preconditions | Test Steps | Expected Result | Actual Result | Status | Automated Test File |
|---|---|---|---|---|---|---|---|---|
| **AT-01** | REQ-01 | **Given** valid superadmin credentials, **When** POST `/api/v1/auth/login` is called, **Then** a signed JWT bearer token is returned. | User exists in DB | 1. Send POST `/auth/login` with email & password. | HTTP 200 OK + JWT access_token | HTTP 200 OK + JWT returned | **PASS** | `tests/system/test_auth_api.py` |
| **AT-02** | REQ-01 | **Given** invalid password, **When** POST `/api/v1/auth/login` is called, **Then** 401 Unauthorized is returned. | User exists | 1. Send POST `/auth/login` with wrong password. | HTTP 401 Unauthorized | HTTP 401 Unauthorized | **PASS** | `tests/system/test_auth_api.py` |
| **AT-03** | REQ-04 | **Given** a `VIEWER` token, **When** attempting POST `/api/v1/departments`, **Then** 403 Forbidden is returned. | Viewer user authenticated | 1. Send POST `/departments` with Viewer token. | HTTP 403 Forbidden | HTTP 403 Forbidden | **PASS** | `tests/system/test_departments_and_employees_api.py` |
| **AT-04** | REQ-06 | **Given** duplicate employee number, **When** POST `/api/v1/employees` is sent, **Then** 409 Conflict is returned. | Employee `EMP-9901` exists | 1. Send POST `/employees` with duplicate number `EMP-9901`. | HTTP 409 Conflict | HTTP 409 Conflict | **PASS** | `tests/system/test_departments_and_employees_api.py` |
| **AT-05** | REQ-05 | **Given** department with active staff, **When** DELETE `/api/v1/departments/{id}` is called, **Then** deletion is blocked. | Department has active employee | 1. Send DELETE `/departments/{id}` as Admin. | HTTP 409 Conflict | HTTP 409 Conflict | **PASS** | `tests/system/test_departments_and_employees_api.py` |
| **AT-06** | REQ-08 | **Given** an active employee, **When** DELETE `/api/v1/employees/{id}` is called, **Then** employee is soft-deactivated. | Employee active | 1. Send DELETE `/employees/{id}` as Admin. | HTTP 200 OK + `is_active=False`, `status=TERMINATED` | HTTP 200 OK + deactivated | **PASS** | `tests/system/test_departments_and_employees_api.py` |
| **AT-07** | REQ-08 | **Given** an active employee, **When** POST `/employees/{id}/reactivate` is called, **Then** 409 Conflict is returned. | Employee already active | 1. Send POST `/employees/{id}/reactivate`. | HTTP 409 Conflict | HTTP 409 Conflict | **PASS** | `tests/system/test_departments_and_employees_api.py` |
| **AT-08** | REQ-09 | **Given** `end_date` earlier than `start_date`, **When** POST employment record, **Then** 422 Unprocessable is returned. | Employee exists | 1. Send POST employment record with invalid dates. | HTTP 422 Unprocessable Entity | HTTP 422 Unprocessable Entity | **PASS** | `tests/system/test_employment_and_background_checks_api.py` |
| **AT-09** | REQ-11 | **Given** background check ID, **When** POST `/execute` with `scenario=approved`, **Then** mock provider returns APPROVED state. | Check pending | 1. Send POST `/execute` with scenario `approved`. | HTTP 200 OK + `status=APPROVED` + `provider_reference` | HTTP 200 OK + APPROVED | **PASS** | `tests/system/test_employment_and_background_checks_api.py` |
| **AT-10** | REQ-10 | **Given** background check with notes, **When** requested by `VIEWER`, **Then** `restricted_notes` is nullified. | Check has notes | 1. Send GET `/background-checks/{id}` as Viewer. | HTTP 200 OK + `restricted_notes=None` | HTTP 200 OK + restricted_notes=None | **PASS** | `tests/system/test_employment_and_background_checks_api.py` |
| **AT-11** | REQ-14 | **Given** a `VIEWER` token, **When** GET `/api/v1/audit-logs` is called, **Then** 403 Forbidden is returned. | Viewer token | 1. Send GET `/audit-logs` as Viewer. | HTTP 403 Forbidden | HTTP 403 Forbidden | **PASS** | `tests/system/test_employment_and_background_checks_api.py` |
