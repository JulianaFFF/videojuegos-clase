class CBase:
    """Base enemiga: 6 torres + nucleo. Se destruye al perder sus torres o al impactar el nucleo."""
    def __init__(self, layout: str) -> None:
        self.layout = layout
        self.turrets = []
        self.core = None
        self.alive = True
