import esper

from src.ecs.components.c_animation import CAnimation
from src.ecs.components.tags.c_tag_explosion import CTagExplosion

def system_explosion_kill(world:esper.World, delta_time:float):
    components = world.get_components(CAnimation, CTagExplosion)

    for explosion_entity, (c_a, _) in components:
        anim = c_a.animations_list[c_a.curr_anim]
        # El ultimo cuadro termina en este update: la explosion desaparece
        if c_a.curr_frame >= anim.end and c_a.curr_anim_time <= delta_time:
            world.delete_entity(explosion_entity)
