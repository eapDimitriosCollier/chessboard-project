from RequestListener.RequestListener import RequestListener
from Request.Request import Request

class Response():
    _requestListeners: list = []
    
    def __init__(self) -> None:
        self._response = None
        self._request : Request = None
    
    def subscribe(self, requestListener: RequestListener) -> None:
        self._requestListeners.append(requestListener)
    
    def unsubscribe(self, requestListener: RequestListener) -> None:
        self._requestListeners.remove(requestListener)
        
    def dispatch(self) -> None:
        for requestListener in self._requestListeners:
            requestListener.onResponse(self)
    
    def dispatchError(self) -> None:
        for requestListener in self._requestListeners:
            requestListener.onErrorResponse(self)
    
    def sendResponse(self, request: Request, response):
        self._request = request
        self._response = response
        self.dispatch()
    
    def sendErrorResponse(self, request: Request, response) -> None:
        self._request = request
        self._response = response
        self.dispatchError()        
        
        