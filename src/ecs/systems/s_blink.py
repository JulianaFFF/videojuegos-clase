import esper

from src.ecs.components.c_surface import CSurface
from src.ecs.components.c_tags import CTagBlink


def system_blink(world: esper.World, delta_time: float) -> None:
    for _, (c_b, c_s) in world.get_components(CTagBlink, CSurface):
        c_b.time += delta_time
        c_s.visible = int(c_b.time / c_b.period) % 2 == 0
