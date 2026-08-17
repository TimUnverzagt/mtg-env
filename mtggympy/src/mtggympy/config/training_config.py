
from mtggympy.server.agents.constants import InternalAgentType


BATCH_SIZE = 128
GAMMA = 0.99
EPS_START = 0.9
EPS_END = 0.01
EPS_DECAY_ETIME_RATIO = 0.33
TAU = 0.005
LR = 3e-4
OPPONENT_TYPE: InternalAgentType = InternalAgentType.RULESBASED
AGENT_SEAT_POS: int = 0