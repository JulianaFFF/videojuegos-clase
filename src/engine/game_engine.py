import asyncio
import platform
import sys
import time
import pygame
import esper

from src.create.prefab_creator import (
    create_camera,
    create_enemy_spawner,
    create_input_player,
    create_player_square,
    create_bullet,
    create_shield,
    create_shield_hud,
    create_text,
)
from src.ecs.components.c_input_command import CInputCommand, CommandPhase
from src.ecs.components.c_shield import CShield, ShieldState
from src.ecs.components.c_surface import CSurface
from src.ecs.components.c_transform import CTransform
from src.ecs.components.c_velocity import CVelocity
from src.ecs.components.tags.c_tag_bullet import CTagBullet
from src.ecs.systems.s_enemy_spawner import system_enemy_spawner
from src.ecs.systems.s_input_player import system_input_player
from src.ecs.systems.s_movement import system_movement
from src.ecs.systems.s_screen_bounce import system_screen_bounce
from src.ecs.systems.s_player_limits import system_player_limits
from src.ecs.systems.s_bullet_limits import system_bullet_limits
from src.ecs.systems.s_collision_player_enemy import system_collision_player_enemy
from src.ecs.systems.s_collision_enemy_bullet import system_collision_enemy_bullet
from src.ecs.systems.s_rendering import system_rendering
from src.ecs.systems.s_animation import system_animation
from src.ecs.systems.s_player_state import system_player_state
from src.ecs.systems.s_enemy_hunter_state import system_enemy_hunter_state
from src.ecs.systems.s_explosion_kill import system_explosion_kill
from src.ecs.systems.s_shield import system_shield
from src.ecs.systems.s_shield_ring import system_shield_ring
from src.ecs.systems.s_shield_hud import system_shield_hud
from src.ecs.systems.s_collision_shield_enemy import system_collision_shield_enemy
from src.ecs.systems.s_camera_shake import system_camera_shake
from src.engine.service_locator import ServiceLocator


class GameEngine:
    def __init__(self) -> None:
        self._load_config_files()

        pygame.init()
        pygame.display.set_caption(self.window_cfg["title"])
        # In the browser the page already scales the canvas: SCALED on top of it breaks the mouse position
        flags = 0 if sys.platform == "emscripten" else pygame.SCALED
        self.screen = pygame.display.set_mode((self.window_cfg["size"]["w"], self.window_cfg["size"]["h"]), flags)
        if sys.platform == "emscripten":
            platform.window.window_resize()  # The page has to adopt the aspect ratio of the game
        self.clock = pygame.time.Clock()
        self.is_running = False
        self.is_paused = False
        self.frame_rate = self.window_cfg["framerate"]
        self.delta_time = 0
        self.last_time = time.perf_counter()
        self.bg_color = pygame.Color(
            self.window_cfg["bg_color"]["r"], self.window_cfg["bg_color"]["g"], self.window_cfg["bg_color"]["b"]
        )
        self.ecs_world = esper.World()  # Initialize the ECS world

    def _load_config_files(self):
        configs = ServiceLocator.configs_service
        self.window_cfg = configs.get("assets/cfg/window.json")
        self.enemies_cfg = configs.get("assets/cfg/enemies.json")
        self.level_01_cfg = configs.get("assets/cfg/level_01.json")
        self.player_cfg = configs.get("assets/cfg/player.json")
        self.bullet_cfg = configs.get("assets/cfg/bullet.json")
        self.explosion_cfg = configs.get("assets/cfg/explosion.json")
        self.shield_cfg = configs.get("assets/cfg/shield.json")
        self.interface_cfg = configs.get("assets/cfg/interface.json")

    async def run(self) -> None:
        self._create()
        self.is_running = True
        while self.is_running:
            self._calculate_time()
            self._process_events()
            self._update()
            self._draw()
            await asyncio.sleep(0)  # Yields to the browser in the web build
        self._clean()

    def _create(self):
        self._player_entity = create_player_square(
            self.ecs_world, self.player_cfg, self.level_01_cfg["player_spawn"], self.shield_cfg
        )
        self._player_c_v = self.ecs_world.component_for_entity(self._player_entity, CVelocity)
        self._player_c_t = self.ecs_world.component_for_entity(self._player_entity, CTransform)
        self._player_c_s = self.ecs_world.component_for_entity(self._player_entity, CSurface)
        create_enemy_spawner(self.ecs_world, self.level_01_cfg)
        create_input_player(self.ecs_world)
        self._player_c_sh = self.ecs_world.component_for_entity(self._player_entity, CShield)
        self._camera = create_camera(self.ecs_world)
        create_text(self.ecs_world, self.interface_cfg["title"])
        create_text(self.ecs_world, self.interface_cfg["instructions"])
        create_shield_hud(self.ecs_world, self.interface_cfg)
        self._pause_entities: list[int] = []

    def _calculate_time(self):
        self.clock.tick(self.frame_rate)
        current_time = time.perf_counter()  # Sub-millisecond precision, needed when framerate is 0 (uncapped)
        self.delta_time = current_time - self.last_time
        self.last_time = current_time

    def _process_events(self):
        for event in pygame.event.get():
            system_input_player(self.ecs_world, event, self._do_action)
            if event.type == pygame.QUIT:
                self.is_running = False

    def _update(self):
        if self.is_paused:
            return
        system_enemy_spawner(self.ecs_world, self.delta_time, self.enemies_cfg)
        system_enemy_hunter_state(self.ecs_world, self._player_entity, self.delta_time)
        system_movement(self.ecs_world, self.delta_time)
        system_screen_bounce(self.ecs_world, self.screen)
        system_player_limits(self.ecs_world, self.screen)
        system_bullet_limits(self.ecs_world, self.screen)
        system_shield(self.ecs_world, self._player_entity, self.delta_time)
        system_collision_shield_enemy(self.ecs_world, self._player_entity, self.explosion_cfg)
        system_collision_player_enemy(self.ecs_world, self._player_entity, self.level_01_cfg, self.explosion_cfg)
        system_collision_enemy_bullet(self.ecs_world, self.explosion_cfg)
        system_player_state(self.ecs_world)
        system_animation(self.ecs_world, self.delta_time)
        system_explosion_kill(self.ecs_world)
        system_shield_ring(self.ecs_world, self.delta_time)
        system_shield_hud(self.ecs_world, self._player_entity)
        system_camera_shake(self.ecs_world, self.delta_time)
        self.ecs_world._clear_dead_entities()  # pylint: disable=protected-access

    def _draw(self):
        self.screen.fill(self.bg_color)
        system_rendering(self.ecs_world, self.screen, self._camera.offset)
        pygame.display.flip()

    def _clean(self):
        pygame.quit()

    def _toggle_pause(self):
        self.is_paused = not self.is_paused
        if self.is_paused:
            ServiceLocator.sounds_service.pause_all()
            self._pause_entities = [
                create_text(self.ecs_world, self.interface_cfg["pause_title"]),
                create_text(self.ecs_world, self.interface_cfg["pause_hint"]),
            ]
        else:
            ServiceLocator.sounds_service.resume_all()
            for entity in self._pause_entities:
                # Immediate: _update, which clears dead entities, does not run while paused
                self.ecs_world.delete_entity(entity, immediate=True)

    def _do_action(self, c_input: CInputCommand):
        """Command pattern: executes the action associated with each input command."""
        input_velocity = self.player_cfg["input_velocity"]
        if c_input.name == "PLAYER_LEFT":
            if c_input.phase == CommandPhase.START:
                self._player_c_v.vel.x -= input_velocity
            elif c_input.phase == CommandPhase.END:
                self._player_c_v.vel.x += input_velocity
        elif c_input.name == "PLAYER_RIGHT":
            if c_input.phase == CommandPhase.START:
                self._player_c_v.vel.x += input_velocity
            elif c_input.phase == CommandPhase.END:
                self._player_c_v.vel.x -= input_velocity
        elif c_input.name == "PLAYER_UP":
            if c_input.phase == CommandPhase.START:
                self._player_c_v.vel.y -= input_velocity
            elif c_input.phase == CommandPhase.END:
                self._player_c_v.vel.y += input_velocity
        elif c_input.name == "PLAYER_DOWN":
            if c_input.phase == CommandPhase.START:
                self._player_c_v.vel.y += input_velocity
            elif c_input.phase == CommandPhase.END:
                self._player_c_v.vel.y -= input_velocity
        elif c_input.name == "PAUSE":
            if c_input.phase == CommandPhase.START:
                self._toggle_pause()
        elif c_input.name == "PLAYER_SHIELD":
            if c_input.phase == CommandPhase.START and not self.is_paused and self._player_c_sh.state == ShieldState.READY:
                create_shield(self.ecs_world, self._player_entity, self.shield_cfg)
        elif c_input.name == "PLAYER_FIRE":
            if c_input.phase == CommandPhase.START and not self.is_paused:
                max_bullets = self.level_01_cfg["player_spawn"]["max_bullets"]
                if len(self.ecs_world.get_component(CTagBullet)) < max_bullets:
                    create_bullet(
                        self.ecs_world,
                        self._player_c_t.pos,
                        pygame.Vector2(self._player_c_s.area.size),
                        pygame.Vector2(pygame.mouse.get_pos()),
                        self.bullet_cfg,
                    )
