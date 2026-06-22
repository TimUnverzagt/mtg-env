
from mtggympy.gameengine.constants import CardType
from mtggympy.gameengine.cards.logic.instances import CardInstance, CreatureInstance
from mtggympy.gameengine.state.event import ActionIntent
from mtggympy.gameengine.state.core import GameState

from mtggympy.logging_config import engine_log as logger

import numpy as np

def collection_to_numpy(collection_args: list[list[int]]) -> np.ndarray:
    intent_array: np.ndarray = np.array(collection_args)
    print(intent_array)
    print(intent_array.shape)
    return np.array(collection_args)


def card_for_playing(acting_seat: int, intent: ActionIntent, game_state: GameState) -> CardInstance | None:
    if(intent.parameters is None):
        logger.error("{}: Arguments are missing. Refusing to process intent!".format(intent.action.name))
        return None
    if(intent.parameters.size != 1):
        logger.error("{}: More than one argument. Refusing to process intent!".format(intent.action.name))
        return None
    card_index: int = intent.parameters.sum() # This colapses various shapes
    if(card_index >= len(game_state.player_states[acting_seat].cards_in_hand)):
        logger.error("{}: No card at given position. Refusing to process intent!".format(intent.action.name))
        return None
    return game_state.player_states[acting_seat].cards_in_hand[card_index]

def lands_for_activation(acting_seat: int, intent: ActionIntent, game_state: GameState) -> list[CardInstance] | None:
    if(intent.parameters is None):
        logger.error("{}: Arguments are missing. Refusing to process intent!".format(intent.action.name))
        return None
    if((len(intent.parameters.shape) < 2) or (intent.parameters.shape[1] != 1)):
        logger.error("{}: Arguments have wrong size. Refusing to process intent!".format(intent.action.name))
        return None
    lands: list[CardInstance] = list(filter(lambda card: card.type is CardType.LAND ,game_state.player_states[acting_seat].cards_in_play))
    target_lands: list[CardInstance] = []
    for index in intent.parameters:
        if (index >= len(lands)):
            logger.error("{}: No card at given position. Refusing to process intent!".format(intent.action.name))
            return None
        target_lands.append(lands[int(index[0])])
    return target_lands
    
def creatures_for_attacking(acting_seat: int, intent: ActionIntent, game_state: GameState) -> list[CreatureInstance] | None:
    if(intent.parameters is None):
        logger.error("{}: Arguments are missing. Refusing to process intent!".format(intent.action.name))
        return None
    if((len(intent.parameters.shape) < 2) or (intent.parameters.shape[1] != 1)):
        logger.error("{}: Arguments have wrong size. Refusing to process intent!".format(intent.action.name))
        return None
    nonlands: list[CardInstance] = list(filter(lambda card: card.type is not CardType.LAND ,game_state.player_states[acting_seat].cards_in_play))
    target_creatures: list[CreatureInstance] = []
    for index in intent.parameters:
        if (index >= len(nonlands)):
            logger.error("{}: No card at given position. Refusing to process intent!".format(intent.action.name))
            return None
        target_card: CardInstance = nonlands[int(index[0])]
        if isinstance(target_card, CreatureInstance):
            target_creatures.append(target_card)
        else:
            logger.error("{}: Card at position is not a creature. Refusing to process intent!".format(intent.action.name))
    return target_creatures