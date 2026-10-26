import pygame
import esper
from src.ecs.components.c_transform import CTransform
from src.ecs.components.c_surface import CSurface
from src.ecs.components.tags.c_tag_bullet import CTagBullet


def system_bullet_limits(world: esper.World, screen: pygame.Surface):
    """
    System that deletes bullets that reach the screen edges.
    """
    screen_rect = screen.get_rect()
    components = world.get_components(CTransform, CSurface, CTagBullet)
    for bullet_entity, (transform, surface, _) in components:
        bullet_rect = surface.get_area_relative(surface.area, transform.pos)
        if not screen_rect.contains(bullet_rect):
            world.delete_entity(bullet_entity)
