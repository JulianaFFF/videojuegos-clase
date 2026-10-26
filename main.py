#!/usr/bin/env python3
"""Función Main"""

import os
from src.engine.game_engine import GameEngine

if __name__ == "__main__":
    # Config and image paths are relative to main.py
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    engine = GameEngine()
    engine.run()
