from environment.card_info import CardInfo

class Card:
    card_catalog: dict[int, CardInfo] = {
        1: CardInfo("Card1"),
        2: CardInfo("Card11"),
        3: CardInfo("Card111")
    }

    def __init__(self, id: int) -> None:
        self.id: int = id
        self.card_info = Card.card_catalog[id]

    def __str__(self, verbose: bool=False) -> str:
        if(verbose):
            return "{}[{}]".format(self.id, str(self.card_info))
        else:
            return "{}[{}]".format(self.id, self.card_info.name)


    
    


    