# Regent College London — HR Management RESTful API

**Module:** SWE7301 Contemporary Software Engineering Practices  
**Assessment:** Assessment 2 — Agile Project Development  
**Institution:** Regent College London HR Team Scenario  
**Target Submission Date:** August 8, 2026  

---

## Executive Project Summary

This project delivers a complete, production-grade, multi-tenant RESTful API backend engineered in Python (FastAPI) for Regent College London’s Human Resource Management System. It manages the complete employee lifecycle—including department allocation, job history tracking, role-based access control (RBAC), immutable audit logging, HR analytics reporting, and deterministic mock integrations with third-party background verification agencies (Disclosure and Barring Service - DBS, UK Home Office Right to Work, Credit Rating Agencies, and Commercial Banks for Confirmation of Payee verification).

---

## Feature Summary

- **Layered Architecture:** 5-tier decoupled flow (`Routes` ➔ `Schemas` ➔ `Services` ➔ `Repositories` / `Integrations` ➔ `Database Models`).
- **Security & Authentication:** Password hashing using Argon2 (`pwdlib`), signed JSON Web Tokens (`PyJWT`) with configurable expiry, and least-privilege Role-Based Access Control (`ADMIN`, `HR_OFFICER`, `VIEWER`).
- **Department & Employee Lifecycle:** Unique employee numbers & work emails, paginated listing with multi-field search, filtering, allowlisted sorting, and soft deactivation (`is_active = False`, status `TERMINATED`, `deactivated_at` timestamp).
- **Employment History:** Detailed employment records tracking job titles, employment types, salary bands, start/end dates, and manager relationships.
- **Deterministic Mock Integrations:** Common adapter interface (`BaseCheckProvider`) and Factory pattern supporting 5 controlled demonstration scenarios (`approved`, `rejected`, `review_required`, `unavailable`, `timeout`).
- **Restricted Notes Privacy:** Automatic sanitization filtering sensitive background-check notes for `VIEWER` role users.
- **HR Analytics Reporting:** Dashboard summary statistics, department headcount breakdown, status distribution, outstanding check tracking, and expiring Right to Work alerts.
- **Immutable Audit Logging:** System-wide audit event logging for all state mutations without exposing endpoints for audit modification or deletion.
- **Automated Testing & Quality:** 30 automated Pytest tests across unit, integration, and system levels achieving ≥85% statement code coverage and zero Ruff linting errors.
- **Dual-Database & Containerization:** Dual support for local SQLite development and PostgreSQL containerization via Docker Compose.

---

## Technology Stack

- **Core Backend:** Python 3.13 / FastAPI 0.111+
- **ASGI Application Server:** Uvicorn
- **ORM & Database Abstraction:** SQLAlchemy 2.x
- **Schema Migrations:** Alembic
- **Data Validation & Settings:** Pydantic v2 & Pydantic Settings
- **Password Hashing:** `pwdlib` with Argon2
- **Authentication Tokens:** PyJWT (HS256)
- **Databases:** PostgreSQL 16 (Assessed Compose Mode) / SQLite 3 (Local Dev & Pytest)
- **Testing & Quality:** Pytest 8.x, `pytest-cov`, HTTPX / FastAPI TestClient, Ruff linter
- **Containerization & CI:** Docker, Docker Compose, GitHub Actions (`.github/workflows/test.yml`)
- **API Demonstration:** Swagger UI (`/docs`), ReDoc (`/redoc`), Postman Collection (`postman/`)

---

## Folder Structure

```
.
├── app/
│   ├── api/
│   │   ├── dependencies.py              # Auth & RBAC dependency injection
│   │   └── v1/
│   │       ├── router.py                # API v1 root router
│   │       └── routes/                  # Controller endpoints
│   │           ├── audit_logs.py
│   │           ├── auth.py
│   │           ├── background_checks.py
│   │           ├── departments.py
│   │           ├── employees.py
│   │           ├── employment_records.py
│   │           ├── health.py
│   │           ├── reports.py
│   │           └── users.py
│   ├── core/                            # Configuration, security, exceptions & logging
│   │   ├── config.py
│   │   ├── exceptions.py
│   │   ├── logging.py
│   │   └── security.py
│   ├── db/                              # Database session, base models & seeders
│   │   ├── base.py
│   │   └── session.py
│   ├── integrations/                    # Mock provider adapters & factory pattern
│   │   ├── bank_provider.py
│   │   ├── base.py
│   │   ├── credit_provider.py
│   │   ├── dbs_provider.py
│   │   ├── home_office_provider.py
│   │   └── provider_factory.py
│   ├── models/                          # SQLAlchemy 2.x ORM entities
│   │   ├── audit_log.py
│   │   ├── background_check.py
│   │   ├── department.py
│   │   ├── employee.py
│   │   ├── employment_record.py
│   │   ├── external_request.py
│   │   └── user.py
│   ├── repositories/                    # Data Access Layer
│   │   ├── audit_logs.py
│   │   ├── background_checks.py
│   │   ├── departments.py
│   │   ├── employees.py
│   │   ├── employment_records.py
│   │   └── users.py
│   ├── schemas/                         # Pydantic v2 DTO request/response schemas
│   └── services/                        # Business logic & domain rules engine
├── alembic/                             # Alembic database migration scripts
├── docs/                                # Technical architecture, ATDD testing & diagrams
├── postman/                             # Postman collection and local environment
├── scripts/                             # CLI scripts (create_admin.py, seed_demo_data.py)
├── tests/                               # Pytest suite (unit/, integration/, system/)
├── .env.example                         # Environment configuration template
├── .github/workflows/test.yml          # GitHub Actions CI workflow
├── docker-compose.yml                   # Docker Compose multi-container setup
├── Dockerfile                           # Production API Docker container recipe
├── pytest.ini                           # Pytest configuration
├── requirements.txt                     # Production dependencies
├── requirements-dev.txt                 # Development & test dependencies
├── ruff.toml                            # Ruff code quality linter settings
└── README.md                            # Main project documentation
```

---

## Local Setup & Quick Start (Mode A: SQLite Beginner Mode)

### 1. Prerequisites
- Python 3.12+ (Python 3.13 supported)
- Git

### 2. Create Virtual Environment & Install Dependencies
```bash
# Clone or navigate to the workspace directory
cd "/Users/sp/Documents/Assignments/Sagar/Contemporary Software Engineering Practices/Assignment 2/Code"

# Create local Python virtual environment
python3 -m venv .venv

# Activate virtual environment
source .venv/bin/activate  # On macOS/Linux
# .venv\Scripts\activate   # On Windows PowerShell

# Upgrade pip and install development dependencies
pip install --upgrade pip
pip install -r requirements-dev.txt
```

### 3. Environment Configuration
Copy the `.env.example` file to `.env`:
```bash
cp .env.example .env
```

### 4. Run Alembic Database Migrations
Apply the initial schema migration to create local SQLite database tables (`hr_management.db`):
```bash
alembic upgrade head
```

### 5. Create Initial Superadmin User
Run the CLI script to create the initial system administrator:
```bash
python scripts/create_admin.py
```
*Default Admin Credentials:*  
- **Email:** `admin@regent.ac.uk`  
- **Password:** `AdminPassword123!`  

### 6. Populate Synthetic Demonstration Data
Seed the database with departments, HR officer, viewer users, and synthetic employee records:
```bash
python scripts/seed_demo_data.py
```
*Seeded Credentials:*  
- **HR Officer:** `hr.officer@regent.ac.uk` / `HrPassword123!`  
- **Viewer:** `viewer@regent.ac.uk` / `ViewerPassword123!`  

### 7. Launch Uvicorn Development Server
```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```
Access the interactive OpenAPI documentation in your browser:  
- **Swagger UI:** `http://localhost:8000/docs`  
- **ReDoc:** `http://localhost:8000/redoc`  

---

## Docker Compose Execution (Mode B: Assessed Demonstration Mode)

To run the complete production stack (PostgreSQL database container + API container):

```bash
# Start Docker Compose in detached mode
docker-compose up --build -d

# View application logs
docker-compose logs -f api

# Stop and tear down containers
docker-compose down -v
```

The API container will automatically wait for PostgreSQL healthiness, run Alembic migrations, create the superadmin user, seed synthetic demo data, and start Uvicorn on `http://localhost:8000`.

---

## Verification & Testing Commands

### 1. Virtual Environment Activation (Required once per terminal session)
```bash
source .venv/bin/activate
```

### 2. Run Full Pytest Suite
```bash
# With activated virtual environment:
pytest -v

# Or directly via virtual environment path:
.venv/bin/pytest -v
```

### 3. Execute Test Coverage Report
```bash
# With activated virtual environment:
pytest --cov=app --cov-report=term-missing

# Or directly via virtual environment path:
.venv/bin/pytest --cov=app --cov-report=term-missing
```

### 4. Run Ruff Code Quality Linting
```bash
# With activated virtual environment:
ruff check app tests

# Or directly via virtual environment path:
.venv/bin/ruff check app tests
```

---

## Role-Based Access Control (RBAC) Matrix

| Operation / Feature | ADMIN | HR_OFFICER | VIEWER | Unauthenticated |
|---|---|---|---|---|
| Health & Version Checks (`/health`, `/version`) | Yes | Yes | Yes | Yes |
| Authentication (`/auth/login`, `/auth/me`) | Yes | Yes | Yes | Public Login |
| System User Management (`/users/*`) | Yes | No | No | No |
| Create / Edit / Delete Department | Yes | No | No | No |
| View Departments & Employees | Yes | Yes | Yes | No |
| Create / Edit Employee | Yes | Yes | No | No |
| Soft Deactivate / Reactivate Employee | Yes | No | No | No |
| Employment Records Management | Yes | Yes | Read Only | No |
| Initiate / Execute Background Checks | Yes | Yes | No | No |
| View Background Check Restricted Notes | Yes | Yes | **Filtered (Hidden)** | No |
| HR Analytics Reports (`/reports/*`) | Yes | Yes | No | No |
| View Immutable Audit Logs (`/audit-logs`) | Yes | No | No | No |

---

## Sample Demonstration Flow (5-10 Minute Demonstration)

1. **Health Verification:** Call `GET http://localhost:8000/health` (Returns `200 OK`, `status="healthy"`).
2. **Administrator Login:** Call `POST http://localhost:8000/api/v1/auth/login` with `admin@regent.ac.uk` / `AdminPassword123!`. Copy `access_token`.
3. **Authenticate Swagger / Postman:** Set `Authorization: Bearer <access_token>`.
4. **Create Department:** Call `POST /api/v1/departments` with name `"Cyber Security"`.
5. **Create Employee:** Call `POST /api/v1/employees` with employee number `"EMP-3001"`, allocating to Cyber Security.
6. **Add Employment Record:** Call `POST /api/v1/employees/{id}/employment-records`.
7. **Initiate Background Check:** Call `POST /api/v1/employees/{id}/background-checks` with `check_type="DBS"`.
8. **Execute Mock Simulation:** Call `POST /api/v1/background-checks/{check_id}/execute` with `scenario="approved"`.
9. **Verify Privacy:** Login as `viewer@regent.ac.uk`, call `GET /api/v1/background-checks/{check_id}` (Verify `restricted_notes` is `null`).
10. **View Audit Trail:** Login as `admin@regent.ac.uk`, call `GET /api/v1/audit-logs` to inspect the recorded audit trail.

---

## Academic Disclaimers, Security Warnings & Limitations

> [!WARNING]
> **Academic Prototype & Mock Integration Notice**  
> This application is an academic backend prototype developed for SWE7301 Assessment 2 at Regent College London. All external integrations (DBS, Home Office, Credit Agency, Bank Verification) are simulated using mock adapters. No real government or financial services are contacted, and only synthetic demonstration data is processed.

> [!IMPORTANT]
> **Security & Compliance Boundary**  
> Passwords are hashed using Argon2 and JWT tokens are cryptographically signed using HS256. While GDPR-aware data minimisation rules are demonstrated (e.g., restricted notes filtering, soft employee deactivation), full legal production compliance would require enterprise Single Sign-On (SSO/SAML), hardware security modules (HSM), and formal organizational data processing controls.

---

## Troubleshooting Guide

- **Issue:** `ModuleNotFoundError: No module named 'app'` when running Alembic.  
  *Fix:* Ensure you execute Alembic from the workspace root where `alembic.ini` is located, or set `export PYTHONPATH=.`.
- **Issue:** `ImportError: email-validator is not installed`.  
  *Fix:* Run `.venv/bin/pip install email-validator` (included in `requirements.txt`).
- **Issue:** `Port 8000 is already in use`.  
  *Fix:* Kill any running Uvicorn process (`pkill -f uvicorn`) or run on port 8001: `uvicorn app.main:app --port 8001`.
