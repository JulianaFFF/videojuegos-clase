class CExplosion:
    """Explosion animada. Si es letal (minas) destruye lo que toque mientras dure."""
    def __init__(self, lethal: bool = False, radius: float = 0, delay: float = 0.0) -> None:
        self.lethal = lethal
        self.radius = radius
        self.delay = delay
