import pygame
import esper
from src.ecs.components.c_transform import CTransform
from src.ecs.components.c_surface import CSurface
from src.ecs.components.tags.c_tag_player import CTagPlayer


def system_player_limits(world: esper.World, screen: pygame.Surface):
    """
    System that keeps the player inside the screen.
    """
    screen_rect = screen.get_rect()
    components = world.get_components(CTransform, CSurface, CTagPlayer)
    for _, (transform, surface, _) in components:
        player_rect = surface.get_area_relative(surface.area, transform.pos)
        if not screen_rect.contains(player_rect):
            player_rect.clamp_ip(screen_rect)
            transform.pos.xy = player_rect.topleft
