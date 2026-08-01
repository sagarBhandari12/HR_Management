from app.core.exceptions import UnprocessableEntityException
from app.integrations.bank_provider import BankVerificationProvider
from app.integrations.base import BaseCheckProvider
from app.integrations.credit_provider import CreditAgencyProvider
from app.integrations.dbs_provider import DBSProvider
from app.integrations.home_office_provider import HomeOfficeProvider
from app.models.background_check import CheckType


class ProviderFactory:
    """Factory for instantiating mock integration providers based on check type."""

    @staticmethod
    def get_provider(check_type: CheckType) -> BaseCheckProvider:
        if check_type == CheckType.DBS:
            return DBSProvider()
        elif check_type == CheckType.RIGHT_TO_WORK:
            return HomeOfficeProvider()
        elif check_type == CheckType.CREDIT:
            return CreditAgencyProvider()
        elif check_type == CheckType.BANK_VERIFICATION:
            return BankVerificationProvider()
        else:
            raise UnprocessableEntityException(f"Unsupported check type '{check_type}'")
