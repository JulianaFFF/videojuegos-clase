import pygame
import esper
from src.ecs.components.c_animation import CAnimation
from src.ecs.components.c_surface import CSurface
from src.ecs.components.c_transform import CTransform
from src.ecs.components.c_velocity import CVelocity
from src.ecs.components.c_enemy_hunter_state import CEnemyHunterState, HunterState


def system_enemy_hunter_state(world: esper.World, player_entity: int, dt: float):
    """
    State machine of the Hunter enemy:
    IDLE   -> CHASE  when the player is closer than distance_start_chase.
    CHASE  -> RETURN when it gets farther than distance_start_return from its origin.
    RETURN -> IDLE   when it reaches its origin again.
    """
    pl_t = world.component_for_entity(player_entity, CTransform)
    pl_s = world.component_for_entity(player_entity, CSurface)
    player_center = pl_t.pos + pygame.Vector2(pl_s.area.size) / 2

    components = world.get_components(CTransform, CVelocity, CSurface, CEnemyHunterState)
    for ent, (c_t, c_v, c_s, c_hst) in components:
        half_size = pygame.Vector2(c_s.area.size) / 2
        hunter_center = c_t.pos + half_size
        origin_center = c_hst.start_pos + half_size

        if c_hst.state == HunterState.IDLE:
            c_v.vel.xy = (0, 0)
            if hunter_center.distance_to(player_center) < c_hst.distance_start_chase:
                c_hst.state = HunterState.CHASE

        if c_hst.state == HunterState.CHASE:
            if hunter_center.distance_to(origin_center) >= c_hst.distance_start_return:
                c_hst.state = HunterState.RETURN
            else:
                direction = player_center - hunter_center
                if direction.length_squared() > 0:
                    c_v.vel = direction.normalize() * c_hst.velocity_chase
                else:
                    c_v.vel.xy = (0, 0)

        if c_hst.state == HunterState.RETURN:
            to_origin = c_hst.start_pos - c_t.pos
            step = c_hst.velocity_return * dt
            if to_origin.length() <= step:
                # Arrived: snap to the origin so it does not oscillate around it
                c_t.pos.xy = c_hst.start_pos
                c_v.vel.xy = (0, 0)
                c_hst.state = HunterState.IDLE
            else:
                c_v.vel = to_origin.normalize() * c_hst.velocity_return

        if world.has_component(ent, CAnimation):
            c_a = world.component_for_entity(ent, CAnimation)
            c_a.set_animation("IDLE" if c_hst.state == HunterState.IDLE else "MOVE")
