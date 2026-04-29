import unittest
from rendering.frame_tree import FrameTree
import rendering.ui_state as ui

class UiStateTest(unittest.TestCase):

    def test_tree_setup(self):
        #Execute
        base_tree: FrameTree = ui.build_new_visualisation_tree()

        #Assert
        self.assertTrue(base_tree.children)
        self.assertEqual(len(base_tree.children), 2)