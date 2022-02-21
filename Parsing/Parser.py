from Parsing import ParserConstants
import re

## Η γραμματική του PGN εκφρασμένη σε BNF. 
## Την γραμματική την βρήκαμε στο 

# <PGN-database>:= <PGN-game> <PGN-database>
#                    <empty>
# <PGN-game>:= <tag-section> <movetext-section>
# <tag-section>:= <tag-pair> <tag-section>
#                   <empty>
# <tag-pair>:= [ <tag-name> <tag-value> ]
# <tag-name>:= <identifier>
# <tag-value>:= <string>
# <movetext-section>:= <element-sequence> <game-termination>
# <element-sequence>:= <element> <element-sequence>
#                        <recursive-variation> <element-sequence>
#                        <empty>
# <element>:= <move-number-indication>
#               <SAN-move>
#               <numeric-annotation-glyph>
# <recursive-variation>:= ( <element-sequence> )
# <game-termination>:= 1-0
#                        0-1
#                        1/2-1/2
#                        *
# <empty>:=
class Tree:
    
    def __init__(self, treeName='', rootNode=None):
        self.treeName = treeName
        self.currentNode = rootNode
        self.rootNode = rootNode
        self.shouldMark = False
        self.markedNodeStack = []
    
    def showTree(self):
        for node in self.rootNode.nodes:
            node.showNode()

    def insertNode(self, node):
        assert(isinstance(node, Node))
        node.nodeParent = self.currentNode
        self.currentNode.nodes.append(node)
        self.currentNode = node

        if self.shouldMark:
            self.markedNodeStack.append(node.id)

    def goToParent(self):
        self.currentNode = self.currentNode.getParent()

    def findNodeById(self, nodeId):
        return self.rootNode.findNodeById(nodeId)

    def removeNode(self, nodeId):
        nodeToRemove = self.findNodeById(nodeId)   
        nodeToRemove.nodeParent.nodes.remove(nodeToRemove)

    def startMarking(self):
        self.shouldMark = True

    def stopMarking(self):
        self.shouldMark = False

    def removeMarkedNodes(self):
        for nodeId in self.markedNodeStack:
            self.removeNode(nodeId)

        self.clearMarkedNodeStack()
    
    def clearMarkedNodeStack(self):
        self.markedNodeStack = []    

class Node:
    count = 0
    
    def __init__(self, nodeName='root', nodeInfo=None):
        Node.count+=1

        self.nodeName = nodeName
        self.nodeParent = None
        self.nodeInfo = nodeInfo
        self.nodes = []
        self.id = Node.count
    
    def showNode(self):
        print(self.nodeName)     
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
        super().__init__(f'ParseError: '+message)

class SyntaxError(ParseError):
    def __init__(self, tokenIndex, expected, got):
        self.message = f'SyntaxError on token #{tokenIndex}. Expected {expected}, got {got}'
        super().__init__(self.message)

class LogicError(ParseError):
    def __init__(self, tokenIndex, errorMessage):
        self.message = f'LogicError on token #{tokenIndex}. {errorMessage}'
        super().__init__(self.message)

class Parser:
    """Απλή υλοποίηση ενός Recursive Descent Parser"""
    def __init__(self, Lexer):
        self.Lexer = Lexer
        self.parseTree = Tree('Parse Tree',  Node('root'))
        self.usedTagIdentifiers = set()

        self.start()
        self.parseTree.showTree()

# Μέθοδοι για το διάβασμα token από τον Lexer
    def nextToken(self):
        self.Lexer.MoveNext()
        token = self.Lexer.GetToken

        if (token['token_type'] == 'COMMENT'):
            self.nextToken()

    def currentToken(self):
        return self.Lexer.GetToken

# Μέθοδοι που ελέγχουν αν το επόμενο token έχει συγκεκριμένη τιμή
    def expectType(self, expectedTokenType):
        currentToken = self.currentToken()
        if (currentToken['token_type'] != expectedTokenType):
            raise SyntaxError(self.Lexer.index, expectedTokenType, currentToken['token_type'])            

    def expectValue(self, expectedTokenValue):
        currentToken = self.currentToken()
        if (currentToken['token_value'] != expectedTokenValue):
            raise SyntaxError(self.Lexer.index, expectedTokenValue, currentToken['token_value'])      

    def maybe(self, listOfFunctions):
        lastPosition = self.Lexer.index
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

                self.Lexer.index = lastPosition
                continue     
            else:
                # Αν εκτελεστεί το παραπάνω χωρίς ParseError, τότε, απλά φεύγουμε απ'την επανάληψη
                self.parseTree.clearMarkedNodeStack()
                break
        
# Μέθοδοι που διέπουν το Recursive Descent μέρος του Parser
# εφαρμόζοντας την γραμματική στο BNF που βρήκαμε.
    def start(self):
        self.PGNDatabase()

    def PGNDatabase(self):
        # Για την αποφυγή του backtracking, αντί να προσπαθήσουμε πρώτα να matchάρουμε τον <empty> κανόνα
        # και ύστερα τους παραγωγικούς κανόνες <PGN Game> <PGN Database>, απλά θέτουμε ότι αν δεν είναι WhiteSpace χαρακτήρας,
        # ισχύουν οι κανόνες <PGN Game> <PGN Database>
        self.parseTree.insertNode(Node('PGNDatabase'))
        self.PGNGame()
        if (not self.Lexer.EOF): 
            self.nextToken() 
            self.PGNDatabase()
        
        self.parseTree.goToParent() 
    
    def PGNGame(self):
        self.parseTree.insertNode(Node('PGNGame'))
        self.TagSection()

        self.nextToken()     
        self.MoveTextSection()
        self.parseTree.goToParent()

    def TagSection(self):
        if (self.currentToken()['token_type'] != 'EMPTY'):
            self.parseTree.insertNode(Node('TagSection'))
            self.TagPair()

            self.nextToken() 
            self.TagSection()
        else:
            # Ολοκληρώθηκαν τα TagSection, οπότε κάνουμε έλεγχο αν υπάρχουν τα 
            # required Tag Identifiers
            
            if (not ParserConstants.REQUIRED_TAG_IDENTIFIERS.issubset(self.usedTagIdentifiers)):
                raise LogicError(self.Lexer.index, 'Missing required Tags.')                   
            
            self.usedTagIdentifiers = set()

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
        self.expectType('IDENTIFIER')
        token = self.currentToken()
        tagIdentifier = token['token_value']
        self.parseTree.insertNode(Node('TagName', token))
        
        if (tagIdentifier in self.usedTagIdentifiers):
            raise LogicError(self.Lexer.index, f'Tag Identifier {tagIdentifier} has already been used.')
        
        if (tagIdentifier not in ParserConstants.VALID_TAG_IDENTIFIERS):
            raise LogicError(self.Lexer.index, f'Tag Identifier {tagIdentifier} is not a valid tag identifier.')
        else:
            self.usedTagIdentifiers.add(tagIdentifier)

        self.parseTree.goToParent()

    def TagValue(self):
        self.expectType('STRING')
        token = self.currentToken()
        self.parseTree.insertNode(Node('TagValue', token))
        self.parseTree.goToParent()
    
    def MoveTextSection(self):
        self.parseTree.insertNode(Node('MoveTextSection'))
        self.ElementSequence()
        self.GameTermination()
        self.nextToken()
        self.parseTree.goToParent()

    def ElementSequence(self):
        currentToken = self.currentToken()
        if (currentToken['token_type'] != 'GAME_END'):
            self.parseTree.insertNode(Node('ElementSequence'))
            self.maybe([self.Element, self.RecursiveVariation])
            self.nextToken()
            self.ElementSequence()

        self.parseTree.goToParent()

    def Element(self):
        self.maybe([self.MoveNumberIndication, self.SANMove, self.NumericAnnotationGlyph])

    def MoveNumberIndication(self):
        currentToken = self.currentToken()
        self.expectType('MOVEMENT')
        self.parseTree.insertNode(Node('Movement', currentToken))

    def SANMove(self):
        currentToken = self.currentToken()
        # Χρήση RegEx για αναγνώριση κινήσεων.
        self.expectType('EXPRESSION')
        SANMoveRegEx = r"(..)?([NBRQK])?([a-h])?([1-8])?(x)?([a-h][1-8])(=[NBRQ])?(\+|#)?$|^O-O(-O)?"
        if (not re.match(SANMoveRegEx, currentToken['token_value'])):
            raise ParseError('Invalid move')

        self.parseTree.insertNode(Node('SANMove', currentToken))
        self.parseTree.goToParent()

    def NumericAnnotationGlyph(self):
        currentToken = self.currentToken()
        self.expectType('EXPRESSION')
        NAGRegEx = r"\$[1-255]"
        if (not re.fullmatch(NAGRegEx, currentToken['token_value'])):
            raise ParseError('Invalid move')

        self.parseTree.insertNode(Node('NumericAnnotationGlyph', currentToken))  
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
        
        self.parseTree.insertNode(Node('GameTermination', token))
        self.parseTree.goToParent()
        
    def Empty(self):
        self.parseTree.insertNode(Node('E'))

        self.parseTree.goToParent()
