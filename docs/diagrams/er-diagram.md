# Database Entity-Relationship (ER) Diagram

```mermaid
erDiagram
    USERS {
        int id PK
        string email UK
        string full_name
        string hashed_password
        string role
        boolean is_active
        datetime created_at
        datetime updated_at
    }

    DEPARTMENTS {
        int id PK
        string name UK
        string description
        boolean is_active
        datetime created_at
        datetime updated_at
    }

    EMPLOYEES {
        int id PK
        string employee_number UK
        string first_name
        string last_name
        string work_email UK
        string personal_email
        string telephone
        date date_of_birth
        int department_id FK
        string status
        boolean is_active
        datetime created_at
        datetime updated_at
        datetime deactivated_at
    }

    EMPLOYMENT_RECORDS {
        int id PK
        int employee_id FK
        string job_title
        string employment_type
        date start_date
        date end_date
        string salary_band
        int manager_id FK
        string status
        datetime created_at
        datetime updated_at
    }

    BACKGROUND_CHECKS {
        int id PK
        int employee_id FK
        string check_type
        string status
        datetime requested_at
        datetime completed_at
        string provider_reference
        date expiry_date
        string restricted_notes
        int created_by FK
        int updated_by FK
        datetime created_at
        datetime updated_at
    }

    EXTERNAL_REQUESTS {
        int id PK
        int background_check_id FK
        string provider
        string request_identifier
        string outcome
        string error_code
        datetime requested_at
        datetime completed_at
    }

    AUDIT_LOGS {
        int id PK
        int actor_user_id FK
        string action
        string entity_type
        int entity_id
        string description
        datetime created_at
    }

    DEPARTMENTS ||--o{ EMPLOYEES : "contains"
    EMPLOYEES ||--o{ EMPLOYMENT_RECORDS : "has history"
    EMPLOYEES ||--o{ BACKGROUND_CHECKS : "undergoes"
    BACKGROUND_CHECKS ||--o{ EXTERNAL_REQUESTS : "audits"
    USERS ||--o{ AUDIT_LOGS : "performs action"
    USERS ||--o{ BACKGROUND_CHECKS : "initiates/updates"
```

## Exporting Diagram Instructions
To export this diagram as PNG or SVG:
1. Open this file in VS Code or GitHub with Mermaid rendering enabled.
2. Use `mmdc` (Mermaid CLI) command:
   ```bash
   npx @mermaid-js/mermaid-cli -i docs/diagrams/er-diagram.md -o docs/diagrams/er-diagram.png
   ```
