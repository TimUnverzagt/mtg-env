
from pygame import Surface
from pygame import Vector2 as Vector
from typing import Optional

import rendering.bounding_box as BoxFunctions
from rendering.frame_tree import FrameTree
from rendering.bounding_box import BoundingBox

def build_padded_frame_in_place(inner_frame: FrameTree, parent: FrameTree, padding_background: Optional[Surface],
                       x_start_padding: float, x_end_padding: float,
                       y_start_padding: float, y_end_padding: float) -> FrameTree:
    prior_box: BoundingBox = BoundingBox(
        Vector(inner_frame.global_bounding_box.dimensions[0], inner_frame.global_bounding_box.dimensions[1]),
        Vector(inner_frame.global_bounding_box.offsets[0], inner_frame.global_bounding_box.offsets[1])
    )
    dimensions: Vector = Vector(
        inner_frame.global_bounding_box.dimensions[0] + x_start_padding + x_end_padding,
        inner_frame.global_bounding_box.dimensions[1] + y_start_padding + y_end_padding
    )
    offsets: Vector = Vector(
        inner_frame.global_bounding_box.offsets[0],
        inner_frame.global_bounding_box.offsets[1]
    )
    padded_frame: FrameTree = FrameTree(inner_frame.name + "-padding", dimensions, offsets)
    inner_frame.global_bounding_box.offsets[0] += x_start_padding
    inner_frame.global_bounding_box.offsets[1] += y_start_padding
    padded_frame.add_child(inner_frame)
    frame_scaling: float = BoxFunctions.get_scaling_to_fit_first_box_to_second(padded_frame.global_bounding_box, inner_frame.global_bounding_box)
    padded_frame.scale_by(frame_scaling, prior_box, parent)
    padded_frame.set_content(padding_background)
    return padded_frame
