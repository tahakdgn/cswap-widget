#!/usr/bin/env python3
"""Convenient root launcher for cswap-widget."""

import sys
import os

# Add src to sys.path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "src"))

from cswap_widget.main import main

if __name__ == "__main__":
    main()
