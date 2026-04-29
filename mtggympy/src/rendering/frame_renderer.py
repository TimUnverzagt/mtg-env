import pygame 
from pygame import Surface
from rendering.frame_tree import FrameTree
from logging_config import ui_log as logger

class FrameRenderer:

    def __init__(self, frame_tree: FrameTree) -> None:
        self.frame_tree = frame_tree
        self.screen: Surface = pygame.display.set_mode((frame_tree.bounding_box.width, frame_tree.bounding_box.height))
        self._render_frame(self.frame_tree)
        pygame.display.flip()
        logger.debug("Vizualisation is ready.")

    def _render_frame(self, current_tree: FrameTree) -> None:
        if(current_tree.content):
            self.screen.blit(current_tree.content, (current_tree.bounding_box.horizontal_offset, current_tree.bounding_box.vertical_offset))
        for child in current_tree.children:
            self._render_frame(child)
        return