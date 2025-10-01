#!/usr/bin/env python3
"""
HingeAutoBot - Quick Start Script
"""

import sys
import os
from pathlib import Path

# Add the app directory to Python path
sys.path.insert(0, str(Path(__file__).parent / "app"))

from main import main

if __name__ == "__main__":
    main()
