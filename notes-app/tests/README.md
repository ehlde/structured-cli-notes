# Tests for yf_api.py

This directory contains comprehensive tests for the `yf_api.py` module.

## Test Structure

- `test_yf_api.py`: Main test file containing unit tests for all functions
- `conftest.py`: Shared pytest configuration and fixtures
- `__init__.py`: Makes this directory a Python package

## Running Tests

### Run All Tests
```bash
pytest
```

### Run Tests with Verbose Output
```bash
pytest -v
```

### Run Only Fast Tests (Skip Integration Tests)
```bash
pytest -m "not slow"
```

### Run Only Integration Tests
```bash
pytest -m slow
```

### Run with Coverage (if coverage is installed)
```bash
pytest --cov=yf_api
```

## Test Categories

### Unit Tests
- **Market Enum Tests**: Verify the Market enum values
- **get_company_name_from_ticker Tests**: Test company name retrieval with mocking
- **get_current_stock_price Tests**: Test current price retrieval with mocking  
- **get_historical_prices Tests**: Test historical price retrieval with mocking

### Integration Tests
- **Real API Tests**: Tests that make actual API calls (marked as `slow`)

## Test Features

### Mocking
All unit tests use `unittest.mock` to mock the `yfinance` library calls, ensuring:
- Tests run quickly without network calls
- Tests are deterministic and reliable
- Tests can simulate error conditions

### Edge Cases Covered
- Empty data responses
- API errors (ValueError)
- Missing data fields
- Single data point scenarios
- Invalid ticker symbols

### Fixtures
Common test data is provided through pytest fixtures:
- `sample_stock_info`: Mock stock information
- `sample_historical_data`: Mock historical price data
- `empty_historical_data`: Empty data for edge cases
- `mock_ticker_factory`: Factory for creating mock ticker objects

## Adding New Tests

When adding new functionality to `yf_api.py`, please:

1. Add corresponding unit tests with mocking
2. Test edge cases and error conditions
3. Add integration tests if needed (mark with `@pytest.mark.slow`)
4. Update this README if new test categories are added

## Dependencies

The tests require:
- `pytest>=8.0.0`
- `pandas>=2.3.0`
- `yfinance>=0.2.65` (for integration tests)

These are automatically installed when running `uv sync` in the project root.
