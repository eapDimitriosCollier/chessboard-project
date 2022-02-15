import ParserConstants
import re
## Η γραμματική του PGN εκφρασμένη σε BNF.
## Την γραμματική την βρήκαμε στο 

# <PGN-database>',= <PGN-game> <PGN-database>
#                    <empty>
# <PGN-game>',= <tag-section> <movetext-section>
# <tag-section>',= <tag-pair> <tag-section>
#                   <empty>
# <tag-pair>',= [ <tag-name> <tag-value> ]
# <tag-name>',= <identifier>
# <tag-value>',= <string>
# <movetext-section>',= <element-sequence> <game-termination>
# <element-sequence>',= <element> <element-sequence>
#                        <recursive-variation> <element-sequence>
#                        <empty>
# <element>',= <move-number-indication>
#               <SAN-move>
#               <numeric-annotation-glyph>
# <recursive-variation>',= ( <element-sequence> )
# <game-termination>',= 1-0
#                        0-1
#                        1/2-1/2
#                        *
# <empty>',=
class Tree:
    def __init__(self, treeName='', rootNode=None):
        self.treeName = treeName
        self.currentNode = rootNode
        self.rootNode = rootNode
        self.shouldTrace = False
        self.markedNodeStack = []
    
    def showTree(self):
        for node in self.rootNode.nodes:
            node.showNode()

    def insertNode(self, node):
        assert(isinstance(node, Node))
        node.nodeParent = self.currentNode
        self.currentNode.nodes.append(node)
        self.currentNode = node

        if self.shouldTrace:
            self.traceStack.append(node.id)

    def goToParent(self):
        self.currentNode = self.currentNode.getParent()

    def findNodeById(self, nodeId):
        return self.rootNode.findNodeById(nodeId)

    def removeNode(self, nodeId):
        nodeToRemove = self.findNodeById(nodeId)   
        nodeToRemove.nodeParent.nodes.remove(nodeToRemove)

    def startMarking(self):
        self.shouldTrace = True

    def stopMarking(self):
        self.shouldTrace = False

    def removeMarkedNodes(self):
        for nodeId in self.markedNodeStack:
            self.removeNode(nodeId)

        self.clearMarkedNodeStack()


    def clearMarkedNodeStack(self):
        self.traceStack = []    

class Node:
    count = 0
    # Βασική υλοποίηση ενός δέντρου. Χρησιμοποιείται για την παραγωγή του Parser Tree.
    def __init__(self, nodeName='root', nodeInfo=None):
        Node.count+=1

        self.nodeName = nodeName
        self.nodeParent = None
        self.nodeInfo = nodeInfo
        self.nodes = []
        self.id = Node.count
    
    def showNode(self):
        print('Node name:\t', self.nodeName)     
        print('Node info:\t', self.nodeInfo) 
        for node in self.nodes:
            node.showNode()

    def getParent(self):
        return self.nodeParent

    def findNodeById(self, searchId):
        if (self.id == searchId):
            return self
        if (self.nodes is not None):
            for node in self.nodes:
                return node.findNodeById()
        raise Exception('Node id not found')

# Κλάσεις για διαχείρηση σφαλμάτων

class ParseError(Exception):
    def __init__(self, message):
        super().__init__(message)
class SyntacticalError(ParseError):
    def __init__(self, tokenIndex, expected, got):
        self.message = f'SyntacticalError on token #{tokenIndex}. Expected {expected}, got {got}'
        super().__init__(self.message)

class SemanticalError(ParseError):
    def __init__(self, tokenIndex, errorMessage):
        self.message = f'SemanticalError on token #{tokenIndex}. {errorMessage}'
        super().__init__(self.message)

class Parser:
    """Απλή υλοποίηση ενός Recursive Descent Parser"""
    def __init__(self, lexerExpressionList):
        self.lexerExpressionList = lexerExpressionList
        self.currentPos =  0
        self.streamLen = len(self.lexerExpressionList)
        self.parseTree = Tree('Parse Tree',  Node('root'))
        self.usedTagIdentifiers = []

        self.start()
        self.parseTree.showTree()

# Μέθοδοι για το διάβασμα token από τον Lexer
    def nextToken(self):
        self.currentPos += 1

        token = self.lexerExpressionList[self.currentPos]

        if (token['token_type'] == 'Comment'):
            self.nextToken()

    def currentToken(self):
        return self.lexerExpressionList[self.currentPos]

# Μέθοδοι που ελέγχουν αν το επόμενο token έχει συγκεκριμένη τιμή
    def expectType(self, expectedTokenType):
        currentToken = self.currentToken()
        if (currentToken['token_type'] != expectedTokenType):
            raise SyntacticalError(self.currentPos, expectedTokenType, currentToken['token_type'])            

    def expectValue(self, expectedTokenValue):
        currentToken = self.currentToken()
        if (currentToken['token_value'] != expectedTokenValue):
            raise SyntacticalError(self.currentPos, expectedTokenValue, currentToken['token_value'])      

    def maybe(self, listOfFunctions):
        lastPosition = self.currentPos
        for index, func in enumerate(listOfFunctions):
            try:
                self.parseTree.startMarking()
                func()
                self.parseTree.stopMarking()
            except ParseError as e:
                # Πρώτα διαγράφουμε όλα τα marked nodes
                self.parseTree.removeMarkedNodes()

                # Αν είμαστε στο τελευταίο function, σημαίνει ότι όλα τα προηγούμενα έχουν αποτύχει.
                # Εφόσον αποτύχει και το τελευταίο, πετάμε το τελευταίο ParseError που πήραμε.
                if index == len(listOfFunctions) - 1:
                    raise e

                self.currentPos = lastPosition
                continue     
            else:
                # Αν εκτελεστεί το παραπάνω χωρίς ParseError, τότε, απλά φεύγουμε απ'την επανάληψη
                self.parseTree.clearMarkedNodeStack()
                break
        
# Μέθοδοι που διέπουν το Recursive Descent μέρος του Parser
#  εφαρμόζοντας την γραμματική στο BNF που βρήκαμε.
    def start(self):
        self.PGNDatabase()

    def PGNDatabase(self):
        token = self.currentToken()
        # Για την αποφυγή του backtracking, αντί να προσπαθήσουμε πρώτα να matchάρουμε τον <empty> κανόνα
        # και ύστερα τους κανόνες <PGN Game> <PGN Database> , απλά θέτουμε ότι αν δεν είναι WhiteSpace χαρακτήρας,
        # ισχύουν οι κανόνες <PGN Game> <PGN Database>
        if (token['token_type'] != 'WhiteSpace'):
            self.parseTree.insertNode(Node('PGNDatabase'))
            self.PGNGame()
            self.nextToken()    
            self.PGNDatabase()
        else:
            self.Empty()
            self.parseTree.goToParent() 
    
    def PGNGame(self):
        self.parseTree.insertNode(Node('PGNGame'))
        self.TagSection()

        self.nextToken()     
        self.MoveTextSection()
        self.parseTree.goToParent()

    def TagSection(self):
        currentToken = self.currentToken()
        if (currentToken['token_type'] != 'WhiteSpace'):
            self.parseTree.insertNode(Node('TagSection'))
            self.TagPair()

            self.nextToken() 
            self.TagSection()
        else:
            # Ολοκληρώθηκαν τα TagSection, οπότε κάνουμε έλεγχο αν υπάρχουν τα 
            # required Tag Identifiers
            requiredTagIdentifiers = []
            for tagIdentifier, isOptional in ParserConstants.VALID_TAG_IDENTIFIERS.items():
                if not isOptional['isOptional']:
                    requiredTagIdentifiers.append(tagIdentifier)
            
            for requiredTagIdentifier in requiredTagIdentifiers:
                if requiredTagIdentifier not in self.usedTagIdentifiers:
                    raise SemanticalError(self.currentPos, 'Missing required Tags.')                   

            self.Empty() 
            self.parseTree.goToParent()

    def TagPair(self):
        self.parseTree.insertNode(Node('TagPair'))
        self.expectValue('[')

        self.nextToken()
        self.TagName()

        self.nextToken()     
        self.TagValue()

        self.nextToken()    
        self.expectValue(']')

        self.parseTree.goToParent()

    def TagName(self):
        self.expectType('Identifier')
        token = self.currentToken()
        tagIdentifier = token['token_value']
        self.parseTree.insertNode(Node('TagName', token))
        
        if (tagIdentifier in self.usedTagIdentifiers):
            raise SemanticalError(self.currentPos, f'Tag Identifier {tagIdentifier} has already been used.')
        
        if (tagIdentifier not in ParserConstants.VALID_TAG_IDENTIFIERS):
            raise SemanticalError(self.currentPos, f'Tag Identifier {tagIdentifier} is not a valid tag identifier.')
        else:
            self.usedTagIdentifiers.append(tagIdentifier)

        self.parseTree.goToParent()

    def TagValue(self):
        self.expectType('String')
        token = self.currentToken()
        self.parseTree.insertNode(Node('TagValue', token))
        self.parseTree.goToParent()
    
    def MoveTextSection(self):
        self.parseTree.insertNode(Node('MoveTextSection'))
        self.ElementSequence()
        self.nextToken()
        self.GameTermination()
        self.parseTree.goToParent()

    def ElementSequence(self):
        currentToken = self.currentToken()
        if (currentToken['token_type'] != 'WhiteSpace'):
            self.parseTree.insertNode(Node('ElementSequence'))
            self.maybe([self.Element, self.RecursiveVariation])
            self.nextToken()
            self.ElementSequence()
        else:
            self.Empty() 
            self.parseTree.goToParent()

    def Element(self):
        self.maybe([self.MoveNumberIndication, self.SANMove, self.NumericAnnotationGlyph])

    def MoveNumberIndication(self):
        self.expectType('Movement')

    def SANMove(self):
        token = self.currentToken()
        # Χρήση RegEx για αναγνώριση κινήσεων.
        self.expectType('Expression')
        SANMoveRegEx = r"([NBRQK])?([a-h])?([1-8])?(x)?([a-h][1-8])(=[NBRQ])?(\+|#)?$|^O-O(-O)?"
        if (not re.match(SANMoveRegEx, token['token_value'])):
            raise ParseError('Invalid move')

        self.parseTree.insertNode(Node('SANMove', token))
        self.parseTree.goToParent()

    def NumericAnnotationGlyph(self):
        token = self.currentToken()
        self.expectType('Expression')
        NAGRegEx = r"\$[1-255]"
        if (not re.fullmatch(NAGRegEx, token['token_value'])):
            raise ParseError('Invalid move')

        self.parseTree.insertNode(Node('NumericAnnotationGlyph', token))  
        self.parseTree.goToParent()  

    def RecursiveVariation(self):
        self.expectValue("(")
        self.nextToken()
        self.ElementSequence()
        self.nextToken()
        self.expectValue(")")
        self.parseTree.goToParent()  

    def GameTermination(self):
        token = self.currentToken()
        self.expectType('Expression')
        GameTerminationRegex = r"1-0|1-1|0-1|\*"
        if (not re.fullmatch(GameTerminationRegex, token['token_value'])):
            raise ParseError('Invalid Game Termination')
        
        self.parseTree.insertNode(Node('GameTermination', token))
        self.parseTree.goToParent()

    def Empty(self):
        self.expectType('WhiteSpace')
        self.parseTree.insertNode(Node('E'))

        self.parseTree.goToParent()

lexerExpressionList = [
    {'token_type': 'Operator',    'token_value':  '['},
    {'token_type': 'Identifier',  'token_value':  'Event'},
    {'token_type': 'String',      'token_value':  'GBR-ch 58th'},
    {'token_type': 'Operator',    'token_value':  ']'},
    {'token_type': 'Operator',    'token_value':  '['},
    {'token_type': 'Identifier',  'token_value':  'Site'},
    {'token_type': 'String',      'token_value':  'Blackpool'},
    {'token_type': 'Operator',    'token_value':  ']'},
    {'token_type': 'Operator',    'token_value':  '['},
    {'token_type': 'Identifier',  'token_value':  'Date'},
    {'token_type': 'String',      'token_value':  '1971.08.12'},
    {'token_type': 'Operator',    'token_value':  ']'},
    {'token_type': 'Operator',    'token_value':  '['},
    {'token_type': 'Identifier',  'token_value':  'Round'},
    {'token_type': 'String',      'token_value':  '4'},
    {'token_type': 'Operator',    'token_value':  ']'},
    {'token_type': 'Operator',    'token_value':  '['},
    {'token_type': 'Identifier',  'token_value':  'White'},
    {'token_type': 'String',      'token_value':  'Littlewood, John Eric'},
    {'token_type': 'Operator',    'token_value':  ']'},
    {'token_type': 'Operator',    'token_value':  '['},
    {'token_type': 'Identifier',  'token_value':  'Black'},
    {'token_type': 'String',      'token_value':  'Whiteley, Andrew'},
    {'token_type': 'Operator',    'token_value':  ']'},
    {'token_type': 'Operator',    'token_value':  '['},
    {'token_type': 'Identifier',  'token_value':  'Result'},
    {'token_type': 'String',      'token_value':  '0-1'},
    {'token_type': 'Operator',    'token_value':  ']'},
    {'token_type': 'Operator',    'token_value':  '['},
    {'token_type': 'Identifier',  'token_value':  'WhiteElo'},
    {'token_type': 'String',      'token_value':  '2310'},
    {'token_type': 'Operator',    'token_value':  ']'},
    {'token_type': 'Operator',    'token_value':  '['},
    {'token_type': 'Identifier',  'token_value':  'BlackElo'},
    {'token_type': 'String',      'token_value':  '2310'},
    {'token_type': 'Operator',    'token_value':  ']'},
    {'token_type': 'Operator',    'token_value':  '['},
    {'token_type': 'Identifier',  'token_value':  'ECO'},
    {'token_type': 'String',      'token_value':  'D44'},
    {'token_type': 'Operator',    'token_value':  ']'},
    {'token_type': 'Operator',    'token_value':  '['},
    {'token_type': 'Identifier',  'token_value':  'EventDate'},
    {'token_type': 'String',      'token_value':  '1971.08.09'},
    {'token_type': 'Operator',    'token_value':  ']'},
    {'token_type': 'Operator',    'token_value':  '['},
    {'token_type': 'Identifier',  'token_value':  'PlyCount'},
    {'token_type': 'String',      'token_value':  '66'},
    {'token_type': 'Operator',    'token_value':  ']'},
    {'token_type': 'Operator',    'token_value':  '['},
    {'token_type': 'Identifier',  'token_value':  'EventType'},
    {'token_type': 'String',      'token_value':  'swiss'},
    {'token_type': 'Operator',    'token_value':  ']'},
    {'token_type': 'Operator',    'token_value':  '['},
    {'token_type': 'Identifier',  'token_value':  'EventRounds'},
    {'token_type': 'String',      'token_value':  '11'},
    {'token_type': 'Operator',    'token_value':  ']'},
    {'token_type': 'Operator',    'token_value':  '['},
    {'token_type': 'Identifier',  'token_value':  'EventCountry'},
    {'token_type': 'String',      'token_value':  'GBR'},
    {'token_type': 'Operator',    'token_value':  ']'},
    {'token_type': 'WhiteSpace',    'token_value':  ''},
    {'token_type': 'Movement',    'token_value':  '1'},
    {'token_type': 'Expression',  'token_value':  'd4'},
    {'token_type': 'Expression',  'token_value':  'd5'},
    {'token_type': 'Movement',    'token_value':  '2'},
    {'token_type': 'Expression',  'token_value':  'c4'},
    {'token_type': 'Expression',  'token_value':  'c6'},
    {'token_type': 'Movement',    'token_value':  '3'},
    {'token_type': 'Expression',  'token_value':  'Nf3'},
    {'token_type': 'Expression',  'token_value':  'Nf6'},
    {'token_type': 'Movement',    'token_value':  '4'},
    {'token_type': 'Expression',  'token_value':  'Nc3'},
    {'token_type': 'Expression',  'token_value':  'e6'},
    {'token_type': 'Movement',    'token_value':  '5'},
    {'token_type': 'Expression',  'token_value':  'Bg5'},
    {'token_type': 'Expression',  'token_value':  'dxc4'},
    {'token_type': 'Movement',    'token_value':  '6'},
    {'token_type': 'Expression',  'token_value':  'e4'},
    {'token_type': 'Expression',  'token_value':  'b5'},
    {'token_type': 'Movement',    'token_value':  '7'},
    {'token_type': 'Expression',  'token_value':  'Qc2'},
    {'token_type': 'Expression',  'token_value':  'h6'},
    {'token_type': 'Movement',    'token_value':  '8'},
    {'token_type': 'Expression',  'token_value':  'Bh4'},
    {'token_type': 'Expression',  'token_value':  'Be7'},
    {'token_type': 'Movement',    'token_value':  '9'},
    {'token_type': 'Expression',  'token_value':  'Be2'},
    {'token_type': 'Expression',  'token_value':  'g5'},
    {'token_type': 'Movement',    'token_value':  '10'},
    {'token_type': 'Expression',  'token_value':  'Bg3'},
    {'token_type': 'Expression',  'token_value':  'g4'},
    {'token_type': 'Movement',    'token_value':  '11'},
    {'token_type': 'Expression',  'token_value':  'Ne5'},
    {'token_type': 'Expression',  'token_value':  'b4'},
    {'token_type': 'Movement',    'token_value':  '12'},
    {'token_type': 'Expression',  'token_value':  'Na4'},
    {'token_type': 'Expression',  'token_value':  'Qxd4'},
    {'token_type': 'Movement',    'token_value':  '13'},
    {'token_type': 'Expression',  'token_value':  'O-O'},
    {'token_type': 'Expression',  'token_value':  'Qxe4'},
    {'token_type': 'Movement',    'token_value':  '14'},
    {'token_type': 'Expression',  'token_value':  'Qd2'},
    {'token_type': 'Expression',  'token_value':  'Ba6'},
    {'token_type': 'Movement',    'token_value':  '15'},
    {'token_type': 'Expression',  'token_value':  'Rfe1'},
    {'token_type': 'Expression',  'token_value':  'Qd5'},
    {'token_type': 'Movement',    'token_value':  '16'},
    {'token_type': 'Expression',  'token_value':  'Qf4'},
    {'token_type': 'Expression',  'token_value':  'Nbd7'},
    {'token_type': 'Movement',    'token_value':  '17'},
    {'token_type': 'Expression',  'token_value':  'Nxc4'},
    {'token_type': 'Expression',  'token_value':  'Nh5'},
    {'token_type': 'Movement',    'token_value':  '18'},
    {'token_type': 'Expression',  'token_value':  'Qc1'},
    {'token_type': 'Expression',  'token_value':  'Nxg3'},
    {'token_type': 'Movement',    'token_value':  '19'},
    {'token_type': 'Expression',  'token_value':  'hxg3'},
    {'token_type': 'Expression',  'token_value':  'Bb5'},
    {'token_type': 'Movement',    'token_value':  '20'},
    {'token_type': 'Expression',  'token_value':  'Qc2'},
    {'token_type': 'Expression',  'token_value':  'Qg5'},
    {'token_type': 'Movement',    'token_value':  '21'},
    {'token_type': 'Expression',  'token_value':  'Rad1'},
    {'token_type': 'Expression',  'token_value':  'Nf6'},
    {'token_type': 'Movement',    'token_value':  '22'},
    {'token_type': 'Expression',  'token_value':  'Nd6+'},
    {'token_type': 'Expression',  'token_value':  'Bxd6'},
    {'token_type': 'Movement',    'token_value':  '23'},
    {'token_type': 'Expression',  'token_value':  'Rxd6'},
    {'token_type': 'Expression',  'token_value':  'O-O'},
    {'token_type': 'Movement',    'token_value':  '24'},
    {'token_type': 'Expression',  'token_value':  'Nc5'},
    {'token_type': 'Expression',  'token_value':  'Rad8'},
    {'token_type': 'Movement',    'token_value':  '25'},
    {'token_type': 'Expression',  'token_value':  'Rxd8'},
    {'token_type': 'Expression',  'token_value':  'Rxd8'},
    {'token_type': 'Movement',    'token_value':  '26'},
    {'token_type': 'Expression',  'token_value':  'Bxb5'},
    {'token_type': 'Expression',  'token_value':  'cxb5'},
    {'token_type': 'Movement',    'token_value':  '27'},
    {'token_type': 'Expression',  'token_value':  'Nd3'},
    {'token_type': 'Expression',  'token_value':  'Qf5'},
    {'token_type': 'Movement',    'token_value':  '28'},
    {'token_type': 'Expression',  'token_value':  'Re3'},
    {'token_type': 'Expression',  'token_value':  'a5'},
    {'token_type': 'Movement',    'token_value':  '29'},
    {'token_type': 'Expression',  'token_value':  'Kf1'},
    {'token_type': 'Expression',  'token_value':  'Ne4'},
    {'token_type': 'Movement',    'token_value':  '30'},
    {'token_type': 'Expression',  'token_value':  'Ke2'},
    {'token_type': 'Expression',  'token_value':  'Rd4'},
    {'token_type': 'Movement',    'token_value':  '31'},
    {'token_type': 'Expression',  'token_value':  'Qc7'},
    {'token_type': 'Expression',  'token_value':  'Rxd3'},
    {'token_type': 'Movement',    'token_value':  '32'},
    {'token_type': 'Expression',  'token_value':  'Rxd3'},
    {'token_type': 'Expression',  'token_value':  'Qxf2+'},
    {'token_type': 'Movement',    'token_value':  '33'},
    {'token_type': 'Expression',  'token_value':  'Kd1'},
    {'token_type': 'Expression',  'token_value':  'Qf1+'},
    {'token_type': 'WhiteSpace',    'token_value':  ''},
    {'token_type': 'Expression',  'token_value':  '0-1'},
    {'token_type': 'WhiteSpace',    'token_value':  ''},
    {'token_type': 'Operator',    'token_value':  '['},
    {'token_type': 'Identifier',  'token_value':  'Event'},
    {'token_type': 'String',      'token_value':  'GBR-ch 58th'},
    {'token_type': 'Operator',    'token_value':  ']'},
    {'token_type': 'Operator',    'token_value':  '['},
    {'token_type': 'Identifier',  'token_value':  'Site'},
    {'token_type': 'String',      'token_value':  'Blackpool'},
    {'token_type': 'Operator',    'token_value':  ']'},
    {'token_type': 'Operator',    'token_value':  '['},
    {'token_type': 'Identifier',  'token_value':  'Date'},
    {'token_type': 'String',      'token_value':  '1971.08.13'},
    {'token_type': 'Operator',    'token_value':  ']'},
    {'token_type': 'Operator',    'token_value':  '['},
    {'token_type': 'Identifier',  'token_value':  'Round'},
    {'token_type': 'String',      'token_value':  '5'},
    {'token_type': 'Operator',    'token_value':  ']'},
    {'token_type': 'Operator',    'token_value':  '['},
    {'token_type': 'Identifier',  'token_value':  'White'},
    {'token_type': 'String',      'token_value':  'Wade, Robert'},
    {'token_type': 'Operator',    'token_value':  ']'},
    {'token_type': 'Operator',    'token_value':  '['},
    {'token_type': 'Identifier',  'token_value':  'Black'},
    {'token_type': 'String',      'token_value':  'Littlewood, John Eric'},
    {'token_type': 'Operator',    'token_value':  ']'},
    {'token_type': 'Operator',    'token_value':  '['},
    {'token_type': 'Identifier',  'token_value':  'Result'},
    {'token_type': 'String',      'token_value':  '0-1'},
    {'token_type': 'Operator',    'token_value':  ']'},
    {'token_type': 'Operator',    'token_value':  '['},
    {'token_type': 'Identifier',  'token_value':  'WhiteElo'},
    {'token_type': 'String',      'token_value':  '2365'},
    {'token_type': 'Operator',    'token_value':  ']'},
    {'token_type': 'Operator',    'token_value':  '['},
    {'token_type': 'Identifier',  'token_value':  'BlackElo'},
    {'token_type': 'String',      'token_value':  '2310'},
    {'token_type': 'Operator',    'token_value':  ']'},
    {'token_type': 'Operator',    'token_value':  '['},
    {'token_type': 'Identifier',  'token_value':  'ECO'},
    {'token_type': 'String',      'token_value':  'D80'},
    {'token_type': 'Operator',    'token_value':  ']'},
    {'token_type': 'Operator',    'token_value':  '['},
    {'token_type': 'Identifier',  'token_value':  'EventDate'},
    {'token_type': 'String',      'token_value':  '1971.08.09'},
    {'token_type': 'Operator',    'token_value':  ']'},
    {'token_type': 'Operator',    'token_value':  '['},
    {'token_type': 'Identifier',  'token_value':  'PlyCount'},
    {'token_type': 'String',      'token_value':  '94'},
    {'token_type': 'Operator',    'token_value':  ']'},
    {'token_type': 'Operator',    'token_value':  '['},
    {'token_type': 'Identifier',  'token_value':  'EventType'},
    {'token_type': 'String',      'token_value':  'swiss'},
    {'token_type': 'Operator',    'token_value':  ']'},
    {'token_type': 'Operator',    'token_value':  '['},
    {'token_type': 'Identifier',  'token_value':  'EventRounds'},
    {'token_type': 'String',      'token_value':  '11'},
    {'token_type': 'Operator',    'token_value':  ']'},
    {'token_type': 'Operator',    'token_value':  '['},
    {'token_type': 'Identifier',  'token_value':  'EventCountry'},
    {'token_type': 'String',      'token_value':  'GBR'},
    {'token_type': 'Operator',    'token_value':  ']'},
        {'token_type': 'WhiteSpace',    'token_value':  ''},
    {'token_type': 'Movement',    'token_value':  '1'},
    {'token_type': 'Expression',  'token_value':  'd4'},
    {'token_type': 'Expression',  'token_value':  'Nf6'},
    {'token_type': 'Movement',    'token_value':  '2'},
    {'token_type': 'Expression',  'token_value':  'c4'},
    {'token_type': 'Expression',  'token_value':  'g6'},
    {'token_type': 'Movement',    'token_value':  '3'},
    {'token_type': 'Expression',  'token_value':  'Nc3'},
    {'token_type': 'Expression',  'token_value':  'd5'},
    {'token_type': 'Movement',    'token_value':  '4'},
    {'token_type': 'Expression',  'token_value':  'Bg5'},
    {'token_type': 'Expression',  'token_value':  'Ne4'},
    {'token_type': 'Movement',    'token_value':  '5'},
    {'token_type': 'Expression',  'token_value':  'Bh4'},
    {'token_type': 'Expression',  'token_value':  'Bg7'},
    {'token_type': 'Movement',    'token_value':  '6'},
    {'token_type': 'Expression',  'token_value':  'e3'},
    {'token_type': 'Expression',  'token_value':  'c5'},
    {'token_type': 'Movement',    'token_value':  '7'},
    {'token_type': 'Expression',  'token_value':  'cxd5'},
    {'token_type': 'Expression',  'token_value':  'Nxc3'},
    {'token_type': 'Movement',    'token_value':  '8'},
    {'token_type': 'Expression',  'token_value':  'bxc3'},
    {'token_type': 'Expression',  'token_value':  'cxd4'},
    {'token_type': 'Movement',    'token_value':  '9'},
    {'token_type': 'Expression',  'token_value':  'cxd4'},
    {'token_type': 'Expression',  'token_value':  'Qxd5'},
    {'token_type': 'Movement',    'token_value':  '10'},
    {'token_type': 'Expression',  'token_value':  'Nf3'},
    {'token_type': 'Expression',  'token_value':  'Nc6'},
    {'token_type': 'Movement',    'token_value':  '11'},
    {'token_type': 'Expression',  'token_value':  'Qa4'},
    {'token_type': 'Expression',  'token_value':  'O-O'},
    {'token_type': 'Movement',    'token_value':  '12'},
    {'token_type': 'Expression',  'token_value':  'Qb5'},
    {'token_type': 'Expression',  'token_value':  'Qe4'},
    {'token_type': 'Movement',    'token_value':  '13'},
    {'token_type': 'Expression',  'token_value':  'Be2'},
    {'token_type': 'Expression',  'token_value':  'e5'},
    {'token_type': 'Movement',    'token_value':  '14'},
    {'token_type': 'Expression',  'token_value':  'd5'},
    {'token_type': 'Expression',  'token_value':  'Nb4'},
    {'token_type': 'Movement',    'token_value':  '15'},
    {'token_type': 'Expression',  'token_value':  'O-O'},
    {'token_type': 'Expression',  'token_value':  'Nxd5'},
    {'token_type': 'Movement',    'token_value':  '16'},
    {'token_type': 'Expression',  'token_value':  'Rac1'},
    {'token_type': 'Expression',  'token_value':  'a6'},
    {'token_type': 'Movement',    'token_value':  '17'},
    {'token_type': 'Expression',  'token_value':  'Qb3'},
    {'token_type': 'Expression',  'token_value':  'Be6'},
    {'token_type': 'Movement',    'token_value':  '18'},
    {'token_type': 'Expression',  'token_value':  'Rc4'},
    {'token_type': 'Expression',  'token_value':  'Nf4'},
    {'token_type': 'Movement',    'token_value':  '19'},
    {'token_type': 'Expression',  'token_value':  'Rxe4'},
    {'token_type': 'Expression',  'token_value':  'Nxe2+'},
    {'token_type': 'Movement',    'token_value':  '20'},
    {'token_type': 'Expression',  'token_value':  'Kh1'},
    {'token_type': 'Expression',  'token_value':  'Bxb3'},
    {'token_type': 'Movement',    'token_value':  '21'},
    {'token_type': 'Expression',  'token_value':  'axb3'},
    {'token_type': 'Expression',  'token_value':  'b5'},
    {'token_type': 'Movement',    'token_value':  '22'},
    {'token_type': 'Expression',  'token_value':  'Be7'},
    {'token_type': 'Expression',  'token_value':  'Rfe8'},
    {'token_type': 'Movement',    'token_value':  '23'},
    {'token_type': 'Expression',  'token_value':  'Bb4'},
    {'token_type': 'Expression',  'token_value':  'f5'},
    {'token_type': 'Movement',    'token_value':  '24'},
    {'token_type': 'Expression',  'token_value':  'Rh4'},
    {'token_type': 'Expression',  'token_value':  'Bf6'},
    {'token_type': 'Movement',    'token_value':  '25'},
    {'token_type': 'Expression',  'token_value':  'Rh3'},
    {'token_type': 'Expression',  'token_value':  'a5'},
    {'token_type': 'Movement',    'token_value':  '26'},
    {'token_type': 'Expression',  'token_value':  'Bd2'},
    {'token_type': 'Expression',  'token_value':  'b4'},
    {'token_type': 'Movement',    'token_value':  '27'},
    {'token_type': 'Expression',  'token_value':  'e4'},
    {'token_type': 'Expression',  'token_value':  'fxe4'},
    {'token_type': 'Movement',    'token_value':  '28'},
    {'token_type': 'Expression',  'token_value':  'Ng5'},
    {'token_type': 'Expression',  'token_value':  'Bxg5'},
    {'token_type': 'Movement',    'token_value':  '29'},
    {'token_type': 'Expression',  'token_value':  'Bxg5'},
    {'token_type': 'Expression',  'token_value':  'Rac8'},
    {'token_type': 'Movement',    'token_value':  '30'},
    {'token_type': 'Expression',  'token_value':  'Re3'},
    {'token_type': 'Expression',  'token_value':  'Nd4'},
    {'token_type': 'Movement',    'token_value':  '31'},
    {'token_type': 'Expression',  'token_value':  'h4'},
    {'token_type': 'Expression',  'token_value':  'h6'},
    {'token_type': 'Movement',    'token_value':  '32'},
    {'token_type': 'Expression',  'token_value':  'Bxh6'},
    {'token_type': 'Expression',  'token_value':  'Nf5'},
    {'token_type': 'Movement',    'token_value':  '33'},
    {'token_type': 'Expression',  'token_value':  'Bg5'},
    {'token_type': 'Expression',  'token_value':  'Nxe3'},
    {'token_type': 'Movement',    'token_value':  '34'},
    {'token_type': 'Expression',  'token_value':  'fxe3'},
    {'token_type': 'Expression',  'token_value':  'Rf8'},
    {'token_type': 'Movement',    'token_value':  '35'},
    {'token_type': 'Expression',  'token_value':  'Ra1'},
    {'token_type': 'Expression',  'token_value':  'Rc3'},
    {'token_type': 'Movement',    'token_value':  '36'},
    {'token_type': 'Expression',  'token_value':  'Rxa5'},
    {'token_type': 'Expression',  'token_value':  'Rxb3'},
    {'token_type': 'Movement',    'token_value':  '37'},
    {'token_type': 'Expression',  'token_value':  'Rxe5'},
    {'token_type': 'Expression',  'token_value':  'Rd3'},
    {'token_type': 'Movement',    'token_value':  '38'},
    {'token_type': 'Expression',  'token_value':  'Rb5'},
    {'token_type': 'Expression',  'token_value':  'b3'},
    {'token_type': 'Movement',    'token_value':  '39'},
    {'token_type': 'Expression',  'token_value':  'Kg1'},
    {'token_type': 'Expression',  'token_value':  'Rc8'},
    {'token_type': 'Movement',    'token_value':  '40'},
    {'token_type': 'Expression',  'token_value':  'Rb7'},
    {'token_type': 'Expression',  'token_value':  'Rc2'},
    {'token_type': 'Movement',    'token_value':  '41'},
    {'token_type': 'Expression',  'token_value':  'Kh2'},
    {'token_type': 'Expression',  'token_value':  'b2'},
    {'token_type': 'Movement',    'token_value':  '42'},
    {'token_type': 'Expression',  'token_value':  'Bf6'},
    {'token_type': 'Expression',  'token_value':  'Rdd2'},
    {'token_type': 'Movement',    'token_value':  '43'},
    {'token_type': 'Expression',  'token_value':  'Kg3'},
    {'token_type': 'Expression',  'token_value':  'Rxg2+'},
    {'token_type': 'Movement',    'token_value':  '44'},
    {'token_type': 'Expression',  'token_value':  'Kf4'},
    {'token_type': 'Expression',  'token_value':  'Rcf2+'},
    {'token_type': 'Movement',    'token_value':  '45'},
    {'token_type': 'Expression',  'token_value':  'Ke5'},
    {'token_type': 'Expression',  'token_value':  'Rg1'},
    {'token_type': 'Movement',    'token_value':  '46'},
    {'token_type': 'Expression',  'token_value':  'Rb8+'},
    {'token_type': 'Expression',  'token_value':  'Kf7'},
    {'token_type': 'Movement',    'token_value':  '47'},
    {'token_type': 'Expression',  'token_value':  'Rb7+'},
    {'token_type': 'Expression',  'token_value':  'Ke8'},
    {'token_type': 'WhiteSpace',    'token_value':  ''},
    {'token_type': 'Expression',  'token_value':  '0-1'},
     {'token_type': 'WhiteSpace',    'token_value':  ''},
       
]
Parser(lexerExpressionList)