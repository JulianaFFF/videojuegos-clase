import random

import esper
import pygame

from src.ecs.components.c_camera import CCamera
from src.ecs.components.c_player import CPlayer
from src.ecs.components.c_transform import CTransform
from src.engine.world_math import wrap_delta


def system_camera(world: esper.World, delta_time: float, world_w: int, world_h: int) -> pygame.Vector2:
    """La camara sigue al jugador. Devuelve el desplazamiento del cuadro (para el parallax)."""
    moved = pygame.Vector2(0, 0)
    for _, c_c in world.get_component(CCamera):
        for _, (_, c_t) in world.get_components(CPlayer, CTransform):
            moved = wrap_delta(c_c.pos, c_t.pos, world_w, world_h)
            c_c.pos.update(c_t.pos)
        if c_c.shake_time > 0:
            c_c.shake_time -= delta_time
            mag = c_c.shake_mag * max(0.0, c_c.shake_time)
            c_c.offset.update(random.uniform(-mag, mag), random.uniform(-mag, mag))
        else:
            c_c.offset.update(0, 0)
    return moved
