
from Lexer import Lexer
from sample_game import txt


print (100 * "*")
print ("\nAscending....")

Lex=Lexer(txt)

while not Lex.EOF:
    token=Lex.GetToken
    print(token)
    Lex.MoveNext()




