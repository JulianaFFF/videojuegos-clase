import pygame
import esper
from src.create.prefab_creator import create_explosion
from src.ecs.components.c_transform import CTransform
from src.ecs.components.c_surface import CSurface
from src.ecs.components.c_shield import CShield, ShieldState
from src.ecs.components.tags.c_tag_enemy import CTagEnemy


def system_collision_player_enemy(world: esper.World, player_entity: int, level_cfg: dict, explosion_cfg: dict):
    """
    System that detects collisions between the player and enemies.
    The enemy is destroyed (leaving an explosion) and the player returns to its spawn position.
    The player cannot be hit while the shield is active.
    """
    if world.component_for_entity(player_entity, CShield).state == ShieldState.ACTIVE:
        return

    pl_t = world.component_for_entity(player_entity, CTransform)
    pl_s = world.component_for_entity(player_entity, CSurface)
    player_rect = CSurface.get_area_relative(pl_s.area, pl_t.pos)

    components = world.get_components(CTransform, CSurface, CTagEnemy)
    for enemy_entity, (transform, surface, _) in components:
        enemy_rect = CSurface.get_area_relative(surface.area, transform.pos)
        if enemy_rect.colliderect(player_rect):
            world.delete_entity(enemy_entity)
            create_explosion(world, pygame.Vector2(enemy_rect.center), explosion_cfg)
            spawn = level_cfg["player_spawn"]["position"]
            pl_t.pos.x = spawn["x"] - player_rect.width / 2
            pl_t.pos.y = spawn["y"] - player_rect.height / 2
            player_rect.topleft = pl_t.pos
