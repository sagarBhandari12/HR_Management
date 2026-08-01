from datetime import datetime, timezone
from typing import List

from sqlalchemy.orm import Session

from app.core.exceptions import NotFoundException, UnprocessableEntityException
from app.integrations.provider_factory import ProviderFactory
from app.models.background_check import BackgroundCheck, CheckStatus
from app.models.external_request import ExternalRequest
from app.models.user import User, UserRole
from app.repositories.background_checks import BackgroundCheckRepository
from app.repositories.employees import EmployeeRepository
from app.schemas.background_check import (
    BackgroundCheckCreate,
    BackgroundCheckExecutionRequest,
    BackgroundCheckResponse,
    BackgroundCheckUpdate,
)
from app.services.auditing import AuditService


class BackgroundCheckService:
    def __init__(self, db: Session):
        self.db = db
        self.check_repo = BackgroundCheckRepository(db)
        self.emp_repo = EmployeeRepository(db)

    def _to_response(self, check: BackgroundCheck, user: User) -> BackgroundCheckResponse:
        res = BackgroundCheckResponse.model_validate(check)
        # Business Rule 22: Restricted check notes must not be returned to Viewer users
        if user.role == UserRole.VIEWER:
            res.restricted_notes = None
        return res

    def create_check(
        self, employee_id: int, check_in: BackgroundCheckCreate, actor: User
    ) -> BackgroundCheckResponse:
        emp = self.emp_repo.get_by_id(employee_id)
        if not emp:
            raise NotFoundException(f"Employee with ID {employee_id} not found.")

        check = BackgroundCheck(
            employee_id=employee_id,
            check_type=check_in.check_type,
            status=CheckStatus.PENDING,
            restricted_notes=check_in.restricted_notes,
            created_by=actor.id,
            updated_by=actor.id,
        )

        created_check = self.check_repo.create(check)

        AuditService.log_event(
            db=self.db,
            actor_user_id=actor.id,
            action="BACKGROUND_CHECK_CREATED",
            entity_type="BackgroundCheck",
            entity_id=created_check.id,
            description=f"Initiated '{created_check.check_type.value}' check for employee '{emp.employee_number}'",
        )

        return self._to_response(created_check, actor)

    def get_check_by_id(self, check_id: int, user: User) -> BackgroundCheckResponse:
        check = self.check_repo.get_by_id(check_id)
        if not check:
            raise NotFoundException(f"Background check with ID {check_id} not found.")
        return self._to_response(check, user)

    def list_checks_for_employee(self, employee_id: int, user: User) -> List[BackgroundCheckResponse]:
        emp = self.emp_repo.get_by_id(employee_id)
        if not emp:
            raise NotFoundException(f"Employee with ID {employee_id} not found.")

        checks = self.check_repo.get_by_employee_id(employee_id)
        return [self._to_response(c, user) for c in checks]

    def update_check(
        self, check_id: int, check_in: BackgroundCheckUpdate, actor: User
    ) -> BackgroundCheckResponse:
        check = self.check_repo.get_by_id(check_id)
        if not check:
            raise NotFoundException(f"Background check with ID {check_id} not found.")

        target_status = check_in.status or check.status
        target_ref = check_in.provider_reference or check.provider_reference

        # Rule 13: A background check cannot be approved without a provider reference and completion date
        if target_status == CheckStatus.APPROVED:
            if not target_ref:
                raise UnprocessableEntityException(
                    "Background check cannot be APPROVED without a valid provider reference."
                )

        # Rule 14: A rejected background check must contain an appropriate non-sensitive reason
        if target_status == CheckStatus.REJECTED:
            if not check_in.restricted_notes and not check.restricted_notes:
                raise UnprocessableEntityException(
                    "A rejected background check must contain a non-sensitive reason note."
                )

        if check_in.status:
            check.status = check_in.status
            if check_in.status in [CheckStatus.APPROVED, CheckStatus.REJECTED, CheckStatus.FAILED]:
                check.completed_at = datetime.now(timezone.utc)
        if check_in.provider_reference:
            check.provider_reference = check_in.provider_reference.strip()
        if check_in.expiry_date:
            check.expiry_date = check_in.expiry_date
        if check_in.restricted_notes:
            check.restricted_notes = check_in.restricted_notes

        check.updated_by = actor.id
        updated_check = self.check_repo.update(check)

        AuditService.log_event(
            db=self.db,
            actor_user_id=actor.id,
            action="BACKGROUND_CHECK_UPDATED",
            entity_type="BackgroundCheck",
            entity_id=updated_check.id,
            description=f"Updated background check {updated_check.id} status to '{updated_check.status.value}'",
        )

        return self._to_response(updated_check, actor)

    def execute_check_simulation(
        self, check_id: int, req_in: BackgroundCheckExecutionRequest, actor: User
    ) -> BackgroundCheckResponse:
        """
        Selects the correct mock provider based on check_type, executes the simulated check,
        records the external request log, updates background check status, and logs an audit event.
        """
        check = self.check_repo.get_by_id(check_id)
        if not check:
            raise NotFoundException(f"Background check with ID {check_id} not found.")

        emp = self.emp_repo.get_by_id(check.employee_id)
        emp_data = {
            "employee_number": emp.employee_number if emp else "EMP-UNKNOWN",
            "first_name": emp.first_name if emp else "Unknown",
            "last_name": emp.last_name if emp else "Unknown",
        }

        # Factory provider selection
        provider = ProviderFactory.get_provider(check.check_type)
        result = provider.execute_check(emp_data, scenario=req_in.scenario)

        # Audit external request log (DO NOT store sensitive raw payloads)
        ext_req = ExternalRequest(
            background_check_id=check.id,
            provider=result.provider_name,
            request_identifier=result.request_identifier,
            outcome=result.status.value,
            error_code=result.error_code,
            requested_at=datetime.now(timezone.utc),
            completed_at=datetime.now(timezone.utc) if result.status != CheckStatus.PENDING else None,
        )
        self.check_repo.create_external_request(ext_req)

        # Update BackgroundCheck state
        check.status = result.status
        if result.provider_reference:
            check.provider_reference = result.provider_reference
        if result.expiry_date:
            check.expiry_date = result.expiry_date
        if result.notes:
            check.restricted_notes = (check.restricted_notes or "") + f"\n[{result.provider_name}]: {result.notes}"

        if result.status in [CheckStatus.APPROVED, CheckStatus.REJECTED, CheckStatus.FAILED, CheckStatus.REVIEW_REQUIRED]:
            check.completed_at = datetime.now(timezone.utc)

        check.updated_by = actor.id
        updated_check = self.check_repo.update(check)

        AuditService.log_event(
            db=self.db,
            actor_user_id=actor.id,
            action="BACKGROUND_CHECK_EXECUTED",
            entity_type="BackgroundCheck",
            entity_id=updated_check.id,
            description=(
                f"Executed '{updated_check.check_type.value}' mock check via {result.provider_name}. "
                f"Scenario: '{req_in.scenario.value}' -> Outcome: '{updated_check.status.value}'"
            ),
        )

        return self._to_response(updated_check, actor)
