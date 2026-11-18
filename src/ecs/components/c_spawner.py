class CSpawner:
    """Generador de enemigos dependiente del nivel y de la alerta."""
    def __init__(self, round_cfg: dict) -> None:
        self.types = round_cfg["enemy_types"]
        self.interval = round_cfg["spawn_interval"]
        self.timer = 3.0
        self.spy_time = round_cfg["spy_time"]
        self.spy_spawned = False
        self.formation = round_cfg["formation"]
        self.formation_timer = 18.0
        self.time = 0.0
