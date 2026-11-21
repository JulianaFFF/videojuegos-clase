"""Utilidades matematicas para un mundo toroidal (wraparound)."""
import math

import pygame


def wrap_delta(src: pygame.Vector2, dst: pygame.Vector2, w: float, h: float) -> pygame.Vector2:
    """Vector mas corto de src a dst teniendo en cuenta que el mundo se envuelve."""
    dx = (dst.x - src.x + w / 2) % w - w / 2
    dy = (dst.y - src.y + h / 2) % h - h / 2
    return pygame.Vector2(dx, dy)


def wrap_pos(pos: pygame.Vector2, w: float, h: float) -> None:
    pos.x %= w
    pos.y %= h


def angle_of(vec: pygame.Vector2) -> float:
    """Angulo en grados medido en sentido horario desde 'arriba' (0 = arriba, 90 = derecha)."""
    if vec.length_squared() == 0:
        return 0.0
    return math.degrees(math.atan2(vec.x, -vec.y)) % 360


def from_angle(deg: float) -> pygame.Vector2:
    rad = math.radians(deg)
    return pygame.Vector2(math.sin(rad), -math.cos(rad))


def snap_angle(deg: float, step: int) -> int:
    return int(round(deg / step) * step) % 360
