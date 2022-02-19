from Lexer import Lexer
from sample_game import txt

Lex=Lexer(txt)

print ("\nAscending....")
print (100 * "*")
while not Lex.EOF:
    print(Lex.GetToken)
    Lex.MoveNext()

input()

print ("\nDescending....")
print (100 * "*")
while not Lex.BOF:
    print(Lex.GetToken)
    Lex.MovePrevious()
 

 
