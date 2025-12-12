class DecisionEvent:

    def __init__(self, name: str, neutral_action_index: int, possible_actions: list [str]) -> None:
        self.name: str = name
        self.neutral_action_index: int = neutral_action_index
        self.possible_actions: list [str] =  possible_actions

    def __str__(self) -> str:
        return "{}: <{}>".format(self.name, ",".join(self.possible_actions))