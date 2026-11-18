import pygame


class CCamera:
    """Camara que sigue al jugador. 'pos' es el centro de la vista en coordenadas de mundo."""
    def __init__(self, pos, view_w: int, view_h: int) -> None:
        self.pos = pygame.Vector2(pos)
        self.prev_pos = pygame.Vector2(pos)
        self.view_w = view_w
        self.view_h = view_h
        self.shake_time = 0.0
        self.shake_mag = 0.0
        self.offset = pygame.Vector2(0, 0)
