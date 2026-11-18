from enum import Enum


class AlertLevel(Enum):
    GREEN = 0
    YELLOW = 1
    RED = 2


class CAlert:
    """Sistema de alertas (patron State). ROJA se activa por tiempo o si escapa el espia."""
    def __init__(self, yellow_time: float, red_time: float) -> None:
        self.level = AlertLevel.GREEN
        self.time = 0.0
        self.yellow_time = yellow_time
        self.red_time = red_time
        self.changed = True
