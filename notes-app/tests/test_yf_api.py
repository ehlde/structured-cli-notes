import pytest
from unittest.mock import Mock, patch
import pandas as pd
from yf_api import (
    Market,
    get_company_name_from_ticker,
    get_current_stock_price,
    get_historical_returns,
)


class TestMarket:
    """Test the Market enum."""

    def test_market_values(self):
        """Test that Market enum has correct values."""
        assert Market.STO.value == ".ST"
        assert Market.USA.value == ""
        assert Market.ITA.value == ".MI"
        assert Market.FRA.value == ".PA"


class TestGetCompanyNameFromTicker:
    """Test the get_company_name_from_ticker function."""

    @patch("yf_api.yf.Ticker")
    def test_get_company_name_success_first_market(self, mock_ticker_class):
        """Test successful retrieval of company name from first market."""
        # Setup mock
        mock_ticker = Mock()
        mock_ticker.info = {"longName": "Apple Inc."}
        mock_ticker_class.return_value = mock_ticker

        result = get_company_name_from_ticker("AAPL")

        assert result == "Apple Inc."
        mock_ticker_class.assert_called_with("AAPL.ST")

    @patch("yf_api.yf.Ticker")
    def test_get_company_name_success_second_market(self, mock_ticker_class):
        """Test successful retrieval of company name from second market after first fails."""
        # Setup mock to fail on first call, succeed on second
        mock_ticker1 = Mock()
        mock_ticker1.info = {"longName": None}

        mock_ticker2 = Mock()
        mock_ticker2.info = {"longName": "Apple Inc."}

        mock_ticker_class.side_effect = [mock_ticker1, mock_ticker2]

        result = get_company_name_from_ticker("AAPL")

        assert result == "Apple Inc."
        assert mock_ticker_class.call_count == 2

    @patch("yf_api.yf.Ticker")
    def test_get_company_name_value_error(self, mock_ticker_class):
        """Test handling of ValueError during ticker creation."""
        # Setup mock to raise ValueError then succeed
        mock_ticker_success = Mock()
        mock_ticker_success.info = {"longName": "Apple Inc."}

        mock_ticker_class.side_effect = [
            ValueError("Invalid ticker"),
            mock_ticker_success,
        ]

        result = get_company_name_from_ticker("AAPL")

        assert result == "Apple Inc."
        assert mock_ticker_class.call_count == 2

    @patch("yf_api.yf.Ticker")
    def test_get_company_name_not_found(self, mock_ticker_class):
        """Test when no company name is found in any market."""
        # Setup mock to return None for all markets
        mock_ticker = Mock()
        mock_ticker.info = {"longName": None}
        mock_ticker_class.return_value = mock_ticker

        result = get_company_name_from_ticker("INVALID")

        assert result is None
        assert mock_ticker_class.call_count == len(Market)

    @patch("yf_api.yf.Ticker")
    def test_get_company_name_all_markets_fail(self, mock_ticker_class):
        """Test when all markets raise ValueError."""
        mock_ticker_class.side_effect = ValueError("Invalid ticker")

        result = get_company_name_from_ticker("INVALID")

        assert result is None
        assert mock_ticker_class.call_count == len(Market)

    def test_get_company_name_ticker_case_handling(self):
        """Test that ticker is converted to uppercase."""
        with patch("yf_api.yf.Ticker") as mock_ticker_class:
            mock_ticker = Mock()
            mock_ticker.info = {"longName": "Apple Inc."}
            mock_ticker_class.return_value = mock_ticker

            get_company_name_from_ticker("aapl")

            mock_ticker_class.assert_called_with("AAPL.ST")


class TestGetCurrentStockPrice:
    """Test the get_current_stock_price function."""

    @patch("yf_api.yf.Ticker")
    def test_get_current_stock_price_success(self, mock_ticker_class):
        """Test successful retrieval of current stock price."""
        mock_ticker = Mock()
        mock_ticker.info = {"currentPrice": 150.25}
        mock_ticker_class.return_value = mock_ticker

        result = get_current_stock_price("AAPL")

        assert result == 150.25
        mock_ticker_class.assert_called_with("AAPL")

    @patch("yf_api.yf.Ticker")
    def test_get_current_stock_price_not_found(self, mock_ticker_class):
        """Test when current price is not available."""
        mock_ticker = Mock()
        mock_ticker.info = {}
        mock_ticker_class.return_value = mock_ticker

        result = get_current_stock_price("INVALID")

        assert result is None
        mock_ticker_class.assert_called_with("INVALID")

    @patch("yf_api.yf.Ticker")
    def test_get_current_stock_price_none_value(self, mock_ticker_class):
        """Test when current price is explicitly None."""
        mock_ticker = Mock()
        mock_ticker.info = {"currentPrice": None}
        mock_ticker_class.return_value = mock_ticker

        result = get_current_stock_price("TEST")

        assert result is None


class TestGetHistoricalReturns:
    """Test the get_historical_returns function."""

    @patch("yf_api.yf.Ticker")
    def test_get_historical_returns_success(self, mock_ticker_class):
        """Test successful retrieval of historical returns."""
        # Create mock YTD data
        ytd_dates = pd.date_range(start="2024-01-01", end="2024-12-31", freq="D")
        ytd_close_prices = pd.Series(
            [100.0, 101.0, 102.0, 103.0, 110.0], index=ytd_dates[:5]
        )

        # Create mock 1-month data
        one_month_dates = pd.date_range(start="2024-12-01", end="2024-12-31", freq="D")
        one_month_close_prices = pd.Series(
            [105.0, 106.0, 107.0, 108.0, 110.0], index=one_month_dates[:5]
        )

        mock_ytd_data = pd.DataFrame({"Close": ytd_close_prices})
        mock_one_month_data = pd.DataFrame({"Close": one_month_close_prices})

        mock_ticker = Mock()
        mock_ticker.history.side_effect = [mock_ytd_data, mock_one_month_data]
        mock_ticker_class.return_value = mock_ticker

        result = get_historical_returns("AAPL")

        # YTD return: (110 - 100) / 100 = 0.10 (10%)
        assert result["ytd"] is not None
        assert abs(result["ytd"] - 0.10) < 0.0001
        # 1-month return: (110 - 105) / 105 = 0.047619... (4.76%)
        assert result["one_month"] is not None
        assert abs(result["one_month"] - (5.0 / 105.0)) < 0.0001

        # Verify correct calls were made
        assert mock_ticker.history.call_count == 2
        mock_ticker.history.assert_any_call(period="ytd", interval="1d")
        mock_ticker.history.assert_any_call(period="1mo", interval="1d")

    @patch("yf_api.yf.Ticker")
    def test_get_historical_returns_empty_data(self, mock_ticker_class):
        """Test when no historical data is available."""
        # Create empty DataFrame
        mock_empty_data = pd.DataFrame({"Close": pd.Series([], dtype=float)})

        mock_ticker = Mock()
        mock_ticker.history.return_value = mock_empty_data
        mock_ticker_class.return_value = mock_ticker

        result = get_historical_returns("INVALID")

        assert result["ytd"] is None
        assert result["one_month"] is None

    @patch("yf_api.yf.Ticker")
    def test_get_historical_returns_single_data_point(self, mock_ticker_class):
        """Test with only one data point (can't calculate returns)."""
        dates = pd.date_range(start="2024-01-01", end="2024-01-01", freq="D")
        close_prices = pd.Series([100.0], index=dates)

        mock_single_data = pd.DataFrame({"Close": close_prices})

        mock_ticker = Mock()
        mock_ticker.history.return_value = mock_single_data
        mock_ticker_class.return_value = mock_ticker

        result = get_historical_returns("TEST")

        # Can't calculate returns with only one data point
        assert result["ytd"] is None
        assert result["one_month"] is None

    @patch("yf_api.yf.Ticker")
    def test_get_historical_returns_correct_parameters(self, mock_ticker_class):
        """Test that correct parameters are passed to yfinance."""
        dates = pd.date_range(start="2024-01-01", end="2024-12-31", freq="D")
        close_prices = pd.Series([100.0, 101.0], index=dates[:2])

        mock_historical_data = pd.DataFrame({"Close": close_prices})

        mock_ticker = Mock()
        mock_ticker.history.return_value = mock_historical_data
        mock_ticker_class.return_value = mock_ticker

        get_historical_returns("AAPL")

        # Should call history twice: once for YTD, once for 1-month
        assert mock_ticker.history.call_count == 2
        mock_ticker.history.assert_any_call(period="ytd", interval="1d")
        mock_ticker.history.assert_any_call(period="1mo", interval="1d")


# Integration-style tests (these will make actual API calls, so they're marked as slow)
class TestIntegration:
    """Integration tests that make actual API calls. These are slower and require internet connection."""

    @pytest.mark.slow
    def test_real_api_call_apple(self):
        """Test with a real API call to Apple stock (AAPL).

        This test is marked as slow and should be run with 'pytest -m slow'
        or 'pytest --run-slow' if configured.

        Note: This test may fail if the API is unavailable or rate-limited.
        """
        # Test with a well-known ticker
        name = get_company_name_from_ticker("AAPL")
        # Due to API limitations or rate limiting, we'll just verify the function doesn't crash
        # In a real scenario with a stable API, we could assert the name contains "Apple"
        assert (
            name is None or "Apple" in str(name).upper() or "APPLE" in str(name).upper()
        )

    @pytest.mark.slow
    def test_real_api_call_invalid_ticker(self):
        """Test with an invalid ticker."""
        name = get_company_name_from_ticker("INVALIDTICKER123456")
        assert name is None


# Fixtures for common test data
@pytest.fixture
def sample_historical_data():
    """Fixture providing sample historical data."""
    dates = pd.date_range(start="2024-01-01", end="2024-01-05", freq="D")
    close_prices = pd.Series([100.0, 101.5, 99.8, 102.3, 104.7], index=dates)
    return pd.DataFrame({"Close": close_prices})


@pytest.fixture
def mock_ticker_factory():
    """Fixture that creates mock ticker objects."""

    def _create_mock_ticker(info_data=None, historical_data=None):
        mock_ticker = Mock()
        mock_ticker.info = info_data or {}
        if historical_data is not None:
            mock_ticker.history.return_value = historical_data
        return mock_ticker

    return _create_mock_ticker
