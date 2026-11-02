from src.engine.services.ConfigsService import ConfigsService
from src.engine.services.FontsService import FontsService
from src.engine.services.ImagesService import ImagesService
from src.engine.services.SoundsService import SoundsService


class ServiceLocator:
    """Single access point for every external resource of the game."""

    configs_service = ConfigsService()
    fonts_service = FontsService()
    images_service = ImagesService()
    sounds_service = SoundsService()
