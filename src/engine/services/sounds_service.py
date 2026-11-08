import pygame


class SoundsService:
    """Efectos de sonido y musica. Si el audio no esta disponible el juego sigue funcionando."""

    def __init__(self) -> None:
        self._sounds = {}
        self._current_music = None
        self.enabled = True

    def get(self, path: str):
        if path not in self._sounds:
            try:
                self._sounds[path] = pygame.mixer.Sound(path)
            except Exception:  # pylint: disable=broad-except
                self._sounds[path] = None
        return self._sounds[path]

    def play(self, path: str, volume: float = 0.6) -> None:
        if not self.enabled:
            return
        snd = self.get(path)
        if snd is not None:
            snd.set_volume(volume)
            snd.play()

    def play_music(self, path: str, volume: float = 0.5, loops: int = -1) -> None:
        if not self.enabled or path == self._current_music:
            return
        try:
            pygame.mixer.music.load(path)
            pygame.mixer.music.set_volume(volume)
            pygame.mixer.music.play(loops)
            self._current_music = path
        except Exception:  # pylint: disable=broad-except
            self._current_music = None

    def stop_music(self) -> None:
        try:
            pygame.mixer.music.stop()
        except Exception:  # pylint: disable=broad-except
            pass
        self._current_music = None
