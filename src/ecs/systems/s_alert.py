import esper

from src.ecs.components.c_alert import AlertLevel, CAlert


def set_alert(c_a: CAlert, level: AlertLevel) -> None:
    if level.value > c_a.level.value:
        c_a.level = level
        c_a.changed = True


def system_alert(world: esper.World, delta_time: float, ctx) -> None:
    """VERDE -> AMARILLA -> ROJA segun el tiempo que el jugador tarda en limpiar la ronda."""
    for _, c_a in world.get_component(CAlert):
        c_a.time += delta_time
        if c_a.time > c_a.red_time:
            set_alert(c_a, AlertLevel.RED)
        elif c_a.time > c_a.yellow_time:
            set_alert(c_a, AlertLevel.YELLOW)
        if c_a.changed:
            c_a.changed = False
            ctx.on_alert_changed(c_a.level)
