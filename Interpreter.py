from threading import Thread
from Lexer.Lexer import Lexer
from Parser.Parser import Parser
from Event.Event import Event
from InterpreterResponse import InterpreterResponse
from GUIRequest import GUIRequest
from RequestListener.RequestListener import RequestListener
import uuid

class Interpreter(RequestListener):
    def __init__(self):
        self.parsingResult = None 
        self.games = []
        self.tags = {}
        self.moves = {}
        self.rawMoves = {}
        self.gameTerminations = {}
        self.interpreterProcess = None
    
    def resetInterpreter(self):
        self.parsingResult = None 
        self.games = []
        self.tags = {}
        self.moves = {}
        self.rawMoves = {}
        self.gameTerminations = {}
        if (self.interpreterProcess):
            GUIRequest().unsubscribe(self)
            self.interpreterProcess._stop()
            self.interpreterProcess = None
    
    def readFile(self, rawPGN):   
        self.resetInterpreter()
        
        self.interpreterProcess = Thread(target=self.start, args=(rawPGN,))
        self.interpreterProcess.start()

    def start(self, rawPGN):
        Event('InterpretationStarted').invoke()
        try:
            parser = Parser(Lexer(rawPGN))
            self.parsingResult = parser.getParsingResult()
        except Exception as exc:
            Event('InterpretationFailed', message='Couldn\'t parse, malformed PGN.', exception=exc).invoke()
            return
        
        self.populateInterpreter()
        Event('InterpretationEnded').invoke()

        # Τώρα που ολοκληρώθηκε το interpretation, ξεκινάμε να ακούμε σε requests
        # από το GUI.
        GUIRequest().subscribe(self)

    def onRequest(self, request: GUIRequest):
        if (isinstance(request, GUIRequest)):
            if (request._type == "GET_GAMES"):
                self.GetGamesRequestHandler(request)
            elif (request._type == "GET_TAGS"):
                self.GetTagsRequestHandler(request) 
            elif (request._type == "GET_RAW_MOVES"):
                self.GetRawMovesRequestHandler(request)
            elif (request._type == "GET_NEXT_MOVE"):
                self.GetNextMoveRequestHandler(request)          

    def GetGamesRequestHandler(self, request: GUIRequest) -> None:
        InterpreterResponse().sendResponse(request, self.games)
    
    def GetTagsRequestHandler(self, request: GUIRequest) -> None:
        gameUUID = request._args
        if gameUUID is None:
            InterpreterResponse().sendErrorResponse(request, 'GameUUID is required')
        
        if (gameUUID in self.tags):
            InterpreterResponse().sendResponse(request, self.tags[gameUUID])
            return
        
        InterpreterResponse().sendErrorResponse(request, 'This game was not found.')
        
    def GetRawMovesRequestHandler(self, request: GUIRequest) -> None:
        gameUUID = request._args
        if gameUUID is None:
            InterpreterResponse().sendErrorResponse(request, 'GameUUID is required')  
        
        if (gameUUID in self.rawMoves):
            InterpreterResponse().sendResponse(request, self.rawMoves[gameUUID])    
            return
        
        InterpreterResponse().sendErrorResponse(request, 'This game was not found.')    
    
    def GetNextMoveRequestHandler(self, request: GUIRequest) -> None:
        prevMove = request._args
        gameUUID = prevMove['gameUUID']
        moveId = prevMove['moveId']
        player = prevMove['player']
        
        nextMove = None
        nextMoveId = prevMove['moveId']
        nextPlayer = prevMove['player']
        
        if gameUUID not in self.games:
            InterpreterResponse().sendErrorResponse(request, 'This game was not found.')     
            return
        elif not self.moves[gameUUID]:
            nextMove = self.gameTerminations[gameUUID]
            InterpreterResponse().sendResponse(request, {
                'nextMove': nextMove, 
                'nextMoveId': nextMoveId,
                'nextPlayer' : nextPlayer
            })
    
        if not moveId or not player:
            # Βρίσκουμε την πρώτη κίνηση
            nextMoveId = '1'
            nextPlayer = 'white'
            nextMove = self.findMove(gameUUID, nextMoveId, nextPlayer)['foundMove']
            
            InterpreterResponse().sendResponse(request, {
                'nextMove': nextMove, 
                'nextMoveId': nextMoveId,
                'nextPlayer' : nextPlayer
            })
            return
            
        
        # Βρίσκουμε την προηγούμενη κίνηση. 
        search = self.findMove(gameUUID, moveId, player)
        if search['isGameTermination']: 
            nextMove = self.gameTerminations[gameUUID]
            nextMoveId = None
            nextPlayer = None
            InterpreterResponse().sendResponse(request, {
                'nextMove': nextMove, 
                'nextMoveId': nextMoveId,
                'nextPlayer' : nextPlayer
            })
            return
        elif search['foundMove']:
            if (player == 'white'): nextPlayer = 'black'        
            else:
                nextPlayer = 'white'
                nextMoveId = str(int(moveId)+1)              
        else:
            InterpreterResponse().sendErrorResponse(request, 'This move was not found.')
            return
        
        # Βρίσκουμε την επόμενη κίνηση
        nextMove = self.findMove(gameUUID, nextMoveId, nextPlayer)['foundMove']
        
        InterpreterResponse().sendResponse(request, {
            'nextMove': nextMove, 
            'nextMoveId': nextMoveId,
            'nextPlayer' : nextPlayer
        })
    
    def populateInterpreter(self):
        # Λίγο πρίν τελειώσει το Interpretation, θα βάλουμε σε κάθε παιχνίδι ένα UUID
        # το οποίο θα ξεχωρίζει κάθε παιχνίδι.
        # Ο λόγος χρήσης UUID είναι επειδή στο μέλλον θέλουμε να χρησιμοποιήσουμε μια βάση δεδομένων
        # για την αποθήκευση των παιχνιδιών. (caching με SQLite δηλαδή).
        
        for game in self.parsingResult:
            # Παράγουμε UUID και γεμίζουμε τα games
            currentGameUUID = str(uuid.uuid4())
            game['uuid'] = currentGameUUID 
            
            self.games.append(currentGameUUID)
            
            # Στην συνέχεια γεμίζουμε τα tags, moves και gameTerminations
            self.tags[currentGameUUID] = game["TagSection"]
            self.moves[currentGameUUID] = game["MovementSection"]
            self.gameTerminations[currentGameUUID] = game["GameTermination"]
            
            # Τέλος βρίσκουμε όλα τα rawMoves
            self.rawMoves[currentGameUUID] = []
            for move in self.moves[currentGameUUID]:
                # Υπάρχει περίπτωση να μην υπάρχει κίνηση από τον μαύρο 
                # (Δηλ. το παιχνίδι τελειώνει με τελευταία την κίνηση του λευκού)
                rawMoveBlack = move['rawMoveBlack'] if 'rawMoveBlack' in move else None
                
                if rawMoveBlack:
                    self.rawMoves[currentGameUUID].append({
                        'moveId' : move['moveId'],
                        'rawMoveWhite' : move['rawMoveWhite'],
                        'rawMoveBlack' : rawMoveBlack
                    })
                else:    
                    self.rawMoves[currentGameUUID].append({
                        'moveId' : move['moveId'],
                        'rawMoveWhite' : move['rawMoveWhite'],
                    })
    
    def findMove(self, gameUUID, moveId, player) -> object:
        movementSection = self.moves[gameUUID]
        foundMove = None
        isGameTermination = False
        
        for index, move in enumerate(movementSection):
            if move['moveId'] == moveId:
                if (player == 'white' and 'whiteActions' not in move) or (player == 'black' and 'blackActions' not in move):
                    foundMove = None
                    break

                foundMove = move['whiteActions'] if player == 'white' else move['blackActions']
                if index == len(movementSection) - 1:
                    if player == 'white': 
                        if 'blackActions' not in move:
                            isGameTermination = True 
                    else:
                        isGameTermination = True       
                break        
        
        return {'foundMove': foundMove, 'isGameTermination': isGameTermination}          
               
                    
        
