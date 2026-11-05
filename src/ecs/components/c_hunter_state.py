from enum import Enum

import pygame

class CHunterState:
    def __init__(self, origin:pygame.Vector2) -> None:
        self.state = HunterState.IDLE
        self.origin = pygame.Vector2(origin)


class HunterState(Enum):
    IDLE = 0
    CHASE = 1
    RETURN = 2
