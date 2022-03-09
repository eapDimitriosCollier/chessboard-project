from Parser.ParseTree.ParseNode import ParseNode
from Parser.ParseTree.ParseTree import ParseTree

class AbstractSyntaxTreeBuilder:
    def __init__(self, parseTree: ParseTree) -> None:
        self.parseTree = parseTree
        self.AST = None
        self.astNodeFunctionMap = {
            'PGNDatabase'           : self.PGNDatabase,
            'PGNGame'               : self.PGNGame,
            'TagSection'            : self.TagSection,
            'TagPair'               : self.TagPair,
            'TagName'               : self.TagName,
            'TagValue'              : self.TagValue,
            'MoveTextSection'       : self.MoveTextSection,
            'GameTermination'       : self.GameTermination,
            'ElementSequence'       : self.ElementSequence,
            'RecursiveVariation'    : self.RecursiveVariation,
            'Element'               : self.Element,
            'SANMove'               : self.SANMove,
            'MoveNumberIndication'  : self.MoveNumberIndication,
            'NumericAnnotationGlyph' : self.NumericAnnotationGlyph,
            'Empty'                  : self.Empty,
        }
        self.actionNodeFunctionMap = {
            'Movement'  : self.getArgsMovement,
            'Promotion' : self.getArgsPromotion,
            'Castle'    : self.getArgsCastle
        }
        
    def build(self) -> None:
        self.parseTree.postOrderTraversal(self.createASTNode)
        self.AST = self.parseTree.rootNode.ASTNode
    
    def createASTNode(self, parseNode: ParseNode) -> None:
        if parseNode:
            if parseNode.nodeName in self.astNodeFunctionMap:
                self.astNodeFunctionMap[parseNode.nodeName](parseNode)
    
    def PGNDatabase(self, parseNode):
        pgnGame = {}
        pgnDatabase = {}
        for node in parseNode.nodes:
            if node.nodeName == 'PGNGame' : pgnGame = node.ASTNode
            elif node.nodeName == 'PGNDatabase' : pgnDatabase = node.ASTNode
            
        parseNode.ASTNode = [pgnGame, *pgnDatabase]
        
    def PGNGame(self, parseNode) -> None:
        tagSection = []
        moveTextSection = {}
        
        for node in parseNode.nodes:
            if node.nodeName == 'TagSection' : tagSection = node.ASTNode
            elif node.nodeName == 'MoveTextSection' : moveTextSection = node.ASTNode
            
        parseNode.ASTNode = {"TagSection": tagSection, **moveTextSection}  
    
    def TagSection(self, parseNode) -> None:
        tagPair = None
        tagSection = []
        
        for node in parseNode.nodes:
            if node.nodeName == 'TagPair' : tagPair = node.ASTNode
            elif node.nodeName == 'TagSection' : tagSection = node.ASTNode
            
        parseNode.ASTNode = [*tagSection, tagPair]
    
    def TagPair(self, parseNode) -> None:
        tagName = None
        tagValue = None
        
        for node in parseNode.nodes:
            if node.nodeName == 'TagName' : tagName = node.ASTNode
            elif node.nodeName == 'TagValue' : tagValue = node.ASTNode
            
        parseNode.ASTNode = {**tagName, **tagValue} 
           
    def TagName(self, parseNode) -> None:
        token = parseNode.nodeInfo
        parseNode.ASTNode = {"name" : token['token_value']}
        
    def TagValue(self, parseNode) -> None:
        token = parseNode.nodeInfo
        parseNode.ASTNode = {"value" : token['token_value']}
    
    def MoveTextSection(self, parseNode):
        elementSequence = None
        gameTermination = None
        
        for node in parseNode.nodes:
            if node.nodeName == 'ElementSequence' : elementSequence = node.ASTNode
            elif node.nodeName == 'GameTermination' : gameTermination = node.ASTNode            
            
        if elementSequence:
            # Ξεχωρίζουμε τα actions σε white/black.
            movementSection = []
            currentMoveId = 0
            isWhitesTurn = True
            for element in elementSequence:
                if 'moveId' in element:
                    if (currentMoveId != element['moveId']):
                        currentMoveId = element['moveId']
                        movementSection.append({'moveId': currentMoveId})
                    continue
                
                if isWhitesTurn:
                    movementSection[int(currentMoveId) - 1]['rawMoveWhite'] = element[0]['rawMove']
                    element[0].pop('rawMove')
                    
                    movementSection[int(currentMoveId) - 1]['whiteActions'] = element
                    isWhitesTurn = False
                else:
                    movementSection[int(currentMoveId) - 1]['rawMoveBlack'] = element[0]['rawMove']
                    element[0].pop('rawMove')
                    
                    movementSection[int(currentMoveId) - 1]['blackActions'] = element
                    isWhitesTurn = True
            
            parseNode.ASTNode = {"MovementSection": movementSection, "GameTermination": gameTermination}
        else:
            parseNode.ASTNode = {"MovementSection": [], "GameTermination": gameTermination}
                                
    def GameTermination(self, parseNode):
        token = parseNode.nodeInfo
        parseNode.ASTNode = token['token_value']
    
    def ElementSequence(self, parseNode):
        element = None
        elementSequence = []
        
        for node in parseNode.nodes:
            if node.nodeName == 'Element' : element = node.ASTNode
            elif node.nodeName == 'ElementSequence' : elementSequence = node.ASTNode
        
        parseNode.ASTNode = [element, *elementSequence]  
    
    def RecursiveVariation(self, parseNode):
        # Απλά θα αγνοούμε τα RecursiveVariations προς το παρόν
        pass
    
    def Element(self, parseNode):
        # Το Element έχει μόνο ένα παιδί, άρα μπορούμε απλά να πάρουμε το πρώτο παιδί του.
        node = parseNode.nodes[0]
        parseNode.ASTNode = node.ASTNode
        
    def MoveNumberIndication(self, parseNode):
        token = parseNode.nodeInfo
        parseNode.ASTNode = {"moveId": token['token_value']}
    
    def SANMove(self, parseNode):
        token = parseNode.nodeInfo
        
        # Γεμίζουμε μια λίστα από "actions" η οποία περιέχει μέσα όλες τις πράξεις που έγιναν από αυτό το SAN Move
        actions = self.extractActions(token['token_value'])
        
        parseNode.ASTNode = []
        for actionName in actions:
            parseNode.ASTNode.append({
                "actionName": actionName, 
                "arguments": self.extractActionArguments(actionName, token['token_value'])
            })
            parseNode.ASTNode[0]["rawMove"] = token['token_value']      
    
    def NumericAnnotationGlyph(self, parseNode):
        # Απλά θα αγνοούμε τα NAGs προς το παρόν
        pass
    
    def Empty(self, parseNode):
        pass
    
    def getAST(self):
        return self.AST
    
    def extractActions(self, sanMove: str) -> str:
        actionStack = []
        
        # Check for Movement, Promotion, Castle
        # Ο έλεγχος για την εγκυρότητα του SANMove έχει γίνει ήδη από το ParseTree.
        
        #TODO: Assert that each player can only castle once
        # can promote 8 times and a checkmate can occur only once per game
        #TODO: Refactor
        
        if 'O' in sanMove:
            actionStack.append('Castle')
        else:
            actionStack.append('Movement')
            if '=' in sanMove:
                actionStack.append('Promotion')
        
        if '+' == sanMove[-1]:
            actionStack.append('Check')
        elif '#' == sanMove[-1]:
            actionStack.append('Checkmate')  
            
        return actionStack       
    
    def extractActionArguments(self, actionName, sanMove):
        if actionName in self.actionNodeFunctionMap:
            return self.actionNodeFunctionMap[actionName](sanMove)
        
        return dict()
    
    def getArgsMovement(self, sanMove):
        result = {
            "piece"         : "",
            "fromRow"       : "",
            "fromColumn"    : "",
            "toSquare"      : "",
            "isCapturing"   : "False"
        }
    
        # Βρίσκουμε το πιόνι που εκτελεί την κίνηση
        result["piece"] = self.extractPiece(sanMove)
        
        # Αφαιρούμε το πιόνι επειδή δεν το χρειαζόμαστε άλλο
        sanMove = sanMove[1:] if sanMove[0] in ('K', 'Q', 'R', 'B', 'N') else sanMove
        
        # Βρίσκουμε το αν το πιόνι τρώει κάποιο άλλο και αφαιρούμε το σύμβολο που το περιγράφει
        if 'x' in sanMove:
            result["isCapturing"] = "True"
            sanMove = sanMove.replace('x', '')
        
        # Αφαιρούμε τα σύμβολα +/#/=[Q|N|B|R] από το τέλος
        sanMove = self.removePromotionIndicators(self.removeConditionIndicators(sanMove))    
        
        # Βρίσκουμε και αφαιρούμε τα 2 τελευταία σύμβολα από το τέλος (toSquare)
        result["toSquare"] = sanMove[-2:]
        sanMove = sanMove[:-2]
        
        # Τώρα υπάρχουν τρεις περιπτώσεις,
        # Ή το sanMove είναι κενό, ή έχει 1 χαρακτήρα ή έχει 2 χαρακτήρες.
        if len(sanMove) >= 1:
            result["fromColumn"] = sanMove[0]
            if len(sanMove) == 2:
                result["fromRow"] = sanMove[1] 
                
        return result        
    
    def getArgsPromotion(self, sanMove):
        result = {
            "promonotionPiece": "",
        }
        
        # Αφαίρεση όλων τον χαρακτήρων από το = και πίσω
        strippedSANMove = sanMove.split('=')[1]
        
        result["promonotionPiece"] = self.extractPiece(strippedSANMove)
        
        return result
        
    def getArgsCastle(self, sanMove):
        result = {
            "type": "",
        }
        
        strippedSANMove = sanMove
        
        strippedSANMove = self.removeConditionIndicators(strippedSANMove)
        
        if strippedSANMove == 'O-O':
            result["type"] = "short"
        else:
            result["type"] = "long"  
            
        return result  
         
    def removeConditionIndicators(self, sanMove) -> str:
        strippedSANMove = sanMove
        
        # Αφαίρεση όλων των χαρακτήρων από = και ύστερα.
        if '=' in sanMove:
            strippedSANMove = strippedSANMove.split('=')[0]
        
        return strippedSANMove
    
    def removePromotionIndicators(self, sanMove) -> str:
        strippedSANMove = sanMove
        # Αφαίρεση όλων των χαρακτήρων +/#
        if sanMove[-1] == '+' or sanMove[-1] == '#':
            strippedSANMove = strippedSANMove[:-1]
            
        return strippedSANMove   
    
    def extractPiece(self, sanMove) -> str:
        piece = "Pawn"
        
        if sanMove[0] == 'K':
            piece = "King"
        elif sanMove[0] == 'Q':
            piece = "Queen"
        elif sanMove[0] == 'R':
            piece = "Rook"
        elif sanMove[0] == 'B':
            piece = "Bishop"
        elif sanMove[0] == 'N':
            piece = "Knight"
                
        return piece
                 