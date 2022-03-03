from EventListener.EventListener import EventListener
from Event.Event import Event
from threading import Lock


class InterpreterEvent(Event):
    """Thread safe Event για τον Interpreter"""
    # To lock θέλουμε να είναι ίδιο για κάθε instance του InterpreterEvent
    _lock = Lock()
    _eventListeners: list = []
    
    # Available flags:
    # START_INTEPRETATION
    # END_INTEPRETATION
    # ERROR
    _flag: str = ''
    _details = None
    
    def __init__(self):
        super().__init__()
    
    def subscribe(self, eventListener: EventListener) -> None:
        InterpreterEvent._lock.acquire()
        InterpreterEvent._eventListeners.append(eventListener)
        InterpreterEvent._lock.release()
        
    def unsubscribe(self, eventListener: EventListener) -> None:
        InterpreterEvent._lock.acquire()
        InterpreterEvent._eventListeners.remove(eventListener)
        InterpreterEvent._lock.release()
        
    def dispatch(self) -> None:
        for eventListener in InterpreterEvent._eventListeners:
            eventListener.onEvent(self)
          
    def dispatchError(self) -> None:
        for eventListener in InterpreterEvent._eventListeners:
            eventListener.onErrorEvent(self)
    
    def startInterpretation(self):
        InterpreterEvent._lock.acquire()
        self._flag = "START_INTERPRETATION"
        self.dispatch()
        InterpreterEvent._lock.release()  
    
    def endInterpretation(self):
        InterpreterEvent._lock.acquire()
        self._flag = "END_INTERPRETATION"
        self.dispatch()
        InterpreterEvent._lock.release()
    
    def interpretationFailed(self, details):
        InterpreterEvent._lock.acquire()
        self._flag = "ERROR"  
        self._details = details 
        self.dispatchError()
        InterpreterEvent._lock.release()
