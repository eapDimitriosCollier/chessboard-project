from abc import ABC, abstractmethod
from Event.Event import Event

class EventListener(ABC):
    @abstractmethod
    def onEvent(self, event: Event):
        pass
    
    @abstractmethod
    def onErrorEvent(self, event: Event):
        pass