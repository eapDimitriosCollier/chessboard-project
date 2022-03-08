import tkinter as tk
from sample_game import txt
from tkinter import filedialog
from Event.Event import Event

from Response.Response import Response
from ResponseListener.ResponseListener import ResponseListener

from Interpreter import Interpreter
from InterpreterResponse import InterpreterResponse
from GUIRequest import GUIRequest

class Application(ResponseListener):
    def __init__(self) -> None:
        self.WIDTH = 600
        self.HEIGHT = 600
        self.TITLE = "PGN Reader"
        self.window = tk.Tk()
        self.start()
    
    def start(self) -> None:
        # Initialize tkinter
        self.window.title(self.TITLE)
        self.window.geometry(f"{self.WIDTH}x{self.HEIGHT}")
        self.window.config(background = "white")
        # -- DEMO ONLY Για να δείξουμε πιο πρέπει να είναι το flow --
        self.games = []
        self.gameUUID = ''
        self.tags = []
        self.rawMoves = []
        self.moveId = None
        self.player = None
        self.currentMove = []
        
        self.window.bind('<space>', lambda e: GUIRequest().getGames())
        self.window.bind('1', lambda e: GUIRequest().getTags(self.gameUUID))
        self.window.bind('2', lambda e: GUIRequest().getRawMoves(self.gameUUID))
        self.window.bind('3', lambda e: GUIRequest().getNextMove(self.gameUUID, self.moveId, self.player))
        
        # Get File...
        #...
        self.interpreterInit()
        self.window.mainloop()  
    
    def interpreterInit(self) -> None:
        # Initialize events
        Event('InterpretationStarted').subscribe(self)
        Event('InterpretationEnded').subscribe(self)
        Event('InterpretationFailed').subscribe(self)
        self.interpreter = Interpreter(txt)
        InterpreterResponse().subscribe(self)
        
    
    def onInterpretationStarted(self, event):
        print('Interpretation Started')
        
    def onInterpretationEnded(self, event):
        print('Interpretation Ended')    
    
    def onInterpretationFailed(self, event):
        print('Interpretation Failed')
    
    def onResponse(self, response: Response):
        if (isinstance(response, InterpreterResponse)):
            # Θα ήταν ωραίο να παίζαμε με match-case αντί για if, αλλά για backwards compatibility
            # ας το αφήσουμε καλύτερα...
            
            if (response._request._type == "GET_GAMES"):
                self.GetGamesResponseHandler(response._response)
            elif (response._request._type == "GET_TAGS"):
                self.GetTagsResponseHandler(response._response)
            elif (response._request._type == "GET_RAW_MOVES"):
                self.GetRawMovesResponseHandler(response._response)
            elif (response._request._type == "GET_NEXT_MOVE"):
                self.GetGetNextMoveResponseHandler(response._response)
            
    def onErrorResponse(self, response: Response):
        if (isinstance(response, InterpreterResponse)):
            self.interpreterErrorResponseHandler(response)
           
    def GetGamesResponseHandler(self, response):
        self.games = response
        self.gameUUID = self.games[0]
        print(self.gameUUID)
    
    def GetTagsResponseHandler(self, response):
        self.tags = response
        print(self.tags)
    
    def GetRawMovesResponseHandler(self, response):
        self.rawMoves = response
        print(self.rawMoves)
    
    def GetGetNextMoveResponseHandler(self, response):
        self.currentMove = response['nextMove']
        self.moveId = response['nextMoveId']
        self.player = response['nextPlayer']
        print('currentMove:', self.currentMove)
        print('moveId: ', self.moveId)
        print('player: ', self.player)
    
    def interpreterErrorResponseHandler(self, response):
        # Αν ο interpreter πετάξει error το παρουσιάζουμε στην οθόνη.
        print(response)
    
if __name__ == '__main__':
    app = Application()
    app.start()
        