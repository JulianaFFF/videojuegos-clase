"""Motor del juego: patron Game Loop (eventos -> actualizacion -> dibujo) y gestor de escenas."""
import asyncio

import pygame

from src.engine.game_session import GameSession
from src.engine.service_locator import ServiceLocator


class GameEngine:
    def __init__(self) -> None:
        configs = ServiceLocator.configs_service
        self.window_cfg = configs.get("assets/cfg/window.json")
        pygame.mixer.pre_init(22050, -16, 2, 512)
        pygame.init()
        pygame.display.set_caption(self.window_cfg["title"])
        self.screen = pygame.display.set_mode(
            (self.window_cfg["size"]["w"], self.window_cfg["size"]["h"]), pygame.SCALED)
        try:
            pygame.mixer.init()
        except pygame.error:
            ServiceLocator.sounds_service.enabled = False
        ServiceLocator.images_service.set_sprites_config(configs.get("assets/cfg/sprites.json"))
        self.clock = pygame.time.Clock()
        self.framerate = self.window_cfg["framerate"]
        self.bg_color = pygame.Color(self.window_cfg["bg_color"]["r"], self.window_cfg["bg_color"]["g"],
                                     self.window_cfg["bg_color"]["b"])
        self.is_running = False
        self.delta_time = 0.0
        self.session = GameSession()
        self.joysticks = []

        # Import tardio para evitar dependencias circulares
        from src.scenes.scenes import SCENES  # pylint: disable=import-outside-toplevel
        self._scenes = SCENES
        self._current_scene = None
        self._next_scene = "intro"

    def switch_scene(self, name: str) -> None:
        self._next_scene = name

    async def run(self) -> None:
        self.is_running = True
        while self.is_running:
            self._apply_scene_change()
            self._calculate_time()
            self._process_events()
            self._update()
            self._draw()
            await asyncio.sleep(0)  # necesario para pygbag (web)
        self._do_clean()

    def _apply_scene_change(self) -> None:
        if self._next_scene is None:
            return
        if self._current_scene is not None:
            self._current_scene.clean()
        self._current_scene = self._scenes[self._next_scene](self)
        self._next_scene = None
        self._current_scene.do_create()

    def _calculate_time(self) -> None:
        self.clock.tick(self.framerate)
        # Se limita el delta para evitar saltos grandes (p. ej. al cambiar de pestana en web)
        self.delta_time = min(self.clock.get_time() / 1000.0, 1 / 20)

    def _process_events(self) -> None:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.is_running = False
            elif event.type == pygame.JOYDEVICEADDED:
                self.joysticks.append(pygame.joystick.Joystick(event.device_index))
            self._current_scene.process_event(event)

    def _update(self) -> None:
        self._current_scene.simulate(self.delta_time)

    def _draw(self) -> None:
        self.screen.fill(self.bg_color)
        self._current_scene.do_draw(self.screen)
        pygame.display.flip()

    def _do_clean(self) -> None:
        if self._current_scene is not None:
            self._current_scene.clean()
        self.session.save_hiscore()
        pygame.quit()
