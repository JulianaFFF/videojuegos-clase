"""HUD lateral: puntajes, ronda, alerta, minimapa, vidas y cargas especiales."""
import esper
import pygame

from src.create.prefab_creator import cfg
from src.ecs.components.c_alert import CAlert
from src.ecs.components.c_base import CBase
from src.ecs.components.c_enemy import CEnemy
from src.ecs.components.c_player import CPlayer
from src.ecs.components.c_spy import CSpy
from src.ecs.components.c_transform import CTransform
from src.engine.service_locator import ServiceLocator


def _text(screen, font, text, color, pos, align="left"):
    surf = font.render(text, False, color)
    x, y = pos
    if align == "right":
        x -= surf.get_width()
    elif align == "center":
        x -= surf.get_width() // 2
    screen.blit(surf, (x, y))


def system_hud(world: esper.World, screen: pygame.Surface, session, panel: pygame.Rect,
               world_w: int, world_h: int, time: float) -> None:
    ui = cfg("interface")
    col = {k: pygame.Color(*v) for k, v in ui["colors"].items()}
    font = ServiceLocator.fonts_service.get(ui["font"], 8)
    screen.fill(col["panel"], panel)
    pygame.draw.line(screen, col["panel_line"], panel.topleft, panel.bottomleft)
    x = panel.x + 4
    r = panel.right - 3
    _text(screen, font, "HI-SCORE", col["red"], (x, 4))
    _text(screen, font, str(session.hiscore), col["white"], (r, 14), "right")
    _text(screen, font, "1UP", col["cyan"], (x, 26))
    _text(screen, font, str(session.score), col["white"], (r, 36), "right")

    # Alerta (estado actual)
    alerts = cfg("alerts")
    for _, c_a in world.get_component(CAlert):
        a_cfg = alerts[c_a.level.name]
        color = pygame.Color(*a_cfg["color"])
        box = pygame.Rect(panel.x + 3, 50, panel.w - 6, 22)
        blink = c_a.level.name == "RED" and int(time * 4) % 2 == 0
        pygame.draw.rect(screen, color if not blink else col["panel"], box)
        _text(screen, font, "COND", (0, 0, 0) if not blink else color, (box.centerx, box.y + 2), "center")
        _text(screen, font, c_a.level.name[:6], (0, 0, 0) if not blink else color,
              (box.centerx, box.y + 12), "center")

    _text(screen, font, "ROUND", col["yellow"], (x, 78))
    _text(screen, font, str(session.round), col["white"], (r, 88), "right")

    # Minimapa
    mm = ui["minimap"]
    m_rect = pygame.Rect(mm["x"], mm["y"], mm["w"], mm["h"])
    pygame.draw.rect(screen, mm["bg"], m_rect)
    pygame.draw.rect(screen, col["panel_line"], m_rect, 1)
    sx, sy = (m_rect.w - 2) / world_w, (m_rect.h - 2) / world_h

    def mpos(p):
        return int(m_rect.x + 1 + p.x * sx), int(m_rect.y + 1 + p.y * sy)

    for ent, (_, c_t) in world.get_components(CBase, CTransform):
        px, py = mpos(c_t.pos)
        screen.fill(mm["base"], (px - 1, py - 1, 3, 3))
    for _, (c_e, c_t) in world.get_components(CEnemy, CTransform):
        if c_e.leader is not None:  # formaciones (bono): se marcan en el minimapa
            screen.fill(mm["enemy"], (*mpos(c_t.pos), 1, 1))
    for _, (_, c_t) in world.get_components(CSpy, CTransform):
        if int(time * 6) % 2 == 0:
            screen.fill(mm["spy"], (*mpos(c_t.pos), 2, 2))
    for _, (_, c_t) in world.get_components(CPlayer, CTransform):
        px, py = mpos(c_t.pos)
        if int(time * 5) % 3:
            screen.fill(mm["player"], (px - 1, py - 1, 2, 2))

    # Vidas y cargas especiales
    life_img = ServiceLocator.images_service.get_frame("player")
    small = pygame.transform.scale(life_img, (8, 10))
    for i in range(min(session.lives, 6)):
        screen.blit(small, (x + i * 10, 166))
    charges = 0
    for _, c_p in world.get_component(CPlayer):
        charges = c_p.special_charges
    _text(screen, font, "SP", col["cyan"], (x, 182))
    for i in range(min(charges, 6)):
        pygame.draw.rect(screen, col["cyan"], (x + 18 + i * 6, 183, 4, 6))
    n_bases = sum(1 for _ in world.get_component(CBase))
    _text(screen, font, "BASE", col["green"], (x, 196))
    _text(screen, font, str(n_bases), col["white"], (r, 196), "right")
