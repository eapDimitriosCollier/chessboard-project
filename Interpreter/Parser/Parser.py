from Interpreter.Parser.AbstractSyntaxTreeBuilder.AbstractSyntaxTreeBuilder import AbstractSyntaxTreeBuilder
from Interpreter.Parser.ParseTreeBuilder.ParseTreeBuilder import ParseTreeBuilder
from Interpreter.Lexer.Lexer import Lexer

class Parser:
    def __init__(self, Lexer: Lexer) -> None:
        
        # Δημιουργία Parse Tree
        parseTreeBuilder = ParseTreeBuilder(Lexer)
        parseTreeBuilder.build()
       
        
        # Δημιουργία AST
        parseTree = parseTreeBuilder.getParseTree()
        ASTBuilder = AbstractSyntaxTreeBuilder(parseTree)
        ASTBuilder.build()
        
        self._AST = ASTBuilder.getAST()
        
    def getParsingResult(self):
        return self._AST    
        
        
        
        
        
        