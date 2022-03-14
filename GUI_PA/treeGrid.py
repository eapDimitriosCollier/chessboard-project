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
from FileExplorer.FileExplorer import FileExplorer
from Lexer.sample_game import txt
from Event.Event import Event
from Response.Response import Response
from ResponseListener.ResponseListener import ResponseListener
from Interpreter import Interpreter
from InterpreterResponse import InterpreterResponse
from GUIRequest import GUIRequest
from CustomTimer import RepeatTimer,threading

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