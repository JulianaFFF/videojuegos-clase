"""Patron Escena: cada pantalla del juego es una escena con su propio mundo ECS."""
import esper
import pygame

from src.create.prefab_creator import create_input_commands
from src.ecs.components.c_input_command import CInputCommand
from src.ecs.systems.s_input import system_input


class Scene:
    def __init__(self, game_engine) -> None:
        self.game_engine = game_engine
        self.ecs_world = esper.World()
        self.screen_rect = game_engine.screen.get_rect()
        self.time = 0.0

    # --- ciclo de vida ---
    def do_create(self) -> None:
        create_input_commands(self.ecs_world)

    def do_update(self, delta_time: float) -> None:
        pass

    def do_draw(self, screen: pygame.Surface) -> None:
        pass

    def do_action(self, action: CInputCommand) -> None:
        pass

    def do_clean(self) -> None:
        pass

    # --- llamadas del motor ---
    def simulate(self, delta_time: float) -> None:
        self.time += delta_time
        self.do_update(delta_time)
        self.ecs_world._clear_dead_entities()  # pylint: disable=protected-access

    def process_event(self, event: pygame.event.Event) -> None:
        system_input(self.ecs_world, event, self.do_action)

    def clean(self) -> None:
        self.do_clean()
        self.ecs_world.clear_database()

    def switch_scene(self, name: str) -> None:
        self.game_engine.switch_scene(name)
