from Request.Request import Request

class GUIRequest(Request):
    
    def getGames(self):
        self._type = "GET_GAMES"
        self.dispatch()

    def getTags(self, gameUUID):
        self._type = "GET_TAGS"
        self._args = gameUUID
        self.dispatch()
    
    def getRawMoves(self, gameUUID):
        self._type = "GET_RAW_MOVES"
        self._args = gameUUID
        self.dispatch()
        
    def getNextMove(self, gameUUID, moveId=None, player=None):
        # prevMove = {
        #   'gameUUID',
        #   'moveId' 
        #   'player' (white/black)
        # }
        # Αν σταλθεί μόνο το gameUUID, επιστρέφουμε την πρώτη κίνηση του παιχνιδιού με αυτό το UUID
        prevMove = {
           'gameUUID': gameUUID,
           'moveId' : moveId,
           'player' : player
        }
        
        self._type = "GET_NEXT_MOVE"
        self._args = prevMove
        self.dispatch()