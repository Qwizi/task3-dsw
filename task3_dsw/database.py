"""Database module."""
from __future__ import annotations

import datetime  # noqa: TCH003
import enum
import json
import uuid
from pathlib import Path

from pydantic import BaseModel, Field, ValidationError, field_validator

from task3_dsw.logger import logger
from task3_dsw.nbp_api import (
    ExchangeRateSchema,
    ExchangeRateSchemaResponse,
    NBPApiClient,
)
from task3_dsw.settings import (
    Settings,
    settings,
)


class InvoiceStatus(str, enum.Enum):
    """Invoice status type."""

    PAID = "Zapłacona"
    UNPAID = "Nie zapłacona"
    OVERPAID = "Nadpłata"


class AddInvoice(BaseModel):
    """Add invoice model."""

    id: uuid.UUID = Field(default_factory=uuid.uuid4)  # noqa: A003, RUF100
    amount: float
    currency: str
    date: datetime.date
    status: InvoiceStatus = InvoiceStatus.UNPAID
    exchange_rate: ExchangeRateSchemaResponse = None

    @field_validator("currency")
    def currency_is_valid(cls, v) -> str:  # noqa: N805, ANN001
        """Validate currency code."""
        if v not in settings.CURRENCIES and v != "PLN":
            msg = f"Currency code {v} is not valid."
            raise ValueError(msg)
        return v


class Invoice(BaseModel):
    """Invoice model."""

    id: uuid.UUID
    amount: float
    currency: str
    date: datetime.date
    status: InvoiceStatus
    exchange_rate: ExchangeRateSchemaResponse | None

    def __str__(self) -> str:
        """Return string representation of invoice."""
        return f"<{self.id} | {self.amount} | {self.currency} | {self.date} | {self.status}>"


class AddPayment(BaseModel):
    """Add payment model."""

    id: uuid.UUID = Field(default_factory=uuid.uuid4)
    invoice_id: uuid.UUID
    amount: float
    currency: str
    date: datetime.date
    exchange_rate: ExchangeRateSchemaResponse = None
    exchange_rate_difference: float = Field(default=0.0)

    @field_validator("currency")
    def currency_is_valid(cls, v) -> str:  # noqa: N805, ANN001
        """Validate currency code."""
        if v not in settings.CURRENCIES and v != "PLN":
            msg = f"Currency code {v} is not valid."
            raise ValueError(msg)
        return v


class Payment(BaseModel):
    """Payment model."""

    id: uuid.UUID
    invoice_id: uuid.UUID
    amount: float
    currency: str
    date: datetime.date
    exchange_rate: ExchangeRateSchemaResponse | None
    exchange_rate_difference: float | None

    def __str__(self) -> str:
        """Return string representation of payment."""
        return f"<{self.id} | {self.invoice_id} | {self.amount} | {self.currency} | {self.date}>"


class DataSchema(BaseModel):
    """Schema for data."""

    invoices: list[Invoice]
    payments: list[Payment]


class Database:
    """Json file database."""

    def __init__(
        self,
        settings: Settings,
        nbp_api_client: NBPApiClient,
        output_file: str | None = None,
    ) -> None:
        """Initialize database."""
        self.settings = settings
        self.data = DataSchema(invoices=[], payments=[])
        self.nbp_api_client = nbp_api_client
        self.output_file = output_file

    def load(self) -> None:
        """
        Load data from json file.

        Raises
        ------
            FileNotFoundError: if file not found
            JSONDecodeError: if json file is not valid
            ValidationError: if json file is not valid
        """
        try:
            with Path.open(self.settings.DATABASE_PATH, "r") as f:
                logger.debug("Load data from json file")
                self.data = DataSchema(**json.load(f))
        except FileNotFoundError:
            self.data = DataSchema(invoices=[], payments=[])
            self.save()
        except (json.decoder.JSONDecodeError, TypeError, ValidationError) as e:
            logger.error(e)

    def save(self) -> None:
        """Save data to json file."""
        filename = self.output_file or self.settings.DATABASE_PATH
        with Path.open(filename, "w") as f:
            f.write(self.data.model_dump_json(indent=4))

    def add_invoice(self, invoice: AddInvoice) -> Invoice:
        """
        Add invoice to database.

        Args:
        ----
            invoice: Invoice

        Returns:
        -------
            Invoice
        """
        self.data.invoices.append(invoice)
        return invoice

    def add_payment(self, payment: Payment) -> Payment:
        """
        Add payment to database.

        Args:
        ----
            payment: Payment

        Returns:
        -------
            Payment
        """
        self.data.payments.append(payment)
        return payment

    def get_invoice(self, invoice_index: int) -> Invoice:
        """
        Get invoice from database.

        Args:
        ----
            invoice_index: int

        Returns:
        -------
            Invoice
        """
        try:
            return self.data.invoices[invoice_index]
        except IndexError:
            return None

    def get_invoices(self) -> list[Invoice]:
        """
        Get invoices from database.

        Returns
        -------
            list[Invoice]
        """
        return self.data.invoices

    def get_payment(self, payment_id: str) -> Payment:
        """
        Get payment from database.

        Args:
        ----
            payment_id: str

        Returns:
        -------
            Payment
        """
        for payment in self.data.payments:
            if payment.id == payment_id:
                return payment
        return None

    def get_payment_by_index(self, payment_index: int) -> Payment:
        """
        Get payment from database.

        Args:
        ----
            payment_index: int

        Returns:
        -------
            Payment
        """
        try:
            return self.data.payments[payment_index]
        except IndexError:
            return None

    def get_payments(self, invoice_id: str | None = None) -> list[Payment]:
        """
        Get payments from database.

        Args:
        ----
            invoice_id: str

        Returns:
        -------
            list[Payment]
        """
        if invoice_id:
            return [
                payment
                for payment in self.data.payments
                if payment.invoice_id == invoice_id
            ]
        return self.data.payments

    def calulate_payments_for_invoice(
        self, invoice: Invoice
    ) -> tuple[int, float, InvoiceStatus]:
        """
        Calculate payments for invoice.

        Args:
        ----
            invoice: Invoice
            save: bool

        Returns:
        -------
            tuple[int, float, InvoiceStatus]
        """
        try:
            invoice_index = self.data.invoices.index(invoice)
            invoice_amount = invoice.amount
            if invoice.currency != "PLN":
                invoice_exchange_rate = self.nbp_api_client.get_exchange_rate(
                    ExchangeRateSchema(
                        table="A", code=invoice.currency, date=invoice.date
                    )
                )
                invoice_amount = invoice.amount * invoice_exchange_rate.rates[0].mid
            payments = self.get_payments(invoice.id)
            if not payments:
                self.data.invoices[invoice_index].status = InvoiceStatus.UNPAID
                return 0, invoice_amount, self.data.invoices[invoice_index].status
            sum_of_payments = 0
            for payment in payments:
                # if payment is in PLN then we can add payment amount to sum of payments
                if payment.currency == "PLN":
                    sum_of_payments += payment.amount
                # If payment currency is not PLN then we need to calculate exchange rate
                else:
                    payment_exchange_rate = self.nbp_api_client.get_exchange_rate(
                        ExchangeRateSchema(
                            table="A", code=payment.currency, date=payment.date
                        )
                    )
                    sum_of_payments += (
                        payment.amount * payment_exchange_rate.rates[0].mid
                    )
            if invoice_amount == sum_of_payments:
                self.data.invoices[invoice_index].status = InvoiceStatus.PAID
            elif invoice_amount > sum_of_payments:
                self.data.invoices[invoice_index].status = InvoiceStatus.UNPAID
            elif invoice_amount < sum_of_payments:
                self.data.invoices[invoice_index].status = InvoiceStatus.OVERPAID
            logger.debug(
                f"Invoice amount: {invoice_amount} Sum of payments: {sum_of_payments} "
            )
            return (
                sum_of_payments,
                invoice_amount,
                self.data.invoices[invoice_index].status,
            )
        except ValueError as e:
            logger.error(f"Invoice not found. {e}")
            return None

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
        try:
            invoice_index = self.data.invoices.index(invoice)
            payment_index = self.data.payments.index(payment)
            # if invoice and payment have the same currency then exchange rate difference is 0
            if invoice.currency == payment.currency:
                self.data.payments[payment_index].exchange_rate_difference = 0
                return None, None, 0

            invoice_exchange_rate = (
                invoice.exchange_rate
                if invoice.exchange_rate
                else self.nbp_api_client.get_exchange_rate(
                    ExchangeRateSchema(
                        code=payment.currency,
                        date=invoice.date,
                    )
                )
            )
            payment_exchange_rate = (
                payment.exchange_rate
                if payment.exchange_rate
                else self.nbp_api_client.get_exchange_rate(
                    ExchangeRateSchema(
                        code=payment.currency,
                        date=payment.date,
                    )
                )
            )

            echange_rate_difference = (
                payment.exchange_rate_difference
                if payment.exchange_rate_difference > 0
                else (
                    payment_exchange_rate.rates[0].mid
                    - invoice_exchange_rate.rates[0].mid
                )
                * invoice.amount
            )
            self.data.payments[
                payment_index
            ].exchange_rate_difference = echange_rate_difference
            self.data.payments[payment_index].exchange_rate = payment_exchange_rate
            self.data.invoices[invoice_index].exchange_rate = invoice_exchange_rate
        except ValueError as e:
            logger.error(f"Payment not found. {e}")
            return None, None, None
        else:
            return invoice_exchange_rate, payment_exchange_rate, echange_rate_difference
