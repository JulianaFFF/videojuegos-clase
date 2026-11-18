class COrientation:
    """El sprite gira segun la direccion de la velocidad, en pasos de 'step' grados."""
    def __init__(self, sprite: str, step: int = 45) -> None:
        self.sprite = sprite
        self.step = step
        self.angle = 0
