#needs to install Pillow (pip install pillow)
from tkinter import *
from tkinter import ttk
from tkinter import messagebox
from PIL import ImageTk,Image
from ChessPiece import Rook,Knight,Bishop,King,Queen,Pawn,Piece
from ChessEngine import Board,PIECENAME,COLOR


ImagePath="./GUI_PA/img"
MainWindowGeometryX=900
MainWindowGeometryY=600
ChessBoardX=600;ChessBoardY=600
ChessBoardSquareSize=64
ChessPieceSize=60
ChessBoardOffset=42+ChessBoardSquareSize-ChessPieceSize
BackGroundColor='#333333'



class ChessMainForm:
    def __init__(self) -> None:
        self.root=Tk()
        self.canvas = Canvas(self.root, width = 800, height = 600) 
        self.ImageContainer=[]
        self.InitializeComponents()
        self.y=0
        self.x=0

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
        self.x+=1
        self.ChessBoard.MovePiece(PIECENAME.ROOK.name,Color=COLOR.BLACK.name, ToRow=self.x,ToCol=0)

    def MovePrevious(self) ->None:
        self.x-=1
        self.ChessBoard.MovePiece(PIECENAME.ROOK.name,Color=COLOR.BLACK.name, ToRow=self.x,ToCol=0)
    
    def MovePiece(self,*args,**kwargs):
        tag=int(kwargs['Tag'])
        Row=kwargs['ToRow']
        Column=kwargs['ToCol']
        self.canvas.moveto(tag,ChessBoardOffset+ChessBoardSquareSize*Column,ChessBoardOffset+ChessBoardSquareSize*Row)


    def CreateMenuBar(self)->None:
        menubar = Menu(self.root)
        filemenu = Menu(menubar, tearoff=0)
        menubar.add_cascade(label="File", menu=filemenu)
        filemenu.add_command(label="Open", command=self.DoNothing)
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
        self.root.iconbitmap(f"{ImagePath}/ico/chess.ico")

        self.canvas = Canvas(self.root, width = MainWindowGeometryX, height = ChessBoardY, bd=0, highlightthickness=0)   
        self.chessBoard_img=ImageTk.PhotoImage(Image.open(f"{ImagePath}/chessboard.png"))
        self.canvas.create_image(0, 0, anchor=NW, image=self.chessBoard_img) 
        self.canvas['background']=BackGroundColor
        
        self.next_icon = ImageTk.PhotoImage(Image.open(f"{ImagePath}/buttons/next.png"))
        self.previous_icon = ImageTk.PhotoImage(Image.open(f"{ImagePath}/buttons/previous.png"))
        self.play_icon = ImageTk.PhotoImage(Image.open(f"{ImagePath}/buttons/play.png"))
        self.pause_icon = ImageTk.PhotoImage(Image.open(f"{ImagePath}/buttons/pause.png"))
        MovePreviousBtn = self.canvas.create_window(650, 550, anchor='nw', window=Button(self.root,image=self.previous_icon,command=self.MovePrevious))
        MoveNextBtn = self.canvas.create_window(700, 550, anchor='nw', window=Button(self.root,image=self.next_icon,command=self.MoveNext) )
        PlayBtn = self.canvas.create_window(750, 550, anchor='nw', window=Button(self.root,image=self.play_icon))#,command=startThread)) 
        PauseBtn = self.canvas.create_window(800, 550, anchor='nw', window=Button(self.root,image=self.pause_icon))#,command=startThread)) 
        self.canvas.pack()

        #Create the checssboard and subscribe to the MovingEvent
        self.ChessBoard=Board()
        self.ChessBoard.OnMovingEvent+= self.MovePiece
        self.ChessBoard.CapturePiece(1,0)

        for obj in self.ChessBoard.Container:
            if isinstance(obj,Piece):
                self.ImageContainer.append(ImageTk.PhotoImage(Image.open(obj.ImageFile)))
                obj.Tag=self.canvas.create_image(ChessBoardOffset+(ChessBoardSquareSize*(obj.Position.Col)),
                                        ChessBoardOffset+(ChessBoardSquareSize*(obj.Position.Row)), 
                                        anchor=NW, image=self.ImageContainer[-1]) 
                
        self.canvas.pack(side="left")
        self.CreateMenuBar()
        self.CreateTree()


if __name__ == '__main__':
    MainWindow=ChessMainForm()