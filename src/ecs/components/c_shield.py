from enum import Enum


class ShieldState(Enum):
    READY = 0
    ACTIVE = 1
    COOLDOWN = 2


class CShield:

    def __init__(self, shield_info: dict) -> None:
        self.state = ShieldState.READY
        self.time_left = 0.0  # Seconds left of the current state (ACTIVE or COOLDOWN)
        self.ready_flash = 0.0
        self.duration = shield_info["duration"]
        self.cooldown = shield_info["cooldown"]
        self.radius = shield_info["radius"]
        self.blink_time = shield_info["blink_time"]
        self.ready_flash_time = shield_info["ready_flash_time"]
        self.shake_kill = shield_info["shake_kill"]
