"""Fabricas (prefabs) de entidades. Todas las entidades del juego se crean aqui."""
import random

import esper
import pygame

from src.ecs.components.c_alert import CAlert
from src.ecs.components.c_animation import CAnimation
from src.ecs.components.c_base import CBase
from src.ecs.components.c_bullet import CBullet
from src.ecs.components.c_camera import CCamera
from src.ecs.components.c_collider import CCollider
from src.ecs.components.c_core import CCore
from src.ecs.components.c_enemy import CEnemy
from src.ecs.components.c_explosion import CExplosion
from src.ecs.components.c_input_command import CInputCommand
from src.ecs.components.c_obstacle import CObstacle
from src.ecs.components.c_orientation import COrientation
from src.ecs.components.c_player import CPlayer
from src.ecs.components.c_spawner import CSpawner
from src.ecs.components.c_spy import CSpy
from src.ecs.components.c_star import CStar
from src.ecs.components.c_surface import CSurface
from src.ecs.components.c_tags import CTagBlink, CTagUI
from src.ecs.components.c_transform import CTransform
from src.ecs.components.c_turret import CTurret
from src.ecs.components.c_velocity import CVelocity
from src.engine.service_locator import ServiceLocator
from src.engine.world_math import angle_of, snap_angle

CFG = "assets/cfg/"


def cfg(name: str) -> dict:
    return ServiceLocator.configs_service.get(CFG + name + ".json")


# ---------------------------------------------------------------- input
def create_input_commands(world: esper.World) -> None:
    input_cfg = cfg("input")
    for name, key_names in input_cfg["keys"].items():
        keys = [getattr(pygame, k) for k in key_names]
        buttons = input_cfg["joy_buttons"].get(name, [])
        world.create_entity(CInputCommand(name, keys, buttons))


# ---------------------------------------------------------------- UI
def create_text(world: esper.World, text: str, pos, color="white", size: int = 8,
                align: str = "center", blink: float = 0.0) -> int:
    ui = cfg("interface")
    font = ServiceLocator.fonts_service.get(ui["font"], size)
    col = ui["colors"].get(color, color) if isinstance(color, str) else color
    c_s = CSurface.from_text(text, font, col)
    pos = pygame.Vector2(pos)
    if align == "left":
        pos.x += c_s.surf.get_width() / 2
    elif align == "right":
        pos.x -= c_s.surf.get_width() / 2
    ent = world.create_entity(CTransform(pos), c_s, CTagUI())
    if blink > 0:
        world.add_component(ent, CTagBlink(blink))
    return ent


def create_image_ui(world: esper.World, surf: pygame.Surface, pos) -> int:
    return world.create_entity(CTransform(pygame.Vector2(pos)), CSurface(surf, layer=9), CTagUI())


# ---------------------------------------------------------------- fondo
def create_starfield(world: esper.World, area_w: int, area_h: int) -> None:
    stars = cfg("world")["stars"]
    for _ in range(stars["number"]):
        world.create_entity(CStar(
            (random.uniform(0, area_w), random.uniform(0, area_h)),
            random.choice(stars["colors"]),
            random.choice(stars["layers"]),
            random.uniform(stars["blink_speed"]["min"], stars["blink_speed"]["max"]),
            random.uniform(0, 1)))


def create_camera(world: esper.World, pos, view_w: int, view_h: int) -> int:
    return world.create_entity(CCamera(pos, view_w, view_h))


# ---------------------------------------------------------------- jugador
def create_player(world: esper.World, pos, special_charges: int) -> int:
    p_cfg = cfg("player")
    surf = ServiceLocator.images_service.get_frame("player")
    return world.create_entity(
        CTransform(pygame.Vector2(pos)), CVelocity(pygame.Vector2(0, 0)),
        CSurface(surf, layer=5), CCollider(p_cfg["hitbox_radius"]),
        COrientation("player", 45), CPlayer(p_cfg, special_charges))


def create_player_bullet(world: esper.World, pos, direction: pygame.Vector2,
                         ship_vel: pygame.Vector2) -> int:
    b_cfg = cfg("player")["bullet"]
    ang = snap_angle(angle_of(direction), 15)
    surf = ServiceLocator.images_service.get_rotated("bullet_v", ang)
    vel = direction.normalize() * b_cfg["speed"] + ship_vel
    return world.create_entity(
        CTransform(pygame.Vector2(pos) + direction.normalize() * 8), CVelocity(vel),
        CSurface(surf, layer=4), CCollider(b_cfg["radius"]), CBullet(True, b_cfg["ttl"]))


_ENEMY_BULLET = None


def create_enemy_bullet(world: esper.World, pos, vel: pygame.Vector2, ttl: float) -> int:
    global _ENEMY_BULLET  # pylint: disable=global-statement
    if _ENEMY_BULLET is None:
        _ENEMY_BULLET = pygame.Surface((4, 4), pygame.SRCALPHA)
        pygame.draw.rect(_ENEMY_BULLET, (255, 140, 0), (0, 0, 4, 4))
        pygame.draw.rect(_ENEMY_BULLET, (255, 255, 160), (1, 1, 2, 2))
    return world.create_entity(
        CTransform(pygame.Vector2(pos)), CVelocity(vel), CSurface(_ENEMY_BULLET, layer=4),
        CCollider(2), CBullet(False, ttl))


# ---------------------------------------------------------------- enemigos
def create_enemy(world: esper.World, kind: str, pos) -> int:
    e_cfg = cfg("enemies")[kind]
    surf = ServiceLocator.images_service.get_frame(e_cfg["sprite"])
    vel = pygame.Vector2(1, 0).rotate(random.uniform(0, 360)) * e_cfg["speed"]
    return world.create_entity(
        CTransform(pygame.Vector2(pos)), CVelocity(vel), CSurface(surf, layer=3),
        CCollider(e_cfg["radius"]), COrientation(e_cfg["sprite"], 45), CEnemy(kind, e_cfg))


def create_formation(world: esper.World, pos) -> list:
    """Formacion: un lider P y cuatro escoltas I que mantienen su posicion relativa."""
    leader = create_enemy(world, "P", pos)
    ents = [leader]
    for off in [(-14, 12), (14, 12), (-28, 24), (28, 24)]:
        ent = create_enemy(world, "I", pygame.Vector2(pos) + pygame.Vector2(off))
        c_e = world.component_for_entity(ent, CEnemy)
        c_e.leader = leader
        c_e.offset = pygame.Vector2(off)
        ents.append(ent)
    return ents


def create_spy(world: esper.World, pos) -> int:
    s_cfg = cfg("enemies")["SPY"]
    surf = ServiceLocator.images_service.get_frame(s_cfg["sprite"])
    vel = pygame.Vector2(1, 0).rotate(random.uniform(0, 360)) * s_cfg["speed"]
    return world.create_entity(
        CTransform(pygame.Vector2(pos)), CVelocity(vel), CSurface(surf, layer=3),
        CCollider(s_cfg["radius"]), COrientation(s_cfg["sprite"], 45), CSpy(s_cfg["escape_time"]))


# ---------------------------------------------------------------- bases
def create_base(world: esper.World, pos, layout: str, round_cfg: dict) -> int:
    images = ServiceLocator.images_service
    spr = cfg("sprites")["base"]
    b_cfg = cfg("bases")
    bg = images.get_base(layout)
    center = pygame.Vector2(pos)
    base_ent = world.create_entity(CTransform(center), CSurface(bg, layer=1), CBase(layout))
    c_base = world.component_for_entity(base_ent, CBase)
    img_c = pygame.Vector2(spr["rect"][2] / 2, spr["rect"][3] / 2)

    def local(x, y, size):
        off = pygame.Vector2(x + size / 2, y + size / 2) - img_c
        if layout == "v":
            off = pygame.Vector2(-off.y, off.x)
        return center + off

    cooldown = b_cfg["turret"]["cooldown"] * round_cfg["turret_cooldown_mult"]
    for sx, sy in spr["turret_slots"]:
        t_ent = world.create_entity(
            CTransform(local(sx, sy, 16)), CSurface(images.get_frame("turret"), layer=2),
            CCollider(b_cfg["turret"]["radius"]),
            CTurret(base_ent, random.uniform(0.5, cooldown)))
        world.component_for_entity(t_ent, CTurret).cooldown = cooldown
        c_base.turrets.append(t_ent)
    cx, cy = spr["core_slot"]
    c_base.core = world.create_entity(
        CTransform(local(cx, cy, 20)), CSurface(images.get_frame("core", 0), layer=2),
        CCollider(b_cfg["core"]["radius"]),
        CCore(base_ent, round_cfg["core_animated"], round_cfg["spawn_e"]))
    return base_ent


# ---------------------------------------------------------------- obstaculos
def create_obstacle(world: esper.World, kind: str, pos) -> int:
    o_cfg = cfg("obstacles")[kind]
    images = ServiceLocator.images_service
    if kind == "mine":
        frames = images.get_frames("mine")
        return world.create_entity(
            CTransform(pygame.Vector2(pos)), CSurface(frames[0], layer=2),
            CAnimation(frames, o_cfg["anim_fps"]), CCollider(o_cfg["radius"]),
            CObstacle(kind, o_cfg["points"]))
    surf = random.choice(images.get_frames(kind))
    return world.create_entity(
        CTransform(pygame.Vector2(pos)), CSurface(surf, layer=2), CCollider(o_cfg["radius"]),
        CObstacle(kind, o_cfg.get("points", 0)))


def create_explosion(world: esper.World, pos, mine: bool = False, delay: float = 0.0) -> int:
    images = ServiceLocator.images_service
    frames = images.get_frames("explosion_mine" if mine else "explosion")
    radius = cfg("obstacles")["mine"]["blast_radius"] if mine else 0
    fps = len(frames) / (cfg("obstacles")["mine"]["blast_time"] if mine else 0.4)
    c_s = CSurface(frames[0], visible=delay <= 0, layer=6)
    ent = world.create_entity(CTransform(pygame.Vector2(pos)), c_s,
                              CAnimation(frames, fps, loop=False), CExplosion(mine, radius, delay))
    if mine:
        world.add_component(ent, CCollider(radius))
    return ent


# ---------------------------------------------------------------- logica de ronda
def create_round_logic(world: esper.World, round_cfg: dict) -> None:
    world.create_entity(CAlert(round_cfg["yellow_time"], round_cfg["red_time"]))
    world.create_entity(CSpawner(round_cfg))
