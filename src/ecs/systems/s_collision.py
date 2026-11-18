"""Sistema de colisiones con hitbox circulares en un mundo con wraparound."""
import esper

from src.ecs.components.c_bullet import CBullet
from src.ecs.components.c_collider import CCollider
from src.ecs.components.c_core import CCore
from src.ecs.components.c_enemy import CEnemy
from src.ecs.components.c_explosion import CExplosion
from src.ecs.components.c_obstacle import CObstacle
from src.ecs.components.c_player import CPlayer, PlayerState
from src.ecs.components.c_spy import CSpy
from src.ecs.components.c_transform import CTransform
from src.ecs.components.c_turret import CTurret
from src.ecs.systems.s_damage import (destroy_obstacle, hit_core, kill_enemy, kill_player,
                                      kill_spy, kill_turret)
from src.engine.world_math import wrap_delta


def _collect(world, comp):
    out = []
    for ent, (c, c_t, c_c) in world.get_components(comp, CTransform, CCollider):
        out.append((ent, c, c_t.pos, c_c.radius))
    return out


def _hit(a_pos, a_r, b_pos, b_r, w, h) -> bool:
    d = wrap_delta(a_pos, b_pos, w, h)
    return d.length_squared() < (a_r + b_r) ** 2


def system_collision(world: esper.World, ctx) -> None:
    w, h = ctx.world_w, ctx.world_h
    alive = world.entity_exists
    bullets = _collect(world, CBullet)
    enemies = _collect(world, CEnemy)
    spies = _collect(world, CSpy)
    turrets = _collect(world, CTurret)
    cores = _collect(world, CCore)
    obstacles = _collect(world, CObstacle)
    players = [p for p in _collect(world, CPlayer) if p[1].state == PlayerState.ALIVE]

    # 1. Balas del jugador
    for b_ent, c_b, b_pos, b_r in bullets:
        if not c_b.from_player:
            continue
        done = False
        for group, action in ((enemies, lambda e: kill_enemy(world, e, ctx)),
                              (spies, lambda e: kill_spy(world, e, ctx)),
                              (turrets, lambda e: kill_turret(world, e, ctx)),
                              (obstacles, None),
                              (cores, None)):
            for ent, comp, pos, r in group:
                if done:
                    break
                if not alive(ent) or not alive(b_ent) or not _hit(b_pos, b_r, pos, r, w, h):
                    continue
                if group is obstacles:
                    if comp.kind != "hard_rock":
                        destroy_obstacle(world, ent, ctx)
                    else:
                        ctx.sfx("rock", 0.2)
                elif group is cores:
                    if not hit_core(world, ent, ctx):
                        ctx.sfx("rock", 0.2)
                elif group is turrets:
                    if world.has_component(ent, CCollider):
                        action(ent)
                    else:
                        continue
                else:
                    action(ent)
                world.delete_entity(b_ent)
                done = True

    # 2. Jugador contra todo lo peligroso
    for p_ent, c_p, p_pos, p_r in players:
        if c_p.invulnerable > 0:
            continue
        for b_ent, c_b, b_pos, b_r in bullets:
            if not c_b.from_player and alive(b_ent) and _hit(p_pos, p_r, b_pos, b_r, w, h):
                world.delete_entity(b_ent)
                kill_player(world, p_ent, ctx)
        for ent, _, pos, r in enemies + spies:
            if alive(ent) and _hit(p_pos, p_r, pos, r, w, h):
                if world.has_component(ent, CSpy):
                    kill_spy(world, ent, ctx)
                else:
                    kill_enemy(world, ent, ctx)
                kill_player(world, p_ent, ctx)
        for ent, comp, pos, r in obstacles:
            if alive(ent) and _hit(p_pos, p_r, pos, r, w, h):
                if comp.kind != "hard_rock":
                    destroy_obstacle(world, ent, ctx, scored=False)
                kill_player(world, p_ent, ctx)
        for ent, _, pos, r in turrets + cores:
            if alive(ent) and world.has_component(ent, CCollider) and _hit(p_pos, p_r, pos, r, w, h):
                kill_player(world, p_ent, ctx)

    # 3. Enemigos contra obstaculos (rocas y minas tambien los destruyen)
    for e_ent, c_e, e_pos, e_r in enemies:
        for o_ent, c_o, o_pos, o_r in obstacles:
            if alive(e_ent) and alive(o_ent) and _hit(e_pos, e_r, o_pos, o_r, w, h):
                if c_o.kind == "mine":
                    destroy_obstacle(world, o_ent, ctx, scored=False)
                kill_enemy(world, e_ent, ctx, scored=False)

    # 4. Explosiones letales de minas
    for x_ent, (c_x, c_t) in world.get_components(CExplosion, CTransform):
        if not c_x.lethal or c_x.delay > 0:
            continue
        for p_ent, _, p_pos, p_r in players:
            if _hit(c_t.pos, c_x.radius, p_pos, p_r, w, h):
                kill_player(world, p_ent, ctx)
        for ent, _, pos, r in enemies:
            if alive(ent) and _hit(c_t.pos, c_x.radius, pos, r, w, h):
                kill_enemy(world, ent, ctx)
        for ent, comp, pos, r in obstacles:
            if alive(ent) and comp.kind == "mine" and _hit(c_t.pos, c_x.radius, pos, r, w, h):
                destroy_obstacle(world, ent, ctx)  # reaccion en cadena
