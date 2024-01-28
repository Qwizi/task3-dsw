
import csv
from pathlib import Path
import tempfile

import pytest


from task3_dsw import settings
from task3_dsw.payments import Payment, add_payment_to_file, create_payments_file, get_payment_from_file, get_payments_from_file


def test_create_payments_file():
    with tempfile.TemporaryDirectory() as tmpdirname:
        payments_file_path = tmpdirname + "/payments.csv"
        settings.PAYMENTS_FILE_PATH = payments_file_path
        create_payments_file()
        assert Path.exists(Path(payments_file_path))

def test_create_payments_file_already_exists():
    with tempfile.TemporaryDirectory() as tmpdirname:
        payments_file_path = tmpdirname + "/payments.csv"
        settings.PAYMENTS_FILE_PATH = payments_file_path
        Path(payments_file_path).touch()
        create_payments_file()
        assert Path.exists(Path(payments_file_path))

def test_add_invoice_to_file(test_payment_schema: Payment):
    with tempfile.TemporaryDirectory() as tmpdirname:
        payments_file_path = tmpdirname + "/payments.csv"
        settings.PAYMENTS_FILE_PATH = payments_file_path
        create_payments_file()
        payment = add_payment_to_file(data=test_payment_schema)
        assert payment.id is not None
        assert payment.amount == test_payment_schema.amount
        assert payment.currency == test_payment_schema.currency
        assert payment.date == test_payment_schema.date

        with Path.open(payments_file_path, "r", newline="") as payments_file:
            reader = csv.reader(payments_file)
            next(reader)
            for row in reader:
                assert row[0] == str(payment.id)
                assert row[1] == str(payment.invoice_id)
                assert row[2] == str(payment.amount)
                assert row[3] == str(payment.currency)
                assert row[4] == str(payment.date)


@pytest.mark.parametrize("type", ["payment_id", "invoice_id"])
def test_get_payment_from_file(type, test_payment_schema: Payment):
    with tempfile.TemporaryDirectory() as tmpdirname:
        payments_file_path = tmpdirname + "/payments.csv"
        settings.PAYMENTS_FILE_PATH = payments_file_path
        create_payments_file()
        payment = add_payment_to_file(data=test_payment_schema)
        payment_from_file = None
        if type == "payment_id":
            payment_from_file = get_payment_from_file(payment_id=payment.id)
        elif type == "invoice_id":
            payment_from_file = get_payment_from_file(invoice_id=payment.invoice_id)
        assert payment_from_file == payment

        with Path.open(payments_file_path, "r", newline="") as payments_file:
            reader = csv.reader(payments_file)
            next(reader)
            for row in reader:
                assert row[0] == str(payment_from_file.id)
                assert row[1] == str(payment_from_file.invoice_id)
                assert row[2] == str(payment_from_file.amount)
                assert row[3] == str(payment_from_file.currency)
                assert row[4] == str(payment_from_file.date)


@pytest.mark.parametrize("type", ["payment_id", "invoice_id"])
def test_get_test_get_payment_from_file_with_invalid_id(type, test_payment_schema: Payment):
    with tempfile.TemporaryDirectory() as tmpdirname:
        payments_file_path = tmpdirname + "/payments.csv"
        settings.PAYMENTS_FILE_PATH = payments_file_path
        create_payments_file()
        payment = add_payment_to_file(data=test_payment_schema)
        payment_from_file = None
        if type == "payment_id":
            payment_from_file = get_payment_from_file(payment_id="invalid_id")
        elif type == "invoice_id":
            payment_from_file = get_payment_from_file(invoice_id="invalid_id")
        assert payment_from_file is None

        with Path.open(payments_file_path, "r", newline="") as payments_file:
            reader = csv.reader(payments_file)
            next(reader)
            for row in reader:
                assert row[0] == str(payment.id)
                assert row[1] == str(payment.invoice_id)
                assert row[2] == str(payment.amount)
                assert row[3] == str(payment.currency)
                assert row[4] == str(payment.date)


def test_get_payments_from_file(test_payment_schema: Payment):
    with tempfile.TemporaryDirectory() as tmpdirname:
        payments_file_path = tmpdirname + "/payments.csv"
        settings.PAYMENTS_FILE_PATH = payments_file_path
        create_payments_file()
        add_payment_to_file(data=test_payment_schema)
        payments_from_file = get_payments_from_file(test_payment_schema.invoice_id)
        assert len(payments_from_file) == 1
        assert payments_from_file[0] == test_payment_schema
        