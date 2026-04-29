import pygame
from pygame import Surface
import os

from rendering.frame_tree import FrameTree, build_texture_tree_from_ratios
from app_config import ROOT_DIR

WINDOW_WIDTH: int = 1920
WINDOW_HEIGHT: int = 1080

def build_background_surface() -> Surface:
    surface: Surface = pygame.image.load(os.path.join(ROOT_DIR, 'assets', 'battle-background.png'))
    return surface

def build_new_visualisation_tree() -> FrameTree:
    background_frame: FrameTree = FrameTree(WINDOW_WIDTH, WINDOW_HEIGHT)
    background_frame.set_content(build_background_surface())
    player_1_frame: FrameTree = build_texture_tree_from_ratios(background_frame.bounding_box, 1.0, 0.5)
    background_frame.add_child(player_1_frame)
    player_2_frame: FrameTree = build_texture_tree_from_ratios(background_frame.bounding_box, 1.0, 0.5, vertical_offset_r=0.5)
    background_frame.add_child(player_2_frame)
    return background_frame