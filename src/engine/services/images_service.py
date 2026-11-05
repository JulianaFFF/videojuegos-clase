import pygame

class ImagesService:
    def __init__(self) -> None:
        self._images = {}

    def get(self, path: str) -> pygame.Surface:
        if path not in self._images:
            self._images[path] = pygame.image.load(path).convert_alpha()
        return self._images[path]

    def get_scaled(self, path: str, size: tuple) -> pygame.Surface:
        key = (path, int(size[0]), int(size[1]))
        if key not in self._images:
            self._images[key] = pygame.transform.scale(self.get(path), key[1:])
        return self._images[key]
