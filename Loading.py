import tkinter as tk
import os
from itertools import count, cycle
from Event.Event import Event

class ImageLabel(tk.Label):
    """
    A Label that displays images, and plays them if they are gifs
    :im: A PIL Image instance or a string filename
    """
    def load(self, path):
        if isinstance(path, str):
            self.path = path

        frames = []
 
        try:
            for i in count(1):
                frames.append(tk.PhotoImage(file=self.path, format=f"gif -index {i}"))
        except:
            pass
        self.frames = cycle(frames)
 
        
        self.delay = 100
 
        if len(frames) == 1:
            self.config(image=next(self.frames))
        else:
            self.next_frame()
 
    def unload(self):
        self.config(image=None)
        self.frames = None
 
    def next_frame(self):
        if self.frames:
            self.config(image=next(self.frames))
            self.after(self.delay, self.next_frame)

class Loading:
    def __init__(self):
        self.window = tk.Tk()
        self.gifPath = f'{os.getcwd()}\loading.gif'
        self.gif = None
        Event('LoadingMessage', message="").subscribe(self)

    def start(self) -> None:
        self.gif = ImageLabel(self.window)
        self.gif.pack()
        self.gif.load(self.gifPath)
        self.window.mainloop()

    def stop(self) -> None:
        self.window.quit()

    def onLoadingMessage(self, event) -> None:
        print(event.message) #Loading message: Giwrgo gamhse tous