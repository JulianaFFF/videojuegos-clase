import esper

from src.ecs.components.c_animation import CAnimation
from src.ecs.components.c_explosion import CExplosion
from src.ecs.components.c_surface import CSurface


def system_explosion(world: esper.World, delta_time: float) -> None:
    """Gestiona el retardo de las explosiones en cadena y elimina las terminadas."""
    for ent, (c_e, c_a, c_s) in world.get_components(CExplosion, CAnimation, CSurface):
        if c_e.delay > 0:
            c_e.delay -= delta_time
            if c_e.delay <= 0:
                c_s.visible = True
            continue
        if c_a.finished:
            world.delete_entity(ent)
