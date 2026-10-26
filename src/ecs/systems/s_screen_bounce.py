import pygame
import esper
import src.ecs.components.c_transform as c_transform
import src.ecs.components.c_velocity as c_velocity
import src.ecs.components.c_surface as c_surface
from src.ecs.components.tags.c_tag_enemy import CTagEnemy
from src.ecs.components.tags.c_tag_hunter import CTagHunter


def system_screen_bounce(world: esper.World, screen: pygame.Surface):
    """
    System that makes enemies bounce off the screen edges.
    The velocity is forced to point back inside the screen (instead of just being inverted),
    so an entity resting on the edge does not flip direction every frame and get stuck.
    """
    screen_rect = screen.get_rect()
    components = world.get_components(c_transform.CTransform, c_velocity.CVelocity, c_surface.CSurface, CTagEnemy)

    for ent, (transform, velocity, surface, _) in components:
        if world.has_component(ent, CTagHunter):
            continue  # Hunters are moved by their own state system
        cuad_rect = surface.get_area_relative(surface.area, transform.pos)
        if cuad_rect.left <= 0:
            velocity.vel.x = abs(velocity.vel.x)  # Move right
        elif cuad_rect.right >= screen_rect.width:
            velocity.vel.x = -abs(velocity.vel.x)  # Move left
        if cuad_rect.top <= 0:
            velocity.vel.y = abs(velocity.vel.y)  # Move down
        elif cuad_rect.bottom >= screen_rect.height:
            velocity.vel.y = -abs(velocity.vel.y)  # Move up
        if not screen_rect.contains(cuad_rect):
            cuad_rect.clamp_ip(screen_rect)  # Keep the rectangle within the screen bounds
            transform.pos.xy = cuad_rect.topleft
