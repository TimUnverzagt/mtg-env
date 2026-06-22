from mtggympy.gameengine.state.event import event_from_step
from mtggympy.gameengine.state.core import GameState, PlayerState
from mtggympy.server.session.observed_state import ObservedGameState, ObservedSelfState, ObservedOpponentState


def observe_game_state(game_state:GameState, seat_of_observer: int) -> ObservedGameState:
    self_state: PlayerState = game_state.player_states[seat_of_observer]
    self_obs: ObservedSelfState = ObservedSelfState(
        name=self_state.name,
        current_life=self_state.current_life,
        cards_in_library=len(self_state.cards_in_library),
        cards_in_hand=self_state.cards_in_hand,
        cards_in_play=self_state.cards_in_play,
        floating_mana=self_state.floating_mana        
    )
    opponent_obs: list[ObservedOpponentState] = []
    number_of_seats: int = len(game_state.player_states)
    for n in range(1, number_of_seats):
        opp_index: int = (seat_of_observer + n) % number_of_seats
        opp_state: PlayerState = game_state.player_states[opp_index]
        opp_obs: ObservedOpponentState = ObservedOpponentState(
            name=opp_state.name,
            current_life=opp_state.current_life,
            cards_in_library=len(opp_state.cards_in_library),
            cards_in_hand=len(opp_state.cards_in_hand),
            cards_in_play=opp_state.cards_in_play,
            floating_mana=opp_state.floating_mana
        )
        opponent_obs.append(opp_obs)

    return ObservedGameState(
        name_of_active_player=game_state.player_states[game_state.active_player_index].name,
        halfturns_completed=game_state.halfturns_completed,
        lands_played_this_turn=game_state.lands_played_this_turn,
        opponent_states=opponent_obs,
        self_is_active_player=(seat_of_observer == game_state.active_player_index),
        self_state=self_obs,
        step=game_state.step,
        event=event_from_step(game_state.step)
    )

