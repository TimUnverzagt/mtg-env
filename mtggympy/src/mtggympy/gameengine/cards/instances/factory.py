
from mtggympy.gameengine.cards.catalog import lookup
from mtggympy.gameengine.cards.catalog.info import CardInfo, CreatureInfo, LandInfo
from mtggympy.gameengine.cards.catalog.lands import LandNames
from mtggympy.gameengine.cards.instances import basics
from mtggympy.gameengine.cards.instances.types import CardInstance, CreatureInstance, LandInstance

from mtggympy.config.logging_config import engine_log as logger

def generate_card_instance(card_name: str) -> CardInstance:
    info: CardInfo | None =  lookup.card_info(card_name)
    if info is None:
        logger.error("Could not instatiate card for name \"{}\"".format(card_name))
        raise Exception
    #LANDS
    if card_name == LandNames.WASTES.value:
        return basics.WastesInstance()
    if card_name == LandNames.PLAINS.value:
        return basics.PlainsInstance()
    if card_name == LandNames.ISLAND.value:
        return basics.IslandInstance()
    if card_name == LandNames.SWAMP.value:
        return basics.SwampInstance()
    if card_name == LandNames.MOUNTAIN.value:
        return basics.MountainInstance()
    if card_name == LandNames.FOREST.value:
        return basics.ForestInstance()
    #CREATURES
    if isinstance(info, CreatureInfo):
        return CreatureInstance(info)
    if isinstance(info, LandInfo):
        return LandInstance(info)
    return CardInstance(info)