import pygame
import esper
import src.ecs.components.c_transform as c_transform
import src.ecs.components.c_velocity as c_velocity

def system_movement(world: esper.World, dt: float):
    """
    System that updates the position of all entities with a CTransform and CVelocity component.
    """
    components = world.get_components(c_transform.CTransform, c_velocity.CVelocity)
    for ent, (transform, velocity) in components:
        transform.pos.x += velocity.vel.x * dt
        transform.pos.y += velocity.vel.y * dt  
        