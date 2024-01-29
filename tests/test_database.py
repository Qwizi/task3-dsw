
import tempfile
from task3_dsw.settings import settings
from task3_dsw.database import DataSchema, Database, Invoice, Payment


def test_database_load(test_database, test_invoice_schema: Invoice):
    """Test database load."""
    test_database.load()
    assert isinstance(test_database.data, DataSchema)
    assert test_database.data.invoices == []

    test_database.add_invoice(test_invoice_schema)
    test_database.save()

def test_database_add_invoice(test_database, test_invoice_schema: Invoice):
    """Test adding an invoice to the database."""
    initial_length = len(test_database.data.invoices)
    test_database.add_invoice(test_invoice_schema)
    assert len(test_database.data.invoices) == initial_length + 1
    assert test_database.data.invoices[-1] == test_invoice_schema

def test_database_add_payment(test_database, test_payment_schema: Payment):
    """Test adding a payment to the database."""
    initial_length = len(test_database.data.payments)
    test_database.add_payment(test_payment_schema)
    assert len(test_database.data.payments) == initial_length + 1
    assert test_database.data.payments[-1] == test_payment_schema

def test_database_get_invoice(test_database, test_invoice_schema: Invoice):
    """Test getting an invoice from the database."""
    test_database.add_invoice(test_invoice_schema)
    invoice = test_database.get_invoice(0)
    assert invoice == test_invoice_schema

def test_database_get_invoices(test_database, test_invoice_schema: Invoice):
    """Test getting all invoices from the database."""
    test_database.add_invoice(test_invoice_schema)
    invoices = test_database.get_invoices()
    assert len(invoices) == 1
    assert invoices[0] == test_invoice_schema

def test_database_get_payment(test_database, test_payment_schema: Payment):
    """Test getting a payment from the database."""
    test_database.add_payment(test_payment_schema)
    payment = test_database.get_payment(test_payment_schema.id)
    assert payment == test_payment_schema

def test_database_get_payments(test_database, test_payment_schema: Payment):
    """Test getting all payments from the database."""
    test_database.add_payment(test_payment_schema)
    payments = test_database.get_payments()
    assert len(payments) == 1
    assert payments[0] == test_payment_schema