"""Datos de la partida que sobreviven entre escenas: puntaje, record, vidas y ronda."""
import json

from src.engine.service_locator import ServiceLocator


class GameSession:
    def __init__(self) -> None:
        self.score_cfg = ServiceLocator.configs_service.get("assets/cfg/score.json")
        self.hiscore = self._load_hiscore()
        self.new_hiscore = False
        self.reset()

    def reset(self) -> None:
        self.score = 0
        self.lives = ServiceLocator.configs_service.get("assets/cfg/player.json")["lives"]
        self.round = 1
        self.next_extra = self.score_cfg["extra_life_first"]
        self.new_hiscore = False

    def add_score(self, points: int) -> bool:
        """Suma puntos; devuelve True si se gano una vida extra."""
        self.score += points
        if self.score > self.hiscore:
            self.hiscore = self.score
            self.new_hiscore = True
        if self.score >= self.next_extra:
            self.next_extra += self.score_cfg["extra_life_every"]
            if self.lives < self.score_cfg["max_lives"]:
                self.lives += 1
                return True
        return False

    def _load_hiscore(self) -> int:
        try:
            with open(self.score_cfg["highscore_file"], encoding="utf-8") as f:
                return int(json.load(f)["hiscore"])
        except Exception:  # pylint: disable=broad-except
            return self.score_cfg["highscore_default"]

    def save_hiscore(self) -> None:
        try:
            with open(self.score_cfg["highscore_file"], "w", encoding="utf-8") as f:
                json.dump({"hiscore": self.hiscore}, f)
        except Exception:  # pylint: disable=broad-except
            pass  # en web el sistema de archivos puede no ser persistente
