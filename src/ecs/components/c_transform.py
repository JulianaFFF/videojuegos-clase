import pygame


class CTransform:
    """Posicion del CENTRO de la entidad en coordenadas de mundo (o de pantalla si es UI)."""
    def __init__(self, pos: pygame.Vector2) -> None:
        self.pos = pygame.Vector2(pos)
