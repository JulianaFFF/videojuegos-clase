from src.scenes.menu_scenes import (CreditsScene, GameOverScene, InstructionsScene, IntroScene,
                                    MenuScene, VictoryScene)
from src.scenes.play_scene import PlayScene

SCENES = {
    "intro": IntroScene,
    "menu": MenuScene,
    "instructions": InstructionsScene,
    "credits": CreditsScene,
    "play": PlayScene,
    "game_over": GameOverScene,
    "victory": VictoryScene,
}
