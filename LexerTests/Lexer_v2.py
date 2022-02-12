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


txt="""

[Event "GBR-ch 58th"]
[Site "Blackpool"]
[Date "1971.08.12"]
[Round "4"]
[White "Littlewood, John Eric"]
[Black "Whiteley, Andrew"]
[Result "0-1"]
[WhiteElo "2310"]
[BlackElo "2310"]
[ECO "D44"]
[EventDate "1971.08.09"]
[PlyCount "66"]
[EventType "swiss"]
[EventRounds "11"]
[EventCountry "GBR"]

1. d4 d5 2. c4 c6 3. Nf3 Nf6 4. Nc3 e6 5. Bg5 dxc4 6. e4 b5 7. Qc2 h6 8.
Bh4 Be7 9. Be2 g5 10. Bg3 g4 11. Ne5 b4 12. Na4 Qxd4 13. O-O Qxe4 14. Qd2
Ba6 15. Rfe1 Qd5 16. Qf4 Nbd7 17. Nxc4 Nh5 18. Qc1 Nxg3 19. hxg3 Bb5 20.
Qc2 Qg5 21. Rad1 Nf6 22. Nd6+ Bxd6 23. Rxd6 O-O 24. Nc5 Rad8 25. Rxd8 Rxd8
26. Bxb5 cxb5 27. Nd3 Qf5 28. Re3 a5 29. Kf1 Ne4 30. Ke2 Rd4 31. Qc7 Rxd3
32. Rxd3 Qxf2+ 33. Kd1 Qf1+ 0-1

[Event "GBR-ch 58th"]
[Site "Blackpool"]
[Date "1971.08.13"]
[Round "5"]
[White "Wade, Robert"]
[Black "Littlewood, John Eric"]
[Result "0-1"]
[WhiteElo "2365"]
[BlackElo "2310"]
[ECO "D80"]
[EventDate "1971.08.09"]
[PlyCount "94"]
[EventType "swiss"]
[EventRounds "11"]
[EventCountry "GBR"]

1. d4 Nf6 2. c4 g6 3. Nc3 d5 4. Bg5 Ne4 5. Bh4 Bg7 6. e3 c5 7. cxd5 Nxc3 8.
bxc3 cxd4 9. cxd4 Qxd5 10. Nf3 Nc6 11. Qa4 O-O 12. Qb5 Qe4 13. Be2 e5 14.
d5 Nb4 15. O-O Nxd5 16. Rac1 a6 17. Qb3 Be6 18. Rc4 Nf4 19. Rxe4 Nxe2+ 20.
Kh1 Bxb3 21. axb3 b5 22. Be7 Rfe8 23. Bb4 f5 24. Rh4 Bf6 25. Rh3 a5 26. Bd2
b4 27. e4 fxe4 28. Ng5 Bxg5 29. Bxg5 Rac8 30. Re3 Nd4 31. h4 h6 32. Bxh6
Nf5 33. Bg5 Nxe3 34. fxe3 Rf8 35. Ra1 Rc3 36. Rxa5 Rxb3 37. Rxe5 Rd3 38.
Rb5 b3 39. Kg1 Rc8 40. Rb7 Rc2 41. Kh2 b2 42. Bf6 Rdd2 43. Kg3 Rxg2+ 44.
Kf4 Rcf2+ 45. Ke5 Rg1 46. Rb8+ Kf7 47. Rb7+ Ke8 0-1

[Event "GBR-ch 58th"]
[Site "Blackpool"]
[Date "1971.08.13"]
[Round "5"]
[White "Whiteley, Andrew"]
[Black "Hartston, William R"]
[Result "1/2-1/2"]
[WhiteElo "2310"]
[BlackElo "2390"]
[ECO "A32"]
[EventDate "1971.08.09"]
[PlyCount "31"]
[EventType "swiss"]
[EventRounds "11"]
[EventCountry "GBR"]

1. d4 Nf6 2. c4 c5 3. Nf3 cxd4 4. Nxd4 e6 5. Nc3 Bb4 6. Nb5 O-O 7. a3 Bxc3+
8. Nxc3 d5 9. cxd5 exd5 10. e3 Nc6 11. Be2 Be6 12. O-O Rc8 13. Bd2 d4 14.
exd4 Nxd4 15. Be3 Nxe2+ 16. Nxe2 1/2-1/2 """




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
                    print (TokenType[NewState],"::\t",Buffer) #Insert old Buf in token list, discard new char, Elevate State
                    Buffer=""
                elif tmp==1:
                    print (TokenType[State],"::\t",Buffer) #Insert old Buf in token list
                    Buffer=char.strip()
                elif tmp==2:
                    print (TokenType[State],"::\t",Buffer+char) #Insert Buf+new char in token list
                    Buffer=""
                elif tmp==3:
                    Buffer+=char.strip()

            else:
                Buffer+=char if Buffer.strip() else char.strip() 
                
            State=NewState
            break
        Col+=1


