from EventListener import EventListener
from Event import Event

class InterpreterResponse(Event):
    _eventListeners: list = []
    _response = None
    
    def subscribe(self, eventListener: EventListener) -> None:
        InterpreterResponse._eventListeners.append(eventListener)
    
    def unsubscribe(self, eventListener: EventListener) -> None:
        InterpreterResponse._eventListeners.remove(eventListener)
        
    def dispatch(self) -> None:
        for eventListener in InterpreterResponse._eventListeners:
            eventListener.onEvent(self)
    
    def sendResponse(self, response):
        self._response = response
        self.dispatch()
