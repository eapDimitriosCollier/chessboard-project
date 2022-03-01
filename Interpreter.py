from Lexer.Lexer import Lexer
from Parser.Parser import Parser
from InterpreterEvent import InterpreterEvent
from InterpreterResponse import InterpreterResponse
from GUIRequest import GUIRequest
from Event import Event
from EventListener import EventListener
from threading import Thread


class Interpreter(EventListener):
    def __init__(self, interpreterEvent: InterpreterEvent, interpreterResponse: InterpreterResponse, rawPGN):
        self.parsingResult = None
        self.interpreterEvent = interpreterEvent
        self.interpreterResponse = interpreterResponse
        
        interpreterThread = Thread(target=self.start, args=(rawPGN,))
        interpreterThread.start()
                  
    def start(self, rawPGN):
        self.interpreterEvent.startInterpretation()
        parser = Parser(Lexer(rawPGN))
        self.parsingResult = parser.getParsingResult()
        print(self.parsingResult)
        self.interpreterEvent.endInterpretation()
    
    def onEvent(self, event: Event):
        if (isinstance(event, GUIRequest)):
            if (event._request == "GET_GAMES"):
                self.interpreterResponse.sendResponse('INTERPRETER SAID HI')
        
        
    
            