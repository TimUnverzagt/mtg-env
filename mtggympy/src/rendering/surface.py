from typing import Callable
import pygame
from pygame import Surface
import math
import os

from config.app_config import SRC_DIR
                
get_width: Callable[[Surface], int] = lambda surf: surf.get_width()
get_height: Callable[[Surface], int] = lambda surf: surf.get_height()

def pad_surface(surface: Surface, padding_ratio: float) -> Surface:
    new_width: int = math.floor(surface.get_width()*(1+padding_ratio))
    new_height: int =  math.floor(surface.get_height()*(1+padding_ratio))
    new_surface: Surface = Surface((new_width, new_height))
    horizontal_padding_offset: int = math.floor(surface.get_width()*(padding_ratio / 2))
    vertical_padding_offset: int = math.floor(surface.get_height()*(padding_ratio / 2))
    new_surface.blit(surface, (horizontal_padding_offset, vertical_padding_offset))
    return new_surface

def load_image(file_name: str, file_type:str, dir_trajectory: list[str]) -> Surface:
    path: str = SRC_DIR
    for dir_name in dir_trajectory:
        path = os.path.join(path, dir_name)
    return pygame.image.load(os.path.join(path, "{}.{}".format(file_name, file_type)))