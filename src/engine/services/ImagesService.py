import pygame


class ImagesService:

    def __init__(self) -> None:
        self._images: dict[tuple[str, float], pygame.Surface] = {}

    def get(self, path: str, scale: float = 1) -> pygame.Surface:
        """Loads an image only once and reuses it for every entity that needs it."""
        key = (path, scale)
        if key not in self._images:
            surface = pygame.image.load(path).convert_alpha()
            if scale != 1:
                surface = pygame.transform.scale_by(surface, scale)
            self._images[key] = surface
        return self._images[key]
