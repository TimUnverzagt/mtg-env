import unittest
from mtggympy.gui.layout.custom.frames.frame_renderer import FrameRenderer
from mtggympy.gameengine.state import GameState
from mtggympy.gameengine.gameobjects import CardInstance
from mtggympy.gameengine.cards.catalog.creatures import CreatureNames as CreatureNames
from tests.default_data import get_default_game_state
#from logging_config import ui_log as logger

class FrameRendererTest(unittest.TestCase):

    def test_basic_rendering(self):
        #Prepare
        renderer: FrameRenderer = FrameRenderer()
        game_state: GameState = get_default_game_state()
        game_state.player_infos[0].cards_in_hand.pop()
        game_state.player_infos[0].cards_in_hand.append(CardInstance(CreatureNames.SLIVER_CONSTRUCT.value))
        #logger.info("Testing logger")
        
        #Execute 
        renderer.render_state(game_state)

        #Assert
        self.assertTrue(renderer)