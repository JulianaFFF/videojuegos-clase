import random
import pygame
import esper

from src.ecs.components.c_surface import CSurface
from src.ecs.components.c_transform import CTransform
from src.ecs.components.c_velocity import CVelocity
from src.ecs.components.c_animation import CAnimation
from src.ecs.components.c_enemy_spawner import CEnemySpawner
from src.ecs.components.c_enemy_hunter_state import CEnemyHunterState
from src.ecs.components.c_player_state import CPlayerState
from src.ecs.components.c_input_command import CInputCommand
from src.ecs.components.tags.c_tag_enemy import CTagEnemy
from src.ecs.components.tags.c_tag_hunter import CTagHunter
from src.ecs.components.tags.c_tag_player import CTagPlayer
from src.ecs.components.tags.c_tag_bullet import CTagBullet
from src.ecs.components.tags.c_tag_explosion import CTagExplosion

_images_cache: dict[str, pygame.Surface] = {}


def _load_image(path: str) -> pygame.Surface:
    """Loads an image only once and reuses it for every entity that needs it."""
    if path not in _images_cache:
        _images_cache[path] = pygame.image.load(path).convert_alpha()
    return _images_cache[path]


def _number_frames(info: dict) -> int:
    return info["animations"]["number_frames"] if "animations" in info else 1


def _frame_size(info: dict) -> pygame.Vector2:
    surface = _load_image(info["image"])
    return pygame.Vector2(surface.get_width() / _number_frames(info), surface.get_height())


def create_square(world: esper.World, size: pygame.Vector2, color: pygame.Color,
                  pos: pygame.Vector2, vel: pygame.Vector2) -> int:
    cuad_entity = world.create_entity()
    world.add_component(cuad_entity, CSurface(size, color))
    world.add_component(cuad_entity, CTransform(pos))
    world.add_component(cuad_entity, CVelocity(vel))
    return cuad_entity


def create_sprite(world: esper.World, pos: pygame.Vector2, vel: pygame.Vector2,
                  info: dict) -> int:
    """Creates an entity from a config with "image" and optional "animations"."""
    sprite_entity = world.create_entity()
    surface = _load_image(info["image"])
    world.add_component(sprite_entity, CSurface.from_surface(surface, _number_frames(info)))
    world.add_component(sprite_entity, CTransform(pos))
    world.add_component(sprite_entity, CVelocity(vel))
    if "animations" in info:
        world.add_component(sprite_entity, CAnimation(info["animations"]))
    return sprite_entity


def create_enemy_square(world: esper.World, pos: pygame.Vector2, enemy_info: dict) -> int:
    if "velocity_chase" in enemy_info:
        return create_enemy_hunter(world, pos, enemy_info)
    speed = random.uniform(enemy_info["velocity_min"], enemy_info["velocity_max"])
    vel = pygame.Vector2(speed, 0).rotate(random.uniform(0, 360))  # Random direction
    enemy_entity = create_sprite(world, pygame.Vector2(pos), vel, enemy_info)
    world.add_component(enemy_entity, CTagEnemy())
    return enemy_entity


def create_enemy_hunter(world: esper.World, pos: pygame.Vector2, enemy_info: dict) -> int:
    enemy_entity = create_sprite(world, pygame.Vector2(pos), pygame.Vector2(0, 0), enemy_info)
    world.add_component(enemy_entity, CEnemyHunterState(pos, enemy_info))
    world.add_component(enemy_entity, CTagEnemy())
    world.add_component(enemy_entity, CTagHunter())
    return enemy_entity


def create_player_square(world: esper.World, player_info: dict, player_lvl_info: dict) -> int:
    size = _frame_size(player_info)
    # The spawn position is the center of the player
    pos = pygame.Vector2(player_lvl_info["position"]["x"] - size.x / 2,
                         player_lvl_info["position"]["y"] - size.y / 2)
    player_entity = create_sprite(world, pos, pygame.Vector2(0, 0), player_info)
    world.add_component(player_entity, CTagPlayer())
    world.add_component(player_entity, CPlayerState())
    return player_entity


def create_bullet(world: esper.World, player_pos: pygame.Vector2, player_size: pygame.Vector2,
                  mouse_pos: pygame.Vector2, bullet_info: dict) -> int:
    size = _frame_size(bullet_info)
    player_center = player_pos + player_size / 2
    # The bullet leaves from the center of the player towards the mouse
    pos = player_center - size / 2
    direction = mouse_pos - player_center
    if direction.length_squared() == 0:
        direction = pygame.Vector2(1, 0)
    vel = direction.normalize() * bullet_info["velocity"]
    bullet_entity = create_sprite(world, pos, vel, bullet_info)
    world.add_component(bullet_entity, CTagBullet())
    return bullet_entity


def create_explosion(world: esper.World, center: pygame.Vector2, explosion_info: dict) -> int:
    size = _frame_size(explosion_info)
    pos = pygame.Vector2(center) - size / 2
    explosion_entity = create_sprite(world, pos, pygame.Vector2(0, 0), explosion_info)
    world.add_component(explosion_entity, CTagExplosion())
    return explosion_entity


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
