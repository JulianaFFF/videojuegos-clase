import esper
from src.ecs.components.c_transform import CTransform
from src.ecs.components.c_surface import CSurface
from src.ecs.components.tags.c_tag_enemy import CTagEnemy


def system_collision_player_enemy(world: esper.World, player_entity: int, level_cfg: dict):
    """
    System that detects collisions between the player and enemies.
    The enemy is destroyed and the player returns to its spawn position.
    """
    pl_t = world.component_for_entity(player_entity, CTransform)
    pl_s = world.component_for_entity(player_entity, CSurface)
    player_rect = pl_s.surf.get_rect(topleft=pl_t.pos)

    components = world.get_components(CTransform, CSurface, CTagEnemy)
    for enemy_entity, (transform, surface, _) in components:
        enemy_rect = surface.surf.get_rect(topleft=transform.pos)
        if enemy_rect.colliderect(player_rect):
            world.delete_entity(enemy_entity)
            spawn = level_cfg["player_spawn"]["position"]
            pl_t.pos.x = spawn["x"] - player_rect.width / 2
            pl_t.pos.y = spawn["y"] - player_rect.height / 2
            player_rect.topleft = pl_t.pos
