from abc import ABC, abstractmethod
from Interpreter.Response.Response import Response

class ResponseListener(ABC):
    @abstractmethod
    def onResponse(self, response: Response):
        pass
    
    @abstractmethod
    def onErrorResponse(self, response: Response):
        pass
