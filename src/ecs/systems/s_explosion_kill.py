import esper
from src.ecs.components.c_animation import CAnimation
from src.ecs.components.tags.c_tag_explosion import CTagExplosion


def system_explosion_kill(world: esper.World):
    """
    System that removes explosions once their animation has finished.
    """
    components = world.get_components(CAnimation, CTagExplosion)
    for ent, (c_a, _) in components:
        if c_a.finished:
            world.delete_entity(ent)
