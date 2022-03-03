from Lexer.Lexer import Lexer
from Parser.Parser import Parser
from InterpreterEvent import InterpreterEvent
from InterpreterResponse import InterpreterResponse
from GUIRequest import GUIRequest
from RequestListener.RequestListener import RequestListener
from threading import Thread

class Interpreter(RequestListener):
    def __init__(self, rawPGN):
        self.parsingResult = None
        
        interpreterThread = Thread(target=self.start, args=(rawPGN,))
        interpreterThread.start()
                  
    def start(self, rawPGN):
        InterpreterEvent().startInterpretation()
        parser = Parser(Lexer(rawPGN))
        self.parsingResult = parser.getParsingResult()
        print(self.parsingResult)
        InterpreterEvent().endInterpretation()
        
        # Τώρα που ολοκληρώθηκε το interpretation, ξεκινάμε να ακούμε σε requests
        # από το GUI.
        GUIRequest().subscribe(self)
    
    def onRequest(self, request: GUIRequest):
        if (isinstance(request, GUIRequest)):
            if (request._type == "GET_GAMES"):
                InterpreterResponse().sendResponse(request, 'INTERPRETER SAID HI')
        
        
    
            