from enum import Enum
import pygame


class HunterState(Enum):
    IDLE = 0
    CHASE = 1
    RETURN = 2


class CEnemyHunterState:

    def __init__(self, start_pos: pygame.Vector2, hunter_info: dict) -> None:
        self.state = HunterState.IDLE
        self.start_pos = pygame.Vector2(start_pos)
        self.velocity_chase = hunter_info["velocity_chase"]
        self.velocity_return = hunter_info["velocity_return"]
        self.distance_start_chase = hunter_info["distance_start_chase"]
        self.distance_start_return = hunter_info["distance_start_return"]
        self.sound_chase = hunter_info["sound_chase"]
