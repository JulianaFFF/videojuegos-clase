from enum import Enum


class CoreState(Enum):
    OPEN = 0
    CLOSING = 1
    CLOSED = 2
    OPENING = 3


class CCore:
    """Nucleo de la base. Si 'animated' alterna entre abierto (vulnerable) y cerrado."""
    def __init__(self, base: int, animated: bool, launches_e: bool) -> None:
        self.base = base
        self.animated = animated
        self.launches_e = launches_e
        self.state = CoreState.OPEN
        self.timer = 0.0
        self.e_timer = 2.0
