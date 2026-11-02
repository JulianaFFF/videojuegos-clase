import pygame
import esper
from src.ecs.components.c_shield import CShield, ShieldState
from src.ecs.components.c_shield_bar import CShieldBar
from src.ecs.components.c_shield_text import CShieldText
from src.ecs.components.c_surface import CSurface


def system_shield_hud(world: esper.World, player_entity: int):
    """
    System that keeps the bar and the text of the shield in sync with its state.
    The bar drains while active and refills during the cooldown.
    """
    c_sh = world.component_for_entity(player_entity, CShield)

    for _, (c_s, c_b) in world.get_components(CSurface, CShieldBar):
        if c_sh.state == ShieldState.ACTIVE:
            fill, color = c_sh.time_left / c_sh.duration, c_b.active
        elif c_sh.state == ShieldState.COOLDOWN:
            fill, color = 1 - c_sh.time_left / c_sh.cooldown, c_b.cooldown
        else:
            fill, color = 1, c_b.flash if c_sh.ready_flash > 0 else c_b.ready
        c_s.surf.fill(c_b.background)
        c_s.surf.fill(color, pygame.Rect(0, 0, c_s.area.width * max(fill, 0), c_s.area.height))

    for _, (c_s, c_t) in world.get_components(CSurface, CShieldText):
        if c_sh.state == ShieldState.READY:
            text, color = c_t.ready_text, c_b.ready
        else:
            text = f"{max(c_sh.time_left, 0):.1f}s"
            color = c_b.active if c_sh.state == ShieldState.ACTIVE else c_b.cooldown
        if text != c_t.text:
            # A text that changes needs a new surface, so its area is replaced too
            c_t.text = text
            c_s.surf = c_t.font.render(text, False, color)
            c_s.area = c_s.surf.get_rect()
