import pygame


class SpawnEventData:
    def __init__(self, time:float, enemy_type:str, position:pygame.Vector2) -> None:
        self.time = time
        self.enemy_type = enemy_type
        self.position = position
        self.triggered = False


class CEnemySpawner:
    def __init__(self, spawn_events:list) -> None:
        self.current_time = 0.0
        self.spawn_events:list[SpawnEventData] = []
        for event in spawn_events:
            self.spawn_events.append(
                SpawnEventData(time=event["time"],
                               enemy_type=event["enemy_type"],
                               position=pygame.Vector2(event["position"]["x"],
                                                       event["position"]["y"])))
