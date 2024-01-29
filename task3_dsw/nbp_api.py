"""Api client for National Bank of Polish."""
from __future__ import annotations

import datetime  # noqa: TCH003

import httpx
from pydantic import BaseModel, field_validator

from task3_dsw.database import Invoice, Payment
from task3_dsw.settings import (
    settings,
)


class NBPApiError(Exception):
    """Base class for NBPApi exceptions."""


class ExchangeRateSchema(BaseModel):
    """Schema for exchange rate."""

    table: str = "a"
    code: str
    date: datetime.date

    @field_validator("code")
    def currency_is_valid(cls, v) -> str:  # noqa: N805, ANN001
        """Validate currency code."""
        if v not in settings.CURRENCIES:
            msg = f"Currency code {v} is not valid."
            raise ValueError(msg)
        return v


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

    def __init__(self) -> None:
        """Initialize NBPApiClient."""
        self.api_url = "http://api.nbp.pl/api/"
        self.headers = {"Accept": "application/json"}
        self.client = httpx.Client(base_url=self.api_url, headers=self.headers)

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

    def calculate_difference(
        self, invoice: Invoice, payment: Payment
    ) -> tuple[ExchangeRateSchemaResponse, ExchangeRateSchemaResponse, float]:
        """
        Calculate exchange rate difference.

        Args:
        ----
            invoice: Invoice
            payment: Payment

        Returns:
        -------
            tuple[ExchangeRateSchemaResponse, ExchangeRateSchemaResponse, float]
        """
        # if invoice and payment have the same currency then exchange rate difference is 0
        if invoice.currency == payment.currency:
            return None, None, 0
        invoice_exchange_rate = self.get_exchange_rate(
            ExchangeRateSchema(
                code=payment.currency,
                date=invoice.date,
            )
        )
        payment_exchange_rate = self.get_exchange_rate(
            ExchangeRateSchema(
                code=payment.currency,
                date=payment.date,
            )
        )
        echange_rate_difference = (
            payment_exchange_rate.rates[0].mid - invoice_exchange_rate.rates[0].mid
        ) * invoice.amount

        return invoice_exchange_rate, payment_exchange_rate, echange_rate_difference
