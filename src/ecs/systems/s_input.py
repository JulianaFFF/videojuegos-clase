from typing import Callable

import esper
import pygame

from src.ecs.components.c_input_command import CInputCommand, CommandPhase

_DIRS = {"UP": (1, -1), "DOWN": (1, 1), "LEFT": (0, -1), "RIGHT": (0, 1)}


def _set(c_input: CInputCommand, pressed: bool, do_action: Callable) -> None:
    if pressed and not c_input.held:
        c_input.held = True
        c_input.phase = CommandPhase.START
        do_action(c_input)
    elif not pressed and c_input.held:
        c_input.held = False
        c_input.phase = CommandPhase.END
        do_action(c_input)


def system_input(world: esper.World, event: pygame.event.Event, do_action: Callable,
                 deadzone: float = 0.4) -> None:
    """Traduce eventos de teclado y gamepad en comandos (patron Command)."""
    for _, c_input in world.get_component(CInputCommand):
        if event.type in (pygame.KEYDOWN, pygame.KEYUP) and event.key in c_input.keys:
            _set(c_input, event.type == pygame.KEYDOWN, do_action)
        elif event.type in (pygame.JOYBUTTONDOWN, pygame.JOYBUTTONUP) \
                and event.button in c_input.joy_buttons:
            _set(c_input, event.type == pygame.JOYBUTTONDOWN, do_action)
        elif c_input.name in _DIRS and event.type == pygame.JOYHATMOTION:
            axis, sign = _DIRS[c_input.name]
            value = event.value[axis] * (-1 if axis == 1 else 1)
            _set(c_input, value == sign, do_action)
        elif c_input.name in _DIRS and event.type == pygame.JOYAXISMOTION and event.axis in (0, 1):
            axis, sign = _DIRS[c_input.name]
            if event.axis == axis:
                _set(c_input, event.value * sign > deadzone, do_action)
