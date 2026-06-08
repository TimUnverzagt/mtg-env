from dataclasses import dataclass
from pygame import Vector2 as Vector


@dataclass
class BoundingBox:
    dimensions: Vector
    offsets: Vector

@dataclass
class MultiInterval:
    start: Vector
    end: Vector 

@dataclass
class SimpleInterval:
    start: float
    end: float

def get_interval_representation(box: BoundingBox) -> MultiInterval:
    return MultiInterval(box.offsets, box.offsets + box.dimensions)

def are_simple_intervals_seperable(first: SimpleInterval, second: SimpleInterval) -> bool:
    are_seperable: bool = False
    are_seperable |= (first.end <= second.start)
    are_seperable |= (first.start >= second.end)
    return are_seperable

def do_bounding_boxes_collide(first: BoundingBox, second: BoundingBox) -> bool:
    first_multi: MultiInterval = get_interval_representation(first)
    second_multi: MultiInterval = get_interval_representation(second)
    are_seperable: bool = False
    are_seperable |= are_simple_intervals_seperable(
        SimpleInterval(first_multi.start[0], first_multi.end[0]), 
        SimpleInterval(second_multi.start[0], second_multi.end[0])
        )
    are_seperable |= are_simple_intervals_seperable(
        SimpleInterval(first_multi.start[1], first_multi.end[1]), 
        SimpleInterval(second_multi.start[1], second_multi.end[1])
        )
    return not are_seperable

def does_first_simple_interval_fit_into_second(first: SimpleInterval, second: SimpleInterval) -> bool:
    fits: bool = True
    fits &= (first.end <= second.end)
    fits &= (first.start >= second.start)
    return fits

def does_first_box_fit_into_second(first: BoundingBox, second: BoundingBox) -> bool:
    first_multi: MultiInterval = get_interval_representation(first)
    second_multi: MultiInterval = get_interval_representation(second)
    fits: bool = True
    fits &= does_first_simple_interval_fit_into_second(
        SimpleInterval(first_multi.start[0], first_multi.end[0]), 
        SimpleInterval(second_multi.start[0], second_multi.end[0])
        )
    fits &= does_first_simple_interval_fit_into_second(
        SimpleInterval(first_multi.start[1], first_multi.end[1]), 
        SimpleInterval(second_multi.start[1], second_multi.end[1])
        )
    return fits

def get_scaling_to_fit_first_box_to_second(first: BoundingBox, second: BoundingBox) -> float:
    x_scaling: float =  second.dimensions[0] / first.dimensions[0]
    y_scaling: float =  second.dimensions[1] / first.dimensions[1]
    return min(x_scaling, y_scaling)
