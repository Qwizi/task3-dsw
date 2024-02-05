"""Settings for task3_dsw."""
from __future__ import annotations

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """
    Settings for task3_dsw.

    Attributes
    ----------
        DEBUG: bool - debug mode
        CURRENCIES: list[str] - list of valid currencies

    """

    DEBUG: bool = False
    DATABASE_PATH: str = "./data/database.json"
    CURRENCIES: list[str] = ["EUR", "USD", "GBP", "PLN"]


settings = Settings()
