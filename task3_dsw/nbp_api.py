"""Api client for National Bank of Polish."""
from __future__ import annotations

import datetime  # noqa: TCH003

import httpx
from pydantic import BaseModel

from task3_dsw.settings import Settings  # noqa: TCH001


class NBPApiError(Exception):
    """Base class for NBPApi exceptions."""


class ExchangeRateSchema(BaseModel):
    """Schema for exchange rate."""

    table: str = "a"
    code: str
    date: datetime.date


class RateSchema(BaseModel):
    """Schema for rate."""

    no: str
    effectiveDate: datetime.date  # noqa: N815
    mid: float


class ExchangeRateSchemaResponse(BaseModel):
    """Schema for exchange rate response."""

    table: str
    currency: str
    code: str
    rates: list[RateSchema]


class NBPApiClient:
    """Class for making requests to api National Bank of Polish."""

    api_url: str
    headers: dict
    client: httpx.Client

    def __init__(self, settings: Settings) -> None:
        """Initialize NBPApiClient with given api_url."""
        self.api_url = "http://api.nbp.pl/api/"
        self.headers = {"Accept": "application/json"}
        self.client = httpx.Client(base_url=self.api_url, headers=self.headers)
        self.settings = settings

    def is_valid_currency_code(self, currency_code: str) -> bool:
        """
        Check if given currency code is valid.

        Args:
        ----
            currency_code: Currency code to be checked.

        Returns:
        -------
            True if currency code is valid, False otherwise.
        """
        return currency_code in self.settings.CURRENCIES

    def get_exchange_rate(self, data: ExchangeRateSchema) -> ExchangeRateSchemaResponse:
        """
        Get exchange rate for given currency code.

        Args:
        ----
            data: ExchangeRateSchema

        Returns:
        -------
            ExchangeRateSchemaResponse

        Raises:
        ------
            NBPApiError: If currency code is invalid or if an HTTP error occurred.
        """
        if not self.is_valid_currency_code(data.code):
            msg = f"This currency is not in CURRENCIES variable: {data.code}"
            raise NBPApiError(msg)
        try:
            endpoint = f"exchangerates/rates/{data.table}/{data.code}/{data.date}/"
            response = self.client.get(endpoint)
            response.raise_for_status()
        except httpx.HTTPStatusError as exc:
            if exc.response.status_code == httpx.codes.NOT_FOUND:
                msg = f"Not found [{exc.response.text}]"
            elif exc.response.status_code == httpx.codes.BAD_REQUEST:
                msg = f"Invalid Request. [{exc.response.text}]"
            else:
                msg = f"An HTTP error occurred with status code {exc.response.status_code}."
            raise NBPApiError(msg) from exc
        except httpx.HTTPError as e:
            msg = f"An HTTP error occurred: {e}"
            raise NBPApiError(msg) from e
        else:
            return ExchangeRateSchemaResponse(**response.json())
