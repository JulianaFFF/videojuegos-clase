import esper
import pygame
import src.ecs.components.c_transform as c_transform
import src.ecs.components.c_surface as c_surface
from src.ecs.components.tags.c_tag_ui import CTagUI


def system_rendering(world: esper.World, screen: pygame.Surface, camera_offset: pygame.Vector2):
    """
    System that renders all entities with a CTransform and CSurface component.
    Only the current area (sprite frame) of the surface is drawn.
    The interface is drawn last, on top of the game and unaffected by the camera.
    """
    componentes = world.get_components(c_transform.CTransform, c_surface.CSurface)
    for ent, (transform, surface) in componentes:
        if surface.visible and not world.has_component(ent, CTagUI):
            screen.blit(surface.surf, transform.pos + camera_offset, area=surface.area)

    interfaz = world.get_components(c_transform.CTransform, c_surface.CSurface, CTagUI)
    for _, (transform, surface, _) in interfaz:
        screen.blit(surface.surf, transform.pos, area=surface.area)
