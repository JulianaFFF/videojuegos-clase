"""Reglas de destruccion de entidades (compartidas por colisiones e IA)."""
import random

import esper
import pygame

from src.create.prefab_creator import cfg, create_explosion
from src.ecs.components.c_base import CBase
from src.ecs.components.c_collider import CCollider
from src.ecs.components.c_core import CCore, CoreState
from src.ecs.components.c_enemy import CEnemy
from src.ecs.components.c_obstacle import CObstacle
from src.ecs.components.c_player import CPlayer, PlayerState
from src.ecs.components.c_spy import CSpy
from src.ecs.components.c_surface import CSurface
from src.ecs.components.c_transform import CTransform
from src.ecs.components.c_turret import CTurret, TurretState
from src.engine.service_locator import ServiceLocator


def _pos(world, ent) -> pygame.Vector2:
    return pygame.Vector2(world.component_for_entity(ent, CTransform).pos)


def kill_enemy(world: esper.World, ent: int, ctx, scored: bool = True) -> None:
    if not world.entity_exists(ent):
        return
    c_e = world.try_component(ent, CEnemy)
    create_explosion(world, _pos(world, ent))
    ctx.sfx("enemy_die", 0.4)
    if scored and c_e is not None:
        ctx.add_score(c_e.points)
    world.delete_entity(ent)


def kill_spy(world: esper.World, ent: int, ctx) -> None:
    create_explosion(world, _pos(world, ent))
    ctx.sfx("enemy_die", 0.5)
    ctx.add_score(cfg("score")["spy_points"])
    ctx.popup("SPY " + str(cfg("score")["spy_points"]))
    world.delete_entity(ent)


def destroy_obstacle(world: esper.World, ent: int, ctx, scored: bool = True) -> None:
    c_o = world.component_for_entity(ent, CObstacle)
    pos = _pos(world, ent)
    if c_o.kind == "mine":
        create_explosion(world, pos, mine=True)
        ctx.sfx("mine", 0.6)
        ctx.shake(0.3, 6)
    else:
        create_explosion(world, pos)
        ctx.sfx("rock", 0.5)
    if scored:
        ctx.add_score(c_o.points)
    world.delete_entity(ent)


def kill_turret(world: esper.World, ent: int, ctx) -> None:
    c_tu = world.component_for_entity(ent, CTurret)
    if c_tu.state == TurretState.DEAD:
        return
    c_tu.state = TurretState.DEAD
    world.component_for_entity(ent, CSurface).surf = \
        ServiceLocator.images_service.get_frame("turret_dead")
    world.remove_component(ent, CCollider)
    create_explosion(world, _pos(world, ent))
    ctx.sfx("turret_die", 0.5)
    ctx.add_score(cfg("bases")["turret"]["points"])
    c_base = world.component_for_entity(c_tu.base, CBase)
    if all(world.component_for_entity(t, CTurret).state == TurretState.DEAD for t in c_base.turrets):
        destroy_base(world, c_tu.base, ctx)


def destroy_base(world: esper.World, base_ent: int, ctx) -> None:
    c_base = world.component_for_entity(base_ent, CBase)
    if not c_base.alive:
        return
    c_base.alive = False
    center = _pos(world, base_ent)
    n = cfg("bases")["explosions_on_destroy"]
    for i in range(n):
        off = pygame.Vector2(random.uniform(-30, 30), random.uniform(-30, 30))
        create_explosion(world, center + off, delay=i * 0.08)
    alive_turrets = sum(1 for t in c_base.turrets
                        if world.component_for_entity(t, CTurret).state != TurretState.DEAD)
    ctx.add_score(cfg("bases")["core"]["points"] + alive_turrets * cfg("bases")["turret"]["points"])
    ctx.sfx("base_die", 0.8)
    ctx.shake(0.6, 8)
    for t in c_base.turrets:
        world.delete_entity(t)
    world.delete_entity(c_base.core)
    world.delete_entity(base_ent)


def hit_core(world: esper.World, core_ent: int, ctx) -> bool:
    """El nucleo solo es vulnerable cuando esta abierto."""
    c_c = world.component_for_entity(core_ent, CCore)
    if c_c.state != CoreState.OPEN:
        return False
    destroy_base(world, c_c.base, ctx)
    return True


def kill_player(world: esper.World, ent: int, ctx) -> None:
    c_p = world.component_for_entity(ent, CPlayer)
    if c_p.state != PlayerState.ALIVE or c_p.invulnerable > 0:
        return
    c_p.state = PlayerState.DEAD
    c_p.dead_time = 0.0
    c_p.held.clear()
    c_p.speed = 0.0
    world.component_for_entity(ent, CSurface).visible = False
    pos = _pos(world, ent)
    n = cfg("player")["death_explosions"]
    for i in range(n):
        off = pygame.Vector2(random.uniform(-14, 14), random.uniform(-14, 14)) if i else pygame.Vector2()
        create_explosion(world, pos + off, delay=i * 0.12)
    ctx.sfx("player_die", 0.8)
    ctx.shake(0.8, 7)


def is_spy(world, ent) -> bool:
    return world.has_component(ent, CSpy)
