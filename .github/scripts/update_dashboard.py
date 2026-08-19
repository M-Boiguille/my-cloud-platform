#!/usr/bin/env python3
"""Met à jour le dashboard statique."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from core.dashboard import update_dashboard


def main():
    path = update_dashboard()
    print(f"Dashboard mis à jour : {path}")


if __name__ == "__main__":
    main()
