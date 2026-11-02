#!/usr/bin/env python3
"""Función Main"""

import asyncio
import os
import sys
import pygame  # pylint: disable=unused-import  # pygbag only detects packages imported here
from src.engine.game_engine import GameEngine


async def main():
    await GameEngine().run()


if __name__ == "__main__":
    # Config and image paths are relative to main.py (pygbag already starts there)
    if sys.platform != "emscripten":
        os.chdir(os.path.dirname(os.path.abspath(__file__)))
    asyncio.run(main())
