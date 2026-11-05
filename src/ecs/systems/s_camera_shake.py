import random

import esper

from src.ecs.components.c_camera_shake import CCameraShake

def system_camera_shake(world:esper.World, delta_time:float):
    for _, c_shake in world.get_component(CCameraShake):
        if c_shake.time_left <= 0:
            c_shake.offset.xy = (0, 0)
            continue
        c_shake.time_left -= delta_time
        # La intensidad se reduce a medida que se acaba el temblor
        strength = c_shake.intensity * max(c_shake.time_left, 0) / c_shake.duration
        c_shake.offset.xy = (random.uniform(-strength, strength),
                             random.uniform(-strength, strength))
