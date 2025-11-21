from environment.base import BaseEnvironment as MtgEnv

def main():
    """ Main program """
    env: MtgEnv = MtgEnv()
    print("Current Environment:")
    print(env)
    return 0

if __name__ == "__main__":
    main()