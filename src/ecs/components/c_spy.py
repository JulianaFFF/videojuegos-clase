class CSpy:
    """Espia: si no se destruye antes de escape_time escapa y provoca ALERTA ROJA."""
    def __init__(self, escape_time: float) -> None:
        self.escape_time = escape_time
        self.time = 0.0
