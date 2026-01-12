"""Top-level pytest fixtures bridge.

This imports fixtures defined under `src/tests/conftest.py`
so they are available to tests located in other subpackages
like `src/api/schemas`.
"""
from src.tests.conftest import *  # noqa: F401,F403
