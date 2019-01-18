"""Base classes for pytest."""
import pytest
import rovercode.app

@pytest.fixture
def testapp():
    """Provide the rover service."""
    return rovercode.app