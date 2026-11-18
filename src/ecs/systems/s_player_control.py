import esper
import pygame

from src.ecs.components.c_player import CPlayer, PlayerState
from src.ecs.components.c_surface import CSurface
from src.ecs.components.c_velocity import CVelocity


def system_player_control(world: esper.World, delta_time: float) -> None:
    """Movimiento con aceleracion en 8 direcciones. La nave nunca se detiene del todo."""
    for ent, (c_p, c_v) in world.get_components(CPlayer, CVelocity):
        c_p.fire_cooldown = max(0.0, c_p.fire_cooldown - delta_time)
        if c_p.invulnerable > 0:
            c_p.invulnerable -= delta_time
            world.component_for_entity(ent, CSurface).flash = max(0.0, c_p.invulnerable)
        if c_p.state != PlayerState.ALIVE:
            c_v.vel.update(0, 0)
            continue
        d = pygame.Vector2(("RIGHT" in c_p.held) - ("LEFT" in c_p.held),
                           ("DOWN" in c_p.held) - ("UP" in c_p.held))
        if d.length_squared() > 0:
            c_p.heading = d.normalize()
            target = c_p.max_speed
        else:
            target = c_p.max_speed * 0.45
        if c_p.speed < target:
            c_p.speed = min(target, c_p.speed + c_p.accel * delta_time)
        else:
            c_p.speed = max(target, c_p.speed - c_p.accel * 0.5 * delta_time)
        # La velocidad gira suavemente hacia el rumbo (inercia)
        desired = c_p.heading * c_p.speed
        c_v.vel += (desired - c_v.vel) * min(1.0, 8 * delta_time)
