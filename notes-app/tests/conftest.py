"""Shared pytest configuration and fixtures."""

import pytest
import pandas as pd
from unittest.mock import Mock


@pytest.fixture
def sample_stock_info():
    """Sample stock info data for testing."""
    return {"longName": "Apple Inc.", "currentPrice": 150.25, "symbol": "AAPL"}


@pytest.fixture
def sample_historical_data():
    """Sample historical price data for testing."""
    dates = pd.date_range(start="2024-01-01", end="2024-01-05", freq="D")
    close_prices = pd.Series([100.0, 101.5, 99.8, 102.3, 104.7], index=dates)
    return pd.DataFrame(
        {
            "Open": [99.5, 101.0, 100.5, 101.8, 103.2],
            "High": [101.0, 102.0, 100.8, 103.0, 105.0],
            "Low": [99.0, 100.5, 99.2, 101.5, 103.0],
            "Close": close_prices,
            "Volume": [1000000, 1100000, 950000, 1050000, 1200000],
        }
    )


@pytest.fixture
def empty_historical_data():
    """Empty historical data for testing edge cases."""
    return pd.DataFrame(
        {
            "Open": pd.Series([], dtype=float),
            "High": pd.Series([], dtype=float),
            "Low": pd.Series([], dtype=float),
            "Close": pd.Series([], dtype=float),
            "Volume": pd.Series([], dtype=int),
        }
    )


@pytest.fixture
def mock_ticker_factory():
    """Factory fixture for creating mock ticker objects."""

    def _create_mock_ticker(info_data=None, historical_data=None):
        mock_ticker = Mock()
        mock_ticker.info = info_data or {}
        if historical_data is not None:
            mock_ticker.history.return_value = historical_data
        return mock_ticker

    return _create_mock_ticker
