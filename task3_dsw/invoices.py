"""Invoices module."""
import csv
import datetime
import uuid
from pathlib import Path

from pydantic import BaseModel, Field

invoices_file_path = "./data/invoices.csv"


class Invoice(BaseModel):
    """Invoice model."""

    id: uuid.UUID = Field(default_factory=uuid.uuid4)  # noqa: A003
    amount: float
    currency: str
    date: datetime.date


def create_invoices_file() -> None:
    """Create invoices file."""
    if not Path.exists(Path(invoices_file_path)):
        with Path.open(invoices_file_path, "w", newline="") as invoices_file:
            writer = csv.writer(invoices_file)
            writer.writerow(["id", "amount", "currency", "date"])


def add_invoice_to_file(data: Invoice) -> None:
    """
    Add invoice to file.

    Args:
    ----
        data: Invoice to be added.

    Returns:
    -------
        Invoice: Added invoice.
    """
    with Path.open(invoices_file_path, "a", newline="") as invoices_file:
        writer = csv.writer(invoices_file)
        writer.writerow([data.id, data.amount, data.currency, data.date])
        return data


def get_invoice_from_file(invoice_id: uuid.UUID) -> Invoice:
    """
    Get invoice from file.

    Args:
    ----
        invoice_id: Invoice id to be searched.

    Returns:
    -------
        Invoice: Found invoice.
    """
    with Path.open(invoices_file_path, "r", newline="") as invoices_file:
        reader = csv.reader(invoices_file)
        for row in reader:
            if row[0] == invoice_id:
                return Invoice(id=row[0], amount=row[1], currency=row[2], date=row[3])
        return None