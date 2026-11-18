import esper

from src.ecs.components.c_animation import CAnimation
from src.ecs.components.c_surface import CSurface


def system_animation(world: esper.World, delta_time: float) -> None:
    for _, (c_s, c_a) in world.get_components(CSurface, CAnimation):
        if c_a.paused or c_a.finished or not c_s.visible:
            continue
        c_a.time += delta_time
        while c_a.time >= c_a.frame_time:
            c_a.time -= c_a.frame_time
            c_a.curr_frame += 1
            if c_a.curr_frame >= len(c_a.frames):
                if c_a.loop:
                    c_a.curr_frame = 0
                else:
                    c_a.curr_frame = len(c_a.frames) - 1
                    c_a.finished = True
                    break
        c_s.surf = c_a.frames[c_a.curr_frame]
