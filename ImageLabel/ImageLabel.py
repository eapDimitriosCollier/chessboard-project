import tkinter as tk
from itertools import count, cycle

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