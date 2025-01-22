# Contents of tests/test_json_handler.py
'''Unit tests for json_handler.py'''
import json
from unittest.mock import mock_open
from unittest.mock import patch
from unit.json_handler import load_and_sort_json


def test_load_and_sort_json_valid_data():
    """Test loading and sorting a valid JSON file."""
    mock_data = json.dumps([
        {"name": "Alice", "age": 25},
        {"name": "Bob", "age": 30},
        {"name": "Charlie", "age": 20}
    ])
    with patch("builtins.open", mock_open(read_data=mock_data)):
        result = load_and_sort_json("mock_file.json", "age")
        assert result == [
            {"name": "Charlie", "age": 20},
            {"name": "Alice", "age": 25},
            {"name": "Bob", "age": 30}
        ]


def test_load_and_sort_json_missing_file():
    """Test behavior when the JSON file is missing."""
    with patch("builtins.open", side_effect=FileNotFoundError):
        result = load_and_sort_json("non_existent.json", "age")
        assert result == []


def test_load_and_sort_json_invalid_json():
    """Test behavior when the JSON file contains invalid JSON."""
    invalid_data = "{name: 'Alice', age: 25}"
    with patch("builtins.open", mock_open(read_data=invalid_data)):
        result = load_and_sort_json("invalid.json", "age")
        assert result == []


def test_load_and_sort_json_missing_key():
    """Test behavior when the sorting key is missing in some records."""
    mock_data = json.dumps([
        {"name": "Alice", "age": 25},
        {"name": "Bob"},
        {"name": "Charlie", "age": 20}
    ])
    with patch("builtins.open", mock_open(read_data=mock_data)):
        result = load_and_sort_json("mock_file.json", "age")
        assert result == []


def test_load_and_sort_json_empty_file():
    """Test behavior when the JSON file is empty."""
    with patch("builtins.open", mock_open(read_data="")):
        result = load_and_sort_json("empty.json", "age")
        assert result == []


def test_load_and_sort_json_empty_array():
    """Test behavior when the JSON file contains an empty array."""
    mock_data = json.dumps([])
    with patch("builtins.open", mock_open(read_data=mock_data)):
        result = load_and_sort_json("empty_array.json", "age")
        assert result == []
