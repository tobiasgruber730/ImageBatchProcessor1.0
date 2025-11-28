import unittest
import json
import os
import sys
from unittest.mock import patch, mock_open



from src.config_loader import ConfigLoader


class TestConfigLoader(unittest.TestCase):
    """
    Unit tests for the ConfigLoader class.
    """

    def test_load_valid_config(self):
        """Test if valid JSON is loaded correctly."""
        mock_data = json.dumps({
            "source_folder": "data/input",
            "number_of_threads": 4
        })


        with patch("os.path.exists", return_value=True):
            with patch("builtins.open", mock_open(read_data=mock_data)):
                loader = ConfigLoader("fake_path.json")
                config = loader.load_config()

                self.assertEqual(config["number_of_threads"], 4)
                self.assertEqual(config["source_folder"], "data/input")

    def test_file_not_found(self):
        """Test if FileNotFoundError is raised when file is missing."""
        with patch("os.path.exists", return_value=False):
            loader = ConfigLoader("non_existent.json")
            with self.assertRaises(FileNotFoundError):
                loader.load_config()


if __name__ == '__main__':
    unittest.main()