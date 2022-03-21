import sys
sys.path.append('../CHESSBOARD-PROJECT')
from Event.Event import Event
from Response.Response import Response
from ResponseListener.ResponseListener import ResponseListener
from Interpreter import Interpreter
from InterpreterResponse import InterpreterResponse
from GUIRequest import GUIRequest
from Lexer.sample_game import txt

class ChessModel():
    def __init__(self) -> None:
        self.games = []
        self.gameUUID = ''
        self.tags = []
        self.rawMoves = []
        self.moveId = None
        self.player = None
        self.currentMove = []
        self.GameActive=False
        self._txt=txt
        
        # Initialize events
        Event('InterpretationStarted').subscribe(self)
        Event('InterpretationEnded').subscribe(self)
        Event('InterpretationFailed').subscribe(self)  
        InterpreterResponse().subscribe(self)
        self.interpreterInit()

    @property
    def Txt(self):
        return self._txt
    
    @Txt.setter
    def Txt(self,data:str):
        self._txt=data

    def GetParserNextMove(self,event):
        if not self.gameUUID:
            GUIRequest().getGames()
        GUIRequest().getNextMove(self.gameUUID, self.moveId, self.player)
        
    def GetParserFirstMove(self,event):
        if not self.gameUUID:
            GUIRequest().getGames()        
        GUIRequest().getNextMove(self.gameUUID)

    def interpreterInit(self) -> None:
        self.interpreter = Interpreter(self._txt)

    def onInterpretationStarted(self, event):
        print('Interpretation Started')
        
    def onInterpretationEnded(self, event):
        print('Interpretation Ended')
        GUIRequest().getGames()
        self.GetParserFirstMove(event)
        
    def onInterpretationFailed(self, event):
        print('Interpretation Failed')
    
    def onResponse(self, response: Response):
        if (isinstance(response, InterpreterResponse)):
            # Θα ήταν ωραίο να παίζαμε με match-case αντί για if, αλλά για backwards compatibility
            # ας το αφήσουμε καλύτερα...
            print (Response)
            
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
        #GUIRequest().getNextMove(self.gameUUID)
        
    
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
        Event('ReadyToMove').invoke()  
        

    def interpreterErrorResponseHandler(self, response):
        # Αν ο interpreter πετάξει error το παρουσιάζουμε στην οθόνη.
        print("Error: ",response)