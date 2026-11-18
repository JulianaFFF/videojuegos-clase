import random

import esper
import pygame

from src.create.prefab_creator import cfg, create_enemy, create_formation, create_spy
from src.ecs.components.c_alert import CAlert
from src.ecs.components.c_enemy import CEnemy
from src.ecs.components.c_player import CPlayer, PlayerState
from src.ecs.components.c_spawner import CSpawner
from src.ecs.components.c_transform import CTransform


def _spawn_point(player_pos: pygame.Vector2, w: int, h: int) -> pygame.Vector2:
    """Punto fuera de la vista, a cierta distancia del jugador."""
    off = pygame.Vector2(1, 0).rotate(random.uniform(0, 360)) * random.uniform(150, 220)
    p = player_pos + off
    return pygame.Vector2(p.x % w, p.y % h)


def system_spawner(world: esper.World, delta_time: float, ctx) -> None:
    alerts = cfg("alerts")
    level = "GREEN"
    for _, c_a in world.get_component(CAlert):
        level = c_a.level.name
    player_pos = None
    for _, (c_p, c_t) in world.get_components(CPlayer, CTransform):
        if c_p.state == PlayerState.ALIVE:
            player_pos = c_t.pos
    if player_pos is None:
        return
    for _, c_s in world.get_component(CSpawner):
        c_s.time += delta_time
        c_s.timer -= delta_time
        n_enemies = sum(1 for _, e in world.get_component(CEnemy) if e.kind != "E")
        if c_s.timer <= 0:
            c_s.timer = c_s.interval * alerts[level]["spawn_interval_mult"]
            if n_enemies < alerts[level]["max_enemies"]:
                create_enemy(world, random.choice(c_s.types),
                             _spawn_point(player_pos, ctx.world_w, ctx.world_h))
        if c_s.spy_time > 0 and not c_s.spy_spawned and c_s.time > c_s.spy_time:
            c_s.spy_spawned = True
            create_spy(world, _spawn_point(player_pos, ctx.world_w, ctx.world_h))
            ctx.on_spy_appears()
        if c_s.formation:
            c_s.formation_timer -= delta_time
            if c_s.formation_timer <= 0:
                c_s.formation_timer = 25.0 if level != "RED" else 14.0
                create_formation(world, _spawn_point(player_pos, ctx.world_w, ctx.world_h))
                ctx.on_formation()
