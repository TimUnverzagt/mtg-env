from __future__ import annotations

class Card:
    def __init__(self, id: int) -> None:
        self.id: int = id
        self.card_info: CardInfo = CARD_CATALOG[id]

    def __str__(self, verbose: bool=False) -> str:
        if(verbose):
            return "[{}] {}".format(self.id, str(self.card_info))
        else:
            return "[{}] {}".format(self.id, self.card_info.name)

class CardInfo:
    def __init__(self, name: str) -> None:
        self.name: str = name
        self.mana_value: int = 1
        self.power: int = 1
    
    def __str__(self) -> str:
        return " -- ".join([
            self.name,
            "({})".format(self.mana_value),
            "{}/X".format(self.power)
        ])



CARD_CATALOG: dict[int, CardInfo] = {
    1: CardInfo("Guy"),
    2: CardInfo("Land"),
    3: CardInfo("StrongGuy")
}

    
    


    