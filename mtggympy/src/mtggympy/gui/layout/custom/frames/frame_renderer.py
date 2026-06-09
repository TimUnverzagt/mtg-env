import pygame 
from pygame import Surface
from mtggympy.gui.layout.custom.frames.frame_tree import FrameTree
import mtggympy.gui.layout.custom.composition as Composition
from mtggympy.gameengine.state import GameState
from mtggympy.logging_config import ui_log as logger

WINDOW_WIDTH: int = 1920
WINDOW_HEIGHT: int = 1080

class FrameRenderer:

    def __init__(self) -> None:
        pygame.init()
        self.screen: Surface = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
        logger.debug("Vizualisation is ready.")

    def render_state(self, game_state:GameState) -> None:
        frame_tree: FrameTree = Composition.build_full_frame(game_state, WINDOW_WIDTH, WINDOW_HEIGHT)
        self._render_frame(frame_tree)
        pygame.display.flip()

    def _render_frame(self, current_tree: FrameTree) -> None:
        if(current_tree.content):
            self.screen.blit(current_tree.content, current_tree.global_bounding_box.offsets)
        for child in current_tree.children:
            self._render_frame(child)
        return