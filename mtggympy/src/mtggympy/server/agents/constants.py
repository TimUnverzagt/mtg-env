from enum import Enum

class InternalAgentType(Enum):
    GOLDFISH = 0
    MONKEY = 1
    RULESBASED = 2

class ExternalAgentType(Enum):
    CONSOLE = 0
    API = 1