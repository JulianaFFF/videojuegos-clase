from enum import Enum


class EnemyState(Enum):
    WANDER = 0
    CHASE = 1
    ATTACK = 2
    FLEE = 3


class CEnemy:
    """Enemigo con IA basada en el patron State + steering behaviours."""
    def __init__(self, kind: str, cfg: dict) -> None:
        self.kind = kind
        self.speed = cfg["speed"]
        self.turn = cfg["turn"]
        self.points = cfg["points"]
        self.sight = cfg.get("sight", 150)
        self.wander_time = cfg.get("wander_time", 1.0)
        self.life_time = cfg.get("life_time", -1)
        self.state = EnemyState.WANDER
        self.state_time = 0.0
        self.wander_dir = None
        self.leader = None          # entidad lider si pertenece a una formacion
        self.offset = None          # desplazamiento respecto al lider
