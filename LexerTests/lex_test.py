from Lexer import Lexer
from sample_game import txt

print (100 * "*")
print ("\nAscending....")
x=Lexer()
x.Tokenize(txt)
Lex=Lexer(txt)
while not Lex.EOF:
    print(Lex.GetToken)
    Lex.MoveNext()

input()
print ("\nDescending....")
print (100 * "*")
while not Lex.BOF:
    print(Lex.GetToken)
    Lex.MovePrevious()
 

