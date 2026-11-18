import esper

from src.create.prefab_creator import cfg, create_enemy
from src.ecs.components.c_core import CCore, CoreState
from src.ecs.components.c_enemy import CEnemy, EnemyState
from src.ecs.components.c_player import CPlayer, PlayerState
from src.ecs.components.c_surface import CSurface
from src.ecs.components.c_transform import CTransform
from src.ecs.components.c_velocity import CVelocity
from src.engine.service_locator import ServiceLocator
from src.engine.world_math import wrap_delta

_FRAME_TIME = 0.12


def system_core(world: esper.World, delta_time: float, ctx) -> None:
    """Nucleo animado (State: OPEN/CLOSING/CLOSED/OPENING) y lanzamiento de enemigos E."""
    c_cfg = cfg("bases")["core"]
    images = ServiceLocator.images_service
    player_pos = None
    for _, (c_p, c_t) in world.get_components(CPlayer, CTransform):
        if c_p.state == PlayerState.ALIVE:
            player_pos = c_t.pos

    for _, (c_c, c_t, c_s) in world.get_components(CCore, CTransform, CSurface):
        c_c.timer += delta_time
        if c_c.animated:
            if c_c.state == CoreState.OPEN and c_c.timer > c_cfg["open_time"]:
                c_c.state, c_c.timer = CoreState.CLOSING, 0.0
            elif c_c.state == CoreState.CLOSING:
                frame = min(3, 1 + int(c_c.timer / _FRAME_TIME))
                c_s.surf = images.get_frame("core", frame)
                if c_c.timer > _FRAME_TIME * 3:
                    c_c.state, c_c.timer = CoreState.CLOSED, 0.0
            elif c_c.state == CoreState.CLOSED and c_c.timer > c_cfg["closed_time"]:
                c_c.state, c_c.timer = CoreState.OPENING, 0.0
            elif c_c.state == CoreState.OPENING:
                frame = max(0, 2 - int(c_c.timer / _FRAME_TIME))
                c_s.surf = images.get_frame("core", frame)
                if c_c.timer > _FRAME_TIME * 3:
                    c_c.state, c_c.timer = CoreState.OPEN, 0.0
                    c_s.surf = images.get_frame("core", 0)

        if c_c.launches_e and player_pos is not None:
            c_c.e_timer -= delta_time
            to_p = wrap_delta(c_t.pos, player_pos, ctx.world_w, ctx.world_h)
            if c_c.e_timer <= 0 and to_p.length() < c_cfg["e_launch_range"]:
                c_c.e_timer = c_cfg["e_cooldown"]
                e_count = sum(1 for _, e in world.get_component(CEnemy) if e.kind == "E")
                if e_count < 3:
                    ent = create_enemy(world, "E", c_t.pos)
                    e_c = world.component_for_entity(ent, CEnemy)
                    e_c.state = EnemyState.CHASE
                    if to_p.length() > 0:
                        world.component_for_entity(ent, CVelocity).vel = to_p.normalize() * e_c.speed
