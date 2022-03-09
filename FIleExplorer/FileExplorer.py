from tkinter import *
from tkinter import filedialog
import os

class FileExplorer:
    def __init__(self):
        self.dataFile = None

    def open(self):
        filepath = filedialog.askopenfilename(initialdir=os.getcwd(), title="Please select a file", filetypes= [("PGN files","*.pgn")])

        self.file = open(filepath,'r')
        self.dataFile = self.file.read()
        self.file.close()
        
        return self.dataFile

# # How to use:

#     print(FileExplorer().open())