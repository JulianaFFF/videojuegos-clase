import esper

from src.ecs.components.c_tags import CTagIntroSlide
from src.ecs.components.c_transform import CTransform


def system_intro_slide(world: esper.World, delta_time: float) -> bool:
    """Desliza los elementos de la intro. Devuelve True cuando todos llegaron."""
    done = True
    for _, (c_t, c_i) in world.get_components(CTransform, CTagIntroSlide):
        to = c_i.target - c_t.pos
        step = c_i.speed * delta_time
        if to.length() <= step:
            c_t.pos.update(c_i.target)
        else:
            c_t.pos += to.normalize() * step
            done = False
    return done
