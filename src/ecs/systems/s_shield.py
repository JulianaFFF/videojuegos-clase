import esper
import pygame

from src.create.prefab_creator import create_explosion
from src.ecs.components.c_shield import CShield
from src.ecs.components.c_surface import CSurface
from src.ecs.components.c_transform import CTransform
from src.ecs.components.tags.c_tag_enemy import CTagEnemy
from src.engine.service_locator import ServiceLocator

def system_shield(world:esper.World, delta_time:float, shield_cfg:dict, explosion_cfg:dict):
    components = world.get_components(CShield, CTransform, CSurface)

    c_sh:CShield
    for _, (c_sh, c_t, c_s) in components:
        player_center = pygame.Vector2(CSurface.get_area_relative(c_s.area, c_t.pos).center)

        if c_sh.is_active:
            c_sh.time_active -= delta_time
            _follow_player(world, c_sh, player_center)
            _destroy_near_enemies(world, c_sh, player_center, explosion_cfg)
            if not c_sh.is_active and world.entity_exists(c_sh.shield_entity):
                world.delete_entity(c_sh.shield_entity)
                c_sh.shield_entity = -1
        elif c_sh.time_cooldown > 0:
            c_sh.time_cooldown -= delta_time
            if c_sh.time_cooldown <= 0:
                c_sh.time_cooldown = 0
                ServiceLocator.sounds_service.play(shield_cfg["sound_ready"])

def _follow_player(world:esper.World, c_sh:CShield, player_center:pygame.Vector2):
    if not world.entity_exists(c_sh.shield_entity):
        return
    sh_t = world.component_for_entity(c_sh.shield_entity, CTransform)
    sh_s = world.component_for_entity(c_sh.shield_entity, CSurface)
    sh_t.pos.xy = (player_center.x - sh_s.area.w / 2, player_center.y - sh_s.area.h / 2)

def _destroy_near_enemies(world:esper.World, c_sh:CShield, player_center:pygame.Vector2, explosion_cfg:dict):
    for enemy_entity, (ene_s, ene_t, _) in world.get_components(CSurface, CTransform, CTagEnemy):
        ene_rect = CSurface.get_area_relative(ene_s.area, ene_t.pos)
        if player_center.distance_to(ene_rect.center) <= c_sh.radius:
            world.delete_entity(enemy_entity)
            create_explosion(world, ene_rect.center, explosion_cfg)
