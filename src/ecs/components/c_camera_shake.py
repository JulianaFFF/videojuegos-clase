import pygame

class CCameraShake:
    def __init__(self) -> None:
        self.intensity = 0.0
        self.duration = 0.0
        self.time_left = 0.0
        self.offset = pygame.Vector2(0, 0)

    def shake(self, intensity:float, duration:float) -> None:
        self.intensity = intensity
        self.duration = duration
        self.time_left = duration
