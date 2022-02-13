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

# txt="""[Event \"The Rumble in the Jungle 1974\"] 1. c4 g6 { "hello" comment 1234} 2. g3 Bg7 3. Bg2 c5# 0-1 """


class Tree:
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

class SyntacticalError(Exception):
    def __init__(self, tokenIndex, expected, got):
        self.message = f'SyntacticalError on token #{tokenIndex}. Expected {expected}, got {got}'
        super().__init__(self.message)

class SemanticalError(Exception):
    def __init__(self, tokenIndex, errorMessage):
        self.message = f'SemanticalError on token #{tokenIndex}. {errorMessage}'
        super().__init__(self.message)

class Parser:
    def __init__(self, lexerExpressionList):
        self.lexerExpressionList = lexerExpressionList
        self.currentPos = -1
        self.streamLen = len(self.lexerExpressionList)
        self.parseTree = Tree('root')
        self.currentNode = self.parseTree

         # Ενα λεξικό από τους identifiers που μπορούν να χρησιμοποιηθούν ως όνομα tag.
         # Κάθε φορά που θα χρησιμοποιείται ένας identifier, θα διαγράφεται από το λεξικό,
         # οπότε αν δεν βρεθεί ο identifier στο παρακάτω λεξικό, θα πετάμε ParseError.

         # Αν κατά την λήξη του parsing του TagSection υπάρχουν tag identifiers που δεν είναι optional
         # στο λεξικό, πετάμε επίσης ParseError
        self.tagIdentififierStack = {
            'Event'        : { 'isOptional': False },
            'Site'         : { 'isOptional': False },
            'Date'         : { 'isOptional': False },
            'Round'        : { 'isOptional': False },
            'White'        : { 'isOptional': False },
            'Black'        : { 'isOptional': False },
            'Result'       : { 'isOptional': False },
            'WhiteTitle'   : { 'isOptional': True },
            'BlackTitle'   : { 'isOptional': True },
            'WhiteElo'     : { 'isOptional': True },
            'BlackElo'     : { 'isOptional': True },
            'WhiteUSCF'    : { 'isOptional': True },
            'BlackUSCF'    : { 'isOptional': True },
            'WhiteNA'      : { 'isOptional': True },
            'BlackNA'      : { 'isOptional': True },
            'WhiteType'    : { 'isOptional': True },
            'BlackType'    : { 'isOptional': True },
            'EventDate'    : { 'isOptional': True },
            'EventSponsor' : { 'isOptional': True },
            'Section'      : { 'isOptional': True },
            'Stage'        : { 'isOptional': True },
            'Board'        : { 'isOptional': True },
        }

        self.start()
        self.parseTree.show_tree()

    def nextToken(self):
        self.currentPos += 1

        token = self.lexerExpressionList[self.currentPos]

        if (token['token_type'] == 'Comment'):
            self.nextToken()

        return token

    def prevToken(self):
        self.currentPos -= 1

        token = self.lexerExpressionList[self.currentPos]

        if (token['token_type'] == 'Comment'):
            self.prevToken()

        return token

    def currentToken(self):
        return self.lexerExpressionList[self.currentPos]

    def lookAhead(self):
        token = self.nextToken()
        self.prevToken()
        return token

    def expectType(self,expectedTokenType):
        currentToken = self.nextToken()
        if (currentToken['token_type'] != expectedTokenType):
            raise SyntacticalError(self.currentPos, expectedTokenType, currentToken['token_type'])            

    def expectValue(self,expectedTokenValue):
        currentToken = self.nextToken()
        if (currentToken['token_value'] != expectedTokenValue):
            raise SyntacticalError(self.currentPos, expectedTokenValue, currentToken['token_value'])      

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
        lookAheadToken = self.lookAhead()
        if (lookAheadToken['token_type'] is not 'WhiteSpace'):
            if (not self.PGNGame()):
                return False
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
        if (not self.MoveTextSection()):
            return False

        self.currentNode = self.currentNode.get_parent()
        return True

    def TagSection(self):
        self.currentNode.insert_node(Tree('TagSection'))
        self.currentNode = self.currentNode.find_node('TagSection')
        lookAheadToken = self.lookAhead()
        if (lookAheadToken['token_type'] is not 'WhiteSpace'):
            if (not self.TagPair()):
                return False
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
        if (not self.TagName()):
            return False
        if (not self.TagValue()):
            return False
        self.expectValue(']')

        self.currentNode = self.currentNode.get_parent() 
        return True

    def TagName(self):
        self.expectType('Identifier')
        token = self.currentToken()
        tagIdentifier = token['token_value']
        self.currentNode.insert_node(Tree('TagName', None, tagIdentifier))
        self.currentNode = self.currentNode.find_node('TagName')
        if (tagIdentifier not in self.tagIdentififierStack):
            raise SemanticalError(self.currentPos, f'Tag Identifier {tagIdentifier} either does not exist or was already used')
        else:
            self.tagIdentififierStack.pop(tagIdentifier)
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
            { 'token_type' : 'Identifier',  'token_value' : 'Event' },
            { 'token_type' : 'String',      'token_value' : 'The Rumble in the Jungle 1974' },
            { 'token_type' : 'Operator',    'token_value' : ']' },
            { 'token_type' : 'Operator',    'token_value' : '[' },
            { 'token_type' : 'Identifier',  'token_value' : 'Event' },
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

