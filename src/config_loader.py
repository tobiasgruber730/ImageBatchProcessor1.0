import json
import os
from typing import Dict, Any

class ConfigLoader:
    """
    Responsible for loading and validating configuration from a JSON file.
    """

    def __init__(self, config_path: str):
        self.config_path = config_path

    def load_config(self) -> Dict[str, Any]:
        """
        Loads the JSON configuration file.

        Returns:
            Dict[str, Any]: A dictionary containing configuration parameters.
        Raises:
            FileNotFoundError: If the file does not exist.
            ValueError: If the JSON is invalid.
        """
        if not os.path.exists(self.config_path):
            raise FileNotFoundError(f"Configuration file not found at: {self.config_path}")

        try:
            with open(self.config_path, 'r') as f:
                return json.load(f)
        except json.JSONDecodeError as e:
            raise ValueError(f"Failed to parse JSON config: {e}")