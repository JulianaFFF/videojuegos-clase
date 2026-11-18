class CObstacle:
    """kind: 'rock' (destructible), 'hard_rock' (indestructible) o 'mine' (explota)."""
    def __init__(self, kind: str, points: int = 0) -> None:
        self.kind = kind
        self.points = points
