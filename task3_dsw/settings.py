"""Settings for task3_dsw."""
from __future__ import annotations

import typing

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """
    Settings for task3_dsw.

    Attributes
    ----------
        NBP_API_URL (str): URL of NBP API.
    """

    NBP_API_URL: str = "http://api.nbp.pl/api/"
    CURRENCIES: typing.ClassVar[list[str]] = ["EUR", "USD", "GBP"]


def get_settings() -> Settings:
    """Get settings for task3_dsw."""
    return Settings()
