"""Payments module."""
from __future__ import annotations

import csv
import datetime  # noqa: TCH003
import uuid
from pathlib import Path

from pydantic import BaseModel, Field

payments_file_path = "./data/payments.csv"


class Payment(BaseModel):
    """Payment model."""

    id: uuid.UUID = Field(default_factory=uuid.uuid4)  # noqa: A003
    invoice_id: uuid.UUID
    amount: float
    currency: str
    transaction_date: datetime.date


def create_payments_file() -> None:
    """Create payments file."""
    if not Path.exists(Path(payments_file_path)):
        with Path.open(payments_file_path, "w", newline="") as payments_file:
            writer = csv.writer(payments_file)
            writer.writerow(["id", "invoice_id", "amount", "currency", "date"])


def add_payment_to_file(data: Payment) -> Payment:
    """
    Add payment to file.

    Args:
    ----
        data: Payment to be added.

    Returns:
    -------
        Payment: Added payment.
    """
    with Path.open(payments_file_path, "a", newline="") as payments_file:
        writer = csv.writer(payments_file)
        writer.writerow(
            [
                data.id,
                data.invoice_id,
                data.amount,
                data.currency,
                data.transaction_date,
            ]
        )
        return data


def get_payments_from_file(invoice_id: uuid.UUID) -> list[Payment]:
    """
    Get payments from file.

    Args:
    ----
        invoice_id: Invoice id to be searched.

    Returns:
    -------
        list[Payment]: List of payments.
    """
    with Path.open(payments_file_path, "r", newline="") as payments_file:
        reader = csv.reader(payments_file)
        return [
            Payment(
                id=row[0],
                invoice_id=row[1],
                amount=row[2],
                currency=row[3],
                transaction_date=row[4],
            )
            for row in reader
            if row[1] == invoice_id
        ]
