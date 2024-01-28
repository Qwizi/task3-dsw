"""Invoices module."""
from __future__ import annotations

import csv
import datetime  # noqa: TCH003
import uuid
from pathlib import Path

from pydantic import BaseModel, Field, field_validator

from task3_dsw import settings


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


def create_invoices_file() -> None:
    """Create invoices file."""
    if not Path.exists(Path(settings.INVOICES_FILE_PATH)):
        with Path.open(settings.INVOICES_FILE_PATH, "w", newline="") as invoices_file:
            writer = csv.writer(invoices_file)
            writer.writerow(["id", "amount", "currency", "date"])


def add_invoice_to_file(data: Invoice) -> Invoice:
    """
    Add invoice to file.

    Example:
    -------
    ```python

    from task3_dsw.invoices import add_invoice_to_file, Invoice

    invoice = add_invoice_to_file(data=Invoice(
        amount=100,
        currency="USD",
        date="2021-01-01",
    ))
    ```

    Args:
    ----
        data: Invoice to be added.

    Returns:
    -------
        Invoice: Added invoice.
    """
    with Path.open(settings.INVOICES_FILE_PATH, "a", newline="") as invoices_file:
        writer = csv.writer(invoices_file)
        writer.writerow([data.id, data.amount, data.currency, data.date])
        return data


def get_invoice_from_file(invoice_id: uuid.UUID) -> Invoice or None:
    """
    Get invoice from file.

    Args:
    ----
        invoice_id: Invoice id to be searched.

    Returns:
    -------
        Invoice: Invoice if found, None otherwise.
    """
    with Path.open(settings.INVOICES_FILE_PATH, "r", newline="") as invoices_file:
        reader = csv.reader(invoices_file)
        next(reader)
        for row in reader:
            if row[0] == str(invoice_id):
                return Invoice(id=row[0], amount=row[1], currency=row[2], date=row[3])
        return None


def get_invoices_from_file() -> list[Invoice]:
    """
    Get invoices from file.

    Returns
    -------
        List[Invoice]: List of invoices.
    """
    with Path.open(settings.INVOICES_FILE_PATH, "r", newline="") as invoices_file:
        reader = csv.reader(invoices_file)
        next(reader)
        return [
            Invoice(id=row[0], amount=row[1], currency=row[2], date=row[3])
            for row in reader
        ]
