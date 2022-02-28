from Lexer.Lexer import Lexer
from sample_game import txt
from Parser.Parser import Parser

Lex = Lexer(txt)
Parser(Lex)