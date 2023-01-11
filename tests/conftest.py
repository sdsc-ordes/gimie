"""Avoid _pytest.pathlib.ImportPathMismatchError for pytest"""
import os
os.environ["PY_IGNORE_IMPORTMISMATCH"] = "1"
