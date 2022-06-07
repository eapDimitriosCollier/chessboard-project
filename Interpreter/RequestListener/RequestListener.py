from abc import ABC, abstractmethod
from Interpreter.Request.Request import Request

class RequestListener(ABC):
    @abstractmethod
    def onRequest(self, request: Request):
        pass