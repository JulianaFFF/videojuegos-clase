import random
import esper
from src.ecs.components.c_camera_shake import CCameraShake


def system_camera_shake(world: esper.World, dt: float):
    """
    System that moves the camera randomly, fading out until the shake finishes.
    """
    for _, c_shake in world.get_component(CCameraShake):
        c_shake.time_left = max(c_shake.time_left - dt, 0)
        strength = c_shake.intensity * c_shake.time_left / c_shake.duration if c_shake.duration else 0
        c_shake.offset.xy = (random.uniform(-strength, strength), random.uniform(-strength, strength))
