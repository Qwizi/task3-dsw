"""Database module."""
from __future__ import annotations

import datetime  # noqa: TCH003
import json
import uuid
from dataclasses import Field
from pathlib import Path
from venv import logger

from pydantic import BaseModel, ValidationError, field_validator

from task3_dsw import settings
from task3_dsw.settings import Settings  # noqa: TCH001


class Invoice(BaseModel):
    """Invoice model."""

    id: uuid.UUID = Field(default_factory=uuid.uuid4)  # noqa: A003, RUF100
    amount: float
    currency: str
    date: datetime.date

    @field_validator("currency")
    def currency_is_valid(cls, v) -> str:  # noqa: N805, ANN001
        """Validate currency code."""
        if v not in settings.CURRENCIES:
            msg = f"Currency code {v} is not valid."
            raise ValueError(msg)
        return v


class Payment(Invoice):
    """Payment model."""

    invoice_id: uuid.UUID


class DataSchema(BaseModel):
    """Schema for data."""

    invoices: list[Invoice]
    payments: list[Payment]


class Database:
    """Json file database."""

    def __init__(self, settings: Settings) -> None:
        """Initialize database."""
        self.settings = settings
        self.data = DataSchema(invoices=[], payments=[])

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
        except (json.decoder.JSONDecodeError, TypeError, ValidationError) as e:
            logger.error(e)

    def save(self) -> None:
        """Save data to json file."""
        with Path.open(self.settings.DATABASE_PATH, "w") as f:
            f.write(self.data.model_dump_json())

    def add_invoice(self, invoice: Invoice) -> Invoice:
        """Add invoice to database."""
        self.data.invoices.append(invoice)
        return invoice

    def add_payment(self, payment: Payment) -> Payment:
        """Add payment to database."""
        self.data.payments.append(payment)
        return payment

    def get_invoice(self, invoice_index: int) -> Invoice:
        """Get invoice from database."""
        try:
            return self.data.invoices[invoice_index]
        except IndexError:
            return None

    def get_invoices(self) -> list[Invoice]:
        """Get invoices from database."""
        return self.data.invoices

    def get_payment(self, payment_id: str) -> Payment:
        """Get payment from database."""
        for payment in self.data.payments:
            if payment.id == payment_id:
                return payment
        return None

    def get_payments(self) -> list[Payment]:
        """Get payments from database."""
        return self.data.payments
