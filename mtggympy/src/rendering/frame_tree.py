from __future__ import annotations
import math
import pygame
from pygame import Surface
from pygame import Vector2 as Vector
from typing import Optional

from logging_config import ui_log as logger
from rendering.bounding_box import BoundingBox, do_bounding_boxes_collide, does_first_box_fit_into_second

class Texture():
    def __init__(self) -> None:
        self.content: int = 1

def get_pixel_width(box: BoundingBox) -> int:
    return math.floor(box.dimensions[0])

def get_pixel_height(box: BoundingBox) -> int:
    return math.floor(box.dimensions[1])

def textures_are_same_height(textures: list[FrameTree]) -> bool:
    reference_height: int|None = None
    for texture in textures:
        if not reference_height:
            reference_height = get_pixel_height(texture.global_bounding_box)
        if reference_height != get_pixel_height(texture.global_bounding_box):
            return False
    return True

class FrameTree():
    def __init__(self, name: str, dimensions: Vector, offsets: Vector = Vector(0,0)) -> None:
        self.name: str = name
        self.global_bounding_box: BoundingBox = BoundingBox(dimensions,offsets)
        self.content: Optional[Surface] = None
        self.children: list[FrameTree] = []

    def child_exceeds_bounding_box(self, child: FrameTree) -> bool:
        return not does_first_box_fit_into_second(child.global_bounding_box, self.global_bounding_box)
    
    def child_collides_with_existing_children(self, child: FrameTree) -> bool:
        does_collide_with_any: bool = False
        for prior_child in self.children:
            does_collide_with_any |= do_bounding_boxes_collide(
                child.global_bounding_box, 
                prior_child.global_bounding_box)
        return does_collide_with_any

    def add_child(self, child: FrameTree) -> None:
        if (self.child_exceeds_bounding_box(child)):
            logger.error("Can't add child {} to {} TextureTree because it would exceed parent bounding box. Aborting addition!"
                         .format(child.name, self.name))
            logger.error("Parent {}: {}".format(self.name, self.global_bounding_box))
            logger.error("Child {}: {}".format(child.name, child.global_bounding_box))
            return
        if (self.child_collides_with_existing_children(child)):
            logger.error("Can't add child {} to {} TextureTree because it collided with preexisting children. Aborting addition!"
                         .format(child.name, self.name))
            logger.error("Parent {}: {}".format(self.name, self.global_bounding_box))
            logger.error("Child {}: {}".format(child.name, child.global_bounding_box))
            for prev_child in self.children:
                logger.error("Prior child {}: {}".format(prev_child.name,prev_child.global_bounding_box))
            return
        self.children.append(child)

    def set_content(self, new_content: Surface):
        target_dimensons: Vector = self.global_bounding_box.dimensions
        self.content = pygame.transform.scale(new_content, (target_dimensons[0], target_dimensons[1]))

    def scale_by(self, scaling_factor: float, prior_root_box: BoundingBox) -> None:
        if (scaling_factor > 1.0):
            logger.error("Can't scale up {} without additional checks, because then this element might exceed parent bounding box. Aborting scaling!"
                         .format(self.name))
            return
        for child in self.children:
            child.scale_by(scaling_factor, prior_root_box)
        local_offset: Vector = self.global_bounding_box.offsets - prior_root_box.offsets
        self.global_bounding_box.dimensions *= scaling_factor
        self.global_bounding_box.offsets = prior_root_box.offsets + local_offset*scaling_factor
        if not self.content:
            return        
        self.content = pygame.transform.scale_by(self.content, scaling_factor)
        

def build_frame_tree_from_ratios(name: str, parent_box: BoundingBox, dimension_ratios: Vector, 
                                   offset_ratios: Vector = Vector(0,0)) -> FrameTree:
    dimensions: Vector = Vector(
        parent_box.dimensions[0] * dimension_ratios[0], 
        parent_box.dimensions[1] * dimension_ratios[1])
    offsets: Vector = Vector(
        parent_box.offsets[0] + parent_box.dimensions[0] * (offset_ratios[0]), 
        parent_box.offsets[1] + parent_box.dimensions[1] * (offset_ratios[1]))
    return FrameTree(name, dimensions, offsets)


