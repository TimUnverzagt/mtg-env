class Player:

    def __init__(self, name: str) -> None:
        print("Setting up new player.")
        self.name: str = name
        self.current_life: int = 5
        self.cards_in_hand: list[str] = ["SomeCard", "SomeCard", "SomeCard"]
        self.cards_in_library: int = 10
        print("Welcome Player {}".format(self.name))

    def __str__(self) -> str:
        return "\n".join([
            "Name: {}".format(self.name),
            "Current Life: {}".format(self.current_life),
            "Cards in Hand: {}".format(" | ".join(self.cards_in_hand)),
            "Cards in Library: {}".format(self.cards_in_library)
        ])