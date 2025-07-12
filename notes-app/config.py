import json
import logging
import signal
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Dict

logger = logging.getLogger("notes_app.config")

CONFIG_DIR = Path.home() / ".config" / "notes-app"
CONFIG_DIR.mkdir(parents=True, exist_ok=True)
LAST_CONFIG_FILE = CONFIG_DIR / ".last_config"
DEFAULT_DATA_FILE_NAME = "scn_data.json"
DEFAULT_DATA_FILE = CONFIG_DIR / DEFAULT_DATA_FILE_NAME


@dataclass
class Config:
    """Configuration storage for the notes app."""

    config_path: Path
    contents: Dict


def save_last_config(file_path: Path) -> None:
    """Save the path of the last used config file."""
    LAST_CONFIG_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(LAST_CONFIG_FILE, "w") as f:
        f.write(str(file_path.absolute()))


def load_last_config() -> Config:
    """Load the last used config file, or fallback to default."""

    config_file_to_load = DEFAULT_DATA_FILE

    # Check if we have a last config file reference
    if LAST_CONFIG_FILE.exists():
        try:
            with open(LAST_CONFIG_FILE, "r") as f:
                last_config_path = Path(f.read().strip())
                if last_config_path.exists():
                    config_file_to_load = last_config_path
                    logger.info(f"Loading last used config: {config_file_to_load}")
                else:
                    logger.info(
                        f"Last config file {last_config_path} not found, using default"
                    )
        except (FileNotFoundError, IOError) as e:
            logger.warning(f"Error reading last config reference: {e}, using default")
    else:
        logger.info(
            f"No last config reference found, using default: {DEFAULT_DATA_FILE}"
        )

    # Load the actual config file
    try:
        with open(config_file_to_load, "r") as f:
            contents = json.load(f)
            return Config(config_path=config_file_to_load, contents=contents)
    except (FileNotFoundError, IOError, json.JSONDecodeError) as e:
        logger.error(f"Error loading config file {config_file_to_load}: {e}")
        # If even the default fails, create it and return empty config
        if config_file_to_load == DEFAULT_DATA_FILE:
            logger.info("Creating new default config file")
            default_contents = {"tickers": []}
            with open(DEFAULT_DATA_FILE, "w") as f:
                json.dump(default_contents, f, indent=2)
            return Config(config_path=DEFAULT_DATA_FILE, contents=default_contents)
        else:
            # Fall back to default if custom config failed
            logger.info("Falling back to default config")
            try:
                with open(DEFAULT_DATA_FILE, "r") as f:
                    contents = json.load(f)
                    return Config(config_path=DEFAULT_DATA_FILE, contents=contents)
            except (FileNotFoundError, IOError, json.JSONDecodeError):
                # Create default if it doesn't exist or is corrupted
                logger.info("Creating new default config file as fallback")
                default_contents = {"tickers": []}
                with open(DEFAULT_DATA_FILE, "w") as f:
                    json.dump(default_contents, f, indent=2)
                return Config(config_path=DEFAULT_DATA_FILE, contents=default_contents)


def create_default_config_if_not_exists() -> None:
    """Create a default data file if it doesn't exist."""
    if not DEFAULT_DATA_FILE.exists():
        with open(DEFAULT_DATA_FILE, "w") as f:
            json.dump({"tickers": []}, f, indent=2)
        logger.info(f"Created default data file: {DEFAULT_DATA_FILE}")


def setup_signal_handlers(config: Config) -> None:
    """Setup signal handlers for graceful shutdown."""

    def signal_handler(signum, frame):
        logger.info("Received interrupt signal, saving config...")
        save_last_config(config.config_path)
        logger.info(f"Config saved to {LAST_CONFIG_FILE}")
        sys.exit(0)

    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
