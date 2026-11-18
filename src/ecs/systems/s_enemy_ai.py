"""IA de enemigos: patron State + steering behaviours (seek, pursuit, flee, wander, arrive)."""
import random

import esper
import pygame

from src.ecs.components.c_enemy import CEnemy, EnemyState
from src.ecs.components.c_player import CPlayer, PlayerState
from src.ecs.components.c_spy import CSpy
from src.ecs.components.c_transform import CTransform
from src.ecs.components.c_velocity import CVelocity
from src.engine.world_math import wrap_delta


def _steer(c_v: CVelocity, desired: pygame.Vector2, turn: float, max_speed: float, dt: float) -> None:
    c_v.vel += (desired - c_v.vel) * min(1.0, turn * dt)
    if c_v.vel.length() > max_speed:
        c_v.vel.scale_to_length(max_speed)


def _change(c_e: CEnemy, state: EnemyState) -> None:
    c_e.state = state
    c_e.state_time = 0.0


def system_enemy_ai(world: esper.World, delta_time: float, ctx) -> None:
    w, h = ctx.world_w, ctx.world_h
    player_pos, player_vel, player_alive = None, pygame.Vector2(0, 0), False
    for p_ent, (c_p, c_t) in world.get_components(CPlayer, CTransform):
        player_pos = c_t.pos
        player_vel = world.component_for_entity(p_ent, CVelocity).vel
        player_alive = c_p.state == PlayerState.ALIVE

    for ent, (c_e, c_t, c_v) in world.get_components(CEnemy, CTransform, CVelocity):
        c_e.state_time += delta_time
        to_player = wrap_delta(c_t.pos, player_pos, w, h) if player_pos is not None else None
        dist = to_player.length() if to_player is not None else 99999

        # Enemigo E: misil con tiempo de vida limitado
        if c_e.life_time > 0 and c_e.state_time > c_e.life_time and c_e.kind == "E" \
                and c_e.state != EnemyState.FLEE:
            ctx.kill_enemy(ent, scored=False)
            continue

        # Formacion: los escoltas mantienen su posicion relativa al lider (arrive)
        if c_e.leader is not None:
            if world.entity_exists(c_e.leader) and world.has_component(c_e.leader, CEnemy):
                l_t = world.component_for_entity(c_e.leader, CTransform)
                l_v = world.component_for_entity(c_e.leader, CVelocity)
                ang = pygame.Vector2(0, -1).angle_to(l_v.vel) if l_v.vel.length() > 0 else 0
                target = l_t.pos + c_e.offset.rotate(ang)
                to_t = wrap_delta(c_t.pos, target, w, h)
                desired = to_t * 4
                if desired.length() > c_e.speed * 1.6:
                    desired.scale_to_length(c_e.speed * 1.6)
                _steer(c_v, desired, 8, c_e.speed * 1.6, delta_time)
                continue
            c_e.leader = None
            _change(c_e, EnemyState.CHASE)

        if c_e.state == EnemyState.WANDER:
            if c_e.wander_dir is None or c_e.state_time > c_e.wander_time:
                c_e.wander_dir = pygame.Vector2(1, 0).rotate(random.uniform(0, 360))
                c_e.state_time = 0.0
            _steer(c_v, c_e.wander_dir * c_e.speed * 0.7, c_e.turn, c_e.speed, delta_time)
            if player_alive and dist < c_e.sight:
                _change(c_e, EnemyState.CHASE)

        elif c_e.state == EnemyState.CHASE:
            if not player_alive or dist > c_e.sight * 1.6:
                _change(c_e, EnemyState.WANDER)
                continue
            # Pursuit: apunta a la posicion futura del jugador
            lead = dist / max(1.0, c_e.speed)
            target = to_player + player_vel * min(lead, 1.0)
            if target.length() > 0:
                _steer(c_v, target.normalize() * c_e.speed, c_e.turn, c_e.speed, delta_time)
            if c_e.kind == "P" and dist < 50:
                _change(c_e, EnemyState.ATTACK)

        elif c_e.state == EnemyState.ATTACK:
            # Embestida rapida
            if to_player is not None and to_player.length() > 0:
                _steer(c_v, to_player.normalize() * c_e.speed * 1.4, c_e.turn * 1.5,
                       c_e.speed * 1.4, delta_time)
            if c_e.state_time > 1.2:
                _change(c_e, EnemyState.FLEE)

        elif c_e.state == EnemyState.FLEE:
            if to_player is not None and to_player.length() > 0:
                _steer(c_v, -to_player.normalize() * c_e.speed, c_e.turn, c_e.speed, delta_time)
            if c_e.state_time > 1.0:
                _change(c_e, EnemyState.CHASE)

    # Espia: deambula evitando al jugador; si no muere a tiempo escapa -> ALERTA ROJA
    for ent, (c_s, c_t, c_v) in world.get_components(CSpy, CTransform, CVelocity):
        c_s.time += delta_time
        if player_pos is not None:
            away = -wrap_delta(c_t.pos, player_pos, w, h)
            if 0 < away.length() < 70:
                _steer(c_v, away.normalize() * 70, 2.0, 70, delta_time)
        if c_s.time > c_s.escape_time:
            world.delete_entity(ent)
            ctx.on_spy_escape()
