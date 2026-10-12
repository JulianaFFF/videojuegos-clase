import pygame
import esper
import src.ecs.components.c_transform as c_transform
import src.ecs.components.c_velocity as c_velocity
import src.ecs.components.c_surface as c_surface


def system_screen_bounce(world: esper.World, screen: pygame.Surface):
    """
    System that makes all entities with a CTransform and CVelocity component bounce off the screen edges.
    """
    screen_rect = screen.get_rect()
    components = world.get_components(c_transform.CTransform, c_velocity.CVelocity, c_surface.CSurface)
    
    for ent, (transform, velocity, surface) in components:
        cuad_rect = surface.surf.get_rect(topleft=transform.pos)
        if cuad_rect.left <= 0 or cuad_rect.right >= screen_rect.width:
            velocity.vel.x *= -1  # Reverse horizontal velocity
            cuad_rect.clamp_ip(screen_rect)  # Keep the rectangle within the screen bounds
            transform.pos.x = cuad_rect.x  # Update position after clamping
        if cuad_rect.top <= 0 or cuad_rect.bottom >= screen_rect.height:
            velocity.vel.y *= -1  # Reverse vertical velocity
            cuad_rect.clamp_ip(screen_rect)  # Keep the rectangle within the screen bounds
            transform.pos.y = cuad_rect.y  # Update position after clamping