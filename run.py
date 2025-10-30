#!/usr/bin/env python3
"""
Runner script for MTG Commander AI.
This script sets up the Python path correctly and runs the game.
"""
import sys
import os

# Add src directory to Python path
src_path = os.path.join(os.path.dirname(__file__), 'src')
sys.path.insert(0, src_path)

# Now import and run main
from main import main

if __name__ == "__main__":
    main()
