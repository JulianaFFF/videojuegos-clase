import esper

from src.ecs.components.c_tags import CTagUI
from src.ecs.components.c_transform import CTransform
from src.engine.world_math import wrap_pos


def system_wraparound(world: esper.World, world_w: int, world_h: int) -> None:
    """Toda entidad del mundo que sale por un borde aparece por el opuesto."""
    for ent, c_t in world.get_component(CTransform):
        if not world.has_component(ent, CTagUI):
            wrap_pos(c_t.pos, world_w, world_h)
