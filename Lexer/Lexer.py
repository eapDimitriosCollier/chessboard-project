from enum import Enum,unique
import re
# Lexer breaks the PGN file in tokens.
# It additionaly removes comments, NAG moves and Recursive Annotation Variation based on the following grammar so as to feed a clean token list to the parser.
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
    ACCEPTA = 8
    ACCEPTB = 9
    ACCEPTC = 10

class Tables:

                   #Operator          ,LBrace             ,RBrace             ,Quote              ,Char               ,Num                ,White Space        ,Period             ,Symbol
    State_Table= ((STATE.OPERATOR     ,STATE.COMMENT      ,STATE.THROWERROR   ,STATE.STRING       ,STATE.IDENTIFIER   ,STATE.NUMBER       ,STATE.BASE         ,STATE.EXPRESSION   ,STATE.EXPRESSION),#BASE_S0
                  (STATE.ACCEPTA      ,STATE.COMMENT      ,STATE.THROWERROR   ,STATE.STRING       ,STATE.IDENTIFIER   ,STATE.NUMBER       ,STATE.ACCEPTA      ,STATE.MOVEMENT     ,STATE.THROWERROR),#OPERATOR_S1
                  (STATE.THROWERROR   ,STATE.THROWERROR   ,STATE.THROWERROR   ,STATE.THROWERROR   ,STATE.IDENTIFIER   ,STATE.EXPRESSION   ,STATE.ACCEPTA      ,STATE.THROWERROR   ,STATE.EXPRESSION),#IDENTIFIER_S2
                  (STATE.COMMENT      ,STATE.COMMENT      ,STATE.ACCEPTB      ,STATE.COMMENT      ,STATE.COMMENT      ,STATE.COMMENT      ,STATE.COMMENT      ,STATE.COMMENT      ,STATE.COMMENT   ),#COMMENT_S3
                  (STATE.ACCEPTA      ,STATE.BASE         ,STATE.BASE         ,STATE.BASE         ,STATE.THROWERROR   ,STATE.NUMBER       ,STATE.ACCEPTA      ,STATE.MOVEMENT     ,STATE.EXPRESSION),#NUMBER_S4
                  (STATE.STRING       ,STATE.STRING       ,STATE.STRING       ,STATE.ACCEPTB      ,STATE.STRING       ,STATE.STRING       ,STATE.STRING       ,STATE.STRING       ,STATE.STRING    ),#STRING)_S5
                  (STATE.ACCEPTC      ,STATE.COMMENT      ,STATE.THROWERROR   ,STATE.THROWERROR   ,STATE.EXPRESSION   ,STATE.EXPRESSION   ,STATE.ACCEPTA      ,STATE.EXPRESSION   ,STATE.EXPRESSION),#EXPRESSION_S6
                  (STATE.OPERATOR     ,STATE.THROWERROR   ,STATE.THROWERROR   ,STATE.THROWERROR   ,STATE.THROWERROR   ,STATE.MOVEMENT     ,STATE.EXPRESSION   ,STATE.ACCEPTA      ,STATE.THROWERROR))#MOVEMENT_S7
   
    
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
        Buffer="";pos=0;line=1;BLANKLINE_MARKER=False
        State=STATE.BASE
        self.tokens=[]
        self._EOF=False
        self._BOF=True 
        #self.Err=False; self.ErrorLog.clear()
        
        txt+=" \n\n"
        for char in (txt):
            pos+=1;Col=-1    
            for symbol in Tables.SymbolsTbl:
                Col+=1
                if (re.match(symbol,char)):
                    NewState=Tables.State_Table[State.value][Col]
                    
                    if NewState==STATE.THROWERROR:
                        raise LexicalError(line,pos)                              
                    
                    if NewState!=State:
                        if NewState.value>=STATE.ACCEPTA.value:
                            if NewState==STATE.ACCEPTA:
                                #Update buffer and then Insert Token
                                #if Buffer:
                                Buffer=self._UpDateBuffer(Buffer,char.strip())
                                self.tokens.append({'token_type': STATE(State).name, 'token_value':Buffer, 'Line':line , 'Position':pos})
                                Buffer=""
                                State=STATE.BASE
                                #break
                            #Update buffer, Trim first and last char, and then Insert Token (for strings and comments)
                            elif NewState==STATE.ACCEPTB:
                                Buffer=self._UpDateBuffer(Buffer,char.strip())
                                Buffer=Buffer[1:-1]
                                self.tokens.append({'token_type': STATE(State).name, 'token_value':Buffer, 'Line':line , 'Position':pos})                            
                                Buffer=""
                                State=STATE.BASE
                                #break
                            #when an operator is the last char of an expression without a leading space, insert two tokens
                            elif NewState==STATE.ACCEPTC:
                                self.tokens.append({'token_type': STATE(State).name, 'token_value':Buffer, 'Line':line , 'Position':pos})                            
                                Buffer=char.strip()
                                NewState=STATE.OPERATOR
                                self.tokens.append({'token_type': STATE(NewState).name, 'token_value':Buffer, 'Line':line , 'Position':pos})   
                                Buffer=""
                                State=STATE.BASE
                                #break    
                                              
                        #as a convention, if there is an immediate ACCEPT on the new State for the same column, then insert token and return to State Zero
                        elif Tables.State_Table[NewState.value][Col].value==STATE.ACCEPTA.value:
                            Buffer=self._UpDateBuffer(Buffer,char)
                            self.tokens.append({'token_type': STATE(NewState).name, 'token_value':Buffer, 'Line':line , 'Position':pos})
                            Buffer=""
                            State=STATE.BASE
                            #break
                        else:
                            Buffer=self._UpDateBuffer(Buffer,char)
                            State=NewState
                            #break;
                    
                    else:
                        Buffer=self._UpDateBuffer(Buffer,char) 
                        State=NewState

                    #increase line count and insert an EMPTY token when there are at least two consequent line feed characters                       
                    if ord(char)==10:
                        pos=0
                        line+=1
                        if not BLANKLINE_MARKER:
                            BLANKLINE_MARKER=True
                        elif BLANKLINE_MARKER:
                            if len(self.tokens)>1 and self.tokens[-1]['token_type']!='EMPTY':
                                self.tokens.append({'token_type': "EMPTY", 'token_value':None, 'Line':line , 'Position':pos})
                            BLANKLINE_MARKER=False
                    else:
                        BLANKLINE_MARKER=False

        #second pass to remove comments, NAG moves and recursive annotation
        self.Evaluator()



    def _UpDateBuffer(self,Buffer,char) -> str:
        if Buffer.strip():
            Buffer+=char
        else:
            Buffer=char

        return Buffer

    def _FixRemoveSpecialTokens(self)->None:
        self.MoveFirst()
        game_termination= ('1-0','0-1','1/2-1/2','*')
        while not self.EOF:
            token=self.GetToken
            #remove period from movement
            if token['token_type']==STATE.MOVEMENT.name:
                token['token_value']=(token['token_value'])[:-1]

            #remove double period from expressions
            if token['token_type']==STATE.EXPRESSION.name and token['token_value'][0:2]=="..":
                token['token_value']=(token['token_value'])[2:]

            #insert game termination                                    
            if token['token_type']==STATE.EXPRESSION.name and token['token_value'] in game_termination:
                self.tokens[self.index]['token_type']="GAME_END"

            #remove NAG
            if token['token_type']==STATE.EXPRESSION.name and token['token_value'][:1] == "$":
                self._RemoveToken(self.index)
                self.index-=1
                continue

            #remove comments
            if token['token_type']==STATE.COMMENT.name:
                self._RemoveToken(self.index)
                self.index-=1
                continue

            self.MoveNext()
        self.MoveFirst()


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

        self.MoveFirst()

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

    def Evaluator(self)->None:
        self._FixRemoveSpecialTokens()
        self._RemoveRecursiveAnnotation()



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


    

