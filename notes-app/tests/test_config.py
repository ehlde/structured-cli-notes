import json
import tempfile
import pytest
from pathlib import Path
from unittest.mock import patch, mock_open

from config import (
    Config,
    save_last_config,
    load_last_config,
    create_default_config_if_not_exists,
    setup_signal_handlers,
    CONFIG_DIR,
    LAST_CONFIG_FILE,
    DEFAULT_DATA_FILE,
)


@pytest.fixture
def temp_config_dir():
    """Create a temporary config directory for testing."""
    with tempfile.TemporaryDirectory() as tmpdir:
        temp_dir = Path(tmpdir) / "test_config"
        temp_dir.mkdir(parents=True, exist_ok=True)
        
        with patch('config.CONFIG_DIR', temp_dir), \
             patch('config.LAST_CONFIG_FILE', temp_dir / ".last_config"), \
             patch('config.DEFAULT_DATA_FILE', temp_dir / "scn_data.json"):
            yield temp_dir


@pytest.fixture
def sample_config_content():
    """Sample config content for testing."""
    return {"tickers": ["AAPL", "GOOGL", "MSFT"]}


class TestConfig:
    """Test the Config dataclass."""
    
    def test_config_creation(self):
        """Test creating a Config instance."""
        path = Path("/test/path.json")
        contents = {"test": "data"}
        config = Config(config_path=path, contents=contents)
        
        assert config.config_path == path
        assert config.contents == contents


class TestSaveLastConfig:
    """Test the save_last_config function."""
    
    def test_save_last_config(self, temp_config_dir):
        """Test saving the last config path."""
        test_path = temp_config_dir / "custom_config.json"
        last_config_file = temp_config_dir / ".last_config"
        
        with patch('config.LAST_CONFIG_FILE', last_config_file):
            save_last_config(test_path)
        
        assert last_config_file.exists()
        with open(last_config_file, "r") as f:
            saved_path = f.read().strip()
        assert saved_path == str(test_path.absolute())
    
    def test_save_last_config_creates_parent_dirs(self):
        """Test that save_last_config creates parent directories if needed."""
        with tempfile.TemporaryDirectory() as tmpdir:
            nested_dir = Path(tmpdir) / "nested" / "config"
            last_config_file = nested_dir / ".last_config"
            test_path = Path("/test/config.json")
            
            with patch('config.LAST_CONFIG_FILE', last_config_file):
                # This should not raise an error even if parent dirs don't exist
                save_last_config(test_path)


class TestLoadLastConfig:
    """Test the load_last_config function."""
    
    def test_load_last_config_no_last_file(self, temp_config_dir, sample_config_content):
        """Test loading config when no last config file exists."""
        default_file = temp_config_dir / "scn_data.json"
        last_config_file = temp_config_dir / ".last_config"
        
        # Create default config file
        with open(default_file, "w") as f:
            json.dump(sample_config_content, f)
        
        with patch('config.DEFAULT_DATA_FILE', default_file), \
             patch('config.LAST_CONFIG_FILE', last_config_file):
            config = load_last_config()
        
        assert config.config_path == default_file
        assert config.contents == sample_config_content
    
    def test_load_last_config_with_valid_last_file(self, temp_config_dir, sample_config_content):
        """Test loading config when a valid last config file exists."""
        custom_config = temp_config_dir / "custom.json"
        default_file = temp_config_dir / "scn_data.json" 
        last_config_file = temp_config_dir / ".last_config"
        
        # Create custom config file
        custom_content = {"tickers": ["TSLA", "NVDA"]}
        with open(custom_config, "w") as f:
            json.dump(custom_content, f)
        
        # Create default config file
        with open(default_file, "w") as f:
            json.dump(sample_config_content, f)
        
        # Save reference to custom config
        with open(last_config_file, "w") as f:
            f.write(str(custom_config.absolute()))
        
        with patch('config.DEFAULT_DATA_FILE', default_file), \
             patch('config.LAST_CONFIG_FILE', last_config_file):
            config = load_last_config()
        
        assert config.config_path == custom_config
        assert config.contents == custom_content
    
    def test_load_last_config_missing_referenced_file(self, temp_config_dir, sample_config_content):
        """Test loading config when last config file references a missing file."""
        missing_config = temp_config_dir / "missing.json"
        default_file = temp_config_dir / "scn_data.json"
        last_config_file = temp_config_dir / ".last_config"
        
        # Create default config file
        with open(default_file, "w") as f:
            json.dump(sample_config_content, f)
        
        # Reference a missing file
        with open(last_config_file, "w") as f:
            f.write(str(missing_config.absolute()))
        
        with patch('config.DEFAULT_DATA_FILE', default_file), \
             patch('config.LAST_CONFIG_FILE', last_config_file):
            config = load_last_config()
        
        # Should fallback to default
        assert config.config_path == default_file
        assert config.contents == sample_config_content
    
    def test_load_last_config_corrupted_last_file(self, temp_config_dir, sample_config_content):
        """Test loading config when last config file is corrupted."""
        default_file = temp_config_dir / "scn_data.json"
        last_config_file = temp_config_dir / ".last_config"
        
        # Create default config file
        with open(default_file, "w") as f:
            json.dump(sample_config_content, f)
        
        # Create corrupted last config file (binary data)
        with open(last_config_file, "wb") as f:
            f.write(b'\x00\x01\x02\x03')
        
        with patch('config.DEFAULT_DATA_FILE', default_file), \
             patch('config.LAST_CONFIG_FILE', last_config_file):
            config = load_last_config()
        
        # Should fallback to default
        assert config.config_path == default_file
        assert config.contents == sample_config_content
    
    def test_load_last_config_creates_default_if_missing(self, temp_config_dir):
        """Test that load_last_config creates default config if it doesn't exist."""
        default_file = temp_config_dir / "scn_data.json"
        last_config_file = temp_config_dir / ".last_config"
        
        with patch('config.DEFAULT_DATA_FILE', default_file), \
             patch('config.LAST_CONFIG_FILE', last_config_file):
            config = load_last_config()
        
        assert config.config_path == default_file
        assert config.contents == {"tickers": []}
        assert default_file.exists()
        
        # Verify file contents
        with open(default_file, "r") as f:
            file_contents = json.load(f)
        assert file_contents == {"tickers": []}
    
    def test_load_last_config_corrupted_json(self, temp_config_dir):
        """Test loading config when referenced config has invalid JSON."""
        custom_config = temp_config_dir / "corrupted.json"
        default_file = temp_config_dir / "scn_data.json"
        last_config_file = temp_config_dir / ".last_config"
        
        # Create corrupted JSON file
        with open(custom_config, "w") as f:
            f.write("{ invalid json }")
        
        # Create default config file
        default_content = {"tickers": ["DEFAULT"]}
        with open(default_file, "w") as f:
            json.dump(default_content, f)
        
        # Reference the corrupted file
        with open(last_config_file, "w") as f:
            f.write(str(custom_config.absolute()))
        
        with patch('config.DEFAULT_DATA_FILE', default_file), \
             patch('config.LAST_CONFIG_FILE', last_config_file):
            config = load_last_config()
        
        # Should fallback to default
        assert config.config_path == default_file
        assert config.contents == default_content


class TestCreateDefaultConfig:
    """Test the create_default_config_if_not_exists function."""
    
    def test_create_default_config_new_file(self, temp_config_dir):
        """Test creating default config when file doesn't exist."""
        default_file = temp_config_dir / "scn_data.json"
        
        with patch('config.DEFAULT_DATA_FILE', default_file):
            create_default_config_if_not_exists()
        
        assert default_file.exists()
        with open(default_file, "r") as f:
            contents = json.load(f)
        assert contents == {"tickers": []}
    
    def test_create_default_config_existing_file(self, temp_config_dir):
        """Test that existing config file is not overwritten."""
        default_file = temp_config_dir / "scn_data.json"
        existing_content = {"tickers": ["EXISTING"]}
        
        # Create existing file
        with open(default_file, "w") as f:
            json.dump(existing_content, f)
        
        with patch('config.DEFAULT_DATA_FILE', default_file):
            create_default_config_if_not_exists()
        
        # Should not be overwritten
        with open(default_file, "r") as f:
            contents = json.load(f)
        assert contents == existing_content


class TestSignalHandlers:
    """Test the setup_signal_handlers function."""
    
    @patch('config.signal.signal')
    def test_setup_signal_handlers(self, mock_signal):
        """Test that signal handlers are properly registered."""
        config = Config(config_path=Path("/test/path.json"), contents={})
        
        setup_signal_handlers(config)
        
        # Verify both SIGINT and SIGTERM handlers were registered
        assert mock_signal.call_count == 2
        calls = mock_signal.call_args_list
        
        # Check that both signals were registered
        registered_signals = [call[0][0] for call in calls]
        import signal
        assert signal.SIGINT in registered_signals
        assert signal.SIGTERM in registered_signals
    
    @patch('config.sys.exit')
    @patch('config.save_last_config')
    @patch('config.signal.signal')
    def test_signal_handler_execution(self, mock_signal, mock_save, mock_exit):
        """Test that signal handler saves config and exits."""
        config = Config(config_path=Path("/test/path.json"), contents={})
        
        setup_signal_handlers(config)
        
        # Get the registered signal handler
        signal_handler = mock_signal.call_args_list[0][0][1]
        
        # Execute the signal handler
        signal_handler(None, None)
        
        # Verify config was saved and program exited
        mock_save.assert_called_once_with(config.config_path)
        mock_exit.assert_called_once_with(0)