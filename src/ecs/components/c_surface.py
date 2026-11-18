import pygame


class CSurface:
    """Imagen a dibujar centrada en CTransform.pos."""
    def __init__(self, surf: pygame.Surface, visible: bool = True, layer: int = 0) -> None:
        self.surf = surf
        self.visible = visible
        self.layer = layer
        self.flash = 0.0  # segundos de parpadeo (game feel al recibir impacto / invulnerable)

    @classmethod
    def from_text(cls, text: str, font: pygame.font.Font, color, layer: int = 10):
        return cls(font.render(text, False, color), layer=layer)
