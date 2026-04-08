from __future__ import annotations
from gameengine.constants import CardType

SEPERATOR: str = " -- "

class CardInfo:
    def __init__(self, name: str) -> None:
        self.type: CardType = CardType.UNKNOWN
        self.name: str = name
    def __str__(self) -> str:
        return SEPERATOR.join([
            "Name: " + self.name,
            "Type: " + str(self.type)
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
        self.type: CardType = CardType.CREATURE
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
        self.type: CardType = CardType.LAND

    
    


    