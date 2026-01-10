#!/usr/bin/env python3
"""
Yamete - Manga/Hentai Downloader (Python CLI)
Standalone script version

Usage: python3 yamete.py [options]
"""

import sys
import os

# Add the python directory to path so imports work
script_dir = os.path.dirname(os.path.abspath(__file__))
python_dir = os.path.join(script_dir, 'python')
if os.path.exists(python_dir):
    sys.path.insert(0, python_dir)

from yamete.cli import main

if __name__ == '__main__':
    sys.exit(main())
