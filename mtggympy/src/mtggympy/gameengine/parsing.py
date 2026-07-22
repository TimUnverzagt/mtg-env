
from mtggympy.gameengine.constants import CardType
from mtggympy.gameengine.cards.instances.types import CardInstance, CreatureInstance
from mtggympy.gameengine.state.event import ActionIntent
from mtggympy.gameengine.state.core import GameState

from mtggympy.config.logging_config import engine_log as logger

import numpy as np

def collection_to_numpy(collection_args: list[list[int]]) -> np.ndarray:
    intent_array: np.ndarray = np.array(collection_args)
    return np.array(intent_array)


def card_for_playing(acting_seat: int, intent: ActionIntent, game_state: GameState) -> CardInstance | None:
    if(intent.parameters is None):
        logger.error("{}: Parsing: Arguments are missing. Refusing to process intent!".format(intent.action.name))
        return None
    if(intent.parameters.size != 1):
        logger.error("{}: Parsing: More than one argument. Refusing to process intent!".format(intent.action.name))
        return None
    card_index: int = intent.parameters.sum() # This colapses various shapes
    if(card_index >= len(game_state.player_states[acting_seat].cards_in_hand)):
        logger.error("{}: Parsing: No card at position {}. Refusing to process intent!".format(intent.action.name, card_index))
        return None
    return game_state.player_states[acting_seat].cards_in_hand[card_index]

def lands_for_activation(acting_seat: int, intent: ActionIntent, game_state: GameState) -> list[CardInstance] | None:
    if(intent.parameters is None):
        logger.error("{}: Parsing: Arguments are missing. Refusing to process intent!".format(intent.action.name))
        return None
    if((len(intent.parameters.shape) < 2) or (intent.parameters.shape[1] != 1)):
        logger.error("{}: Parsing: Arguments have wrong size. Refusing to process intent!".format(intent.action.name))
        return None
    lands: list[CardInstance] = list(filter(lambda card: card.type is CardType.LAND ,game_state.player_states[acting_seat].cards_in_play))
    target_lands: list[CardInstance] = []
    for index in intent.parameters:
        if (index >= len(lands)):
            logger.error("{}: Parsing: No card at given position {}. Refusing to process intent!".format(intent.action.name, index))
            return None
        target_lands.append(lands[int(index[0])])
    return target_lands

def creatures_for_attacking(acting_seat: int, intent: ActionIntent, game_state: GameState) -> list[CreatureInstance] | None:
    if(intent.parameters is None):
        logger.error("{}: Parsing: Arguments are missing. Refusing to process intent!".format(intent.action.name))
        return None
    if((len(intent.parameters.shape) < 2) or (intent.parameters.shape[1] != 1)):
        logger.error("{}: Parsing: Arguments have wrong size. Refusing to process intent!".format(intent.action.name))
        return None
    nonlands: list[CardInstance] = list(filter(lambda card: card.type is not CardType.LAND ,game_state.player_states[acting_seat].cards_in_play))
    target_creatures: list[CreatureInstance] = []
    for index in intent.parameters:
        if (index >= len(nonlands)):
            logger.error("{}: Parsing: No card at position {}. Refusing to process intent!".format(intent.action.name, index))
            return None
        target_card: CardInstance = nonlands[int(index[0])]
        if isinstance(target_card, CreatureInstance):
            target_creatures.append(target_card)
        else:
            logger.error("{}: Parsing: Card at position {} is not a creature. Refusing to process intent!".format(intent.action.name, index))
    return target_creatures

    
def blocker_attacker_pairs(acting_seat: int, intent: ActionIntent, game_state: GameState) -> list[tuple[CreatureInstance, CreatureInstance]] | None:
    if(intent.parameters is None):
        logger.error("{}: Parsing: Arguments are missing. Refusing to process intent!".format(intent.action.name))
        return None
    if((len(intent.parameters.shape) < 2) or (intent.parameters.shape[1] != 2)):
        logger.error("{}: Parsing: Arguments have wrong size. Refusing to process intent!".format(intent.action.name))
        return None
    # attacker is active player because you can only attack on your own turn
    attacker_nonlands: list[CardInstance] = list(filter(lambda card: card.type is not CardType.LAND, game_state.player_states[game_state.active_player_index].cards_in_play))
    # blocker is acting player because they input how to block
    blocker_nonlands: list[CardInstance] = list(filter(lambda card: card.type is not CardType.LAND, game_state.player_states[acting_seat].cards_in_play))
    pairs: list[tuple[CreatureInstance, CreatureInstance]] = []
    for pair_index in intent.parameters:
        blocker_index: int = pair_index[0]
        attacker_index: int = pair_index[1]
        if (blocker_index >= len(blocker_nonlands)):
            logger.error("{}: Parsing: No card at position {} for blocker. Refusing to process intent!".format(intent.action.name, blocker_index))
            return None
        if (attacker_index >= len(attacker_nonlands)):
            logger.error("{}: Parsing: No card at position {} for attacker. Refusing to process intent!".format(intent.action.name, attacker_index))
            return None
        attacking_card: CardInstance = attacker_nonlands[int(attacker_index)]
        blocking_card: CardInstance = blocker_nonlands[int(blocker_index)]
        if not isinstance(attacking_card, CreatureInstance):
            logger.error("{}: Parsing: Card at attacker position {} is not a creature. Refusing to process intent!".format(intent.action.name, attacker_index))
            return
        if not isinstance(blocking_card, CreatureInstance):
            logger.error("{}: Parsing: Card at blocker position {} is not a creature. Refusing to process intent!".format(intent.action.name, attacker_index))
            return
        pairs.append((blocking_card, attacking_card))
    return pairs