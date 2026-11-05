import asyncio

import pygame
import esper

from src.create.prefab_creator import (create_bullet_square, create_camera, create_enemy_spawner,
                                       create_input_player, create_interface, create_pause_texts,
                                       create_player_square, create_shield)

from src.ecs.components.c_input_command import CInputCommand, CommandPhase
from src.ecs.components.c_surface import CSurface
from src.ecs.components.c_transform import CTransform
from src.ecs.components.c_velocity import CVelocity
from src.ecs.components.tags.c_tag_bullet import CTagBullet
from src.ecs.components.tags.c_tag_pause_text import CTagPauseText

from src.ecs.systems.s_animation import system_animation
from src.ecs.systems.s_bullet_limits import system_bullet_limits
from src.ecs.systems.s_camera_shake import system_camera_shake
from src.ecs.systems.s_collision_enemy_bullet import system_collision_enemy_bullet
from src.ecs.systems.s_collision_player_enemy import system_collision_player_enemy
from src.ecs.systems.s_enemy_spawner import system_enemy_spawner
from src.ecs.systems.s_explosion_kill import system_explosion_kill
from src.ecs.systems.s_hunter_state import system_hunter_state
from src.ecs.systems.s_input_player import system_input_player
from src.ecs.systems.s_movement import system_movement
from src.ecs.systems.s_player_limits import system_player_limits
from src.ecs.systems.s_player_state import system_player_state
from src.ecs.systems.s_rendering import system_rendering
from src.ecs.systems.s_screen_bounce import system_screen_bounce
from src.ecs.systems.s_shield import system_shield
from src.ecs.systems.s_shield_hud import system_shield_hud

from src.engine.service_locator import ServiceLocator

class GameEngine:
    def __init__(self) -> None:
        self._load_config_files()

        pygame.init()
        pygame.display.set_caption(self.window_cfg["title"])
        self.screen = pygame.display.set_mode(
            (self.window_cfg["size"]["w"], self.window_cfg["size"]["h"]),
            pygame.SCALED)
        self.clock = pygame.time.Clock()
        self.is_running = False
        self.is_paused = False
        self.framerate = self.window_cfg["framerate"]
        self.delta_time = 0
        self.game_time = 0
        self.bg_color = pygame.Color(self.window_cfg["bg_color"]["r"],
                                     self.window_cfg["bg_color"]["g"],
                                     self.window_cfg["bg_color"]["b"])

        self.ecs_world = esper.World()

    def _load_config_files(self):
        configs = ServiceLocator.configs_service
        window_data = configs.get("assets/cfg/window.json")
        self.window_cfg = window_data.get("window", window_data)
        self.enemies_cfg = configs.get("assets/cfg/enemies.json")
        self.level_01_cfg = configs.get("assets/cfg/level_01.json")
        self.player_cfg = configs.get("assets/cfg/player.json")
        self.bullet_cfg = configs.get("assets/cfg/bullet.json")
        self.explosion_cfg = configs.get("assets/cfg/explosion.json")
        self.interface_cfg = configs.get("assets/cfg/interface.json")
        self.shield_cfg = configs.get("assets/cfg/shield.json")

    async def run(self) -> None:
        self._create()
        self.is_running = True
        while self.is_running:
            self._calculate_time()
            self._process_events()
            self._update()
            self._draw()
            await asyncio.sleep(0)
        self._clean()

    def _create(self):
        self._player_entity = create_player_square(self.ecs_world, self.player_cfg,
                                                   self.level_01_cfg["player_spawn"], self.shield_cfg)
        self._player_c_v = self.ecs_world.component_for_entity(self._player_entity, CVelocity)
        self._player_c_t = self.ecs_world.component_for_entity(self._player_entity, CTransform)
        self._player_c_s = self.ecs_world.component_for_entity(self._player_entity, CSurface)
        self.max_bullets = self.level_01_cfg["player_spawn"]["max_bullets"]
        self.num_bullets = 0

        create_enemy_spawner(self.ecs_world, self.level_01_cfg)
        create_input_player(self.ecs_world)
        create_camera(self.ecs_world)
        create_interface(self.ecs_world, self.interface_cfg)

    def _calculate_time(self):
        self.clock.tick(self.framerate)
        self.delta_time = self.clock.get_time() / 1000.0

    def _process_events(self):
        for event in pygame.event.get():
            system_input_player(self.ecs_world, event, self._do_action)
            if event.type == pygame.QUIT:
                self.is_running = False

    def _update(self):
        # En pausa no se ejecutan los sistemas del juego: nada se mueve, choca ni anima
        if self.is_paused:
            return
        self.game_time += self.delta_time

        system_enemy_spawner(self.ecs_world, self.enemies_cfg, self.delta_time)
        system_movement(self.ecs_world, self.delta_time)

        system_player_state(self.ecs_world, self.player_cfg)
        system_hunter_state(self.ecs_world, self._player_entity, self.delta_time, self.enemies_cfg["Hunter"])

        system_screen_bounce(self.ecs_world, self.screen)
        system_player_limits(self.ecs_world, self.screen)
        system_bullet_limits(self.ecs_world, self.screen)

        system_shield(self.ecs_world, self.delta_time, self.shield_cfg, self.explosion_cfg)
        system_collision_player_enemy(self.ecs_world, self._player_entity, self.level_01_cfg, self.explosion_cfg)
        system_collision_enemy_bullet(self.ecs_world, self.explosion_cfg)

        system_explosion_kill(self.ecs_world, self.delta_time)
        system_animation(self.ecs_world, self.delta_time)
        system_camera_shake(self.ecs_world, self.delta_time)
        system_shield_hud(self.ecs_world, self._player_entity, self.interface_cfg, self.game_time)
        self.ecs_world._clear_dead_entities()
        self.num_bullets = len(self.ecs_world.get_component(CTagBullet))

    def _draw(self):
        self.screen.fill(self.bg_color)
        system_rendering(self.ecs_world, self.screen)
        pygame.display.flip()

    def _clean(self):
        self.ecs_world.clear_database()
        pygame.quit()

    def _toggle_pause(self):
        self.is_paused = not self.is_paused
        if self.is_paused:
            pygame.mixer.pause()
            create_pause_texts(self.ecs_world, self.interface_cfg, self.screen.get_size())
        else:
            pygame.mixer.unpause()
            for pause_entity, _ in self.ecs_world.get_component(CTagPauseText):
                self.ecs_world.delete_entity(pause_entity, immediate=True)

    def _do_action(self, c_input:CInputCommand):
        # Las flechas siempre actualizan la velocidad (aun en pausa) para no
        # perder el estado de las teclas presionadas; como el sistema de
        # movimiento no corre en pausa, el jugador no se mueve.
        if c_input.name == "PLAYER_LEFT":
            if c_input.phase == CommandPhase.START:
                self._player_c_v.vel.x -= self.player_cfg["input_velocity"]
            elif c_input.phase == CommandPhase.END:
                self._player_c_v.vel.x += self.player_cfg["input_velocity"]

        elif c_input.name == "PLAYER_RIGHT":
            if c_input.phase == CommandPhase.START:
                self._player_c_v.vel.x += self.player_cfg["input_velocity"]
            elif c_input.phase == CommandPhase.END:
                self._player_c_v.vel.x -= self.player_cfg["input_velocity"]

        elif c_input.name == "PLAYER_UP":
            if c_input.phase == CommandPhase.START:
                self._player_c_v.vel.y -= self.player_cfg["input_velocity"]
            elif c_input.phase == CommandPhase.END:
                self._player_c_v.vel.y += self.player_cfg["input_velocity"]

        elif c_input.name == "PLAYER_DOWN":
            if c_input.phase == CommandPhase.START:
                self._player_c_v.vel.y += self.player_cfg["input_velocity"]
            elif c_input.phase == CommandPhase.END:
                self._player_c_v.vel.y -= self.player_cfg["input_velocity"]

        elif c_input.name == "PAUSE":
            if c_input.phase == CommandPhase.START:
                self._toggle_pause()

        elif self.is_paused:
            return

        elif c_input.name == "PLAYER_FIRE":
            if c_input.phase == CommandPhase.START:
                self.num_bullets = len(self.ecs_world.get_component(CTagBullet))
                if self.num_bullets < self.max_bullets:
                    create_bullet_square(self.ecs_world,
                                         self._player_c_t.pos,
                                         self._player_c_s.area.size,
                                         pygame.Vector2(pygame.mouse.get_pos()),
                                         self.bullet_cfg)

        elif c_input.name == "PLAYER_SHIELD":
            if c_input.phase == CommandPhase.START:
                create_shield(self.ecs_world, self._player_entity, self.shield_cfg)
