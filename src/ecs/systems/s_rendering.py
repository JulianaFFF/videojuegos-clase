import esper
import pygame

from src.ecs.components.c_camera_shake import CCameraShake
from src.ecs.components.c_transform import CTransform
from src.ecs.components.c_surface import CSurface
from src.ecs.components.tags.c_tag_hud import CTagHUD

def system_rendering(world:esper.World, screen:pygame.Surface):
    offset = pygame.Vector2(0, 0)
    for _, c_shake in world.get_component(CCameraShake):
        offset = c_shake.offset

    components = world.get_components(CTransform, CSurface)
    
    c_t:CTransform
    c_s:CSurface
    hud = []
    for entity, (c_t, c_s) in components:
        if world.has_component(entity, CTagHUD):
            hud.append((c_t, c_s))
            continue
        screen.blit(c_s.surf, c_t.pos + offset, area=c_s.area)
    # La interfaz se dibuja encima y no tiembla con la camara
    for c_t, c_s in hud:
        screen.blit(c_s.surf, c_t.pos, area=c_s.area)
