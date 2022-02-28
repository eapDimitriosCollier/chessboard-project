from abc import ABC, abstractmethod
from EventListener import EventListener

class Event(ABC):
    @abstractmethod
    def subscribe(self, eventListener: EventListener):
        pass
    
    @abstractmethod
    def unsubscribe(self, eventListener: EventListener):
        pass
    
    @abstractmethod
    def dispatch(self):
        pass