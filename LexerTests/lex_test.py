from Lexer import Lexer
from sample_game import txt

print (100 * "*")
print ("\nAscending....")

Lex=Lexer(txt)
game=0
while not Lex.EOF:
    token=Lex.GetToken
    print(token)
    if token['token_type']=='GAME_END':
        game+=1
    Lex.MoveNext()

print ("Total Games:",game)
input()
print ("\nDescending....")
print (100 * "*")
while not Lex.BOF:
    print(Lex.GetToken)
    Lex.MovePrevious()
 

