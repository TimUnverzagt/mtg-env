from enum import Enum
from typing import TypeAlias, Union


class InternalAgentType(Enum):
    GOLDFISH = 0
    MONKEY = 1
    RULESBASED = 2

class ExternalAgentType(Enum):
    CONSOLE = 0
    API = 1

AgentType: TypeAlias = Union[InternalAgentType, ExternalAgentType]