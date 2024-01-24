"""Settings for task3_dsw."""
from __future__ import annotations

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """
    Settings for task3_dsw.

    Attributes
    ----------
        CURRENCIES: list[str]
    """

    CURRENCIES: list[str] = ["EUR", "USD", "GBP"]
