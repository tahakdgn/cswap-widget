#!/usr/bin/env python3
"""Desktop shortcut generator for cswap-widget."""

import os
import sys

# Ensure src/ is accessible
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "src")))

from cswap_widget.utils.shortcut import create_desktop_shortcut

if __name__ == "__main__":
    success = create_desktop_shortcut()
    if success:
        print("[OK] Masaustu kisayolu ('cswap Widget.lnk') basariyla olusturuldu!")
    else:
        print("[HATA] Kisayol olusturulurken bir hata meydana geldi.")

