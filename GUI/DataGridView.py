
from tkinter import *
from tkinter import ttk
from GUI.ChessFormConstants import *
from Event.Event import Event

class DataGridView:
    def __init__(self,tkRoot,tkCanvas) -> None:
        self.root=tkRoot
        self.canvas=tkCanvas
        self.model = None
        
    def connectModel(self, model):
        Event('GamesUpdated').subscribe(self)
        Event('TagsUpdated').subscribe(self)
        Event('RawMovesUpdated').subscribe(self)
        self.model = model
    
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
        self.canvas.create_window(600, 0, anchor='nw', window=self.tree)


        columns = ('White Move', 'Black Move')
        self.tree_moves = ttk.Treeview(self.root, columns=columns, show='headings',height=5)
        self.tree_moves.column('White Move',width=148,minwidth=148)
        self.tree_moves.column('Black Move',width=148,minwidth=148)
        self.tree_moves.heading('White Move', text='-White Move-')
        self.tree_moves.heading('Black Move', text='-Black Move-')
        self.canvas.create_window(600, 150,height=350, anchor='nw', window=self.tree_moves)
        self.canvas.pack()


        tmpList=[];tmpList2=[]
        for n in range(1, 15):
            tmpList.append((f'Sample Event {n}', f'Sample Opponents {n}'))
            tmpList2.append((f'White Move {n}', f'Black Move {n}'))

        for record in tmpList:
            self.tree.insert('', 'end', values=record)     
        for record in tmpList2:       
            self.tree_moves.insert('', 'end', values=record)   
    
    def onGamesUpdated(self, event):
        print('From Datagrid view: GamesUpdated Event')
        print(self.model.games)
        
        self.model.GetParserTags(self.model.games[0])
        self.model.GetParserRawMoves(self.model.games[0])
    
    def onTagsUpdated(self, event):
        print('From Datagrid view: TagsUpdated Event')
        print(self.model.tags)
        
    
    def onRawMovesUpdated(self, event):
        print('From Datagrid view: RawMovesUpdated Event')
        print(self.model.rawMoves)
  
