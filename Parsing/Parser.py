from Parsing.ParseTreeBuilder.ParseTreeBuilder import ParseTreeBuilder
from LexerTests.Lexer import Lexer

class Parser:
    def __init__(self, Lexer: Lexer) -> None:
        self.parseTreeBuilder = ParseTreeBuilder(Lexer)
        self.parseTreeBuilder.build()
        self.parseTree = self.parseTreeBuilder.getParseTree()
        self.parseTree.showTree()
        
        
        
        