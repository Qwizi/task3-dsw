"""Settings for task3_dsw."""
from __future__ import annotations

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """
    Settings for task3_dsw.

    Attributes
    ----------
        CURRENCIES: list[str] - list of valid currencies
        INVOICES_FILE_PATH: str - path to invoices file
        PAYMENTS_FILE_PATH: str - path to payments file
    """

    INVOICES_FILE_PATH: str = "./data/invoices.csv"
    PAYMENTS_FILE_PATH: str = "./data/payments.csv"
    CURRENCIES: list[str] = ["EUR", "USD", "GBP"]


settings = Settings()
