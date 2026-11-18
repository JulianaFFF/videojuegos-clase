from enum import Enum


class TurretState(Enum):
    IDLE = 0
    AIM = 1
    FIRE = 2
    DEAD = 3


class CTurret:
    def __init__(self, base: int, cooldown: float) -> None:
        self.base = base
        self.state = TurretState.IDLE
        self.timer = cooldown
        self.cooldown = cooldown
