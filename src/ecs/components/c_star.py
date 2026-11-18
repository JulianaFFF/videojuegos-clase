import pygame


class CStar:
    """Estrella del fondo: color, capa de profundidad (parallax) y parpadeo."""
    def __init__(self, pos, color, depth: float, blink_speed: float, phase: float) -> None:
        self.pos = pygame.Vector2(pos)
        self.color = pygame.Color(*color)
        self.depth = depth
        self.blink_speed = blink_speed
        self.phase = phase
        self.visible = True
