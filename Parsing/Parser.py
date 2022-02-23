from typing import Callable
from Parsing import ParserConstants
from LexerTests.Lexer import Lexer
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

## TODO: Make all Exceptions, "UnknownParserError"s
class Node:
    count = 0
    
    def __init__(self, nodeName: str = 'root', nodeInfo: dict = None) -> None:
        Node.count+=1

        self.nodeName = nodeName
        self.nodeParent = None
        self.nodeInfo = nodeInfo
        self.nodes = []
        self.id = Node.count
    
    def showNode(self) -> None:
        print(f'{self.nodeParent.nodeName} -> {self.nodeName}')
        #print(self.nodeInfo)
        #print(f'Parent: {self.nodeParent.nodeName}')  
        for node in self.nodes:
            node.showNode()

    def findNodeById(self, searchId: int) -> 'Node':
        if (self.id == searchId):
            return self
        
        for node in self.nodes:
            found = node.findNodeById(searchId) 
            if found:
                return found
            
    def postOrderTraversal(self, func: Callable) -> None:
        currentNode = self
        for node in self.nodes:
            node.postOrderTraversal(func)

        func(currentNode)
        
class Tree:
    def __init__(self, treeName: str = '', rootNode=None) -> None:
        self.treeName = treeName
        self.currentNode = rootNode
        self.rootNode = rootNode
        self.shouldMark = False
        self.currentMarkingPosition = 0
        self.markedNodeMap = {}
        self.grammarMap = {}
    
    def showTree(self) -> None:
        for node in self.rootNode.nodes:
            node.showNode()

    def insertNode(self, node: Node) -> None:
        assert(isinstance(node, Node))
        self.currentNode.nodes.append(node)
        node.nodeParent = self.currentNode
        self.currentNode = node

        if self.shouldMark:
            self.markedNodeMap[self.currentMarkingPosition].append(node.id)

    def addReferenceToGrammarMap(self) -> None:
        self.grammarMap[self.currentNode.nodeName] = self.currentNode
        
    def resetGrammarMap(self) -> None:
        for nodeName in self.grammarMap.keys():
            self.grammarMap[nodeName] = None
         
    def goTo(self, nodeName) -> None:
        if (nodeName in self.grammarMap):
            self.currentNode = self.grammarMap[nodeName]
        else:
            raise Exception("This grammar node wasn't found")    
    
    def goToRoot(self) -> None:
        self.currentNode = self.rootNode
    
    def postOrderTraversal(self, func) -> None:
        self.rootNode.postOrderTraversal(func)
    
    def findNodeById(self, nodeId: int) -> Node:
        return self.rootNode.findNodeById(nodeId) 
        
    def removeNode(self, nodeId: int) -> None:
        nodeToRemove = self.findNodeById(nodeId)   
        nodeToRemove.nodeParent.nodes.remove(nodeToRemove)

    def startMarking(self, currentMarkingPosition) -> None:
        self.shouldMark = True
        self.currentMarkingPosition = currentMarkingPosition
        self.markedNodeMap[self.currentMarkingPosition] = []

    def stopMarking(self) -> None:
        self.shouldMark = False
        self.currentMarkingPosition = 0

    def removeMarkedNodes(self) -> None:
        if self.markedNodeMap[self.currentMarkingPosition] is not None:
            self.markedNodeMap[self.currentMarkingPosition].sort(reverse=True)
            
            for nodeId in self.markedNodeMap[self.currentMarkingPosition]:
                self.removeNode(nodeId)
            
        self.clearMarkedNodeStack()
    
    def clearMarkedNodeStack(self) -> None:
        if (self.currentMarkingPosition in self.markedNodeMap):
            del self.markedNodeMap[self.currentMarkingPosition]  

# Κλάσεις για διαχείρηση σφαλμάτων

class ParseError(Exception):
    def __init__(self, message:str) -> None:
        super().__init__(f'ParseError: {message}')

class SyntaxError(ParseError):
    def __init__(self, tokenIndex: int, line: int, position: int, expected: str, got: str) -> None:
        self.message = f'SyntaxError on token #{tokenIndex} (Line: {line}, Position: {position}). Expected {expected}, got {got}'
        super().__init__(self.message)

class LogicError(ParseError):
    def __init__(self, tokenIndex: int, line: int, position: int, errorMessage: str) -> None:
        self.message = f'LogicError on token #{tokenIndex} (Line: {line}, Position: {position}). {errorMessage}'
        super().__init__(self.message)

class Parser:
    """Απλή υλοποίηση ενός Recursive Descent Parser"""
    def __init__(self, Lexer: Lexer):
        self.Lexer = Lexer
        self.usedTagIdentifiers = set()
        
        self.parseTree = Tree('Parse Tree',  Node('root'))
        self.AST = []
        self.buildParseTree()
        self.parseTree.showTree()
        self.buildAST()

# Μέθοδοι για το διάβασμα token από τον Lexer
    def nextToken(self) -> None:
        self.Lexer.MoveNext()
        token = self.Lexer.GetToken

        if (token['token_type'] == 'COMMENT'):
            self.nextToken()

    def currentToken(self) -> dict:
        return self.Lexer.GetToken

# Μέθοδοι που ελέγχουν αν το επόμενο token έχει συγκεκριμένη τιμή
    def expectType(self, expectedTokenType: str) -> None:
        currentToken = self.currentToken()
        if (currentToken['token_type'] != expectedTokenType):
            raise SyntaxError(self.Lexer.index, currentToken['Line'], currentToken['Position'], expectedTokenType, currentToken['token_type'])            

    def expectValue(self, expectedTokenValue: str) -> None:
        currentToken = self.currentToken()
        if (currentToken['token_value'] != expectedTokenValue):
            raise SyntaxError(self.Lexer.index, currentToken['Line'], currentToken['Position'], expectedTokenValue, currentToken['token_value'])      

    def maybe(self, listOfFunctions: list) -> None:
        lastPosition = self.Lexer.index
        for index, func in enumerate(listOfFunctions):
            try:
                self.parseTree.startMarking(lastPosition)
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
# Οι παρακάτω μέθοδοι χτίζουν το Parse Tree
    def buildParseTree(self) -> None:
        self.PGNDatabase()

    def PGNDatabase(self) -> None:
        self.parseTree.insertNode(Node('PGNDatabase'))
        self.parseTree.addReferenceToGrammarMap()
        self.PGNGame()
        self.nextToken() 
        if (not self.Lexer.EOF):
            self.parseTree.goTo('PGNDatabase')
            self.PGNDatabase()
            self.parseTree.resetGrammarMap()
    
    def PGNGame(self) -> None:
        self.parseTree.insertNode(Node('PGNGame'))
        self.parseTree.addReferenceToGrammarMap()
        self.TagSection()
        
        self.parseTree.goTo('PGNGame')
        
        self.nextToken()     
        self.MoveTextSection()

    def TagSection(self) -> None:
        currentToken = self.currentToken()
        if (currentToken['token_type'] != 'EMPTY'):
            self.parseTree.insertNode(Node('TagSection'))
            self.parseTree.addReferenceToGrammarMap()
            self.TagPair()
            
            self.parseTree.goTo('TagSection')
            
            self.nextToken() 
            self.TagSection()
        else:
            # Ολοκληρώθηκαν τα TagSection, οπότε κάνουμε έλεγχο αν υπάρχουν τα 
            # required Tag Identifiers
                
            if (not ParserConstants.REQUIRED_TAG_IDENTIFIERS.issubset(self.usedTagIdentifiers)):
                raise LogicError(self.Lexer.index, currentToken['Line'], currentToken['Position'], 'Missing required Tags.')                   
                
            self.usedTagIdentifiers = set()
            
            self.parseTree.goTo('TagSection')
            self.Empty()

    def TagPair(self) -> None:
        self.parseTree.insertNode(Node('TagPair'))
        self.parseTree.addReferenceToGrammarMap()
        self.expectValue('[')

        self.nextToken()
        self.TagName()
        self.parseTree.goTo('TagPair')
        
        self.nextToken()     
        self.TagValue()

        self.nextToken()    
        self.expectValue(']')

    def TagName(self) -> None:
        self.expectType('IDENTIFIER')
        currentToken = self.currentToken()
        tagIdentifier = currentToken['token_value']
        self.parseTree.insertNode(Node('TagName', currentToken))
        
        if (tagIdentifier in self.usedTagIdentifiers):
            raise LogicError(self.Lexer.index, currentToken['Line'], currentToken['Position'], f'Tag Identifier {tagIdentifier} has already been used.')
        
        if (tagIdentifier not in ParserConstants.VALID_TAG_IDENTIFIERS):
            raise LogicError(self.Lexer.index, currentToken['Line'], currentToken['Position'], f'Tag Identifier {tagIdentifier} is not a valid tag identifier.')
        else:
            self.usedTagIdentifiers.add(tagIdentifier)

    def TagValue(self) -> None:
        self.expectType('STRING')
        token = self.currentToken()
        self.parseTree.insertNode(Node('TagValue', token))
    
    def MoveTextSection(self) -> None:
        self.parseTree.insertNode(Node('MoveTextSection'))
        self.parseTree.addReferenceToGrammarMap()
        self.ElementSequence()
        
        self.parseTree.goTo('MoveTextSection')
        self.GameTermination()
        self.nextToken()

    def ElementSequence(self) -> None:
        currentToken = self.currentToken()
        if (currentToken['token_type'] != 'GAME_END'):
            self.parseTree.insertNode(Node('ElementSequence'))
            self.parseTree.addReferenceToGrammarMap()
            self.maybe([self.Element, self.RecursiveVariation])
            
            self.parseTree.goTo('ElementSequence')
            self.nextToken()
            self.ElementSequence()    

    def Element(self) -> None:
        self.parseTree.insertNode(Node('Element'))
        self.maybe([self.MoveNumberIndication, self.SANMove, self.NumericAnnotationGlyph])

    def MoveNumberIndication(self) -> None:
        currentToken = self.currentToken()
        self.expectType('MOVEMENT')
        self.parseTree.insertNode(Node('MoveNumberIndication', currentToken))

    def SANMove(self) -> None:
        currentToken = self.currentToken()
        self.parseTree.insertNode(Node('SANMove', currentToken))
        # Χρήση RegEx για αναγνώριση κινήσεων.
        self.expectType('EXPRESSION')
        SANMoveRegEx = r"(..)?([NBRQK])?([a-h])?([1-8])?(x)?([a-h][1-8])(=[NBRQ])?(\+|#)?$|^O-O(-O)?"
        if (not re.match(SANMoveRegEx, currentToken['token_value'])):
            raise ParseError('Invalid move', currentToken['Line'], currentToken['Position'],  currentToken['token_value'])

    def NumericAnnotationGlyph(self) -> None:
        currentToken = self.currentToken()
        self.expectType('EXPRESSION')
        self.parseTree.insertNode(Node('NumericAnnotationGlyph', currentToken)) 
        NAGRegEx = r"\$[1-255]"
        if (not re.fullmatch(NAGRegEx, currentToken['token_value'])):
            raise ParseError('Invalid move', currentToken['Line'], currentToken['Position'], currentToken['token_value'])

    def RecursiveVariation(self) -> None:
        self.parseTree.insertNode(Node('RecursiveVariation'))
        self.expectValue("(")
        self.nextToken()
        self.ElementSequence()
        self.nextToken()
        self.expectValue(")") 

    def GameTermination(self) -> None:
        token = self.currentToken()
        self.parseTree.insertNode(Node('GameTermination', token))
        
    def Empty(self) -> None:
        self.parseTree.insertNode(Node('E'))

## Οι παρακάτω μέθοδοι χτίζουν το AST
    def buildAST(self) -> None:
        self.parseTree.postOrderTraversal(self.createASTNode)
    
    def createASTNode(self, node):
        # ASTNodeGenerationMap = {
        #     'PGNGame' : None
        # }
        # if node:
        #    print(node.nodeName) 
        pass
            
                         