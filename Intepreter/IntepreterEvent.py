from EventListener import EventListener
from Event import Event

class IntepreterEvent(Event):
    _eventListeners: list[EventListener]
      
    # START_INTEPRETTING
    # END_INTEPRETTING
    _type: str
    
    def subscribe(self, eventListener: EventListener):
        self._eventListeners.append(eventListener)
    
    def unsubscribe(self, eventListener: EventListener):
        self._eventListeners.remove(eventListener)
    