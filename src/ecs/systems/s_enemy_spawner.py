import esper

from src.ecs.components.c_enemy_spawner import CEnemySpawner
from src.create.prefab_creator import create_enemy_square


def system_enemy_spawner(world:esper.World, enemies:dict, delta_time:float):
    components = world.get_component(CEnemySpawner)

    c_spw:CEnemySpawner
    for _, c_spw in components:
        c_spw.current_time += delta_time
        for spw_evt in c_spw.spawn_events:
            if not spw_evt.triggered and c_spw.current_time >= spw_evt.time:
                create_enemy_square(world, spw_evt.position,
                                    enemies[spw_evt.enemy_type])
                spw_evt.triggered = True
