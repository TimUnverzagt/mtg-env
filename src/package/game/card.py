from game.card_info import CardInfo
import game.constants as const

class Card:
    def __init__(self, id: int) -> None:
        self.id: int = id
        self.card_info: CardInfo = const.CARD_CATALOG[id]

    def __str__(self, verbose: bool=False) -> str:
        if(verbose):
            return "[{}] {}".format(self.id, str(self.card_info))
        else:
            return "[{}] {}".format(self.id, self.card_info.name)


    
    


    