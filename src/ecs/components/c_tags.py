class CTagUI:
    """Entidad en coordenadas de pantalla (texto, menus); no usa camara ni wraparound."""
class CTagBlink:
    """Texto que parpadea."""
    def __init__(self, period: float = 0.5) -> None:
        self.period = period
        self.time = 0.0
class CTagIntroSlide:
    """Elemento de la intro animada que se desliza hasta su destino."""
    def __init__(self, target, speed: float) -> None:
        self.target = target
        self.speed = speed
