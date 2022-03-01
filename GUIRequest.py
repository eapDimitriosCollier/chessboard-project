from EventListener import EventListener
from Event import Event

class GUIRequest(Event):
    _eventListeners: list = []

    _request: str = ''
    _args: list = []
    
    def subscribe(self, eventListener: EventListener) -> None:
        GUIRequest._eventListeners.append(eventListener)
    
    def unsubscribe(self, eventListener: EventListener) -> None:
        GUIRequest._eventListeners.remove(eventListener)
        
    def dispatch(self) -> None:
        for eventListener in GUIRequest._eventListeners:
            eventListener.onEvent(self)
    
    def getGames(self):
        self._request = "GET_GAMES"
        self._args = []
        self.dispatch()

    def getTags(self, gameUUID):
        self._request = "GET_TAGS"
        self._args = gameUUID
        self.dispatch()