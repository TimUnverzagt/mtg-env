class ActionEvent:

    def __init__(self, name: str, possible_actions: list [str]) -> None:
        self.name = name
        self.possible_actions =  possible_actions

    def __str__(self) -> str:
        return "{}: <{}>".format(self.name, ",".join(self.possible_actions))