import uuid
from datetime import date, timedelta
from typing import Any, Dict

from app.integrations.base import BaseCheckProvider, CheckProviderResult, ScenarioType
from app.models.background_check import CheckStatus


class CreditAgencyProvider(BaseCheckProvider):
    """Mock adapter for Credit Rating & Financial Risk verification agency."""

    @property
    def provider_name(self) -> str:
        return "CREDIT_AGENCY_UK"

    def execute_check(
        self,
        employee_data: Dict[str, Any],
        scenario: ScenarioType = ScenarioType.APPROVED,
    ) -> CheckProviderResult:
        req_id = f"CRED-REQ-{uuid.uuid4().hex[:8].upper()}"
        emp_num = employee_data.get("employee_number", "EMP-UNKNOWN")
        today = date.today()

        if scenario == ScenarioType.APPROVED:
            return CheckProviderResult(
                provider_name=self.provider_name,
                request_identifier=req_id,
                status=CheckStatus.APPROVED,
                provider_reference=f"CRED-REF-{uuid.uuid4().hex[:10].upper()}",
                completion_date=today,
                expiry_date=today + timedelta(days=365),  # 1 Year validity
                notes=f"Credit history check passed for employee {emp_num}. No active CCJs or bankruptcy recorded.",
            )
        elif scenario == ScenarioType.REJECTED:
            return CheckProviderResult(
                provider_name=self.provider_name,
                request_identifier=req_id,
                status=CheckStatus.REJECTED,
                provider_reference=f"CRED-REF-{uuid.uuid4().hex[:10].upper()}",
                completion_date=today,
                notes=f"Credit check failed due to severe financial risk flag for employee {emp_num}.",
            )
        elif scenario == ScenarioType.REVIEW_REQUIRED:
            return CheckProviderResult(
                provider_name=self.provider_name,
                request_identifier=req_id,
                status=CheckStatus.REVIEW_REQUIRED,
                provider_reference=f"CRED-REF-{uuid.uuid4().hex[:10].upper()}",
                completion_date=today,
                notes=f"Credit check requires manual audit due to identity history mismatch for employee {emp_num}.",
            )
        elif scenario == ScenarioType.UNAVAILABLE:
            return CheckProviderResult(
                provider_name=self.provider_name,
                request_identifier=req_id,
                status=CheckStatus.FAILED,
                error_code="CREDIT_AGENCY_503",
                notes="Credit Bureau API end-point is currently unavailable.",
            )
        elif scenario == ScenarioType.TIMEOUT:
            return CheckProviderResult(
                provider_name=self.provider_name,
                request_identifier=req_id,
                status=CheckStatus.FAILED,
                error_code="CREDIT_AGENCY_504",
                notes="Credit agency inquiry timeout after 25000ms.",
            )
        else:
            return CheckProviderResult(
                provider_name=self.provider_name,
                request_identifier=req_id,
                status=CheckStatus.FAILED,
                error_code="UNKNOWN_SCENARIO",
                notes=f"Unsupported scenario '{scenario}'",
            )
