#ΠΛΗΠΡΟ-ΗΛΕ54
#ΤΕΛΙΚΗ ΕΡΓΑΣΙΑ

import re
from string import whitespace

def Base():
    return 0,1
def _Base():
    return 0,2
def Operator():
    return 1,1
def Identifier():
    return 2,1
def Comment():
    return 3,1
def Number():
    return 4,1
def String():
    return 5,1
def Expression():
    return 6,1
def _Expression():
    return 6,3
def Movement():
    return 7,0
def ThrowError():
    return -1,-1

            # Rows are FSM States, Column Headerσ are inputs, Row&Column intersection is Action
            # Input:
            #Operator   , LBrace     ,RBrace     ,Quote      ,Char       ,Num        ,WhiteSpace, Period     , Symbol
FSM_Table= ((Operator   , Comment    ,ThrowError ,String     ,Identifier ,Number     ,Base       ,ThrowError , ThrowError),    #S0_Base       S0
            (ThrowError , ThrowError ,ThrowError ,ThrowError ,Identifier ,ThrowError ,Base       ,ThrowError , ThrowError),    #S1_Operator   S1
            (Base       , ThrowError ,ThrowError ,String     ,Identifier ,_Expression,Base       ,ThrowError , ThrowError),    #S2_Identifier S2 
            (Comment    , Comment    ,_Base      ,Comment    ,Comment    ,Comment    ,Comment    ,Comment    , Comment   ),    #S3_Comment    S3
            (Expression , Base       ,Base       ,Base       ,Base       ,Number     ,Base       ,Movement   ,_Expression),    #S4_Number     S4
            (String     , String     ,String     ,_Base      ,String     ,String     ,String     ,String     , String    ),    #S5_String     S5
            (Expression , Comment    ,ThrowError ,ThrowError ,Expression ,Expression ,Base       ,ThrowError , Expression),    #S6_Expression S6
            (Operator   , ThrowError ,ThrowError ,ThrowError ,ThrowError ,ThrowError ,Expression ,ThrowError , ThrowError))    #S7_Movement   S7
    
TokenType=("Base","Operator","Identifier","Comment","Number","String","Expression","Movement")

#Symbol Table
SymbolsTbl=(("[\[\]]","Operator"),          #Column 0
            ("{",     "LBrace"  ),          #Column 1
            ("}",     "RBrace"),            #Column 2
            ("\"",    "Quote" ),            #Column 3
            ("[A-Za-z]","Char"),            #Column 4
            ("[0-9]","Number"),             #Column 5
            ("[ \t\r\n\f]","WhiteSpace"),   #Column 6
            ("\.","Period"),                #Column 7
            ("[^\[\{}\"A-Za-z0-9 \t\r\n\f\.]","OtherSymbols"))         #Column 8


txt2="[Event \"The Rumble in the Jungle\"] 1. c4 g6{comment} 2. g3 Bg7 3. Bg2 c5# 0-1" + " "
txt2="[Event \"The Rumble in the Jungle 1974\"] 1. c4 g6 { \"hello\" comment 1234} 2. g3 Bg7 3. Bg2 c5# 0-1" + " "


State=0
Buffer=""
pos=0
NewState=0
tmp=0
for char in txt2:
    pos+=1
    Col=0
    Buffer+=char
    for symbol in SymbolsTbl:
        if (re.match(symbol[0],char)):
            NewState,tmp =(FSM_Table[State][Col])()
            if NewState<0: 
                 print ("Error in position:",pos)
                 break
            if State != NewState and Buffer[:-1].strip():
                if tmp==1:
                    print (TokenType[State],"--",Buffer[:-1]) #Insert old Buf in token list
                    Buffer=Buffer[-1:]
                if tmp==2:
                    print (TokenType[State],"--",Buffer) #Insert Buf+new char in token list
                    Buffer=""
                elif tmp==0:
                    Buffer=Buffer[:-1] 
                else:
                    pass

            State=NewState
            break
        Col+=1


