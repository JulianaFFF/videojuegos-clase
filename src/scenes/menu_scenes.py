"""Escenas de interfaz: intro, menu, instrucciones, creditos, victoria y game over."""
import pygame

from src.create.prefab_creator import cfg, create_image_ui, create_starfield, create_text
from src.ecs.components.c_input_command import CInputCommand, CommandPhase
from src.ecs.components.c_surface import CSurface
from src.ecs.components.c_tags import CTagIntroSlide, CTagUI
from src.ecs.components.c_transform import CTransform
from src.ecs.systems.s_blink import system_blink
from src.ecs.systems.s_intro_slide import system_intro_slide
from src.ecs.systems.s_rendering import system_rendering
from src.ecs.systems.s_starfield import system_draw_starfield, system_starfield
from src.engine.scenes_base import Scene
from src.engine.service_locator import ServiceLocator


class StarsScene(Scene):
    """Escena con fondo de estrellas desplazandose (modo menu)."""
    music_key = "menu"

    def do_create(self) -> None:
        super().do_create()
        create_starfield(self.ecs_world, self.screen_rect.w, self.screen_rect.h)
        m_cfg = cfg("music")
        ServiceLocator.sounds_service.play_music(m_cfg[self.music_key], m_cfg["volume"])
        mv = cfg("world")["stars"]["menu_velocity"]
        self.star_scroll = pygame.Vector2(-mv["x"], -mv["y"])

    def do_update(self, delta_time: float) -> None:
        system_starfield(self.ecs_world, delta_time, self.star_scroll * delta_time,
                         self.screen_rect.w, self.screen_rect.h, self.time)
        system_blink(self.ecs_world, delta_time)

    def do_draw(self, screen: pygame.Surface) -> None:
        system_draw_starfield(self.ecs_world, screen)
        system_rendering(self.ecs_world, screen, 1, 1, self.screen_rect, self.time)

    def _pressed(self, action: CInputCommand, *names) -> bool:
        return action.phase == CommandPhase.START and action.name in names


class IntroScene(StarsScene):
    """Intro animada: texto de presentacion y logo que cae desde arriba."""
    music_key = "intro"

    def do_create(self) -> None:
        super().do_create()
        cx = self.screen_rect.centerx
        self.presents = [create_text(self.ecs_world, "UN PROYECTO DEL EQUIPO UWU", (cx, 90), "gray"),
                         create_text(self.ecs_world, "PRESENTA", (cx, 104), "gray")]
        logo = ServiceLocator.images_service.get_clean(cfg("sprites")["title"])
        self.logo = create_image_ui(self.ecs_world, logo, (cx, -60))
        ship = create_image_ui(self.ecs_world, ServiceLocator.images_service.get_rotated("player", 90),
                               (-20, 190))
        self.ecs_world.add_component(ship, CTagIntroSlide(pygame.Vector2(280, 190), 70))

    def do_update(self, delta_time: float) -> None:
        super().do_update(delta_time)
        self.star_scroll.update(-30 - self.time * 20, 0)
        if self.presents and self.time > 2.2:
            for ent in self.presents:
                self.ecs_world.delete_entity(ent)
            self.presents = []
            self.ecs_world.add_component(self.logo, CTagIntroSlide(pygame.Vector2(self.screen_rect.centerx, 90), 80))
        system_intro_slide(self.ecs_world, delta_time)
        if self.time > 6.5:
            self.switch_scene("menu")

    def do_action(self, action) -> None:
        if self._pressed(action, "START", "FIRE"):
            self.switch_scene("menu")


class MenuScene(StarsScene):
    OPTIONS = [("JUGAR", "play_new"), ("INSTRUCCIONES", "instructions"), ("CREDITOS", "credits")]

    def do_create(self) -> None:
        super().do_create()
        cx = self.screen_rect.centerx
        session = self.game_engine.session
        create_text(self.ecs_world, "1UP", (40, 8), "cyan")
        create_text(self.ecs_world, str(session.score), (40, 18), "white")
        create_text(self.ecs_world, "HI-SCORE", (180, 8), "red")
        create_text(self.ecs_world, str(session.hiscore), (180, 18), "white")
        logo = ServiceLocator.images_service.get_clean(cfg("sprites")["title"])
        create_image_ui(self.ecs_world, logo, (cx, 70))
        self.option_ents = []
        for i, (text, _) in enumerate(self.OPTIONS):
            self.option_ents.append(create_text(self.ecs_world, text, (cx, 124 + i * 14), "white"))
        self.cursor = create_text(self.ecs_world, ">", (0, 0), "yellow")
        self.selected = 0
        create_text(self.ecs_world, "PRESIONA ENTER", (cx, 178), "yellow", blink=0.5)
        create_text(self.ecs_world, "(C) 2026 COSMONIAN Equipo UwU", (cx, 196), "gray")
        self._move_cursor()
        self.idle = 0.0

    def _move_cursor(self) -> None:
        opt = self.ecs_world.component_for_entity(self.option_ents[self.selected], CTransform)
        surf = self.ecs_world.component_for_entity(self.option_ents[self.selected], CSurface).surf
        self.ecs_world.component_for_entity(self.cursor, CTransform).pos.update(
            opt.pos.x - surf.get_width() / 2 - 10, opt.pos.y)

    def do_update(self, delta_time: float) -> None:
        super().do_update(delta_time)
        self.idle += delta_time
        if self.idle > 25:
            self.switch_scene("intro")

    def do_action(self, action) -> None:
        self.idle = 0.0
        if self._pressed(action, "UP", "DOWN"):
            self.selected = (self.selected + (1 if action.name == "DOWN" else -1)) % len(self.OPTIONS)
            ServiceLocator.sounds_service.play(cfg("sounds")["select"], 0.4)
            self._move_cursor()
        elif self._pressed(action, "START", "FIRE"):
            ServiceLocator.sounds_service.play(cfg("sounds")["select"], 0.4)
            target = self.OPTIONS[self.selected][1]
            if target == "play_new":
                self.game_engine.session.reset()
                self.switch_scene("play")
            else:
                self.switch_scene(target)


class InstructionsScene(StarsScene):
    music_key = "instructions"

    def do_create(self) -> None:
        super().do_create()
        cx = self.screen_rect.centerx
        lines = cfg("interface")["instructions"]
        for i, line in enumerate(lines):
            create_text(self.ecs_world, line, (cx, 8 + i * 9), "yellow" if i == 0 else "white")
        images = ServiceLocator.images_service
        legend = [("enemy_i", "I"), ("enemy_p", "P"), ("enemy_e", "E"), ("enemy_spy", "SPY"),
                  ("rock", "ROCA"), ("hard_rock", "DURA"), ("mine", "MINA")]
        for i, (spr, name) in enumerate(legend):
            x = 18 + i * 37
            create_image_ui(self.ecs_world, images.get_frame(spr), (x, 178))
            create_text(self.ecs_world, name, (x, 192), "cyan")
        create_text(self.ecs_world, "ENTER: VOLVER", (cx, 202), "gray", blink=0.6)

    def do_action(self, action) -> None:
        if self._pressed(action, "START", "FIRE", "PAUSE"):
            self.switch_scene("menu")


class CreditsScene(StarsScene):
    music_key = "credits"

    def do_create(self) -> None:
        super().do_create()
        cx = self.screen_rect.centerx
        self.lines = []
        for i, item in enumerate(cfg("interface")["credits"]):
            line, color = (item, "white") if isinstance(item, str) else item
            ent = create_text(self.ecs_world, line, (cx, self.screen_rect.h + 10 + i * 12), color)
            self.lines.append(ent)

    def do_update(self, delta_time: float) -> None:
        super().do_update(delta_time)
        last = None
        for ent in self.lines:
            c_t = self.ecs_world.component_for_entity(ent, CTransform)
            c_t.pos.y -= 18 * delta_time
            last = c_t
        if last is not None and last.pos.y < -10:
            self.switch_scene("menu")

    def do_action(self, action) -> None:
        if self._pressed(action, "START", "FIRE", "PAUSE"):
            self.switch_scene("menu")


class _EndScene(StarsScene):
    title = ""
    title_color = "white"
    subtitle = ""

    def do_create(self) -> None:
        super().do_create()
        session = self.game_engine.session
        session.save_hiscore()
        cx = self.screen_rect.centerx
        create_text(self.ecs_world, self.title, (cx, 50), self.title_color, size=16)
        create_text(self.ecs_world, self.subtitle, (cx, 76), "white")
        create_text(self.ecs_world, "PUNTAJE", (cx, 100), "cyan")
        create_text(self.ecs_world, str(session.score), (cx, 112), "white")
        create_text(self.ecs_world, "RONDA " + str(session.round), (cx, 128), "yellow")
        if session.new_hiscore:
            # Escena de felicitacion de puntaje maximo (bono)
            create_text(self.ecs_world, "FELICIDADES!", (cx, 150), "yellow", blink=0.25)
            create_text(self.ecs_world, "NUEVO RECORD", (cx, 162), "red", blink=0.25)
        create_text(self.ecs_world, "ENTER: MENU", (cx, 192), "gray", blink=0.6)

    def do_update(self, delta_time: float) -> None:
        super().do_update(delta_time)
        if self.time > 15:
            self.switch_scene("menu")

    def do_action(self, action) -> None:
        if self.time > 1.0 and self._pressed(action, "START", "FIRE"):
            self.switch_scene("menu")


class GameOverScene(_EndScene):
    music_key = "game_over"
    title = "GAME OVER"
    title_color = "red"
    subtitle = "TU FLOTA FUE DESTRUIDA"


class VictoryScene(_EndScene):
    music_key = "victory"
    title = "VICTORIA"
    title_color = "green"
    subtitle = "10 RONDAS COMPLETADAS"


__all__ = ["IntroScene", "MenuScene", "InstructionsScene", "CreditsScene", "GameOverScene",
           "VictoryScene", "CTagUI"]
