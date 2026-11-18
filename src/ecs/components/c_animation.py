from typing import List

import pygame


class CAnimation:
    """Animacion cuadro a cuadro: lista de superficies + velocidad (fps)."""
    def __init__(self, frames: List[pygame.Surface], fps: float, loop: bool = True) -> None:
        self.frames = frames
        self.frame_time = 1.0 / fps
        self.loop = loop
        self.curr_frame = 0
        self.time = 0.0
        self.finished = False
        self.paused = False
