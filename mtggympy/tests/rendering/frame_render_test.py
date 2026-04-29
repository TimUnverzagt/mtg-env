import unittest
from rendering.frame_renderer import FrameRenderer
from rendering.frame_tree import FrameTree
import rendering.ui_state as ui

class FrameRendererTest(unittest.TestCase):

    def test_background_rendering(self):
        #Prepare
        base_tree: FrameTree = ui.build_new_visualisation_tree()
        
        #Execute 
        renderer: FrameRenderer = FrameRenderer(base_tree)

        #Assert
        self.assertTrue(renderer)