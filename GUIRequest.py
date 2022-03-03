from Request.Request import Request

class GUIRequest(Request):
    
    def getGames(self):
        self._type = "GET_GAMES"
        self._args = []
        self.dispatch()

    def getTags(self, gameUUID):
        self._type = "GET_TAGS"
        self._args = gameUUID
        self.dispatch()
    
    def getMoves(self, gameUUID):
        self._type = "GET_MOVES"
        self._args = gameUUID
        self.dispatch()
        
    def getNextMove(self, gameUUID):
        self._type = "GET_NEXT_MOVE"
        self._args = gameUUID
        self.dispatch()