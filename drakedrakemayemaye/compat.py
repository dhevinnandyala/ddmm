"""Python version detection helpers for drakedrakemayemaye."""

import sys

PYTHON_VERSION = sys.version_info

# Minimum supported version
MIN_VERSION = (3, 10)

# Feature flags
HAS_MATCH_CASE = PYTHON_VERSION >= (3, 10)
HAS_EXCEPTION_GROUPS = PYTHON_VERSION >= (3, 11)
HAS_NESTED_FSTRINGS = PYTHON_VERSION >= (3, 12)


def check_python_version() -> None:
    """Raise an error if the Python version is too old."""
    if PYTHON_VERSION < MIN_VERSION:
        sys.exit(
            f"drakedrakemayemaye requires Python {MIN_VERSION[0]}.{MIN_VERSION[1]}+, "
            f"but you are running Python {PYTHON_VERSION[0]}.{PYTHON_VERSION[1]}"
        )
