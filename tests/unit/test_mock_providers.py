import pytest

from app.integrations.bank_provider import BankVerificationProvider
from app.integrations.base import ScenarioType
from app.integrations.credit_provider import CreditAgencyProvider
from app.integrations.dbs_provider import DBSProvider
from app.integrations.home_office_provider import HomeOfficeProvider
from app.integrations.provider_factory import ProviderFactory
from app.models.background_check import CheckStatus, CheckType


@pytest.mark.unit
def test_provider_factory():
    assert isinstance(ProviderFactory.get_provider(CheckType.DBS), DBSProvider)
    assert isinstance(ProviderFactory.get_provider(CheckType.RIGHT_TO_WORK), HomeOfficeProvider)
    assert isinstance(ProviderFactory.get_provider(CheckType.CREDIT), CreditAgencyProvider)
    assert isinstance(ProviderFactory.get_provider(CheckType.BANK_VERIFICATION), BankVerificationProvider)


@pytest.mark.unit
def test_dbs_provider_scenarios():
    provider = DBSProvider()
    emp_data = {"employee_number": "EMP-TEST-01"}

    res_app = provider.execute_check(emp_data, ScenarioType.APPROVED)
    assert res_app.status == CheckStatus.APPROVED
    assert res_app.provider_reference.startswith("DBS-CERT-")

    res_rej = provider.execute_check(emp_data, ScenarioType.REJECTED)
    assert res_rej.status == CheckStatus.REJECTED

    res_rev = provider.execute_check(emp_data, ScenarioType.REVIEW_REQUIRED)
    assert res_rev.status == CheckStatus.REVIEW_REQUIRED

    res_un = provider.execute_check(emp_data, ScenarioType.UNAVAILABLE)
    assert res_un.status == CheckStatus.FAILED
    assert res_un.error_code == "DBS_SERVICE_503"

    res_to = provider.execute_check(emp_data, ScenarioType.TIMEOUT)
    assert res_to.status == CheckStatus.FAILED
    assert res_to.error_code == "DBS_GATEWAY_504"


@pytest.mark.unit
def test_home_office_provider_scenarios():
    provider = HomeOfficeProvider()
    emp_data = {"employee_number": "EMP-TEST-02"}

    res_app = provider.execute_check(emp_data, ScenarioType.APPROVED)
    assert res_app.status == CheckStatus.APPROVED
    assert res_app.provider_reference.startswith("HO-SHARECODE-")
    assert res_app.expiry_date is not None


@pytest.mark.unit
def test_credit_provider_scenarios():
    provider = CreditAgencyProvider()
    emp_data = {"employee_number": "EMP-TEST-03"}

    res_app = provider.execute_check(emp_data, ScenarioType.APPROVED)
    assert res_app.status == CheckStatus.APPROVED
    assert res_app.provider_reference.startswith("CRED-REF-")


@pytest.mark.unit
def test_bank_provider_scenarios():
    provider = BankVerificationProvider()
    emp_data = {"employee_number": "EMP-TEST-04"}

    res_app = provider.execute_check(emp_data, ScenarioType.APPROVED)
    assert res_app.status == CheckStatus.APPROVED
    assert res_app.provider_reference.startswith("BANK-COP-")
