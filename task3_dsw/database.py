"""Database module."""
from __future__ import annotations

import datetime  # noqa: TCH003
import enum
import json
from pathlib import Path

from pydantic import BaseModel, Field, ValidationError, field_validator

from task3_dsw.logger import logger
from task3_dsw.nbp_api import (
    ExchangeRateSchema,
    ExchangeRateSchemaResponse,
    NBPApiClient,
    NBPApiError,
)
from task3_dsw.settings import (
    Settings,
    settings,
)


class InvoiceStatus(str, enum.Enum):
    """Invoice status type."""

    PAID = "Zaplacona"
    UNPAID = "Nie zaplacona"
    OVERPAID = "Nadplata"


class AddPayment(BaseModel):
    """Add payment model."""

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

    amount: float
    currency: str
    date: datetime.date
    exchange_rate: ExchangeRateSchemaResponse | None
    exchange_rate_difference: float | None

    def __str__(self) -> str:
        """Return string representation of payment."""
        return f"<{self.amount} | {self.currency} | {self.date}>"


class AddInvoice(BaseModel):
    """Add invoice model."""

    amount: float
    currency: str
    date: datetime.date
    status: InvoiceStatus = InvoiceStatus.UNPAID
    exchange_rate: ExchangeRateSchemaResponse = None
    payments: list[Payment] = []

    @field_validator("currency")
    def currency_is_valid(cls, v) -> str:  # noqa: N805, ANN001
        """Validate currency code."""
        if v not in settings.CURRENCIES and v != "PLN":
            msg = f"Currency code {v} is not valid."
            raise ValueError(msg)
        return v


class Invoice(BaseModel):
    """Invoice model."""

    amount: float
    currency: str
    date: datetime.date
    status: InvoiceStatus
    exchange_rate: ExchangeRateSchemaResponse | None
    payments: list[Payment]

    def __str__(self) -> str:
        """Return string representation of invoice."""
        return f"<{self.amount} | {self.currency} | {self.date} | {self.status}>"


class DataSchema(BaseModel):
    """Schema for data."""

    invoices: list[Invoice]


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
        self.data = DataSchema(invoices=[])
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
            self.data = DataSchema(invoices=[])
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

    def add_payment(self, invoice: Invoice, payment: Payment) -> Payment:
        """
        Add payment to database.

        Args:
        ----
            invoice: Invoice
            payment: Payment

        Returns:
        -------
            Payment
        """
        invoice_index = self.data.invoices.index(invoice)
        self.data.invoices[invoice_index].payments.append(payment)
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

    def get_payment(self, invoice: Invoice, payment_index: int) -> Payment:
        """
        Get payment from database.

        Args:
        ----
            invoice: Invoice
            payment_index: int

        Returns:
        -------
            Payment
        """
        try:
            return self.data.invoices[self.data.invoices.index(invoice)].payments[
                payment_index
            ]
        except IndexError:
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

    def get_payments(self, invoice: Invoice) -> list[Payment]:
        """
        Get payments from database.

        Args:
        ----
            invoice: Invoice

        Returns:
        -------
            list[Payment]
        """
        try:
            return self.data.invoices[self.data.invoices.index(invoice)].payments
        except (ValueError, IndexError) as e:
            logger.error(f"Invoice not found. {e}")
            return None

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
            tuple[sum_of_payments(int), invoice_amount(float), InvoiceStatus]
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
            payments = self.get_payments(invoice)
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
            payment_index = self.data.invoices[invoice_index].payments.index(payment)

            exchange_rate_difference = 0
            invoice_exchange_rate = None
            payment_exchange_rate = None

            if invoice.currency == payment.currency:
                # Jeśli waluta faktury i płatności są takie same, różnica to po prostu różnica między kwotami
                return exchange_rate_difference
                # Jeśli waluty są różne, musimy przeliczyć jedną z kwot na walutę drugiej kwoty
            if invoice.currency == "PLN":
                invoice_exchange_rate = self.nbp_api_client.get_exchange_rate(
                    ExchangeRateSchema(
                        table="A", code=payment.currency, date=invoice.date
                    )
                )
                payment_exchange_rate = self.nbp_api_client.get_exchange_rate(
                    ExchangeRateSchema(
                        table="A", code=payment.currency, date=payment.date
                    )
                )
                # Przeliczenie wartości faktury na walutę płatności
                invoice_amount = invoice.amount / invoice_exchange_rate.rates[0].mid
                logger.debug(f"Invoice amount in payment currency: {invoice_amount}")
                # Przeliczenie otrzymanych należności na walutę płatności
                payment_amount = invoice.amount / payment_exchange_rate.rates[0].mid
                logger.debug(f"Payment amount in payment currency: {payment_amount}")
                # Obliczenie różnicy między kwotami
                exchange_rate_difference = payment_amount - invoice_amount
                logger.debug(f"Exchange rate difference: {exchange_rate_difference}")

            else:
                # Jeśli waluta płatności to PLN, przelicz kwotę faktury na PLN
                invoice_exchange_rate = self.nbp_api_client.get_exchange_rate(
                    ExchangeRateSchema(
                        table="A", code=invoice.currency, date=invoice.date
                    )
                )
                payment_exchange_rate = self.nbp_api_client.get_exchange_rate(
                    ExchangeRateSchema(
                        table="A", code=invoice.currency, date=payment.date
                    )
                )

                # Przeliczenie wartości faktury na PLN
                invoice_amount = invoice.amount * invoice_exchange_rate.rates[0].mid
                logger.debug(f"Invoice amount in PLN: {invoice_amount}")
                # Przeliczenie otrzymanych należności na PLN
                payment_amount = payment.amount * payment_exchange_rate.rates[0].mid
                logger.debug(f"Payment amount in PLN: {payment_amount}")
                # Obliczenie różnicy między kwotami
                exchange_rate_difference = payment_amount - invoice_amount

            rounded_exchange_rate_difference = round(exchange_rate_difference, 2)
            self.data.invoices[invoice_index].payments[
                payment_index
            ].exchange_rate_difference = rounded_exchange_rate_difference

            self.data.invoices[invoice_index].payments[
                payment_index
            ].exchange_rate = payment_exchange_rate
            self.data.invoices[invoice_index].exchange_rate = invoice_exchange_rate
        except ValueError as e:
            logger.error(f"Payment not found. {e}")
            return exchange_rate_difference
        except NBPApiError as e:
            raise NBPApiError(e) from e
        else:
            return rounded_exchange_rate_difference
