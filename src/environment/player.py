class Player:
    name: str
    current_life: int
    cards_in_hand: list[str]
    cards_in_library: int

    def __init__(self, name: str) -> None:
        print("Setting up new player.")
        self.name = name
        self.current_life = 5
        self.cards_in_hand = ["SomeCard", "SomeCard", "SomeCard"]
        self.cards_in_library = 10
        print("Welcome Player {}".format(self.name))

    def __str__(self) -> str:
        return "\n".join([
            "Name: {}".format(self.name),
            "Current Life: {}".format(self.current_life),
            "Cards in Hand: {}".format(" | ".join(self.cards_in_hand)),
            "Cards in Library: {}".format(self.cards_in_library)
        ])