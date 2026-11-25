"""Escena de juego: una ronda. Al limpiarla se recarga con la ronda siguiente."""
import random

import pygame

from src.create.prefab_creator import (cfg, create_base, create_camera, create_obstacle,
                                       create_player, create_player_bullet, create_round_logic,
                                       create_starfield)
from src.ecs.components.c_alert import AlertLevel, CAlert
from src.ecs.components.c_base import CBase
from src.ecs.components.c_bullet import CBullet
from src.ecs.components.c_camera import CCamera
from src.ecs.components.c_input_command import CInputCommand, CommandPhase
from src.ecs.components.c_player import CPlayer, PlayerState
from src.ecs.components.c_surface import CSurface
from src.ecs.components.c_transform import CTransform
from src.ecs.components.c_velocity import CVelocity
from src.ecs.systems.s_alert import set_alert, system_alert
from src.ecs.systems.s_animation import system_animation
from src.ecs.systems.s_bullet_ttl import system_bullet_ttl
from src.ecs.systems.s_camera import system_camera
from src.ecs.systems.s_collision import system_collision
from src.ecs.systems.s_core import system_core
from src.ecs.systems.s_damage import kill_enemy
from src.ecs.systems.s_enemy_ai import system_enemy_ai
from src.ecs.systems.s_explosion import system_explosion
from src.ecs.systems.s_hud import system_hud
from src.ecs.systems.s_movement import system_movement
from src.ecs.systems.s_orientation import system_orientation
from src.ecs.systems.s_player_control import system_player_control
from src.ecs.systems.s_rendering import system_rendering
from src.ecs.systems.s_spawner import system_spawner
from src.ecs.systems.s_starfield import system_draw_starfield, system_starfield
from src.ecs.systems.s_turrets import system_turrets
from src.ecs.systems.s_wraparound import system_wraparound
from src.engine.scenes_base import Scene
from src.engine.service_locator import ServiceLocator
from src.engine.world_math import from_angle, wrap_delta


class PlayScene(Scene):
    def __init__(self, game_engine) -> None:
        super().__init__(game_engine)
        world_cfg = cfg("world")
        win = cfg("window")
        self.world_w = world_cfg["size"]["w"]
        self.world_h = world_cfg["size"]["h"]
        self.view = pygame.Rect(0, 0, win["play_area"]["w"], win["play_area"]["h"])
        self.panel = pygame.Rect(self.view.right, 0, win["size"]["w"] - self.view.w, win["size"]["h"])
        self.session = game_engine.session
        self.levels = cfg("levels")
        self.round_cfg = self.levels["rounds"][(self.session.round - 1) % len(self.levels["rounds"])]
        self.font = ServiceLocator.fonts_service.get(cfg("interface")["font"], 8)
        self.paused = False
        self.banner_time = cfg("interface")["round_banner_time"]
        self.clear_time = -1.0
        self.over_time = -1.0
        self.popup_text = ""
        self.popup_time = 0.0
        self.player_ent = None

    # ------------------------------------------------------------------ creacion
    def do_create(self) -> None:
        super().do_create()
        start = pygame.Vector2(self.levels["player_start"]["x"], self.levels["player_start"]["y"])
        create_starfield(self.ecs_world, self.view.w, self.view.h)
        create_camera(self.ecs_world, start, self.view.w, self.view.h)
        create_round_logic(self.ecs_world, self.round_cfg)
        base_positions = []
        for b in self.round_cfg["bases"]:
            create_base(self.ecs_world, (b["x"], b["y"]), b["layout"], self.round_cfg)
            base_positions.append(pygame.Vector2(b["x"], b["y"]))
        rng = random.Random(self.session.round * 7919)
        for kind, count in (("rock", self.round_cfg["rocks"]), ("hard_rock", self.round_cfg["hard_rocks"]),
                            ("mine", self.round_cfg["mines"])):
            for _ in range(count):
                for _try in range(40):
                    p = pygame.Vector2(rng.uniform(0, self.world_w), rng.uniform(0, self.world_h))
                    if wrap_delta(p, start, self.world_w, self.world_h).length() < 90:
                        continue
                    if any(wrap_delta(p, b, self.world_w, self.world_h).length() < 60 for b in base_positions):
                        continue
                    create_obstacle(self.ecs_world, kind, p)
                    break
        self.player_ent = create_player(self.ecs_world, start, self.round_cfg["special_charges"])
        music = cfg("music")
        ServiceLocator.sounds_service.play_music(
            music["rounds"][(self.session.round - 1) % len(music["rounds"])], music["volume"])
        self.sfx("round_start", 0.6)

    # ------------------------------------------------------------------ contexto para sistemas
    def sfx(self, name: str, volume: float = 0.5) -> None:
        ServiceLocator.sounds_service.play(cfg("sounds")[name], volume)

    def shake(self, duration: float, magnitude: float) -> None:
        for _, c_c in self.ecs_world.get_component(CCamera):
            c_c.shake_time = max(c_c.shake_time, duration)
            c_c.shake_mag = magnitude

    def add_score(self, points: int) -> None:
        if self.session.add_score(points):
            self.sfx("extra_life", 0.7)
            self.popup("1UP!")

    def popup(self, text: str, duration: float = 2.0) -> None:
        self.popup_text = text
        self.popup_time = duration

    def kill_enemy(self, ent: int, scored: bool = True) -> None:
        kill_enemy(self.ecs_world, ent, self, scored)

    def on_alert_changed(self, level: AlertLevel) -> None:
        a_cfg = cfg("alerts")[level.name]
        ServiceLocator.sounds_service.play(a_cfg["sound"], 0.6)
        self.popup(a_cfg["text"], 2.5)

    def on_spy_appears(self) -> None:
        self.sfx("spy", 0.6)
        self.popup("SPY SHIP SIGHTED", 2.5)

    def on_spy_escape(self) -> None:
        for _, c_a in self.ecs_world.get_component(CAlert):
            set_alert(c_a, AlertLevel.RED)
        self.popup("EL ESPIA ESCAPO!", 2.5)

    def on_formation(self) -> None:
        self.sfx("spy", 0.5)
        self.popup("FORMATION ATTACK", 2.5)

    # ------------------------------------------------------------------ comandos
    def do_action(self, action: CInputCommand) -> None:
        if action.name == "PAUSE" and action.phase == CommandPhase.START:
            self.paused = not self.paused
            return
        c_p = self.ecs_world.component_for_entity(self.player_ent, CPlayer)
        if action.name in ("UP", "DOWN", "LEFT", "RIGHT"):
            if action.phase == CommandPhase.START:
                c_p.held.add(action.name)
            else:
                c_p.held.discard(action.name)
            return
        if self.paused or c_p.state != PlayerState.ALIVE or self.banner_time > 0 \
                or action.phase != CommandPhase.START:
            return
        if action.name == "FIRE":
            self._fire(c_p)
        elif action.name == "SPECIAL":
            self._special(c_p)

    def _player_bullets(self) -> int:
        return sum(1 for _, b in self.ecs_world.get_component(CBullet) if b.from_player)

    def _fire(self, c_p: CPlayer) -> None:
        """Disparo simple: dos balas, una al frente y otra atras."""
        p_cfg = cfg("player")
        if c_p.fire_cooldown > 0 or self._player_bullets() > p_cfg["bullet"]["max_on_screen"] - 2:
            return
        c_p.fire_cooldown = p_cfg["bullet"]["cooldown"]
        pos = self.ecs_world.component_for_entity(self.player_ent, CTransform).pos
        vel = self.ecs_world.component_for_entity(self.player_ent, CVelocity).vel
        create_player_bullet(self.ecs_world, pos, c_p.heading, vel)
        create_player_bullet(self.ecs_world, pos, -c_p.heading, vel)
        self.sfx("shoot", 0.3)

    def _special(self, c_p: CPlayer) -> None:
        """Disparo especial: tres balas al frente (abanico) y una atras. Cargas definidas por ronda."""
        p_cfg = cfg("player")
        if c_p.special_charges <= 0 or c_p.fire_cooldown > 0:
            return
        c_p.special_charges -= 1
        c_p.fire_cooldown = p_cfg["special"]["cooldown"]
        pos = self.ecs_world.component_for_entity(self.player_ent, CTransform).pos
        vel = self.ecs_world.component_for_entity(self.player_ent, CVelocity).vel
        base_ang = pygame.Vector2(0, -1).angle_to(c_p.heading)
        spread = p_cfg["special"]["spread_deg"]
        for d in (-spread, 0, spread):
            create_player_bullet(self.ecs_world, pos, from_angle(base_ang + d), vel)
        create_player_bullet(self.ecs_world, pos, -c_p.heading, vel)
        self.sfx("special", 0.5)

    # ------------------------------------------------------------------ bucle
    def do_update(self, delta_time: float) -> None:
        if self.paused:
            return
        world = self.ecs_world
        self.popup_time = max(0.0, self.popup_time - delta_time)
        if self.banner_time > 0:
            self.banner_time -= delta_time
            system_starfield(world, delta_time, pygame.Vector2(0, -0.3), self.view.w, self.view.h, self.time)
            return

        system_player_control(world, delta_time)
        system_enemy_ai(world, delta_time, self)
        system_turrets(world, delta_time, self)
        system_core(world, delta_time, self)
        if self.clear_time < 0:
            system_spawner(world, delta_time, self)
            system_alert(world, delta_time, self)
        system_movement(world, delta_time)
        system_wraparound(world, self.world_w, self.world_h)
        scroll = system_camera(world, delta_time, self.world_w, self.world_h)
        system_starfield(world, delta_time, scroll, self.view.w, self.view.h, self.time)
        system_collision(world, self)
        system_bullet_ttl(world, delta_time)
        system_orientation(world)
        system_animation(world, delta_time)
        system_explosion(world, delta_time)
        self._update_player_state(delta_time)
        self._update_round_state(delta_time)

    def _update_player_state(self, delta_time: float) -> None:
        """Muerte -> espera -> reaparicion con invulnerabilidad, o fin del juego."""
        c_p = self.ecs_world.component_for_entity(self.player_ent, CPlayer)
        if c_p.state != PlayerState.DEAD:
            return
        c_p.dead_time += delta_time
        if c_p.dead_time < cfg("player")["respawn_time"]:
            return
        if self.session.lives > 0:
            self.session.lives -= 1
            c_p.state = PlayerState.ALIVE
            c_p.invulnerable = cfg("player")["invulnerable_time"]
            c_p.held = {n for _, ci in self.ecs_world.get_component(CInputCommand) if ci.held
                        for n in [ci.name] if n in ("UP", "DOWN", "LEFT", "RIGHT")}
            self.ecs_world.component_for_entity(self.player_ent, CSurface).visible = True
            self.banner_time = 1.2
        else:
            self.switch_scene("game_over")

    def _update_round_state(self, delta_time: float) -> None:
        bases_left = sum(1 for _ in self.ecs_world.get_component(CBase))
        if bases_left == 0 and self.clear_time < 0:
            self.clear_time = 3.0
            self.add_score(cfg("score")["round_clear_bonus"])
            self.popup("ROUND CLEAR!", 3.0)
        if self.clear_time > 0:
            self.clear_time -= delta_time
            if self.clear_time <= 0:
                if self.session.round >= len(self.levels["rounds"]):
                    self.switch_scene("victory")
                else:
                    self.session.round += 1
                    self.switch_scene("play")

    # ------------------------------------------------------------------ dibujo
    def do_draw(self, screen: pygame.Surface) -> None:
        screen.set_clip(self.view)
        system_draw_starfield(self.ecs_world, screen)
        screen.set_clip(None)
        system_rendering(self.ecs_world, screen, self.world_w, self.world_h, self.view, self.time)
        system_hud(self.ecs_world, screen, self.session, self.panel, self.world_w, self.world_h, self.time)
        cx, cy = self.view.center
        if self.banner_time > 0:
            self._center_text(screen, "ROUND " + str(self.session.round), "yellow", cy - 30)
            self._center_text(screen, "READY", "white", cy - 16)
        if self.popup_time > 0 and int(self.popup_time * 6) % 2 == 0:
            self._center_text(screen, self.popup_text, "cyan", 20)
        if self.paused:
            self._center_text(screen, "PAUSA", "white", cy)

    def _center_text(self, screen, text: str, color: str, y: int) -> None:
        col = cfg("interface")["colors"][color]
        surf = self.font.render(text, False, col)
        bg = pygame.Rect(0, 0, surf.get_width() + 4, surf.get_height() + 4)
        bg.center = (self.view.centerx, y + surf.get_height() // 2)
        screen.fill((0, 0, 0), bg)
        screen.blit(surf, (self.view.centerx - surf.get_width() // 2, y))
