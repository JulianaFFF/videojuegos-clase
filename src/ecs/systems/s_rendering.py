import esper
import pygame

from src.ecs.components.c_camera import CCamera
from src.ecs.components.c_surface import CSurface
from src.ecs.components.c_tags import CTagUI
from src.ecs.components.c_transform import CTransform
from src.engine.world_math import wrap_delta


def system_rendering(world: esper.World, screen: pygame.Surface, world_w: int, world_h: int,
                     view: pygame.Rect, time: float) -> None:
    """Dibuja el mundo relativo a la camara (con wraparound) y despues la interfaz."""
    cam = None
    for _, c_c in world.get_component(CCamera):
        cam = c_c
    to_draw = []
    ui = []
    for ent, (c_t, c_s) in world.get_components(CTransform, CSurface):
        if not c_s.visible:
            continue
        if c_s.flash > 0 and int(time * 16) % 2 == 0:
            continue
        if world.has_component(ent, CTagUI) or cam is None:
            ui.append((c_s.layer, c_t.pos, c_s.surf))
            continue
        rel = wrap_delta(cam.pos, c_t.pos, world_w, world_h)
        scr = pygame.Vector2(view.centerx, view.centery) + rel + cam.offset
        w, h = c_s.surf.get_size()
        if -w < scr.x - view.x < view.w + w and -h < scr.y - view.y < view.h + h:
            to_draw.append((c_s.layer, scr, c_s.surf))
    old_clip = screen.get_clip()
    screen.set_clip(view)
    for _, pos, surf in sorted(to_draw, key=lambda d: d[0]):
        screen.blit(surf, (round(pos.x - surf.get_width() / 2), round(pos.y - surf.get_height() / 2)))
    screen.set_clip(old_clip)
    for _, pos, surf in sorted(ui, key=lambda d: d[0]):
        screen.blit(surf, (round(pos.x - surf.get_width() / 2), round(pos.y - surf.get_height() / 2)))
