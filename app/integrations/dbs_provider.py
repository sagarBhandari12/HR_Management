import uuid
from datetime import date, timedelta
from typing import Any, Dict

from app.integrations.base import BaseCheckProvider, CheckProviderResult, ScenarioType
from app.models.background_check import CheckStatus


class DBSProvider(BaseCheckProvider):
    """Mock adapter for Disclosure and Barring Service (DBS) enhanced criminal record checks."""

    @property
    def provider_name(self) -> str:
        return "DBS_UK_GOV"

    def execute_check(
        self,
        employee_data: Dict[str, Any],
        scenario: ScenarioType = ScenarioType.APPROVED,
    ) -> CheckProviderResult:
        req_id = f"DBS-REQ-{uuid.uuid4().hex[:8].upper()}"
        emp_num = employee_data.get("employee_number", "EMP-UNKNOWN")
        today = date.today()

        if scenario == ScenarioType.APPROVED:
            return CheckProviderResult(
                provider_name=self.provider_name,
                request_identifier=req_id,
                status=CheckStatus.APPROVED,
                provider_reference=f"DBS-CERT-{uuid.uuid4().hex[:10].upper()}",
                completion_date=today,
                expiry_date=today + timedelta(days=1095),  # 3 Years validity
                notes=f"Enhanced DBS Check passed cleanly for employee {emp_num}. No disclosures found.",
            )
        elif scenario == ScenarioType.REJECTED:
            return CheckProviderResult(
                provider_name=self.provider_name,
                request_identifier=req_id,
                status=CheckStatus.REJECTED,
                provider_reference=f"DBS-CERT-{uuid.uuid4().hex[:10].upper()}",
                completion_date=today,
                notes=f"DBS check resulted in adverse findings for employee {emp_num}. Non-sensitive reason recorded.",
            )
        elif scenario == ScenarioType.REVIEW_REQUIRED:
            return CheckProviderResult(
                provider_name=self.provider_name,
                request_identifier=req_id,
                status=CheckStatus.REVIEW_REQUIRED,
                provider_reference=f"DBS-REF-{uuid.uuid4().hex[:10].upper()}",
                completion_date=today,
                notes=f"DBS request requires manual compliance panel review for employee {emp_num}.",
            )
        elif scenario == ScenarioType.UNAVAILABLE:
            return CheckProviderResult(
                provider_name=self.provider_name,
                request_identifier=req_id,
                status=CheckStatus.FAILED,
                error_code="DBS_SERVICE_503",
                notes="Disclosure and Barring Service portal is temporarily unavailable due to scheduled maintenance.",
            )
        elif scenario == ScenarioType.TIMEOUT:
            return CheckProviderResult(
                provider_name=self.provider_name,
                request_identifier=req_id,
                status=CheckStatus.FAILED,
                error_code="DBS_GATEWAY_504",
                notes="Gateway connection to DBS portal timed out after 30000ms.",
            )
        else:
            return CheckProviderResult(
                provider_name=self.provider_name,
                request_identifier=req_id,
                status=CheckStatus.FAILED,
                error_code="UNKNOWN_SCENARIO",
                notes=f"Unsupported scenario '{scenario}'",
            )
