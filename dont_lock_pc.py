"""Backward-compatible launcher.

The application now lives in the ``dontlockpc`` package under ``src/``. This
thin shim keeps the old ``python dont_lock_pc.py`` command working.
"""

from __future__ import annotations

import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "src"))

from dontlockpc.app import main  # noqa: E402

if __name__ == "__main__":
    main()
