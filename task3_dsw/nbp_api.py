"""Api Narodowego Banku Polskiego."""

import httpx


class NBPApiClient:
    """Class for making requests to Narodowego Banku Polskiego."""

    def __init__(self, api_url: str) -> None:
        """Initialize NBPApiClient with given api_url."""
        self.api_url = api_url
        self.headers = {"Accept": "application/json"}
        self.client = httpx.Client(base_url=self.api_url, headers=self.headers)

    def is_valid_currency_code(self, currency_code: str) -> bool:
        """
        Check if given currency code is valid.

        Args:
        ----
            currency_code: Currency code to be checked.

        Returns:
        -------
            True if currency code is valid, False otherwise.
        """
        currences_code = ["EUR", "USD", "GBP"]
        return currency_code in currences_code

    def get_exchange_rate(self, currency_code: str) -> dict:
        """
        Get exchange rate for given currency code.

        Args:
        ----
            currency_code: Currency code for which exchange rate will be returned.

        Returns:
        -------
            Exchange rate for given currency code.
        """
        if not self.is_valid_currency_code(currency_code):
            msg = "Invalid currency code."
            raise ValueError(msg)

        return self.client.get(f"exchangerates/rates/a/{currency_code}/").json()
