import esper
from src.ecs.components.c_animation import CAnimation
from src.ecs.components.c_surface import CSurface


def system_animation(world: esper.World, dt: float):
    """
    System that advances the frame of every animation and moves the
    drawn area of the surface to the current frame of the texture.
    """
    components = world.get_components(CSurface, CAnimation)
    for _, (c_s, c_a) in components:
        anim = c_a.animations_list[c_a.curr_anim]
        c_a.curr_anim_time -= dt
        while c_a.curr_anim_time <= 0:
            c_a.curr_anim_time += anim.framerate
            c_a.curr_frame += 1
            if c_a.curr_frame > anim.end:
                c_a.curr_frame = anim.start
                c_a.finished = True
        c_s.area.x = c_s.area.w * c_a.curr_frame
