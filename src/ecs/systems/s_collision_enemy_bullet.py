import esper

from src.create.prefab_creator import create_explosion
from src.ecs.components.c_surface import CSurface
from src.ecs.components.c_transform import CTransform
from src.ecs.components.tags.c_tag_bullet import CTagBullet
from src.ecs.components.tags.c_tag_enemy import CTagEnemy

def system_collision_enemy_bullet(world:esper.World, explosion_cfg:dict):
    enemies = world.get_components(CSurface, CTransform, CTagEnemy)
    bullets = world.get_components(CSurface, CTransform, CTagBullet)
    destroyed_bullets = set()

    for enemy_entity, (ene_s, ene_t, _) in enemies:
        ene_rect = CSurface.get_area_relative(ene_s.area, ene_t.pos)
        for bullet_entity, (bul_s, bul_t, _) in bullets:
            if bullet_entity in destroyed_bullets:
                continue
            bul_rect = CSurface.get_area_relative(bul_s.area, bul_t.pos)
            if ene_rect.colliderect(bul_rect):
                world.delete_entity(enemy_entity)
                world.delete_entity(bullet_entity)
                destroyed_bullets.add(bullet_entity)
                create_explosion(world, ene_rect.center, explosion_cfg)
                break
