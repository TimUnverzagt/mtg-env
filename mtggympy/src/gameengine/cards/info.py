from __future__ import annotations
from gameengine.constants import CardType, ManaColor

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
    def __init__(self, name:str, mana_cost: dict[ManaColor, int]):
        super().__init__(name)
        self.mana_cost = mana_cost
    def __str__(self) -> str:
        return SEPERATOR.join([
            super().__str__(),
            "MV: " + str(self.mana_cost)
        ])
    
class CreatureInfo(SpellInfo):
    def __init__(self, name: str, mana_cost: dict[ManaColor, int], power: int, thoughness: int):
        super().__init__(name, mana_cost)
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

    
    


    