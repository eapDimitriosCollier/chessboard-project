from tkinter import *
from tkinter import filedialog

class Application:
    def __init__(self) -> None:
        self.WIDTH = 600
        self.HEIGHT = 600
        self.TITLE = "PGN Reader"
        self.window = Tk()
        self.start()
    
    def start(self):
        # Initialize tkinter
        self.window.title(self.TITLE)
        self.window.geometry("{self.WIDTH}x{self.HEIGHT}")
        self.window.config(background = "white")
        self.window.mainloop()
        
      
        

        