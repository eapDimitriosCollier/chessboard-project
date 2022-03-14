from ChessPiece import King,Queen,Rook,Knight,Bishop,Pawn,COLOR,PIECENAME

class Board:
    def __init__(self) -> None:
        self.Container=[]
        self.PopulateBoard()
        self.MovingEvent=Event()
        self.CaptureEvent=Event()
        self.PromoteEvent=Event()
        # self.MovingEvent+=self.PrinBoard
        # self.CaptureEvent+=self.PrinBoard
        # self.PromoteEvent+=self.PrinBoard

    @staticmethod
    def fileRanktoRowCol(cls,fileRank:str)-> tuple[int,int]:
        return (int(fileRank[1])-1,int(ord(fileRank[0])-97))

    @property        
    def UnicodeBoard(self)->list:
        """Returns a 2D list of the current state of the chess board with unicode characters"""
        array=[[None for i in range(8)] for c in range(8)]
        for item in self.Container:
            #if isinstance(item,Piece) and item.IsVisible:
            array[item.Position.Row][item.Position.Col]=item.Unicode
        return array

    def PopulateBoard(self)->None:
        self.Container.clear()
        self.Container.append(Rook(Color=COLOR.BLACK,Row=0,Column=0))
        self.Container.append(Knight(Color=COLOR.BLACK,Row=0,Column=1))
        self.Container.append(Bishop(Color=COLOR.BLACK,Row=0,Column=2))
        self.Container.append(Queen(Color=COLOR.BLACK,Row=0,Column=3))
        self.Container.append(King(Color=COLOR.BLACK,Row=0,Column=4))
        self.Container.append(Bishop(Color=COLOR.BLACK,Row=0,Column=5))
        self.Container.append(Knight(Color=COLOR.BLACK,Row=0,Column=6))
        self.Container.append(Rook(Color=COLOR.BLACK,Row=0,Column=7))
        for col in range (0,8):
            self.Container.append(Pawn(Color=COLOR.BLACK,Row=1,Column=col))
            self.Container.append(Pawn(Color=COLOR.WHITE,Row=6,Column=col))
        self.Container.append(Rook(Color=COLOR.WHITE,Row=7,Column=0))
        self.Container.append(Knight(Color=COLOR.WHITE,Row=7,Column=1))
        self.Container.append(Bishop(Color=COLOR.WHITE,Row=7,Column=2))
        self.Container.append(Queen(Color=COLOR.WHITE,Row=7,Column=3))
        self.Container.append(King(Color=COLOR.WHITE,Row=7,Column=4))
        self.Container.append(Bishop(Color=COLOR.WHITE,Row=7,Column=5))
        self.Container.append(Knight(Color=COLOR.WHITE,Row=7,Column=6))
        self.Container.append(Rook(Color=COLOR.WHITE,Row=7,Column=7))    
        print(len(self.Container))


    def MovePiece(self, Piece:str,Color:str, ToRow:int,ToCol:int,FromRow:int=None,FromCol:int=None, Capture:bool=False)-> None:
        tag=""
        tmpItem=0
        if Capture:
            for item in [piece for piece in self.Container if (piece.Position.Row==ToRow and piece.Position.Col==ToCol )]:
                tmpItem=item
                break

            
        for item in [piece for piece in self.Container if str(piece)==Piece and piece.Color==Color 
                    and (piece.Position.Row==FromRow if FromRow else not None) and (piece.Position.Col==FromCol if FromCol else not None)]: 

            if [ToRow,ToCol] in item.GetValidMoves(self.UnicodeBoard):
                item.Position.Row=ToRow
                item.Position.Col=ToCol
                tag=item.Tag
                break    
        else:
            #print (item.GetValidMoves(self.UnicodeBoard))
            fromX=FromRow if FromRow!=None else "any"
            fromY=FromCol if FromCol!=None else "any"
            raise Exception (f"Move {Color} {Piece} to: ({ToRow},{ToCol}) from: ({fromX},{fromY}) is not valid!")    
        
        #raise moving event. All the event subscribers will be notified from the event handler
        self.MovingEvent( Piece,Color,ToRow=ToRow,ToCol=ToCol,Tag=tag) #,FromRow=FromRow,FromCol=FromCol
        if Capture:
            self.Container.pop(self.Container.index(tmpItem))
            self.CaptureEvent(Tag=tmpItem.Tag)
 
    def CapturePiece(self, Row:int,Col:int)-> None:
        for item in [piece for piece in self.Container if (piece.Position.Row==Row and piece.Position.Col==Col )]:
            #item.IsVisible=False
            self.Container.pop(self.Container.index(item))
            self.CaptureEvent(Tag=item.Tag)
            break
        else:
            raise Exception (f"No piece at ({Row},{Col})")    

        
    def PromotePiece(self,Row:int,Col:int,Piece:str,Color:COLOR)-> None:
        for item in [piece for piece in self.Container if (piece.Position.Row==Row and piece.Position.Col==Col)]:
            self.CapturePiece(Row,Col)
            color=COLOR.BLACK if Color=='BLACK' else COLOR.WHITE

            #item.IsVisible=False
            if Piece==PIECENAME.ROOK.name:
                self.Container.append(Rook(Color=color,Row=Row,Column=Col))

            if Piece==PIECENAME.KNIGHT.name:
                self.Container.append(Knight(Color=color,Row=Row,Column=Col))

            if Piece==PIECENAME.BISHOP.name:
                self.Container.append(Bishop(Color=color,Row=Row,Column=Col))

            if Piece==PIECENAME.QUEEN.name:
                self.Container.append(Queen(Color=color,Row=Row,Column=Col))

            if Piece==PIECENAME.KING.name:
                self.Container.append(King(Color=color,Row=Row,Column=Col))

            if Piece==PIECENAME.PAWN.name:
                self.Container.append(Pawn(Color=color,Row=Row,Column=Col))
            
            self.PromoteEvent()
            break
        else:
            raise Exception (f"No piece at ({Row},{Col})")      

    def KingKastling(self,Color:str)-> None:    
        if Color==COLOR.WHITE.name:
            _ToRow=7 
        else:
            _ToRow=0

        self.MovePiece(PIECENAME.ROOK.name,Color,ToRow=_ToRow,ToCol=5,FromRow=_ToRow)#FromCol=7

        for item in [piece for piece in self.Container if (piece.Position.Row==_ToRow and piece.Position.Col==4)]:
            tmpKing=item
            break
        
        if isinstance(tmpKing,King):
            tmpKing.Position.Col=6

        self.MovingEvent( PIECENAME.KING.name,Color,ToRow=tmpKing.Position.Row,ToCol=tmpKing.Position.Col,Tag=tmpKing.Tag)#FromCol=4

        

    def QueenKastling(self,Color:str)-> None:
        if Color==COLOR.WHITE.name:
            _ToRow=7 
        else:
            _ToRow=0

        self.MovePiece(PIECENAME.ROOK.name,Color,ToRow=_ToRow,ToCol=3,FromRow=_ToRow)

        for item in [piece for piece in self.Container if (piece.Position.Row==_ToRow and piece.Position.Col==4)]:
            tmpKing=item
            break
        
        if isinstance(tmpKing,King):
            tmpKing.Position.Col=2
        
        self.MovingEvent( PIECENAME.KING.name,Color,ToRow=tmpKing.Position.Row,ToCol=tmpKing.Position.Col,Tag=tmpKing.Tag)#FromCol=4

    
    def PrinBoard(self,*args,**kwargs):
        print("",end= "\t")     
        i=0       
        for a in range(ord("a"),ord("h")+1):
            print(f"{chr(a)}/{i}",end= "\t")
            i+=1
        print()
        
        i=0
        for _ in self.UnicodeBoard:
            print (i,end="\t")
            i+=1
            for item in _:
                print(item,end= "\t")
            print()    

class Event:
    def __init__(self):
        self.__eventhandlers = []
 
    def __iadd__(self, handler):
        self.__eventhandlers.append(handler)
        return self
 
    def __isub__(self, handler):
        self.__eventhandlers.remove(handler)
        return self
 
    def __call__(self, *args, **keywargs):
        #This is the OnEvent method
        for eventhandler in self.__eventhandlers:
            eventhandler(*args, **keywargs)



if __name__ == '__main__':
    ChessBoard=Board()
    ChessBoard.MovingEvent+= lambda *args,**kwargs:print(f"Τhis is an event triggered method! {args},{kwargs}")
    ChessBoard.MovingEvent+= lambda *args,**kwargs:print(f"Τhis is an other event triggered method! {args},{kwargs}")
    #ChessBoard.MovingEvent+= ChessBoard.PrinBoard


    ChessBoard.MovePiece("PAWN","WHITE",ToRow=4,ToCol=3,FromRow=None,FromCol=None,Capture=False)
    
    quit() 

    ChessBoard.CapturePiece(1,0)

