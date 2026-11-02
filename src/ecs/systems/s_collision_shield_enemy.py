import pygame
import esper
from src.create.prefab_creator import create_explosion
from src.ecs.components.c_camera_shake import CCameraShake
from src.ecs.components.c_shield import CShield, ShieldState
from src.ecs.components.c_surface import CSurface
from src.ecs.components.c_transform import CTransform
from src.ecs.components.tags.c_tag_enemy import CTagEnemy


def system_collision_shield_enemy(world: esper.World, player_entity: int, explosion_cfg: dict):
    """
    System that destroys every enemy that touches the ring of the active shield,
    shaking the camera with each one.
    """
    c_sh = world.component_for_entity(player_entity, CShield)
    if c_sh.state != ShieldState.ACTIVE:
        return

    pl_t = world.component_for_entity(player_entity, CTransform)
    pl_s = world.component_for_entity(player_entity, CSurface)
    player_center = pl_t.pos + pygame.Vector2(pl_s.area.size) / 2

    components = world.get_components(CTransform, CSurface, CTagEnemy)
    for enemy_entity, (transform, surface, _) in components:
        enemy_rect = CSurface.get_area_relative(surface.area, transform.pos)
        enemy_center = pygame.Vector2(enemy_rect.center)
        if enemy_center.distance_to(player_center) < c_sh.radius + enemy_rect.width / 2:
            world.delete_entity(enemy_entity)
            create_explosion(world, enemy_center, explosion_cfg)
            for _, c_shake in world.get_component(CCameraShake):
                c_shake.start(c_sh.shake_kill)
