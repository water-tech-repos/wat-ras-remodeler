"""Utility method for tests"""
import os
from typing import Union


def delete_if_exists(filepath: Union[str, None]):
    """Check if a file exists and delete if it does (local filesystem only)."""
    if filepath is not None and os.path.exists(filepath):
        os.remove(filepath)
