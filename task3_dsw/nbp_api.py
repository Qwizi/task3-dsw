"""Api client for National Bank of Polish."""
from __future__ import annotations

import datetime  # noqa: TCH003

import httpx
from pydantic import BaseModel, field_validator

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
        except (httpx.HTTPStatusError, httpx.HTTPError) as exc:
            msg = f"NBPAPIError: {exc}"
            raise NBPApiError(msg) from exc
        else:
            return ExchangeRateSchemaResponse(**response.json())
