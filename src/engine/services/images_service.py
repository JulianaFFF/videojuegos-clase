import pygame


class ImagesService:
    """Administra imagenes: archivos completos, recortes de la hoja de sprites
    (definidos en sprites.json) y versiones rotadas cacheadas."""

    def __init__(self) -> None:
        self._images = {}
        self._frames = {}
        self._rotated = {}
        self._sprites_cfg = None

    def get(self, path: str) -> pygame.Surface:
        if path not in self._images:
            self._images[path] = pygame.image.load(path).convert_alpha()
        return self._images[path]

    def get_scaled(self, path: str, size: tuple) -> pygame.Surface:
        key = (path, int(size[0]), int(size[1]))
        if key not in self._images:
            self._images[key] = pygame.transform.scale(self.get(path), key[1:])
        return self._images[key]

    def get_clean(self, path: str, min_alpha: int = 100) -> pygame.Surface:
        """Imagen con los pixeles semitransparentes eliminados (para el logo)."""
        key = ("__clean__", path)
        if key not in self._images:
            surf = self.get(path).copy()
            for x in range(surf.get_width()):
                for y in range(surf.get_height()):
                    if surf.get_at((x, y)).a < min_alpha:
                        surf.set_at((x, y), (0, 0, 0, 0))
            self._images[key] = surf
        return self._images[key]

    def set_sprites_config(self, cfg: dict) -> None:
        self._sprites_cfg = cfg

    def get_frames(self, name: str) -> list:
        if name not in self._frames:
            sheet = self.get(self._sprites_cfg["sheet"])
            self._frames[name] = [sheet.subsurface(pygame.Rect(r)).copy()
                                  for r in self._sprites_cfg["frames"][name]]
        return self._frames[name]

    def get_frame(self, name: str, index: int = 0) -> pygame.Surface:
        frames = self.get_frames(name)
        return frames[index % len(frames)]

    def get_rotated(self, name: str, angle_deg: int, index: int = 0) -> pygame.Surface:
        """Angulo en grados medido en sentido horario desde 'arriba' (sprites miran hacia arriba)."""
        key = (name, angle_deg, index)
        if key not in self._rotated:
            self._rotated[key] = pygame.transform.rotate(self.get_frame(name, index), -angle_deg)
        return self._rotated[key]

    def get_base(self, layout: str) -> pygame.Surface:
        """Construye la imagen de fondo de una base (tuberias) a partir del sprite compuesto,
        borrando las torres y el nucleo, que se dibujan como entidades propias."""
        key = ("__base__", layout)
        if key not in self._images:
            cfg = self._sprites_cfg["base"]
            sheet = self.get(self._sprites_cfg["sheet"])
            surf = sheet.subsurface(pygame.Rect(cfg["rect"])).copy()
            key_color = pygame.Color(*cfg["colorkey"])
            for x in range(surf.get_width()):
                for y in range(surf.get_height()):
                    if surf.get_at((x, y))[:3] == key_color[:3]:
                        surf.set_at((x, y), (0, 0, 0, 0))
            for sx, sy in cfg["turret_slots"]:
                surf.fill((0, 0, 0, 0), pygame.Rect(sx, sy, 16, 16))
            cx, cy = cfg["core_slot"]
            surf.fill((0, 0, 0, 0), pygame.Rect(cx, cy, 20, 20))
            if layout == "v":
                surf = pygame.transform.rotate(surf, -90)
            self._images[key] = surf
        return self._images[key]
