from Parser.AbstractSyntaxTreeBuilder.AbstractSyntaxTreeBuilder import AbstractSyntaxTreeBuilder
from Parser.ParseTreeBuilder.ParseTreeBuilder import ParseTreeBuilder
from LexerTests.Lexer import Lexer

class Parser:
    def __init__(self, Lexer: Lexer) -> None:
        self.parseTreeBuilder = ParseTreeBuilder(Lexer)
        self.parseTreeBuilder.build()
        self.parseTree = self.parseTreeBuilder.getParseTree()
        self.ASTBuilder = AbstractSyntaxTreeBuilder(self.parseTree)
        self.ASTBuilder.build()
        print(self.ASTBuilder.getAST())
        
        
        
        
        
        