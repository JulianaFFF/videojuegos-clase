import pygame


class CShieldRing:

    def __init__(self, radius: float, grow_time: float, color: pygame.Color) -> None:
        self.radius = radius
        self.grow_time = grow_time
        self.color = color
        self.elapsed = 0.0
