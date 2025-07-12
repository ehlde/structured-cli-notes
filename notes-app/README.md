# Notes App

App for notes with stock market data integration.

## Running Tests

### Quick Commands
```bash
# Run all unit tests (recommended)
python run_tests.py unit

# Run all tests
python run_tests.py all

# Run with coverage (if installed)
python run_tests.py coverage

# Run integration tests only
python run_tests.py slow
```

### Direct pytest Commands
```bash
# Unit tests only
uv run pytest tests/ -v -k "not TestIntegration"

# All tests
uv run pytest tests/ -v

# With coverage
uv run pytest tests/ --cov=yf_api --cov-report=term-missing
```

## Dependencies

Install dependencies with:
```bash
uv sync
```
