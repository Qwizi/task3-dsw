from pathlib import Path
import tempfile
from unittest.mock import Mock
import pytest
from task3_dsw.database import Database, Invoice, InvoiceStatus
from task3_dsw.database import Payment
from task3_dsw.nbp_api import NBPApiClient

from task3_dsw.settings import Settings

@pytest.fixture
def settings():
    return Settings()


@pytest.fixture
def nbp_api_client_mock():
    """Mock for NBPApiClient."""
    return Mock()

@pytest.fixture
def nbp_api_client():
    """Mock for NBPApiClient."""
    return NBPApiClient()

@pytest.fixture
def test_invoice_schema():
    _id = "f48f03f8-ed21-4b6f-a2a3-a3158daa669b"
    return Invoice(
        id=_id,
        amount=100,
        currency="USD",
        date="2021-01-01",
        exchange_rate=None,
        status=InvoiceStatus.UNPAID,
    )

@pytest.fixture
def test_payment_schema(test_invoice_schema: Invoice):
    _id = "3236cbeb-a61b-4850-9a0e-c1fdbd772c4d"
    return Payment(
        id=_id,
        invoice_id=test_invoice_schema.id,
        amount=100,
        currency="USD",
        date="2021-01-01",
        exchange_rate_difference=0.0,
        exchange_rate=None
    )

@pytest.fixture
def test_database(settings, nbp_api_client):
    """Create temporary database.json file."""
    with tempfile.TemporaryDirectory() as tmpdirname:
        database_path = tmpdirname + "/database.json"
        settings.DATABASE_PATH = database_path
        database = Database(settings=settings, nbp_api_client=nbp_api_client)
        database.load()
        yield database