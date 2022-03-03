class Request():
    _requestListeners: list = []

    def __init__(self) -> None:
        self._type = ''
        self._args = None
    
    def subscribe(self, requestListener) -> None:
        Request._requestListeners.append(requestListener)
    
    def unsubscribe(self, requestListener) -> None:
        Request._requestListeners.remove(requestListener)
        
    def dispatch(self) -> None:
        for requestListener in Request._requestListeners:
            requestListener.onRequest(self)