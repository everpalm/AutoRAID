# Contents of tests/test_amd64/test_rog_x570.py
'''Copyright (c) 2024 Jaron Cheng'''
import json
import logging
import pytest
from tests.test_amd64.test_amd64_system import TestAMD64System

# Set up logger
logger = logging.getLogger(__name__)


@pytest.fixture(scope="module")
def amd64_settings():
    """Fixture to load AMD64 settings from a JSON file."""
    with open('config/rog_x570.json', 'r', encoding='utf-8') as f:
        return json.load(f)


class TestRogX570(TestAMD64System):
    '''Duplicate of TestAMD64NVMe to simulate a new test system'''
