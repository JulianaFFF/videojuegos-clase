from enum import Enum


class CommandPhase(Enum):
    NA = 0
    START = 1
    END = 2


class CInputCommand:
    """Patron Command simplificado: una accion con nombre asociada a teclas/botones."""
    def __init__(self, name: str, keys: list, joy_buttons: list) -> None:
        self.name = name
        self.keys = keys
        self.joy_buttons = joy_buttons
        self.phase = CommandPhase.NA
        self.held = False
