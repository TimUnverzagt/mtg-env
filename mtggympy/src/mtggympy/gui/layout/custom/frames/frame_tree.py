from __future__ import annotations
import math
import pygame
from pygame import Surface
from pygame import Vector2 as Vector
from typing import Optional

from mtggympy.logging_config import ui_log as logger
from mtggympy.gui.layout.custom.bounding_box import BoundingBox, do_bounding_boxes_collide, does_first_box_fit_into_second

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

    def child_exceeds_bounding_box(self, child_box: BoundingBox) -> bool:
        return not does_first_box_fit_into_second(child_box, self.global_bounding_box)
    
    def child_collides_with_other_children(self, child_box: BoundingBox, child_name: str) -> bool:
        does_collide_with_any: bool = False
        for prior_child in self.children:
            if(child_name ==  prior_child.name):
                continue
            does_collide_with_any |= do_bounding_boxes_collide(
                child_box, 
                prior_child.global_bounding_box)
        return does_collide_with_any
    
    def is_new_child_position_valid(self, child_box: BoundingBox, child_name: str, error_prefix: str) -> bool:
        if (self.child_exceeds_bounding_box(child_box)):
            logger.error("{} child bounding box exceeds parent bounding box".format(error_prefix))
            logger.info("Parent {}: {}".format(self.name, self.global_bounding_box))
            logger.info("Child {}: {}".format(child_name, child_box))
            return False
    
        if (self.child_collides_with_other_children(child_box, child_name)):
            logger.info("{} child bounding box collides with other child".format(error_prefix))
            logger.info("Parent {}: {}".format(self.name, self.global_bounding_box))
            logger.info("Child {}: {}".format(child_name, child_box))
            for prev_child in self.children:
                logger.info("Prior child {}: {}".format(prev_child.name,prev_child.global_bounding_box))
                return False
        return True


    def add_child(self, child: FrameTree) -> None:
        error_prefix: str = "Can't add child {} to {} TextureTree:".format(child.name, self.name)
        if not self.is_new_child_position_valid(child.global_bounding_box, child.name, error_prefix):
            logger.warning("Aborting child addition!")
        self.children.append(child)

    def set_content(self, new_content: Optional[Surface]) -> None:
        if not new_content:
            return
        target_dimensons: Vector = self.global_bounding_box.dimensions
        self.content = pygame.transform.scale(new_content, (target_dimensons[0], target_dimensons[1]))

    def scale_by(self, scaling_factor: float, root_box: BoundingBox, parent: FrameTree) -> None:
        local_offset: Vector = self.global_bounding_box.offsets - root_box.offsets
        new_bounding_box:BoundingBox = BoundingBox(
            self.global_bounding_box.dimensions * scaling_factor,
            root_box.offsets + local_offset*scaling_factor
        )
        error_prefix: str = "Can't scale tree {} inside {} by {}:".format(self.name, parent.name, scaling_factor)
        executing_properly: bool = parent.is_new_child_position_valid(new_bounding_box, self.name, error_prefix)
        self.global_bounding_box.dimensions *= scaling_factor
        self.global_bounding_box.offsets = root_box.offsets + local_offset*scaling_factor
        self.set_content(self.content)
        if (not executing_properly):
            return 
        if (scaling_factor < 1):
            for child in self.children:
                child.scale_by(scaling_factor, root_box, self)
        else:
            logger.info("Not propagating upscaling to children, because its messy.")
        

def build_frame_tree_from_ratios(name: str, parent_box: BoundingBox, dimension_ratios: Vector, 
                                   offset_ratios: Vector = Vector(0,0)) -> FrameTree:
    dimensions: Vector = Vector(
        parent_box.dimensions[0] * dimension_ratios[0], 
        parent_box.dimensions[1] * dimension_ratios[1])
    offsets: Vector = Vector(
        parent_box.offsets[0] + parent_box.dimensions[0] * (offset_ratios[0]), 
        parent_box.offsets[1] + parent_box.dimensions[1] * (offset_ratios[1]))
    return FrameTree(name, dimensions, offsets)


