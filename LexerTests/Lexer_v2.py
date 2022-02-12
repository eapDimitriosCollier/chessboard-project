#ΠΛΗΠΡΟ-ΗΛΕ54
#ΤΕΛΙΚΗ ΕΡΓΑΣΙΑ

from distutils.command.build import build
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

            # Rows are FSM States, Column Headers are inputs, Row&Column intersection is Action
            # Input:
            #Operator   , LBrace     ,RBrace     ,Quote      ,Char       ,Num        ,WhiteSpace, Period     , Symbol
FSM_Table= ((Operator   , Comment    ,ThrowError ,String     ,Identifier ,Number     ,Base       ,ThrowError , ThrowError),    #S0_Base       S0
            (ThrowError , ThrowError ,ThrowError ,ThrowError ,Identifier ,ThrowError ,Base       ,ThrowError , ThrowError),    #S1_Operator   S1
            (Base       , ThrowError ,ThrowError ,String     ,Identifier ,_Expression,Base       ,ThrowError ,_Expression),    #S2_Identifier S2 
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


txt="""[Event "F/S Return Match"]
[Site "Belgrade, Serbia JUG"]
[Date "1992.11.04"]
[Round "29"]
[White "Fischer, Robert J."]
[Black "Spassky, Boris V."]
[Result "1/2-1/2"]
1. e4 e5 2. Nf3 Nc6 3. Bb5 a6 {This opening is called "ggg" the Ruy Lopez.} 4. Ba4 Nf6 5. O-O Be7 6. Re1 b5 7. Bb3 d6 8. c3 O-O-O 9. h3 Nb8 10. d4 Nbd7
11. c4 c6 12. cxb5 axb5 13. Nc3 Bb7 14. Bg5 b4 15. Nb1 h6 16. Bh4 c5 17. dxe5
Nxe4 18. Bxe7 Qxe7 19. exd6 Qf6 20. Nbd2 Nxd6 21. Nc4 Nxc4 22. Bxc4 Nb6
23. Ne5 Rae8 24. Bxf7+ Rxf7 25. Nxf7 Rxe1+ 26. Qxe1 Kxf7 27. Qe3 Qg5 28. Qxg5
hxg5 29. b3 Ke6
35. Ra7 g6 36. Ra6+ Kc5 37. Ke1 Nf4 38. g3 Nxh3 39. Kd2 Kb5 40. Rd6 Kc5 41. Ra6
Nf2 42. g4 Bd3 43. Re6 1/2-1/2 """



txt="""[  Event"The Rumble in the Jungle 1974" ] 1. c4 g6 { "hello" comment 1234  } 2. g3 Bg7 3. Bg2 c5# 0-1 """

State=0;Buffer="";pos=0;NewState=0;tmp=0

for char in txt + " ":
    pos+=1
    Col=0
    #Buffer+=char
    for symbol in SymbolsTbl:
        if (re.match(symbol[0],char)):
            NewState,tmp =(FSM_Table[State][Col])()
            if NewState<0: 
                 print ("Error in position:",pos)
                 break
            #print (pos)
            if State != NewState and Buffer.strip():
                if tmp==0:
                    print (TokenType[NewState],"--",Buffer) #Insert old Buf in token list, discard new char, Elevate State
                    Buffer=""
                elif tmp==1:
                    print (TokenType[State],"--",Buffer) #Insert old Buf in token list
                    Buffer=char.strip()
                elif tmp==2:
                    print (TokenType[State],"--",Buffer+char) #Insert Buf+new char in token list
                    Buffer=""
                elif tmp==3:
                    Buffer+=char.strip()

            else:
                Buffer+=char if Buffer.strip() else char.strip() 
                
            State=NewState
            break
        Col+=1


