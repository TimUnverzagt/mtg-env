from typing import Callable
from pygame import Surface
import math
                
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