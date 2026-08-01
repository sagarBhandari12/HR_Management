# System Architecture Overview

**System:** Regent College London HR Management RESTful API  
**Framework:** FastAPI, SQLAlchemy 2.x, Pydantic v2  

---

## Architectural Pattern: Layered Architecture

The system enforces a strict 5-tier layered architecture to isolate concerns, maintain testability, and decouple database schemas from business logic and HTTP interface definitions.

```
                  ┌─────────────────────────────────────┐
                  │    HTTP Client / Postman / Swagger  │
                  └──────────────────┬──────────────────┘
                                     │ HTTP (JSON)
                                     ▼
                  ┌─────────────────────────────────────┐
                  │          API Routes Layer           │
                  │   (FastAPI Routers & Controllers)   │
                  └──────────────────┬──────────────────┘
                                     │ Validated DTOs (Pydantic Schemas)
                                     ▼
                  ┌─────────────────────────────────────┐
                  │           Service Layer             │
                  │  (Business Logic & Rules Engine)    │
                  └──────┬──────────────────────┬───────┘
                         │                      │
       Integrations      │                      │ DB Repositories
                         ▼                      ▼
┌─────────────────────────────────┐   ┌─────────────────────────────────┐
│       Integrations Layer        │   │        Repository Layer         │
│  (Mock Providers: DBS, etc.)    │   │     (Data Access Layer)         │
└─────────────────────────────────┘   └────────────────┬────────────────┘
                                                       │ SQLAlchemy ORM
                                                       ▼
                                      ┌─────────────────────────────────┐
                                      │     Database (SQLAlchemy Models)│
                                      │    (PostgreSQL / SQLite Storage)│
                                      └─────────────────────────────────┘
```

---

## Component Breakdown

1. **API Router Layer (`app/api/v1/routes/`)**  
   - Handles HTTP requests, path parameters, query params, and JSON payloads.
   - Enforces Authentication (`get_current_user`) and RBAC authorization (`require_role`).
   - Delegates all logic to Service methods and returns standard JSON responses / HTTP status codes.

2. **Schemas Layer (`app/schemas/`)**  
   - Pydantic v2 data validation schemas (Data Transfer Objects).
   - Validates incoming request payloads (email format, date ranges, password strength, enum constraints).
   - Defines response models to sanitize output (excluding sensitive fields like `hashed_password`).

3. **Service Layer (`app/services/`)**  
   - Encapsulates domain logic and business rules.
   - Enforces policies (e.g., unique email check, department deletion blocking when active employees exist, employee deactivation logic).
   - Triggers audit logging events automatically upon state mutation.

4. **Integration Layer (`app/integrations/`)**  
   - Defines standard interface (`BaseCheckProvider`) for background check execution.
   - Includes 4 concrete mock providers (`DBSProvider`, `HomeOfficeProvider`, `CreditAgencyProvider`, `BankVerificationProvider`).
   - Managed via a Factory (`ProviderFactory`) to dynamically load provider implementation by check type.

5. **Repository Layer (`app/repositories/`)**  
   - Abstracts SQLAlchemy 2.x database CRUD operations.
   - Handles query building, pagination, allowlisted sorting, filtering, and transaction boundaries.

6. **Database & Models Layer (`app/db/` & `app/models/`)**  
   - Defines declarative SQLAlchemy ORM entities with foreign keys, indexes, and unique constraints.
   - Migration management provided via Alembic.
