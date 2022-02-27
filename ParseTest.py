from LexerTests.Lexer import Lexer
from LexerTests.sample_game import txt
from Parser.Parser import Parser

Lex = Lexer(txt)
Parser(Lex)