from typing import List

from sqlalchemy.orm import Session

from app.core.exceptions import ConflictException, NotFoundException, UnprocessableEntityException
from app.models.employee import EmployeeStatus
from app.models.employment_record import EmploymentRecord
from app.models.user import User
from app.repositories.employees import EmployeeRepository
from app.repositories.employment_records import EmploymentRecordRepository
from app.schemas.employment_record import EmploymentRecordCreate, EmploymentRecordResponse, EmploymentRecordUpdate
from app.services.auditing import AuditService


class EmploymentRecordService:
    def __init__(self, db: Session):
        self.db = db
        self.record_repo = EmploymentRecordRepository(db)
        self.emp_repo = EmployeeRepository(db)

    def create_record(
        self, employee_id: int, record_in: EmploymentRecordCreate, actor: User
    ) -> EmploymentRecordResponse:
        emp = self.emp_repo.get_by_id(employee_id)
        if not emp:
            raise NotFoundException(f"Employee with ID {employee_id} not found.")

        # Business Rule 11: A terminated/deactivated employee cannot receive a new active employment record
        if not emp.is_active or emp.status == EmployeeStatus.TERMINATED:
            raise ConflictException(
                f"Cannot create employment record for terminated/inactive employee '{emp.employee_number}'. "
                "Employee must be reactivated first."
            )

        # Validate manager if specified
        if record_in.manager_id:
            manager = self.emp_repo.get_by_id(record_in.manager_id)
            if not manager:
                raise NotFoundException(f"Manager employee with ID {record_in.manager_id} not found.")

        record = EmploymentRecord(
            employee_id=employee_id,
            job_title=record_in.job_title.strip(),
            employment_type=record_in.employment_type,
            start_date=record_in.start_date,
            end_date=record_in.end_date,
            salary_band=record_in.salary_band.strip(),
            manager_id=record_in.manager_id,
            status=record_in.status,
        )

        created_record = self.record_repo.create(record)

        AuditService.log_event(
            db=self.db,
            actor_user_id=actor.id,
            action="EMPLOYMENT_RECORD_CREATED",
            entity_type="EmploymentRecord",
            entity_id=created_record.id,
            description=f"Created employment record '{created_record.job_title}' for employee '{emp.employee_number}'",
        )

        return EmploymentRecordResponse.model_validate(created_record)

    def list_records_for_employee(self, employee_id: int) -> List[EmploymentRecordResponse]:
        emp = self.emp_repo.get_by_id(employee_id)
        if not emp:
            raise NotFoundException(f"Employee with ID {employee_id} not found.")

        records = self.record_repo.get_by_employee_id(employee_id)
        return [EmploymentRecordResponse.model_validate(r) for r in records]

    def get_record_by_id(self, record_id: int) -> EmploymentRecordResponse:
        record = self.record_repo.get_by_id(record_id)
        if not record:
            raise NotFoundException(f"Employment record with ID {record_id} not found.")
        return EmploymentRecordResponse.model_validate(record)

    def update_record(
        self, record_id: int, record_in: EmploymentRecordUpdate, actor: User
    ) -> EmploymentRecordResponse:
        record = self.record_repo.get_by_id(record_id)
        if not record:
            raise NotFoundException(f"Employment record with ID {record_id} not found.")

        start_date = record_in.start_date or record.start_date
        end_date = record_in.end_date if record_in.end_date is not None else record.end_date

        if end_date and start_date and end_date < start_date:
            raise UnprocessableEntityException("Employment end_date cannot be earlier than start_date.")

        changes = []
        if record_in.job_title:
            record.job_title = record_in.job_title.strip()
            changes.append("job_title")
        if record_in.employment_type:
            record.employment_type = record_in.employment_type
            changes.append("employment_type")
        if record_in.start_date:
            record.start_date = record_in.start_date
            changes.append("start_date")
        if record_in.end_date is not None:
            record.end_date = record_in.end_date
            changes.append("end_date")
        if record_in.salary_band:
            record.salary_band = record_in.salary_band.strip()
            changes.append("salary_band")
        if record_in.manager_id is not None:
            if record_in.manager_id > 0:
                manager = self.emp_repo.get_by_id(record_in.manager_id)
                if not manager:
                    raise NotFoundException(f"Manager employee with ID {record_in.manager_id} not found.")
                record.manager_id = record_in.manager_id
            else:
                record.manager_id = None
            changes.append("manager_id")
        if record_in.status:
            record.status = record_in.status
            changes.append("status")

        updated_record = self.record_repo.update(record)

        if changes:
            AuditService.log_event(
                db=self.db,
                actor_user_id=actor.id,
                action="EMPLOYMENT_RECORD_UPDATED",
                entity_type="EmploymentRecord",
                entity_id=updated_record.id,
                description=f"Updated employment record {updated_record.id}: " + ", ".join(changes),
            )

        return EmploymentRecordResponse.model_validate(updated_record)
