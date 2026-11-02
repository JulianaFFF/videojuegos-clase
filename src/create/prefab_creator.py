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
from src.ecs.components.tags.c_tag_shield_fx import CTagShieldFx
from src.ecs.components.tags.c_tag_ui import CTagUI
from src.ecs.components.c_camera_shake import CCameraShake
from src.ecs.components.c_shield import CShield, ShieldState
from src.ecs.components.c_shield_bar import CShieldBar
from src.ecs.components.c_shield_ring import CShieldRing
from src.ecs.components.c_shield_text import CShieldText
from src.engine.service_locator import ServiceLocator


def _load_image(info: dict) -> pygame.Surface:
    return ServiceLocator.images_service.get(info["image"], info.get("scale", 1))


def _color(info: dict) -> pygame.Color:
    return pygame.Color(info["r"], info["g"], info["b"])


def _number_frames(info: dict) -> int:
    return info["animations"]["number_frames"] if "animations" in info else 1


def _frame_size(info: dict) -> pygame.Vector2:
    surface = _load_image(info)
    return pygame.Vector2(surface.get_width() / _number_frames(info), surface.get_height())


def create_square(world: esper.World, size: pygame.Vector2, color: pygame.Color, pos: pygame.Vector2, vel: pygame.Vector2) -> int:
    cuad_entity = world.create_entity()
    world.add_component(cuad_entity, CSurface(size, color))
    world.add_component(cuad_entity, CTransform(pos))
    world.add_component(cuad_entity, CVelocity(vel))
    return cuad_entity


def create_sprite(world: esper.World, pos: pygame.Vector2, vel: pygame.Vector2, info: dict) -> int:
    """Creates an entity from a config with "image" and optional "animations"."""
    sprite_entity = world.create_entity()
    surface = _load_image(info)
    world.add_component(sprite_entity, CSurface.from_surface(surface, _number_frames(info)))
    world.add_component(sprite_entity, CTransform(pos))
    world.add_component(sprite_entity, CVelocity(vel))
    if "animations" in info:
        world.add_component(sprite_entity, CAnimation(info["animations"]))
    if "sound" in info:
        ServiceLocator.sounds_service.play(info["sound"])
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


def create_player_square(world: esper.World, player_info: dict, player_lvl_info: dict, shield_info: dict) -> int:
    size = _frame_size(player_info)
    # The spawn position is the center of the player
    pos = pygame.Vector2(player_lvl_info["position"]["x"] - size.x / 2, player_lvl_info["position"]["y"] - size.y / 2)
    player_entity = create_sprite(world, pos, pygame.Vector2(0, 0), player_info)
    world.add_component(player_entity, CTagPlayer())
    world.add_component(player_entity, CPlayerState(player_info["sound_move"]))
    world.add_component(player_entity, CShield(shield_info))
    return player_entity


def create_bullet(
    world: esper.World, player_pos: pygame.Vector2, player_size: pygame.Vector2, mouse_pos: pygame.Vector2, bullet_info: dict
) -> int:
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


def create_shield(world: esper.World, player_entity: int, shield_info: dict) -> None:
    """Activates the shield: sprite and ring around the player, sound and camera shake."""
    c_shield = world.component_for_entity(player_entity, CShield)
    c_shield.state = ShieldState.ACTIVE
    c_shield.time_left = c_shield.duration

    # Position is updated every frame by system_shield
    shield_entity = create_sprite(world, pygame.Vector2(0, 0), pygame.Vector2(0, 0), shield_info)
    world.add_component(shield_entity, CTagShieldFx())

    # 30% of margin so the overshoot of the ring animation is not clipped
    side = int(shield_info["radius"] * 2 * 1.3)
    ring_surface = pygame.Surface((side, side), pygame.SRCALPHA)
    ring_entity = world.create_entity()
    world.add_component(ring_entity, CSurface.from_surface(ring_surface))
    world.add_component(ring_entity, CTransform(pygame.Vector2(0, 0)))
    world.add_component(
        ring_entity, CShieldRing(shield_info["radius"], shield_info["ring_grow_time"], _color(shield_info["ring_color"]))
    )
    world.add_component(ring_entity, CTagShieldFx())

    for _, c_shake in world.get_component(CCameraShake):
        c_shake.start(shield_info["shake_activate"])


def create_text(world: esper.World, text_info: dict) -> int:
    font = ServiceLocator.fonts_service.get(text_info["font"], text_info["size"])
    c_surface = CSurface.from_text(text_info["text"], font, _color(text_info["color"]))
    pos = pygame.Vector2(text_info["position"]["x"], text_info["position"]["y"])
    if text_info.get("align") == "center":
        pos.x -= c_surface.area.width / 2
    text_entity = world.create_entity()
    world.add_component(text_entity, c_surface)
    world.add_component(text_entity, CTransform(pos))
    world.add_component(text_entity, CTagUI())
    return text_entity


def create_shield_hud(world: esper.World, interface_info: dict) -> None:
    create_text(world, interface_info["shield_label"])

    value_info = interface_info["shield_value"]
    value_entity = create_text(world, value_info)
    font = ServiceLocator.fonts_service.get(value_info["font"], value_info["size"])
    world.add_component(value_entity, CShieldText(font, value_info["text"]))

    bar_info = interface_info["shield_bar"]
    bar_entity = world.create_entity()
    world.add_component(
        bar_entity, CSurface(pygame.Vector2(bar_info["size"]["w"], bar_info["size"]["h"]), _color(bar_info["color_background"]))
    )
    world.add_component(bar_entity, CTransform(pygame.Vector2(bar_info["position"]["x"], bar_info["position"]["y"])))
    world.add_component(
        bar_entity,
        CShieldBar(
            _color(bar_info["color_background"]),
            _color(bar_info["color_ready"]),
            _color(bar_info["color_active"]),
            _color(bar_info["color_cooldown"]),
            _color(bar_info["color_flash"]),
        ),
    )
    world.add_component(bar_entity, CTagUI())


def create_camera(world: esper.World) -> CCameraShake:
    c_shake = CCameraShake()
    world.add_component(world.create_entity(), c_shake)
    return c_shake


def create_input_player(world: esper.World):
    input_commands = [
        ("PLAYER_LEFT", pygame.K_LEFT),
        ("PLAYER_RIGHT", pygame.K_RIGHT),
        ("PLAYER_UP", pygame.K_UP),
        ("PLAYER_DOWN", pygame.K_DOWN),
        ("PLAYER_FIRE", pygame.BUTTON_LEFT),
        ("PLAYER_SHIELD", pygame.K_SPACE),
        ("PAUSE", pygame.K_p),
    ]
    for name, key in input_commands:
        input_entity = world.create_entity()
        world.add_component(input_entity, CInputCommand(name, key))


def create_enemy_spawner(world: esper.World, level_cfg: dict) -> int:
    spawner_entity = world.create_entity()
    world.add_component(spawner_entity, CEnemySpawner(level_cfg))
    return spawner_entity
