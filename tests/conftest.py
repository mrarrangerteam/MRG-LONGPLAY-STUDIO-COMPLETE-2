"""Shared test fixtures."""

import pytest
import sys


@pytest.fixture(scope="session", autouse=True)
def qapp():
    """Create a QApplication instance for all tests that need Qt widgets."""
    from PyQt6.QtWidgets import QApplication
    app = QApplication.instance()
    if app is None:
        app = QApplication(sys.argv)
    yield app
