# RESTful API Endpoints Inventory

**System:** Regent College London HR Management RESTful API  
**Base URL:** `http://localhost:8000/api/v1`  
**Authentication:** HTTP Bearer (JWT Header: `Authorization: Bearer <token>`)  

---

## 1. System & Health

| Method | Endpoint | Description | Auth Required | Permitted Roles |
|---|---|---|---|---|
| `GET` | `/health` | Application status & uptime | No | Public |
| `GET` | `/health/database` | Database connectivity status | No | Public |
| `GET` | `/version` | API version & build information | No | Public |

---

## 2. Authentication

| Method | Endpoint | Description | Auth Required | Permitted Roles |
|---|---|---|---|---|
| `POST` | `/api/v1/auth/login` | Authenticate user & issue JWT | No | Public |
| `GET` | `/api/v1/auth/me` | Fetch authenticated user profile | Yes | All Authenticated |

---

## 3. User Management

| Method | Endpoint | Description | Auth Required | Permitted Roles |
|---|---|---|---|---|
| `POST` | `/api/v1/users` | Register a new application user | Yes | `ADMIN` |
| `GET` | `/api/v1/users` | List application users | Yes | `ADMIN` |
| `GET` | `/api/v1/users/{id}` | Get user details by ID | Yes | `ADMIN` |
| `PATCH` | `/api/v1/users/{id}` | Update user role or active status | Yes | `ADMIN` |

---

## 4. Employee Management

| Method | Endpoint | Description | Auth Required | Permitted Roles |
|---|---|---|---|---|
| `POST` | `/api/v1/employees` | Create new employee record | Yes | `ADMIN`, `HR_OFFICER` |
| `GET` | `/api/v1/employees` | Paginated employee list (search/filter/sort) | Yes | `ADMIN`, `HR_OFFICER`, `VIEWER` |
| `GET` | `/api/v1/employees/{id}` | Get detailed employee record | Yes | `ADMIN`, `HR_OFFICER`, `VIEWER` |
| `PATCH` | `/api/v1/employees/{id}` | Update employee details | Yes | `ADMIN`, `HR_OFFICER` |
| `DELETE` | `/api/v1/employees/{id}` | Deactivate employee (Soft Delete) | Yes | `ADMIN` |
| `POST` | `/api/v1/employees/{id}/reactivate` | Reactivate inactive employee | Yes | `ADMIN` |

---

## 5. Department Management

| Method | Endpoint | Description | Auth Required | Permitted Roles |
|---|---|---|---|---|
| `POST` | `/api/v1/departments` | Create new department | Yes | `ADMIN` |
| `GET` | `/api/v1/departments` | List all departments | Yes | `ADMIN`, `HR_OFFICER`, `VIEWER` |
| `GET` | `/api/v1/departments/{id}`| Get department details | Yes | `ADMIN`, `HR_OFFICER`, `VIEWER` |
| `PATCH` | `/api/v1/departments/{id}`| Update department | Yes | `ADMIN` |
| `DELETE` | `/api/v1/departments/{id}`| Delete department (blocked if active staff) | Yes | `ADMIN` |

---

## 6. Employment Records

| Method | Endpoint | Description | Auth Required | Permitted Roles |
|---|---|---|---|---|
| `POST` | `/api/v1/employees/{id}/employment-records` | Add employment record | Yes | `ADMIN`, `HR_OFFICER` |
| `GET` | `/api/v1/employees/{id}/employment-records` | List employment history | Yes | `ADMIN`, `HR_OFFICER`, `VIEWER` |
| `GET` | `/api/v1/employment-records/{record_id}` | Get specific record | Yes | `ADMIN`, `HR_OFFICER`, `VIEWER` |
| `PATCH` | `/api/v1/employment-records/{record_id}` | Update employment record | Yes | `ADMIN`, `HR_OFFICER` |

---

## 7. Background Checks

| Method | Endpoint | Description | Auth Required | Permitted Roles |
|---|---|---|---|---|
| `POST` | `/api/v1/employees/{id}/background-checks` | Initiate background check | Yes | `ADMIN`, `HR_OFFICER` |
| `GET` | `/api/v1/employees/{id}/background-checks` | List checks for employee | Yes | `ADMIN`, `HR_OFFICER`, `VIEWER`* |
| `GET` | `/api/v1/background-checks/{check_id}` | Get check details (*restricted notes filtered for Viewer) | Yes | `ADMIN`, `HR_OFFICER`, `VIEWER`* |
| `PATCH` | `/api/v1/background-checks/{check_id}` | Manually update check status/notes | Yes | `ADMIN`, `HR_OFFICER` |
| `POST` | `/api/v1/background-checks/{check_id}/execute` | Trigger mock provider execution | Yes | `ADMIN`, `HR_OFFICER` |

---

## 8. Reporting

| Method | Endpoint | Description | Auth Required | Permitted Roles |
|---|---|---|---|---|
| `GET` | `/api/v1/reports/dashboard` | Summary statistics dashboard | Yes | `ADMIN`, `HR_OFFICER` |
| `GET` | `/api/v1/reports/headcount-by-department` | Department headcount breakdown | Yes | `ADMIN`, `HR_OFFICER` |
| `GET` | `/api/v1/reports/employment-status` | Employment status distribution | Yes | `ADMIN`, `HR_OFFICER` |
| `GET` | `/api/v1/reports/outstanding-checks` | Pending/In-progress check report | Yes | `ADMIN`, `HR_OFFICER` |
| `GET` | `/api/v1/reports/expiring-right-to-work` | Expiring checks alert report | Yes | `ADMIN`, `HR_OFFICER` |

---

## 9. Audit Logs

| Method | Endpoint | Description | Auth Required | Permitted Roles |
|---|---|---|---|---|
| `GET` | `/api/v1/audit-logs` | Retrieve system audit trial | Yes | `ADMIN` |
