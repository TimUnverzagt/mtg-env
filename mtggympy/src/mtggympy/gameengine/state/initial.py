

from mtggympy.config.defaults import Player
from mtggympy.gameengine.constants import GameStep
from mtggympy.gameengine.state.core import GameState
from mtggympy.gameengine.transition import draw_card, shuffle_cards


def get_initial_game_state() -> GameState:
    player1: Player = Player("Player1")
    shuffle_cards(player1.info.cards_in_library)
    player2: Player = Player("Player2")
    shuffle_cards(player2.info.cards_in_library)
    game_state: GameState = GameState(
        halfturns_completed = 0,
        active_player_index = 0,
        game_over = False,
        step=GameStep.UPKEEP,
        player_states = [player1.info, player2.info],
        winner_positions=[],
        lands_played_this_turn=0
    )
    for _ in range(0,7):
        draw_card(0, game_state)
        draw_card(1, game_state)
    return game_state