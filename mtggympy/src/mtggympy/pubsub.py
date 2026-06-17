from queue import Queue
from mtggympy.gameengine.priority.event import ActionIntent


DESKTOP_INTENT_QUEUE: Queue[ActionIntent] = Queue()