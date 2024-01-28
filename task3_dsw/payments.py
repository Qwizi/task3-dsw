"""Payments module."""
from __future__ import annotations

import csv
import uuid  # noqa: TCH003
from pathlib import Path

from task3_dsw import settings
from task3_dsw.invoices import Invoice


class Payment(Invoice):
    """Payment model."""

    invoice_id: uuid.UUID


def create_payments_file() -> None:
    """Create payments file."""
    if not Path.exists(Path(settings.PAYMENTS_FILE_PATH)):
        with Path.open(settings.PAYMENTS_FILE_PATH, "w", newline="") as payments_file:
            writer = csv.writer(payments_file)
            writer.writerow(["id", "invoice_id", "amount", "currency", "date"])


def add_payment_to_file(data: Payment) -> Payment:
    """
    Add payment to file.

    Example:
    -------
    ```python
    from task3_dsw.payments import add_payment_to_file, Payment

    payment = add_payment_to_file(data=Payment(
        invoice_id="123e4567-e89b-12d3-a456-426614174000",
        amount=100,
        currency="USD",
        date="2021-01-01",
    ))
    ```

    Args:
    ----
        file_path: Path to file.
        data: Payment to be added.

    Returns:
    -------
        Payment: Added payment.
    """
    with Path.open(settings.PAYMENTS_FILE_PATH, "a", newline="") as payments_file:
        writer = csv.writer(payments_file)
        writer.writerow(
            [
                data.id,
                data.invoice_id,
                data.amount,
                data.currency,
                data.date,
            ]
        )
        return data


def get_payment_from_file(**kwargs: str) -> Payment:
    """
    Get payment.

    Args:
    ----
        **kwargs: Keyword arguments.

    Returns:
    -------
        Payment: Payment.
    """
    with Path.open(settings.PAYMENTS_FILE_PATH, "r", newline="") as payments_file:
        reader = csv.reader(payments_file)
        next(reader)
        for row in reader:
            if (
                kwargs.get("payment_id") and row[0] == str(kwargs.get("payment_id"))
            ) or (kwargs.get("invoice_id") and row[1] == str(kwargs.get("invoice_id"))):
                return Payment(
                    id=row[0],
                    invoice_id=row[1],
                    amount=row[2],
                    currency=row[3],
                    date=row[4],
                )
        return None


def get_payments_from_file(invoice_id: uuid.UUID) -> list[Payment]:
    """
    Get payments from file.

    Args:
    ----
        file_path: Path to file.
        invoice_id: Invoice id to be searched.

    Returns:
    -------
        list[Payment]: List of payments.
    """
    with Path.open(settings.PAYMENTS_FILE_PATH, "r", newline="") as payments_file:
        reader = csv.reader(payments_file)
        return [
            Payment(
                id=row[0],
                invoice_id=row[1],
                amount=row[2],
                currency=row[3],
                date=row[4],
            )
            for row in reader
            if row[1] == str(invoice_id)
        ]
