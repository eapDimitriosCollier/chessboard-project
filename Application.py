import tkinter as tk
from tkinter import filedialog
from Event import Event
from EventListener import EventListener
from GUIRequest import GUIRequest
from sample_game import txt
from Interpreter import Interpreter
from InterpreterEvent import InterpreterEvent
from InterpreterResponse import InterpreterResponse

class Application(EventListener):
    def __init__(self) -> None:
        self.WIDTH = 600
        self.HEIGHT = 600
        self.TITLE = "PGN Reader"
        self.window = tk.Tk()
        self.start()
    
    def start(self):
        # Initialize tkinter
        self.window.title(self.TITLE)
        self.window.geometry(f"{self.WIDTH}x{self.HEIGHT}")
        self.window.config(background = "white")
        
        self.window.bind('<space>', lambda e: self.guiGetGames())
        # Get File...
        #...
        self.interpreterInit()
        self.window.mainloop()  
    
    def interpreterInit(self):
        # Initialize events
        interpreterEvent = InterpreterEvent()
        interpreterEvent.subscribe(self)
        
        interpreterResponse = InterpreterResponse()
        interpreterResponse.subscribe(self)
        
        self.interpreter = Interpreter(interpreterEvent, interpreterResponse, txt)
        
        self.guiRequest = GUIRequest()
        self.guiRequest.subscribe(self.interpreter)
    
    def onEvent(self, event: Event):
        if (isinstance(event, InterpreterEvent)):
            if (event._state == "START_INTERPRETATION"):
                print("Interpretation started")
                # Loading window...
            elif (event._state == "END_INTERPRETATION"):
                # Stop loading window...
                print("Interpretation ended")
        elif (isinstance(event, InterpreterResponse)):
            print(event._response)  
    
    def guiGetGames(self):
        self.guiRequest.getGames()
        
if __name__ == '__main__':
    app = Application()
    app.start()
        