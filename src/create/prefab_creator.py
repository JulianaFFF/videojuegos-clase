import random
import pygame
import esper

from src.ecs.components import c_surface
from src.ecs.components import c_transform
from src.ecs.components import c_velocity
from src.ecs.components.c_enemy_spawner import CEnemySpawner


def create_square(world: esper.World, size: pygame.Vector2, color: pygame.Color,
                  pos: pygame.Vector2, vel: pygame.Vector2) -> int:
    cuad_entity = world.create_entity()
    world.add_component(cuad_entity, c_surface.CSurface(size, color))
    world.add_component(cuad_entity, c_transform.CTransform(pos))
    world.add_component(cuad_entity, c_velocity.CVelocity(vel))
    return cuad_entity


def create_enemy_square(world: esper.World, pos: pygame.Vector2, enemy_info: dict) -> int:
    size = pygame.Vector2(enemy_info["size"]["x"], enemy_info["size"]["y"])
    color = pygame.Color(enemy_info["color"]["r"], enemy_info["color"]["g"], enemy_info["color"]["b"])
    speed = random.uniform(enemy_info["velocity_min"], enemy_info["velocity_max"])
    vel = pygame.Vector2(speed, 0).rotate(random.uniform(0, 360))  # Random direction
    return create_square(world, size, color, pygame.Vector2(pos), vel)


def create_enemy_spawner(world: esper.World, level_cfg: dict) -> int:
    spawner_entity = world.create_entity()
    world.add_component(spawner_entity, CEnemySpawner(level_cfg))
    return spawner_entity
