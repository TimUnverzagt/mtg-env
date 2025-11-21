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