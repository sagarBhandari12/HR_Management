import uuid
from datetime import date, timedelta
from typing import Any, Dict

from app.integrations.base import BaseCheckProvider, CheckProviderResult, ScenarioType
from app.models.background_check import CheckStatus


class BankVerificationProvider(BaseCheckProvider):
    """Mock adapter for Commercial Bank Account Ownership Verification Service."""

    @property
    def provider_name(self) -> str:
        return "UK_BANK_COP_VERIFY"

    def execute_check(
        self,
        employee_data: Dict[str, Any],
        scenario: ScenarioType = ScenarioType.APPROVED,
    ) -> CheckProviderResult:
        req_id = f"BANK-REQ-{uuid.uuid4().hex[:8].upper()}"
        emp_num = employee_data.get("employee_number", "EMP-UNKNOWN")
        today = date.today()

        if scenario == ScenarioType.APPROVED:
            return CheckProviderResult(
                provider_name=self.provider_name,
                request_identifier=req_id,
                status=CheckStatus.APPROVED,
                provider_reference=f"BANK-COP-{uuid.uuid4().hex[:10].upper()}",
                completion_date=today,
                expiry_date=today + timedelta(days=365),
                notes=f"Confirmation of Payee (CoP) verified name match for payroll for employee {emp_num}.",
            )
        elif scenario == ScenarioType.REJECTED:
            return CheckProviderResult(
                provider_name=self.provider_name,
                request_identifier=req_id,
                status=CheckStatus.REJECTED,
                provider_reference=f"BANK-COP-{uuid.uuid4().hex[:10].upper()}",
                completion_date=today,
                notes=f"Bank account name mismatch for payroll verification for employee {emp_num}.",
            )
        elif scenario == ScenarioType.REVIEW_REQUIRED:
            return CheckProviderResult(
                provider_name=self.provider_name,
                request_identifier=req_id,
                status=CheckStatus.REVIEW_REQUIRED,
                provider_reference=f"BANK-COP-{uuid.uuid4().hex[:10].upper()}",
                completion_date=today,
                notes=f"Partial name match returned by bank. Payroll compliance review required for employee {emp_num}.",
            )
        elif scenario == ScenarioType.UNAVAILABLE:
            return CheckProviderResult(
                provider_name=self.provider_name,
                request_identifier=req_id,
                status=CheckStatus.FAILED,
                error_code="BANK_VERIFY_503",
                notes="Open Banking verification service is down.",
            )
        elif scenario == ScenarioType.TIMEOUT:
            return CheckProviderResult(
                provider_name=self.provider_name,
                request_identifier=req_id,
                status=CheckStatus.FAILED,
                error_code="BANK_VERIFY_504",
                notes="Bank API verification gateway timeout.",
            )
        else:
            return CheckProviderResult(
                provider_name=self.provider_name,
                request_identifier=req_id,
                status=CheckStatus.FAILED,
                error_code="UNKNOWN_SCENARIO",
                notes=f"Unsupported scenario '{scenario}'",
            )
