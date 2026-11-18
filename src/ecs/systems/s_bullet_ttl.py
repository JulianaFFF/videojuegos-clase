import esper

from src.ecs.components.c_bullet import CBullet


def system_bullet_ttl(world: esper.World, delta_time: float) -> None:
    for ent, c_b in world.get_component(CBullet):
        c_b.ttl -= delta_time
        if c_b.ttl <= 0:
            world.delete_entity(ent)
