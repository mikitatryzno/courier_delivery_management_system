"""Project-level pytest fixtures bridge.

Re-export fixtures defined under `src/tests/conftest.py`
so pytest discovers them for all test locations.
"""
from src.tests.conftest import *  # noqa: F401,F403
