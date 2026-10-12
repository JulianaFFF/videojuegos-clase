import esper
from src.ecs.components.c_enemy_spawner import CEnemySpawner
from src.create.prefab_creator import create_enemy_square


def system_enemy_spawner(world: esper.World, dt: float, enemies_cfg: dict):
    """
    System that creates enemies when the elapsed time reaches each spawn event time.
    """
    components = world.get_component(CEnemySpawner)
    for ent, spawner in components:
        spawner.current_time += dt
        for event in spawner.spawn_events:
            if not event.triggered and spawner.current_time >= event.time:
                create_enemy_square(world, event.position, enemies_cfg[event.enemy_type])
                event.triggered = True
