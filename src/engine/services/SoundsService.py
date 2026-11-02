import pygame


class SoundsService:

    def __init__(self) -> None:
        self._sounds: dict[str, pygame.mixer.Sound] = {}

    def get(self, path: str) -> pygame.mixer.Sound:
        if path not in self._sounds:
            self._sounds[path] = pygame.mixer.Sound(path)
        return self._sounds[path]

    def play(self, path: str) -> None:
        self.get(path).play()

    def pause_all(self) -> None:
        pygame.mixer.pause()

    def resume_all(self) -> None:
        pygame.mixer.unpause()
