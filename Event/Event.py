from abc import ABC, abstractmethod

class Event(ABC):
    @abstractmethod
    def subscribe(self, eventListener):
        pass
    
    @abstractmethod
    def unsubscribe(self, eventListener):
        pass
    
    @abstractmethod
    def dispatch(self):
        pass
    
    @abstractmethod
    def dispatchError(self):
        pass