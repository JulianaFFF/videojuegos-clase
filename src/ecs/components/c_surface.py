import pygame

class CSurface:

    def __init__(self, size: pygame.Vector2, color: pygame.Color) -> None:
        self.surf = pygame.Surface(size)
        self.surf.fill(color)
        # Area of the surface that is drawn and used for collisions (a single sprite frame)
        self.area = self.surf.get_rect()

    @classmethod
    def from_surface(cls, surface: pygame.Surface, number_frames: int = 1) -> "CSurface":
        c_surf = cls(pygame.Vector2(0, 0), pygame.Color(0, 0, 0))
        c_surf.surf = surface
        # The texture is a linear strip of frames, so each frame has width / number_frames
        frame_w = surface.get_width() / max(number_frames, 1)
        c_surf.area = pygame.Rect(0, 0, frame_w, surface.get_height())
        return c_surf

    @staticmethod
    def get_area_relative(area: pygame.Rect, pos: pygame.Vector2) -> pygame.Rect:
        """Returns the area placed at the given position (screen space rect)."""
        return pygame.Rect(pos.x, pos.y, area.width, area.height)
