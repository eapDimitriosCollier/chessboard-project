import sys
sys.path.append('../chessboard-project')
from Parser.ParseTree.ParseNode import ParseNode
from Parser.ParseTree.ParseTree import ParseTree
from Parser import ParserConstants
from Lexer.Lexer import Lexer
from Event.Event import Event
import re

## Η γραμματική του PGN εκφρασμένη σε BNF. 
#: Add source
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

# Κλάσεις για διαχείρηση σφαλμάτων

class ParseError(Exception):
    def __init__(self, message: str) -> None:
        super().__init__(f'ParseError: {message}')

class SyntaxError(ParseError):
    def __init__(self, tokenIndex: int, line: int, position: int,  errorMessage: str = '', expected: str = '', got: str = '') -> None:
        self.message = f'SyntaxError on token #{tokenIndex} (Line: {line}, Position: {position}).'
        
        if expected and got: 
            errorMessage = f'Expected {expected}, got {got}' 
            
        self.message = self.message, ' ', errorMessage
        super().__init__(self.message)

class LogicError(ParseError):
    def __init__(self, tokenIndex: int, line: int, position: int, errorMessage: str) -> None:
        self.message = f'LogicError on token #{tokenIndex} (Line: {line}, Position: {position}). {errorMessage}'
        super().__init__(self.message)

class ParseTreeBuilder:
    """Απλή υλοποίηση ενός Recursive Descent Parser"""
    def __init__(self, Lexer: Lexer) -> None:
        self.Lexer = Lexer
        Event('LoadingMessage', message='Building Parse Tree...').invoke()
        self.usedTagIdentifiers = set()
        self.parseTree = None

    def nextToken(self) -> None:
        self.Lexer.MoveNext()
        token = self.currentToken()
        
        if (token['token_type'] == 'COMMENT'):
            self.nextToken()

    def currentToken(self) -> dict:
        return self.Lexer.GetToken

# Μέθοδοι που ελέγχουν αν το επόμενο token έχει συγκεκριμένη τιμή
    def expectType(self, expectedTokenType: str) -> None:
        currentToken = self.currentToken()
        if (currentToken['token_type'] != expectedTokenType):
            raise SyntaxError(self.Lexer.index, currentToken['Line'], currentToken['Position'], '', expectedTokenType, currentToken['token_type'])            

    def expectValue(self, expectedTokenValue: str) -> None:
        currentToken = self.currentToken()
        if (currentToken['token_value'] != expectedTokenValue):
            raise SyntaxError(self.Lexer.index, currentToken['Line'], currentToken['Position'], '', expectedTokenValue, currentToken['token_value'])      
 
    def maybe(self, possibleProductionRules: list) -> None:
        """Μέθοδος που εκτελεί τους γραμματικούς κανόνες έναν έναν.
           Αν βρεθεί σφάλμα, προχωράει στον επόμενο κανόνα. 
           Αν βρεθεί σφάλμα σε όλους τους κανόνες, πετάει το σφάλμα του τελευταίου."""
        lastPosition = self.Lexer.index
        for index, productionRule in enumerate(possibleProductionRules):
            try:
                # Μαρκάρουμε τα nodes τα οποία μπαίνουν στο δέντρο (δηλαδή καταγράφουμε τα id τους σε μια λίστα)
                # ώστε αν υπάρξει σφάλμα να μπορούμε εύκολα να τα διαγράψουμε.
                self.parseTree.startMarking(lastPosition)
                productionRule()
                self.parseTree.stopMarking()
            except ParseError as e:
                # Αν είμαστε στον τελευταίο κανόνα, σημαίνει ότι όλα τα προηγούμενα έχουν αποτύχει.
                # Εφόσον αποτύχει και το τελευταίο, πετάμε το τελευταίο ParseError που πήραμε.
                if index == len(possibleProductionRules) - 1:
                    raise e
                
                # Πρώτα διαγράφουμε όλα τα marked nodes
                self.parseTree.removeMarkedNodes(lastPosition)
                self.Lexer.index = lastPosition
                continue     
            else:
                # Αν εκτελεστεί το παραπάνω χωρίς ParseError, τότε, απλά φεύγουμε απ'την επανάληψη
                self.parseTree.clearMarkedNodeStack(lastPosition)
                break
    
    def getParseTree(self) -> ParseTree:
        return self.parseTree            
      
# Μέθοδοι που διέπουν το Recursive Descent μέρος του Parser
# εφαρμόζοντας την γραμματική στο BNF που βρήκαμε.
# Οι παρακάτω μέθοδοι χτίζουν το Parse Tree
    def build(self) -> None:
        self.parseTree = ParseTree()
        while (not self.Lexer.EOF):
            self.PGNDatabase()
            self.parseTree.goTo('PGNDatabase')
            self.parseTree.resetGrammarMap()

    def PGNDatabase(self) -> None:
        self.parseTree.insertNode(ParseNode('PGNDatabase'))
        self.parseTree.addReferenceToGrammarMap()
        self.PGNGame()
        self.nextToken()

    def PGNGame(self) -> None:
        self.parseTree.insertNode(ParseNode('PGNGame'))
        self.parseTree.addReferenceToGrammarMap()
        self.TagSection()
        
        self.parseTree.goTo('PGNGame')
        
        self.nextToken()     
        self.MoveTextSection()

    def TagSection(self) -> None:
        currentToken = self.currentToken()
        if (currentToken['token_type'] != 'EMPTY'):
            self.parseTree.insertNode(ParseNode('TagSection'))
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
        self.parseTree.insertNode(ParseNode('TagPair'))
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
        self.parseTree.insertNode(ParseNode('TagName', currentToken))
        
        if (tagIdentifier in self.usedTagIdentifiers):
            raise LogicError(self.Lexer.index, currentToken['Line'], currentToken['Position'], f'Tag Identifier {tagIdentifier} has already been used.')
        
        self.usedTagIdentifiers.add(tagIdentifier)

    def TagValue(self) -> None:
        self.expectType('STRING')
        token = self.currentToken()
        self.parseTree.insertNode(ParseNode('TagValue', token))
    
    def MoveTextSection(self) -> None:
        self.parseTree.insertNode(ParseNode('MoveTextSection'))
        self.parseTree.addReferenceToGrammarMap()
        self.ElementSequence()
        
        self.parseTree.goTo('MoveTextSection')
        self.GameTermination()
        self.nextToken()

    def ElementSequence(self) -> None:
        
        currentToken = self.currentToken()
        if (currentToken['token_type'] != 'GAME_END'):
            self.parseTree.insertNode(ParseNode('ElementSequence'))
            self.parseTree.addReferenceToGrammarMap()
            self.maybe([self.Element, self.RecursiveVariation])
            
            self.parseTree.goTo('ElementSequence')
            self.nextToken()
            self.ElementSequence()    

    def Element(self) -> None:
        self.parseTree.insertNode(ParseNode('Element'))
        self.maybe([self.MoveNumberIndication, self.SANMove, self.NumericAnnotationGlyph])

    def MoveNumberIndication(self) -> None:
        currentToken = self.currentToken()
        self.expectType('MOVEMENT')
        self.parseTree.insertNode(ParseNode('MoveNumberIndication', currentToken))

    def SANMove(self) -> None:
        currentToken = self.currentToken()
        self.parseTree.insertNode(ParseNode('SANMove', currentToken))
        # Χρήση RegEx για αναγνώριση κινήσεων.
        self.expectType('EXPRESSION')
        SANMoveRegEx = r"(..)?([NBRQK])?([a-h])?([1-8])?(x)?([a-h][1-8])(=[NBRQK])?(\+|#)?$|^O-O(-O)?"
        if (not re.match(SANMoveRegEx, currentToken['token_value'])):
            raise SyntaxError(self.Lexer.index, currentToken['Line'], currentToken['Position'], 'Invalid move')

    def NumericAnnotationGlyph(self) -> None:
        currentToken = self.currentToken()
        self.expectType('EXPRESSION')
        self.parseTree.insertNode(ParseNode('NumericAnnotationGlyph', currentToken)) 
        NAGRegEx = r"\$[1-255]"
        if (not re.fullmatch(NAGRegEx, currentToken['token_value'])):
            raise SyntaxError(self.Lexer.index, currentToken['Line'], currentToken['Position'], 'Invalid NAG')

    def RecursiveVariation(self) -> None:
        self.parseTree.insertNode(ParseNode('RecursiveVariation'))
        self.expectValue("(")
        self.nextToken()
        self.ElementSequence()
        self.nextToken()
        self.expectValue(")") 

    def GameTermination(self) -> None:
        token = self.currentToken()
        self.parseTree.insertNode(ParseNode('GameTermination', token))
        
    def Empty(self) -> None:
        self.parseTree.insertNode(ParseNode('E'))
