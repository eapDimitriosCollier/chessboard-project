from enum import Enum,unique

@unique
class COLOR(Enum):
    BLACK=False
    WHITE=True

class PIECENAME(Enum):
    ROOK=1
    KNIGHT=2
    BISHOP=3
    QUEEN=4
    KING=5
    PAWN=6
ImagePath="./GUI_PA/img/"

#Black Pieces 0x265A to 0x265F
#White Pieces 0x2654 to 0x2659
BlackUnicodes=[ chr(i) for i in range(0x265a,0x265f+1)]
WhiteUnicodes=[ chr(i) for i in range(0x2654,0x2659+1)]

class PiecePosition:
    def __init__(self,Row=None,Column=None) -> None:
        self.Row=Row
        self.Col=Column
    
    @property
    def Row(self)->bool:
        return self._Row
    
    @Row.setter
    def Row(self,data:int):
        self._Row=data
        self._Rank=data

    @property
    def Col(self)->bool:
        return self._Col
    
    @Col.setter
    def Col(self,data:int):
        self._Col=data
        self._File=chr(data+96+1)

    @property
    def Rank(self)->bool:
        return self._Row
    
    @Rank.setter
    def Rank(self,data:int):
        self._Rank=data

    @property
    def File(self)->bool:
        return self._File
    
    @File.setter
    def File(self,data:str):
        self._File=data
        self._Col=ord(data)-96+1

    @property
    def FileRank(self)->bool:
        return f'{self._File}{self._Rank}'
    
    @FileRank.setter
    def FileRank(self,data:str):
        self.File=data[0]
        self.Rank=data[1]



class Piece:
    def __init__(self,**kwargs) -> None: 
         self._color=kwargs['Color']
         self._isVisible=True
         self._imagefile=kwargs['ImageFile']
         Row=kwargs['Row']
         Column=kwargs['Column']
         if 'Unicode' in kwargs:
             self._unicode=kwargs['Unicode']
         self.Position=PiecePosition(Row,Column)
         self.Tag=[] # List to hold any var type, will be used to hold Image Id


    # @property
    # def Name(self)->str:
    #      return self.__str__()

    #Black Pieces 0x265A to 0x265F
    #White Pieces 0x2654 to 0x2659
    @property
    def Unicode(self)->str:
         return self._unicode

    @property
    def Color(self)->str:
        return self._color.name
    
    @property
    def IsVisible(self)->bool:
        return self._isVisible
    
    @IsVisible.setter
    def IsVisible(self,data:bool):
        self._isVisible=data

    @property
    def ImageFile(self):
        return self._imagefile
    
    # @ImageFile.setter
    # def ImageFile(self,data):
    #     self._imagefile=data


class Rook(Piece):
    def __init__(self,**kwargs) -> None: 
        if kwargs['Color']==COLOR.BLACK:
            kwargs['ImageFile']=f"{ImagePath}brook.png"
            kwargs['Unicode']="\u265C"
        else:
            kwargs['ImageFile']=f"{ImagePath}wrook.png"
            kwargs['Unicode']="\u2656"
        super().__init__(**kwargs)

    def __str__(self) -> str:
        return PIECENAME.ROOK.name

    def GetValidMoves(self,Board:list)->list:
        validMoves=[]
        row=self.Position.Row
        col=self.Position.Col
        color=True
        if self.Color==COLOR.BLACK.name:
            color=False

        row=self.Position.Row;col=self.Position.Col
        #move down on an empty square or by killing an opponet
        #stop on first piece
        while (row <7):
            if not Board[row+1][col] or Board[row+1][col] in (BlackUnicodes if color else WhiteUnicodes):
                validMoves.append([row+1,col])
                if Board[row+1][col]:break
            else:break
            row+=1

        row=self.Position.Row;col=self.Position.Col
        #move up on an empty square or by killing an opponet
        #stop on first piece
        while (row >0):
            if not Board[row-1][col] or Board[row-1][col] in (BlackUnicodes if color else WhiteUnicodes):
                validMoves.append([row-1,col])
                if Board[row-1][col]:break
            else:break
            row-=1

        row=self.Position.Row;col=self.Position.Col
        #move left on an empty square or by killing an opponet
        #stop on first piece
        while (col >0):
            if not Board[row][col-1] or Board[row][col-1] in (BlackUnicodes if color else WhiteUnicodes):
                validMoves.append([row,col-1])
                if Board[row][col-1]:break
            else:break
            col-=1

        row=self.Position.Row;col=self.Position.Col
        #move right on an empty square or by killing an opponet
        #stop on first piece
        while (col <7):
            if not Board[row][col+1] or Board[row][col+1] in (BlackUnicodes if color else WhiteUnicodes):
                validMoves.append([row,col+1])
                if Board[row][col+1]:break
            else:break
            col+=1

        return sorted(validMoves)

class Knight(Piece):
    def __init__(self,**kwargs) -> None: 
        if kwargs['Color']==COLOR.BLACK:
            kwargs['ImageFile']=f"{ImagePath}bknight.png"
            kwargs['Unicode']="\u265E"
        else:
            kwargs['ImageFile']=f"{ImagePath}wknight.png"
            kwargs['Unicode']="\u2658"
        super().__init__(**kwargs)

    def __str__(self) -> str:
        return PIECENAME.KNIGHT.name

    def GetValidMoves(self,Board:list)->list:
        validMoves=[]
        row=self.Position.Row
        col=self.Position.Col
        color=True
        if self.Color==COLOR.BLACK.name:
            color=False

        #move Two Up and one Right or Left on an empty square or by killing an opponet
        if row>1:
            if col<7 and (not Board[row-2][col+1] or Board[row-2][col+1] in (BlackUnicodes if color else WhiteUnicodes)):
                validMoves.append([row-2,col+1])
            if col>0 and (not Board[row-2][col-1] or Board[row-2][col-1] in (BlackUnicodes if color else WhiteUnicodes)):
                validMoves.append([row-2,col-1])

        #move One Up and Two Right or Left on an empty square or by killing an opponet
        if row>0:
            if col<6 and (not Board[row-1][col+2] or Board[row-1][col+2] in (BlackUnicodes if color else WhiteUnicodes)):
                validMoves.append([row-1,col+2])
            if col>1 and (not Board[row-1][col-2] or Board[row-1][col-2] in (BlackUnicodes if color else WhiteUnicodes)):
                validMoves.append([row-1,col-2])


        #move Two Down and one Right or Left on an empty square or by killing an opponet
        if row<6:
            if col<7 and (not Board[row+2][col+1] or Board[row+2][col+1] in (BlackUnicodes if color else WhiteUnicodes)):
                validMoves.append([row+2,col+1])
            if col>0 and (not Board[row+2][col-1] or Board[row+2][col-1] in (BlackUnicodes if color else WhiteUnicodes)):
                validMoves.append([row+2,col-1])

        #move One Down and Two Right or Left on an empty square or by killing an opponet
        if row<7:
            if col<6 and (not Board[row+1][col+2] or Board[row+1][col+2] in (BlackUnicodes if color else WhiteUnicodes)):
                validMoves.append([row+1,col+2])
            if col>1 and (not Board[row+1][col-2] or Board[row+1][col-2] in (BlackUnicodes if color else WhiteUnicodes)):
                validMoves.append([row+1,col-2])
        
        return sorted(validMoves)

class Bishop(Piece):
    def __init__(self,**kwargs) -> None: 
        if kwargs['Color']==COLOR.BLACK:
            kwargs['ImageFile']=f"{ImagePath}bbishop.png"
            kwargs['Unicode']="\u265D"
        else:
            kwargs['ImageFile']=f"{ImagePath}wbishop.png"
            kwargs['Unicode']="\u2657"
        super().__init__(**kwargs)

    def __str__(self) -> str:
        return PIECENAME.BISHOP.name

    def GetValidMoves(self,Board:list)->list:
        validMoves=[]
        row=self.Position.Row
        col=self.Position.Col
        color=True
        if self.Color==COLOR.BLACK.name:
            color=False

        #move upRight on an empty square or by killing an opponet
        #stop on first piece
        while (row>0 and col<7):
            if not Board[row-1][col+1] or Board[row-1][col+1] in (BlackUnicodes if color else WhiteUnicodes):
                validMoves.append([row-1,col+1])
                if Board[row-1][col+1]:break
            else:break 
            row-=1;col+=1

        row=self.Position.Row;col=self.Position.Col
        #move upLeft on an empty square or by killing an opponet
        #stop on first piece
        while (row>0 and col>0):
            if not Board[row-1][col-1] or Board[row-1][col-1] in (BlackUnicodes if color else WhiteUnicodes):
                validMoves.append([row-1,col-1])
                if Board[row-1][col-1]:break
            else:break
            row-=1;col-=1

        row=self.Position.Row;col=self.Position.Col
        #move downRight on an empty square or by killing an opponet
        #stop on first piece
        while (row<7 and col<7):
            if not Board[row+1][col+1] or Board[row+1][col+1] in (BlackUnicodes if color else WhiteUnicodes):
                validMoves.append([row+1,col+1])
                if Board[row+1][col+1]: break
            else:break
            row+=1;col+=1

        row=self.Position.Row;col=self.Position.Col
        #move downLeft on an empty square or by killing an opponet
        #stop on first piece
        while (row <7 and col>0):
            if not Board[row+1][col-1] or Board[row+1][col-1] in (BlackUnicodes if color else WhiteUnicodes):
                validMoves.append([row+1,col-1])
                if Board[row+1][col-1]:break
            else:break
            row+=1;col-=1
        return sorted(validMoves)

class Queen(Piece):
    def __init__(self,**kwargs) -> None: 
        if kwargs['Color']==COLOR.BLACK:
            kwargs['ImageFile']=f"{ImagePath}bqueen.png"
            kwargs['Unicode']="\u265B"
        else:
            kwargs['ImageFile']=f"{ImagePath}wqueen.png"
            kwargs['Unicode']="\u2655"
        super().__init__(**kwargs)

    def __str__(self) -> str:
        return PIECENAME.QUEEN.name

    def GetValidMoves(self,Board:list)->list:
        validMoves=[]
        row=self.Position.Row
        col=self.Position.Col
        color=COLOR.BLACK if self.Color==COLOR.BLACK else COLOR.WHITE

        #Queen has the same movement set with the Bishop and the Rook
        #A temporary class of each of them is declared
        #and the valid move list is inherited through composition
        tmpRook=Rook(Color=color,Row=row,Column=col)
        validMoves=tmpRook.GetValidMoves(Board)
        tmpBishop=Bishop(Color=color,Row=row,Column=col)
        validMoves.extend(tmpBishop.GetValidMoves(Board))
        return sorted(validMoves)


class King(Piece):
    def __init__(self,**kwargs) -> None: 
        if kwargs['Color']==COLOR.BLACK:
            kwargs['ImageFile']=f"{ImagePath}bking.png"
            kwargs['Unicode']="\u265A"
        else:
            kwargs['ImageFile']=f"{ImagePath}wking.png"
            kwargs['Unicode']="\u2654"
        super().__init__(**kwargs)

    def __str__(self) -> str:
        return PIECENAME.KING.name

    def GetValidMoves(self,Board:list)->list:
        validMoves=[]
        row=self.Position.Row
        col=self.Position.Col
        color=True
        if self.Color==COLOR.BLACK.name:
            color=False

        #move up on empty square or by killing an opponet
        if row>0 and (not Board[row-1][col] or Board[row-1][col] in (BlackUnicodes if color else WhiteUnicodes)):
            validMoves.append([row-1,col])
        #move upRight on an empty square or by killing an opponet
        if row>0 and col<7 and (not Board[row-1][col+1] or Board[row-1][col+1] in (BlackUnicodes if color else WhiteUnicodes)):
            validMoves.append([row-1,col+1])
        #move upLeft on an empty square or by killing an opponet
        if row>0 and col>0 and (not Board[row-1][col-1] or Board[row-1][col-1] in (BlackUnicodes if color else WhiteUnicodes)):
            validMoves.append([row-1,col-1])

        #move down on empty square
        if row<7 and (not Board[row+1][col] or Board[row+1][col] in (BlackUnicodes if color else WhiteUnicodes)):
            validMoves.append([row+1,col])
        #move downRight on an empty square or by killing an opponet
        if row<7 and col<7 and (not Board[row+1][col+1] or Board[row+1][col+1] in (BlackUnicodes if color else WhiteUnicodes)):
            validMoves.append([row+1,col+1])
        #move downLeft on an empty square or by killing an opponet
        if row<7 and col>0 and (not Board[row+1][col-1] or Board[row+1][col-1] in (BlackUnicodes if color else WhiteUnicodes)):
            validMoves.append([row+1,col-1])

        #move Right on an empty square or by killing an opponet
        if col<7 and (not Board[row][col+1] or Board[row][col+1] in (BlackUnicodes if color else WhiteUnicodes)):
            validMoves.append([row,col+1])
        #move Left on an empty square or by killing an opponet
        if col>0 and (not Board[row][col-1] or Board[row][col-1] in (BlackUnicodes if color else WhiteUnicodes)):
            validMoves.append([row,col-1])

        
        return sorted(validMoves)

class Pawn(Piece):
    def __init__(self,**kwargs) -> None: 
        if kwargs['Color']==COLOR.BLACK:
            kwargs['ImageFile']=f"{ImagePath}bpawn.png"
            kwargs['Unicode']="\u265F"
        else:
            kwargs['ImageFile']=f"{ImagePath}wpawn.png"
            kwargs['Unicode']="\u2659"

        super().__init__(**kwargs)

    def __str__(self) -> str:
        return PIECENAME.PAWN.name

    def GetValidMoves(self,Board:list)->list:
        validMoves=[]
        row=self.Position.Row
        col=self.Position.Col

        if self.Color==COLOR.WHITE.name:
            if row<=6:
                if Board[row-1][col]==None:
                    validMoves=[[row-1,col]]

                if col>1 and Board[row-1][col-1]:
                    if Board[row-1][col-1] in BlackUnicodes:
                        validMoves.append([row-1,col-1])

                if col<7 and Board[row-1][col+1]:
                    if Board[row-1][col+1] in BlackUnicodes:
                        validMoves.append([row-1,col+1])

            #if this is the first move then it can move one additional square
            if row==6 and not Board[row-2][col]:
                    validMoves.append([row-2,col])

        else:
            if row>=1:
                if Board[row+1][col]==None:
                    validMoves=[[row+1,col]]

                if col>1 and Board[row+1][col-1]:
                    if Board[row+1][col-1] in WhiteUnicodes:
                        validMoves.append([row+1,col-1])

                if col<7 and Board[row+1][col+1]:
                    if Board[row+1][col+1] in BlackUnicodes:
                        validMoves.append([row+1,col+1])

            #if this is the first move then it can move one additional square
            if row==1 and not Board[row+2][col]:
                validMoves.append([row+2,col])
        
        return sorted(validMoves)

    

    
    
    
        