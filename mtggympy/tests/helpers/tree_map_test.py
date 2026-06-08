import unittest
from mtggympy.helpers.typing_extensions import Tree
from mtggympy.helpers.tree_map import tree_map

class TestTreeMap(unittest.TestCase):

    def test_tree_min(self):
        #Setup
        t1: Tree[int] = (1, (2, 3, 4), 5)
        t2: Tree[int] = (5, (4, 3, 2), 1)

        #Execute
        res: Tree[int] = tree_map(min, t1, t2)

        #Assert
        self.assertEqual(res, (1,(2,3,2),1))
