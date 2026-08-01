# Technical Evidence Checklist

**System:** Regent College London HR Management RESTful API  
**Assessment:** SWE7301 Assessment 2 — Agile Project Development  

Use this checklist during your viva demonstration or portfolio screenshot capture session to ensure all required evidence items are captured from the running application:

---

## 1. Local Environment & Installation Evidence

- [x] **EV-01: Terminal — Python & Tooling Audit**  
  *Command:* `python3 --version && git --version && docker --version`  
  *Expected Output:* Python 3.13.x, Git 2.x, Docker 29.x.

- [x] **EV-02: Terminal — Virtual Environment & Dependency Installation**  
  *Command:* `.venv/bin/pip list`  
  *Expected Output:* List of installed packages (FastAPI, SQLAlchemy, Alembic, Pydantic, Pytest, Argon2, PyJWT).

- [x] **EV-03: Terminal — Alembic Database Migration**  
  *Command:* `.venv/bin/alembic upgrade head`  
  *Expected Output:* `Running upgrade -> 3963b9794730, Initial schema setup`.

- [x] **EV-04: Terminal — Initial Administrator Creation**  
  *Command:* `.venv/bin/python scripts/create_admin.py`  
  *Expected Output:* `[+] Initial Superadmin successfully created: Email: admin@regent.ac.uk`.

- [x] **EV-05: Terminal — Demo Data Population**  
  *Command:* `.venv/bin/python scripts/seed_demo_data.py`  
  *Expected Output:* Seeded HR Officer, Viewer, 4 Departments, and 3 Synthetic Employees.

---

## 2. API Demonstration & OpenAPI / Swagger Evidence

- [ ] **EV-06: Browser — Interactive Swagger UI Documentation**  
  *URL:* `http://localhost:8000/docs`  
  *Visual Evidence:* OpenAPI interface showing grouped tags (`Authentication`, `System Users Management`, `Department Management`, `Employee Management`, `Employment Records`, `Background Checks & Mock Integrations`, `HR Analytics & Reports`, `Audit Trails`).

- [ ] **EV-07: Browser — Swagger Bearer Authentication**  
  *Action:* Authorize via `POST /api/v1/auth/login` token using `Bearer <token>` button.

- [ ] **EV-08: Swagger — Department Creation & Active Employee Deletion Block**  
  *Action:* Execute `POST /api/v1/departments` followed by `DELETE /api/v1/departments/{id}` when employees exist (shows 409 Conflict).

- [ ] **EV-09: Swagger — Soft Deactivation & Controlled Reactivation**  
  *Action:* Execute `DELETE /api/v1/employees/{id}` (shows `is_active=false`, `status=TERMINATED`), then `POST /api/v1/employees/{id}/reactivate`.

- [ ] **EV-10: Swagger — Mock Provider Check Execution**  
  *Action:* Execute `POST /api/v1/background-checks/{id}/execute` with `scenario="approved"` and `scenario="rejected"`.

---

## 3. Automated Testing, Coverage & Quality Evidence

- [x] **EV-11: Terminal — Pytest Automated Test Suite Execution**  
  *Command:* `.venv/bin/pytest -v`  
  *Expected Output:* 30 passed tests across unit, integration, and system levels.

- [x] **EV-12: Terminal — Pytest Code Coverage Report**  
  *Command:* `.venv/bin/pytest --cov=app --cov-report=term-missing`  
  *Expected Output:* `TOTAL 85%` statement coverage.

- [x] **EV-13: Terminal — Ruff Code Quality & Syntax Inspection**  
  *Command:* `.venv/bin/ruff check app tests`  
  *Expected Output:* `All checks passed!`.

---

## 4. Postman & Docker Evidence

- [ ] **EV-14: Postman — Collection Runner Execution**  
  *Action:* Import `postman/HR_Management_API.postman_collection.json` and run full collection against `http://localhost:8000`.

- [ ] **EV-15: Docker Compose — Production Stack Build & Run**  
  *Command:* `docker-compose up --build`  
  *Expected Output:* PostgreSQL container `hr_postgres_db` healthy and API container `hr_management_api` active.
