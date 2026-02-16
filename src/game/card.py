from __future__ import annotations
from game.capabilities import IActiveGameElement
from uuid import UUID, uuid4
from game import constants as const

SEPERATOR: str = " -- "

class CardInstance(IActiveGameElement):
    def __init__(self, card_id: int, zone : str=const.LIBRARY) -> None:
        self.instance_id: UUID = uuid4()
        self.card_id: int = card_id
        self.zone: str = zone

        self.card_info: CardInfo = CARD_CATALOG[card_id]
        self.tapped: bool = False

    def get_id(self) -> UUID:
        return self.instance_id
    
    def get_zone(self) -> str:
        return self.zone

    def __str__(self, verbose: bool=False) -> str:
        if(verbose):
            return "[{}] {}".format(self.card_id, str(self.card_info))
        else:
            return "[{}] {}".format(self.card_id, self.card_info.name)

class CardInfo:
    def __init__(self, name: str) -> None:
        self.type: str = "UnknownType"
        self.name: str = name
    def __str__(self) -> str:
        return SEPERATOR.join([
            "Name: " + self.name,
            "Type: " + self.type
        ])
    
class SpellInfo(CardInfo):
    def __init__(self, name:str, mana_value: int):
        super().__init__(name)
        self.mana_value = mana_value
    def __str__(self) -> str:
        return SEPERATOR.join([
            super().__str__(),
            "MV: " + str(self.mana_value)
        ])
    
class CreatureInfo(SpellInfo):
    def __init__(self, name: str, mana_value: int, power: int, thoughness: int):
        super().__init__(name, mana_value)
        self.type: str = "Creature"
        self.power: int = power
        self.toughness: int =  thoughness
    def __str__(self) -> str:
        return SEPERATOR.join([
            super().__str__(),
            "Pow/Toug: " + str(self.power) + "/" + str(self.toughness) 
        ])

class LandInfo(CardInfo):
    def __init__(self, name: str):
        super().__init__(name)
        self.type: str = "Land"




CARD_CATALOG: dict[int, CardInfo] = {
    1: CreatureInfo("Guy", 1, 1, 1),
    2: LandInfo("Land"),
    3: CreatureInfo("StrongGuy", 3, 3, 3)
}

    
    


    