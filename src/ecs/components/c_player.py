from enum import Enum

import pygame


class PlayerState(Enum):
    ALIVE = 0
    DEAD = 1


class CPlayer:
    """Estado del jugador (patron State: ALIVE / DEAD)."""
    def __init__(self, cfg: dict, special_charges: int) -> None:
        self.state = PlayerState.ALIVE
        self.heading = pygame.Vector2(0, -1)
        self.input_dir = pygame.Vector2(0, 0)
        self.max_speed = cfg["max_speed"]
        self.accel = cfg["acceleration"]
        self.speed = 0.0
        self.dead_time = 0.0
        self.invulnerable = cfg["invulnerable_time"]
        self.fire_cooldown = 0.0
        self.special_charges = special_charges
        self.held = set()
