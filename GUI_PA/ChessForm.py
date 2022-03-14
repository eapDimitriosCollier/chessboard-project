import sys
from time import sleep
sys.path.append('../CHESSBOARD-PROJECT')
from GUI_PA.Sound import *
from tkinter import *
from tkinter import ttk,messagebox
from PIL import ImageTk,Image
from ChessPiece import Rook,Knight,Bishop,King,Queen,Pawn,Piece
from ChessEngine import Board,PIECENAME,COLOR
from ChessConstants import *
from tkinter import filedialog
from FileExplorer.FileExplorer import FileExplorer
from Lexer.sample_game import txt
from Event.Event import Event
from Response.Response import Response
from ResponseListener.ResponseListener import ResponseListener
from Interpreter import Interpreter
from InterpreterResponse import InterpreterResponse
from GUIRequest import GUIRequest
from CustomTimer import RepeatTimer,threading

class ChessMainForm:
    def __init__(self) -> None:
        self.root=Tk()
        self.canvas = Canvas(self.root, width = 800, height = 600) 
        self.ImageContainer=[]
        self.AnimationSpeed=.5
        self.AnimateTimerThread=None
        self.InitializeComponents()
        self.root.mainloop()

    def DoNothing(self):
        pass


    def item_selected(self,event):
        for selected_item in self.tree.selection():
            item = self.tree.item(selected_item)
            print (item)
            

    #https://www.pythontutorial.net/tkinter/tkinter-treeview/        
    def CreateTree(self):
        # define columns
        columns = ('Chess Game', 'Opponents')
        self.tree = ttk.Treeview(self.root, columns=columns, show='headings',height=5)
        self.tree.column('Chess Game',width=148,minwidth=148)
        self.tree.column('Opponents',width=148,minwidth=148)
        self.tree.heading('Chess Game', text='-Chess Game-')
        self.tree.heading('Opponents', text='-Opponents-')
        
        self.style = ttk.Style(self.root)
        self.style.theme_use("clam")
        self.style.configure("Treeview", background='#CC8844', fieldbackground=BackGroundColor, foreground="white",font=('Calibri', 10,'bold'))
        self.style.configure("Treeview",rowheight=25)
        self.style.map("Treeview",background=[('selected','#512521')])
        #self.style.layout("Treeview", [('Treeview.treearea', {'sticky': 'nswe'})])
        self.canvas.create_window(600, 0, anchor='nw', window=self.tree)
        self.tree.bind('<<TreeviewSelect>>', self.item_selected)
        

        columns = ('White Move', 'Black Move')
        self.tree_moves = ttk.Treeview(self.root, columns=columns, show='headings',height=5)
        self.tree_moves.column('White Move',width=148,minwidth=148)
        self.tree_moves.column('Black Move',width=148,minwidth=148)
        self.tree_moves.heading('White Move', text='-White Move-')
        self.tree_moves.heading('Black Move', text='-Black Move-')
        self.canvas.create_window(600, 150,height=350, anchor='nw', window=self.tree_moves)


        tmpList=[];tmpList2=[]
        for n in range(1, 15):
            tmpList.append((f'Sample Event {n}', f'Sample Opponents {n}'))
            tmpList2.append((f'White Move {n}', f'Black Move {n}'))

        for record in tmpList:
            self.tree.insert('', 'end', values=record)     
        for record in tmpList2:       
            self.tree_moves.insert('', 'end', values=record)   
        

        #self.scrollbar = ttk.Scrollbar(self.root, orient=tk.VERTICAL, command=self.tree.yview)
        #self.tree.configure(yscroll=self.scrollbar.set)
        #self.scrollbar.pack(side=RIGHT,fill=Y)
        #self.Tree = self.canvas.create_window(907, 15,height=200,anchor="nw", window=self.scrollbar)
    
    def MoveNext(self) ->None:
        if not self.gameUUID:
            GUIRequest().getGames()
        self.GetParserNextMove(None)


    def MovePrevious(self) ->None:
        pass
        # self.ChessBoard.MovePiece(PIECENAME.ROOK.name,Color=COLOR.BLACK.name, ToRow=self.x,ToCol=0)

    #Triggered by Checs Engine PromoteEvent
    def PromotePiece(self):
        obj=self.ChessBoard.Container[-1]
        if isinstance(obj,Piece):
            self.ImageContainer.append(ImageTk.PhotoImage(Image.open(obj.ImageFile)))
            obj.Tag=self.canvas.create_image(ChessBoardOffset+(ChessBoardSquareSize*(obj.Position.Col)),
                                        ChessBoardOffset+(ChessBoardSquareSize*(obj.Position.Row)), 
                                        anchor=NW, image=self.ImageContainer[-1]) 
            
    #Triggered by Checs Engine CaptureEvent
    def HidePiece(self,Tag):
        Sound.PlayWAV(CaptureWAV)
        self.canvas.itemconfig(Tag, state='hidden') 

    #Triggered by Checs Engine MoveEvent
    def MovePiece(self,*args,**kwargs):
        tag=int(kwargs['Tag'])
        Row=kwargs['ToRow']
        Column=kwargs['ToCol']
        #self.canvas.moveto(tag,ChessBoardOffset+ChessBoardSquareSize*Column,ChessBoardOffset+ChessBoardSquareSize*Row)
        #return
        xx=ChessBoardOffset+ChessBoardSquareSize*Column
        yy=ChessBoardOffset+ChessBoardSquareSize*Row
        Thread=threading.Thread(target=self.AnimateMove,kwargs={'tag':tag,'destX':xx,'destY':yy})
        Thread.daemon=True
        Thread.start()

    #Triggered by GetGetNextMoveResponseHandler
    def OnReadyToMove(self):
        if self.moveId:
            self.GameActive=True
            for item in self.currentMove:
                self.MakeMove(item)
        else:
            self.GameActive=False
            if self.AnimateTimerThread:
                self.AnimateTimerThread.stop()
            messagebox.showinfo(title="Game End", message=self.currentMove)
            self.ChessBoard.PopulateBoard()
            self.PopulateBoardIMG()      
        

    def AnimateMove(self,tag,destX,destY):
        self.Lock.acquire()
        x,y=self.canvas.coords(tag)
        self.Lock.release()
        dx=destX-x
        dy=destY-y
        slope=0
        toggle=False
        
        #raise moving image 
        self.canvas.tag_raise(tag)

        #Calculate slope to find the proper stepX and StepY 
        if dx and dy:
            slope=abs(dy/dx)
            #print("slope=",slope, int(slope)==slope,int(slope))
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
            
            self.canvas.moveto(tag,(x+stepX),int(y+stepY))
            self.canvas.update()
            #sleep(self.AnimationSpeed/1000)
            x,y=self.canvas.coords(tag)

        self.canvas.moveto(tag,destX,destY)
        Sound.PlayWAV(MoveWAV)
        

    def PlayGameThread(self):
        self.Pause=False
        if not self.gameUUID:
            GUIRequest().getGames()

        self.AnimateTimerThread=RepeatTimer(self.AnimationSpeed,self.StartGameAnimation)
        self.GameActive=True
        self.AnimateTimerThread.start()
        
        

    def StartGameAnimation(self):
        if self.GameActive:
            self.GetParserNextMove(None)
        else:
            self.AnimateTimerThread.stop()

    #triggered by pause button
    def PauseGame(self):
        if self.AnimateTimerThread:
            self.AnimateTimerThread.stop()



    def ShowPiece(self,Tag):
        self.canvas.itemconfig(Tag, state='normal')

    #MenuItem File_Open
    def FileDialog(self):
        PgnString=FileExplorer().open()
        print (PgnString)
        self.txt=PgnString

        self.interpreterInit()
        

    def CreateMenuBar(self)->None:
        menubar = Menu(self.root)
        filemenu = Menu(menubar, tearoff=0)
        menubar.add_cascade(label="File", menu=filemenu)
        #filemenu.add_command(label="Open", command=self.DoNothing)
        filemenu.add_command(label="Open", command=self.FileDialog)
        
        filemenu.add_command(label="Close", command=self.DoNothing)
        filemenu.add_separator()
        filemenu.add_command(label="Exit", command=quit)

        helpmenu = Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Help", menu=helpmenu)
        helpmenu.add_command(label="Help Index", command=self.DoNothing)
        helpmenu.add_command(label="About...", command=self.DoNothing)
        helpmenu = Menu(menubar, tearoff=0)
        self.root.config(menu=menubar)
            

    def InitializeComponents(self)-> None:
        """ Initializing ChessEngine and all the visual components of the main form"""
        self.root.geometry(f"{MainWindowGeometryX}x{MainWindowGeometryY}")
        self.root.minsize(600, 600)
        self.root.maxsize(MainWindowGeometryX, MainWindowGeometryY)
        
        self.root['background']=BackGroundColor    
        self.root.title("Chess PGN Viewer")
        # self.root.iconbitmap(f"{ImagePath}/ico/chess.ico")

        self.canvas = Canvas(self.root, width = MainWindowGeometryX, height = ChessBoardY, bd=0, highlightthickness=0)   
        self.chessBoard_img=ImageTk.PhotoImage(Image.open(f"{ImagePath}/chessboard.png"))
        self.canvas.create_image(0, 0, anchor=NW, image=self.chessBoard_img) 
        self.canvas['background']=BackGroundColor
        

        self.next_icon = ImageTk.PhotoImage(Image.open(f"{ImagePath}/Buttons/next.png"))
        self.previous_icon = ImageTk.PhotoImage(Image.open(f"{ImagePath}/Buttons/previous.png"))
        self.play_icon = ImageTk.PhotoImage(Image.open(f"{ImagePath}/Buttons/play.png"))
        self.pause_icon = ImageTk.PhotoImage(Image.open(f"{ImagePath}/Buttons/pause.png"))
        MovePreviousBtn = self.canvas.create_window(650, 550, anchor='nw', window=Button(self.root,image=self.previous_icon,command=self.MovePrevious))
        MoveNextBtn = self.canvas.create_window(700, 550, anchor='nw', window=Button(self.root,image=self.next_icon,command=self.MoveNext) )
        PlayBtn = self.canvas.create_window(750, 550, anchor='nw', window=Button(self.root,image=self.play_icon,command=self.PlayGameThread))
        PauseBtn = self.canvas.create_window(800, 550, anchor='nw',window=Button(self.root,image=self.pause_icon,command=self.PauseGame))
        self.canvas.pack()

        #Create the checssboard and subscribe to the MovingEvent
        self.ChessBoard=Board()
        self.ChessBoard.MovingEvent+= self.MovePiece
        self.ChessBoard.CaptureEvent+= self.HidePiece
        self.ChessBoard.PromoteEvent+= self.PromotePiece
        self.Thread=None
        self.Lock=threading.Lock()
        self.ThreadCondition=threading.Condition(self.Lock)
        self.ThreadEvent= threading.Event()
        self.Pause=False
        self.txt=""
        
        self.HurryUp=False

        self.PopulateBoardIMG()
        # for obj in self.ChessBoard.Container:
        #     if isinstance(obj,Piece):
        #         self.ImageContainer.append(ImageTk.PhotoImage(Image.open(obj.ImageFile)))
        #         obj.Tag=self.canvas.create_image(ChessBoardOffset+(ChessBoardSquareSize*(obj.Position.Col)),
        #                                 ChessBoardOffset+(ChessBoardSquareSize*(obj.Position.Row)), 
        #                                 anchor=NW, image=self.ImageContainer[-1]) 
        #         print (obj.Tag,self.canvas.coords(obj.Tag))


    
        # self.ChessBoard.CapturePiece(1,0)
        # self.ChessBoard.CapturePiece(0,6)
        # self.ChessBoard.CapturePiece(0,5)
        # self.ChessBoard.KingKastling(COLOR.BLACK.name)      
        # self.ChessBoard.CapturePiece(7,1)
        # self.ChessBoard.CapturePiece(7,2)
        # self.ChessBoard.CapturePiece(7,3)
        # self.ChessBoard.QueenKastling(COLOR.WHITE.name)
        #self.UpdateBoard()                        
        self.canvas.pack(side="left")
        self.CreateMenuBar()
        self.CreateTree()

        self.games = []
        self.gameUUID = ''
        self.tags = []
        self.rawMoves = []
        self.moveId = None
        self.player = None
        self.currentMove = []
        self.GameActive=False
        
        # self.root.bind('<space>', lambda e : GUIRequest().getGames())
        # self.root.bind('1', lambda e: GUIRequest().getTags(self.gameUUID))
        # self.root.bind('2', lambda e: GUIRequest().getRawMoves(self.gameUUID))
        # #self.root.bind('3', lambda e: GUIRequest().getNextMove(self.gameUUID, self.moveId, self.player))
        # self.root.bind('3', self.GetParserNextMove)
        
        # Get File...
        #...
        self.interpreterInit()

    def PopulateBoardIMG(self)->None:
        for obj in self.ChessBoard.Container:
            self.canvas.delete(obj.Tag)

        self.ImageContainer.clear()
        for obj in self.ChessBoard.Container:
            if isinstance(obj,Piece):
                self.ImageContainer.append(ImageTk.PhotoImage(Image.open(obj.ImageFile)))
                obj.Tag=self.canvas.create_image(ChessBoardOffset+(ChessBoardSquareSize*(obj.Position.Col)),
                                        ChessBoardOffset+(ChessBoardSquareSize*(obj.Position.Row)), 
                                        anchor=NW, image=self.ImageContainer[-1]) 
                print (obj.Tag,self.canvas.coords(obj.Tag))

    def MakeMove(self,data):
        argNode={}
        color=self.player.upper()

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
            self.HurryUp=True
        
            if capture=='True':    
                self.ChessBoard.MovePiece(piece,Color=color,ToRow=toRow,ToCol=toCol,FromRow=fromRow,FromCol=fromColumn,Capture=True)
            else:
                self.ChessBoard.MovePiece(piece,Color=color,ToRow=toRow,ToCol=toCol,FromRow=fromRow,FromCol=fromColumn,Capture=False)
                    
        #if it is a Catle move then check its type
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
            
            

    def GetParserNextMove(self,event):
        GUIRequest().getNextMove(self.gameUUID, self.moveId, self.player)
        

        # if self.moveId:
        #     self.GameActive=True
        #     for item in self.currentMove:
        #         self.MakeMove(item)
        # else:
        #     self.GameActive=False
        #     if self.AnimateTimerThread.isActive:
        #         self.AnimateTimerThread.stop()
        #     messagebox.showinfo(title="Game End", message=self.currentMove)
        #     self.ChessBoard.PopulateBoard()
        #     self.PopulateBoardIMG()
 
        
    def UpdateBoard(self)->None:
        for obj in self.ChessBoard.Container:
            if isinstance(obj,Piece):
                self.MovePiece(ToRow=obj.Position.Row,ToCol=obj.Position.Col,Tag=obj.Tag) 

    def interpreterInit(self) -> None:
        # Initialize events
        Event('InterpretationStarted').subscribe(self)
        Event('InterpretationEnded').subscribe(self)
        Event('InterpretationFailed').subscribe(self)  
        self.interpreter = Interpreter(txt)
        #self.interpreter = Interpreter(self.txt)
        InterpreterResponse().subscribe(self)

    
    def onInterpretationStarted(self, event):
        print('Interpretation Started')
        
    def onInterpretationEnded(self, event):
        print('Interpretation Ended')
 


    
    def onInterpretationFailed(self, event):
        print('Interpretation Failed')
    
    def onResponse(self, response: Response):
        if (isinstance(response, InterpreterResponse)):
            # Θα ήταν ωραίο να παίζαμε με match-case αντί για if, αλλά για backwards compatibility
            # ας το αφήσουμε καλύτερα...
            
            if (response._request._type == "GET_GAMES"):
                self.GetGamesResponseHandler(response._response)
            elif (response._request._type == "GET_TAGS"):
                self.GetTagsResponseHandler(response._response)
            elif (response._request._type == "GET_RAW_MOVES"):
                self.GetRawMovesResponseHandler(response._response)
            elif (response._request._type == "GET_NEXT_MOVE"):
                self.GetGetNextMoveResponseHandler(response._response)
                self.OnReadyToMove()
            
    def onErrorResponse(self, response: Response):
        if (isinstance(response, InterpreterResponse)):
            self.interpreterErrorResponseHandler(response)
           
    def GetGamesResponseHandler(self, response):
        self.games = response
        self.gameUUID = self.games[0]
        print(self.gameUUID)
    
    def GetTagsResponseHandler(self, response):
        self.tags = response
        print(self.tags)
    
    def GetRawMovesResponseHandler(self, response):
        self.rawMoves = response
        print(self.rawMoves)
    
    def GetGetNextMoveResponseHandler(self, response):
        self.currentMove = response['nextMove']
        self.moveId = response['nextMoveId']
        self.player = response['nextPlayer']
        print('currentMove:', self.currentMove)
        print('moveId: ', self.moveId)
        print('player: ', self.player)
        
        

  


    def interpreterErrorResponseHandler(self, response):
        # Αν ο interpreter πετάξει error το παρουσιάζουμε στην οθόνη.
        
        print(response)
        

if __name__ == '__main__':
    MainWindow=ChessMainForm()
