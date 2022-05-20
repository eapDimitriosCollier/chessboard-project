import sys
from time import sleep
sys.path.append('../chessboard-project')
from FileExplorer.FileExplorer import FileExplorer
from ChessView import ChessView
from ChessEngine import Board
from ChessPiece import Piece
from ChessFormConstants import *
from ChessModel import ChessModel
from Event.Event import Event
from Sound import *
from CustomTimer import RepeativeTimer,threading

class ChessController:

    def __init__(self,view:ChessView,model:ChessModel) -> None:
        self.view=view
        self.model=model
        self.ChessBoard=Board()
        self.Animation=True
        self.AnimationTaktTime=1 # in seconds
        self.AnimationPixelStep=10 # in pixels
        self.AnimationStepDelay=1 # in milliseconds
        self.AnimateTimerThread=None
        self.AnimationStatus='OFF'
        self.Lock=threading.Lock()
        Sound.SoundON=True
        self.ChessBoard.MovingEvent+= self.MovePiece
        self.ChessBoard.CaptureEvent+= self.CapturePiece
        self.ChessBoard.PromoteEvent+= self.PromotePiece
        self.ChessBoard.HideEvent+= self.HidePiece
                
        Event('ReadyToMove').subscribe(self)
        Event('LoadingStart').subscribe(self)
        Event('LoadingStop').subscribe(self)

   
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
            self.Pause_btn()
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
            #self.AnimateMove(tag=tag, destX=xx,destY=yy)
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
        while self.AnimationStatus=='HURRY':
            sleep(100/1000)
        self.Lock.acquire()
        x,y=self.view.canvas.coords(tag)
        self.AnimationStatus='ON'
        self.Lock.release()
        dx=destX-x
        dy=destY-y
        slope=0
        delay=self.AnimationStepDelay/1000
        step=self.AnimationPixelStep
        #Calculate slope to find the proper stepX and StepY 
        if dx and dy:
            slope=abs(dy/dx)
            stepX=step if dx>0 else -step
            stepY=slope*step if dy>0 else -slope*step
        
        #if there is no slope just make a single step on proper axis
        else:
            if dy!=0:
                stepY=step if dy>0 else -step
            else:
                stepY=0

            if dx!=0:
                stepX=step if dx>0 else -step
            else:
                stepX=0

        def isReachedOrExceeded(dest,coord,step):
            if step>0:
                if coord+step >= dest:
                    return True
                else:
                    return False
            elif step<0:
                if coord+step <= dest:
                    return True
                else:
                    return False
            elif step==0:
                return False
            
        toggle=True
        while not (isReachedOrExceeded(destX,x,stepX) or isReachedOrExceeded(destY,y,stepY) or self.AnimationStatus=='HURRY'):
            if int(slope*step)!=slope*step:    
                #toggle to compensate for floating point
                if toggle:
                    stepY=slope*step if dy>0 else -slope*step
                    stepY=int(stepY)
                    toggle=False
                else:
                    stepY=slope*step if dy>0 else -slope*step
                    stepY=int(stepY)+ (1 if stepY>0 else -1)
                    toggle=True
            
            self.view.MoveImage(tag,(x+stepX),(y+stepY))
            sleep(delay)
            x,y=self.view.GetImageCoords(tag)
        
        self.view.MoveImage(tag,destX,destY)
        with self.Lock:
            self.AnimationStatus='OFF'
        Sound.PlayWAV(MoveWAV)
        
        # if not self.view.isPlayEnabled:
        #     self.view.MoveNextBtn['state']="normal"


    def HidePiece(self,Tag)->None:
        self.view.HideImage(Tag)

    def InsertPiece(self,x:int,y:int,img:str)->int:
        return self.view.InsertImage(x,y,img)

    def MoveNext_btn(self) ->None:
        self.view.MoveNextBtn['state']='disable'
        if self.AnimationStatus=='ON':
            with self.Lock:
                self.AnimationStatus='HURRY'
        self.model.GetParserNextMove()
        self.view.MoveNextBtn['state']='normal'
        
    def MovePrevious_btn(self) ->None:
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

    def Play_btn(self)->None:
        self.view.PlayEnabled()
        self.AnimateTimerThread=RepeativeTimer(self.AnimationTaktTime,self.StartGameAnimation)
        self.AnimateTimerThread.start()
        
    def Pause_btn(self)->None:
        if self.AnimateTimerThread:
            self.AnimateTimerThread.stop()        
        self.view.PauseEnabled()

    def ClearBoardIMG(self)->None:
        for obj in self.ChessBoard.Container:
            self.view.DeleteImage(obj.Tag)

    def StartGameAnimation(self):
        if self.AnimationStatus=='ON':
            with self.Lock:
                self.AnimationStatus='HURRY'
        self.model.GetParserNextMove()

    #triggered by pause button
    def PauseGame(self):
        if self.AnimateTimerThread:
            self.AnimateTimerThread.stop()
        self.MoveNextBtn['state']="normal"
        self.MovePreviousBtn['state']="normal"
        self.PlayBtn['state']="normal"

    def FileDialog(self):
        self.Pause_btn()
        PgnString=FileExplorer().open()
        self.ClearBoardIMG()
        self.ChessBoard.PopulateBoard()
        self.PopulateBoardIMG()
        
        self.model.resetModel()
        self.model.Txt=PgnString
        self.model.interpret()    
              

    def PopulateBoardIMG(self)->None:
        for obj in self.ChessBoard.Container:
            if isinstance(obj,Piece):
                x=ChessBoardOffset+(ChessBoardSquareSize*(obj.Position.Col))
                y=ChessBoardOffset+(ChessBoardSquareSize*(obj.Position.Row))
                img=obj.ImageFile
                obj.Tag=self.InsertPiece(x,y,img)

    def DoNothing(self):
        pass

    def onLoadingStart(self, event):
        self.view.loadingStart()
    
    def onLoadingStop(self, event):
        self.view.loadingStop()
    
if __name__ == '__main__':
    ChessCtrl=ChessController(ChessView,ChessModel)
    ChessCtrl.Start()