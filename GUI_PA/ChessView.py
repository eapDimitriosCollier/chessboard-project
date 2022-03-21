from tkinter import *
from tkinter import messagebox
from ChessFormConstants import *
from PIL import ImageTk,Image
from FormView import View
        
class ChessView(View):
    def __init__(self) -> None:
        self.root=Tk()
        self.root.withdraw()
        self.canvas = Canvas(self.root, width = 800, height = 600) 
        self.ImageContainer=[]
        self.controller=None

        self.title="Chess PGN Viewer"
        self.icon=f"{ImagePath}/ico/chess.ico"
        self.InitializeComponents()
        self.CreateMenuBar()

    def PlayEnabled(self)->None:
        self.MoveNextBtn['state']="disable"
        self.MovePreviousBtn['state']="disable"
        self.PlayBtn['state']="disable"

    def PauseEnabled(self)->None:
        self.MoveNextBtn['state']="normal"
        self.MovePreviousBtn['state']="normal"
        self.PlayBtn['state']="normal"

    def GetImageCoords(self,tag:int)-> list[int,int]:
        x,y=self.canvas.coords(tag)
        return (x,y)

    def InsertImage(self,x:int,y:int,imgFile:str)-> int:
        self.ImageContainer.append(ImageTk.PhotoImage(Image.open(imgFile)))
        tag=self.canvas.create_image(x,y,anchor=NW, image=self.ImageContainer[-1]) 
        return tag

    def DeleteImage(self,imageTag:int)-> None:
        self.canvas.delete(imageTag)

    def HideImage(self,tag)->None:
        self.canvas.itemconfig(tag, state='hidden') 

    def MoveImage(self,tag:int,x:int,y:int)-> None:
        #raise moving image 
        self.canvas.tag_raise(tag)
        self.canvas.moveto(tag,x,y)        

    def InitializeComponents(self)-> None:
        self.root.geometry(f"{MainWindowGeometryX}x{MainWindowGeometryY}")
        self.root.minsize(MainWindowGeometryX, MainWindowGeometryY)
        self.root.maxsize(MainWindowGeometryX, MainWindowGeometryY)
        
        self.root['background']=BackGroundColor    
        self.root.title(self.title)
        self.root.iconbitmap(self.icon)

        self.canvas = Canvas(self.root, width = MainWindowGeometryX, height = ChessBoardY, bd=0, highlightthickness=0)   
        self.chessBoard_img=ImageTk.PhotoImage(Image.open(f"{ImagePath}/chessboard.png"))
        self.canvas.create_image(0, 0, anchor=NW, image=self.chessBoard_img) 
        self.canvas['background']=BackGroundColor
        

        self.next_icon = ImageTk.PhotoImage(Image.open(f"{ImagePath}/Buttons/next.png"))
        self.previous_icon = ImageTk.PhotoImage(Image.open(f"{ImagePath}/Buttons/previous.png"))
        self.play_icon = ImageTk.PhotoImage(Image.open(f"{ImagePath}/Buttons/play.png"))
        self.pause_icon = ImageTk.PhotoImage(Image.open(f"{ImagePath}/Buttons/pause.png"))
        self.MovePreviousBtn = Button(self.root,image=self.previous_icon)
        self.MoveNextBtn = Button(self.root,image=self.next_icon) 
        self.PlayBtn=Button(self.root,image=self.play_icon,state='normal')
        self.PauseBtn = Button(self.root,image=self.pause_icon)
        #self.PauseBtn = self.canvas.create_window(800, 550, anchor='nw',window=Button(self.root,image=self.pause_icon))
        

        self.canvas.create_window(650, 550, anchor='nw', window=self.MovePreviousBtn)        
        self.canvas.create_window(700, 550, anchor='nw', window=self.MoveNextBtn)
        self.canvas.create_window(750, 550, anchor='nw', window=self.PlayBtn)
        self.canvas.create_window(800, 550, anchor='nw', window=self.PauseBtn)
    
        self.canvas.pack()


    def CreateMenuBar(self)->None:
        menubar = Menu(self.root)
        self.filemenu = Menu(menubar, tearoff=0)
        menubar.add_cascade(label="File", menu=self.filemenu)
        self.filemenu.add_command(label="Open")
        #filemenu.add_command(label="Close", command=self.DoNothing)
        self.filemenu.add_separator()
        self.filemenu.add_command(label="Exit")#, command=quit)

        self.helpmenu = Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Help", menu=self.helpmenu)
        self.helpmenu.add_command(label="Help Index")
        self.helpmenu.add_command(label="About...")
        self.helpmenu = Menu(menubar, tearoff=0)
        self.root.config(menu=menubar)    
    
    def msgBox(self,title:str,text:str)->None:
        messagebox.showinfo(title=title, message=text)
        

    def Couple(self,controller) -> None:
        self.MovePreviousBtn.config(command=controller.MovePrevious)
        self.MoveNextBtn.config(command=controller.MoveNext)
        self.PlayBtn.config(command=controller.Play)
        self.PauseBtn.config(command=controller.Pause)
        
        self.filemenu.entryconfig(index=self.filemenu.index("Open"),command=controller.FileDialog)
        self.filemenu.entryconfig(index=self.filemenu.index("Exit"),command=quit)
        
    def Show(self) -> None:
        #self.PauseBtn.config(command=lambda: self.msgBox("aaa","bbb"))
        self.root.deiconify()
        self.root.mainloop()
        


def test():
    print ("test")

if __name__ == '__main__':
    #ChessCtrl=ChessController()
    ChessForm=ChessView()
    ChessForm.Show()
    
