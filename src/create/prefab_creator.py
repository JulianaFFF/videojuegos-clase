import random

import esper
import pygame

from src.ecs.components.c_camera_shake import CCameraShake
from src.ecs.components.c_enemy_spawner import CEnemySpawner
from src.ecs.components.c_hunter_state import CHunterState
from src.ecs.components.c_input_command import CInputCommand
from src.ecs.components.c_player_state import CPlayerState
from src.ecs.components.c_shield import CShield
from src.ecs.components.c_surface import CSurface
from src.ecs.components.c_text import CText
from src.ecs.components.c_transform import CTransform
from src.ecs.components.c_velocity import CVelocity
from src.ecs.components.tags.c_tag_bullet import CTagBullet
from src.ecs.components.tags.c_tag_enemy import CTagEnemy
from src.ecs.components.tags.c_tag_explosion import CTagExplosion
from src.ecs.components.tags.c_tag_hud import CTagHUD
from src.ecs.components.tags.c_tag_hunter import CTagHunter
from src.ecs.components.tags.c_tag_pause_text import CTagPauseText
from src.ecs.components.tags.c_tag_player import CTagPlayer
from src.ecs.components.tags.c_tag_shield import CTagShield
from src.ecs.components.tags.c_tag_shield_bar import CTagShieldBar
from src.ecs.components.tags.c_tag_shield_text import CTagShieldText
from src.ecs.components.c_animation import CAnimation
from src.engine.service_locator import ServiceLocator


def create_square(world:esper.World, size:pygame.Vector2, pos:pygame.Vector2,
                  vel:pygame.Vector2, color:pygame.Color) -> int:
    cuad_entity = world.create_entity()
    world.add_component(cuad_entity, CSurface(size=size, color=color))
    world.add_component(cuad_entity, CTransform(pos=pos))
    world.add_component(cuad_entity, CVelocity(vel=vel))
    return cuad_entity

def create_sprite(world:esper.World, pos:pygame.Vector2, vel:pygame.Vector2, surface:pygame.Surface) -> int:
    sprite_entity = world.create_entity()
    world.add_component(sprite_entity, CTransform(pos=pos))
    world.add_component(sprite_entity, CVelocity(vel=vel))
    world.add_component(sprite_entity, CSurface.from_surface(surface))
    return sprite_entity


def create_enemy_square(world:esper.World, pos:pygame.Vector2, enemy_info:dict) -> int:
    if "animations" in enemy_info:
        return create_enemy_hunter(world, pos, enemy_info)
    enemy_surface = ServiceLocator.images_service.get(enemy_info["image"])
    speed = random.uniform(enemy_info["velocity_min"], enemy_info["velocity_max"])
    angle = random.uniform(0, 360)
    vel = pygame.Vector2(speed, 0).rotate(angle)
    enemy_entity = create_sprite(world, pygame.Vector2(pos), vel, enemy_surface)
    world.add_component(enemy_entity, CTagEnemy("Bouncer"))
    ServiceLocator.sounds_service.play(enemy_info["sound"])
    return enemy_entity


def create_enemy_hunter(world:esper.World, pos:pygame.Vector2, hunter_info:dict) -> int:
    hunter_surface = ServiceLocator.images_service.get(hunter_info["image"])
    vel = pygame.Vector2(0, 0)
    hunter_entity = create_sprite(world, pygame.Vector2(pos), vel, hunter_surface)
    world.add_component(hunter_entity, CTagEnemy("Hunter"))
    world.add_component(hunter_entity, CTagHunter(hunter_info))
    world.add_component(hunter_entity, CHunterState(pos))
    _add_animation(world, hunter_entity, hunter_info["animations"])
    return hunter_entity


def create_explosion(world:esper.World, center:tuple, explosion_info:dict) -> int:
    explosion_surface = ServiceLocator.images_service.get(explosion_info["image"])
    frame_w = explosion_surface.get_width() / explosion_info["animations"]["number_frames"]
    pos = pygame.Vector2(center[0] - (frame_w / 2),
                         center[1] - (explosion_surface.get_height() / 2))
    vel = pygame.Vector2(0, 0)
    explosion_entity = create_sprite(world, pos, vel, explosion_surface)
    world.add_component(explosion_entity, CTagExplosion())
    _add_animation(world, explosion_entity, explosion_info["animations"])
    ServiceLocator.sounds_service.play(explosion_info["sound"])
    return explosion_entity


def _add_animation(world:esper.World, entity:int, animations_info:dict) -> None:
    c_a = CAnimation(animations_info)
    c_s = world.component_for_entity(entity, CSurface)
    # El area de dibujo y colision es un solo cuadro del sprite
    c_s.area.w = c_s.surf.get_width() / c_a.number_frames
    c_s.area.x = c_s.area.w * c_a.curr_frame
    world.add_component(entity, c_a)


def create_player_square(world:esper.World, player_info:dict, player_lvl_info:dict, shield_info:dict) -> int:
    player_sprite = ServiceLocator.images_service.get(player_info["image"])
    size = player_sprite.get_size()
    size = (size[0] / player_info["animations"]["number_frames"], size[1])
    pos = pygame.Vector2(player_lvl_info["position"]["x"] - (size[0] / 2), 
                         player_lvl_info["position"]["y"] - (size[1] / 2))
    vel = pygame.Vector2(0, 0)
    player_entity = create_sprite(world, pos, vel, player_sprite)
    world.add_component(player_entity, CTagPlayer())
    _add_animation(world, player_entity, player_info["animations"])
    world.add_component(player_entity, CPlayerState())
    world.add_component(player_entity, CShield(shield_info))
    return player_entity


def create_enemy_spawner(world:esper.World, level_data:dict) -> int:
    spawner_entity = world.create_entity()
    world.add_component(spawner_entity,
                        CEnemySpawner(level_data["enemy_spawn_events"]))
    return spawner_entity

def create_input_player(world:esper.World):
    input_left = world.create_entity()
    input_right = world.create_entity()
    input_up = world.create_entity()
    input_down = world.create_entity()
    
    world.add_component(input_left, CInputCommand("PLAYER_LEFT", pygame.K_LEFT))
    world.add_component(input_right, CInputCommand("PLAYER_RIGHT", pygame.K_RIGHT))
    world.add_component(input_up, CInputCommand("PLAYER_UP", pygame.K_UP))
    world.add_component(input_down, CInputCommand("PLAYER_DOWN", pygame.K_DOWN))

    input_fire = world.create_entity()
    world.add_component(input_fire, CInputCommand("PLAYER_FIRE", pygame.BUTTON_LEFT))

    input_special = world.create_entity()
    world.add_component(input_special, CInputCommand("PLAYER_SHIELD", pygame.K_SPACE))

    input_pause = world.create_entity()
    world.add_component(input_pause, CInputCommand("PAUSE", pygame.K_p))


def create_bullet_square(world:esper.World, player_pos:pygame.Vector2, player_size:pygame.Vector2,
                         mouse_pos:pygame.Vector2, bullet_info:dict):
    bullet_surface = ServiceLocator.images_service.get(bullet_info["image"])
    bullet_size = bullet_surface.get_rect().size
    player_center = pygame.Vector2(player_pos.x + (player_size[0] / 2),
                                   player_pos.y + (player_size[1] / 2))
    vel = (mouse_pos - player_center)
    if vel.length_squared() == 0:
        return -1
    vel = vel.normalize() * bullet_info["velocity"]
    pos = pygame.Vector2(player_pos.x + (player_size[0] / 2) - (bullet_size[0] / 2),
                         player_pos.y + (player_size[1] / 2) - (bullet_size[1] / 2))
    bullet_entity = create_sprite(world, pos, vel, bullet_surface)
    world.add_component(bullet_entity, CTagBullet())
    ServiceLocator.sounds_service.play(bullet_info["sound"])
    return bullet_entity


def _color(color_info:dict) -> pygame.Color:
    return pygame.Color(color_info["r"], color_info["g"], color_info["b"])


def create_text(world:esper.World, font_path:str, text_info:dict) -> int:
    font = ServiceLocator.fonts_service.get(font_path, text_info["size"])
    color = _color(text_info["color"])
    anchor_pos = (text_info["position"]["x"], text_info["position"]["y"])
    c_s = CSurface.from_text(text_info.get("text", ""), font, color)
    rect = c_s.surf.get_rect(**{text_info["anchor"]: anchor_pos})
    text_entity = world.create_entity()
    world.add_component(text_entity, CTransform(pygame.Vector2(rect.topleft)))
    world.add_component(text_entity, c_s)
    world.add_component(text_entity, CText(font, color, text_info["anchor"], anchor_pos))
    world.add_component(text_entity, CTagHUD())
    return text_entity


def create_interface(world:esper.World, interface_info:dict) -> None:
    font_path = interface_info["font"]
    create_text(world, font_path, interface_info["title"])
    create_text(world, font_path, interface_info["instructions"])
    create_text(world, font_path, interface_info["shield_label"])

    bar_info = interface_info["shield_bar"]
    bar_entity = world.create_entity()
    world.add_component(bar_entity, CTransform(pygame.Vector2(bar_info["position"]["x"],
                                                              bar_info["position"]["y"])))
    world.add_component(bar_entity, CSurface(pygame.Vector2(bar_info["size"]["x"], bar_info["size"]["y"]),
                                             _color(bar_info["color_bg"])))
    world.add_component(bar_entity, CTagHUD())
    world.add_component(bar_entity, CTagShieldBar())

    status_entity = create_text(world, font_path, interface_info["shield_status"])
    world.add_component(status_entity, CTagShieldText())


def create_pause_texts(world:esper.World, interface_info:dict, screen_size:tuple) -> None:
    overlay_info = interface_info["pause_overlay"]
    overlay = pygame.Surface(screen_size, pygame.SRCALPHA)
    overlay.fill((*_color(overlay_info["color"])[:3], overlay_info["alpha"]))
    overlay_entity = world.create_entity()
    world.add_component(overlay_entity, CTransform(pygame.Vector2(0, 0)))
    world.add_component(overlay_entity, CSurface.from_surface(overlay))
    world.add_component(overlay_entity, CTagHUD())
    world.add_component(overlay_entity, CTagPauseText())

    for key in ("pause", "pause_hint"):
        text_entity = create_text(world, interface_info["font"], interface_info[key])
        world.add_component(text_entity, CTagPauseText())


def create_camera(world:esper.World) -> int:
    camera_entity = world.create_entity()
    world.add_component(camera_entity, CCameraShake())
    return camera_entity


def create_shield(world:esper.World, player_entity:int, shield_info:dict) -> int:
    c_sh = world.component_for_entity(player_entity, CShield)
    if not c_sh.is_ready:
        return -1
    pl_t = world.component_for_entity(player_entity, CTransform)
    pl_s = world.component_for_entity(player_entity, CSurface)
    player_center = CSurface.get_area_relative(pl_s.area, pl_t.pos).center

    # El sprite del escudo se escala para coincidir con su radio de accion
    number_frames = shield_info["animations"]["number_frames"]
    diameter = c_sh.radius * 2
    shield_surface = ServiceLocator.images_service.get_scaled(shield_info["image"],
                                                              (diameter * number_frames, diameter)).copy()
    # Se aclara el sprite para que el escudo brille sobre el fondo oscuro
    shield_surface.fill((90, 110, 140), special_flags=pygame.BLEND_RGB_ADD)
    pos = pygame.Vector2(player_center[0] - c_sh.radius, player_center[1] - c_sh.radius)
    shield_entity = create_sprite(world, pos, pygame.Vector2(0, 0), shield_surface)
    world.add_component(shield_entity, CTagShield())
    _add_animation(world, shield_entity, shield_info["animations"])

    c_sh.time_active = c_sh.duration
    c_sh.time_cooldown = c_sh.cooldown
    c_sh.shield_entity = shield_entity

    for _, c_shake in world.get_component(CCameraShake):
        c_shake.shake(shield_info["screen_shake"]["intensity"], shield_info["screen_shake"]["duration"])
    ServiceLocator.sounds_service.play(shield_info["sound_activate"])
    return shield_entity
