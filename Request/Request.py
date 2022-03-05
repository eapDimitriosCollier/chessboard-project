from threading import Lock

class Request():
    _requestListeners: list = []
    _lock = Lock()
    
    def __init__(self) -> None:
        self._type = ''
        self._args = None
    
    def subscribe(self, requestListener) -> None:
        Request._lock.acquire()
        Request._requestListeners.append(requestListener)
        Request._lock.release()
    
    def unsubscribe(self, requestListener) -> None:
        Request._lock.acquire()
        Request._requestListeners.remove(requestListener)
        Request._lock.release()
        
    def dispatch(self) -> None:
        Request._lock.acquire()
        for requestListener in Request._requestListeners:
            requestListener.onRequest(self)
        Request._lock.release()   
