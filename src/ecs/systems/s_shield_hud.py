import esper
import pygame

from src.ecs.components.c_shield import CShield
from src.ecs.components.c_surface import CSurface
from src.ecs.components.c_text import CText
from src.ecs.components.c_transform import CTransform
from src.ecs.components.tags.c_tag_shield_bar import CTagShieldBar
from src.ecs.components.tags.c_tag_shield_text import CTagShieldText

def _color(cfg:dict) -> pygame.Color:
    return pygame.Color(cfg["r"], cfg["g"], cfg["b"])

def system_shield_hud(world:esper.World, player_entity:int, interface_cfg:dict, game_time:float):
    c_sh = world.component_for_entity(player_entity, CShield)
    bar_cfg = interface_cfg["shield_bar"]
    status_cfg = interface_cfg["shield_status"]
    # El "LISTO" parpadea suavemente para llamar la atencion
    blink_on = int(game_time * 3) % 2 == 0

    if c_sh.is_active:
        fill = c_sh.time_active / c_sh.duration
        bar_color = _color(bar_cfg["color_active"])
        text = status_cfg["text_active"]
        text_color = _color(status_cfg["color"])
    elif c_sh.time_cooldown > 0:
        fill = 1 - (c_sh.time_cooldown / c_sh.cooldown)
        bar_color = _color(bar_cfg["color_charging"])
        text = f"{c_sh.time_cooldown:.1f}s"
        text_color = _color(status_cfg["color"])
    else:
        fill = 1
        bar_color = _color(bar_cfg["color_ready"])
        text = status_cfg["text_ready"]
        text_color = _color(status_cfg["color_ready"]) if blink_on else _color(status_cfg["color"])

    for _, (c_s, _) in world.get_components(CSurface, CTagShieldBar):
        c_s.surf.fill(_color(bar_cfg["color_bg"]))
        fill_rect = c_s.surf.get_rect()
        fill_rect.w = round(fill_rect.w * max(0, min(fill, 1)))
        c_s.surf.fill(bar_color, fill_rect)

    # Texto dinamico: se vuelve a renderizar la superficie cuando cambia
    for _, (c_s, c_t, c_txt, _) in world.get_components(CSurface, CTransform, CText, CTagShieldText):
        if c_txt.text == text and c_txt.color == text_color:
            continue
        c_txt.text = text
        c_txt.color = text_color
        c_s.surf = c_txt.font.render(text, True, text_color)
        c_s.area = c_s.surf.get_rect()
        rect = c_s.surf.get_rect(**{c_txt.anchor: c_txt.anchor_pos})
        c_t.pos.xy = rect.topleft
