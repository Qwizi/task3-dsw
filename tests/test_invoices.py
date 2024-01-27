import csv
import datetime
from pathlib import Path
import tempfile

import pytest

from task3_dsw import settings

from task3_dsw.invoices import Invoice, create_invoices_file, add_invoice_to_file, get_invoice_from_file

def test_create_invoices_file():
    with tempfile.TemporaryDirectory() as tmpdirname:
        invoices_file_path = tmpdirname + "/invoices.csv"
        settings.INVOICES_FILE_PATH = invoices_file_path
        create_invoices_file()
        assert Path.exists(Path(invoices_file_path))

def test_create_invoice_file_already_exists():
    with tempfile.TemporaryDirectory() as tmpdirname:
        invoices_file_path = tmpdirname + "/invoices.csv"
        settings.INVOICES_FILE_PATH = invoices_file_path
        Path(invoices_file_path).touch()
        create_invoices_file()
        assert Path.exists(Path(invoices_file_path))


def test_add_invoice_to_file():
    with tempfile.TemporaryDirectory() as tmpdirname:
        invoices_file_path = tmpdirname + "/invoices.csv"
        settings.INVOICES_FILE_PATH = invoices_file_path

        create_invoices_file()
        invoice = add_invoice_to_file(data=Invoice(amount=100, currency="USD", date="2021-01-01"))
        assert invoice.id is not None
        assert invoice.amount == 100
        assert invoice.currency == "USD"
        assert str(invoice.date) == "2021-01-01"

        with Path.open(invoices_file_path, "r", newline="") as invoices_file:
            reader = csv.reader(invoices_file)
            next(reader)
            for row in reader:
                assert row[0] == str(invoice.id)
                assert row[1] == str(invoice.amount)
                assert row[2] == str(invoice.currency)
                assert row[3] == str(invoice.date)

def test_get_invoice_from_file():
    with tempfile.TemporaryDirectory() as tmpdirname:
        invoices_file_path = tmpdirname + "/invoices.csv"
        settings.INVOICES_FILE_PATH = invoices_file_path
        create_invoices_file()
        invoice = add_invoice_to_file(data=Invoice(amount=100, currency="USD", date="2021-01-01"))
        invoice_from_file = get_invoice_from_file(invoice.id)
        assert invoice_from_file == invoice

        with Path.open(invoices_file_path, "r", newline="") as invoices_file:
            reader = csv.reader(invoices_file)
            next(reader)
            for row in reader:
                assert row[0] == str(invoice_from_file.id)
                assert row[1] == str(invoice_from_file.amount)
                assert row[2] == str(invoice_from_file.currency)
                assert row[3] == str(invoice_from_file.date)

def test_get_invoice_from_with_invalid_id():
    with tempfile.TemporaryDirectory() as tmpdirname:
        invoices_file_path = tmpdirname + "/invoices.csv"
        settings.INVOICES_FILE_PATH = invoices_file_path
        create_invoices_file()
        add_invoice_to_file(data=Invoice(amount=100, currency="USD", date="2021-01-01"))
        invoice_from_file = get_invoice_from_file("invalid_id")
        assert invoice_from_file is None

def test_get_invoice_from_file_when_file_not_exits():
    with tempfile.TemporaryDirectory() as tmpdirname:
        invoices_file_path = tmpdirname + "/invoices.csv"
        settings.INVOICES_FILE_PATH = invoices_file_path
        with pytest.raises(FileNotFoundError):
            get_invoice_from_file("invalid_id")    