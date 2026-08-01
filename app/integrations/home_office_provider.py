import uuid
from datetime import date, timedelta
from typing import Any, Dict

from app.integrations.base import BaseCheckProvider, CheckProviderResult, ScenarioType
from app.models.background_check import CheckStatus


class HomeOfficeProvider(BaseCheckProvider):
    """Mock adapter for UK Home Office Right to Work verification service."""

    @property
    def provider_name(self) -> str:
        return "HOME_OFFICE_RTW"

    def execute_check(
        self,
        employee_data: Dict[str, Any],
        scenario: ScenarioType = ScenarioType.APPROVED,
    ) -> CheckProviderResult:
        req_id = f"HO-REQ-{uuid.uuid4().hex[:8].upper()}"
        emp_num = employee_data.get("employee_number", "EMP-UNKNOWN")
        today = date.today()

        if scenario == ScenarioType.APPROVED:
            return CheckProviderResult(
                provider_name=self.provider_name,
                request_identifier=req_id,
                status=CheckStatus.APPROVED,
                provider_reference=f"HO-SHARECODE-{uuid.uuid4().hex[:9].upper()}",
                completion_date=today,
                expiry_date=today + timedelta(days=730),  # 2 Years Right to Work validity
                notes=f"Right to Work share code verified cleanly for employee {emp_num}. Full work permission granted.",
            )
        elif scenario == ScenarioType.REJECTED:
            return CheckProviderResult(
                provider_name=self.provider_name,
                request_identifier=req_id,
                status=CheckStatus.REJECTED,
                provider_reference=f"HO-SHARECODE-{uuid.uuid4().hex[:9].upper()}",
                completion_date=today,
                notes=f"Right to work verification failed for employee {emp_num}. Share code expired or visa restriction.",
            )
        elif scenario == ScenarioType.REVIEW_REQUIRED:
            return CheckProviderResult(
                provider_name=self.provider_name,
                request_identifier=req_id,
                status=CheckStatus.REVIEW_REQUIRED,
                provider_reference=f"HO-REF-{uuid.uuid4().hex[:9].upper()}",
                completion_date=today,
                notes="Home Office Employer Checking Service request submitted. Pending official response.",
            )
        elif scenario == ScenarioType.UNAVAILABLE:
            return CheckProviderResult(
                provider_name=self.provider_name,
                request_identifier=req_id,
                status=CheckStatus.FAILED,
                error_code="HOME_OFFICE_503",
                notes="Home Office online verification API is down for emergency maintenance.",
            )
        elif scenario == ScenarioType.TIMEOUT:
            return CheckProviderResult(
                provider_name=self.provider_name,
                request_identifier=req_id,
                status=CheckStatus.FAILED,
                error_code="HOME_OFFICE_504",
                notes="Home Office sharecode service gateway timeout.",
            )
        else:
            return CheckProviderResult(
                provider_name=self.provider_name,
                request_identifier=req_id,
                status=CheckStatus.FAILED,
                error_code="UNKNOWN_SCENARIO",
                notes=f"Unsupported scenario '{scenario}'",
            )
