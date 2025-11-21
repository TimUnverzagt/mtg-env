from environment.base import BaseEnvironment as MtgEnv
from environment.player import Player

def main():
    """ Main program """
    alice: Player = Player("Alice")
    bob: Player = Player("Bob")
    env: MtgEnv = MtgEnv([alice, bob])
    print(25*"-")
    print("Starting Environment:")
    print(env.step(alice, (0, "Pass")))
    print(25*"-")
    print(env.step(alice, (1, "Pass")))
    print(25*"-")
    print(env.step(bob, (0, "Pass")))
    return 0

if __name__ == "__main__":
    main()