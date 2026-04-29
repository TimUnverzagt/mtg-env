from dataclasses import dataclass


@dataclass
class BoundingBox:
        width: int
        height: int
        horizontal_offset: int
        vertical_offset: int

def get_horizontal_spread(box: BoundingBox) -> tuple[int, int]:
      return (box.horizontal_offset, box.horizontal_offset + box.width)

def get_vertical_spread(box: BoundingBox) -> tuple[int, int]:
      return (box.vertical_offset, box.vertical_offset + box.height)

def are_intervals_seperable(first_interval: tuple[int, int], second_interval: tuple[int,int]) -> bool:
      are_seperable: bool = False
      are_seperable |= (max(first_interval) <= min(second_interval))
      are_seperable |= (min(first_interval) >= max(second_interval))
      return not are_seperable

def do_bounding_boxes_collide(first_box: BoundingBox, second_box: BoundingBox) -> bool:
    are_seperable: bool = False
    are_seperable |= are_intervals_seperable(get_horizontal_spread(first_box), get_horizontal_spread(second_box))
    are_seperable |= are_intervals_seperable(get_vertical_spread(first_box), get_vertical_spread(second_box))
    return not are_seperable

def does_first_interval_fit_into_second(first_interval: tuple[int, int], second_interval: tuple[int,int]) -> bool:
    fits: bool = True
    fits &= (max(first_interval) <= max(second_interval))
    fits &= (min(first_interval) >= min(second_interval))
    return fits


def does_first_box_fit_into_second(first_box: BoundingBox, second_box: BoundingBox) -> bool:
    fits: bool = True
    fits &= does_first_interval_fit_into_second(get_horizontal_spread(first_box), get_horizontal_spread(second_box))
    fits &= does_first_interval_fit_into_second(get_vertical_spread(first_box), get_vertical_spread(second_box))
    return fits
