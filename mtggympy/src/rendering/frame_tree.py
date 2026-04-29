from __future__ import annotations
import math
import pygame
from pygame import Surface
from typing import Optional

from logging_config import ui_log as logger
from rendering.bounding_box import BoundingBox, do_bounding_boxes_collide, does_first_box_fit_into_second

class Texture():
    def __init__(self) -> None:
        self.content: int = 1

def textures_are_same_height(textures: list[FrameTree]) -> bool:
    height: int|None = None
    for texture in textures:
        if not height:
            height = texture.bounding_box.height
        if height != texture.bounding_box.height:
            return False
    return True

class FrameTree():
    def __init__(self, width: int, height: int, horizontal_offset: int=0, vertical_offset:int=0) -> None:
        self.bounding_box: BoundingBox = BoundingBox(width, height, horizontal_offset, vertical_offset)
        self.content: Optional[Surface] = None
        self.children: list[FrameTree] = []

    def child_exceeds_bounding_box(self, box: BoundingBox) -> bool:
        return not does_first_box_fit_into_second(box, self.bounding_box)
    
    def child_collides_with_existing_children(self, box: BoundingBox) -> bool:
        does_collide_with_any: bool = False
        for prior_child in self.children:
            does_collide_with_any |= do_bounding_boxes_collide(box, prior_child.bounding_box)
        return does_collide_with_any

    def add_child(self, child: FrameTree) -> None:
        if (self.child_exceeds_bounding_box(child.bounding_box)):
            logger.error("Can't add child to this TextureTree because it would exceed parent bounding box. Aborting addition!")
            return
        if (self.child_collides_with_existing_children(child.bounding_box)):
            logger.error("Can't add child to this TextureTree because it collided with preexisting children. Aborting addition!")
            return
        self.children.append(child)

    def set_content(self, new_content: Surface):
        self.content = pygame.transform.scale(new_content, (self.bounding_box.width, self.bounding_box.height))

def build_texture_tree_from_ratios(parent_box: BoundingBox, width_r: float, height_r: float, horizontal_offset_r: float=0, vertical_offset_r:float=0) -> FrameTree:
    width: int = math.floor(parent_box.width * width_r)
    horizontal_offset: int = math.floor(parent_box.width * horizontal_offset_r)
    height: int = math.floor(parent_box.height * height_r)
    vertical_offset: int = math.floor(parent_box.height * vertical_offset_r)
    return FrameTree(width, height, horizontal_offset, vertical_offset)


