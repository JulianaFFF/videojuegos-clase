class CShield:
    def __init__(self, shield_info:dict) -> None:
        self.duration = shield_info["duration"]
        self.cooldown = shield_info["cooldown"]
        self.radius = shield_info["radius"]
        self.time_active = 0.0
        self.time_cooldown = 0.0
        self.shield_entity = -1

    @property
    def is_active(self) -> bool:
        return self.time_active > 0

    @property
    def is_ready(self) -> bool:
        return self.time_active <= 0 and self.time_cooldown <= 0
