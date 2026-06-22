from queue import Queue
from mtggympy.gameengine.state.event import ActionIntent


DESKTOP_INTENT_QUEUE: Queue[ActionIntent] = Queue()