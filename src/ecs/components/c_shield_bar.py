import pygame


class CShieldBar:

    def __init__(
        self, background: pygame.Color, ready: pygame.Color, active: pygame.Color, cooldown: pygame.Color, flash: pygame.Color
    ) -> None:
        self.background = background
        self.ready = ready
        self.active = active
        self.cooldown = cooldown
        self.flash = flash
