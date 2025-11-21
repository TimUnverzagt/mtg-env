from environment.base import BaseEnvironment as MtgEnv

def main():
    """ Main program """
    env: MtgEnv = MtgEnv()
    print("Starting Environment:")
    print(env)
    env.pass_turn()
    print(25*"-")
    print("Environment Turn 2:")
    print(env)
    env.pass_turn()
    print(25*"-")
    print("Environment Turn 3:")
    print(env)
    return 0

if __name__ == "__main__":
    main()