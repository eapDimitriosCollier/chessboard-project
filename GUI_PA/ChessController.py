import sys
sys.path.append('../CHESSBOARD-PROJECT')
from FileExplorer.FileExplorer import FileExplorer
from FormView import View
from ChessView import ChessView
from ChessEngine import Board
from ChessPiece import Piece
from ChessFormConstants import *
from ChessModel import ChessModel
from Event.Event import Event
from Sound import *
from CustomTimer import RepeativeTimer,threading


class ChessController:

    def __init__(self,view:ChessView,model=ChessModel) -> None:
        self.view=view
        self.model=model
        self.ChessBoard=Board()
        self.Animation=True
        self.AnimationSpeed=.5
        self.AnimateTimerThread=None
        Sound.SoundON=True
        self.ChessBoard.MovingEvent+= self.MovePiece
        self.ChessBoard.CaptureEvent+= self.CapturePiece
        self.ChessBoard.PromoteEvent+= self.PromotePiece
        self.ChessBoard.HideEvent+= self.HidePiece
        self.Lock=threading.Lock()
        Event('ReadyToMove').subscribe(self)
        
   
    def Start(self)->None:
        self.view=self.view()
        self.view.Couple(self)
        
        self.model=self.model()
        self.ClearBoardIMG()
        self.PopulateBoardIMG()
        self.view.Show()

    def ParseMove(self,data):
        """Parses the move dictionary returned by the interpreter"""
        print (data)
        argNode={}
        color=self.model.player.upper()

        #if it's a normal movement then retrieve movement fields
        if data['actionName']=="Movement":
            argNode=data['arguments']
            piece=argNode['piece'].upper()
            fromRow=(8-int(argNode['fromRow'])) if argNode['fromRow'] else None
            fromColumn=int(ord(argNode['fromColumn'])-97) if argNode['fromColumn'] else None
            toSquare=argNode['toSquare']
            toCol=int(ord(toSquare[0])-97)
            toRow=8-int(toSquare[1])
            capture=argNode['isCapturing']

            self.Row=toRow
            self.Column=toCol
        
            if capture=='True':    
                self.ChessBoard.MovePiece(piece,Color=color,ToRow=toRow,ToCol=toCol,FromRow=fromRow,FromCol=fromColumn,Capture=True)
            else:
                self.ChessBoard.MovePiece(piece,Color=color,ToRow=toRow,ToCol=toCol,FromRow=fromRow,FromCol=fromColumn,Capture=False)
                    
        #if it is a Castle move then check its type
        elif data['actionName']=='Castle':
            argNode=data['arguments']
            castleType=argNode['type'].upper()
            if castleType=="LONG":
                self.ChessBoard.QueenKastling(color)
            else:
                self.ChessBoard.KingKastling(color)

        elif data['actionName']=='Promotion':
            argNode=data['arguments']
            promoteToPiece=argNode['promonotionPiece'].upper()
            self.ChessBoard.PromotePiece(self.Row,self.Column,promoteToPiece,color)
            

        elif data['actionName']=='Check':
            Sound.PlayWAV(CheckWAV)

    #Triggered by ChessModel.GetGetNextMoveResponseHandler
    def onReadyToMove(self,event):
        if self.model.moveId:
            self.model.GameActive=True
            for item in self.model.currentMove:
                self.ParseMove(item)
        else:
            self.Pause()
            self.view.msgBox("Game End",f"Result:{self.model.currentMove}")
            self.model.GameActive=False
            self.ClearBoardIMG()
            self.ChessBoard.PopulateBoard()
            self.PopulateBoardIMG()   


    #Triggered by Chess Engine MoveEvent
    def MovePiece(self,*args,**kwargs):
        tag=int(kwargs['Tag'])
        Row=kwargs['ToRow']
        Column=kwargs['ToCol']
        if self.Animation:
            xx=ChessBoardOffset+ChessBoardSquareSize*Column
            yy=ChessBoardOffset+ChessBoardSquareSize*Row
            Thread=threading.Thread(target=self.AnimateMove,kwargs={'tag':tag,'destX':xx,'destY':yy})
            Thread.daemon=True
            Thread.start()
        else:
            self.view.MoveImage(tag,ChessBoardOffset+ChessBoardSquareSize*Column,ChessBoardOffset+ChessBoardSquareSize*Row)
            Sound.PlayWAV(MoveWAV)

    #Triggered by Chess Engine CaptureEvent
    def CapturePiece(self,Tag):
        Sound.PlayWAV(CaptureWAV)
        self.view.HideImage(Tag)

    #Triggered by Chess Engine PromoteEvent
    def PromotePiece(self):
        obj=self.ChessBoard.Container[-1]
        x=ChessBoardOffset+(ChessBoardSquareSize*(obj.Position.Col))
        y=ChessBoardOffset+(ChessBoardSquareSize*(obj.Position.Row))
        img=obj.ImageFile
        obj.Tag=self.InsertPiece(x,y,img)
        Sound.PlayWAV(PromoteWAV)

    def AnimateMove(self,tag,destX,destY):
        self.Lock.acquire()
        x,y=self.view.canvas.coords(tag)
        self.Lock.release()
        dx=destX-x
        dy=destY-y
        slope=0
        toggle=False

        #Calculate slope to find the proper stepX and StepY 
        if dx and dy:
            slope=abs(dy/dx)
            stepX=1 if dx>0 else -1
            stepY=slope if dy>0 else -slope
        
        #if there is no slope just make a single step on proper axis
        else:
            if dy!=0:
                stepY=1 if dy>0 else -1
            else:
                stepY=0

            if dx!=0:
                stepX=1 if dx>0 else -1
            else:
                stepX=0

        while x!=destX or y!=destY:
            #make sure to exit the loop if the destinatuon is bypassed when toggling is on
            if slope!=0:
                if dy>0:
                    if y>=destY: break
                else:
                    if y<=destY: break

                if int(slope)!=slope:    
                    #toggle to compensate for floating point
                    if not toggle:           
                        if int(slope)>0:
                            stepY=-int(slope) if dy>0 else int(slope)
                            toggle=False
                        else:
                            stepY=1 if dy>0 else -1
                            toggle=True            
                    else:
                        stepY=0
                        toggle=False
            
            self.view.MoveImage(tag,(x+stepX),int(y+stepY))
            x,y=self.view.GetImageCoords(tag)
        
        self.view.MoveImage(tag,destX,destY)
        Sound.PlayWAV(MoveWAV)

    def HidePiece(self,Tag)->None:
        self.view.HideImage(Tag)

    def InsertPiece(self,x:int,y:int,img:str)->int:
        return self.view.InsertImage(x,y,img)

    def MoveNext(self) ->None:
        self.view.MoveNextBtn['state']='disable'
        self.model.GetParserNextMove(None)
        self.view.MoveNextBtn['state']='normal'
        
    def MovePrevious(self) ->None:
        self.ClearBoardIMG()
        if self.model.moveId:
            if self.model.player=="white":
                if int(self.model.moveId)>1:
                    self.model.player="black"
                    self.ChessBoard.PopState()
                    self.model.moveId=str(int(self.model.moveId)-1)
            else:
                self.ChessBoard.PopState()
                self.model.player="white"                      
        
        self.PopulateBoardIMG()
        Sound.PlayWAV(MoveWAV)

    def ClearBoardIMG(self)->None:
        for obj in self.ChessBoard.Container:
            self.view.DeleteImage(obj.Tag)

    def Play(self)->None:
        self.view.PlayEnabled()
        self.AnimateTimerThread=RepeativeTimer(self.AnimationSpeed,self.StartGameAnimation)
        self.GameActive=True
        self.AnimateTimerThread.start()
        

    def Pause(self)->None:
        if self.AnimateTimerThread:
            self.AnimateTimerThread.stop()        
        self.view.PauseEnabled()

    def StartGameAnimation(self):
        #if self.GameActive:
        self.model.GetParserNextMove(None)
        #else:
        #self.AnimateTimerThread.stop()

    #triggered by pause button
    def PauseGame(self):
        if self.AnimateTimerThread:
            self.AnimateTimerThread.stop()
        self.MoveNextBtn['state']="normal"
        self.MovePreviousBtn['state']="normal"
        self.PlayBtn['state']="normal"

    def FileDialog(self):
        self.Pause()
        PgnString=FileExplorer().open()
        self.ClearBoardIMG()
        self.ChessBoard.PopulateBoard()
        self.PopulateBoardIMG() 
        self.model.Txt=PgnString
        self.model.GameActive=False
        self.model.interpreterInit()     
              

    def PopulateBoardIMG(self)->None:
        for obj in self.ChessBoard.Container:
            if isinstance(obj,Piece):
                x=ChessBoardOffset+(ChessBoardSquareSize*(obj.Position.Col))
                y=ChessBoardOffset+(ChessBoardSquareSize*(obj.Position.Row))
                img=obj.ImageFile
                obj.Tag=self.InsertPiece(x,y,img)

    def DoNothing(self):
        pass

if __name__ == '__main__':
    ChessCtrl=ChessController(ChessView,ChessModel)
    ChessCtrl.Start()