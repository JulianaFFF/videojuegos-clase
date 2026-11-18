import math

import esper
import pygame

from src.ecs.components.c_star import CStar


def system_starfield(world: esper.World, delta_time: float, scroll: pygame.Vector2,
                     area_w: int, area_h: int, time: float) -> None:
    """Parallax: cada capa se desplaza segun su profundidad. Parpadeo por estrella."""
    for _, c_s in world.get_component(CStar):
        c_s.pos -= scroll * c_s.depth
        c_s.pos.x %= area_w
        c_s.pos.y %= area_h
        c_s.visible = math.sin((time * c_s.blink_speed + c_s.phase) * 2 * math.pi * 2) > -0.3


def system_draw_starfield(world: esper.World, screen: pygame.Surface) -> None:
    for _, c_s in world.get_component(CStar):
        if c_s.visible:
            size = 2 if c_s.depth >= 0.8 else 1
            screen.fill(c_s.color, (int(c_s.pos.x), int(c_s.pos.y), size, 1))
