from unittest.mock import Mock
import pytest

from task3_dsw.settings import Settings

@pytest.fixture
def settings():
    return Settings()


@pytest.fixture
def nbp_api_client_mock():
    """Mock for NBPApiClient."""
    return Mock()