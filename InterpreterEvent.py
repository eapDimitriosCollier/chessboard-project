from EventListener import EventListener
from Event import Event

class InterpreterEvent(Event):
    _eventListeners: list = []
      
    # START_INTEPRETATION
    # END_INTEPRETATION
    _state: str = ''
    
    def subscribe(self, eventListener: EventListener) -> None:
        InterpreterEvent._eventListeners.append(eventListener)
    
    def unsubscribe(self, eventListener: EventListener) -> None:
        InterpreterEvent._eventListeners.remove(eventListener)
        
    def dispatch(self) -> None:
        for eventListener in InterpreterEvent._eventListeners:
            eventListener.onEvent(self)
    
    def startInterpretation(self):
        self._state = "START_INTERPRETATION"
        self.dispatch()
    
    def endInterpretation(self):
        self._state = "END_INTERPRETATION"
        self.dispatch()   
