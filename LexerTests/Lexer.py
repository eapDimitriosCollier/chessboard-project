from enum import Enum,unique
import re

@unique
class STATE(Enum):
    THROWERROR=-1
    BASE=0
    OPERATOR=1
    IDENTIFIER = 2
    COMMENT = 3
    NUMBER = 4 
    STRING = 5
    EXPRESSION = 6
    MOVEMENT = 7
    GAME_END = 8
     
@unique
class ACTION(Enum):
    TRANSERT = 1       #Transit State and Insert Token
    TRANSIT = 2        #Transit State only
    TRANSERTDIS = 3    #Transit State, Insert Token, Discard New Char
    TRANSERTDIN = 4    #Transit State, Insert Token on New State, Discard Last Char

class Tables:

                   #Operator          ,LBrace             ,RBrace             ,Quote              ,Char               ,Num                ,White Space        ,Period             ,Symbol
    State_Table= ((STATE.OPERATOR     ,STATE.COMMENT      ,STATE.THROWERROR   ,STATE.STRING       ,STATE.IDENTIFIER   ,STATE.NUMBER       ,STATE.BASE         ,STATE.THROWERROR   ,STATE.THROWERROR),#BASE_S0
                  (STATE.THROWERROR   ,STATE.THROWERROR   ,STATE.THROWERROR   ,STATE.THROWERROR   ,STATE.IDENTIFIER   ,STATE.THROWERROR   ,STATE.BASE         ,STATE.THROWERROR   ,STATE.THROWERROR),#OPERATOR_S1
                  (STATE.BASE         ,STATE.THROWERROR   ,STATE.THROWERROR   ,STATE.STRING       ,STATE.IDENTIFIER   ,STATE.EXPRESSION   ,STATE.BASE         ,STATE.THROWERROR   ,STATE.EXPRESSION),#IDENTIFIER_S2
                  (STATE.COMMENT      ,STATE.COMMENT      ,STATE.BASE         ,STATE.COMMENT      ,STATE.COMMENT      ,STATE.COMMENT      ,STATE.COMMENT      ,STATE.COMMENT      ,STATE.COMMENT   ),#COMMENT_S3
                  (STATE.GAME_END     ,STATE.BASE         ,STATE.BASE         ,STATE.BASE         ,STATE.THROWERROR   ,STATE.NUMBER       ,STATE.BASE         ,STATE.MOVEMENT     ,STATE.GAME_END  ),#NUMBER_S4
                  (STATE.STRING       ,STATE.STRING       ,STATE.STRING       ,STATE.BASE         ,STATE.STRING       ,STATE.STRING       ,STATE.STRING       ,STATE.STRING       ,STATE.STRING    ),#STRING)_S5
                  (STATE.EXPRESSION   ,STATE.COMMENT      ,STATE.THROWERROR   ,STATE.THROWERROR   ,STATE.EXPRESSION   ,STATE.EXPRESSION   ,STATE.BASE         ,STATE.THROWERROR   ,STATE.EXPRESSION),#EXPRESSION_S6
                  (STATE.OPERATOR     ,STATE.THROWERROR   ,STATE.THROWERROR   ,STATE.THROWERROR   ,STATE.THROWERROR   ,STATE.THROWERROR   ,STATE.EXPRESSION   ,STATE.THROWERROR   ,STATE.THROWERROR),#MOVEMENT_S7
                  (STATE.THROWERROR   ,STATE.THROWERROR   ,STATE.THROWERROR   ,STATE.THROWERROR   ,STATE.THROWERROR   ,STATE.GAME_END     ,STATE.BASE         ,STATE.THROWERROR   ,STATE.GAME_END  ))#GAME_TERM_S8

                   #Operator          ,LBrace             ,RBrace             ,Quote              ,Char               ,Num                ,White Space        ,Period             ,Symbol
    Action_Table=((ACTION.TRANSERT    ,ACTION.TRANSERTDIS ,ACTION.TRANSERT    ,ACTION.TRANSERTDIS ,ACTION.TRANSERT    ,ACTION.TRANSERT    ,ACTION.TRANSERT    ,ACTION.TRANSERT    ,ACTION.TRANSERT ),#BASE_S0
                  (ACTION.TRANSERT    ,ACTION.TRANSERT    ,ACTION.TRANSERT    ,ACTION.TRANSERT    ,ACTION.TRANSERT    ,ACTION.TRANSERT    ,ACTION.TRANSERT    ,ACTION.TRANSERT    ,ACTION.TRANSERT ),#IDENTIFIER_S2
                  (ACTION.TRANSERT    ,ACTION.TRANSERT    ,ACTION.TRANSERT    ,ACTION.TRANSERTDIS ,ACTION.TRANSERT    ,ACTION.TRANSIT     ,ACTION.TRANSERT    ,ACTION.TRANSERT    ,ACTION.TRANSIT  ),#COMMENT_S3
                  (ACTION.TRANSERT    ,ACTION.TRANSERT    ,ACTION.TRANSERTDIS ,ACTION.TRANSERT    ,ACTION.TRANSERT    ,ACTION.TRANSERT    ,ACTION.TRANSERT    ,ACTION.TRANSERT    ,ACTION.TRANSERT ),#OPERATOR_S1
                  (ACTION.TRANSERT    ,ACTION.TRANSERT    ,ACTION.TRANSERT    ,ACTION.TRANSERT    ,ACTION.TRANSERT    ,ACTION.TRANSERT    ,ACTION.TRANSERT    ,ACTION.TRANSERTDIN ,ACTION.TRANSIT  ),#NUMBER_S4
                  (ACTION.TRANSERT    ,ACTION.TRANSERT    ,ACTION.TRANSERT    ,ACTION.TRANSERTDIS ,ACTION.TRANSERT    ,ACTION.TRANSERT    ,ACTION.TRANSERT    ,ACTION.TRANSERT    ,ACTION.TRANSERT ),#STRING_S5
                  (ACTION.TRANSERT    ,ACTION.TRANSERT    ,ACTION.TRANSERT    ,ACTION.TRANSERT    ,ACTION.TRANSERT    ,ACTION.TRANSERT    ,ACTION.TRANSERT    ,ACTION.TRANSERT    ,ACTION.TRANSERT ),#EXPRESSION_S6
                  (ACTION.TRANSERT    ,ACTION.TRANSERT    ,ACTION.TRANSERT    ,ACTION.TRANSERT    ,ACTION.TRANSERT    ,ACTION.TRANSERT    ,ACTION.TRANSERT    ,ACTION.TRANSERT    ,ACTION.TRANSERT ),#MOVEMENT_S7
                  (ACTION.TRANSERT    ,ACTION.TRANSERT    ,ACTION.TRANSERT    ,ACTION.TRANSERT    ,ACTION.TRANSERT    ,ACTION.TRANSERT    ,ACTION.TRANSERT    ,ACTION.TRANSERT    ,ACTION.TRANSERT ))#GAME_TERM_S8

    
    
    SymbolsTbl=(("[\[\]]"),       #Column 0 - Operator
                ("{"),              #Column 1 - Right Brace
                ("}"),              #Column 2 - Left Brace
                ("\""),             #Column 3 - Quote
                ("[A-Za-z]"),       #Column 4 - Char
                ("[0-9]"),          #Column 5 - Number
                ("[ \t\r\n\f]"),    #Column 6 - White Space
                ("\."),             #Column 7 - Period
                ("[^\[\{}\"A-Za-z0-9 \t\r\n\f\.]")) #Column 8 - All Other Symbols


class LexicalError(Exception):
    def __init__(self, line, position):
        self.message = f'Unknown lexeme at line {line}, position {position}'
        super().__init__(self.message)
        
class Lexer:

    def __init__(self,text=None) -> None:
        self.tokens=[]
        self.ErrorLog=[]
        self.index=0
        self.EOF=False
        self.BOF=True
        self.Err=False    
        if text:self.Tokenize(text)
        
    @property
    def GetToken(self):
        return self.tokens[self.index]
    
    def MoveNext(self):
        if self.index<len(self.tokens)-1:            
            self.index+=1
            self.EOF=False
            self.BOF=False
        else:
            self.EOF=True
            self.BOF=False
            
    def MovePrevious(self):
        if self.index>0:            
            self.index-=1
            self.BOF=False
            self.EOF=False
        else:
            self.EOF=False
            self.BOF=True

    def MoveFirst(self):
            self.EOF=False
            self.BOF=True
            self.index=0
        
    def MoveLast(self):
            self.EOF=True
            self.BOF=False
            self.index=len(self.tokens)-1

    def Tokenize(self,txt):
        Buffer="";pos=0;line=1
        State=STATE.BASE
        self.tokens=[]
        self.EOF=False
        self.BOF=True 
        self.Err=False; self.ErrorLog=[]
        
        
        for char in txt + " ":
            #line+=1 if ord(char)==10 else 0
            if ord(char)==10:
                pos=0
                line+=1
            pos+=1
            Col=0    
            for symbol in Tables.SymbolsTbl:
                if (re.match(symbol,char)):
                    NewState=Tables.State_Table[State.value][Col]
                    Action=Tables.Action_Table[State.value][Col]
                    
                    if NewState==STATE.THROWERROR:       
                        try:
                            raise LexicalError(line,pos)
                        except LexicalError as e:
                            self.ErrorLog.append(e)
                            self.Err=True
                            break
                    
                    if State != NewState:
                        if Action==ACTION.TRANSERT:
                            if Buffer.strip():
                                #print (STATE(State).name,"::",Buffer) #Insert old Buf in token list    
                                self.tokens.append({'token_type': STATE(State).name, 'token_value':Buffer})
                            Buffer=char.strip()                                                            
                        elif Action==ACTION.TRANSIT:
                            Buffer+=char
                        elif Action==ACTION.TRANSERTDIS:
                            if Buffer.strip():
                                #print (STATE(State).name,"::",Buffer) #Insert Buf+new char in token list
                                self.tokens.append({'token_type': STATE(State).name, 'token_value':Buffer})
                            Buffer=""
                        elif Action==ACTION.TRANSERTDIN:
                            if Buffer.strip():
                                #print (STATE(NewState).name,"::",Buffer) #Insert Buf+new char in token list
                                self.tokens.append({'token_type': STATE(NewState).name, 'token_value':Buffer})
                            Buffer=""
                    else:
                        #add only one EMPTY token on multiple blank lines
                        if ord(char)==10 and len(self.tokens)>1 and self.tokens[-1]!={'token_type': 'EMPTY', 'token_value':None}: #new line character
                            self.tokens.append({'token_type': "EMPTY", 'token_value':None})
                        else:
                            Buffer+=char 
                        
                    State=NewState
                    break
                Col+=1


if __name__ == '__main__':
    from sample_game import txt
    #Lex=Lexer(" 12a 12e 5this is a pipe")
    Lex=Lexer(txt)

    game=0
    while not Lex.EOF and not Lex.Err:
        token=Lex.GetToken
        print(token)
        if token['token_type']=='GAME_END':
            game+=1
        Lex.MoveNext()
    
    for ErrorItem in Lex.ErrorLog:
        print(ErrorItem)
    

