import esper
from src.ecs.components.c_animation import CAnimation
from src.ecs.components.c_velocity import CVelocity
from src.ecs.components.c_player_state import CPlayerState, PlayerState
from src.engine.service_locator import ServiceLocator


def system_player_state(world: esper.World):
    """
    System that switches the player between IDLE and MOVE depending on its velocity.
    """
    components = world.get_components(CVelocity, CAnimation, CPlayerState)
    for _, (c_v, c_a, c_pst) in components:
        if c_v.vel.magnitude_squared() > 0:
            if c_pst.state == PlayerState.IDLE:
                ServiceLocator.sounds_service.play(c_pst.sound_move)
            c_pst.state = PlayerState.MOVE
            c_a.set_animation("MOVE")
        else:
            c_pst.state = PlayerState.IDLE
            c_a.set_animation("IDLE")
