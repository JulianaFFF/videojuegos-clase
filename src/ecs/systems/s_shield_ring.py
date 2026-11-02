import pygame
import esper
from src.ecs.components.c_shield_ring import CShieldRing
from src.ecs.components.c_surface import CSurface


def _ease_out_back(t: float) -> float:
    """Goes from 0 to 1 passing slightly over 1, so the ring feels like it snaps into place."""
    overshoot = 3.0
    t -= 1
    return 1 + (overshoot + 1) * t**3 + overshoot * t**2


def system_shield_ring(world: esper.World, dt: float):
    """
    System that redraws the ring that marks the range of the shield, growing from the player.
    """
    for _, (c_s, c_r) in world.get_components(CSurface, CShieldRing):
        c_r.elapsed += dt
        radius = c_r.radius * _ease_out_back(min(c_r.elapsed / c_r.grow_time, 1))
        center = c_s.surf.get_rect().center
        c_s.surf.fill((0, 0, 0, 0))
        pygame.draw.circle(c_s.surf, (c_r.color.r, c_r.color.g, c_r.color.b, 40), center, radius)
        pygame.draw.circle(c_s.surf, c_r.color, center, radius, 2)
