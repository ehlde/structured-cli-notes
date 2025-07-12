import yfinance as yf
from typing import Dict, Optional
from enum import Enum
from contextlib import redirect_stderr
from io import StringIO


class Market(Enum):
    STO = ".ST"
    USA = ""
    ITA = ".MI"
    FRA = ".PA"


def get_company_name_from_ticker(ticker: str) -> Optional[str]:
    for market in Market:
        ticker_extended = ticker.upper() + market.value
        print(ticker_extended)
        try:
            with redirect_stderr(StringIO()):  # Suppress stderr output
                stock = yf.Ticker(ticker_extended)
                name = stock.info.get("longName", None)
                if name is not None:
                    return name
        except ValueError:
            continue
    return None


def get_current_stock_price(ticker: str) -> Optional[float]:
    stock = yf.Ticker(ticker)
    return stock.info.get("currentPrice", None)


def get_historical_returns(ticker: str) -> Dict[str, Optional[float]]:
    """Fetches the 1-month and year-to-date returns for a given stock ticker.

    Returns:
        Dict with keys:
        - 'one_month': 1-month return as percentage (e.g., 0.05 for 5%)
        - 'ytd': Year-to-date return as percentage (e.g., 0.15 for 15%)
    """
    stock = yf.Ticker(ticker)

    # Get YTD data
    ytd_data = stock.history(period="ytd", interval="1d")
    # Get 1-month data
    one_month_data = stock.history(period="1mo", interval="1d")

    results: Dict[str, Optional[float]] = {"one_month": None, "ytd": None}

    # Calculate YTD return
    if not ytd_data.empty and len(ytd_data) > 1:
        ytd_start = ytd_data["Close"].iloc[0]
        ytd_latest = ytd_data["Close"].iloc[-1]
        results["ytd"] = (ytd_latest - ytd_start) / ytd_start

    # Calculate 1-month return
    if not one_month_data.empty and len(one_month_data) > 1:
        one_month_start = one_month_data["Close"].iloc[0]
        one_month_latest = one_month_data["Close"].iloc[-1]
        results["one_month"] = (one_month_latest - one_month_start) / one_month_start

    return results


if __name__ == "__main__":
    # Example usage
    ticker = "AAPL"
    print(f"Company Name: {get_company_name_from_ticker(ticker)}")
    print(f"Current Price: {get_current_stock_price(ticker)}")
    returns = get_historical_returns(ticker)
    print(
        f"1-Month Return: {returns['one_month']:.2%}"
        if returns["one_month"]
        else "1-Month Return: N/A"
    )
    print(f"YTD Return: {returns['ytd']:.2%}" if returns["ytd"] else "YTD Return: N/A")
