import pygame


class CShieldText:

    def __init__(self, font: pygame.font.Font, text: str) -> None:
        self.font = font
        self.text = text  # Text currently rendered in the surface
        self.ready_text = text
