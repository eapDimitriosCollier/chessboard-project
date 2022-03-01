from abc import ABC, abstractmethod
from Event import Event

class EventListener(ABC):
    @abstractmethod
    def onEvent(self, event: Event):
        pass