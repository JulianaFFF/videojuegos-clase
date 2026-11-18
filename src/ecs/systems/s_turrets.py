import esper
import pygame

from src.create.prefab_creator import cfg, create_enemy_bullet
from src.ecs.components.c_player import CPlayer, PlayerState
from src.ecs.components.c_surface import CSurface
from src.ecs.components.c_transform import CTransform
from src.ecs.components.c_turret import CTurret, TurretState
from src.engine.service_locator import ServiceLocator
from src.engine.world_math import wrap_delta


def system_turrets(world: esper.World, delta_time: float, ctx) -> None:
    """Torres de las bases (patron State): IDLE -> AIM -> FIRE -> IDLE. DEAD es final."""
    t_cfg = cfg("bases")["turret"]
    images = ServiceLocator.images_service
    player_pos = None
    for _, (c_p, c_t) in world.get_components(CPlayer, CTransform):
        if c_p.state == PlayerState.ALIVE:
            player_pos = c_t.pos

    for _, (c_tu, c_t, c_s) in world.get_components(CTurret, CTransform, CSurface):
        if c_tu.state == TurretState.DEAD:
            continue
        c_tu.timer -= delta_time
        to_p = wrap_delta(c_t.pos, player_pos, ctx.world_w, ctx.world_h) \
            if player_pos is not None else None
        in_range = to_p is not None and to_p.length() < t_cfg["range"]
        if c_tu.state == TurretState.IDLE:
            if c_tu.timer <= 0 and in_range:
                c_tu.state = TurretState.AIM
                c_tu.timer = t_cfg["aim_time"]
                c_s.surf = images.get_frame("turret_fire")
        elif c_tu.state == TurretState.AIM:
            if c_tu.timer <= 0:
                c_tu.state = TurretState.FIRE
        elif c_tu.state == TurretState.FIRE:
            if in_range and to_p.length() > 0:
                vel = to_p.normalize() * t_cfg["bullet_speed"]
                create_enemy_bullet(world, pygame.Vector2(c_t.pos), vel, t_cfg["bullet_ttl"])
                ctx.sfx("enemy_shot", 0.3)
            c_tu.state = TurretState.IDLE
            c_tu.timer = c_tu.cooldown
            c_s.surf = images.get_frame("turret")
