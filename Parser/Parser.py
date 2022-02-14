import ParserConstants

## Η γραμματική του PGN εκφρασμένη σε BNF.
## Την γραμματική την βρήκαμε στο 

# <PGN-database> ::= <PGN-game> <PGN-database>
#                    <empty>
# <PGN-game> ::= <tag-section> <movetext-section>
# <tag-section> ::= <tag-pair> <tag-section>
#                   <empty>
# <tag-pair> ::= [ <tag-name> <tag-value> ]
# <tag-name> ::= <identifier>
# <tag-value> ::= <string>
# <movetext-section> ::= <element-sequence> <game-termination>
# <element-sequence> ::= <element> <element-sequence>
#                        <recursive-variation> <element-sequence>
#                        <empty>
# <element> ::= <move-number-indication>
#               <SAN-move>
#               <numeric-annotation-glyph>
# <recursive-variation> ::= ( <element-sequence> )
# <game-termination> ::= 1-0
#                        0-1
#                        1/2-1/2
#                        *
# <empty> ::=

class Tree:
    # Βασική υλοποίηση ενός δέντρου. Χρησιμοποιείται για την παραγωγή του Parser Tree.
    def __init__(self, nodeName='root', nodes=None, nodeInfo=None):
        self.nodeName = nodeName
        self.nodeParent = None
        self.nodeInfo = nodeInfo
        self.nodes = []
        if nodes != None:
            for node in nodes:
                self.insert_node(node)

    def insert_node(self, node):
        assert(isinstance(node, Tree))
        node.nodeParent = self
        self.nodes.append(node)

    def find_node(self, nodeName):
        if self.nodeName == nodeName:
            print(nodeName)
            return self

        for node in self.nodes:
            foundNode = node.find_node(nodeName)
            if foundNode is not None:
                return foundNode

    def show_tree(self):
        print('Node name:\t', self.nodeName)     
        print('Node info:\t', self.nodeInfo) 
        for node in self.nodes:
            node.show_tree()

    def get_parent(self):
        return self.nodeParent

# Κλάσεις για διαχείρηση σφαλμάτων
class SyntacticalError(Exception):
    def __init__(self, tokenIndex, expected, got):
        self.message = f'SyntacticalError on token #{tokenIndex}. Expected {expected}, got {got}'
        super().__init__(self.message)

class SemanticalError(Exception):
    def __init__(self, tokenIndex, errorMessage):
        self.message = f'SyntacticalError on token #{tokenIndex}. {errorMessage}'
        super().__init__(self.message)

class Parser:
    """Απλή υλοποίηση ενός Recursive Descent Parser"""
    def __init__(self, lexerExpressionList):
        self.lexerExpressionList = lexerExpressionList
        self.currentPos = 0
        self.streamLen = len(self.lexerExpressionList)
        self.parseTree = Tree('root')
        self.currentNode = self.parseTree
        self.usedTagIdentifiers = []

        self.start()
        self.parseTree.show_tree()

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

# Μέθοδοι που διέπουν το Recursive Descent μέρος του Parser
#  εφαρμόζοντας την γραμματική στο BNF που βρήκαμε.
    def start(self):
        if (not self.PGNDatabase()):
            return False

        return True

    def PGNDatabase(self):
        if (self.currentNode == None):
            print('Finished Parsing!!')
            return False

        self.currentNode.insert_node(Tree('PGNDatabase'))
        self.currentNode = self.currentNode.find_node('PGNDatabase')
        currentToken = self.currentToken()
        if (currentToken['token_type'] != 'WhiteSpace'):
            if (not self.PGNGame()):
                return False
            self.nextToken()    
            if (not self.PGNDatabase()):
                return False
        else:
          self.Empty()
          self.currentNode = self.currentNode.get_parent()              
        
        return True        
    
    def PGNGame(self):
        self.currentNode.insert_node(Tree('PGNGame'))
        self.currentNode = self.currentNode.find_node('PGNGame')

        if (not self.TagSection()):
            return False
        self.nextToken()     
        if (not self.MoveTextSection()):
            return False

        self.currentNode = self.currentNode.get_parent()
        return True

    def TagSection(self):
        self.currentNode.insert_node(Tree('TagSection'))
        self.currentNode = self.currentNode.find_node('TagSection')

        currentToken = self.currentToken()
        if (currentToken['token_type'] != 'WhiteSpace'):
            if (not self.TagPair()):
                return False
            self.nextToken() 
            if (not self.TagSection()):
                return False
        else:
            self.Empty()
            self.currentNode = self.currentNode.get_parent()    
        return True

    def TagPair(self):
        self.currentNode.insert_node(Tree('TagPair'))
        self.currentNode = self.currentNode.find_node('TagPair')
        self.expectValue('[')
        self.nextToken()
        if (not self.TagName()):
            return False
        self.nextToken()     
        if (not self.TagValue()):
            return False

        self.nextToken()    
        self.expectValue(']')
        self.currentNode = self.currentNode.get_parent() 
        return True

    def TagName(self):
        self.expectType('Identifier')
        token = self.currentToken()
        tagIdentifier = token['token_value']
        self.currentNode.insert_node(Tree('TagName', None, token))
        self.currentNode = self.currentNode.find_node('TagName')
        
        if (tagIdentifier in self.usedTagIdentifiers):
            raise SemanticalError(self.currentPos, f'Tag Identifier {tagIdentifier} has already been used.')
        
        if (tagIdentifier not in ParserConstants.VALID_TAG_IDENTIFIERS):
            raise SemanticalError(self.currentPos, f'Tag Identifier {tagIdentifier} is not a valid tag identifier.')
        else:
            self.usedTagIdentifiers.append(tagIdentifier)

        self.currentNode = self.currentNode.get_parent()
        return True

    def TagValue(self):
        self.expectType('String')
        token = self.currentToken()
        self.currentNode.insert_node(Tree('TagValue', None, token))
        self.currentNode = self.currentNode.find_node('TagValue')
        self.currentNode = self.currentNode.get_parent()
        return True
    
    def MoveTextSection(self):
        self.currentNode.insert_node(Tree('MoveTextSection'))
        self.currentNode = self.currentNode.get_parent()  
        return True

    def Empty(self):
        self.expectType('WhiteSpace')
        self.currentNode.insert_node(Tree('E'))
        self.currentNode = self.currentNode.get_parent() 
        return True


lexerExpressionList = [
            { 'token_type' : 'Operator',    'token_value' : '[' },
            { 'token_type' : 'Identifier',  'token_value' : 'Event' },
            { 'token_type' : 'String',      'token_value' : 'The Rumble in the Jungle 1974' },
            { 'token_type' : 'Operator',    'token_value' : ']' },
            { 'token_type' : 'Operator',    'token_value' : '[' },
            { 'token_type' : 'Identifier',  'token_value' : 'Round' },
            { 'token_type' : 'String',      'token_value' : 'The Rumble in the Jungle 1974' },
            { 'token_type' : 'Operator',    'token_value' : ']' },
            { 'token_type' : 'Operator',    'token_value' : '[' },
            { 'token_type' : 'Identifier',  'token_value' : 'Site' },
            { 'token_type' : 'String',      'token_value' : 'The Rumble in the Jungle 1974' },
            { 'token_type' : 'Operator',    'token_value' : ']' },
            { 'token_type' : 'WhiteSpace',  'token_value' : '' },
            { 'token_type' : 'Movement',    'token_value' : '1' },
            { 'token_type' : 'Expression',  'token_value' : 'c4' },
            { 'token_type' : 'Expression',  'token_value' : 'g6' },
            { 'token_type' : 'Comment',     'token_value' : 'hello comment 1234' },
            { 'token_type' : 'Movement',    'token_value' : '2' },
            { 'token_type' : 'Expression',  'token_value' : 'g3' },
            { 'token_type' : 'Expression',  'token_value' : 'Bg7' },
            { 'token_type' : 'Movement',    'token_value' : '3' },
            { 'token_type' : 'Expression',  'token_value' : 'Bg2' },
            { 'token_type' : 'Expression',  'token_value' : 'c5#' },
            { 'token_type' : 'Expression',  'token_value' : '0-1' },
            { 'token_type' : 'WhiteSpace',   'token_value' : '' },
        ]

Parser(lexerExpressionList)

