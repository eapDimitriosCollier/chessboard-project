from Request.Request import Request
from threading import Lock

class Response():
    _responseListeners: list = []
    _lock = Lock()

    def __init__(self) -> None:
        self._response = None
        self._request : Request = None
    
    def subscribe(self, responseListener) -> None:
        Response._lock.acquire()
        Response._responseListeners.append(responseListener)
        Response._lock.release()
    
    def unsubscribe(self, responseListener) -> None:
        Response._lock.acquire()
        Response._responseListeners.remove(responseListener)
        Response._lock.release()
        
    def dispatch(self) -> None:
        Response._lock.acquire()
        for responseListener in self._responseListeners:
            responseListener.onResponse(self)
        Response._lock.release()
    
    def dispatchError(self) -> None:
        Response._lock.acquire()
        for responseListener in self._responseListeners:
            responseListener.onErrorResponse(self)
        Response._lock.release()
    
    def sendResponse(self, request: Request, response):
        self._request = request
        self._response = response
        self.dispatch()
    
    def sendErrorResponse(self, request: Request, response) -> None:
        self._request = request
        self._response = response
        self.dispatchError()        
        
        