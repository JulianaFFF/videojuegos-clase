import esper

from src.ecs.components.c_orientation import COrientation
from src.ecs.components.c_player import CPlayer
from src.ecs.components.c_surface import CSurface
from src.ecs.components.c_velocity import CVelocity
from src.engine.service_locator import ServiceLocator
from src.engine.world_math import angle_of, snap_angle


def system_orientation(world: esper.World) -> None:
    """Rota el sprite segun la direccion de movimiento (o el rumbo, para el jugador)."""
    images = ServiceLocator.images_service
    for ent, (c_o, c_v, c_s) in world.get_components(COrientation, CVelocity, CSurface):
        c_p = world.try_component(ent, CPlayer)
        vec = c_p.heading if c_p is not None else c_v.vel
        if vec.length_squared() == 0:
            continue
        ang = snap_angle(angle_of(vec), c_o.step)
        if ang != c_o.angle or c_s.surf is images.get_frame(c_o.sprite):
            c_o.angle = ang
            c_s.surf = images.get_rotated(c_o.sprite, ang)
