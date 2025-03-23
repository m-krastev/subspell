import os
import json
from pathlib import Path
from typing import Optional, Dict, Any
from .language_rules import BG_SYSTEM_INSTRUCTION

class ConfigManager:
    """Manages application configuration and preferences."""
    
    def __init__(self, config_dir: Optional[str] = None):
        """
        Initialize the configuration manager.
        
        Args:
            config_dir: Directory to store config files (defaults to user's home directory)
        """
        if config_dir is None:
            config_dir = os.path.expanduser("~")
        
        self.config_dir = Path(config_dir) / ".subspell"
        self.config_file = self.config_dir / "config.json"
        self.config: Dict[str, Any] = {}
        
        # Create config directory if it doesn't exist
        self.config_dir.mkdir(parents=True, exist_ok=True)
        
        # Load existing config or create default
        self.load_config()
    
    def load_config(self):
        """Load configuration from file or create default."""
        if self.config_file.exists():
            try:
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    self.config = json.load(f)
            except Exception as e:
                print(f"Error loading config: {e}")
                self.config = self.get_default_config()
        else:
            self.config = self.get_default_config()
            self.save_config()
    
    def save_config(self):
        """Save current configuration to file."""
        try:
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(self.config, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"Error saving config: {e}")
    
    def get_default_config(self) -> Dict[str, Any]:
        """Get default configuration values."""
        return {
            "theme": "system",
            "llm_prompt": BG_SYSTEM_INSTRUCTION,
            "window_size": "1200x800",
            "window_position": None,
            "temperature": 0.2,
            "top_k": 40,
            "top_p": 0.95,
            "model": "gemini-2.0-flash",
        }
    
    def get(self, key: str, default: Any = None) -> Any:
        """Get a configuration value."""
        return self.config.get(key, default)
    
    def set(self, key: str, value: Any):
        """Set a configuration value and save to file."""
        self.config[key] = value
        self.save_config()
    
    def update(self, updates: Dict[str, Any]):
        """Update multiple configuration values at once."""
        self.config.update(updates)
        self.save_config() 