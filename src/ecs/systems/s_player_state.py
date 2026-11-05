import esper
from src.ecs.components.c_player_state import CPlayerState, PlayerState
from src.ecs.components.c_velocity import CVelocity
from src.ecs.components.c_animation import CAnimation
from src.engine.service_locator import ServiceLocator

def system_player_state(world:esper.World, player_info:dict):
    components = world.get_components(CVelocity, CAnimation, CPlayerState)
    for _, (c_v, c_a, c_pst) in components:
        if c_pst.state == PlayerState.IDLE:
            _do_idle_state(c_v, c_a, c_pst, player_info)
        elif c_pst.state == PlayerState.MOVE:
            _do_move_state(c_v, c_a, c_pst)

def _do_idle_state(c_v:CVelocity, c_a:CAnimation, c_pst:CPlayerState, player_info:dict):
    c_a.set_animation("IDLE")
    if c_v.vel.magnitude_squared() > 0:
        c_pst.state = PlayerState.MOVE
        # Sonido de propulsion al empezar a moverse
        if "sound_move" in player_info:
            ServiceLocator.sounds_service.play(player_info["sound_move"])

def _do_move_state(c_v:CVelocity, c_a:CAnimation, c_pst:CPlayerState):
    c_a.set_animation("MOVE")
    if c_v.vel.magnitude_squared() <= 0:
        c_pst.state = PlayerState.IDLE
