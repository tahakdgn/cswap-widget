"""Utility functions for cswap-widget."""

from .shortcut import create_desktop_shortcut
from .chrome import (
    find_chrome_executable,
    get_chrome_profiles,
    find_chrome_profile_for_account,
    launch_chrome_profile,
    open_claude_for_account,
)

__all__ = [
    "create_desktop_shortcut",
    "find_chrome_executable",
    "get_chrome_profiles",
    "find_chrome_profile_for_account",
    "launch_chrome_profile",
    "open_claude_for_account",
]
