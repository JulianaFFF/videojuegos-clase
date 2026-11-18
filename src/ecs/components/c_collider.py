class CCollider:
    """Hitbox circular (radio en pixeles), independiente del tamano del sprite."""
    def __init__(self, radius: float) -> None:
        self.radius = radius
