from enum import Enum,unique
import re

# Lexer breaks the PGN file in tokens.
# It additionaly removes comments and Recursive Variation and NAGs, based on the following grammar to feed a cleand token list to the parser.

# <recursive-variation> ::= ( <element-sequence> )
# <element-sequence> ::= <element> <element-sequence>
#                        <recursive-variation> <element-sequence>
#                        <empty>
# <element> ::= <move-number-indication>
#               <SAN-move>
#               <numeric-annotation-glyph>

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

     
@unique
class ACTION(Enum):
    TRANSERT = 1       #Transit State and Insert Token
    TRANSIT = 2        #Transit State only
    TRANSERTDIS = 3    #Transit State, Insert Token, Discard New Char
    TRANSERTDIN = 4    #Transit State, Insert Token on New State, Discard Last Char

class Tables:

                   #Operator          ,LBrace             ,RBrace             ,Quote              ,Char               ,Num                ,White Space        ,Period             ,Symbol
    State_Table= ((STATE.OPERATOR     ,STATE.COMMENT      ,STATE.THROWERROR   ,STATE.STRING       ,STATE.IDENTIFIER   ,STATE.NUMBER       ,STATE.BASE         ,STATE.THROWERROR   ,STATE.EXPRESSION),#BASE_S0
                  (STATE.THROWERROR   ,STATE.THROWERROR   ,STATE.THROWERROR   ,STATE.THROWERROR   ,STATE.IDENTIFIER   ,STATE.NUMBER       ,STATE.BASE         ,STATE.MOVEMENT     ,STATE.THROWERROR),#OPERATOR_S1
                  (STATE.OPERATOR     ,STATE.THROWERROR   ,STATE.THROWERROR   ,STATE.STRING       ,STATE.IDENTIFIER   ,STATE.EXPRESSION   ,STATE.BASE         ,STATE.THROWERROR   ,STATE.EXPRESSION),#IDENTIFIER_S2
                  (STATE.COMMENT      ,STATE.COMMENT      ,STATE.BASE         ,STATE.COMMENT      ,STATE.COMMENT      ,STATE.COMMENT      ,STATE.COMMENT      ,STATE.COMMENT      ,STATE.COMMENT   ),#COMMENT_S3
                  (STATE.EXPRESSION   ,STATE.BASE         ,STATE.BASE         ,STATE.BASE         ,STATE.THROWERROR   ,STATE.NUMBER       ,STATE.BASE         ,STATE.MOVEMENT     ,STATE.EXPRESSION),#NUMBER_S4
                  (STATE.STRING       ,STATE.STRING       ,STATE.STRING       ,STATE.BASE         ,STATE.STRING       ,STATE.STRING       ,STATE.STRING       ,STATE.STRING       ,STATE.STRING    ),#STRING)_S5
                  (STATE.OPERATOR     ,STATE.COMMENT      ,STATE.THROWERROR   ,STATE.THROWERROR   ,STATE.EXPRESSION   ,STATE.EXPRESSION   ,STATE.BASE         ,STATE.EXPRESSION   ,STATE.EXPRESSION),#EXPRESSION_S6
                  (STATE.OPERATOR     ,STATE.THROWERROR   ,STATE.THROWERROR   ,STATE.THROWERROR   ,STATE.THROWERROR   ,STATE.THROWERROR   ,STATE.EXPRESSION   ,STATE.EXPRESSION   ,STATE.THROWERROR))#MOVEMENT_S7

    Action_Table=((ACTION.TRANSERT    ,ACTION.TRANSERTDIS ,ACTION.TRANSERT    ,ACTION.TRANSERTDIS ,ACTION.TRANSERT    ,ACTION.TRANSERT    ,ACTION.TRANSERT    ,ACTION.TRANSERT    ,ACTION.TRANSERT ),#BASE_S0
                  (ACTION.TRANSERT    ,ACTION.TRANSERT    ,ACTION.TRANSERT    ,ACTION.TRANSERT    ,ACTION.TRANSERT    ,ACTION.TRANSERT    ,ACTION.TRANSERT    ,ACTION.TRANSERT    ,ACTION.TRANSERT ),#IDENTIFIER_S2
                  (ACTION.TRANSERT    ,ACTION.TRANSERT    ,ACTION.TRANSERT    ,ACTION.TRANSERTDIS ,ACTION.TRANSERT    ,ACTION.TRANSIT     ,ACTION.TRANSERT    ,ACTION.TRANSERT    ,ACTION.TRANSIT  ),#COMMENT_S3
                  (ACTION.TRANSERT    ,ACTION.TRANSERT    ,ACTION.TRANSERTDIS ,ACTION.TRANSERT    ,ACTION.TRANSERT    ,ACTION.TRANSERT    ,ACTION.TRANSERT    ,ACTION.TRANSERT    ,ACTION.TRANSERT ),#OPERATOR_S1
                  (ACTION.TRANSERT    ,ACTION.TRANSERT    ,ACTION.TRANSERT    ,ACTION.TRANSERT    ,ACTION.TRANSERT    ,ACTION.TRANSERT    ,ACTION.TRANSERT    ,ACTION.TRANSERTDIN ,ACTION.TRANSIT  ),#NUMBER_S4
                  (ACTION.TRANSERT    ,ACTION.TRANSERT    ,ACTION.TRANSERT    ,ACTION.TRANSERTDIS ,ACTION.TRANSERT    ,ACTION.TRANSERT    ,ACTION.TRANSERT    ,ACTION.TRANSERT    ,ACTION.TRANSERT ),#STRING_S5
                  (ACTION.TRANSERT    ,ACTION.TRANSERT    ,ACTION.TRANSERT    ,ACTION.TRANSERT    ,ACTION.TRANSERT    ,ACTION.TRANSERT    ,ACTION.TRANSERT    ,ACTION.TRANSERT    ,ACTION.TRANSERT ),#EXPRESSION_S6
                  (ACTION.TRANSERT    ,ACTION.TRANSERT    ,ACTION.TRANSERT    ,ACTION.TRANSERT    ,ACTION.TRANSERT    ,ACTION.TRANSERT    ,ACTION.TRANSERT    ,ACTION.TRANSERT    ,ACTION.TRANSERT ))#MOVEMENT_S7
                  

    
    
    SymbolsTbl=(("[\[\]()]"),       #Column 0 - Operator
                ("{"),              #Column 1 - Right Brace
                ("}"),              #Column 2 - Left Brace
                ("\""),             #Column 3 - Quote
                ("[A-Za-z]"),       #Column 4 - Char
                ("[0-9]"),          #Column 5 - Number
                ("[ \t\r\n\f]"),    #Column 6 - White Space
                ("\."),             #Column 7 - Period
                ("[^\[\](){}\"A-Za-z0-9 \t\r\n\f\.]")) #Column 8 - All Other Symbols
                

class ErrorHandling(Exception):
    def __init__(self,ErrMessage):
        self.ErrMessage='Lexical Error! \n' + ErrMessage
        super().__init__(self.ErrMessage)

class LexicalError(ErrorHandling):
    def __init__(self, line, position):
        self.ErrMessage = f'Unknown lexeme at line {line}, position {position}'
        super().__init__(self.ErrMessage)

class TokenPatternError(ErrorHandling):
    def __init__(self, line, position):
        self.ErrMessage = f'Unmathcing lexeme staring at line {line}, position {position}'
        super().__init__(self.ErrMessage)

class TokenIndexError(ErrorHandling):
    def __init__(self,index):
        self.ErrMessage = f'Token list index {index} out of range'
        super().__init__(self.ErrMessage)
        
class Lexer:

    def __init__(self,text=None) -> None:
        self.tokens=[]
        self._index=0
        self._EOF=False
        self._BOF=True
        if text:self.Tokenize(text)
        
    @property
    def GetToken(self)->int:
        return self.tokens[self.index]
        
    @property
    def index(self)->int:
        return self._index
    
    @index.setter
    def index(self,index) -> None:
            if index<0 or index > len(self.tokens)-1:
                raise TokenIndexError(index)
            else:            
                if index==len(self.tokens)-1:
                    self._EOF=True
                    self._BOF=False
                elif index==0:
                    self._EOF=False
                    self._BOF=True

                self._index=index

    @property
    def EOF(self)->bool:
        return self._EOF

    @property
    def BOF(self)->bool:
        return self._BOF

    def MoveNext(self) -> None:
        if self.index<len(self.tokens)-1:            
            self._index+=1
            self._EOF=False
            self._BOF=False
        else:
            self._EOF=True
            self._BOF=False
            
    def MovePrevious(self) -> None:
        if self.index>0:            
            self._index-=1
            self._BOF=False
            self._EOF=False
        else:
            self._EOF=False
            self._BOF=True

    def MoveFirst(self) -> None:
            self._EOF=False
            self._BOF=True
            self._index=0
        
    def MoveLast(self) -> None:
            self._EOF=True
            self._BOF=False
            self._index=len(self.tokens)-1

    def SetPosition(self,index) -> None:
            if index<0 or index > len(self.tokens)-1:
                raise TokenIndexError(index)
            else:            
                if index==len(self.tokens)-1:
                    self._EOF=True
                    self._BOF=False
                elif index==0:
                    self._EOF=False
                    self._BOF=True

                self._index=index



    def Tokenize(self,txt) -> None:
        Buffer="";pos=0;line=1
        State=STATE.BASE
        self.tokens=[]
        self._EOF=False
        self._BOF=True 
        #self.Err=False; self.ErrorLog.clear()
        
        
        for char in txt + " \n":
            #line+=1 if ord(char)==10 else 0
            pos+=1
            Col=0    
            for symbol in Tables.SymbolsTbl:
                if (re.match(symbol,char)):
                    NewState=Tables.State_Table[State.value][Col]
                    Action=Tables.Action_Table[State.value][Col]

                    if NewState==STATE.THROWERROR:
                        raise LexicalError(line,pos)
                    
                    if State != NewState:
                        if Action==ACTION.TRANSERT:
                            if Buffer.strip():
                                #print (STATE(State).name,"::",Buffer) #Insert old Buf in token list    
                                self.tokens.append({'token_type': STATE(State).name, 'token_value':Buffer, 'Line':line , 'Position':pos})
                            Buffer=char.strip()                                                            
                        elif Action==ACTION.TRANSIT:
                            Buffer+=char
                        elif Action==ACTION.TRANSERTDIS:
                            if Buffer.strip():
                                #print (STATE(State).name,"::",Buffer) #Insert Buf+new char in token list
                                self.tokens.append({'token_type': STATE(State).name, 'token_value':Buffer, 'Line':line , 'Position':pos})
                            Buffer=""
                        elif Action==ACTION.TRANSERTDIN:
                            if Buffer.strip():
                                #print (STATE(NewState).name,"::",Buffer) #Insert Buf+new char in token list
                                self.tokens.append({'token_type': STATE(NewState).name, 'token_value':Buffer, 'Line':line , 'Position':pos})
                            Buffer=""
                    else:
                        #add only one EMPTY token on multiple blank lines
                        if ord(char)==10 and len(self.tokens)>1 and self.tokens[-1]['token_type']!='EMPTY': 
                            if ( len(Buffer)>=1 and not Buffer.strip() ) or pos==1:
                                self.tokens.append({'token_type': "EMPTY", 'token_value':None, 'Line':line , 'Position':pos})
                        else:
                            Buffer+=char 
                        
                    State=NewState
                    break
                Col+=1
            #Increment line on line feed character
            if ord(char)==10:
                pos=0
                line+=1

        #second pass to remove comments and recursive annotation
        self.TokenizeExtended()

    def _RemoveNAG(self):
        self.MoveFirst()
        while not self.EOF:
            token=self.GetToken
            if token['token_type']==STATE.EXPRESSION.name and token['token_value'][:1] == "$":
                #print(token)
                self._RemoveToken(self.index)
                self._index-=1
            self.MoveNext()

    def _insertGameEnd(self):
        self.MoveFirst()
        while not self.EOF:
            token=self.GetToken
            game_termination= ('1-0','0-1','1/2-1/2','*')
            if token['token_type']==STATE.EXPRESSION.name and token['token_value'] in game_termination:
                self.tokens[self.index]['token_type']="GAME_END"
            self.MoveNext()

    def _RemoveComments(self,token=None)->None:
        if token:
            if token['token_type']==STATE.COMMENT.name:
                index=self.index
                self._RemoveToken(index)
                self.MovePrevious()
        else:
            self.MoveFirst()
            while not self.EOF:
                token=self.GetToken
                if token['token_type']==STATE.COMMENT.name:
                    index=self.index
                    self._RemoveToken(index)
                    self._index-=1
                self.MoveNext()

    def _RemoveRecursiveAnnotation(self,MatchState: bool = False, StartingPosition:int = 0,Ret:bool = False )->None:
        if not StartingPosition:
            self.MoveFirst()
        CurrentPos=StartingPosition
        Match=MatchState
        while not self.EOF:
            token=self.GetToken
            #if Left parenthesis is not found yet
            if not Match:
                if self._checkLParenthesis(token):
                    Match=True
                    #print(token)
                    CurrentPos=self.index
                    self.MoveNext()
                    continue
            #if Left parenthesis has already found
            elif Match:
                #match Right Parenthesis and delete all the tokens in between
                if self._checkRParenthesis(token):
                    #print (token)
                    for i in range(CurrentPos,self.index+1):
                        self._RemoveToken(CurrentPos)
                    self._index=CurrentPos
                    # continues on single matching parenthesis and returns on nested parenthesis
                    if not Ret:
                        Match=False
                        continue
                    else:
                        return
                #if Nested Left Parenthesis is found call the method recursively
                elif self._checkLParenthesis(token):
                    #print (token)
                    self.MoveNext()
                    self._RemoveRecursiveAnnotation(MatchState=True,StartingPosition=self.index-1,Ret=True)
                    continue
            self.MoveNext()
            

    def _checkLParenthesis(self,token)->bool:
        if token['token_type']==STATE.OPERATOR.name and token['token_value']=="(":
            return True
        else:
            return False

    def _checkRParenthesis(self,token)->bool:
        if token['token_type']==STATE.OPERATOR.name and token['token_value']==")":
            return True
        else:
            return False
        
    def _RemoveToken(self,index):
        try:
            del self.tokens[index]
        except Exception as e:
            print (e)

    def TokenizeExtended(self)->None:
        self._RemoveComments()
        self._RemoveRecursiveAnnotation()
        self._RemoveNAG()
        self._insertGameEnd()
        self.MoveFirst()


if __name__ == '__main__':
    from sample_game import txt

    Lex=Lexer(txt)
    game=1;cnt=0
    Lex.MoveFirst()
    i=0
    token=Lex.GetToken
    while not Lex.EOF:
        oldToken=token
        token=Lex.GetToken
        
        print(f"Game Id: {game} -Token Id: {i} --> {token}")
        if token["token_type"]=="EMPTY" and oldToken["token_type"]=='GAME_END':
            i=0;game+=1
        i+=1        
        Lex.MoveNext()


    

