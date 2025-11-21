from environment.card import Card

class Player:

    def __init__(self, name: str) -> None:
        print("Setting up new player.")
        self.name: str = name
        self.current_life: int = 5
        self.cards_in_hand: list[Card] = [Card(1), Card(2), Card(1)]
        self.cards_in_library: int = 10
        print("Welcome Player {}".format(self.name))

    def __str__(self) -> str:
        return "\n".join([
            "Name: {}".format(self.name),
            "Current Life: {}".format(self.current_life),
            "Cards in Hand: {}".format(" | ".join(map(Card.__str__, self.cards_in_hand))),
            "Cards in Library: {}".format(self.cards_in_library)
        ])