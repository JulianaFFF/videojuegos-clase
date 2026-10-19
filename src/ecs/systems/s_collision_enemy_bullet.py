import esper
from src.ecs.components.c_transform import CTransform
from src.ecs.components.c_surface import CSurface
from src.ecs.components.tags.c_tag_enemy import CTagEnemy
from src.ecs.components.tags.c_tag_bullet import CTagBullet


def system_collision_enemy_bullet(world: esper.World):
    """
    System that destroys both the enemy and the bullet when they collide.
    """
    enemies = world.get_components(CTransform, CSurface, CTagEnemy)
    bullets = world.get_components(CTransform, CSurface, CTagBullet)
    destroyed_bullets = set()
    for enemy_entity, (e_transform, e_surface, _) in enemies:
        enemy_rect = e_surface.surf.get_rect(topleft=e_transform.pos)
        for bullet_entity, (b_transform, b_surface, _) in bullets:
            if bullet_entity in destroyed_bullets:
                continue
            bullet_rect = b_surface.surf.get_rect(topleft=b_transform.pos)
            if enemy_rect.colliderect(bullet_rect):
                world.delete_entity(enemy_entity)
                world.delete_entity(bullet_entity)
                destroyed_bullets.add(bullet_entity)
                break
