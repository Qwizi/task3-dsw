import httpx
import pytest
from task3_dsw import settings
from task3_dsw.database import Invoice, Payment
from task3_dsw.nbp_api import ExchangeRateSchema, ExchangeRateSchemaResponse, NBPApiClient, RateSchema, NBPApiError

def test_invalid_exchange_rate_currency_code():
    with pytest.raises(ValueError):
        ExchangeRateSchema(code="xD", table="a", date="2021-01-04")

def test_valid_exchange_rate_currency_code():
    settings.CURRENCIES = ["CHF"]
    assert ExchangeRateSchema(code="CHF", table="a", date="2021-01-04").code == "CHF"


def test_get_exchange_rate_valid_code(nbp_api_client_mock):
    settings.CURRENCIES = ["EUR", "USD", "GBP"]
    data = ExchangeRateSchema(code="EUR", table="a", date="2024-01-02")
    mock_return_data = {'table': 'A', 'currency': 'euro', 'code': 'EUR', 'rates': [{'no': '001/A/NBP/2024', 'effectiveDate': '2024-01-02', 'mid': 4.3434}]}
    nbp_api_client_mock.get_exchange_rate.return_value = mock_return_data
    assert nbp_api_client_mock.get_exchange_rate(data) == mock_return_data

@pytest.mark.parametrize("error_code", [httpx.codes.NOT_FOUND, httpx.codes.BAD_REQUEST])
def test_get_exchange_rate_http_error(error_code, nbp_api_client_mock):
    data = ExchangeRateSchema(code="EUR", table="a", date="2024-01-02")
    if error_code == httpx.codes.NOT_FOUND:
        nbp_api_client_mock.get_exchange_rate.side_effect = NBPApiError("Not found [404 NotFound]")
    elif error_code == httpx.codes.BAD_REQUEST:
        nbp_api_client_mock.get_exchange_rate.side_effect = NBPApiError("Invalid Request. [400 BadRequest]")
    else:
        nbp_api_client_mock.get_exchange_rate.side_effect = httpx.HTTPError("An HTTP error occurred")
    with pytest.raises(NBPApiError):
        nbp_api_client_mock.get_exchange_rate(data)


def test_calculate_difference_same_currency(mocker):
    invoice = Invoice(id="edb009c4-203b-4197-9778-82356d475a20", currency="EUR", amount=100, date="2021-01-01")
    payment = Payment(id="6ee0c0e8-6b94-4720-9c52-164bc8470097", invoice_id=invoice.id, currency="EUR", amount=50, date="2021-01-02")
    nbp_api_client = NBPApiClient()
    invoice_exchange_rate, payment_exchange_rate, difference = nbp_api_client.calculate_difference(invoice, payment)
    assert invoice_exchange_rate is None
    assert payment_exchange_rate is None
    assert difference == 0


def test_calculate_difference_different_currency(mocker):
    invoice = Invoice(id="edb009c4-203b-4197-9778-82356d475a20", currency="PLN", amount=100, date="2021-01-01")
    payment = Payment(id="6ee0c0e8-6b94-4720-9c52-164bc8470097", invoice_id=invoice.id, currency="EUR", amount=50, date="2021-01-02")
    nbp_api_client = NBPApiClient()
    invoice_exchange_rate = ExchangeRateSchemaResponse(table="a", currency="euro", code="EUR", rates=[RateSchema(no="001/A/NBP/2021", effectiveDate="2021-01-01", mid=4.3434)])
    payment_exchange_rate = ExchangeRateSchemaResponse(table="a", currency="euro", code="EUR", rates=[RateSchema(no="001/A/NBP/2021", effectiveDate="2021-01-02", mid=3.6434)])
    mocker.patch.object(NBPApiClient, "get_exchange_rate", side_effect=[invoice_exchange_rate, payment_exchange_rate])
    invoice_exchange_rate, payment_exchange_rate, difference = nbp_api_client.calculate_difference(invoice, payment)
    assert invoice_exchange_rate == invoice_exchange_rate
    assert payment_exchange_rate == payment_exchange_rate
    assert difference == (payment_exchange_rate.rates[0].mid - invoice_exchange_rate.rates[0].mid) * invoice.amount