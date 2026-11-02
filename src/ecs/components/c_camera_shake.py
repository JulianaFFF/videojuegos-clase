import pygame


class CCameraShake:

    def __init__(self) -> None:
        self.intensity = 0.0
        self.duration = 0.0
        self.time_left = 0.0
        self.offset = pygame.Vector2(0, 0)

    def start(self, shake_info: dict) -> None:
        # A weaker shake never interrupts a stronger one that is still running
        current = self.intensity * self.time_left / self.duration if self.duration > 0 else 0
        if shake_info["intensity"] >= current:
            self.intensity = shake_info["intensity"]
            self.duration = shake_info["duration"]
            self.time_left = shake_info["duration"]
