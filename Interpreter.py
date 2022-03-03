from Lexer.Lexer import Lexer
from Parser.Parser import Parser
from InterpreterEvent import InterpreterEvent
from InterpreterResponse import InterpreterResponse
from GUIRequest import GUIRequest
from RequestListener.RequestListener import RequestListener
from threading import Thread
import uuid

class Interpreter(RequestListener):
    def __init__(self, rawPGN):
        self.parsingResult = None

        interpreterThread = Thread(target=self.start, args=(rawPGN,))
        interpreterThread.start()

    def start(self, rawPGN):
        # Περιορίζουμε το PGN σε 602 παιχνίδια
        # (Αυτό το κάνουμε μόνο για τώρα επειδή το sample_game έχει 602 παιχνίδια.)
        # O πραγματικός περιορισμός θα είναι 50 παιχνίδια 
        # (Επειδή αν θεωρήσουμε ότι κάθε παιχνίδι έχει από ~200 κινήσεις, 
        # το Parse Tree ξεπερνάει το βάθος των 1000 node και υπάρχει κίνδυνος stack overflow)
        if self.countGames(rawPGN) > 602:
           InterpreterEvent().interpretationFailed('Too many games') 
           return  
        
        InterpreterEvent().startInterpretation()
        try:
            parser = Parser(Lexer(rawPGN))
            self.parsingResult = parser.getParsingResult()
        except Exception as exc:
            pass    
        InterpreterEvent().endInterpretation()

        # Τώρα που ολοκληρώθηκε το interpretation, ξεκινάμε να ακούμε σε requests
        # από το GUI.
        GUIRequest().subscribe(self)

    def onRequest(self, request: GUIRequest):
        if (isinstance(request, GUIRequest)):
            if (request._type == "GET_GAMES"):
                InterpreterResponse().sendResponse(request, 'INTERPRETER SAID HI')

    def countGames(self, rawPGN):
        splitGames = rawPGN.split("]\n\n")
        return len(splitGames)