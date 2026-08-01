# System Assumptions & Boundary Conditions

**Module:** SWE7301 Contemporary Software Engineering Practices  
**System:** Regent College London Human Resource Management RESTful API  
**Date:** August 2026  

---

## Technical & Academic Context

1. **Academic Backend Prototype:**  
   The system is an academic backend software prototype developed to demonstrate RESTful API design, layered architecture, automated testing (ATDD), security principles, and Agile development practices for Regent College London HR Team.

2. **Demonstration Interface:**  
   Swagger UI (`/docs`) and Postman collections serve as the primary demonstration clients. The project intentionally excludes a graphical frontend (Web/Mobile UI) as the assessed deliverable is purely a backend RESTful API.

3. **Database Environments:**  
   - **PostgreSQL 16+** is the target production/assessed database configuration run via Docker Compose.  
   - **SQLite** (via file or in-memory) is used as a fast, convenient fallback for local development and unit/integration automated tests.  
   - SQLAlchemy 2.x and Alembic are configured to remain database-agnostic.

4. **External System Simulation:**  
   - Third-party integrations (Disclosure and Barring Service - DBS, Home Office Right to Work, Credit Rating Agencies, and Commercial Banks for account verification) are simulated using deterministic mock provider adapters (`DBSProvider`, `HomeOfficeProvider`, `CreditAgencyProvider`, `BankVerificationProvider`).  
   - Mock integration patterns demonstrate standard API interaction, error handling, retries, timeouts, and state translations without making actual external HTTP calls or transmitting real data to live government/financial endpoints.

5. **Data Privacy & Synthetic Data:**  
   - Only synthetic, non-PII demonstration data is used.  
   - No real employee names, bank account numbers, national insurance numbers, passport values, or DBS certificate numbers are used or stored.

6. **Auditability & Deletion Policy:**  
   - Employee record deletion is strictly implemented as a soft deactivation (`is_active = False`, `status = TERMINATED`, with a recorded `deactivated_at` timestamp).  
   - Hard deletion is prohibited in compliance with HR record-retention best practices and auditability rules.

7. **Proportionate Security & Production Readiness:**  
   - Passwords are hashed using Argon2 (`pwdlib`).  
   - Authentication relies on signed JSON Web Tokens (JWT) with configurable expiry.  
   - Role-Based Access Control (RBAC) is enforced across `ADMIN`, `HR_OFFICER`, and `VIEWER` roles.  
   - The system is not claimed to be fully production-ready (e.g., hardware security modules, enterprise SSO/SAML, and compliance certifications are out of scope for this academic prototype).

8. **GDPR Data Minimisation:**  
   - The API minimizes sensitive field exposure. Unrestricted Viewer accounts cannot access restricted background check notes or audit logs.  
   - Complete legal compliance would require additional organizational controls, data processing agreements, and infrastructure hardening beyond the scope of this software prototype.
