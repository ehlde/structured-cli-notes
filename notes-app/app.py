import logging
import sys
from pathlib import Path

from config import (
    CONFIG_DIR,
    Config,
    create_default_config_if_not_exists,
    load_last_config,
    save_last_config,
    setup_signal_handlers,
)
from yf_api import get_company_name_from_ticker

logger = logging.getLogger("notes_app")


def setup_logging() -> None:
    """Set up logging configuration."""
    logging.basicConfig(
        stream=sys.stdout,
        level=logging.INFO,
        format="%(asctime)s - %(levelname)s - %(message)s",
    )
    logging.info("Logging setup complete.")


def initial_setup() -> None:
    """Perform initial setup for the application."""

    if not CONFIG_DIR.exists():
        print("Config directory does not exist, do you want to create it? (y/n)")
        if input().strip().lower() == "y":
            CONFIG_DIR.mkdir(parents=True, exist_ok=True)
            logger.info(f"Created config directory: {CONFIG_DIR}")
        else:
            print(
                "Exiting application. \n"
                "Please create the config directory manually or restart the program."
            )
            sys.exit(0)

    create_default_config_if_not_exists()


def main():
    initial_setup()
    setup_logging()

    # Try to load the last used config, or use default
    config = load_last_config()
    
    # Setup signal handlers for graceful shutdown
    setup_signal_handlers(config)

    for ticker in config.contents.get("tickers", []):
        company_name = get_company_name_from_ticker(ticker)
        logger.info(f"Ticker: {ticker}, Company Name: {company_name}")
    
    # Save config on normal exit too
    save_last_config(config.config_path)


if __name__ == "__main__":
    main()
