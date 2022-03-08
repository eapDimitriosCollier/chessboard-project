from ChessPiece import King,Queen,Rook,Knight,Bishop,Pawn,COLOR,PIECENAME

class Board:
    def __init__(self) -> None:
        self.Container=[]
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
        
        self.MovingEvent = Event()
        self.CaptureEvent  = Event()
        #self.CaptureEvent= Event()
        self.MovingEvent+=self.PrinBoard
        self.CaptureEvent+=self.PrinBoard

    @property        
    def UnicodeBoard(self)->list:
        """Returns a 2D list of the current state of the chess board with unicode characters"""
        array=[[None for i in range(8)] for c in range(8)]
        for item in self.Container:
            #if isinstance(item,Piece) and item.IsVisible:
            array[item.Position.Row][item.Position.Col]=item.Unicode
        return array

    def MovePiece(self, Piece:str,Color:str, ToRow:int,ToCol:int,FromRow:int=None,FromCol:int=None )-> None:
        tag=""
        for item in [piece for piece in self.Container if str(piece)==Piece and piece.Color==Color 
                    and (piece.Position.Row==FromRow if FromRow else not None) and (piece.Position.Col==FromCol if FromCol else not None)]: 

            if [ToRow,ToCol] in item.GetValidMoves(self.UnicodeBoard):
                item.Position.Row=ToRow
                item.Position.Col=ToCol
                tag=item.Tag
                break    
        else:
            fromX=FromRow if FromRow!=None else "any"
            fromY=FromCol if FromCol!=None else "any"
            raise Exception (f"Move {Color} {Piece} to: ({ToRow},{ToCol}) from: ({fromX},{fromY}) is not valid!")    
        
        #raise moving event. All the event subscribers will be notified from the event handler
        self.MovingEvent( Piece,Color,ToRow=ToRow,ToCol=ToCol,Tag=tag) #,FromRow=FromRow,FromCol=FromCol

    def CapturePiece(self,Row:int,Col:int)-> None:
        for item in [piece for piece in self.Container if (piece.Position.Row==Row and piece.Position.Col==Col)]:
            #item.IsVisible=False
            self.Container.pop(self.Container.index(item))
            self.CaptureEvent(Tag=item.Tag)
            break
        else:
            raise Exception (f"No piece at ({Row},{Col})")    

        
    def PromotePiece(self,Row:int,Col:int,Piece:PIECENAME,Color:COLOR)-> None:
        for item in [piece for piece in self.Container if (piece.Position.Row==Row and piece.Position.Col==Col)]:
            #item.IsVisible=False
            if Piece==PIECENAME.ROOK.name:
                self.Container.append(Rook(Color=Color,Row=Row,Column=Col))

            if Piece==PIECENAME.KNIGHT.name:
                self.Container.append(Knight(Color=Color,Row=Row,Column=Col))

            if Piece==PIECENAME.BISHOP.name:
                self.Container.append(Bishop(Color=Color,Row=Row,Column=Col))

            if Piece==PIECENAME.QUEEN.name:
                self.Container.append(Queen(Color=Color,Row=Row,Column=Col))

            if Piece==PIECENAME.KING.name:
                self.Container.append(King(Color=Color,Row=Row,Column=Col))

            if Piece==PIECENAME.PAWN.name:
                self.Container.append(Pawn(Color=Color,Row=Row,Column=Col))
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




    ChessBoard.CapturePiece(1,0)
    
    #ChessBoard.MovePiece(PIECENAME.KNIGHT.name,Color=COLOR.WHITE.name,ToRow=5,ToCol=0)
    ChessBoard.CapturePiece(0,6)
    ChessBoard.CapturePiece(0,5)
    for item in ChessBoard.Container:
        if isinstance(item,Rook):
            print (item.Unicode,item,item.Position.FileRank,item.GetValidMoves(ChessBoard.UnicodeBoard))
    ChessBoard.KingKastling(COLOR.BLACK.name)
    ChessBoard.CapturePiece(7,1)
    ChessBoard.CapturePiece(7,2)
    ChessBoard.CapturePiece(7,6)
    ChessBoard.CapturePiece(7,5)
    ChessBoard.CapturePiece(7,3)
    ChessBoard.QueenKastling(COLOR.WHITE.name)
    # ChessBoard.CapturePiece(7,3)
    # ChessBoard.PromotePiece(1,0,PIECENAME.KING.name,COLOR.BLACK)
    # ChessBoard.KingKastling(COLOR.WHITE.name)
    # ChessBoard.QueenKastling(COLOR.WHITE.name)
    #ChessBoard.MovePiece("KNIGHT",Color=COLOR.BLACK.name,ToRow=2,ToCol=2,FromRow=0)
    #ChessBoard.PrinBoard()
