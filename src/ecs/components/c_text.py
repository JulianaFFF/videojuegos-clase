import pygame

class CText:
    def __init__(self, font:pygame.font.Font, color:pygame.Color, anchor:str, anchor_pos:tuple) -> None:
        self.font = font
        self.color = color
        self.anchor = anchor
        self.anchor_pos = anchor_pos
        self.text = ""
