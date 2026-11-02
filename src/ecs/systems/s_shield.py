import pygame
import esper
from src.ecs.components.c_shield import CShield, ShieldState
from src.ecs.components.c_surface import CSurface
from src.ecs.components.c_transform import CTransform
from src.ecs.components.tags.c_tag_shield_fx import CTagShieldFx

BLINK_FREQUENCY = 12  # Toggles per second of the warning before the shield runs out


def system_shield(world: esper.World, player_entity: int, dt: float):
    """
    State machine of the shield: ACTIVE -> COOLDOWN -> READY.
    While active its effects follow the player and blink when it is about to end.
    """
    c_sh = world.component_for_entity(player_entity, CShield)
    c_sh.ready_flash = max(c_sh.ready_flash - dt, 0)

    if c_sh.state == ShieldState.COOLDOWN:
        c_sh.time_left -= dt
        if c_sh.time_left <= 0:
            c_sh.state = ShieldState.READY
            c_sh.time_left = 0.0
            c_sh.ready_flash = c_sh.ready_flash_time

    elif c_sh.state == ShieldState.ACTIVE:
        c_sh.time_left -= dt
        pl_t = world.component_for_entity(player_entity, CTransform)
        pl_s = world.component_for_entity(player_entity, CSurface)
        player_center = pl_t.pos + pygame.Vector2(pl_s.area.size) / 2
        finished = c_sh.time_left <= 0
        visible = c_sh.time_left > c_sh.blink_time or int(c_sh.time_left * BLINK_FREQUENCY) % 2 == 0
        for fx_entity, (c_t, c_s, _) in world.get_components(CTransform, CSurface, CTagShieldFx):
            if finished:
                world.delete_entity(fx_entity)
            c_t.pos = player_center - pygame.Vector2(c_s.area.size) / 2
            c_s.visible = visible
        if finished:
            c_sh.state = ShieldState.COOLDOWN
            c_sh.time_left = c_sh.cooldown
