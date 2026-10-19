import random
import pygame
import esper

from src.ecs.components import c_surface
from src.ecs.components import c_transform
from src.ecs.components import c_velocity
from src.ecs.components.c_enemy_spawner import CEnemySpawner
from src.ecs.components.c_input_command import CInputCommand
from src.ecs.components.tags.c_tag_enemy import CTagEnemy
from src.ecs.components.tags.c_tag_player import CTagPlayer
from src.ecs.components.tags.c_tag_bullet import CTagBullet


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
    enemy_entity = create_square(world, size, color, pygame.Vector2(pos), vel)
    world.add_component(enemy_entity, CTagEnemy())
    return enemy_entity


def create_player_square(world: esper.World, player_info: dict, player_lvl_info: dict) -> int:
    size = pygame.Vector2(player_info["size"]["x"], player_info["size"]["y"])
    color = pygame.Color(player_info["color"]["r"], player_info["color"]["g"], player_info["color"]["b"])
    # The spawn position is the center of the player
    pos = pygame.Vector2(player_lvl_info["position"]["x"] - size.x / 2,
                         player_lvl_info["position"]["y"] - size.y / 2)
    player_entity = create_square(world, size, color, pos, pygame.Vector2(0, 0))
    world.add_component(player_entity, CTagPlayer())
    return player_entity


def create_bullet(world: esper.World, player_pos: pygame.Vector2, player_size: pygame.Vector2,
                  mouse_pos: pygame.Vector2, bullet_info: dict) -> int:
    size = pygame.Vector2(bullet_info["size"]["x"], bullet_info["size"]["y"])
    color = pygame.Color(bullet_info["color"]["r"], bullet_info["color"]["g"], bullet_info["color"]["b"])
    player_center = player_pos + player_size / 2
    # The bullet leaves from the center of the player towards the mouse
    pos = player_center - size / 2
    direction = mouse_pos - player_center
    if direction.length_squared() == 0:
        direction = pygame.Vector2(1, 0)
    vel = direction.normalize() * bullet_info["velocity"]
    bullet_entity = create_square(world, size, color, pos, vel)
    world.add_component(bullet_entity, CTagBullet())
    return bullet_entity


def create_input_player(world: esper.World):
    input_commands = [
        ("PLAYER_LEFT", pygame.K_LEFT),
        ("PLAYER_RIGHT", pygame.K_RIGHT),
        ("PLAYER_UP", pygame.K_UP),
        ("PLAYER_DOWN", pygame.K_DOWN),
        ("PLAYER_FIRE", pygame.BUTTON_LEFT),
    ]
    for name, key in input_commands:
        input_entity = world.create_entity()
        world.add_component(input_entity, CInputCommand(name, key))


def create_enemy_spawner(world: esper.World, level_cfg: dict) -> int:
    spawner_entity = world.create_entity()
    world.add_component(spawner_entity, CEnemySpawner(level_cfg))
    return spawner_entity
