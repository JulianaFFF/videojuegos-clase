import esper
import pygame
import src.ecs.components.c_transform as c_transform
import src.ecs.components.c_surface as c_surface

def system_rendering(world: esper.World, screen: pygame.Surface):
    """
    System that renders all entities with a CTransform and CSurface component.
    Only the current area (sprite frame) of the surface is drawn.
    """
    componentes = world.get_components(c_transform.CTransform, c_surface.CSurface)
    for ent, (transform, surface) in componentes:
        screen.blit(surface.surf, transform.pos, area=surface.area)
